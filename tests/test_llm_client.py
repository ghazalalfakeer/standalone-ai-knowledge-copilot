"""Unit tests for Task 3 LLM logic.

These tests use a fake SDK client. They never call Gemini and therefore do not
consume API quota or incur model cost.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.llm_client import (
    GeminiLLMClient,
    LLMConfigurationError,
    estimate_cost_usd,
)
from src.llm_records import save_llm_run


class FakeCountResponse:
    total_tokens = 12


class FakeUsageMetadata:
    prompt_token_count = 12
    candidates_token_count = 20
    thoughts_token_count = 3
    total_token_count = 35


class FakeGenerateResponse:
    text = "A context window is the amount of tokenized information the model can use."
    usage_metadata = FakeUsageMetadata()


class FakeModels:
    def count_tokens(self, **kwargs):
        assert kwargs["model"] == "gemini-test-model"
        assert kwargs["contents"] == "Explain context windows."
        return FakeCountResponse()

    def generate_content(self, **kwargs):
        assert kwargs["model"] == "gemini-test-model"
        assert kwargs["contents"] == "Explain context windows."
        assert kwargs["config"]["temperature"] == 0.2
        assert kwargs["config"]["max_output_tokens"] == 128
        return FakeGenerateResponse()


class FakeClient:
    models = FakeModels()


def test_generate_collects_token_usage_without_real_api_call() -> None:
    client = GeminiLLMClient(
        api_key=None,
        model="gemini-test-model",
        temperature=0.2,
        max_output_tokens=128,
        input_cost_per_1m_usd=1.0,
        output_cost_per_1m_usd=2.0,
        client=FakeClient(),
    )

    result = client.generate("Explain context windows.")

    assert result.prompt_tokens_precount == 12
    assert result.input_tokens == 12
    assert result.output_tokens == 20
    assert result.thought_tokens == 3
    assert result.total_tokens == 35
    assert result.estimated_cost_usd == pytest.approx(0.000058)
    assert "context window" in result.response_text.lower()


def test_estimate_cost_requires_configured_prices() -> None:
    cost = estimate_cost_usd(
        input_tokens=100,
        output_tokens=200,
        thought_tokens=0,
        input_cost_per_1m_usd=None,
        output_cost_per_1m_usd=None,
    )

    assert cost is None


def test_missing_api_key_is_rejected_for_real_client() -> None:
    with pytest.raises(LLMConfigurationError, match="GEMINI_API_KEY"):
        GeminiLLMClient(
            api_key=None,
            model="gemini-test-model",
        )


def test_llm_run_can_be_saved_as_json(tmp_path: Path) -> None:
    client = GeminiLLMClient(
        api_key=None,
        model="gemini-test-model",
        client=FakeClient(),
        max_output_tokens=128,
    )

    result = client.generate("Explain context windows.")
    path = save_llm_run(result, tmp_path)

    assert path.exists()

    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["model"] == "gemini-test-model"
    assert saved["prompt"] == "Explain context windows."
    assert saved["total_tokens"] == 35
