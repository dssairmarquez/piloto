from __future__ import annotations
from typing import Any
from app.db import Db, utc_now_iso


class MessagesRepo:
    def __init__(self, db: Db) -> None:
        self.db = db

    def list_by_chat(self, chat_id: int) -> list[dict[str, Any]]:
        return self.db.fetchall(
            """
            SELECT id, chat_id, role, content, created_at
            FROM messages
            WHERE chat_id = ?
            ORDER BY id ASC
            """,
            (chat_id,),
        )

    def add(self, chat_id: int, role: str, content: str) -> int:
        return self.db.execute(
            """
            INSERT INTO messages(chat_id, role, content, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (chat_id, role, content, utc_now_iso()),
        )
