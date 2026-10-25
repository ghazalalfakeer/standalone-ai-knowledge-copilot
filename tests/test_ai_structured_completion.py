from src.ai_models import SummaryPayload
from src.llm_client import GeminiLLMClient, LLMResponseError
import pytest


class FinishReason:
    def __init__(self, name: str):
        self.name = name


class Candidate:
    def __init__(self, finish_reason: str):
        self.finish_reason = FinishReason(finish_reason)


class Meta:
    prompt_token_count = 10
    candidates_token_count = 25
    thoughts_token_count = 15
    total_token_count = 50


class Response:
    def __init__(self, text: str, parsed, finish_reason: str = "STOP"):
        self.text = text
        self.parsed = parsed
        self.candidates = [Candidate(finish_reason)]
        self.usage_metadata = Meta()


class RecoveryModels:
    def __init__(self):
        self.configs = []

    def count_tokens(self, *, model: str, contents: str):
        class Count:
            total_tokens = 10
        return Count()

    def generate_content(self, *, model: str, contents: str, config: dict):
        self.configs.append(config)
        if len(self.configs) == 1:
            return Response(
                '{"summary":"truncated',
                None,
                finish_reason="MAX_TOKENS",
            )
        payload = {"summary": "Complete summary.", "key_points": ["Recovered"]}
        return Response(
            '{"summary":"Complete summary.","key_points":["Recovered"]}',
            payload,
            finish_reason="STOP",
        )


class AlwaysTruncatedModels(RecoveryModels):
    def generate_content(self, *, model: str, contents: str, config: dict):
        self.configs.append(config)
        return Response('{"summary":"truncated', None, finish_reason="MAX_TOKENS")


class FakeClient:
    def __init__(self, models):
        self.models = models


def test_structured_generation_uses_low_thinking_and_recovers_from_max_tokens():
    models = RecoveryModels()
    client = GeminiLLMClient(
        api_key=None,
        model="gemini-3.8-flash",
        fallback_model="gemini-3.6-flash",
        structured_max_output_tokens=2048,
        thinking_level="low",
        client=FakeClient(models),
    )

    payload, run = client.generate_structured(
        "Summarize this sufficiently long sample text.",
        SummaryPayload,
    )

    assert payload.summary == "Complete summary."
    assert run.max_output_tokens == 4096
    assert models.configs[0]["max_output_tokens"] == 2048
    assert models.configs[1]["max_output_tokens"] == 4096
    assert models.configs[0]["thinking_config"] == {"thinking_level": "low"}
    assert models.configs[1]["thinking_config"] == {"thinking_level": "low"}


def test_structured_generation_stops_after_one_completion_recovery():
    models = AlwaysTruncatedModels()
    client = GeminiLLMClient(
        api_key=None,
        model="gemini-3.8-flash",
        fallback_model=None,
        structured_max_output_tokens=2048,
        thinking_level="low",
        client=FakeClient(models),
    )

    with pytest.raises(LLMResponseError, match="incomplete structured response"):
        client.generate_structured(
            "Summarize this sufficiently long sample text.",
            SummaryPayload,
        )

    assert len(models.configs) == 2
