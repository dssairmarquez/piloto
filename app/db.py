from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Any

from app.config import DB_PATH


def utc_now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


class Db:
    def __init__(self, path: str = DB_PATH) -> None:
        self.path = path
        self._init()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init(self) -> None:
        """
        Esquema nuevo:
        - contexts = globales
        - context_groups + context_group_items = agrupación
        - project_contexts = asignación y activación por proyecto (N a N)
        """
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS contexts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS context_groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS context_group_items (
                    group_id INTEGER NOT NULL,
                    context_id INTEGER NOT NULL,
                    PRIMARY KEY (group_id, context_id),
                    FOREIGN KEY(group_id) REFERENCES context_groups(id) ON DELETE CASCADE,
                    FOREIGN KEY(context_id) REFERENCES contexts(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS project_contexts (
                    project_id INTEGER NOT NULL,
                    context_id INTEGER NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 0,
                    PRIMARY KEY (project_id, context_id),
                    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE,
                    FOREIGN KEY(context_id) REFERENCES contexts(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS chats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('user','assistant')),
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(chat_id) REFERENCES chats(id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_chats_project ON chats(project_id);
                CREATE INDEX IF NOT EXISTS idx_messages_chat ON messages(chat_id);

                CREATE INDEX IF NOT EXISTS idx_proj_ctx_active
                  ON project_contexts(project_id, is_active);

                CREATE INDEX IF NOT EXISTS idx_ctx_groups_name
                  ON context_groups(name);
                """
            )

    def fetchall(self, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        with self.connect() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def fetchone(self, query: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute(query, params).fetchone()
            return dict(row) if row else None

    def execute(self, query: str, params: tuple[Any, ...] = ()) -> int:
        with self.connect() as conn:
            cur = conn.execute(query, params)
            return int(cur.lastrowid) if cur.lastrowid is not None else 0

    def executescript(self, script: str) -> None:
        with self.connect() as conn:
            conn.executescript(script)
