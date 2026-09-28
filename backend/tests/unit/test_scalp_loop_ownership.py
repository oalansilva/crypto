from __future__ import annotations

import asyncio

from app import main
from app.services.scalp_loop import api_scalp_loop_enabled
from app.workers.runtime_worker import _env_enabled


def test_api_loop_fallback_is_enabled_without_an_override(monkeypatch):
    monkeypatch.delenv("SCALP_API_LOOP_ENABLED", raising=False)
    assert api_scalp_loop_enabled() is True


def test_api_loop_can_yield_to_dedicated_dev_worker(monkeypatch):
    monkeypatch.setenv("SCALP_API_LOOP_ENABLED", "0")
    monkeypatch.setenv("RUN_SCALP_LOOP", "1")
    assert api_scalp_loop_enabled() is False
    assert _env_enabled("RUN_SCALP_LOOP") is True


def test_api_only_and_production_fallback_can_be_explicitly_enabled(monkeypatch):
    monkeypatch.setenv("SCALP_API_LOOP_ENABLED", "true")
    assert api_scalp_loop_enabled() is True


def test_api_startup_yields_loop_when_dedicated_worker_owns_it(monkeypatch):
    monkeypatch.setattr(main, "should_start_ohlcv_ingestion", lambda: False)
    monkeypatch.setattr(main, "should_start_binance_realtime_connector", lambda: False)
    monkeypatch.setattr(main, "should_start_backfill_scheduler", lambda: False)
    monkeypatch.setattr(main, "api_scalp_loop_enabled", lambda: False)
    started = []

    async def start_loop():
        started.append(True)

    monkeypatch.setattr(main, "start_scalp_loop", start_loop)
    asyncio.run(main._start_noncritical_services())
    assert started == []
