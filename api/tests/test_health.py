"""
test_health.py
--------------
Tests pytest pour l'endpoint GET /health de l'API Plant Disease Detection.
"""

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health_returns_200() -> None:
    """GET /health doit retourner un statut HTTP 200."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_response_body() -> None:
    """GET /health doit retourner le JSON attendu avec status='ok' et model_version='dummy-v0'."""
    response = client.get("/health")
    data = response.json()
    assert data["status"] == "ok"
    assert data["model_version"] == "dummy-v0"


def test_health_response_keys() -> None:
    """GET /health doit contenir exactement les clés 'status' et 'model_version'."""
    response = client.get("/health")
    data = response.json()
    assert set(data.keys()) == {"status", "model_version"}
