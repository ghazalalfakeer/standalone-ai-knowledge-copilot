"""Task 3 command-line demo: make the project's first Gemini LLM call."""

from __future__ import annotations

import argparse
import sys

from src.config import get_settings
from src.llm_client import (
    GeminiLLMClient,
    LLMConfigurationError,
    LLMError,
)
from src.llm_records import save_llm_run

DEFAULT_PROMPT = (
    "Explain in three concise bullet points what a context window is in "
    "a large language model."
)


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Task 3: first Gemini LLM API call with token tracking."
    )
    parser.add_argument(
        "--prompt",
        default=DEFAULT_PROMPT,
        help="Prompt to send to Gemini.",
    )
    return parser


def main() -> int:
    """Run one Gemini prompt and save the evidence as JSON."""
    args = build_parser().parse_args()
    settings = get_settings()

    try:
        client = GeminiLLMClient(
            api_key=settings.gemini_api_key_value(),
            model=settings.gemini_model,
            temperature=settings.llm_temperature,
            max_output_tokens=settings.llm_max_output_tokens,
            input_cost_per_1m_usd=(
                settings.gemini_input_cost_per_1m_usd
            ),
            output_cost_per_1m_usd=(
                settings.gemini_output_cost_per_1m_usd
            ),
        )
    except LLMConfigurationError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    try:
        result = client.generate(args.prompt)
        record_path = save_llm_run(result)
    except LLMError as exc:
        print(f"LLM error: {exc}", file=sys.stderr)
        return 1
    finally:
        client.close()

    print()
    print("Standalone AI Knowledge Copilot")
    print("Task 3 - First Gemini LLM Call")
    print("=" * 72)
    print(f"Model: {result.model}")
    print(f"Configured temperature: {result.temperature}")

    if result.model.startswith("gemini-3.8"):
        print(
            "Temperature sent to model: no "
            "(Gemini 3.8 compatibility)"
        )
    else:
        print("Temperature sent to model: yes")
    print(f"Max output tokens: {result.max_output_tokens}")
    print()
    print("PROMPT")
    print("-" * 72)
    print(result.prompt)
    print()
    print("MODEL RESPONSE")
    print("-" * 72)
    print(result.response_text)
    print()
    print("TOKEN USAGE")
    print("-" * 72)
    print(f"Prompt tokens (pre-count): {result.prompt_tokens_precount}")
    print(f"Input tokens (usage metadata): {result.input_tokens}")
    print(f"Output tokens: {result.output_tokens}")
    print(f"Thinking tokens: {result.thought_tokens}")
    print(f"Total tokens: {result.total_tokens}")

    if result.estimated_cost_usd is None:
        print(
            "Estimated cost: not calculated (current per-token prices are "
            "not configured)."
        )
    else:
        print(f"Estimated cost (USD): {result.estimated_cost_usd:.8f}")

    print()
    print(f"Run record saved to: {record_path}")
    print("Task 3 LLM demo completed successfully.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
