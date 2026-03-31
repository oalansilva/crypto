import json
import asyncio

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routes import lab as lab_routes
from app.routes import market as market_routes


app = FastAPI()
app.include_router(lab_routes.router)
app.include_router(market_routes.router)
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
            "input": {"user_id": "tester"},
        },
        {
            "run_id": "run-new",
            "status": "running",
            "step": "execution",
            "created_at_ms": 3000,
            "updated_at_ms": 4000,
            "trace": {"viewer_url": "http://example.test/lab/runs/run-new"},
            "heavy": {"ignore": True},
            "input": {"user_id": "tester"},
        },
    ]

    for item in runs:
        (tmp_path / f"{item['run_id']}.json").write_text(json.dumps(item), encoding="utf-8")

    payload = asyncio.run(lab_routes.list_runs(limit=5, current_user_id="tester")).model_dump()
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
                    "input": {"user_id": "tester"},
                }
            ),
            encoding="utf-8",
        )

    payload = asyncio.run(lab_routes.list_runs(limit=20, current_user_id="tester")).model_dump()
    assert len(payload["runs"]) == 20
    assert payload["runs"][0]["run_id"] == "run-24"


class _FailingAsyncClient:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url, params=None):
        raise RuntimeError("boom")


def test_market_prices_gracefully_degrades(monkeypatch):
    market_routes._PRICE_CACHE.clear()
    monkeypatch.setattr(market_routes.httpx, "AsyncClient", _FailingAsyncClient)

    response = client.get("/api/market/prices")

    assert response.status_code == 200
    assert response.json() == {"prices": [], "fetched_at": None}
