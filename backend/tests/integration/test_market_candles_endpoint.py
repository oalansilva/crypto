from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
import httpx
import pandas as pd
import pytest

from app import api as app_api
from utils.market_data_mocks import block_external_network


@pytest.fixture(autouse=True)
def isolate_market_candles_storage(monkeypatch):
    class _DisabledOhlcvRepository:
        enabled = False

    with app_api._CANDLES_CACHE_LOCK:
        app_api._CANDLES_CACHE.clear()
    monkeypatch.setattr(app_api, "_OHLCV_REPO", _DisabledOhlcvRepository())
    yield
    with app_api._CANDLES_CACHE_LOCK:
        app_api._CANDLES_CACHE.clear()


def _build_df(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], utc=True)
    df = df.sort_values("timestamp_utc")
    df["time"] = df["timestamp_utc"]
    df["timestamp"] = (df["timestamp_utc"].astype("int64") // 1_000_000).astype("int64")
    return df.set_index("timestamp_utc", drop=False)


@dataclass
class _FakeProvider:
    source: str
    df: pd.DataFrame

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        since_str: str | None = None,
        until_str: str | None = None,
        limit: int | None = None,
    ) -> pd.DataFrame:
        out = self.df.copy()
        if isinstance(limit, int) and limit > 0:
            out = out.tail(limit)
        return out


def _build_app() -> FastAPI:
    test_app = FastAPI()
    test_app.include_router(app_api.router)
    return test_app


async def _get(path: str):
    app = _build_app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.get(path)


async def test_market_candles_crypto_returns_ordered_and_limited(monkeypatch):
    block_external_network(monkeypatch)

    crypto_df = _build_df(
        [
            {
                "timestamp_utc": "2025-01-01T02:00:00Z",
                "open": 101,
                "high": 103,
                "low": 100,
                "close": 102,
                "volume": 10,
            },
            {
                "timestamp_utc": "2025-01-01T00:00:00Z",
                "open": 99,
                "high": 101,
                "low": 98,
                "close": 100,
                "volume": 8,
            },
            {
                "timestamp_utc": "2025-01-01T01:00:00Z",
                "open": 100,
                "high": 102,
                "low": 99,
                "close": 101,
                "volume": 9,
            },
        ]
    )
    fake_ccxt = _FakeProvider(source="ccxt", df=crypto_df)

    def _fake_get_market_data_provider(data_source: str | None):
        assert data_source == "ccxt"
        return fake_ccxt

    monkeypatch.setattr(app_api, "get_market_data_provider", _fake_get_market_data_provider)

    response = await _get("/api/market/candles?symbol=BTC/USDT&timeframe=1h&limit=2")
    assert response.status_code == 200, response.text
    payload = response.json()

    assert payload["asset_type"] == "crypto"
    assert payload["data_source"] == "ccxt"
    assert payload["count"] == 2
    assert [c["timestamp_utc"] for c in payload["candles"]] == [
        "2025-01-01T01:00:00+00:00",
        "2025-01-01T02:00:00+00:00",
    ]


async def test_market_candles_refreshes_when_persisted_crypto_candles_are_stale(monkeypatch):
    block_external_network(monkeypatch)

    stale_candles = [
        {
            "timestamp_utc": "2026-04-24T00:00:00+00:00",
            "open": 0.2499,
            "high": 0.2519,
            "low": 0.2499,
            "close": 0.2516,
            "volume": 8827222.3,
            "source": "ccxt",
        }
    ]

    class _StaleOhlcvRepository:
        enabled = True

        def read_recent_candles(self, *_args, **_kwargs):
            return stale_candles

        def write_candles(self, *_args, **_kwargs):
            return 1

    fresh_df = _build_df(
        [
            {
                "timestamp_utc": "2026-05-02T00:00:00Z",
                "open": 0.2483,
                "high": 0.251,
                "low": 0.247,
                "close": 0.2503,
                "volume": 10,
            }
        ]
    )
    fake_ccxt = _FakeProvider(source="ccxt", df=fresh_df)

    monkeypatch.setattr(app_api, "_OHLCV_REPO", _StaleOhlcvRepository())
    monkeypatch.setattr(app_api, "get_market_data_provider", lambda *_args: fake_ccxt)

    response = await _get("/api/market/candles?symbol=ADA/USDT&timeframe=1d&limit=200")
    assert response.status_code == 200, response.text
    payload = response.json()

    assert payload["data_source"] == "ccxt"
    assert payload["candles"][-1]["timestamp_utc"] == "2026-05-02T00:00:00+00:00"


async def test_market_candles_uses_fresh_persisted_crypto_candles(monkeypatch):
    block_external_network(monkeypatch)

    now = datetime.now(timezone.utc).replace(microsecond=0)
    persisted = [
        {
            "timestamp_utc": (now - timedelta(hours=1)).isoformat(),
            "open": 1,
            "high": 2,
            "low": 1,
            "close": 2,
            "volume": 10,
            "source": "ccxt",
        }
    ]

    class _FreshOhlcvRepository:
        enabled = True

        def read_recent_candles(self, *_args, **_kwargs):
            return persisted

    def _fail_get_market_data_provider(data_source: str | None):
        raise AssertionError(f"Unexpected provider selection: {data_source}")

    monkeypatch.setattr(app_api, "_OHLCV_REPO", _FreshOhlcvRepository())
    monkeypatch.setattr(app_api, "get_market_data_provider", _fail_get_market_data_provider)

    response = await _get("/api/market/candles?symbol=ADA/USDT&timeframe=1d&limit=200")
    assert response.status_code == 200, response.text
    payload = response.json()

    assert payload["data_source"] == "timescaledb"
    assert payload["candles"] == persisted


async def test_market_candles_stock_intraday_rejected(monkeypatch):
    block_external_network(monkeypatch)

    def _fail_get_market_data_provider(data_source: str | None):
        raise AssertionError(f"Unexpected provider selection: {data_source}")

    monkeypatch.setattr(app_api, "get_market_data_provider", _fail_get_market_data_provider)

    response = await _get("/api/market/candles?symbol=NVDA&timeframe=15m&limit=100")
    assert response.status_code == 400, response.text
    assert "MVP supports only crypto pairs" in response.json()["detail"]


async def test_market_candles_stock_four_hour_rejected(monkeypatch):
    block_external_network(monkeypatch)

    def _fail_get_market_data_provider(data_source: str | None):
        raise AssertionError(f"Unexpected provider selection: {data_source}")

    monkeypatch.setattr(app_api, "get_market_data_provider", _fail_get_market_data_provider)

    response = await _get("/api/market/candles?symbol=NVDA&timeframe=4h&limit=100")
    assert response.status_code == 400, response.text
    assert "MVP supports only crypto pairs" in response.json()["detail"]


async def test_market_candles_stock_daily_rejected(monkeypatch):
    block_external_network(monkeypatch)

    def _fail_get_market_data_provider(data_source: str | None):
        raise AssertionError(f"Unexpected provider selection: {data_source}")

    monkeypatch.setattr(app_api, "get_market_data_provider", _fail_get_market_data_provider)

    response = await _get("/api/market/candles?symbol=NVDA&timeframe=1d&limit=100")
    assert response.status_code == 400, response.text
    assert "MVP supports only crypto pairs" in response.json()["detail"]


async def test_market_candles_invalid_timeframe_returns_400(monkeypatch):
    block_external_network(monkeypatch)

    response = await _get("/api/market/candles?symbol=NVDA&timeframe=5m&limit=100")
    assert response.status_code == 400
    assert "MVP supports only crypto pairs" in response.json()["detail"]
