"""Pydantic request and response models for the FastAPI application."""

from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response returned by the health-check endpoint."""

    status: str = Field(description="Current service health status")
    service: str = Field(description="Application/service name")
    environment: str = Field(description="Current runtime environment")


class KnowledgeItem(BaseModel):
    """Public API representation of one knowledge item."""

    id: str
    title: str
    content: str
    tags: list[str]
    source: str | None = None


class KnowledgeResponse(BaseModel):
    """Response containing all available knowledge items."""

    version: str
    count: int = Field(ge=0)
    items: list[KnowledgeItem]


class KnowledgeSearchRequest(BaseModel):
    """Request body for deterministic, non-AI knowledge search."""

    query: str = Field(
        min_length=1,
        max_length=200,
        description="Text to search for in title, content, ID, or tags",
        examples=["json"],
    )
    tag: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="Optional exact tag filter",
        examples=["python"],
    )


class KnowledgeSearchResponse(BaseModel):
    """Response returned by the non-AI search endpoint."""

    query: str
    tag: str | None
    count: int = Field(ge=0)
    items: list[KnowledgeItem]
