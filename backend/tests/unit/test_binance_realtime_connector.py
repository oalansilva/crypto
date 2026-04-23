from __future__ import annotations

from collections import deque
from types import SimpleNamespace

import httpx
import pytest

import app.services.binance_realtime_connector as connector


def _build_settings(**overrides):
    defaults = {
        "binance_base_url": "https://api.binance.com",
        "binance_ws_base_url": "wss://stream.binance.com:9443",
        "binance_top_pairs_limit": 100,
        "binance_top_pairs_refresh_seconds": 60,
        "binance_top_pairs_ttl_seconds": 180,
        "binance_price_ttl_seconds": 10.0,
        "binance_ws_heartbeat_timeout_seconds": 20.0,
        "binance_ws_reconnect_base_seconds": 1.0,
        "binance_ws_reconnect_max_seconds": 30.0,
        "binance_rate_limit_per_minute": 1200,
        "binance_request_timeout_seconds": 8.0,
        "binance_rest_max_retries": 3,
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


def _build_connector(monkeypatch, **overrides):
    monkeypatch.setattr(connector, "get_settings", lambda: _build_settings(**overrides))
    return connector.BinanceRealtimeConnector()


class _FakeResponse:
    def __init__(self, payload, status_code: int = 200, headers=None):
        self._payload = payload
        self.status_code = status_code
        self.headers = headers or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise ValueError(f"status {self.status_code}")

    def json(self):
        return self._payload


class _FakeAsyncClient:
    def __init__(self, responses, calls):
        self._responses = list(responses)
        self._calls = calls

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url, params):
        self._calls.append((url, params))
        if not self._responses:
            raise AssertionError("Unexpected HTTP request")
        return self._responses.pop(0)


def test_connector_helpers_and_token_bucket_wait_path(monkeypatch):
    assert connector._to_float("12.5") == 12.5
    assert connector._to_float("nan") is None
    assert connector._to_int("5") == 5
    assert connector._to_int("bad") is None
    assert connector._normalize_symbols(["btc/usdt", "BTC/USDT", None, "", "ETHUSDT"]) == [
        "BTCUSDT",
        "ETHUSDT",
    ]

    latency = deque([12.0, 8.0, 14.0])
    assert connector._percentile(latency, 95) == 14.0
    assert connector._percentile(deque(), 95) is None


@pytest.mark.asyncio
async def test_token_bucket_waits_and_short_circuits(monkeypatch):
    marker = iter([0.0, 0.0, 2.0])

    def _monotonic():
        return next(marker, 2.0)

    monkeypatch.setattr(connector.time, "monotonic", _monotonic)
    sleep_calls = []

    async def _sleep(delay: float) -> None:
        sleep_calls.append(delay)

    monkeypatch.setattr(connector.asyncio, "sleep", _sleep)
    monkeypatch.setattr(connector.random, "uniform", lambda _a, _b: 0.0)

    bucket = connector._TokenBucket(max_tokens=2, refill_per_second=1.0)
    bucket._tokens = 1
    await bucket.take(2)

    assert len(sleep_calls) == 1
    assert sleep_calls[0] >= 1.0

    bucket2 = connector._TokenBucket(max_tokens=5, refill_per_second=1.0)
    await bucket2.take(0)
    assert bucket2._tokens == 5


@pytest.mark.asyncio
async def test_safe_request_success_rate_limit_and_failures(monkeypatch):
    c = _build_connector(monkeypatch)
    c._max_rest_retries = 2

    async def no_wait(_cost=1.0):
        return None

    c._rate_limiter.take = no_wait

    requests: list[tuple[str, dict | None]] = []
    sleep_calls: list[float] = []

    monkeypatch.setattr(
        connector.httpx,
        "AsyncClient",
        lambda timeout: _FakeAsyncClient(
            [
                _FakeResponse({"ok": 1}, headers={"X-MBX-USED-WEIGHT-1m": "12"}),
                _FakeResponse({"ok": 2}, headers={"X-MBX-WEIGHT-1M": "1200"}),
            ],
            requests,
        ),
    )

    async def _sleep(delay: float) -> None:
        sleep_calls.append(delay)
        return None

    monkeypatch.setattr(connector.asyncio, "sleep", _sleep)
    result = await c._safe_request("/api/v3/ticker/24hr")
    assert result == {"ok": 1}
    assert c._last_rest_weight_used == 12
    assert c._last_rest_weight_limit is None
    assert requests[0][0] == "https://api.binance.com/api/v3/ticker/24hr"

    requests.clear()
    wait_calls = []

    async def _sleep_retry(delay: float) -> None:
        wait_calls.append(delay)
        return None

    monkeypatch.setattr(connector.asyncio, "sleep", _sleep_retry)
    _rate_limit_responses = iter(
        [
            _FakeResponse({}, status_code=429, headers={"Retry-After": "1.2"}),
            _FakeResponse({"ok": 3}),
        ]
    )

    def _new_client_with_rate_limit_chain(timeout):
        return _FakeAsyncClient([next(_rate_limit_responses)], requests)

    monkeypatch.setattr(
        connector.httpx,
        "AsyncClient",
        lambda timeout: _new_client_with_rate_limit_chain(timeout),
    )
    result = await c._safe_request("/api/v3/ticker/24hr", weight=2.0)
    assert result == {"ok": 3}
    assert wait_calls and wait_calls[-1] == 1.2

    requests.clear()
    c._max_rest_retries = 1
    with pytest.raises(RuntimeError):
        monkeypatch.setattr(
            connector.httpx,
            "AsyncClient",
            lambda timeout: _FakeAsyncClient([_FakeResponse({}, status_code=429)], requests),
        )
        await c._safe_request("/api/v3/ticker/24hr")


@pytest.mark.asyncio
async def test_safe_request_retries_on_http_errors(monkeypatch):
    c = _build_connector(monkeypatch)
    c._max_rest_retries = 2

    async def no_wait(_cost=1.0):
        return None

    c._rate_limiter.take = no_wait

    requests: list[tuple[str, dict | None]] = []
    sleep_calls: list[float] = []

    monkeypatch.setattr(
        connector.httpx,
        "AsyncClient",
        lambda timeout: _FakeAsyncClient(
            [_FakeResponse({}, status_code=500), _FakeResponse({}, status_code=500)],
            requests,
        ),
    )

    async def _sleep(delay: float) -> None:
        sleep_calls.append(delay)

    monkeypatch.setattr(connector.asyncio, "sleep", _sleep)
    with pytest.raises(ValueError):
        await c._safe_request("/api/v3/ticker/24hr")
    assert len(requests) == 2
    assert sleep_calls


@pytest.mark.asyncio
async def test_refresh_top_pairs_and_syncing_flow(monkeypatch):
    c = _build_connector(monkeypatch, binance_top_pairs_limit=3)
    c._max_rest_retries = 1

    async def fake_safe_request(endpoint, params=None, weight=1.0):
        assert endpoint == "/api/v3/ticker/24hr"
        assert weight == 40.0
        return [
            {"symbol": "xrpusdt", "quoteVolume": "10"},
            {"symbol": "btcusdt", "quoteVolume": "50"},
            {"symbol": "ethusdt", "quoteVolume": "20"},
            {"symbol": 5, "quoteVolume": "1000"},
            {"symbol": "ada", "quoteVolume": "100"},
            {"symbol": "ethusdt", "quoteVolume": "30"},
            {"symbol": "bad", "quoteVolume": "nan"},
        ]

    c._safe_request = fake_safe_request

    sync_calls: list[list[str]] = []

    async def fake_sync(symbols):
        sync_calls.append(symbols)

    c._sync_prices_from_rest = fake_sync
    await c._refresh_top_pairs()
    assert c._pairs == ["BTCUSDT", "ETHUSDT", "ETHUSDT"]
    assert len(sync_calls) == 1

    c._prices["BTCUSDT"] = connector._PriceRecord(
        symbol="BTCUSDT",
        price=1.0,
        change_24h_pct=None,
        bid=1.0,
        ask=1.0,
        event_time_ms=1,
        event_to_cache_ms=0.0,
        updated_at_iso="2026-01-01T00:00:00Z",
        updated_at_ts=1.0,
        source="rest-sync",
    )
    await c._refresh_top_pairs()
    assert len(sync_calls) == 1

    c2 = _build_connector(monkeypatch)

    async def fake_safe_request(_endpoint, _params=None, weight=1.0):
        return {}

    c2._safe_request = fake_safe_request
    with pytest.raises(ValueError):
        await c2._refresh_top_pairs()


@pytest.mark.asyncio
async def test_sync_prices_from_rest_prunes_stale_symbols(monkeypatch):
    c = _build_connector(monkeypatch)
    c._pair_ttl_seconds = 10
    c._pairs = ["BTCUSDT"]
    c._prices = {
        "OLD": connector._PriceRecord(
            symbol="OLD",
            price=1.0,
            change_24h_pct=None,
            bid=1.0,
            ask=1.0,
            event_time_ms=111,
            event_to_cache_ms=0.0,
            updated_at_iso="2026-01-01T00:00:00Z",
            updated_at_ts=100.0,
            source="rest-sync",
        )
    }

    async def fake_safe_request(endpoint, params=None, weight=1.0):
        return [
            {"symbol": "BTCUSDT", "price": "64000"},
            {"symbol": "", "price": "1"},
            {"symbol": "ETHUSDT", "price": "2100"},
        ]

    c._safe_request = fake_safe_request
    monkeypatch.setattr(connector.time, "time", lambda: 200.0)
    await c._sync_prices_from_rest(["BTCUSDT", "ETHUSDT"])
    assert "OLD" not in c._prices
    assert "BTCUSDT" in c._prices
    assert "ETHUSDT" in c._prices
    assert c._prices["BTCUSDT"].source == "rest-sync"


@pytest.mark.asyncio
async def test_ws_loop_and_consume_stream_pathways(monkeypatch):
    c = _build_connector(monkeypatch)
    c._pairs = ["BTCUSDT"]
    c._reconnect_base_seconds = 1.0
    c._reconnect_max_seconds = 1.0
    c._pair_ttl_seconds = 10

    async def sync_passthrough(_symbols):
        return None

    c._sync_prices_from_rest = sync_passthrough

    async def current_pairs_once():
        return ["BTCUSDT"]

    async def consume_once(_ws):
        c._pairs_changed.set()

    c._current_pairs = current_pairs_once
    c._consume_ws_stream = consume_once

    connection_calls: list[str] = []

    class _FakeConnect:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

    def fake_connect(*_a, **_k):
        connection_calls.append("connect")
        return _FakeConnect()

    c._shutdown.clear()
    monkeypatch.setattr(connector.websockets, "connect", fake_connect)
    monkeypatch.setattr(connector.time, "time", lambda: 200.0)
    shutdown_calls = {"count": 0}

    async def current_pairs_second():
        shutdown_calls["count"] += 1
        if shutdown_calls["count"] == 1:
            return ["BTCUSDT"]
        c._shutdown.set()
        return ["BTCUSDT"]

    c._current_pairs = current_pairs_second
    await c._ws_loop()
    assert connection_calls == ["connect"]
    assert c._pairs_changed.is_set()
    c._pairs_changed.clear()
    c._shutdown.clear()

    def fake_connect_error(*_a, **_k):
        raise RuntimeError("ws failed")

    reconnect_calls = {"count": 0}
    monkeypatch.setattr(connector.websockets, "connect", fake_connect_error)

    async def fake_current_pairs():
        return ["BTCUSDT"]

    c._current_pairs = fake_current_pairs

    async def fake_sync(symbols):
        reconnect_calls["count"] += 1
        c._shutdown.set()

    c._sync_prices_from_rest = fake_sync
    await c._ws_loop()
    assert reconnect_calls["count"] == 1


@pytest.mark.asyncio
async def test_consume_stream_handles_timeout_invalid_and_fallback_message(monkeypatch):
    c = _build_connector(monkeypatch)
    c._pairs = ["BTCUSDT"]

    async def fake_sync(_pairs):
        pass

    c._sync_prices_from_rest = fake_sync

    class _FakeSocket:
        def __init__(self):
            self.i = 0

        async def recv(self):
            self.i += 1
            if self.i == 1:
                return '{"s":"BTCUSDT","c":"64000","b":"63900","a":"64010","P":"1.4","E":2000}'
            raise connector.asyncio.TimeoutError

    await c._consume_ws_stream(_FakeSocket())
    assert c._ws_disconnect_count == 1

    class _ConnClosed(Exception):
        pass

    monkeypatch.setattr(connector.websockets, "ConnectionClosed", _ConnClosed)

    class _ClosedSocket:
        async def recv(self):
            raise _ConnClosed("closed")

    await c._consume_ws_stream(_ClosedSocket())
    assert c._ws_disconnect_count == 2
    assert "BTCUSDT" in c._prices

    await c._handle_ws_message("not-json")
    await c._handle_ws_message("123")
    c._pairs = []
    await c._handle_ws_message(
        '{"data":{"s":"ETHUSDT","c":"3000","b":"2999","a":"3001","P":"-0.5","E":2000}}'
    )
    assert "ETHUSDT" in c._prices

    c._pairs = []
    await c._handle_ws_message(
        '{"s":"XRPUSDT","c":"3500","b":"3490","a":"3510","P":"0.1","E":2000}'
    )
    assert "XRPUSDT" in c._prices

    c._pairs = ["ETHUSDT"]
    before = set(c._prices)
    await c._handle_ws_message('{"s":"BTCUSDT","c":"100"}')
    assert set(c._prices) == before


@pytest.mark.asyncio
async def test_fallback_prices_and_latest_prices_ordered_with_stale_flags(monkeypatch):
    c = _build_connector(monkeypatch)
    c._prices["BTCUSDT"] = connector._PriceRecord(
        symbol="BTCUSDT",
        price=63000.0,
        change_24h_pct=None,
        bid=62990.0,
        ask=63010.0,
        event_time_ms=1000000,
        event_to_cache_ms=0.0,
        updated_at_iso="2026-01-01T00:00:00Z",
        updated_at_ts=1.0,
        source="rest-sync",
    )
    c._price_ttl_seconds = 1

    async def fake_safe_request(endpoint, params=None, weight=1.0):
        assert endpoint == "/api/v3/ticker/24hr"
        return [
            {"symbol": "ETHUSDT", "lastPrice": "2100", "priceChangePercent": "3"},
            {"symbol": "BTCUSDT", "lastPrice": "oops"},
            {"symbol": "BAD", "priceChangePercent": "1"},
        ]

    c._safe_request = fake_safe_request
    monkeypatch.setattr(connector.time, "time", lambda: 10.0)
    prices, fetched_at, stale = await c.get_latest_prices(["BTCUSDT", "ETHUSDT", "XRPUSDT"])
    assert [item["symbol"] for item in prices] == ["BTCUSDT", "ETHUSDT"]
    assert fetched_at is not None
    assert stale is True

    async def _failing_request(*_a, **_k):
        raise RuntimeError("down")

    c._safe_request = _failing_request
    assert await c._fetch_fallback_prices(["BTCUSDT"]) == []
    assert c._rest_sync_error_count == 1


@pytest.mark.asyncio
async def test_public_accessors_use_singleton_connector(monkeypatch):
    c = _build_connector(monkeypatch)
    c._pairs = ["BTCUSDT"]
    monkeypatch.setattr(connector, "_read_external_snapshot", lambda: None)

    class _DummyConnector:
        def __init__(self, delegate):
            self._delegate = delegate
            self._running = False

        async def get_top_pairs(self):
            return await self._delegate.get_top_pairs()

        async def get_status(self):
            return await self._delegate.get_status()

        async def get_latest_prices(self, symbols=None):
            return await self._delegate.get_latest_prices(symbols)

        async def start(self):
            self._running = True
            self.started = True

        async def stop(self):
            self._running = False
            self.stopped = True

        async def get_connector_status(self, *args):
            return await self.get_status(*args)

    dummy = _DummyConnector(c)
    monkeypatch.setattr(connector, "_connector", dummy)
    dummy.started = False
    dummy.stopped = False

    assert connector.is_running() is False
    top = await connector.get_top_pairs()
    assert top["pairs"] == ["BTCUSDT"]
    status = await connector.get_connector_status()
    assert status["top_pairs_count"] == 1
    await connector.start_binance_realtime_connector()
    await connector.stop_binance_realtime_connector()
    await connector.get_market_latest_prices(["BTCUSDT"])
    assert dummy.started is True
    assert dummy.stopped is True
    assert connector.is_running() is False


@pytest.mark.asyncio
async def test_snapshot_payload_and_external_snapshot_accessors(monkeypatch):
    c = _build_connector(
        monkeypatch, binance_top_pairs_ttl_seconds=10, binance_price_ttl_seconds=5.0
    )
    monkeypatch.setattr(connector.time, "time", lambda: 100.0)

    c._running = True
    c._pairs = ["ETHUSDT", "BTCUSDT"]
    c._pair_cache_updated_at = 95.0
    c._last_pair_refresh_at = 96.0
    c._last_ws_connect_at = 97.0
    c._last_ws_disconnect_at = 98.0
    c._last_ws_message_at = 99.0
    c._last_ws_event_loop_ms = 12.5
    c._pair_snapshot_error_count = 1
    c._rest_sync_error_count = 2
    c._ws_reconnect_count = 3
    c._ws_disconnect_count = 4
    c._last_rest_weight_used = 11
    c._last_rest_weight_limit = 1200
    c._latency_ms.extend([10.0, 20.0, 30.0])
    c._prices = {
        "ETHUSDT": connector._PriceRecord(
            symbol="ETHUSDT",
            price=3000.0,
            change_24h_pct=-1.0,
            bid=2999.0,
            ask=3001.0,
            event_time_ms=1,
            event_to_cache_ms=9.0,
            updated_at_iso="2026-04-23T03:00:00Z",
            updated_at_ts=90.0,
            source="ws",
        ),
        "BTCUSDT": connector._PriceRecord(
            symbol="BTCUSDT",
            price=64000.0,
            change_24h_pct=1.5,
            bid=63999.0,
            ask=64001.0,
            event_time_ms=2,
            event_to_cache_ms=7.0,
            updated_at_iso="2026-04-23T03:01:00Z",
            updated_at_ts=91.0,
            source="rest",
        ),
    }

    payload = await c._build_snapshot_payload()
    assert payload["running"] is True
    assert payload["top_pairs"]["count"] == 2
    assert [item["symbol"] for item in payload["prices"]] == ["BTCUSDT", "ETHUSDT"]
    assert payload["status"]["latency_p95_ms"] == 30.0
    assert payload["status"]["rest_sync_errors"] == 2

    captured: dict[str, object] = {}
    monkeypatch.setattr(
        connector, "write_snapshot", lambda data: captured.setdefault("payload", data)
    )
    await c._flush_snapshot(running=False)
    assert captured["payload"]["running"] is False
    external_payload = dict(payload)
    external_payload["running"] = True

    class _ExternalOnlyConnector:
        _running = False

        async def get_top_pairs(self):
            raise AssertionError("should use external snapshot")

        async def get_status(self):
            raise AssertionError("should use external snapshot")

        async def get_latest_prices(self, symbols=None):
            raise AssertionError("should use external snapshot")

    monkeypatch.setattr(connector, "_connector", _ExternalOnlyConnector())
    monkeypatch.setattr(connector, "read_snapshot", lambda: external_payload)
    monkeypatch.setattr(connector, "snapshot_is_fresh", lambda payload: True)

    assert connector.is_running() is True
    top = await connector.get_top_pairs()
    assert top["pairs"] == ["ETHUSDT", "BTCUSDT"]
    status = await connector.get_connector_status()
    assert status["running"] is True
    assert status["top_pairs_count"] == 2

    prices, fetched_at, stale = await connector.get_market_latest_prices(["ETHUSDT", "BTCUSDT"])
    assert [item["symbol"] for item in prices] == ["ETHUSDT", "BTCUSDT"]
    assert fetched_at == payload["fetched_at"]
    assert stale is False


@pytest.mark.asyncio
async def test_snapshot_helper_branches_and_worker_runner(monkeypatch):
    c = _build_connector(monkeypatch)

    seen: list[bool | None] = []

    async def fake_flush(*, running=None):
        seen.append(running)
        c._shutdown.set()

    monkeypatch.setattr(c, "_flush_snapshot", fake_flush)
    await c._snapshot_loop()
    assert seen == [None]

    fallback_prices = ([{"symbol": "BTCUSDT", "price": 1.0}], "2026-04-23T00:00:00Z", True)

    class _FallbackConnector:
        _running = False

        async def get_top_pairs(self):
            return {
                "pairs": ["LOCAL"],
                "count": 1,
                "is_stale": False,
                "cached_at": "x",
                "ttl_seconds": 60,
            }

        async def get_status(self):
            return {"running": False, "top_pairs_count": 1}

        async def get_latest_prices(self, symbols=None):
            return fallback_prices

        async def start(self):
            self.started = True

        async def stop(self):
            self.stopped = True

    dummy = _FallbackConnector()
    dummy.started = False
    dummy.stopped = False
    monkeypatch.setattr(connector, "_connector", dummy)
    monkeypatch.setattr(connector, "snapshot_is_fresh", lambda payload: bool(payload))

    monkeypatch.setattr(connector, "read_snapshot", lambda: {"running": False})
    assert connector._read_external_snapshot() is None

    monkeypatch.setattr(
        connector,
        "read_snapshot",
        lambda: {"running": True, "top_pairs": "bad", "status": "bad", "prices": "bad"},
    )
    assert await connector.get_top_pairs() == {
        "pairs": [],
        "count": 0,
        "is_stale": False,
        "cached_at": None,
        "ttl_seconds": 0,
    }
    assert await connector.get_connector_status() == {
        "running": True,
        "service": "binance-realtime-connector",
        "pair_limit": 0,
        "pair_refresh_seconds": 0,
        "price_ttl_seconds": 0,
        "ws_stream_limit": 0,
    }
    assert await connector.get_market_latest_prices(["BTCUSDT"]) == ([], None, True)

    monkeypatch.setattr(connector, "read_snapshot", lambda: None)
    assert await connector.get_top_pairs() == await dummy.get_top_pairs()
    assert await connector.get_connector_status() == await dummy.get_status()
    assert await connector.get_market_latest_prices(["BTCUSDT"]) == fallback_prices

    real_connector = _build_connector(monkeypatch)
    started = {"value": False}

    async def real_start():
        started["value"] = True

    monkeypatch.setattr(real_connector, "start", real_start)
    monkeypatch.setattr(connector, "_connector", real_connector)
    monkeypatch.setenv("BINANCE_REALTIME_ENABLED", "0")
    await connector.start_binance_realtime_connector()
    assert started["value"] is False
    monkeypatch.setenv("BINANCE_REALTIME_ENABLED", "1")
    await connector.start_binance_realtime_connector()
    assert started["value"] is True

    events: list[str] = []

    class _Loop:
        def add_signal_handler(self, _sig, handler):
            handler()

    class _WorkerConnector:
        async def start(self):
            events.append("start")

        async def stop(self):
            events.append("stop")

    monkeypatch.setattr(connector.asyncio, "get_running_loop", lambda: _Loop())
    monkeypatch.setattr(connector, "_connector", _WorkerConnector())
    await connector.run_binance_realtime_worker()
    assert events == ["start", "stop"]
