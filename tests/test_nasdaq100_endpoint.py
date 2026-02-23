from fastapi.testclient import TestClient

from app.main import app


def test_nasdaq100_endpoint_returns_payload():
    client = TestClient(app)
    res = client.get("/api/markets/us/nasdaq100")
    assert res.status_code == 200
    data = res.json()
    assert "symbols" in data
    assert isinstance(data["symbols"], list)
    assert data["count"] == len(data["symbols"])
    assert data["count"] == 100
    assert "AAPL" in data["symbols"]
