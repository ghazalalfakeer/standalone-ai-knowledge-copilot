import httpx
import pytest

from src.ai_models import SummaryPayload
from src.api import app
from src.llm_client import GeminiLLMClient, LLMRateLimitError, LLMTimeoutError


class ProviderError(Exception):
    def __init__(self, status_code: int):
        self.status_code = status_code
        super().__init__(f"provider status {status_code}")


class Meta:
    prompt_token_count = 7
    candidates_token_count = 9
    thoughts_token_count = 2
    total_token_count = 18


class ValidResponse:
    text = '{"summary":"Fallback worked.","key_points":["Resilient"]}'
    parsed = {"summary": "Fallback worked.", "key_points": ["Resilient"]}
    usage_metadata = Meta()


class FallbackModels:
    def __init__(self):
        self.generation_models: list[str] = []

    def count_tokens(self, *, model: str, contents: str):
        class Count:
            total_tokens = 7
        return Count()

    def generate_content(self, *, model: str, contents: str, config: dict):
        self.generation_models.append(model)
        if model == "gemini-3.8-flash":
            raise ProviderError(503)
        return ValidResponse()


class RateLimitedModels(FallbackModels):
    def generate_content(self, *, model: str, contents: str, config: dict):
        self.generation_models.append(model)
        raise ProviderError(429)


class FakeClient:
    def __init__(self, models):
        self.models = models


def test_structured_generation_falls_back_after_primary_503():
    models = FallbackModels()
    client = GeminiLLMClient(
        api_key=None,
        model="gemini-3.8-flash",
        fallback_model="gemini-3.6-flash",
        client=FakeClient(models),
    )

    payload, run = client.generate_structured(
        "Summarize this sufficiently long sample text.",
        SummaryPayload,
    )

    assert payload.summary == "Fallback worked."
    assert run.model == "gemini-3.6-flash"
    assert models.generation_models == ["gemini-3.8-flash", "gemini-3.6-flash"]


def test_rate_limit_does_not_fan_out_to_fallback_model():
    models = RateLimitedModels()
    client = GeminiLLMClient(
        api_key=None,
        model="gemini-3.8-flash",
        fallback_model="gemini-3.6-flash",
        client=FakeClient(models),
    )

    with pytest.raises(LLMRateLimitError):
        client.generate_structured(
            "Summarize this sufficiently long sample text.",
            SummaryPayload,
        )

    assert models.generation_models == ["gemini-3.8-flash"]


def test_openapi_documents_ai_reliability_responses():
    schema = app.openapi()
    responses = schema["paths"]["/ai/summarize"]["post"]["responses"]
    assert "429" in responses
    assert "502" in responses
    assert "503" in responses
    assert "504" in responses


class TimeoutThenSuccessModels(FallbackModels):
    def generate_content(self, *, model: str, contents: str, config: dict):
        self.generation_models.append(model)
        if model == "gemini-3.8-flash":
            raise httpx.ReadTimeout("simulated read timeout")
        return ValidResponse()


class AlwaysTimeoutModels(FallbackModels):
    def generate_content(self, *, model: str, contents: str, config: dict):
        self.generation_models.append(model)
        raise httpx.ReadTimeout("simulated read timeout")


def test_structured_generation_falls_back_after_primary_timeout():
    models = TimeoutThenSuccessModels()
    client = GeminiLLMClient(
        api_key=None,
        model="gemini-3.8-flash",
        fallback_model="gemini-3.6-flash",
        client=FakeClient(models),
    )

    payload, run = client.generate_structured(
        "Summarize this sufficiently long sample text.",
        SummaryPayload,
    )

    assert payload.summary == "Fallback worked."
    assert run.model == "gemini-3.6-flash"
    assert models.generation_models == ["gemini-3.8-flash", "gemini-3.6-flash"]


def test_timeout_after_fallback_is_specific_error():
    models = AlwaysTimeoutModels()
    client = GeminiLLMClient(
        api_key=None,
        model="gemini-3.8-flash",
        fallback_model="gemini-3.6-flash",
        client=FakeClient(models),
    )

    with pytest.raises(LLMTimeoutError):
        client.generate_structured(
            "Summarize this sufficiently long sample text.",
            SummaryPayload,
        )

    assert models.generation_models == ["gemini-3.8-flash", "gemini-3.6-flash"]

class DeadlineThenSuccessModels(FallbackModels):
    def generate_content(self, *, model: str, contents: str, config: dict):
        self.generation_models.append(model)
        if model == "gemini-3.8-flash":
            raise ProviderError(504)
        return ValidResponse()


class AlwaysDeadlineModels(FallbackModels):
    def generate_content(self, *, model: str, contents: str, config: dict):
        self.generation_models.append(model)
        raise ProviderError(504)


def test_structured_generation_falls_back_after_provider_504():
    models = DeadlineThenSuccessModels()
    client = GeminiLLMClient(
        api_key=None,
        model="gemini-3.8-flash",
        fallback_model="gemini-3.6-flash",
        client=FakeClient(models),
    )

    payload, run = client.generate_structured(
        "Summarize this sufficiently long sample text.",
        SummaryPayload,
    )

    assert payload.summary == "Fallback worked."
    assert run.model == "gemini-3.6-flash"
    assert models.generation_models == ["gemini-3.8-flash", "gemini-3.6-flash"]


def test_provider_504_after_fallback_becomes_timeout_error():
    models = AlwaysDeadlineModels()
    client = GeminiLLMClient(
        api_key=None,
        model="gemini-3.8-flash",
        fallback_model="gemini-3.6-flash",
        client=FakeClient(models),
    )

    with pytest.raises(LLMTimeoutError):
        client.generate_structured(
            "Summarize this sufficiently long sample text.",
            SummaryPayload,
        )

    assert models.generation_models == ["gemini-3.8-flash", "gemini-3.6-flash"]

