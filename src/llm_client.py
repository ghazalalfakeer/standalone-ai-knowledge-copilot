"""Gemini LLM client used by Task 3.

The module intentionally keeps the first LLM integration small and explicit.
It demonstrates:

- API-key based configuration
- a simple Gemini prompt
- temperature and output-token configuration
- token counting
- response usage metadata
- optional cost estimation
- application-specific error handling
- dependency injection so tests do not call the real API
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


class LLMError(Exception):
    """Base exception for Task 3 LLM errors."""


class LLMConfigurationError(LLMError):
    """Raised when the LLM client is not configured correctly."""


class LLMRequestError(LLMError):
    """Raised when a request to the model fails."""


class LLMResponseError(LLMError):
    """Raised when the model returns an unusable response."""


@dataclass(frozen=True)
class LLMRunResult:
    """Structured evidence from one successful LLM call."""

    timestamp_utc: str
    model: str
    prompt: str
    response_text: str
    temperature: float
    max_output_tokens: int
    prompt_tokens_precount: int | None
    input_tokens: int | None
    output_tokens: int | None
    thought_tokens: int | None
    total_tokens: int | None
    estimated_cost_usd: float | None

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of the run."""
        return asdict(self)


def estimate_cost_usd(
    *,
    input_tokens: int | None,
    output_tokens: int | None,
    thought_tokens: int | None,
    input_cost_per_1m_usd: float | None,
    output_cost_per_1m_usd: float | None,
) -> float | None:
    """Estimate request cost when current per-million-token prices are supplied.

    The calculation is deliberately configuration-driven instead of hardcoded.
    Gemini output pricing can include thinking tokens, so thought tokens are
    included in the output side of this simple estimate.
    """

    if input_cost_per_1m_usd is None or output_cost_per_1m_usd is None:
        return None

    if input_tokens is None:
        return None

    billable_output_tokens = (output_tokens or 0) + (thought_tokens or 0)

    input_cost = (input_tokens / 1_000_000) * input_cost_per_1m_usd
    output_cost = (
        billable_output_tokens / 1_000_000
    ) * output_cost_per_1m_usd

    return round(input_cost + output_cost, 8)


class GeminiLLMClient:
    """Small wrapper around the Google Gen AI SDK for the Task 3 demo."""

    def __init__(
        self,
        *,
        api_key: str | None,
        model: str,
        temperature: float = 0.2,
        max_output_tokens: int = 256,
        input_cost_per_1m_usd: float | None = None,
        output_cost_per_1m_usd: float | None = None,
        client: Any | None = None,
    ) -> None:
        if not model.strip():
            raise LLMConfigurationError("Gemini model must not be empty.")

        if not 0.0 <= temperature <= 2.0:
            raise LLMConfigurationError(
                "temperature must be between 0.0 and 2.0."
            )

        if max_output_tokens < 1:
            raise LLMConfigurationError(
                "max_output_tokens must be at least 1."
            )

        self.model = model.strip()
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.input_cost_per_1m_usd = input_cost_per_1m_usd
        self.output_cost_per_1m_usd = output_cost_per_1m_usd
        self._owns_client = client is None

        if client is not None:
            # Dependency injection is used by unit tests, so no network call
            # or real API key is required in the test suite.
            self._client = client
        else:
            if not api_key or not api_key.strip():
                raise LLMConfigurationError(
                    "GEMINI_API_KEY is missing. Add it to your local .env file."
                )
            self._client = self._create_google_client(api_key.strip())

    @staticmethod
    def _create_google_client(api_key: str) -> Any:
        """Create the real Google Gen AI client lazily.

        Importing the SDK here keeps unit tests independent from a live Gemini
        installation and lets them use a fake injected client.
        """

        try:
            from google import genai
        except ImportError as exc:
            raise LLMConfigurationError(
                "google-genai is not installed. Run: "
                "pip install -r requirements.txt"
            ) from exc

        return genai.Client(api_key=api_key)

    def count_prompt_tokens(self, prompt: str) -> int | None:
        """Count input tokens before generation."""
        normalized_prompt = self._validate_prompt(prompt)

        try:
            response = self._client.models.count_tokens(
                model=self.model,
                contents=normalized_prompt,
            )
        except Exception as exc:  # SDK-specific exceptions may change.
            raise LLMRequestError(
                f"Gemini token-count request failed: {exc}"
            ) from exc

        total_tokens = getattr(response, "total_tokens", None)
        return int(total_tokens) if total_tokens is not None else None

    def generate(self, prompt: str) -> LLMRunResult:
        """Send one prompt to Gemini and return structured run evidence."""
        normalized_prompt = self._validate_prompt(prompt)
        prompt_tokens_precount = self.count_prompt_tokens(normalized_prompt)

        generation_config: dict[str, Any] = {
            "max_output_tokens": self.max_output_tokens,
        }
        # Gemini 3.8 Flash deprecated sampling controls such as temperature.
        # Keep the setting in our educational configuration, but do not send it
        # to that model family. Other/fake models still receive it.
        if not self.model.startswith("gemini-3.8"):
            generation_config["temperature"] = self.temperature

        try:
            response = self._client.models.generate_content(
                model=self.model,
                contents=normalized_prompt,
                config=generation_config,
            )
        except Exception as exc:  # Wrap SDK/network errors for our application.
            raise LLMRequestError(
                f"Gemini generate-content request failed: {exc}"
            ) from exc

        response_text = getattr(response, "text", None)

        if not isinstance(response_text, str) or not response_text.strip():
            raise LLMResponseError(
                "Gemini returned no usable text response."
            )

        usage_metadata = getattr(response, "usage_metadata", None)

        input_tokens = self._usage_int(
            usage_metadata,
            "prompt_token_count",
        )
        output_tokens = self._usage_int(
            usage_metadata,
            "candidates_token_count",
        )
        thought_tokens = self._usage_int(
            usage_metadata,
            "thoughts_token_count",
        )
        total_tokens = self._usage_int(
            usage_metadata,
            "total_token_count",
        )

        # If usage metadata does not expose prompt tokens, the explicit
        # pre-count is still useful for basic token awareness.
        cost_input_tokens = input_tokens or prompt_tokens_precount

        estimated_cost = estimate_cost_usd(
            input_tokens=cost_input_tokens,
            output_tokens=output_tokens,
            thought_tokens=thought_tokens,
            input_cost_per_1m_usd=self.input_cost_per_1m_usd,
            output_cost_per_1m_usd=self.output_cost_per_1m_usd,
        )

        return LLMRunResult(
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
            model=self.model,
            prompt=normalized_prompt,
            response_text=response_text.strip(),
            temperature=self.temperature,
            max_output_tokens=self.max_output_tokens,
            prompt_tokens_precount=prompt_tokens_precount,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            thought_tokens=thought_tokens,
            total_tokens=total_tokens,
            estimated_cost_usd=estimated_cost,
        )

    def close(self) -> None:
        """Close the SDK client when this wrapper created it."""
        if not self._owns_client:
            return

        close_method = getattr(self._client, "close", None)
        if callable(close_method):
            close_method()

    @staticmethod
    def _validate_prompt(prompt: str) -> str:
        if not isinstance(prompt, str) or not prompt.strip():
            raise LLMConfigurationError("Prompt must be a non-empty string.")
        return prompt.strip()

    @staticmethod
    def _usage_int(usage_metadata: Any, field_name: str) -> int | None:
        if usage_metadata is None:
            return None

        value = getattr(usage_metadata, field_name, None)
        return int(value) if value is not None else None
