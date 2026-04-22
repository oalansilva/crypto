from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pandas as pd

import app.api as api
from app.services.asset_classification import classify_asset_type


def _build_api_app() -> FastAPI:
    app = FastAPI()
    app.include_router(api.router)
    return app


class _Provider:
    def __init__(self, response: pd.DataFrame, *, keep_full_history_kwarg: bool = True):
        self.response = response
        self.calls = []
        self._keep_full_history_kwarg = keep_full_history_kwarg

    def fetch_ohlcv(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        if self._keep_full_history_kwarg and "full_history_if_empty" in kwargs:
            return self.response
        if not self._keep_full_history_kwarg and "full_history_if_empty" in kwargs:
            raise TypeError("full_history_if_empty unsupported")
        return self.response


def _ohlcv_frame(limit: int = 2, include_volume: bool = True) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "timestamp_utc": pd.date_range("2026-01-01", periods=limit, tz=timezone.utc),
            "timestamp": [1000 + i for i in range(limit)],
            "open": [1.0 + i for i in range(limit)],
            "high": [1.2 + i for i in range(limit)],
            "low": [0.8 + i for i in range(limit)],
            "close": [1.1 + i for i in range(limit)],
            **({"volume": [10 + i for i in range(limit)]} if include_volume else {}),
        }
    )


def test_api_health_presets_metadata_and_indicator_schema(monkeypatch):
    monkeypatch.setattr(
        api,
        "get_presets",
        lambda: [
            {
                "id": "base",
                "name": "Base",
                "description": "Default preset",
                "config": {
                    "mode": "run",
                    "exchange": "binance",
                    "symbol": "BTC/USDT",
                    "timeframe": "1d",
                    "strategies": ["ema_rsi_volume"],
                },
            }
        ],
    )
    monkeypatch.setattr(
        api,
        "get_all_indicators_metadata",
        lambda: {"ta": ["ema"], "custom": []},
    )
    dyn_mod = __import__("app.schemas.dynamic_schema_generator", fromlist=["*"])
    monkeypatch.setattr(
        dyn_mod,
        "get_dynamic_indicator_schema",
        lambda name: {} if name == "missing" else {"name": name},
    )

    client = TestClient(_build_api_app())

    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    presets = client.get("/api/presets")
    assert presets.status_code == 200
    payload = presets.json()
    assert payload[0]["id"] == "base"

    strategies = client.get("/api/strategies/metadata")
    assert strategies.status_code == 200
    payload = strategies.json()
    assert payload["ta"] == ["ema"]
    assert len(payload["custom"]) == 3

    schema = client.get("/api/indicator/ema/schema")
    assert schema.status_code == 200
    assert schema.json()["name"] == "ema"

    missing = client.get("/api/indicator/missing/schema")
    assert missing.status_code == 404


def test_api_us_nasdaq100_symbols(monkeypatch, tmp_path):
    cfg = tmp_path / "nasdaq100.json"
    cfg.write_text('["aapl", "msft"]', encoding="utf-8")
    monkeypatch.setattr(api, "NASDAQ100_CONFIG_PATH", cfg)

    client = TestClient(_build_api_app())
    response = client.get("/api/markets/us/nasdaq100")
    assert response.status_code == 200
    data = response.json()
    assert data["symbols"] == ["AAPL", "MSFT"]
    assert data["count"] == 2

    cfg.write_text('["a", 2]', encoding="utf-8")
    bad_payload = client.get("/api/markets/us/nasdaq100")
    assert bad_payload.status_code == 500


def test_api_market_candles_crypto_and_stock_paths(monkeypatch):
    crypto_provider = _Provider(_ohlcv_frame())
    stooq_provider = _Provider(_ohlcv_frame(), keep_full_history_kwarg=False)
    yahoo_provider = _Provider(_ohlcv_frame(), keep_full_history_kwarg=False)

    def provider_factory(source):
        if source == api.CCXT_SOURCE:
            return crypto_provider
        return stooq_provider

    monkeypatch.setattr(api, "get_market_data_provider", provider_factory)

    yahoo_mod = __import__("app.api", fromlist=["YahooMarketDataProvider"])
    monkeypatch.setattr(
        yahoo_mod,
        "YahooMarketDataProvider",
        lambda: SimpleNamespace(fetch_ohlcv=yahoo_provider.fetch_ohlcv),
    )

    client = TestClient(_build_api_app())

    first = client.get(
        "/api/market/candles", params={"symbol": "BTC/USDT", "timeframe": "15m", "limit": 2}
    )
    assert first.status_code == 200
    assert first.json()["data_source"] == api.CCXT_SOURCE
    assert first.json()["count"] == 2
    assert len(crypto_provider.calls) == 1

    cached = client.get(
        "/api/market/candles", params={"symbol": "BTC/USDT", "timeframe": "15m", "limit": 2}
    )
    assert cached.status_code == 200
    assert len(crypto_provider.calls) == 1

    stock = client.get(
        "/api/market/candles", params={"symbol": "AAPL", "timeframe": "1d", "limit": 1}
    )
    assert stock.status_code == 200
    assert stock.json()["data_source"] == api.STOOQ_SOURCE
    assert stock.json()["asset_type"] == "stock"

    bad_timeframe = client.get(
        "/api/market/candles", params={"symbol": "AAPL", "timeframe": "1h", "limit": 1}
    )
    assert bad_timeframe.status_code == 400

    empty = client.get("/api/market/candles", params={"symbol": "", "timeframe": "1d", "limit": 1})
    assert empty.status_code == 400


def test_api_market_candles_without_timestamp_column_raises_via_api(monkeypatch):
    provider = _Provider(_ohlcv_frame().drop(columns=["timestamp_utc"]))
    monkeypatch.setattr(api, "get_market_data_provider", lambda *_: provider)

    client = TestClient(_build_api_app())
    response = client.get(
        "/api/market/candles", params={"symbol": "BTC/USDT", "timeframe": "1d", "limit": 1}
    )
    assert response.status_code == 400


def test_api_cache_read_and_write_helpers():
    api._CANDLES_CACHE.clear()
    payload = {"foo": "bar"}
    api._write_candles_cache("BTC/USDT", "1d", 10, payload)

    assert api._read_candles_cache("BTC/USDT", "1d", 10) == payload
    key = ("BTC/USDT", "1d", 10)
    api._CANDLES_CACHE[key]["expires_at"] = 0
    assert api._read_candles_cache("BTC/USDT", "1d", 10) is None


def test_api_internal_helpers():
    assert classify_asset_type("BTC/USDT") == "crypto"
    assert classify_asset_type("AAPL") == "stock"
    assert classify_asset_type("BTCUSDT", "cryptomoeda") == "crypto"
    assert classify_asset_type("BTC/USDT", "stock") == "stock"

    assert api._validate_market_timeframe("stock", "1d") == "1d"

    try:
        api._validate_market_timeframe("stock", "1h")
    except ValueError as exc:
        assert "Stocks currently support only timeframe='1d'." in str(exc)
    else:
        raise AssertionError("Expected ValueError")

    try:
        api._validate_market_timeframe("crypto", "2h")
    except ValueError as exc:
        assert "Unsupported timeframe '2h' for crypto" in str(exc)
    else:
        raise AssertionError("Expected ValueError")

    one_minute = api._ui_default_since_str("1m", limit=3_000)
    five_minute = api._ui_default_since_str("5m", limit=2_000)
    fifteen_minute = api._ui_default_since_str("15m", limit=10_000)
    one_hour = api._ui_default_since_str("1h", limit=50_000)
    four_hour = api._ui_default_since_str("4h", limit=200_000)

    assert (datetime.now(timezone.utc) - datetime.fromisoformat(one_minute)).days == 1
    assert (datetime.now(timezone.utc) - datetime.fromisoformat(five_minute)).days in {3, 4}
    assert (datetime.now(timezone.utc) - datetime.fromisoformat(fifteen_minute)).days == 30
    assert (datetime.now(timezone.utc) - datetime.fromisoformat(one_hour)).days >= 7
    assert (datetime.now(timezone.utc) - datetime.fromisoformat(four_hour)).days >= 30

    since = api._ui_default_since_str("1d", limit=60)
    since_dt = datetime.fromisoformat(since)
    now = datetime.now(timezone.utc)
    delta = now - since_dt
    assert delta.days >= 89

    assert api._normalize_candles_frame(None, 10) == []
    assert api._normalize_candles_frame(_ohlcv_frame(0), 10) == []

    idx_df = _ohlcv_frame(2).set_index("timestamp_utc")
    candles = api._normalize_candles_frame(idx_df, 1)
    assert len(candles) == 1

    bad = _ohlcv_frame(2).drop(columns=["timestamp_utc"])
    try:
        api._normalize_candles_frame(bad, 1)
    except ValueError as exc:
        assert "missing timestamp_utc" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_api_market_candles_metrics_route():
    client = TestClient(_build_api_app())
    response = client.get("/api/market/candles/metrics")
    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] in {"market_ohlcv", "disabled"}
    assert payload["metrics"]["ingest"]["rows_received"] >= 0
