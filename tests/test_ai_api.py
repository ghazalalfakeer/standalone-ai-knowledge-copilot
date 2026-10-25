from datetime import datetime, timezone

from fastapi.testclient import TestClient

from src.ai_models import ExtractionPayload, SummaryPayload
from src.api import app, get_ai_service
from src.llm_client import LLMRunResult


def fake_run() -> LLMRunResult:
    return LLMRunResult(
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
        model="fake-gemini",
        prompt="fake prompt",
        response_text="fake response",
        temperature=0.2,
        max_output_tokens=768,
        prompt_tokens_precount=12,
        input_tokens=12,
        output_tokens=20,
        thought_tokens=5,
        total_tokens=37,
        estimated_cost_usd=None,
    )


class FakeAIService:
    def summarize(self, text: str, max_sentences: int, style: str, focus: str | None):
        return (
            SummaryPayload(
                summary="Short validated summary.",
                key_points=["Point one", "Point one", " Point two "],
            ),
            fake_run(),
        )

    def extract(self, text: str):
        return (
            ExtractionPayload(
                people=["Alice", " alice ", ""],
                organizations=["Example GmbH"],
                dates=[],
                amounts=["100 EUR"],
                keywords=["invoice", " Invoice ", "approval"],
            ),
            fake_run(),
        )


def fake_service() -> FakeAIService:
    return FakeAIService()


app.dependency_overrides[get_ai_service] = fake_service
client = TestClient(app)


def test_summarize_endpoint_returns_structured_payload_and_usage():
    response = client.post(
        "/ai/summarize",
        json={
            "text": "This is sufficiently long sample input text for summarization.",
            "max_sentences": 2,
            "style": "executive",
            "focus": "risk",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["summary"] == "Short validated summary."
    assert data["key_points"] == ["Point one", "Point two"]
    assert data["model"] == "fake-gemini"
    assert data["usage"]["total_tokens"] == 37


def test_extract_endpoint_normalizes_duplicate_entities():
    response = client.post(
        "/ai/extract",
        json={"text": "Alice from Example GmbH approved an invoice for 100 EUR today."},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["people"] == ["Alice"]
    assert data["amounts"] == ["100 EUR"]
    assert data["keywords"] == ["invoice", "approval"]
    assert data["usage"]["input_tokens"] == 12


def test_ai_request_validation_rejects_short_text():
    assert client.post("/ai/summarize", json={"text": "short"}).status_code == 422


def test_ai_request_validation_rejects_unknown_summary_style():
    response = client.post(
        "/ai/summarize",
        json={
            "text": "This text is definitely long enough to pass validation.",
            "style": "creative",
        },
    )
    assert response.status_code == 422
