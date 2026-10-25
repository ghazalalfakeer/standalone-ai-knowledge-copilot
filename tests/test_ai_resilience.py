from fastapi.testclient import TestClient

from src.api import app, get_ai_service
from src.llm_client import (
    GeminiLLMClient,
    LLMProviderUnavailableError,
    LLMRateLimitError,
)


class ProviderError(Exception):
    def __init__(self, status_code: int):
        self.status_code = status_code
        super().__init__(f"provider status {status_code}")


class FailingModels:
    def __init__(self, status_code: int):
        self.status_code = status_code

    def count_tokens(self, **kwargs):
        class Count:
            total_tokens = 5
        return Count()

    def generate_content(self, **kwargs):
        raise ProviderError(self.status_code)


class FakeClient:
    def __init__(self, status_code: int):
        self.models = FailingModels(status_code)


def test_provider_503_becomes_specific_application_error():
    client = GeminiLLMClient(api_key=None, model="fake", client=FakeClient(503))
    try:
        client.generate("A valid prompt for testing provider unavailability.")
        assert False, "expected LLMProviderUnavailableError"
    except LLMProviderUnavailableError:
        pass


def test_provider_429_becomes_specific_application_error():
    client = GeminiLLMClient(api_key=None, model="fake", client=FakeClient(429))
    try:
        client.generate("A valid prompt for testing provider rate limiting.")
        assert False, "expected LLMRateLimitError"
    except LLMRateLimitError:
        pass
