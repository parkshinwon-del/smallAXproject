import pytest
from fastapi.testclient import TestClient


def test_health_ok(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    from titlegene.main import app
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_missing_api_key_raises(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    import importlib
    import titlegene.config as cfg
    importlib.reload(cfg)
    with pytest.raises(SystemExit):
        cfg.validate()
