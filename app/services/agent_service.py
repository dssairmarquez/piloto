# --- RUTA: app/services/agent_service.py ---
from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional

from openai import OpenAI
from openai import APIError, APIConnectionError, APIStatusError

from app.config import BASE_INSTRUCTIONS, DEFAULT_MODEL
from app.repositories.chats_repo import ChatsRepo
from app.repositories.contexts_repo import ContextsRepo
from app.repositories.messages_repo import MessagesRepo
from app.services.fs_tools import FsTools


def require_env(name: str) -> str:
    val = os.environ.get(name, "").strip()
    if not val:
        raise RuntimeError(f"Missing environment variable: {name}")
    return val


EventFn = Callable[[str, dict[str, Any]], None]


@dataclass(frozen=True)
class ChatTurn:
    role: str
    content: str


class VisibleConsole:
    """
    Windows: abre una ventana PowerShell visible que hace tail -f a un log.
    Log: <AGENT_WORKDIR>/agent_console.log

    Control:
      set AGENT_VISIBLE_CONSOLE=1  (default)
      set AGENT_VISIBLE_CONSOLE=0
    """

    def __init__(self, workdir: Path) -> None:
        self.workdir = workdir
        self.log_path = (workdir / "agent_console.log").resolve()
        self._started = False
        self._proc: Optional[subprocess.Popen] = None
        self.enabled = (os.environ.get("AGENT_VISIBLE_CONSOLE", "1").strip() == "1")

    def start_if_needed(self) -> None:
        if not self.enabled or self._started:
            return

        self.workdir.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            self.log_path.write_text("", encoding="utf-8", errors="replace")

        if os.name == "nt":
            try:
                cmd = [
                    "powershell",
                    "-NoExit",
                    "-Command",
                    f'Write-Host "MiniGPT Agent Console (tail) -> {str(self.log_path)}"; '
                    f'Write-Host ""; '
                    f'Get-Content -Path "{str(self.log_path)}" -Wait',
                ]
                self._proc = subprocess.Popen(
                    cmd,
                    cwd=str(self.workdir),
                    creationflags=subprocess.CREATE_NEW_CONSOLE,  # type: ignore[attr-defined]
                )
            except Exception:
                pass

        self._started = True

    def append(self, text: str) -> None:
        if not self.enabled:
            return
        try:
            self.start_if_needed()
            with self.log_path.open("a", encoding="utf-8", errors="replace") as f:
                f.write(text)
                if not text.endswith("\n"):
                    f.write("\n")
        except Exception:
            pass


class ShellRunner:
    def __init__(self, visible: VisibleConsole) -> None:
        self.default_timeout = int(os.environ.get("AGENT_CMD_TIMEOUT_SECONDS", "3600"))
        self.visible = visible

    def run(self, command: str, timeout: Optional[int] = None, cwd: Optional[str] = None) -> dict[str, Any]:
        t = timeout if timeout is not None else self.default_timeout

        self.visible.append("\n" + "=" * 90)
        self.visible.append(f"[RUN] cwd={cwd or ''}")
        self.visible.append(command)
        self.visible.append("-" * 90)

        try:
            completed = subprocess.run(
                command,
                shell=True,
                text=True,
                capture_output=True,
                timeout=t,
                cwd=cwd,
            )
            out = (completed.stdout or "") + (completed.stderr or "")
            out_trim = out[-200_000:]

            self.visible.append(f"[EXIT] {completed.returncode}")
            self.visible.append(out_trim if out_trim.strip() else "(sin output)")
            self.visible.append("=" * 90 + "\n")

            return {
                "ok": completed.returncode == 0,
                "returncode": completed.returncode,
                "output": out_trim,
            }
        except subprocess.TimeoutExpired as e:
            out = ((e.stdout or "") + (e.stderr or "")).strip()
            msg = (out + "\n\n[timeout]").strip()

            self.visible.append("[TIMEOUT]")
            self.visible.append(msg if msg else "(sin output)")
            self.visible.append("=" * 90 + "\n")

            return {"ok": False, "returncode": None, "output": msg}
        except Exception as e:
            msg = f"[runner error] {e}"

            self.visible.append("[ERROR]")
            self.visible.append(msg)
            self.visible.append("=" * 90 + "\n")

            return {"ok": False, "returncode": None, "output": msg}


class AgentService:
    def __init__(
        self,
        chats: ChatsRepo,
        messages: MessagesRepo,
        contexts: ContextsRepo,
        client: OpenAI,
        model: str = DEFAULT_MODEL,
    ) -> None:
        self.chats = chats
        self.messages = messages
        self.contexts = contexts
        self.client = client
        self.model = model

        self.fs = FsTools()
        self.root = Path(self.fs.root)  # FsTools guarda root como Path internamente
        self.visible = VisibleConsole(self.root)
        self.shell = ShellRunner(self.visible)

        # cwd persistente por chat (simula sesión)
        self._cwd_by_chat: dict[int, Path] = {}

    def _agent_rules(self) -> str:
        return (
            "MODO AGENTE (OBLIGATORIO):\n"
            "- Si la tarea requiere varios pasos, primero crea un PLAN corto (lista numerada).\n"
            "- Luego ejecuta paso a paso.\n"
            "- Para ejecutar comandos usa run_shell.\n"
            "- Para crear proyectos/código con carpetas y archivos usa herramientas FS.\n"
            "- Regla dura: si afirmas que vas a ejecutar una acción con herramientas, DEBES llamar la tool en ese mismo turno.\n"
            "- Después de cada tool, evalúa el output y decide el siguiente paso.\n"
            "- No inventes outputs.\n"
            "\n"
            "REGLAS IMPORTANTES DE CONSOLA (Windows):\n"
            "- NO uses `activate`.\n"
            "- Crea el venv en el proyecto como `.venv`.\n"
            "- Instala con: `.venv\\Scripts\\python -m pip install ...`\n"
            "- Ejecuta con:  `.venv\\Scripts\\python app.py`\n"
            "\n"
            "REGLA CRÍTICA DE FS:\n"
            "- Las tools de FS operan RELATIVO al directorio actual (cwd) del chat.\n"
            "- Si estás en el proyecto, `write_file app.py` debe crear app.py dentro del proyecto.\n"
        )

    def _build_instructions(self, project_id: int) -> str:
        actives = self.contexts.active_contexts_for_project(project_id)
        base = BASE_INSTRUCTIONS + "\n\n" + self._agent_rules()

        if not actives:
            return base

        joined = "\n\n".join([f"[{c['name']}]\n{c['content']}".strip() for c in actives])
        return (
            BASE_INSTRUCTIONS
            + "\n\n"
            + "Contextos activos del proyecto (prioritarios):\n"
            + joined
            + "\n\n"
            + self._agent_rules()
        )

    def _load_history(self, chat_id: int, limit: int = 40) -> list[ChatTurn]:
        msgs = self.messages.list_by_chat(chat_id)
        if len(msgs) > limit:
            msgs = msgs[-limit:]
        return [ChatTurn(m["role"], m["content"]) for m in msgs]

    def _tools(self) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "run_shell",
                    "description": "Ejecuta un comando de consola en el servidor y devuelve stdout+stderr.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string"},
                            "timeout_seconds": {"type": "integer"},
                        },
                        "required": ["command"],
                        "additionalProperties": False,
                    },
                },
            },
            {
                "type": "function",
                "function": {"name": "fs_root", "description": "Devuelve el directorio raíz del sandbox.", "parameters": {"type": "object", "properties": {}, "additionalProperties": False}},
            },
            {
                "type": "function",
                "function": {"name": "pwd", "description": "Devuelve el directorio actual (cwd) del chat.", "parameters": {"type": "object", "properties": {}, "additionalProperties": False}},
            },
            {
                "type": "function",
                "function": {"name": "list_dir", "description": "Lista el contenido de una carpeta (relativa al cwd del chat).", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "additionalProperties": False}},
            },
            {
                "type": "function",
                "function": {"name": "make_dirs", "description": "Crea carpetas (relativo al cwd del chat).", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"], "additionalProperties": False}},
            },
            {
                "type": "function",
                "function": {"name": "read_file", "description": "Lee un archivo (relativo al cwd del chat).", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "max_chars": {"type": "integer"}}, "required": ["path"], "additionalProperties": False}},
            },
            {
                "type": "function",
                "function": {"name": "write_file", "description": "Crea o reemplaza un archivo (relativo al cwd del chat).", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}, "overwrite": {"type": "boolean"}, "create_dirs": {"type": "boolean"}}, "required": ["path", "content"], "additionalProperties": False}},
            },
            {
                "type": "function",
                "function": {"name": "append_file", "description": "Append a un archivo (relativo al cwd del chat).", "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}, "create_dirs": {"type": "boolean"}}, "required": ["path", "content"], "additionalProperties": False}},
            },
            {
                "type": "function",
                "function": {"name": "remove_path", "description": "Elimina un archivo/carpeta (relativo al cwd del chat).", "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"], "additionalProperties": False}},
            },
        ]

    def _emit_tool_call(self, emit: EventFn, name: str, display_command: str, extra: dict[str, Any] | None = None) -> None:
        payload: dict[str, Any] = {"name": name, "command": display_command}
        if extra:
            payload.update(extra)
        emit("tool_call", payload)

    def _emit_tool_output(self, emit: EventFn, name: str, display_command: str, out: dict[str, Any]) -> None:
        emit("tool_output", {"name": name, "command": display_command, "result": out})

    def _get_chat_cwd(self, chat_id: int) -> Path:
        cwd = self._cwd_by_chat.get(chat_id)
        if cwd is None:
            cwd = self.root
            self._cwd_by_chat[chat_id] = cwd
        return cwd

    def _set_chat_cwd(self, chat_id: int, new_cwd: Path) -> None:
        self._cwd_by_chat[chat_id] = new_cwd

    def _path_is_within_root(self, p: Path) -> bool:
        try:
            p.resolve().relative_to(self.root.resolve())
            return True
        except Exception:
            return False

    def _resolve_fs_path_for_chat(self, chat_id: int, user_path: str) -> str:
        """
        Convierte user_path (relativo al cwd del chat) a una ruta RELATIVA AL ROOT del FsTools.

        Ej:
          root = C:\...\proyectos_python_piloto
          cwd(chat) = root\api_hello_world

          user_path="app.py"        -> "api_hello_world/app.py"
          user_path="src/app.py"    -> "api_hello_world/src/app.py"
          user_path="."             -> "api_hello_world"
          user_path="api_hello_world" (estando en root) -> "api_hello_world"
          user_path="C:\...\root\api_hello_world\app.py" -> "api_hello_world/app.py" (si está dentro del root)
        """
        up = (user_path or "").strip()
        if not up:
            up = "."

        # Si es absoluta y está dentro del root, la convertimos a relativa al root
        p = Path(up)
        if p.is_absolute():
            p_res = p.resolve()
            if not self._path_is_within_root(p_res):
                raise ValueError("ruta absoluta fuera del sandbox")
            rel = p_res.relative_to(self.root.resolve()).as_posix()
            return rel or "."

        # Relativa: la anclamos al cwd del chat (pero devolvemos relativa al root)
        cwd = self._get_chat_cwd(chat_id).resolve()
        rel_cwd = cwd.relative_to(self.root.resolve()).as_posix()  # e.g. "api_hello_world" o "."
        if up in [".", "./", ".\\"]:
            return rel_cwd if rel_cwd else "."

        # Normaliza separadores
        # up = up.replace("\\", "/").lstrip("/")
        # if rel_cwd and rel_cwd != ".":
        #     return f"{rel_cwd}/{up}"
        # return up
    
        # Normaliza separadores
        up = up.replace("\\", "/").lstrip("/")

        # Si el usuario ya dio un path relativo al ROOT (ej: "prueba_terraform/main.tf"),
        # no lo volvemos a prefijar con el cwd.
        if rel_cwd and rel_cwd != ".":
            # up ya incluye el cwd (o está "dentro" de ese prefijo)
            if up == rel_cwd or up.startswith(rel_cwd + "/"):
                return up
            return f"{rel_cwd}/{up}"

        return up

    def _handle_cd(self, chat_id: int, cmd: str) -> dict[str, Any] | None:
        m = re.match(r"^\s*cd\s+(.+)\s*$", cmd, re.IGNORECASE)
        if not m:
            return None

        raw_path = m.group(1).strip().strip('"').strip("'")
        try:
            # Caso 1: cd absoluto dentro del root (permitido)
            p = Path(raw_path)
            if p.is_absolute():
                p_res = p.resolve()
                if not self._path_is_within_root(p_res):
                    return {"ok": False, "returncode": None, "output": "cd fuera del sandbox (no permitido)"}
                if not p_res.exists() or not p_res.is_dir():
                    return {"ok": False, "returncode": None, "output": f"No es directorio: {raw_path}"}
                self._set_chat_cwd(chat_id, p_res)
                return {"ok": True, "returncode": 0, "output": f"[cwd] {str(p_res)}"}

            # Caso 2: cd relativo (siempre relativo al cwd del chat, pero sin salir del root)
            # Convertimos a una ruta relativa al root y luego a path absoluto dentro del root
            rel_to_root = self._resolve_fs_path_for_chat(chat_id, raw_path)
            target_abs = (self.root / Path(rel_to_root)).resolve()

            if not self._path_is_within_root(target_abs):
                return {"ok": False, "returncode": None, "output": "cd fuera del sandbox (no permitido)"}
            if not target_abs.exists() or not target_abs.is_dir():
                return {"ok": False, "returncode": None, "output": f"No es directorio: {raw_path}"}

            self._set_chat_cwd(chat_id, target_abs)
            return {"ok": True, "returncode": 0, "output": f"[cwd] {str(target_abs)}"}
        except Exception as e:
            return {"ok": False, "returncode": None, "output": f"[cd error] {e}"}

    def run(self, chat_id: int, user_text: str, emit: EventFn) -> str:
        chat = self.chats.get(chat_id)
        if not chat:
            raise ValueError("Chat not found")

        project_id = int(chat["project_id"])
        instructions = self._build_instructions(project_id)

        # Siempre empezamos desde root (evita arrastre raro entre tareas)
        #self._set_chat_cwd(chat_id, self.root)

        # Mantener cwd persistente por chat.
        # Si no hay cwd aún, inicializamos en root.
        _ = self._get_chat_cwd(chat_id)

        self.visible.start_if_needed()
        self.visible.append(f"\n[CHAT #{chat_id}] User: {user_text}\n")

        self.messages.add(chat_id, "user", user_text)

        history = self._load_history(chat_id, limit=40)
        convo: list[dict[str, Any]] = [{"role": "system", "content": instructions}]
        convo += [{"role": t.role, "content": t.content} for t in history]

        emit("status", {"text": "Armando plan / decidiendo acciones..."})

        max_loops = int(os.environ.get("AGENT_MAX_LOOPS", "20"))
        final_text = ""
        nudge_count = 0

        last_tool_ok: Optional[bool] = None
        last_tool_cmd: str = ""
        last_tool_output: str = ""

        for _ in range(max_loops):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=convo,
                    tools=self._tools(),
                    tool_choice="auto",
                )
            except (APIConnectionError,) as e:
                final_text = f"Error de conexión con OpenAI: {e}"
                break
            except (APIStatusError,) as e:
                final_text = f"Error API OpenAI ({e.status_code}): {getattr(e, 'message', str(e))}"
                break
            except (APIError,) as e:
                final_text = f"Error OpenAI: {e}"
                break
            except Exception as e:
                final_text = f"Error inesperado: {e}"
                break

            msg = resp.choices[0].message
            tool_calls = getattr(msg, "tool_calls", None) or []

            assistant_entry: dict[str, Any] = {"role": "assistant", "content": msg.content or ""}
            if tool_calls:
                assistant_entry["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in tool_calls
                ]

            if msg.content:
                emit("assistant_chunk", {"text": msg.content})
                final_text = msg.content
                self.visible.append(f"\n[ASSISTANT]\n{msg.content}\n")

            convo.append(assistant_entry)

            # Si no hay tools y venimos de error, obligar a corregir
            if not tool_calls:
                if last_tool_ok is False and nudge_count < 4:
                    nudge_count += 1
                    convo.append(
                        {
                            "role": "user",
                            "content": (
                                "Falló el último comando y aún no has completado el objetivo. "
                                "Corrige y continúa EJECUTANDO tools.\n\n"
                                f"CWD actual: {str(self._get_chat_cwd(chat_id))}\n"
                                f"Último comando: {last_tool_cmd}\n"
                                f"Output:\n{last_tool_output[:2500]}\n\n"
                                "Pista: si el error es 'No such file', verifica con list_dir y crea con write_file "
                                "(recuerda: write_file es relativo al cwd del chat)."
                            ),
                        }
                    )
                    continue
                break

            for tc in tool_calls:
                fn_name = tc.function.name
                args_raw = tc.function.arguments or "{}"
                try:
                    args = json.loads(args_raw)
                except Exception:
                    args = {}

                out: dict[str, Any]
                display_cmd = fn_name

                if fn_name == "run_shell":
                    cmd = str(args.get("command", "")).strip()
                    timeout_s = args.get("timeout_seconds", None)
                    display_cmd = cmd if cmd else "run_shell"

                    cd_out = self._handle_cd(chat_id, cmd)
                    if cd_out is not None:
                        cwd_now = str(self._get_chat_cwd(chat_id))
                        self._emit_tool_call(emit, "run_shell", display_cmd, {"timeout_seconds": timeout_s, "cwd": cwd_now})
                        out = cd_out
                        self._emit_tool_output(emit, "run_shell", display_cmd, out)
                    else:
                        cwd_now = str(self._get_chat_cwd(chat_id))
                        self._emit_tool_call(emit, "run_shell", display_cmd, {"timeout_seconds": timeout_s, "cwd": cwd_now})
                        out = self.shell.run(cmd, timeout=timeout_s, cwd=cwd_now)
                        self._emit_tool_output(emit, "run_shell", display_cmd, out)

                    last_tool_ok = bool(out.get("ok"))
                    last_tool_cmd = display_cmd
                    last_tool_output = str(out.get("output") or "")

                elif fn_name == "pwd":
                    cwd_now = str(self._get_chat_cwd(chat_id))
                    display_cmd = "pwd"
                    self._emit_tool_call(emit, "pwd", display_cmd)
                    out = {"ok": True, "output": cwd_now}
                    self._emit_tool_output(emit, "pwd", display_cmd, out)

                    last_tool_ok = True
                    last_tool_cmd = display_cmd
                    last_tool_output = cwd_now

                elif fn_name == "fs_root":
                    display_cmd = "fs_root"
                    self._emit_tool_call(emit, "fs_root", display_cmd)
                    out = {"ok": True, "output": str(self.root)}
                    self._emit_tool_output(emit, "fs_root", display_cmd, out)

                    last_tool_ok = True
                    last_tool_cmd = display_cmd
                    last_tool_output = str(self.root)

                elif fn_name == "list_dir":
                    path = str(args.get("path", "."))
                    try:
                        relp = self._resolve_fs_path_for_chat(chat_id, path)
                        display_cmd = f"list_dir {path}"
                        self._emit_tool_call(emit, "list_dir", display_cmd, {"resolved": relp})
                        r = self.fs.list_dir(path=relp)
                        out = {"ok": r.ok, "output": r.output, "meta": r.meta or {}, "resolved": relp}
                    except Exception as e:
                        out = {"ok": False, "output": f"[fs error] {e}"}
                    self._emit_tool_output(emit, "list_dir", display_cmd, out)

                    last_tool_ok = bool(out.get("ok"))
                    last_tool_cmd = display_cmd
                    last_tool_output = str(out.get("output") or "")

                elif fn_name == "make_dirs":
                    path = str(args.get("path", ""))
                    try:
                        relp = self._resolve_fs_path_for_chat(chat_id, path)
                        display_cmd = f"make_dirs {path}"
                        self._emit_tool_call(emit, "make_dirs", display_cmd, {"resolved": relp})
                        r = self.fs.make_dirs(path=relp)
                        out = {"ok": r.ok, "output": r.output, "meta": r.meta or {}, "resolved": relp}
                    except Exception as e:
                        out = {"ok": False, "output": f"[fs error] {e}"}
                    self._emit_tool_output(emit, "make_dirs", display_cmd, out)

                    last_tool_ok = bool(out.get("ok"))
                    last_tool_cmd = display_cmd
                    last_tool_output = str(out.get("output") or "")

                elif fn_name == "read_file":
                    path = str(args.get("path", ""))
                    max_chars = int(args.get("max_chars", 200_000))
                    try:
                        relp = self._resolve_fs_path_for_chat(chat_id, path)
                        display_cmd = f"read_file {path}"
                        self._emit_tool_call(emit, "read_file", display_cmd, {"resolved": relp})
                        r = self.fs.read_text(path=relp, max_chars=max_chars)
                        out = {"ok": r.ok, "output": r.output, "meta": r.meta or {}, "resolved": relp}
                    except Exception as e:
                        out = {"ok": False, "output": f"[fs error] {e}"}
                    self._emit_tool_output(emit, "read_file", display_cmd, out)

                    last_tool_ok = bool(out.get("ok"))
                    last_tool_cmd = display_cmd
                    last_tool_output = str(out.get("output") or "")

                elif fn_name == "write_file":
                    path = str(args.get("path", ""))
                    content = str(args.get("content", ""))
                    overwrite = bool(args.get("overwrite", True))
                    create_dirs = bool(args.get("create_dirs", True))
                    try:
                        relp = self._resolve_fs_path_for_chat(chat_id, path)
                        display_cmd = f"write_file {path}"
                        self._emit_tool_call(emit, "write_file", display_cmd, {"resolved": relp})
                        r = self.fs.write_text(path=relp, content=content, overwrite=overwrite, create_dirs=create_dirs)
                        out = {"ok": r.ok, "output": r.output, "meta": r.meta or {}, "resolved": relp}
                    except Exception as e:
                        out = {"ok": False, "output": f"[fs error] {e}"}
                    self._emit_tool_output(emit, "write_file", display_cmd, out)

                    last_tool_ok = bool(out.get("ok"))
                    last_tool_cmd = display_cmd
                    last_tool_output = str(out.get("output") or "")

                elif fn_name == "append_file":
                    path = str(args.get("path", ""))
                    content = str(args.get("content", ""))
                    create_dirs = bool(args.get("create_dirs", True))
                    try:
                        relp = self._resolve_fs_path_for_chat(chat_id, path)
                        display_cmd = f"append_file {path}"
                        self._emit_tool_call(emit, "append_file", display_cmd, {"resolved": relp})
                        r = self.fs.append_text(path=relp, content=content, create_dirs=create_dirs)
                        out = {"ok": r.ok, "output": r.output, "meta": r.meta or {}, "resolved": relp}
                    except Exception as e:
                        out = {"ok": False, "output": f"[fs error] {e}"}
                    self._emit_tool_output(emit, "append_file", display_cmd, out)

                    last_tool_ok = bool(out.get("ok"))
                    last_tool_cmd = display_cmd
                    last_tool_output = str(out.get("output") or "")

                elif fn_name == "remove_path":
                    path = str(args.get("path", ""))
                    try:
                        relp = self._resolve_fs_path_for_chat(chat_id, path)
                        display_cmd = f"remove_path {path}"
                        self._emit_tool_call(emit, "remove_path", display_cmd, {"resolved": relp})
                        r = self.fs.remove_path(path=relp)
                        out = {"ok": r.ok, "output": r.output, "meta": r.meta or {}, "resolved": relp}
                    except Exception as e:
                        out = {"ok": False, "output": f"[fs error] {e}"}
                    self._emit_tool_output(emit, "remove_path", display_cmd, out)

                    last_tool_ok = bool(out.get("ok"))
                    last_tool_cmd = display_cmd
                    last_tool_output = str(out.get("output") or "")

                else:
                    display_cmd = fn_name
                    self._emit_tool_call(emit, fn_name, display_cmd)
                    out = {"ok": False, "output": f"Tool no soportada: {fn_name}"}
                    self._emit_tool_output(emit, fn_name, display_cmd, out)

                    last_tool_ok = False
                    last_tool_cmd = display_cmd
                    last_tool_output = str(out.get("output") or "")

                convo.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "name": fn_name,
                        "content": json.dumps(out, ensure_ascii=False),
                    }
                )

        if not final_text.strip():
            if last_tool_ok is False and last_tool_output:
                final_text = f"No se completó la tarea. Último error:\n{last_tool_cmd}\n{last_tool_output}"
            else:
                final_text = "Listo. (No hubo salida final clara del modelo.)"

        self.messages.add(chat_id, "assistant", final_text.strip())
        emit("final", {"text": final_text.strip()})
        self.visible.append(f"\n[FINAL]\n{final_text.strip()}\n")
        return final_text.strip()


_openai_client: Optional[OpenAI] = None


def get_openai_client() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        api_key = require_env("OPENAI_API_KEY")
        _openai_client = OpenAI(api_key=api_key)
    return _openai_client
