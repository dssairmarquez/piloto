from __future__ import annotations
from typing import Any

from fastapi import APIRouter, HTTPException

from app.db import Db
from app.models import CreateProjectIn
from app.repositories.projects_repo import ProjectsRepo
from app.repositories.chats_repo import ChatsRepo

router = APIRouter(prefix="/api", tags=["projects"])

db = Db()
projects = ProjectsRepo(db)
chats = ChatsRepo(db)


@router.get("/projects")
def list_projects() -> list[dict[str, Any]]:
    return projects.list()


@router.post("/projects")
def create_project(payload: CreateProjectIn) -> dict[str, Any]:
    pid = projects.create(payload.name.strip())
    return {"id": pid}


@router.get("/projects/{project_id}")
def get_project(project_id: int) -> dict[str, Any]:
    p = projects.get(project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return p


@router.delete("/projects/{project_id}")
def delete_project(project_id: int) -> dict[str, Any]:
    if not projects.get(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    projects.delete(project_id)
    return {"ok": True}


@router.get("/projects/{project_id}/chats")
def list_project_chats(project_id: int) -> list[dict[str, Any]]:
    if not projects.get(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    return chats.list_by_project(project_id)


@router.post("/projects/{project_id}/chats")
def create_project_chat(project_id: int, payload: dict) -> dict[str, Any]:
    if not projects.get(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    title = (payload.get("title") or "").strip()
    if not title:
        raise HTTPException(status_code=400, detail="Missing title")
    cid = chats.create(project_id, title)
    return {"id": cid}
