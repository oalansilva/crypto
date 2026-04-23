from __future__ import annotations

from datetime import datetime

from app.services.ohlcv_backfill_store import OhlcvBackfillStore
from app.services.ohlcv_backfill_store import (
    _default_job_state,
    _default_timeframe_state,
)

import app.services.ohlcv_backfill_store as backfill_store_module


def _new_store(monkeypatch):
    monkeypatch.setattr(backfill_store_module, "get_redis_client", lambda: None)
    backfill_store_module._MEMORY_JOBS.clear()
    backfill_store_module._MEMORY_JOBS_LIST.clear()
    return OhlcvBackfillStore()


def test_backfill_store_init_save_update_and_list(monkeypatch):
    store = _new_store(monkeypatch)

    job = _default_job_state(
        job_id="job-1",
        symbol="BTC/USDT",
        timeframes_state={"1d": _default_timeframe_state("1d", "2026-01-01T00:00:00+00:00", 10)},
        requested_window={"start": "2026-01-01T00:00:00+00:00", "end": "2026-01-02T00:00:00+00:00"},
        provider="ccxt",
    )
    store.init_job(job)

    duplicate = store.init_job(job)
    assert duplicate["job_id"] == "job-1"
    assert duplicate["attempts"] == 0

    updated = store.update_job(
        "job-1", processed=5, status="running", percent=50.5, eta_seconds=10.0
    )
    assert updated is not None
    assert updated["processed"] == 5
    assert updated["status"] == "running"

    items, total = store.list_jobs(page=1, page_size=20)
    assert total == 1
    assert items[0]["job_id"] == "job-1"

    store.save_job(
        {
            "job_id": "job-2",
            "symbol": "ETH/USDT",
            "timeframes": ["1h"],
            "status": "pending",
            "requested_window": {},
            "processed": 0,
            "written": 0,
            "duplicates": 0,
            "attempts": 0,
            "requested_source": None,
            "page_size": 1000,
            "max_requests_per_minute": 60,
        }
    )
    items_status_filtered, total_status_filtered = store.list_jobs(status_filter="pending")
    assert total_status_filtered == 1
    assert items_status_filtered[0]["symbol"] == "ETH/USDT"

    paginated, total_paginated = store.list_jobs(page=2, page_size=1)
    assert total_paginated == 2
    assert len(paginated) == 1


def test_backfill_store_exists_active_and_events(monkeypatch):
    store = _new_store(monkeypatch)
    now = datetime.utcnow().isoformat()
    store.save_job(
        {
            "job_id": "job-active",
            "symbol": "BTC/USDT",
            "timeframes": ["1d"],
            "status": "pending",
            "timeframe_states": {"1d": {}},
            "requested_window": {},
            "processed": 0,
            "written": 0,
            "duplicates": 0,
            "attempts": 0,
            "request_source": None,
            "page_size": 1000,
            "max_requests_per_minute": 60,
            "created_at": now,
            "started_at": None,
            "updated_at": now,
            "finished_at": None,
            "percent": 0,
            "eta_seconds": None,
            "events": [],
        }
    )
    assert store.exists_active_for_symbol("BTC/USDT") is True

    store.update_job("job-active", status="completed")
    assert store.exists_active_for_symbol("BTC/USDT") is False

    store.record_event("job-active", {"message": "started", "level": "info", "ts": now})
    final = store.get_job("job-active")
    assert final["events"][0]["message"] == "started"

    for idx in range(90):
        store.record_event(
            "job-active",
            {"message": f"event-{idx}", "level": "info", "ts": now},
        )
    final = store.get_job("job-active")
    assert len(final["events"]) <= 60
