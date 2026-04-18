from __future__ import annotations

from dataclasses import dataclass

from fastapi import FastAPI
import httpx
import pandas as pd

from app import api as app_api
from utils.market_data_mocks import block_external_network


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


async def test_market_candles_stock_intraday_rejected(monkeypatch):
    block_external_network(monkeypatch)

    stock_df = _build_df(
        [
            {
                "timestamp_utc": "2025-02-03T14:30:00Z",
                "open": 210,
                "high": 212,
                "low": 209,
                "close": 211,
                "volume": 1000,
            },
            {
                "timestamp_utc": "2025-02-03T14:45:00Z",
                "open": 211,
                "high": 213,
                "low": 210,
                "close": 212,
                "volume": 1200,
            },
        ]
    )

    class _FakeYahooProvider:
        def fetch_ohlcv(
            self,
            symbol: str,
            timeframe: str,
            since_str: str | None = None,
            until_str: str | None = None,
            limit: int | None = None,
        ) -> pd.DataFrame:
            assert symbol == "NVDA"
            assert timeframe == "15m"
            out = stock_df.copy()
            if isinstance(limit, int) and limit > 0:
                out = out.tail(limit)
            return out

    monkeypatch.setattr(app_api, "YahooMarketDataProvider", _FakeYahooProvider)

    def _fail_get_market_data_provider(data_source: str | None):
        raise AssertionError(f"Unexpected provider selection: {data_source}")

    monkeypatch.setattr(app_api, "get_market_data_provider", _fail_get_market_data_provider)

    response = await _get("/api/market/candles?symbol=NVDA&timeframe=15m&limit=100")
    assert response.status_code == 400, response.text
    assert "Stocks currently support only timeframe='1d'" in response.json()["detail"]
    payload = response.json()


async def test_market_candles_stock_daily_uses_stooq_first(monkeypatch):
    block_external_network(monkeypatch)

    stock_df = _build_df(
        [
            {
                "timestamp_utc": "2025-02-01T00:00:00Z",
                "open": 200,
                "high": 205,
                "low": 198,
                "close": 203,
                "volume": 5000,
            },
        ]
    )
    fake_stooq = _FakeProvider(source="stooq", df=stock_df)

    def _fake_get_market_data_provider(data_source: str | None):
        assert data_source == "stooq"
        return fake_stooq

    monkeypatch.setattr(app_api, "get_market_data_provider", _fake_get_market_data_provider)

    class _FailYahooProvider:
        def fetch_ohlcv(self, *args, **kwargs):
            raise AssertionError("Yahoo fallback should not be called when stooq succeeds")

    monkeypatch.setattr(app_api, "YahooMarketDataProvider", _FailYahooProvider)

    response = await _get("/api/market/candles?symbol=NVDA&timeframe=1d&limit=100")
    assert response.status_code == 200, response.text
    payload = response.json()


async def test_market_candles_invalid_timeframe_returns_400(monkeypatch):
    block_external_network(monkeypatch)

    response = await _get("/api/market/candles?symbol=NVDA&timeframe=5m&limit=100")
    assert response.status_code == 400
    assert (
        "Unsupported timeframe" in response.json()["detail"]
        or "Stocks currently support only timeframe='1d'" in response.json()["detail"]
    )
