"""Extractor de información del usuario a partir del historial de conversación."""

import json
from typing import List, Optional

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

from ai_foundation.llm import get_llm
from ai_foundation.utils.logging import logger

from .models import Turn, UserProfile


class ExtractedInfo(BaseModel):
    name: Optional[str] = Field(
        default=None,
        description="El nombre del usuario si fue mencionado. None si no.",
    )
    new_likes: List[str] = Field(
        default_factory=list,
        description="Nuevas preferencias o gustos que el usuario mencionó.",
    )
    new_events: List[str] = Field(
        default_factory=list,
        description="Nuevos eventos o situaciones importantes que el usuario mencionó.",
    )


_EXTRACTION_SYSTEM = """Eres un asistente de extracción de información.
Tu tarea es analizar una conversación y extraer únicamente información personal del USUARIO (no del asistente):
- nombre del usuario (si lo mencionó)
- gustos, preferencias o cosas que le gustan
- eventos importantes de su vida

Responde SOLO con un objeto JSON válido con esta estructura exacta:
{
  "name": "nombre o null",
  "new_likes": ["gusto1", "gusto2"],
  "new_events": ["evento1", "evento2"]
}

Si no hay información nueva, usa listas vacías y null para el nombre."""


def extract_info(history: List[Turn], llm: BaseChatModel | None = None) -> ExtractedInfo:
    """Analiza el historial y extrae información sobre el usuario."""
    if not history:
        return ExtractedInfo()

    llm = llm or get_llm()

    history_text = "\n".join([f"{t.role}: {t.content}" for t in history[-10:]])
    messages = [
        SystemMessage(content=_EXTRACTION_SYSTEM),
        HumanMessage(content=f"Conversación:\n{history_text}"),
    ]

    try:
        response = llm.invoke(messages)
        raw = response.content
        if isinstance(raw, list):
            raw = next((item["text"] for item in raw if item.get("type") == "text"), "")

        # Limpiar posibles bloques markdown
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        data = json.loads(raw.strip())
        return ExtractedInfo(**data)
    except Exception as e:
        logger.error(f"Error en extracción de información del usuario: {e}")
        return ExtractedInfo()


def update_profile_from_extraction(profile: UserProfile, extracted: ExtractedInfo) -> UserProfile:
    """Aplica la información extraída al perfil del usuario sin borrar datos previos."""
    if extracted.name and not profile.name:
        profile.name = extracted.name

    for like in extracted.new_likes:
        if like and like not in profile.likes:
            profile.likes.append(like)

    for event in extracted.new_events:
        if event and event not in profile.events:
            profile.events.append(event)

    return profile
