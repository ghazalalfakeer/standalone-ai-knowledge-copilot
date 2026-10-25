"""Pydantic schemas for reliable Task 4 LLM endpoints."""
from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field, field_validator


class TokenUsage(BaseModel):
    """LLM usage metadata returned with AI responses."""

    prompt_tokens_precount: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    thinking_tokens: int | None = None
    total_tokens: int | None = None
    estimated_cost_usd: float | None = None


class SummaryRequest(BaseModel):
    text: str = Field(min_length=10, max_length=20_000)
    max_sentences: int = Field(default=3, ge=1, le=8)
    style: Literal["concise", "executive", "technical"] = "concise"
    focus: str | None = Field(default=None, max_length=200)

    @field_validator("text", "focus")
    @classmethod
    def strip_text_fields(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class SummaryPayload(BaseModel):
    summary: str = Field(min_length=1)
    key_points: list[str] = Field(default_factory=list, max_length=8)

    @field_validator("summary")
    @classmethod
    def clean_summary(cls, value: str) -> str:
        return value.strip()

    @field_validator("key_points")
    @classmethod
    def clean_key_points(cls, values: list[str]) -> list[str]:
        return _clean_unique(values, limit=8)


class SummaryResponse(SummaryPayload):
    model: str
    usage: TokenUsage


class ExtractionRequest(BaseModel):
    text: str = Field(min_length=10, max_length=20_000)

    @field_validator("text")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class ExtractionPayload(BaseModel):
    people: list[str] = Field(default_factory=list)
    organizations: list[str] = Field(default_factory=list)
    dates: list[str] = Field(default_factory=list)
    amounts: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list, max_length=12)

    @field_validator("people", "organizations", "dates", "amounts")
    @classmethod
    def clean_entities(cls, values: list[str]) -> list[str]:
        return _clean_unique(values)

    @field_validator("keywords")
    @classmethod
    def clean_keywords(cls, values: list[str]) -> list[str]:
        return _clean_unique(values, limit=12)


class ExtractionResponse(ExtractionPayload):
    model: str
    usage: TokenUsage


def _clean_unique(values: list[str], limit: int | None = None) -> list[str]:
    """Strip blanks and remove duplicates while preserving model order."""
    cleaned: list[str] = []
    seen: set[str] = set()
    for raw in values:
        value = raw.strip()
        key = value.casefold()
        if not value or key in seen:
            continue
        seen.add(key)
        cleaned.append(value)
        if limit is not None and len(cleaned) >= limit:
            break
    return cleaned
