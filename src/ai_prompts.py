"""Centralized, testable prompt templates for Task 4."""
from __future__ import annotations

SYSTEM_INSTRUCTION = (
    "You are a precise backend application component. "
    "Return only information supported by the supplied text. "
    "Never invent names, dates, amounts, organizations, or facts. "
    "Follow the response schema exactly."
)


def build_summary_prompt(*, text: str, max_sentences: int, style: str, focus: str | None) -> str:
    style_instructions = {
        "concise": "Use direct, compact language.",
        "executive": "Prioritize decisions, outcomes, risks, and business-relevant facts.",
        "technical": "Preserve important technical terminology and implementation details.",
    }
    focus_instruction = (
        f" Pay special attention to this focus area when it is supported by the text: {focus}."
        if focus
        else ""
    )
    return (
        f"Summarize the text in at most {max_sentences} sentences. "
        f"{style_instructions[style]} "
        "Return up to 5 concise key points in addition to the summary. "
        "Do not add facts that are not explicitly supported by the text."
        f"{focus_instruction}\n\n"
        f"TEXT:\n{text.strip()}"
    )


def build_extraction_prompt(*, text: str) -> str:
    return (
        "Extract only explicitly stated entities from the text. "
        "Return people, organizations, dates, monetary amounts, and up to 10 useful keywords. "
        "Use the original wording where practical. "
        "If a category is absent, return an empty list. "
        "Do not infer or invent missing information.\n\n"
        f"TEXT:\n{text.strip()}"
    )
