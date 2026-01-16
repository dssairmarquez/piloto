from __future__ import annotations
import os

DB_PATH = os.environ.get("APP_DB_PATH", "app.db")
DEFAULT_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

APP_TITLE = "MiniGPT Projects"

BASE_INSTRUCTIONS = (
    "Eres un asistente útil, claro y conciso. "
    "Si falta información, haz preguntas concretas. "
    "Responde en el mismo idioma del usuario."
)
