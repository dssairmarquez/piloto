from __future__ import annotations
from typing import Any
from app.db import Db, utc_now_iso


class ChatsRepo:
    def __init__(self, db: Db) -> None:
        self.db = db

    def list_by_project(self, project_id: int) -> list[dict[str, Any]]:
        return self.db.fetchall(
            """
            SELECT id, project_id, title, created_at
            FROM chats
            WHERE project_id = ?
            ORDER BY id DESC
            """,
            (project_id,),
        )

    def create(self, project_id: int, title: str) -> int:
        return self.db.execute(
            "INSERT INTO chats(project_id, title, created_at) VALUES (?, ?, ?)",
            (project_id, title, utc_now_iso()),
        )

    def get(self, chat_id: int) -> dict[str, Any] | None:
        return self.db.fetchone(
            "SELECT id, project_id, title, created_at FROM chats WHERE id = ?",
            (chat_id,),
        )

    def delete(self, chat_id: int) -> None:
        self.db.execute("DELETE FROM chats WHERE id = ?", (chat_id,))
