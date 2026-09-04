"""Application configuration, loaded from environment variables / .env.

Single source of truth for every tunable value referenced across the
backend, so nothing hardcodes a model name or a path in more than one place.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    gemini_api_key: str = ""
    # Deprecated single-model settings — kept for backward compatibility
    # with any existing .env, but app.ai.gemini_client now tries a whole
    # ordered chain of models (see MODEL_FALLBACK_CHAIN there) rather than
    # a single fixed one, so these two values are no longer read directly.
    gemini_model_fast: str = "gemini-3.5-flash"
    gemini_model_reasoning: str = "gemini-3.5-flash"

    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    database_path: str = "./data/mandateops.db"

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def gemini_configured(self) -> bool:
        return bool(self.gemini_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
