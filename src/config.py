"""Application configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Typed application settings loaded from environment variables or .env."""

    app_name: str = "Standalone AI Knowledge Copilot"
    app_env: Literal["development", "test", "production"] = "development"
    log_level: str = "INFO"
    data_file: Path = PROJECT_ROOT / "data" / "sample_knowledge.json"

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


@lru_cache
def get_settings() -> Settings:
    """Create settings once and reuse them throughout the application."""
    return Settings()
