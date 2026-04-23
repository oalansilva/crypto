from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

import app.main as main
import app.routes.market as market_route


@pytest.mark.asyncio
async def test_market_endpoints_cover_running_and_nonrunning_paths(monkeypatch):
    def fallback_payload(symbols: list[str]):
        return {
            "prices": [{"symbol": symbols[0], "price": 1.0, "change_24h_pct": 2.5}],
            "fetched_at": "x",
        }

    async def fetch_latest(symbols):
        return (
            [
                {"symbol": "BTCUSDT", "price": 64000.0, "change_24h_pct": 1.2},
                {"symbol": "ETHUSDT", "price": 3000.0, "change_24h_pct": -0.5},
            ],
            "2026-04-18T22:30:00Z",
            False,
        )

    async def fetch_latest_error(_symbols):
        raise RuntimeError("connector failure")

    async def fetch_fallback(symbols):
        return fallback_payload(list(symbols))

    async def fetch_failed(_symbols):
        raise RuntimeError("not used")

    async def latest_top_pairs():
        return {
            "pairs": ["BTCUSDT", "ETHUSDT"],
            "count": 2,
            "is_stale": False,
            "cached_at": "2026-04-18T22:00:00Z",
            "ttl_seconds": 60,
        }

    async def latest_status():
        return {"running": True, "pair_limit": 100}

    monkeypatch.setattr(market_route, "is_running", lambda: True)
    monkeypatch.setattr(market_route, "get_market_latest_prices", fetch_latest)
    market_route._PRICE_CACHE.clear()

    out_running = await market_route.get_market_prices("BTCUSDT,ETHUSDT")
    assert [item["symbol"] for item in out_running["prices"]] == ["BTCUSDT", "ETHUSDT"]
    assert out_running["fetched_at"] == "2026-04-18T22:30:00Z"

    monkeypatch.setattr(market_route, "get_market_latest_prices", fetch_latest_error)
    monkeypatch.setattr(market_route, "_fetch_binance_prices", fetch_fallback)
    market_route._PRICE_CACHE.clear()
    out_fallback = await market_route.get_market_prices("BTCUSDT")
    assert out_fallback == {
        "prices": [{"symbol": "BTCUSDT", "price": 1.0, "change_24h_pct": 2.5}],
        "fetched_at": "x",
    }

    monkeypatch.setattr(market_route, "is_running", lambda: False)
    monkeypatch.setattr(market_route, "_fetch_binance_prices", fetch_fallback)
    market_route._PRICE_CACHE.clear()
    out_not_running = await market_route.get_market_prices("BTCUSDT")
    assert out_not_running["prices"][0]["symbol"] == "BTCUSDT"
    assert out_not_running["fetched_at"] == "x"

    assert await market_route.get_binance_top_pairs() == {
        "running": False,
        "pairs": [],
        "count": 0,
        "cached_at": None,
        "is_stale": False,
        "ttl_seconds": 0,
    }

    monkeypatch.setattr(market_route, "is_running", lambda: True)
    monkeypatch.setattr(market_route, "get_top_pairs", latest_top_pairs)
    assert await market_route.get_binance_top_pairs() == await latest_top_pairs()

    monkeypatch.setattr(market_route, "is_running", lambda: False)
    assert await market_route.get_binance_realtime_prices() == {
        "running": False,
        "prices": [],
        "fetched_at": None,
        "is_stale": True,
    }

    async def live_prices(_symbols):
        return (
            [{"symbol": "BTCUSDT", "price": 1.0, "change_24h_pct": 2.5}],
            "2026-04-18T22:30:00Z",
            True,
        )

    monkeypatch.setattr(market_route, "is_running", lambda: True)
    monkeypatch.setattr(market_route, "get_market_latest_prices", live_prices)
    prices_running = await market_route.get_binance_realtime_prices("BTCUSDT")
    assert prices_running["running"] is True
    assert prices_running["prices"][0]["symbol"] == "BTCUSDT"

    async def latest_prices_fail(_symbols):
        raise RuntimeError("down")

    monkeypatch.setattr(market_route, "get_market_latest_prices", latest_prices_fail)
    assert await market_route.get_binance_realtime_prices("BTCUSDT") == {
        "running": False,
        "prices": [],
        "fetched_at": None,
        "is_stale": True,
    }

    monkeypatch.setattr(market_route, "is_running", lambda: False)
    assert await market_route.get_binance_status() == {
        "running": False,
        "service": "binance-realtime-connector",
        "pair_limit": 0,
        "pair_refresh_seconds": 0,
        "price_ttl_seconds": 0,
    }

    monkeypatch.setattr(market_route, "is_running", lambda: True)
    monkeypatch.setattr(market_route, "get_connector_status", latest_status)
    status_running = await market_route.get_binance_status()
    assert status_running["running"] is True
    assert status_running["pair_limit"] == 100

    assert market_route._to_fallback_payload(
        [{"symbol": "BTCUSDT", "price": 1.0, "change_24h_pct": None}, {"foo": "bar"}]
    ) == [{"symbol": "BTCUSDT", "price": 1.0, "change_24h_pct": None}]

    monkeypatch.setattr(market_route, "is_running", lambda: False)
    monkeypatch.setattr(market_route, "_fetch_binance_prices", fetch_failed)
    market_route._PRICE_CACHE.clear()
    failed = await market_route.get_market_prices("BTCUSDT")
    assert failed == {"prices": [], "fetched_at": None}


@pytest.mark.asyncio
async def test_main_lifespan_starts_and_stops_binance_connector(monkeypatch):
    lifecycle_calls: list[str] = []

    async def start_connector():
        lifecycle_calls.append("start")

    async def stop_connector():
        lifecycle_calls.append("stop")

    async def start_snapshot_worker():
        lifecycle_calls.append("start_worker")

    async def stop_snapshot_worker():
        lifecycle_calls.append("stop_worker")

    def start_ohlcv():
        lifecycle_calls.append("start_ohlcv")

    def stop_ohlcv():
        lifecycle_calls.append("stop_ohlcv")

    class _SignalMonitorStub:
        def __init__(self):
            self.stopped = False

        def stop(self):
            self.stopped = True

    class _BackfillSchedulerStub:
        def __init__(self):
            self.started = False
            self.stopped = False

        def start_scheduler(self):
            self.started = True

        def stop_scheduler(self):
            self.stopped = True

    signal_stub = _SignalMonitorStub()
    scheduler_stub = _BackfillSchedulerStub()

    class _WorkflowSession:
        def query(self, model):
            return self

        def filter(self, *_, **__):
            return self

        def first(self):
            return None

        def all(self):
            return []

        def add(self, *_args, **_kwargs):
            return None

        def commit(self):
            return None

        def close(self):
            lifecycle_calls.append("workflow_db_closed")

    monkeypatch.setattr(main, "start_binance_realtime_connector", start_connector)
    monkeypatch.setattr(main, "stop_binance_realtime_connector", stop_connector)
    monkeypatch.setattr(main, "start_signal_feed_snapshot_worker", start_snapshot_worker)
    monkeypatch.setattr(main, "stop_signal_feed_snapshot_worker", stop_snapshot_worker)
    monkeypatch.setattr(main, "start_ohlcv_ingestion", start_ohlcv)
    monkeypatch.setattr(main, "stop_ohlcv_ingestion", stop_ohlcv)
    monkeypatch.setattr(main, "signal_monitor", signal_stub)
    monkeypatch.setattr(main, "get_backfill_service", lambda: scheduler_stub)
    monkeypatch.setattr(
        main,
        "Base",
        SimpleNamespace(metadata=SimpleNamespace(create_all=lambda *_args, **_kwargs: None)),
    )
    monkeypatch.setattr(main, "engine", object())
    monkeypatch.setattr(main, "sync_postgres_identity_sequences", lambda: None)
    monkeypatch.setattr(main, "seed_combo_templates_if_empty", lambda: None)

    import app.database as app_database
    import app.workflow_database as workflow_database
    import app.workflow_models as workflow_models

    monkeypatch.setattr(app_database, "ensure_runtime_schema_migrations", lambda: None)
    monkeypatch.setattr(workflow_database, "init_workflow_schema", lambda: None)
    monkeypatch.setattr(workflow_database, "get_workflow_db", lambda: iter([_WorkflowSession()]))
    monkeypatch.setattr(workflow_database, "bootstrap_project_workflow_db", lambda *_: None)
    monkeypatch.setattr(workflow_models, "Project", object)

    async_context = main.lifespan(main.app)
    await async_context.__aenter__()
    await async_context.__aexit__(None, None, None)

    assert lifecycle_calls[0] == "workflow_db_closed"
    assert scheduler_stub.started is True
    assert scheduler_stub.stopped is True
    assert "start" in lifecycle_calls
    assert "stop" in lifecycle_calls
    assert lifecycle_calls.index("start") > lifecycle_calls.index("workflow_db_closed")
    assert lifecycle_calls.index("start") < lifecycle_calls.index("stop")
    assert "start_ohlcv" in lifecycle_calls
    assert lifecycle_calls.index("start_ohlcv") < lifecycle_calls.index("stop_ohlcv")
    assert signal_stub.stopped
    assert "stop_worker" in lifecycle_calls
    assert "workflow_db_closed" in lifecycle_calls


@pytest.mark.asyncio
async def test_start_noncritical_services_logs_timeout_and_failures(monkeypatch):
    errors: list[str] = []
    exceptions: list[str] = []

    def failing_ohlcv():
        raise RuntimeError("ohlcv")

    async def start_connector():
        return None

    async def fake_wait_for(coro, timeout):
        coro.close()
        raise asyncio.TimeoutError()

    class _SchedulerStub:
        def start_scheduler(self):
            raise RuntimeError("scheduler")

    monkeypatch.setattr(main, "start_ohlcv_ingestion", failing_ohlcv)
    monkeypatch.setattr(main, "start_binance_realtime_connector", start_connector)
    monkeypatch.setattr(main.asyncio, "wait_for", fake_wait_for)
    monkeypatch.setattr(main, "get_backfill_service", lambda: _SchedulerStub())
    monkeypatch.setattr(main.logger, "error", lambda message, *a, **k: errors.append(str(message)))
    monkeypatch.setattr(
        main.logger,
        "exception",
        lambda message, *a, **k: exceptions.append(str(message)),
    )

    await main._start_noncritical_services()

    assert "Timed out while starting Binance realtime connector" in errors
    assert any("Failed to start OHLCV ingestion service" in item for item in exceptions)
    assert any("Failed to start OHLCV backfill scheduler" in item for item in exceptions)

    async def fake_wait_for_error(coro, timeout):
        coro.close()
        raise RuntimeError("connector")

    monkeypatch.setattr(main.asyncio, "wait_for", fake_wait_for_error)
    await main._start_noncritical_services()
    assert any("Failed to start Binance realtime connector" in item for item in exceptions)


@pytest.mark.asyncio
async def test_lifespan_cancels_pending_noncritical_startup(monkeypatch):
    started = asyncio.Event()
    cancelled = asyncio.Event()

    async def pending_start():
        started.set()
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            cancelled.set()
            raise

    class _SignalMonitorStub:
        def stop(self):
            return None

    class _BackfillSchedulerStub:
        def stop_scheduler(self):
            return None

    class _WorkflowSession:
        def query(self, model):
            return self

        def filter(self, *_, **__):
            return self

        def first(self):
            return None

        def all(self):
            return []

        def add(self, *_args, **_kwargs):
            return None

        def commit(self):
            return None

        def close(self):
            return None

    monkeypatch.setattr(main, "_start_noncritical_services", pending_start)
    monkeypatch.setattr(main, "stop_binance_realtime_connector", lambda: asyncio.sleep(0))
    monkeypatch.setattr(main, "stop_signal_feed_snapshot_worker", lambda: asyncio.sleep(0))
    monkeypatch.setattr(main, "stop_ohlcv_ingestion", lambda: None)
    monkeypatch.setattr(main, "signal_monitor", _SignalMonitorStub())
    monkeypatch.setattr(main, "get_backfill_service", lambda: _BackfillSchedulerStub())
    monkeypatch.setattr(
        main,
        "Base",
        SimpleNamespace(metadata=SimpleNamespace(create_all=lambda *_args, **_kwargs: None)),
    )
    monkeypatch.setattr(main, "engine", object())
    monkeypatch.setattr(main, "sync_postgres_identity_sequences", lambda: None)
    monkeypatch.setattr(main, "seed_combo_templates_if_empty", lambda: None)

    import app.database as app_database
    import app.workflow_database as workflow_database
    import app.workflow_models as workflow_models

    monkeypatch.setattr(app_database, "ensure_runtime_schema_migrations", lambda: None)
    monkeypatch.setattr(workflow_database, "init_workflow_schema", lambda: None)
    monkeypatch.setattr(workflow_database, "get_workflow_db", lambda: iter([_WorkflowSession()]))
    monkeypatch.setattr(workflow_database, "bootstrap_project_workflow_db", lambda *_: None)
    monkeypatch.setattr(workflow_models, "Project", object)

    async_context = main.lifespan(main.app)
    await async_context.__aenter__()
    await started.wait()
    assert main.app.state.noncritical_services_task.done() is False
    await async_context.__aexit__(None, None, None)
    assert cancelled.is_set()
