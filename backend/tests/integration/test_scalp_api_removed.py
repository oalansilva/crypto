from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_scalp_status_endpoint_returns_404_after_router_removal():
    client = TestClient(app)
    response = client.get("/api/scalp/status")
    assert response.status_code == 404
