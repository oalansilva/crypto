from __future__ import annotations

from types import SimpleNamespace

import pytest

import app.binance_realtime_worker as worker


class _Response:
    def __init__(self, payload, status_code: int = 200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"status {self.status_code}")

    def json(self):
        return self._payload


class _Client:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls: list[tuple[str, dict | None]] = []

    async def get(self, url, params=None):
        self.calls.append((url, params))
        if not self._responses:
            raise AssertionError("Unexpected request")
        return self._responses.pop(0)


@pytest.mark.asyncio
async def test_worker_fetch_helpers_and_payload_building():
    assert worker._to_float("12.5") == 12.5
    assert worker._to_float("nan") is None
    assert worker._is_supported_binance_symbol("BTCUSDT") is True
    assert worker._is_supported_binance_symbol("BTCBTC") is False
    assert worker._timestamp_to_iso(None) is None
    assert worker._utc_now_iso().endswith("Z")

    top_pairs_client = _Client(
        [
            _Response(
                [
                    {"symbol": "BTCUSDT", "quoteVolume": "400"},
                    {"symbol": "ETHUSDT", "quoteVolume": "200"},
                    {"symbol": "BAD", "quoteVolume": "999"},
                    {"symbol": "SOLUSDT", "quoteVolume": "300"},
                ]
            )
        ]
    )
    pairs = await worker._fetch_top_pairs(
        top_pairs_client,
        base_url="https://api.binance.com",
        pair_limit=2,
    )
    assert pairs == ["BTCUSDT", "SOLUSDT"]

    price_client = _Client(
        [
            _Response(
                {
                    "lastPrice": "64000",
                    "priceChangePercent": "1.5",
                    "bidPrice": None,
                    "askPrice": None,
                }
            ),
            _Response({"lastPrice": "3000", "priceChangePercent": "-1.0", "bidPrice": "2999"}),
            _Response({}, status_code=500),
        ]
    )
    prices = await worker._fetch_price_snapshot(
        price_client,
        base_url="https://api.binance.com",
        symbols=["BTCUSDT", "ETHUSDT", "XRPUSDT"],
    )
    assert [item["symbol"] for item in prices] == ["BTCUSDT", "ETHUSDT"]
    assert prices[0]["bid"] == prices[0]["price"]
    assert prices[0]["ask"] == prices[0]["price"]

    payload = worker._build_snapshot_payload(
        running=True,
        pair_limit=5,
        pair_refresh_seconds=60,
        price_ttl_seconds=10.0,
        ws_stream_limit=2,
        pairs=["BTCUSDT", "ETHUSDT"],
        prices=prices,
        top_pairs_cached_at_ts=100.0,
        last_pair_refresh_at_ts=101.0,
        pair_refresh_errors=1,
        rest_sync_errors=2,
    )
    assert payload["running"] is True
    assert payload["top_pairs"]["count"] == 2
    assert payload["status"]["ws_stream_limit"] == 2
    assert payload["status"]["pair_refresh_errors"] == 1
    assert payload["status"]["rest_sync_errors"] == 2


@pytest.mark.asyncio
async def test_run_worker_writes_running_and_stopped_snapshots(monkeypatch):
    handlers = []

    class _Loop:
        def add_signal_handler(self, _sig, handler):
            handlers.append(handler)

    class _AsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, url, params=None):
            if params is None:
                return _Response(
                    [
                        {"symbol": "BTCUSDT", "quoteVolume": "400"},
                        {"symbol": "ETHUSDT", "quoteVolume": "200"},
                    ]
                )
            return _Response(
                {
                    "lastPrice": "64000",
                    "priceChangePercent": "1.2",
                    "bidPrice": "63999",
                    "askPrice": "64001",
                }
            )

    monkeypatch.setattr(
        worker,
        "get_settings",
        lambda: SimpleNamespace(
            binance_base_url="https://api.binance.com",
            binance_top_pairs_limit=2,
            binance_ws_stream_limit=1,
            binance_top_pairs_refresh_seconds=60,
            binance_price_ttl_seconds=10.0,
            binance_request_timeout_seconds=2.0,
        ),
    )
    monkeypatch.setattr(worker.asyncio, "get_running_loop", lambda: _Loop())
    monkeypatch.setattr(worker.httpx, "AsyncClient", lambda timeout: _AsyncClient())
    monkeypatch.setattr(worker.time, "time", lambda: 100.0)

    written: list[dict[str, object]] = []

    def fake_write_snapshot(payload):
        written.append(payload)
        if payload["running"]:
            for handler in handlers:
                handler()

    async def fake_to_thread(func, *args, **kwargs):
        return func(*args, **kwargs)

    monkeypatch.setattr(worker, "write_snapshot", fake_write_snapshot)
    monkeypatch.setattr(worker.asyncio, "to_thread", fake_to_thread)

    await worker._run_worker()

    assert [item["running"] for item in written] == [True, False]
    assert written[0]["top_pairs"]["pairs"] == ["BTCUSDT", "ETHUSDT"]
    assert written[0]["status"]["ws_stream_limit"] == 1
    assert written[0]["prices"][0]["symbol"] == "BTCUSDT"


def test_worker_main_calls_asyncio_run(monkeypatch):
    called = {"value": False}

    def fake_run(coro):
        called["value"] = True
        coro.close()

    monkeypatch.setattr(worker.asyncio, "run", fake_run)
    worker.main()
    assert called["value"] is True
