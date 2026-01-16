from __future__ import annotations
from typing import Any

from fastapi import APIRouter, HTTPException

from app.db import Db
from app.models import (
    ApplyGroupToProjectIn,
    CreateContextIn,
    CreateGroupIn,
    SetGroupItemsIn,
    ToggleProjectContextIn,
)
from app.repositories.projects_repo import ProjectsRepo
from app.repositories.contexts_repo import ContextsRepo

router = APIRouter(prefix="/api", tags=["contexts"])

db = Db()
projects = ProjectsRepo(db)
ctx = ContextsRepo(db)


# -------- Global contexts --------
@router.get("/contexts")
def list_contexts() -> list[dict[str, Any]]:
    return ctx.list_contexts()


@router.post("/contexts")
def create_context(payload: CreateContextIn) -> dict[str, Any]:
    cid = ctx.create_context(payload.name.strip(), payload.content.strip())
    return {"id": cid}


@router.delete("/contexts/{context_id}")
def delete_context(context_id: int) -> dict[str, Any]:
    if not ctx.get_context(context_id):
        raise HTTPException(status_code=404, detail="Context not found")
    ctx.delete_context(context_id)
    return {"ok": True}


# -------- Project view of contexts --------
@router.get("/projects/{project_id}/contexts")
def list_contexts_for_project(project_id: int) -> list[dict[str, Any]]:
    if not projects.get(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    return ctx.list_project_contexts(project_id)


@router.post("/projects/{project_id}/contexts/toggle")
def toggle_context_for_project(project_id: int, payload: ToggleProjectContextIn) -> dict[str, Any]:
    if not projects.get(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    if not ctx.get_context(payload.context_id):
        raise HTTPException(status_code=404, detail="Context not found")
    ctx.toggle_project_context(project_id, payload.context_id, payload.is_active)
    return {"ok": True}


# -------- Groups --------
@router.get("/context-groups")
def list_groups() -> list[dict[str, Any]]:
    return ctx.list_groups()


@router.post("/context-groups")
def create_group(payload: CreateGroupIn) -> dict[str, Any]:
    gid = ctx.create_group(payload.name.strip())
    return {"id": gid}


@router.delete("/context-groups/{group_id}")
def delete_group(group_id: int) -> dict[str, Any]:
    if not ctx.get_group(group_id):
        raise HTTPException(status_code=404, detail="Group not found")
    ctx.delete_group(group_id)
    return {"ok": True}


@router.get("/context-groups/{group_id}/items")
def get_group_items(group_id: int) -> dict[str, Any]:
    if not ctx.get_group(group_id):
        raise HTTPException(status_code=404, detail="Group not found")
    return {"context_ids": ctx.group_items(group_id)}


@router.post("/context-groups/{group_id}/items")
def set_group_items(group_id: int, payload: SetGroupItemsIn) -> dict[str, Any]:
    if not ctx.get_group(group_id):
        raise HTTPException(status_code=404, detail="Group not found")
    # valida ids existentes (simple)
    for cid in payload.context_ids:
        if not ctx.get_context(cid):
            raise HTTPException(status_code=404, detail=f"Context not found: {cid}")
    ctx.set_group_items(group_id, payload.context_ids)
    return {"ok": True}


@router.post("/projects/{project_id}/contexts/apply-group")
def apply_group_to_project(project_id: int, payload: ApplyGroupToProjectIn) -> dict[str, Any]:
    if not projects.get(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    if not ctx.get_group(payload.group_id):
        raise HTTPException(status_code=404, detail="Group not found")
    ctx.apply_group_to_project(project_id, payload.group_id, payload.is_active)
    return {"ok": True}
