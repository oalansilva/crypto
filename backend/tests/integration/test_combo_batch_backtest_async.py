from __future__ import annotations

from fastapi import FastAPI
import httpx

from app.routes import combo_routes
from app.services.batch_backtest_store import get_batch_backtest_store


def _build_app() -> FastAPI:
    app = FastAPI()
    app.include_router(combo_routes.router)
    app.dependency_overrides[combo_routes.get_current_user] = lambda: "user-123"
    return app


async def test_batch_backtest_start_enqueues_job(monkeypatch):
    app = _build_app()
    store = get_batch_backtest_store()
    captured: dict[str, object] = {}

    def fake_enqueue(job_id: str, payload: dict[str, object]) -> str:
        captured["job_id"] = job_id
        captured["payload"] = payload
        store.update_job(job_id, task_id="task-123")
        return "task-123"

    monkeypatch.setattr(combo_routes, "enqueue_batch_backtest", fake_enqueue)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/combos/backtest/batch",
            json={
                "template_name": "ema_rsi",
                "symbols": ["BTC/USDT", "ETH/USDT"],
                "timeframe": "1d",
                "deep_backtest": False,
            },
        )

    assert response.status_code == 200, response.text
    job_id = response.json()["job_id"]
    assert captured["job_id"] == job_id
    assert captured["payload"] == {
        "template_name": "ema_rsi",
        "symbols": ["BTC/USDT", "ETH/USDT"],
        "timeframe": "1d",
        "data_source": None,
        "start_date": None,
        "end_date": None,
        "period_type": None,
        "deep_backtest": False,
        "custom_ranges": None,
        "initial_capital": 100,
        "direction": "long",
        "user_id": "user-123",
    }

    progress = store.get_job(job_id)
    assert progress is not None
    assert progress["status"] == "queued"
    assert progress["task_id"] == "task-123"
    assert progress["total"] == 2


async def test_batch_backtest_pause_and_cancel_update_shared_state(monkeypatch):
    app = _build_app()
    store = get_batch_backtest_store()

    def fake_enqueue(job_id: str, payload: dict[str, object]) -> str:
        store.update_job(job_id, task_id="task-456")
        return "task-456"

    monkeypatch.setattr(combo_routes, "enqueue_batch_backtest", fake_enqueue)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        create_response = await client.post(
            "/api/combos/backtest/batch",
            json={
                "template_name": "ema_rsi",
                "symbols": ["BTC/USDT"],
                "timeframe": "1d",
                "deep_backtest": False,
            },
        )
        job_id = create_response.json()["job_id"]

        pause_response = await client.post(f"/api/combos/backtest/batch/{job_id}/pause")
        assert pause_response.status_code == 200, pause_response.text
        paused = store.get_job(job_id)
        assert paused is not None
        assert paused["status"] == "paused"
        assert paused["pause_requested"] is True

        # Simulate the worker resuming the same record before a later cancel request.
        store.update_job(job_id, status="running", pause_requested=False, cancel_requested=False)

        cancel_response = await client.post(f"/api/combos/backtest/batch/{job_id}/cancel")
        assert cancel_response.status_code == 200, cancel_response.text
        cancelled = store.get_job(job_id)
        assert cancelled is not None
        assert cancelled["status"] == "running"
        assert cancelled["cancel_requested"] is True
