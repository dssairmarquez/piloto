from __future__ import annotations
from typing import Any
from app.db import Db, utc_now_iso


class ProjectsRepo:
    def __init__(self, db: Db) -> None:
        self.db = db

    def list(self) -> list[dict[str, Any]]:
        return self.db.fetchall("SELECT id, name, created_at FROM projects ORDER BY id DESC")

    def create(self, name: str) -> int:
        return self.db.execute(
            "INSERT INTO projects(name, created_at) VALUES (?, ?)",
            (name, utc_now_iso()),
        )

    def get(self, project_id: int) -> dict[str, Any] | None:
        return self.db.fetchone(
            "SELECT id, name, created_at FROM projects WHERE id = ?",
            (project_id,),
        )

    def delete(self, project_id: int) -> None:
        self.db.execute("DELETE FROM projects WHERE id = ?", (project_id,))
