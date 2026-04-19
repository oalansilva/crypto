from __future__ import annotations

import json
from types import SimpleNamespace

import pytest
from redis.exceptions import RedisError

from app.routes import combo_routes
from app.services import batch_backtest_queue
from app.services.batch_backtest_store import BatchBacktestStore, get_batch_backtest_store
from app.services.redis_store import get_redis_client
from app.tasks import batch_backtest_tasks


class _ExplodingRedis:
    def __init__(self, *, get_exc: Exception | None = None, set_exc: Exception | None = None):
        self._get_exc = get_exc
        self._set_exc = set_exc

    def get(self, _key: str):
        if self._get_exc is not None:
            raise self._get_exc
        return None

    def setex(self, _key: str, _ttl: int, _payload: str):
        if self._set_exc is not None:
            raise self._set_exc

    def pipeline(self):
        raise RedisError("pipeline unavailable")


class _PipelineRedis:
    def __init__(self):
        self.entries: list[str] = []

    def get(self, _key: str):
        return None

    def setex(self, _key: str, _ttl: int, _payload: str):
        return None

    def pipeline(self):
        return self

    def lpush(self, _key: str, payload: str):
        self.entries.append(payload)
        return self

    def ltrim(self, _key: str, _start: int, _end: int):
        return self

    def expire(self, _key: str, _ttl: int):
        return self

    def execute(self):
        return True


def _reset_store_caches():
    get_batch_backtest_store.cache_clear()
    get_redis_client.cache_clear()


def test_enqueue_batch_backtest_success_updates_task_id(monkeypatch):
    _reset_store_caches()
    store = BatchBacktestStore()
    store.init_job("job-1", 2)
    monkeypatch.setattr(batch_backtest_queue, "get_batch_backtest_store", lambda: store)

    class _Result:
        id = "task-1"

    monkeypatch.setattr(
        batch_backtest_queue.run_batch_backtest_task,
        "delay",
        lambda job_id, payload: _Result(),
    )

    task_id = batch_backtest_queue.enqueue_batch_backtest("job-1", {"symbols": ["BTC/USDT"]})

    assert task_id == "task-1"
    assert store.get_job("job-1")["task_id"] == "task-1"


def test_enqueue_batch_backtest_failure_marks_job_failed(monkeypatch):
    _reset_store_caches()
    store = BatchBacktestStore()
    store.init_job("job-2", 1)
    monkeypatch.setattr(batch_backtest_queue, "get_batch_backtest_store", lambda: store)

    def _raise(*_args, **_kwargs):
        raise RuntimeError("broker down")

    monkeypatch.setattr(batch_backtest_queue.run_batch_backtest_task, "delay", _raise)

    with pytest.raises(RuntimeError, match="broker down"):
        batch_backtest_queue.enqueue_batch_backtest("job-2", {"symbols": ["BTC/USDT"]})

    job = store.get_job("job-2")
    assert job["status"] == "failed"
    assert "queue dispatch failed" in job["last_error"]


def test_batch_backtest_store_falls_back_from_redis_failures():
    store = BatchBacktestStore()
    store._redis = _ExplodingRedis(
        get_exc=RedisError("get failed"), set_exc=RedisError("set failed")
    )

    assert store.get_job("missing-job") is None
    assert store._redis is None

    store._redis = _ExplodingRedis(set_exc=RedisError("set failed"))
    saved = store.save_job({"job_id": "job-3", "status": "queued"})

    assert saved["job_id"] == "job-3"
    assert store._redis is None
    assert store.get_job("job-3")["status"] == "queued"


def test_batch_backtest_store_handles_existing_jobs_missing_updates_and_dead_letters():
    store = BatchBacktestStore()

    first = store.init_job("job-4", 3)
    second = store.init_job("job-4", 99)
    assert first["total"] == second["total"] == 3

    assert store.update_job("missing-job", status="running") is None

    redis = _PipelineRedis()
    store._redis = redis
    store.record_dead_letter(
        job_id="job-4",
        task_id="task-4",
        payload={"symbol": "BTC/USDT"},
        reason="failed permanently",
        retry_count=3,
    )
    assert len(redis.entries) == 1
    assert json.loads(redis.entries[0])["job_id"] == "job-4"

    store._redis = _ExplodingRedis()
    store.record_dead_letter(
        job_id="job-4",
        task_id="task-4",
        payload={"symbol": "ETH/USDT"},
        reason="fallback",
        retry_count=1,
    )
    assert store._redis is None


def test_get_redis_client_returns_none_for_empty_url(monkeypatch):
    _reset_store_caches()
    monkeypatch.setattr(
        "app.services.redis_store.get_settings",
        lambda: SimpleNamespace(redis_url=""),
    )
    assert get_redis_client() is None


def test_batch_backtest_task_hooks_update_store(monkeypatch):
    store = BatchBacktestStore()
    store.init_job("job-5", 1)
    monkeypatch.setattr(batch_backtest_tasks, "get_batch_backtest_store", lambda: store)
    monkeypatch.setattr(
        batch_backtest_tasks.BatchBacktestTask,
        "request",
        SimpleNamespace(retries=2, id="task-5"),
        raising=False,
    )

    task = batch_backtest_tasks.BatchBacktestTask()
    task.on_retry(RuntimeError("retry me"), "task-5", ("job-5", {"a": 1}), {}, None)
    retry_job = store.get_job("job-5")
    assert retry_job["status"] == "retrying"
    assert retry_job["retry_count"] == 2
    assert retry_job["task_id"] == "task-5"

    task.on_failure(RuntimeError("boom"), "task-5", ("job-5", {"a": 1}), {}, None)
    failed_job = store.get_job("job-5")
    assert failed_job["status"] == "failed"
    assert failed_job["dead_lettered"] is True


def test_run_batch_backtest_task_runs_job(monkeypatch):
    store = BatchBacktestStore()
    store.init_job("job-6", 1)
    monkeypatch.setattr(batch_backtest_tasks, "get_batch_backtest_store", lambda: store)

    calls: list[tuple[str, dict[str, object]]] = []

    def fake_run(job_id: str, payload: dict[str, object]) -> None:
        calls.append((job_id, payload))

    monkeypatch.setattr(batch_backtest_tasks, "run_batch_backtest", fake_run)

    result = batch_backtest_tasks.run_batch_backtest_task.apply(
        args=("job-6", {"symbols": ["BTC/USDT"]}),
        throw=True,
    ).result

    assert result["job_id"] == "job-6"
    assert result["task_id"]
    assert calls == [("job-6", {"symbols": ["BTC/USDT"]})]
    assert store.get_job("job-6")["status"] == "running"


@pytest.mark.asyncio
async def test_start_batch_backtest_returns_503_when_enqueue_fails(monkeypatch):
    from fastapi import FastAPI
    import httpx

    test_app = FastAPI()
    test_app.include_router(combo_routes.router)
    test_app.dependency_overrides[combo_routes.get_current_user] = lambda: "user-123"

    def explode(*_args, **_kwargs):
        raise RuntimeError("queue unavailable")

    monkeypatch.setattr(combo_routes, "enqueue_batch_backtest", explode)

    transport = httpx.ASGITransport(app=test_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/api/combos/backtest/batch",
            json={
                "template_name": "ema_rsi",
                "symbols": ["BTC/USDT"],
                "timeframe": "1d",
                "deep_backtest": False,
            },
        )

    assert response.status_code == 503
    assert response.json()["detail"] == "Batch queue is unavailable"
