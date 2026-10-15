from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient
from prometheus_client import REGISTRY

from app.config import settings
from app.main import app

api = TestClient(app)


def fake_llm_response():
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="Mocked answer"))],
        usage=SimpleNamespace(prompt_tokens=10, completion_tokens=5),
    )


def test_health():
    response = api.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ask_success():
    with patch("app.llm_client.client") as mock_client:
        mock_client.chat.completions.create.return_value = fake_llm_response()
        response = api.post("/ask", json={"question": "What is MLOps?"})

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "Mocked answer"
    assert body["prompt_version"] == "v2"
    assert body["prompt_tokens"] == 10
    assert body["completion_tokens"] == 5


def test_ask_unknown_prompt_version_returns_400():
    with patch("app.llm_client.client") as mock_client:
        response = api.post(
            "/ask", json={"question": "Hi", "prompt_version": "v999"}
        )

    assert response.status_code == 400
    mock_client.chat.completions.create.assert_not_called()


def test_ask_missing_question_returns_422():
    response = api.post("/ask", json={})
    assert response.status_code == 422


def test_ask_provider_failure_returns_502():
    with patch("app.llm_client.client") as mock_client:
        mock_client.chat.completions.create.side_effect = RuntimeError("boom")
        response = api.post("/ask", json={"question": "Hi"})

    assert response.status_code == 502


def test_success_increments_request_counter():
    labels = {
        "model": settings.model_name,
        "prompt_version": "v1",
        "status": "success",
    }
    before = REGISTRY.get_sample_value("llm_requests_total", labels) or 0

    with patch("app.llm_client.client") as mock_client:
        mock_client.chat.completions.create.return_value = fake_llm_response()
        api.post("/ask", json={"question": "Hi", "prompt_version": "v1"})

    after = REGISTRY.get_sample_value("llm_requests_total", labels)
    assert after == before + 1


def test_metrics_endpoint_exposes_llm_metrics():
    response = api.get("/metrics")
    assert response.status_code == 200
    assert "llm_requests_total" in response.text