"""FastAPI backend for the Standalone AI Knowledge Copilot through Task 4."""
from __future__ import annotations

from typing import Any

from fastapi import Depends, FastAPI, HTTPException, status

from src.ai_models import (
    ExtractionRequest,
    ExtractionResponse,
    SummaryRequest,
    SummaryResponse,
    TokenUsage,
)
from src.ai_service import AIService
from src.config import get_settings
from src.llm_client import (
    GeminiLLMClient,
    LLMConfigurationError,
    LLMError,
    LLMProviderUnavailableError,
    LLMRateLimitError,
    LLMTimeoutError,
    LLMRequestError,
    LLMResponseError,
    LLMRunResult,
)
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
    version="0.4.0",
    description="Standalone AI Knowledge Copilot through Task 4.",
)

AI_ERROR_RESPONSES = {
    429: {"description": "AI provider rate limit reached."},
    502: {"description": "AI provider returned an unusable response or request failed."},
    503: {"description": "AI service is not configured or provider is temporarily unavailable."},
    504: {"description": "AI provider timed out after bounded retries and fallback."},
}


def get_storage() -> JsonStorage:
    return JsonStorage(settings.resolved_data_file(), validator=validate_knowledge_data)


def load_knowledge() -> dict[str, Any]:
    try:
        return get_storage().read()
    except StorageError as exc:
        logger.exception("Failed to load knowledge data", extra={"event": "knowledge_load_failed"})
        raise HTTPException(status_code=500, detail="Knowledge data could not be loaded.") from exc


def get_ai_service() -> AIService:
    try:
        client = GeminiLLMClient(
            api_key=settings.gemini_api_key_value(),
            model=settings.gemini_model,
            fallback_model=settings.gemini_fallback_model_value(),
            temperature=settings.llm_temperature,
            max_output_tokens=settings.llm_max_output_tokens,
            structured_max_output_tokens=settings.llm_structured_max_output_tokens,
            thinking_level=settings.llm_thinking_level,
            timeout_seconds=settings.llm_timeout_seconds,
            max_retries=settings.llm_max_retries,
            input_cost_per_1m_usd=settings.gemini_input_cost_per_1m_usd,
            output_cost_per_1m_usd=settings.gemini_output_cost_per_1m_usd,
        )
        return AIService(client)
    except LLMConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is not configured.",
        ) from exc


def _usage_from_run(run: LLMRunResult) -> TokenUsage:
    return TokenUsage(
        prompt_tokens_precount=run.prompt_tokens_precount,
        input_tokens=run.input_tokens,
        output_tokens=run.output_tokens,
        thinking_tokens=run.thought_tokens,
        total_tokens=run.total_tokens,
        estimated_cost_usd=run.estimated_cost_usd,
    )


def _raise_ai_http_error(exc: LLMError, operation: str) -> None:
    logger.exception("AI operation failed", extra={"event": f"ai_{operation}_failed"})
    if isinstance(exc, LLMConfigurationError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is not configured.",
        ) from exc
    if isinstance(exc, LLMProviderUnavailableError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI provider is temporarily unavailable. Please retry later.",
        ) from exc
    if isinstance(exc, LLMRateLimitError):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="AI provider rate limit reached. Please retry later.",
        ) from exc
    if isinstance(exc, LLMTimeoutError):
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="AI provider timed out. Please retry later.",
        ) from exc
    if isinstance(exc, (LLMRequestError, LLMResponseError)):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI {operation} failed.",
        ) from exc
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="AI request failed.",
    ) from exc


@app.get("/health", response_model=HealthResponse, tags=["System"])
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", service=settings.app_name, environment=settings.app_env)


@app.get("/knowledge", response_model=KnowledgeResponse, tags=["Knowledge"])
def get_knowledge() -> KnowledgeResponse:
    data = load_knowledge()
    items = [KnowledgeItem.model_validate(item) for item in data["items"]]
    return KnowledgeResponse(version=data["version"], count=len(items), items=items)


@app.post("/knowledge/search", response_model=KnowledgeSearchResponse, tags=["Knowledge"])
def search_knowledge(request: KnowledgeSearchRequest) -> KnowledgeSearchResponse:
    data = load_knowledge()
    query = request.query.strip().lower()
    tag = request.tag.strip().lower() if request.tag else None
    matches: list[KnowledgeItem] = []

    for raw in data["items"]:
        item = KnowledgeItem.model_validate(raw)
        searchable = " ".join([item.id, item.title, item.content, *item.tags]).lower()
        if query in searchable and (
            tag is None or any(item_tag.lower() == tag for item_tag in item.tags)
        ):
            matches.append(item)

    return KnowledgeSearchResponse(
        query=request.query,
        tag=request.tag,
        count=len(matches),
        items=matches,
    )


@app.post(
    "/ai/summarize",
    response_model=SummaryResponse,
    tags=["AI"],
    responses=AI_ERROR_RESPONSES,
)
def summarize(
    request: SummaryRequest,
    service: AIService = Depends(get_ai_service),
) -> SummaryResponse:
    try:
        payload, run = service.summarize(
            request.text,
            request.max_sentences,
            request.style,
            request.focus,
        )
    except LLMError as exc:
        _raise_ai_http_error(exc, "summarization")

    return SummaryResponse(
        **payload.model_dump(),
        model=run.model,
        usage=_usage_from_run(run),
    )


@app.post(
    "/ai/extract",
    response_model=ExtractionResponse,
    tags=["AI"],
    responses=AI_ERROR_RESPONSES,
)
def extract(
    request: ExtractionRequest,
    service: AIService = Depends(get_ai_service),
) -> ExtractionResponse:
    try:
        payload, run = service.extract(request.text)
    except LLMError as exc:
        _raise_ai_http_error(exc, "extraction")

    return ExtractionResponse(
        **payload.model_dump(),
        model=run.model,
        usage=_usage_from_run(run),
    )
