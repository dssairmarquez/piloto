from __future__ import annotations
from typing import Any
from app.db import Db, utc_now_iso


class ContextsRepo:
    def __init__(self, db: Db) -> None:
        self.db = db

    # ---------- Global contexts ----------
    def list_contexts(self) -> list[dict[str, Any]]:
        return self.db.fetchall(
            "SELECT id, name, content, created_at FROM contexts ORDER BY id DESC"
        )

    def create_context(self, name: str, content: str) -> int:
        return self.db.execute(
            "INSERT INTO contexts(name, content, created_at) VALUES (?, ?, ?)",
            (name, content, utc_now_iso()),
        )

    def delete_context(self, context_id: int) -> None:
        self.db.execute("DELETE FROM contexts WHERE id = ?", (context_id,))

    def get_context(self, context_id: int) -> dict[str, Any] | None:
        return self.db.fetchone(
            "SELECT id, name, content, created_at FROM contexts WHERE id = ?",
            (context_id,),
        )

    # ---------- Project bindings ----------
    def list_project_contexts(self, project_id: int) -> list[dict[str, Any]]:
        # devuelve todos los contextos, con estado activo/inactivo para el proyecto
        return self.db.fetchall(
            """
            SELECT c.id, c.name, c.content, c.created_at,
                   COALESCE(pc.is_active, 0) AS is_active,
                   CASE WHEN pc.project_id IS NULL THEN 0 ELSE 1 END AS is_linked
            FROM contexts c
            LEFT JOIN project_contexts pc
              ON pc.context_id = c.id AND pc.project_id = ?
            ORDER BY COALESCE(pc.is_active,0) DESC, c.id DESC
            """,
            (project_id,),
        )

    def toggle_project_context(self, project_id: int, context_id: int, is_active: bool) -> None:
        # upsert binding
        with self.db.connect() as conn:
            conn.execute(
                """
                INSERT INTO project_contexts(project_id, context_id, is_active)
                VALUES (?, ?, ?)
                ON CONFLICT(project_id, context_id)
                DO UPDATE SET is_active = excluded.is_active
                """,
                (project_id, context_id, 1 if is_active else 0),
            )

    def active_contexts_for_project(self, project_id: int) -> list[dict[str, Any]]:
        return self.db.fetchall(
            """
            SELECT c.id, c.name, c.content, c.created_at
            FROM contexts c
            INNER JOIN project_contexts pc
              ON pc.context_id = c.id
            WHERE pc.project_id = ? AND pc.is_active = 1
            ORDER BY c.id ASC
            """,
            (project_id,),
        )

    # ---------- Groups ----------
    def list_groups(self) -> list[dict[str, Any]]:
        return self.db.fetchall(
            "SELECT id, name, created_at FROM context_groups ORDER BY id DESC"
        )

    def create_group(self, name: str) -> int:
        return self.db.execute(
            "INSERT INTO context_groups(name, created_at) VALUES (?, ?)",
            (name, utc_now_iso()),
        )

    def delete_group(self, group_id: int) -> None:
        self.db.execute("DELETE FROM context_groups WHERE id = ?", (group_id,))

    def get_group(self, group_id: int) -> dict[str, Any] | None:
        return self.db.fetchone(
            "SELECT id, name, created_at FROM context_groups WHERE id = ?",
            (group_id,),
        )

    def group_items(self, group_id: int) -> list[int]:
        rows = self.db.fetchall(
            "SELECT context_id FROM context_group_items WHERE group_id = ? ORDER BY context_id ASC",
            (group_id,),
        )
        return [int(r["context_id"]) for r in rows]

    def set_group_items(self, group_id: int, context_ids: list[int]) -> None:
        with self.db.connect() as conn:
            conn.execute("DELETE FROM context_group_items WHERE group_id = ?", (group_id,))
            for cid in context_ids:
                conn.execute(
                    "INSERT INTO context_group_items(group_id, context_id) VALUES (?, ?)",
                    (group_id, cid),
                )

    def apply_group_to_project(self, project_id: int, group_id: int, is_active: bool) -> None:
        context_ids = self.group_items(group_id)
        with self.db.connect() as conn:
            for cid in context_ids:
                conn.execute(
                    """
                    INSERT INTO project_contexts(project_id, context_id, is_active)
                    VALUES (?, ?, ?)
                    ON CONFLICT(project_id, context_id)
                    DO UPDATE SET is_active = excluded.is_active
                    """,
                    (project_id, cid, 1 if is_active else 0),
                )
