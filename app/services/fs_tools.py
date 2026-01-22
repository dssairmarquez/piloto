from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class FsResult:
    ok: bool
    output: str
    meta: dict[str, Any] | None = None


class FsTools:
    """
    Herramientas de filesystem para el agente, con un directorio raíz (sandbox) configurable.

    - No permite escapar del root (previene ../../).
    - Crea carpetas automáticamente cuando se escribe archivo (opcional).
    """

    def __init__(self, root: str | None = None) -> None:
        root_env = (os.environ.get("AGENT_WORKDIR") or "").strip()
        self.root = Path(root or root_env or "C:/Users/Interno/Documents/proyectos_python_piloto").resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _resolve(self, user_path: str) -> Path:
        up = (user_path or "").strip()
        if not up:
            raise ValueError("path vacío")
        # Normaliza y asegura ruta relativa
        up = up.replace("\\", "/")
        rel = Path(up)
        if rel.is_absolute():
            # Si te pasan absoluta, la tratamos como relativa (sin / inicial)
            rel = Path(*rel.parts[1:]) if len(rel.parts) > 1 else Path(rel.name)

        full = (self.root / rel).resolve()

        # Seguridad: no salir del root
        try:
            full.relative_to(self.root)
        except Exception:
            raise ValueError("ruta inválida (escape del directorio raíz)")

        return full

    def info_root(self) -> FsResult:
        return FsResult(ok=True, output=str(self.root))

    def list_dir(self, path: str = ".") -> FsResult:
        try:
            p = self._resolve(path)
            if not p.exists():
                return FsResult(ok=False, output=f"No existe: {path}")
            if not p.is_dir():
                return FsResult(ok=False, output=f"No es directorio: {path}")

            items = []
            for child in sorted(p.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                typ = "dir" if child.is_dir() else "file"
                size = ""
                if child.is_file():
                    try:
                        size = f" ({child.stat().st_size} bytes)"
                    except Exception:
                        size = ""
                rel = child.relative_to(self.root).as_posix()
                items.append(f"- [{typ}] {rel}{size}")

            out = "\n".join(items) if items else "(vacío)"
            return FsResult(ok=True, output=out)
        except Exception as e:
            return FsResult(ok=False, output=f"[fs error] {e}")

    def make_dirs(self, path: str) -> FsResult:
        try:
            p = self._resolve(path)
            p.mkdir(parents=True, exist_ok=True)
            rel = p.relative_to(self.root).as_posix()
            return FsResult(ok=True, output=f"Directorio listo: {rel}")
        except Exception as e:
            return FsResult(ok=False, output=f"[fs error] {e}")

    def read_text(self, path: str, max_chars: int = 200_000) -> FsResult:
        try:
            p = self._resolve(path)
            if not p.exists():
                return FsResult(ok=False, output=f"No existe: {path}")
            if not p.is_file():
                return FsResult(ok=False, output=f"No es archivo: {path}")

            data = p.read_text(encoding="utf-8", errors="replace")
            if len(data) > max_chars:
                data = data[:max_chars] + "\n\n[... truncado ...]"
            return FsResult(ok=True, output=data, meta={"path": path})
        except Exception as e:
            return FsResult(ok=False, output=f"[fs error] {e}")

    def write_text(
        self,
        path: str,
        content: str,
        overwrite: bool = True,
        create_dirs: bool = True,
    ) -> FsResult:
        try:
            p = self._resolve(path)
            if create_dirs:
                p.parent.mkdir(parents=True, exist_ok=True)

            if p.exists() and (not overwrite):
                return FsResult(ok=False, output=f"Ya existe y overwrite=false: {path}")

            p.write_text(content or "", encoding="utf-8", errors="replace")
            rel = p.relative_to(self.root).as_posix()
            return FsResult(ok=True, output=f"Escrito: {rel} ({len(content or '')} chars)")
        except Exception as e:
            return FsResult(ok=False, output=f"[fs error] {e}")

    def append_text(self, path: str, content: str, create_dirs: bool = True) -> FsResult:
        try:
            p = self._resolve(path)
            if create_dirs:
                p.parent.mkdir(parents=True, exist_ok=True)

            with p.open("a", encoding="utf-8", errors="replace") as f:
                f.write(content or "")

            rel = p.relative_to(self.root).as_posix()
            return FsResult(ok=True, output=f"Append: {rel} (+{len(content or '')} chars)")
        except Exception as e:
            return FsResult(ok=False, output=f"[fs error] {e}")

    def remove_path(self, path: str) -> FsResult:
        try:
            p = self._resolve(path)
            if not p.exists():
                return FsResult(ok=False, output=f"No existe: {path}")

            if p.is_dir():
                shutil.rmtree(p)
                return FsResult(ok=True, output=f"Directorio eliminado: {path}")
            else:
                p.unlink()
                return FsResult(ok=True, output=f"Archivo eliminado: {path}")
        except Exception as e:
            return FsResult(ok=False, output=f"[fs error] {e}")
