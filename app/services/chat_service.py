from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from openai import OpenAI
from openai import APIError, APIConnectionError, APIStatusError

from app.config import BASE_INSTRUCTIONS, DEFAULT_MODEL
from app.repositories.chats_repo import ChatsRepo
from app.repositories.contexts_repo import ContextsRepo
from app.repositories.messages_repo import MessagesRepo


def require_env(name: str) -> str:
    import os

    val = os.environ.get(name, "").strip()
    if not val:
        raise RuntimeError(f"Missing environment variable: {name}")
    return val


@dataclass(frozen=True)
class ChatTurn:
    role: str
    content: str


class ChatService:
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

    def _build_instructions(self, project_id: int) -> str:
        actives = self.contexts.active_contexts_for_project(project_id)
        if not actives:
            return BASE_INSTRUCTIONS

        joined = "\n\n".join(
            [f"[{c['name']}]\n{c['content']}".strip() for c in actives]
        )
        return (
            BASE_INSTRUCTIONS
            + "\n\n"
            + "Contextos activos del proyecto (prioritarios):\n"
            + joined
        )

    def _load_history(self, chat_id: int, limit: int = 40) -> list[ChatTurn]:
        msgs = self.messages.list_by_chat(chat_id)
        if len(msgs) > limit:
            msgs = msgs[-limit:]
        return [ChatTurn(m["role"], m["content"]) for m in msgs]

    def send_user_message(self, chat_id: int, user_text: str) -> str:
        chat = self.chats.get(chat_id)
        if not chat:
            raise ValueError("Chat not found")

        project_id = int(chat["project_id"])
        instructions = self._build_instructions(project_id)

        self.messages.add(chat_id, "user", user_text)

        history = self._load_history(chat_id, limit=40)
        input_items = [{"role": t.role, "content": t.content} for t in history]

        try:
            response = self.client.responses.create(
                model=self.model,
                instructions=instructions,
                input=input_items,
            )
            assistant_text = (response.output_text or "").strip()
            if not assistant_text:
                assistant_text = "Lo siento, no pude generar una respuesta."
        except (APIConnectionError,) as e:
            assistant_text = f"Error de conexión con OpenAI: {e}"
        except (APIStatusError,) as e:
            assistant_text = f"Error API OpenAI ({e.status_code}): {getattr(e, 'message', str(e))}"
        except (APIError,) as e:
            assistant_text = f"Error OpenAI: {e}"
        except Exception as e:
            assistant_text = f"Error inesperado: {e}"

        self.messages.add(chat_id, "assistant", assistant_text)
        return assistant_text


_openai_client: Optional[OpenAI] = None


def get_openai_client() -> OpenAI:
    global _openai_client
    if _openai_client is None:
        api_key = require_env("OPENAI_API_KEY")
        _openai_client = OpenAI(api_key=api_key)
    return _openai_client
