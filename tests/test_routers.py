import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    from titlegene.main import app
    return TestClient(app, raise_server_exceptions=True)


# ── /api/analyze ─────────────────────────────────

def test_analyze_returns_session_and_report(client):
    with patch("titlegene.routers.generate.claude_service.analyze", return_value="보고서 요약"):
        resp = client.post("/api/analyze", json={
            "product_name": "무릎보호대", "content": "글내용", "target": "50대여성"
        })
    assert resp.status_code == 200
    data = resp.json()
    assert "session_id" in data
    assert data["report_text"] == "보고서 요약"


def test_analyze_missing_field_returns_422(client):
    resp = client.post("/api/analyze", json={"product_name": "무릎보호대"})
    assert resp.status_code == 422


def test_analyze_api_error_returns_502(client):
    from titlegene.services.claude_service import ClaudeAPIError
    with patch("titlegene.routers.generate.claude_service.analyze", side_effect=ClaudeAPIError("fail")):
        resp = client.post("/api/analyze", json={
            "product_name": "p", "content": "c", "target": "t"
        })
    assert resp.status_code == 502


# ── /api/generate-title ──────────────────────────

def test_generate_title_ok(client):
    with patch("titlegene.routers.generate.claude_service.analyze", return_value="보고서"):
        r = client.post("/api/analyze", json={"product_name": "p", "content": "c", "target": "t"})
    sid = r.json()["session_id"]

    with patch("titlegene.routers.generate.claude_service.generate_title", return_value="멋진 제목"):
        resp = client.post("/api/generate-title", json={"session_id": sid})
    assert resp.status_code == 200
    assert resp.json()["title_text"] == "멋진 제목"


def test_generate_title_unknown_session_returns_404(client):
    resp = client.post("/api/generate-title", json={"session_id": "없는세션"})
    assert resp.status_code == 404


# ── /api/differentiate ───────────────────────────

def test_differentiate_ok(client):
    with patch("titlegene.routers.generate.claude_service.analyze", return_value="보고서"):
        r = client.post("/api/analyze", json={"product_name": "p", "content": "c", "target": "t"})
    sid = r.json()["session_id"]

    with patch("titlegene.routers.generate.claude_service.differentiate", return_value="차별화 제목"):
        resp = client.post("/api/differentiate", json={"session_id": sid})
    assert resp.status_code == 200
    assert resp.json()["diff_title"] == "차별화 제목"


def test_differentiate_unknown_session_returns_404(client):
    resp = client.post("/api/differentiate", json={"session_id": "없는세션"})
    assert resp.status_code == 404


# ── /api/refine ──────────────────────────────────

def test_refine_ok(client):
    with patch("titlegene.routers.generate.claude_service.analyze", return_value="보고서"):
        r = client.post("/api/analyze", json={"product_name": "p", "content": "c", "target": "t"})
    sid = r.json()["session_id"]

    with patch("titlegene.routers.generate.claude_service.refine", return_value="개선 제목"):
        resp = client.post("/api/refine", json={"session_id": sid, "feedback": "더 젊게"})
    assert resp.status_code == 200
    assert resp.json()["refined_title"] == "개선 제목"


def test_refine_loop_limit_exceeded_returns_400(client):
    with patch("titlegene.routers.generate.claude_service.analyze", return_value="r"):
        r = client.post("/api/analyze", json={"product_name": "p", "content": "c", "target": "t"})
    sid = r.json()["session_id"]

    from titlegene.services.session_store import LoopLimitError
    with patch("titlegene.routers.generate.claude_service.refine", side_effect=LoopLimitError("초과")):
        resp = client.post("/api/refine", json={"session_id": sid, "feedback": "피드백"})
    assert resp.status_code == 400
    assert "초과" in resp.json()["detail"]


def test_refine_unknown_session_returns_404(client):
    resp = client.post("/api/refine", json={"session_id": "없는세션", "feedback": "피드백"})
    assert resp.status_code == 404
