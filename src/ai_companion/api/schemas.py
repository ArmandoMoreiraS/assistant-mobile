"""Schemas (DTOs) para la API REST del AI Companion."""

from pydantic import BaseModel


class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    response: str
    user_name: str | None = None


class ProfileResponse(BaseModel):
    user_id: str
    name: str | None = None
    likes: list[str] = []
    events: list[str] = []


class EndSessionRequest(BaseModel):
    user_id: str


class EndSessionResponse(BaseModel):
    message: str
    profile: ProfileResponse
