
from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, status

from src.config import get_settings
from src.logging_config import get_structured_logger
from src.models import (
    HealthResponse,
    KnowledgeItem,
    KnowledgeResponse,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
)
from src.storage import JsonStorage, StorageError, validate_knowledge_data

settings = get_settings()
logger = get_structured_logger(__name__, settings.log_level)

app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description=(
        "Task 2 backend for the Standalone AI Knowledge Copilot. "
        "This version is intentionally non-AI and exposes validated JSON "
        "knowledge through REST endpoints."
    ),
)


def get_storage() -> JsonStorage:
    """Build the Task 1 storage service using Task 2 configuration."""
    return JsonStorage(
        file_path=settings.resolved_data_file(),
        validator=validate_knowledge_data,
    )


def load_knowledge() -> dict[str, Any]:
    """Load knowledge and convert storage failures to an HTTP 500 response."""
    storage = get_storage()

    try:
        data = storage.read()
    except StorageError as exc:
        logger.exception(
            "Failed to load knowledge data",
            extra={
                "event": "knowledge_load_failed",
                "path": settings.resolved_data_file(),
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Knowledge data could not be loaded.",
        ) from exc

    logger.info(
        "Knowledge data loaded",
        extra={
            "event": "knowledge_loaded",
            "path": settings.resolved_data_file(),
            "result_count": len(data["items"]),
        },
    )
    return data


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Check backend health",
)
def health_check() -> HealthResponse:
    """Return a simple health response for monitoring and smoke tests."""
    logger.info("Health check requested", extra={"event": "health_check"})
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        environment=settings.app_env,
    )


@app.get(
    "/knowledge",
    response_model=KnowledgeResponse,
    tags=["Knowledge"],
    summary="Return all knowledge items",
)
def get_knowledge() -> KnowledgeResponse:
    """Expose the validated JSON storage from Task 1 through HTTP."""
    data = load_knowledge()
    items = [KnowledgeItem.model_validate(item) for item in data["items"]]
    return KnowledgeResponse(
        version=data["version"],
        count=len(items),
        items=items,
    )


@app.post(
    "/knowledge/search",
    response_model=KnowledgeSearchResponse,
    tags=["Knowledge"],
    summary="Search knowledge without AI",
)
def search_knowledge(
    request: KnowledgeSearchRequest,
) -> KnowledgeSearchResponse:
    """Perform deterministic case-insensitive search over local knowledge."""
    data = load_knowledge()
    query = request.query.strip().lower()
    requested_tag = request.tag.strip().lower() if request.tag else None
    matches: list[KnowledgeItem] = []

    for raw_item in data["items"]:
        item = KnowledgeItem.model_validate(raw_item)
        searchable_text = " ".join(
            [item.id, item.title, item.content, *item.tags]
        ).lower()

        query_matches = query in searchable_text
        tag_matches = (
            requested_tag is None
            or any(tag.lower() == requested_tag for tag in item.tags)
        )

        if query_matches and tag_matches:
            matches.append(item)

    logger.info(
        "Knowledge search completed",
        extra={
            "event": "knowledge_search",
            "result_count": len(matches),
        },
    )

    return KnowledgeSearchResponse(
        query=request.query,
        tag=request.tag,
        count=len(matches),
        items=matches,
    )
