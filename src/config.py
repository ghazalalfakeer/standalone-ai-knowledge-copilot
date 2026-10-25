"""Typed application configuration loaded from environment variables."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "Standalone AI Knowledge Copilot"
    app_env: Literal["development", "test", "production"] = "development"
    log_level: str = "INFO"
    data_file: Path = PROJECT_ROOT / "data" / "sample_knowledge.json"

    gemini_api_key: SecretStr | None = None
    gemini_model: str = "gemini-3.8-flash"
    gemini_fallback_model: str | None = "gemini-3.6-flash"
    llm_temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    llm_max_output_tokens: int = Field(default=768, ge=1, le=65536)
    llm_structured_max_output_tokens: int = Field(default=2048, ge=256, le=65536)
    llm_thinking_level: Literal["low", "medium", "high"] = "low"
    llm_timeout_seconds: float = Field(default=60.0, gt=0.0, le=300.0)
    llm_max_retries: int = Field(default=2, ge=0, le=8)
    gemini_input_cost_per_1m_usd: float | None = Field(default=None, ge=0.0)
    gemini_output_cost_per_1m_usd: float | None = Field(default=None, ge=0.0)

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    def resolved_data_file(self) -> Path:
        return self.data_file if self.data_file.is_absolute() else PROJECT_ROOT / self.data_file

    def gemini_api_key_value(self) -> str | None:
        if self.gemini_api_key is None:
            return None
        value = self.gemini_api_key.get_secret_value().strip()
        return value or None

    def gemini_fallback_model_value(self) -> str | None:
        if self.gemini_fallback_model is None:
            return None
        value = self.gemini_fallback_model.strip()
        return value or None


@lru_cache
def get_settings() -> Settings:
    return Settings()
