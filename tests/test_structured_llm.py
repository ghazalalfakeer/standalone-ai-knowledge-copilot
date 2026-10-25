import pytest

from src.ai_models import SummaryPayload
from src.llm_client import GeminiLLMClient, LLMResponseError


class Count:
    total_tokens = 5


class Meta:
    prompt_token_count = 5
    candidates_token_count = 8
    thoughts_token_count = 0
    total_token_count = 13


class ValidResponse:
    text = '{"summary":"ok","key_points":["a"]}'
    parsed = {"summary": "ok", "key_points": ["a"]}
    usage_metadata = Meta()


class InvalidResponse:
    text = '{"summary":"","key_points":[]}'
    parsed = {"summary": "", "key_points": []}
    usage_metadata = Meta()


class Models:
    def __init__(self, response):
        self.response = response

    def count_tokens(self, **kwargs):
        return Count()

    def generate_content(self, **kwargs):
        assert kwargs["config"]["response_mime_type"] == "application/json"
        assert kwargs["config"]["response_schema"] is SummaryPayload
        return self.response


class Fake:
    def __init__(self, response):
        self.models = Models(response)


def test_structured_output_is_validated():
    client = GeminiLLMClient(api_key=None, model="fake", client=Fake(ValidResponse()))
    payload, run = client.generate_structured(
        "Please summarize this valid sample text.", SummaryPayload
    )
    assert payload.summary == "ok"
    assert run.total_tokens == 13


def test_invalid_structured_output_raises_application_error():
    client = GeminiLLMClient(api_key=None, model="fake", client=Fake(InvalidResponse()))
    with pytest.raises(LLMResponseError):
        client.generate_structured("Please summarize this valid sample text.", SummaryPayload)
