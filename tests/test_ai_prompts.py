from src.ai_prompts import build_extraction_prompt, build_summary_prompt


def test_summary_prompt_contains_style_focus_and_grounding_rule():
    prompt = build_summary_prompt(
        text="A technical system had a latency increase after deployment.",
        max_sentences=2,
        style="technical",
        focus="latency",
    )
    assert "at most 2 sentences" in prompt
    assert "technical terminology" in prompt
    assert "latency" in prompt
    assert "Do not add facts" in prompt


def test_extraction_prompt_requires_empty_lists_for_missing_categories():
    prompt = build_extraction_prompt(text="Example text long enough for a prompt.")
    assert "empty list" in prompt
    assert "Do not infer or invent" in prompt
