import json

from fastapi.testclient import TestClient

from app.main import app
from app.routes import lab as lab_routes
from app.routes import market as market_routes


client = TestClient(app)


def test_list_lab_runs_returns_recent_lightweight_payload(tmp_path, monkeypatch):
    monkeypatch.setattr(lab_routes, "_runs_dir", lambda: tmp_path)

    runs = [
        {
            "run_id": "run-old",
            "status": "done",
            "step": "review",
            "created_at_ms": 1000,
            "updated_at_ms": 2000,
        },
        {
            "run_id": "run-new",
            "status": "running",
            "step": "execution",
            "created_at_ms": 3000,
            "updated_at_ms": 4000,
            "trace": {"viewer_url": "http://example.test/lab/runs/run-new"},
            "heavy": {"ignore": True},
        },
    ]

    for item in runs:
        (tmp_path / f"{item['run_id']}.json").write_text(json.dumps(item), encoding="utf-8")

    response = client.get("/api/lab/runs", params={"limit": 5})

    assert response.status_code == 200
    payload = response.json()
    assert [item["run_id"] for item in payload["runs"]] == ["run-new", "run-old"]
    assert payload["runs"][0] == {
        "run_id": "run-new",
        "status": "running",
        "step": "execution",
        "created_at_ms": 3000,
        "updated_at_ms": 4000,
        "viewer_url": "http://example.test/lab/runs/run-new",
    }
    assert "heavy" not in payload["runs"][0]


def test_list_lab_runs_respects_limit_and_ignores_invalid_files(tmp_path, monkeypatch):
    monkeypatch.setattr(lab_routes, "_runs_dir", lambda: tmp_path)
    (tmp_path / "broken.json").write_text("not-json", encoding="utf-8")

    for index in range(25):
        (tmp_path / f"run-{index}.json").write_text(
            json.dumps(
                {
                    "run_id": f"run-{index}",
                    "status": "queued",
                    "step": "upstream",
                    "created_at_ms": index,
                    "updated_at_ms": index,
                }
            ),
            encoding="utf-8",
        )

    response = client.get("/api/lab/runs", params={"limit": 50})

    assert response.status_code == 422


class _MockResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"status={self.status_code}")

    def json(self):
        return self._payload


class _MockAsyncClient:
    calls = 0

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url, params=None):
        type(self).calls += 1
        assert url == "https://api.binance.com/api/v3/ticker/24hr"
        assert params == {"symbols": json.dumps(["BTCUSDT", "ETHUSDT"])}
        return _MockResponse(
            [
                {"symbol": "BTCUSDT", "lastPrice": "65000.12", "priceChangePercent": "1.25"},
                {"symbol": "ETHUSDT", "lastPrice": "3200.50", "priceChangePercent": "-0.75"},
            ]
        )


def test_market_prices_uses_cache(monkeypatch):
    market_routes._PRICE_CACHE.clear()
    _MockAsyncClient.calls = 0
    monkeypatch.setattr(market_routes.httpx, "AsyncClient", _MockAsyncClient)

    first = client.get("/api/market/prices", params={"symbols": "BTCUSDT,ETHUSDT"})
    second = client.get("/api/market/prices", params={"symbols": "BTCUSDT,ETHUSDT"})

    assert first.status_code == 200
    assert second.status_code == 200
    assert _MockAsyncClient.calls == 1
    assert first.json()["prices"] == [
        {"symbol": "BTCUSDT", "price": 65000.12, "change_24h_pct": 1.25},
        {"symbol": "ETHUSDT", "price": 3200.5, "change_24h_pct": -0.75},
    ]
    assert second.json() == first.json()
    assert first.json()["fetched_at"]


class _FailingAsyncClient(_MockAsyncClient):
    async def get(self, url, params=None):
        raise RuntimeError("boom")


def test_market_prices_gracefully_degrades(monkeypatch):
    market_routes._PRICE_CACHE.clear()
    monkeypatch.setattr(market_routes.httpx, "AsyncClient", _FailingAsyncClient)

    response = client.get("/api/market/prices")

    assert response.status_code == 200
    assert response.json() == {"prices": [], "fetched_at": None}
