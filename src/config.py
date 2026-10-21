"""Application configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Typed application settings loaded from environment variables or .env."""

    # Task 2 settings
    app_name: str = "Standalone AI Knowledge Copilot"
    app_env: Literal["development", "test", "production"] = "development"
    log_level: str = "INFO"
    data_file: Path = PROJECT_ROOT / "data" / "sample_knowledge.json"

    # Task 3 Gemini / LLM settings
    gemini_api_key: SecretStr | None = None
    gemini_model: str = "gemini-3.8-flash"
    llm_temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    llm_max_output_tokens: int = Field(default=256, ge=1, le=65536)

    # Optional paid-tier price inputs. They are deliberately not hardcoded
    # because model pricing and free/paid tiers can change over time.
    gemini_input_cost_per_1m_usd: float | None = Field(default=None, ge=0.0)
    gemini_output_cost_per_1m_usd: float | None = Field(default=None, ge=0.0)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def resolved_data_file(self) -> Path:
        """Return the configured data path as an absolute path."""
        if self.data_file.is_absolute():
            return self.data_file
        return PROJECT_ROOT / self.data_file

    def gemini_api_key_value(self) -> str | None:
        """Return the Gemini API key as plain text only when it is needed."""
        if self.gemini_api_key is None:
            return None

        value = self.gemini_api_key.get_secret_value().strip()
        return value or None


@lru_cache
def get_settings() -> Settings:
    """Create settings once and reuse them throughout the application."""
    return Settings()
