from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from typing import Any, Callable, Optional

from openai import OpenAI
from openai import APIError, APIConnectionError, APIStatusError

from app.config import BASE_INSTRUCTIONS, DEFAULT_MODEL
from app.repositories.chats_repo import ChatsRepo
from app.repositories.contexts_repo import ContextsRepo
from app.repositories.messages_repo import MessagesRepo


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


class ShellRunner:
    def __init__(self) -> None:
        self.default_timeout = int(os.environ.get("AGENT_CMD_TIMEOUT_SECONDS", "3600"))

    def run(self, command: str, timeout: Optional[int] = None) -> dict[str, Any]:
        t = timeout if timeout is not None else self.default_timeout
        try:
            completed = subprocess.run(
                command,
                shell=True,
                text=True,
                capture_output=True,
                timeout=t,
            )
            out = (completed.stdout or "") + (completed.stderr or "")
            return {
                "ok": completed.returncode == 0,
                "returncode": completed.returncode,
                "output": out[-200_000:],
            }
        except subprocess.TimeoutExpired as e:
            out = ((e.stdout or "") + (e.stderr or "")).strip()
            return {
                "ok": False,
                "returncode": None,
                "output": (out + "\n\n[timeout]").strip(),
            }
        except Exception as e:
            return {"ok": False, "returncode": None, "output": f"[runner error] {e}"}


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
        self.shell = ShellRunner()

    def _agent_rules(self) -> str:
        return (
            "MODO AGENTE (OBLIGATORIO):\n"
            "- Si la tarea requiere varios pasos, primero crea un PLAN corto (lista numerada).\n"
            "- Luego ejecuta paso a paso.\n"
            "- Para ejecutar comandos usa la herramienta run_shell.\n"
            "- Regla dura: si afirmas que vas a ejecutar un comando, DEBES llamar run_shell en ese mismo turno.\n"
            "- Después del comando, evalúa el output y decide el siguiente paso.\n"
            "- No inventes outputs de consola.\n"
            "- Finaliza SOLO cuando el objetivo esté completado.\n"
        )

    def _build_instructions(self, project_id: int) -> str:
        actives = self.contexts.active_contexts_for_project(project_id)
        if not actives:
            return BASE_INSTRUCTIONS + "\n\n" + self._agent_rules()

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
                            "command": {"type": "string", "description": "Comando a ejecutar tal cual."},
                            "timeout_seconds": {"type": "integer", "description": "Timeout opcional (segundos)."},
                        },
                        "required": ["command"],
                        "additionalProperties": False,
                    },
                },
            }
        ]

    def _looks_like_it_should_run_tools(self, user_text: str, assistant_text: str) -> bool:
        ut = (user_text or "").lower()
        at = (assistant_text or "").lower()
        # Heurística simple: si el usuario pide acciones que típicamente requieren shell,
        # o el asistente dice "voy a ejecutar / ejecutaré / comando", entonces debería haber tool.
        signals_user = any(k in ut for k in ["archivo", "escritorio", "desktop", "ip", "ipconfig", "ifconfig", "crear", "guardar", "escribe", "write"])
        signals_assistant = any(k in at for k in ["ejecut", "comando", "voy a proceder", "voy a hacerlo ahora", "paso 1", "obtener la ip"])
        return signals_user or signals_assistant

    def run(self, chat_id: int, user_text: str, emit: EventFn) -> str:
        chat = self.chats.get(chat_id)
        if not chat:
            raise ValueError("Chat not found")

        project_id = int(chat["project_id"])
        instructions = self._build_instructions(project_id)

        # Guardamos mensaje usuario
        self.messages.add(chat_id, "user", user_text)

        # Historial para modelo
        history = self._load_history(chat_id, limit=40)
        convo: list[dict[str, Any]] = [{"role": "system", "content": instructions}]
        convo += [{"role": t.role, "content": t.content} for t in history]

        emit("status", {"text": "Armando plan / decidiendo acciones..."})

        max_loops = int(os.environ.get("AGENT_MAX_LOOPS", "12"))
        final_text = ""
        nudge_count = 0

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

            convo.append(assistant_entry)

            # Si no hubo tool_calls pero "debería", empujamos UNA VEZ (o dos max) al modelo a ejecutar.
            if not tool_calls and self._looks_like_it_should_run_tools(user_text, msg.content or "") and nudge_count < 2:
                nudge_count += 1
                convo.append(
                    {
                        "role": "user",
                        "content": (
                            "Continúa AHORA con el siguiente paso y EJECUTA el/los comando(s) necesarios usando run_shell. "
                            "No te quedes en el plan: ejecuta y luego analiza el output."
                        ),
                    }
                )
                continue

            if not tool_calls:
                break

            for tc in tool_calls:
                fn_name = tc.function.name
                args_raw = tc.function.arguments or "{}"
                try:
                    args = json.loads(args_raw)
                except Exception:
                    args = {"command": args_raw}

                if fn_name != "run_shell":
                    out = {"ok": False, "output": f"Tool no soportada: {fn_name}"}
                    cmd = ""
                    timeout_s = None
                else:
                    cmd = str(args.get("command", ""))
                    timeout_s = args.get("timeout_seconds", None)

                    emit("tool_call", {"name": "run_shell", "command": cmd, "timeout_seconds": timeout_s})
                    out = self.shell.run(cmd, timeout=timeout_s)
                    emit("tool_output", {"name": "run_shell", "command": cmd, "result": out})

                convo.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "name": fn_name,
                        "content": json.dumps(out, ensure_ascii=False),
                    }
                )

        if not final_text.strip():
            final_text = "Listo. (No hubo salida final clara del modelo.)"

        self.messages.add(chat_id, "assistant", final_text.strip())
        emit("final", {"text": final_text.strip()})
        return final_text.strip()


_openai_client: Optional[OpenAI] = None


def get_openai_client() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        api_key = require_env("OPENAI_API_KEY")
        _openai_client = OpenAI(api_key=api_key)
    return _openai_client
