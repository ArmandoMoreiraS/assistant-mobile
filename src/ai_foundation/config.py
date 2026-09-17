"""Configuration module — loads and validates environment variables at startup."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    anthropic_api_key: str = Field(default="", description="Anthropic API key")
    google_api_key: str = Field(default="", description="Google Gemini API key")
    langchain_api_key: str = Field(default="", description="LangSmith API key")
    langchain_tracing_v2: bool = Field(default=False, description="Enable LangSmith tracing")


settings = Settings()
