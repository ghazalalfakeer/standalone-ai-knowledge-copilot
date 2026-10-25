"""Task 4 service layer: prompt templates + structured validation."""
from __future__ import annotations

from src.ai_models import ExtractionPayload, SummaryPayload
from src.ai_prompts import SYSTEM_INSTRUCTION, build_extraction_prompt, build_summary_prompt
from src.llm_client import GeminiLLMClient, LLMRunResult


class AIService:
    def __init__(self, client: GeminiLLMClient) -> None:
        self.client = client

    def summarize(
        self,
        text: str,
        max_sentences: int,
        style: str = "concise",
        focus: str | None = None,
    ) -> tuple[SummaryPayload, LLMRunResult]:
        prompt = build_summary_prompt(
            text=text,
            max_sentences=max_sentences,
            style=style,
            focus=focus,
        )
        return self.client.generate_structured(
            prompt,
            SummaryPayload,
            system_instruction=SYSTEM_INSTRUCTION,
        )

    def extract(self, text: str) -> tuple[ExtractionPayload, LLMRunResult]:
        prompt = build_extraction_prompt(text=text)
        return self.client.generate_structured(
            prompt,
            ExtractionPayload,
            system_instruction=SYSTEM_INSTRUCTION,
        )
