from __future__ import annotations

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
        return ([{"symbol": "BTCUSDT", "price": 1.0, "change_24h_pct": 2.5}], "2026-04-18T22:30:00Z", True)

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

    class _SignalMonitorStub:
        def __init__(self):
            self.stopped = False

        def stop(self):
            self.stopped = True

    signal_stub = _SignalMonitorStub()

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
    monkeypatch.setattr(main, "signal_monitor", signal_stub)
    monkeypatch.setattr(main, "Base", SimpleNamespace(metadata=SimpleNamespace(create_all=lambda *_: None)))
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

    assert lifecycle_calls[0] == "start"
    assert lifecycle_calls[-1] == "stop"
    assert signal_stub.stopped
    assert "stop_worker" in lifecycle_calls
    assert "workflow_db_closed" in lifecycle_calls
