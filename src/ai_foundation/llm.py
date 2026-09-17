"""LLM factory — centralises LLM client construction for Google Gemini."""

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI

from ai_foundation.config import settings


def get_llm(
    model: str | None = None,
    temperature: float = 0.0,
) -> BaseChatModel:
    """Return a configured LLM instance.

    Parameters
    ----------
    model:
        Model name. Defaults to 'gemini-3.6-flash' for Gemini.
    temperature:
        Sampling temperature in [0.0, 2.0] (default: 0.0 for deterministic output).

    Returns
    -------
    BaseChatModel
        A configured LangChain chat model instance.
    """
    return ChatGoogleGenerativeAI(
        model=model or "gemini-3.6-flash",
        temperature=temperature,
        google_api_key=settings.google_api_key or None,
    )
