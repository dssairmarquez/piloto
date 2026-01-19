from __future__ import annotations

import json
import queue
import threading
from typing import Any, Iterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.db import Db
from app.models import SendMessageIn
from app.repositories.chats_repo import ChatsRepo
from app.repositories.contexts_repo import ContextsRepo
from app.repositories.messages_repo import MessagesRepo
from app.services.chat_service import ChatService
from app.services.agent_service import AgentService, get_openai_client

router = APIRouter(prefix="/api", tags=["chats"])

db = Db()
chats = ChatsRepo(db)
messages = MessagesRepo(db)
contexts = ContextsRepo(db)


@router.get("/chats/{chat_id}")
def get_chat(chat_id: int) -> dict[str, Any]:
    ch = chats.get(chat_id)
    if not ch:
        raise HTTPException(status_code=404, detail="Chat not found")
    return ch


@router.delete("/chats/{chat_id}")
def delete_chat(chat_id: int) -> dict[str, Any]:
    if not chats.get(chat_id):
        raise HTTPException(status_code=404, detail="Chat not found")
    chats.delete(chat_id)
    return {"ok": True}


@router.get("/chats/{chat_id}/messages")
def list_messages(chat_id: int) -> list[dict[str, Any]]:
    if not chats.get(chat_id):
        raise HTTPException(status_code=404, detail="Chat not found")
    msgs = messages.list_by_chat(chat_id)
    return [{"role": m["role"], "content": m["content"], "created_at": m["created_at"]} for m in msgs]


# --- Modo clásico (sin streaming, sin tools) ---
@router.post("/chats/{chat_id}/messages")
def send_message(chat_id: int, payload: SendMessageIn) -> dict[str, Any]:
    if not chats.get(chat_id):
        raise HTTPException(status_code=404, detail="Chat not found")

    service = ChatService(
        chats=chats,
        messages=messages,
        contexts=contexts,
        client=get_openai_client(),
    )

    try:
        assistant_text = service.send_user_message(chat_id, payload.content.strip())
        return {"assistant": assistant_text}
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {e}")


# --- Modo AGENTE (streaming real + ejecución de comandos) ---
@router.post("/chats/{chat_id}/agent-stream")
def agent_stream(chat_id: int, payload: SendMessageIn) -> StreamingResponse:
    if not chats.get(chat_id):
        raise HTTPException(status_code=404, detail="Chat not found")

    agent = AgentService(
        chats=chats,
        messages=messages,
        contexts=contexts,
        client=get_openai_client(),
    )

    def sse(event: str, data: dict[str, Any]) -> bytes:
        return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n".encode("utf-8")

    q: queue.Queue[bytes | None] = queue.Queue()

    def emit_cb(event: str, data: dict[str, Any]) -> None:
        q.put(sse(event, data))

    def worker() -> None:
        try:
            emit_cb("status", {"text": "Iniciando agente..."})
            agent.run(chat_id, payload.content.strip(), emit_cb)
        except Exception as e:
            emit_cb("error", {"text": str(e)})
        finally:
            q.put(None)  # sentinel

    t = threading.Thread(target=worker, daemon=True)
    t.start()

    def gen() -> Iterator[bytes]:
        while True:
            item = q.get()
            if item is None:
                break
            yield item
        yield sse("done", {"ok": True})

    return StreamingResponse(gen(), media_type="text/event-stream")
