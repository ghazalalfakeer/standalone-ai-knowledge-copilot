"""Reusable Gemini client with validation, retries, timeouts and model fallback."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Callable, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class LLMError(Exception):
    pass


class LLMConfigurationError(LLMError):
    pass


class LLMRequestError(LLMError):
    pass


class LLMProviderUnavailableError(LLMRequestError):
    pass


class LLMRateLimitError(LLMRequestError):
    pass


class LLMTimeoutError(LLMRequestError):
    pass


class LLMResponseError(LLMError):
    pass


@dataclass(frozen=True)
class LLMRunResult:
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
        return asdict(self)


def estimate_cost_usd(
    *,
    input_tokens: int | None,
    output_tokens: int | None,
    thought_tokens: int | None,
    input_cost_per_1m_usd: float | None,
    output_cost_per_1m_usd: float | None,
) -> float | None:
    if input_cost_per_1m_usd is None or output_cost_per_1m_usd is None or input_tokens is None:
        return None
    output_billable = (output_tokens or 0) + (thought_tokens or 0)
    return round(
        (input_tokens / 1_000_000) * input_cost_per_1m_usd
        + (output_billable / 1_000_000) * output_cost_per_1m_usd,
        8,
    )


class GeminiLLMClient:
    """Gemini client with bounded retries and one configurable fallback model.

    The fallback is attempted for transient provider failures: HTTP 503/504 and
    network timeouts. Rate limits and non-transient request errors are surfaced
    directly instead of being multiplied across models.
    """

    def __init__(
        self,
        *,
        api_key: str | None,
        model: str,
        fallback_model: str | None = None,
        temperature: float = 0.2,
        max_output_tokens: int = 768,
        structured_max_output_tokens: int = 2048,
        thinking_level: str = "low",
        timeout_seconds: float = 60.0,
        max_retries: int = 2,
        input_cost_per_1m_usd: float | None = None,
        output_cost_per_1m_usd: float | None = None,
        client: Any | None = None,
    ) -> None:
        if not model.strip():
            raise LLMConfigurationError("Gemini model must not be empty.")
        if not 0 <= temperature <= 2:
            raise LLMConfigurationError("temperature must be between 0.0 and 2.0.")
        if max_output_tokens < 1:
            raise LLMConfigurationError("max_output_tokens must be at least 1.")
        if structured_max_output_tokens < 256:
            raise LLMConfigurationError("structured_max_output_tokens must be at least 256.")
        if thinking_level not in {"low", "medium", "high"}:
            raise LLMConfigurationError("thinking_level must be low, medium, or high.")
        if timeout_seconds <= 0:
            raise LLMConfigurationError("timeout_seconds must be positive.")
        if max_retries < 0:
            raise LLMConfigurationError("max_retries cannot be negative.")

        self.model = model.strip()
        cleaned_fallback = fallback_model.strip() if fallback_model and fallback_model.strip() else None
        self.fallback_model = cleaned_fallback if cleaned_fallback != self.model else None
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens
        self.structured_max_output_tokens = structured_max_output_tokens
        self.thinking_level = thinking_level
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.input_cost_per_1m_usd = input_cost_per_1m_usd
        self.output_cost_per_1m_usd = output_cost_per_1m_usd
        self._owns_client = client is None

        if client is not None:
            self._client = client
        else:
            if not api_key or not api_key.strip():
                raise LLMConfigurationError("GEMINI_API_KEY is missing. Add it to your local .env file.")
            self._client = self._create_google_client(api_key.strip())

    def _create_google_client(self, api_key: str) -> Any:
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise LLMConfigurationError(
                "google-genai is not installed. Run pip install -r requirements.txt"
            ) from exc

        retry = types.HttpRetryOptions(
            attempts=self.max_retries + 1,
            initial_delay=0.5,
            max_delay=4.0,
        )
        http = types.HttpOptions(
            timeout=int(self.timeout_seconds * 1000),
            retry_options=retry,
        )
        return genai.Client(api_key=api_key, http_options=http)

    @staticmethod
    def _validate_prompt(prompt: str) -> str:
        if not isinstance(prompt, str) or not prompt.strip():
            raise LLMConfigurationError("Prompt must be a non-empty string.")
        return prompt.strip()

    def _candidate_models(self) -> tuple[str, ...]:
        if self.fallback_model:
            return self.model, self.fallback_model
        return (self.model,)

    @staticmethod
    def _provider_status_code(exc: Exception) -> int | None:
        value = getattr(exc, "status_code", None)
        if isinstance(value, int):
            return value
        response = getattr(exc, "response", None)
        value = getattr(response, "status_code", None)
        return int(value) if isinstance(value, int) else None

    @staticmethod
    def _is_timeout_error(exc: Exception) -> bool:
        current: BaseException | None = exc
        seen: set[int] = set()
        while current is not None and id(current) not in seen:
            seen.add(id(current))
            if isinstance(current, httpx.TimeoutException):
                return True
            current = current.__cause__ or current.__context__
        return False

    @classmethod
    def _raise_request_error(cls, exc: Exception, operation: str) -> None:
        status_code = cls._provider_status_code(exc)
        if cls._is_timeout_error(exc):
            raise LLMTimeoutError(
                f"Gemini timed out during {operation}."
            ) from exc
        if status_code == 504:
            raise LLMTimeoutError(
                f"Gemini deadline was exceeded during {operation}."
            ) from exc
        if status_code == 503:
            raise LLMProviderUnavailableError(
                f"Gemini is temporarily unavailable during {operation}."
            ) from exc
        if status_code == 429:
            raise LLMRateLimitError(
                f"Gemini rate limit was reached during {operation}."
            ) from exc
        raise LLMRequestError(f"Gemini {operation} request failed: {exc}") from exc

    def _call_with_fallback(
        self,
        operation: str,
        call: Callable[[str], Any],
    ) -> tuple[str, Any]:
        models = self._candidate_models()
        for index, model in enumerate(models):
            try:
                return model, call(model)
            except Exception as exc:
                status_code = self._provider_status_code(exc)
                has_fallback = index + 1 < len(models)
                is_transient = status_code in {503, 504} or self._is_timeout_error(exc)
                if is_transient and has_fallback:
                    continue
                self._raise_request_error(exc, operation)
        raise LLMProviderUnavailableError(f"Gemini is temporarily unavailable during {operation}.")

    def _count_prompt_tokens_for_model(self, prompt: str, model: str) -> int | None:
        try:
            response = self._client.models.count_tokens(model=model, contents=prompt)
        except Exception:
            # Token pre-counting is observability metadata. It should not make
            # an otherwise valid generation fail; provider usage metadata is
            # still collected from the generation response when available.
            return None
        value = getattr(response, "total_tokens", None)
        return int(value) if value is not None else None

    def count_prompt_tokens(self, prompt: str) -> int | None:
        prompt = self._validate_prompt(prompt)
        try:
            response = self._client.models.count_tokens(model=self.model, contents=prompt)
        except Exception as exc:
            self._raise_request_error(exc, "token-count")
        value = getattr(response, "total_tokens", None)
        return int(value) if value is not None else None

    @staticmethod
    def _usage_int(meta: Any, name: str) -> int | None:
        if meta is None:
            return None
        value = getattr(meta, name, None)
        return int(value) if value is not None else None

    def _run_result(
        self,
        *,
        model: str,
        prompt: str,
        response: Any,
        precount: int | None,
        max_output_tokens_used: int | None = None,
    ) -> LLMRunResult:
        text = getattr(response, "text", None)
        if not isinstance(text, str) or not text.strip():
            raise LLMResponseError("Gemini returned no usable text response.")

        meta = getattr(response, "usage_metadata", None)
        input_tokens = self._usage_int(meta, "prompt_token_count")
        output_tokens = self._usage_int(meta, "candidates_token_count")
        thoughts = self._usage_int(meta, "thoughts_token_count")
        total = self._usage_int(meta, "total_token_count")
        cost = estimate_cost_usd(
            input_tokens=input_tokens or precount,
            output_tokens=output_tokens,
            thought_tokens=thoughts,
            input_cost_per_1m_usd=self.input_cost_per_1m_usd,
            output_cost_per_1m_usd=self.output_cost_per_1m_usd,
        )
        return LLMRunResult(
            datetime.now(timezone.utc).isoformat(),
            model,
            prompt,
            text.strip(),
            self.temperature,
            max_output_tokens_used or self.max_output_tokens,
            precount,
            input_tokens,
            output_tokens,
            thoughts,
            total,
            cost,
        )

    def _generation_config(
        self,
        model: str,
        *,
        max_output_tokens: int | None = None,
        structured: bool = False,
    ) -> dict[str, Any]:
        config: dict[str, Any] = {
            "max_output_tokens": max_output_tokens or self.max_output_tokens
        }
        # Gemini 3.6+ ignores classic sampling parameters. For simple structured
        # API work, explicitly use low thinking so reasoning does not consume
        # most of the completion budget before the JSON is finished.
        if model.startswith("gemini-3.8") or model.startswith("gemini-3.6"):
            if structured:
                config["thinking_config"] = {"thinking_level": self.thinking_level}
        else:
            config["temperature"] = self.temperature
        return config

    @staticmethod
    def _finish_reason(response: Any) -> str | None:
        candidates = getattr(response, "candidates", None)
        if not candidates:
            return None
        reason = getattr(candidates[0], "finish_reason", None)
        if reason is None:
            return None
        name = getattr(reason, "name", None)
        if isinstance(name, str):
            return name.upper()
        value = getattr(reason, "value", None)
        if isinstance(value, str):
            return value.upper()
        return str(reason).split(".")[-1].upper()

    def generate(self, prompt: str, *, system_instruction: str | None = None) -> LLMRunResult:
        prompt = self._validate_prompt(prompt)

        def request(model: str) -> Any:
            config = self._generation_config(model)
            if system_instruction:
                config["system_instruction"] = system_instruction.strip()
            return self._client.models.generate_content(
                model=model,
                contents=prompt,
                config=config,
            )

        used_model, response = self._call_with_fallback("generate-content", request)
        precount = self._count_prompt_tokens_for_model(prompt, used_model)
        return self._run_result(model=used_model, prompt=prompt, response=response, precount=precount)

    def generate_structured(
        self,
        prompt: str,
        schema: type[T],
        *,
        system_instruction: str | None = None,
    ) -> tuple[T, LLMRunResult]:
        prompt = self._validate_prompt(prompt)

        def request_with_limit(model: str, output_limit: int) -> Any:
            config = self._generation_config(
                model,
                max_output_tokens=output_limit,
                structured=True,
            )
            config.update(
                {
                    "response_mime_type": "application/json",
                    "response_schema": schema,
                }
            )
            if system_instruction:
                config["system_instruction"] = system_instruction.strip()
            return self._client.models.generate_content(
                model=model,
                contents=prompt,
                config=config,
            )

        def initial_request(model: str) -> Any:
            return request_with_limit(model, self.structured_max_output_tokens)

        used_model, response = self._call_with_fallback(
            "structured generation", initial_request
        )
        output_limit_used = self.structured_max_output_tokens

        # A hard max-output limit also includes hidden thinking tokens. For
        # structured JSON, an incomplete candidate is not usable, so perform
        # one bounded recovery with extra completion headroom instead of
        # passing truncated JSON downstream to Pydantic.
        if self._finish_reason(response) == "MAX_TOKENS":
            recovery_limit = min(
                max(self.structured_max_output_tokens * 2, 4096),
                8192,
            )

            def recovery_request(model: str) -> Any:
                return request_with_limit(model, recovery_limit)

            used_model, response = self._call_with_fallback(
                "structured generation recovery", recovery_request
            )
            output_limit_used = recovery_limit
            if self._finish_reason(response) == "MAX_TOKENS":
                raise LLMResponseError(
                    "Gemini returned an incomplete structured response even after "
                    "bounded completion recovery."
                )

        precount = self._count_prompt_tokens_for_model(prompt, used_model)
        run = self._run_result(
            model=used_model,
            prompt=prompt,
            response=response,
            precount=precount,
            max_output_tokens_used=output_limit_used,
        )
        parsed = getattr(response, "parsed", None)
        try:
            if isinstance(parsed, schema):
                value = parsed
            elif parsed is not None:
                value = schema.model_validate(parsed)
            else:
                value = schema.model_validate_json(run.response_text)
        except (ValidationError, ValueError, TypeError) as exc:
            raise LLMResponseError(
                f"Model returned invalid structured output for {schema.__name__}: {exc}"
            ) from exc
        return value, run

    def close(self) -> None:
        if self._owns_client:
            close = getattr(self._client, "close", None)
            if callable(close):
                close()
