"""Basic API tests required for Task 2."""

from fastapi.testclient import TestClient

from src.api import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "Standalone AI Knowledge Copilot"
    assert body["environment"] in {"development", "test", "production"}


def test_get_knowledge_endpoint() -> None:
    response = client.get("/knowledge")

    assert response.status_code == 200
    body = response.json()
    assert body["version"] == "1.0"
    assert body["count"] == len(body["items"])
    assert body["count"] >= 1
    assert {"id", "title", "content", "tags", "source"} <= body["items"][0].keys()


def test_search_knowledge_endpoint() -> None:
    response = client.post(
        "/knowledge/search",
        json={"query": "json", "tag": "python"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["query"] == "json"
    assert body["tag"] == "python"
    assert body["count"] >= 1
    assert any(item["id"] == "json-storage" for item in body["items"])


def test_search_request_validation() -> None:
    response = client.post(
        "/knowledge/search",
        json={"query": ""},
    )

    assert response.status_code == 422
