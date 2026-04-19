from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import httpx
import pandas as pd
import pytest

from app.services.market_data_providers import (
    AlphaVantageMarketDataProvider,
    CCXT_SOURCE,
    CcxtMarketDataProvider,
    StooqEodProvider,
    STOOQ_SOURCE,
    YahooMarketDataProvider,
    get_market_data_provider,
    normalize_data_source,
    resolve_data_source_for_symbol,
    validate_data_source_timeframe,
)
import app.services.market_data_providers as providers


def _frame(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    if rows:
        df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], utc=True)
        df["time"] = df["timestamp_utc"]
        df["timestamp"] = (df["time"].astype("int64") // 1_000_000).astype("int64")
        df = df.sort_values("timestamp_utc")
        df = df.set_index("timestamp_utc", drop=False)
    return df


class _FakeResponse:
    def __init__(self, payload, status_code: int = 200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("bad", request=None, response=None)

    def json(self):
        return self._payload

    @property
    def text(self):
        return self._payload if isinstance(self._payload, str) else str(self._payload)


def test_source_resolution_and_provider_registry():
    assert normalize_data_source(None) == CCXT_SOURCE
    assert normalize_data_source("  CCXT  ") == CCXT_SOURCE
    assert normalize_data_source("default") == CCXT_SOURCE
    assert normalize_data_source("BINANCE") == CCXT_SOURCE
    assert normalize_data_source("stooq-eod") == STOOQ_SOURCE
    assert normalize_data_source("stooq") == STOOQ_SOURCE
    assert resolve_data_source_for_symbol("BTC/USDT") == CCXT_SOURCE
    assert resolve_data_source_for_symbol("AAPL") == STOOQ_SOURCE
    assert validate_data_source_timeframe(None, "1d") == CCXT_SOURCE
    assert validate_data_source_timeframe("stooq", "1d") == STOOQ_SOURCE

    providers._PROVIDERS.clear()
    assert get_market_data_provider("stooq").source == STOOQ_SOURCE
    assert get_market_data_provider("stooq") is get_market_data_provider("stooq")
    assert get_market_data_provider("ccxt").source == CCXT_SOURCE
    assert get_market_data_provider("ccxt") is get_market_data_provider(CCXT_SOURCE)

    with pytest.raises(ValueError, match="Unsupported data_source"):
        normalize_data_source("bad-provider")
    with pytest.raises(ValueError, match="data_source=stooq supports only"):
        validate_data_source_timeframe("stooq", "4h")


def test_ccxt_provider_fetch_delegates_to_loader():
    calls = []

    class _FakeLoader:
        def fetch_data(self, **kwargs):
            calls.append(kwargs)
            return pd.DataFrame({"timestamp": [1]})

    provider = CcxtMarketDataProvider(loader=_FakeLoader())
    out = provider.fetch_ohlcv(
        "BTC/USDT", "1h", since_str="2026-01-01", until_str="2026-01-02", limit=2
    )
    assert list(calls[0]) == [
        "symbol",
        "timeframe",
        "since_str",
        "until_str",
        "limit",
        "full_history_if_empty",
    ]
    assert not out.empty
    assert out.iloc[0]["timestamp"] == 1


def test_stooq_provider_helpers_and_parser(tmp_path):
    provider = StooqEodProvider(
        cache_dir=tmp_path, ttl_seconds=300, max_retries=2, retry_backoff_seconds=0.0
    )

    assert provider.map_symbol("AAPL") == "aapl.us"
    assert provider.map_symbol("BRK.B") == "brk-b.us"
    with pytest.raises(ValueError, match="must not be empty"):
        provider.map_symbol("  ")
    with pytest.raises(ValueError, match="Invalid US ticker"):
        provider.map_symbol("BRK/B")

    assert provider._normalize_timeframe("1d") == "1d"
    with pytest.raises(ValueError, match="only timeframe '1d'"):
        provider._normalize_timeframe("15m")

    parquet, meta = provider._cache_paths("aapl.us", "1d")
    assert str(parquet).endswith("aapl_us_1d.parquet")
    assert str(meta).endswith("aapl_us_1d.meta.json")

    assert provider._parse_datetime_utc(None) is None
    assert provider._parse_datetime_utc("  ") is None
    parsed = provider._parse_datetime_utc("2026-04-18")
    assert parsed.tzinfo is not None
    assert provider._parse_datetime_utc("nonsense") is None

    csv_payload = "Date,Open,High,Low,Close,Volume\n" "2026-04-18,100,110,90,105,1000\n"
    parsed = provider._parse_stooq_csv(csv_payload, provider_symbol="aapl.us")
    assert list(parsed.columns) == [
        "timestamp",
        "timestamp_utc",
        "time",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]
    assert parsed.index.name == "timestamp_utc"

    with pytest.raises(ValueError, match="missing 'open'"):
        provider._parse_stooq_csv("Date,foo\n1,2", provider_symbol="aapl.us")
    with pytest.raises(ValueError, match="Stooq returned no rows"):
        provider._parse_stooq_csv("Date,Open,High,Low,Close,Volume\n", provider_symbol="aapl.us")

    raw = provider._slice_dataframe(
        _frame(
            [
                {
                    "timestamp_utc": "2026-04-15",
                    "open": 1,
                    "high": 2,
                    "low": 1,
                    "close": 1.5,
                    "volume": 10,
                },
                {
                    "timestamp_utc": "2026-04-16",
                    "open": 1,
                    "high": 3,
                    "low": 1,
                    "close": 2.0,
                    "volume": 10,
                },
            ]
        ),
        since_str="2026-04-15T00:00:00Z",
        until_str="2026-04-15T23:59:59Z",
        limit=1,
    )
    assert len(raw) == 1
    assert raw.index[0].strftime("%Y-%m-%d") == "2026-04-15"

    standardized = provider._standardize_columns(
        pd.DataFrame(
            {
                "time": ["2026-04-18", "2026-04-19"],
                "open": [1, 2],
                "high": [2, 3],
                "low": [0.5, 1],
                "close": [1.5, 2.5],
            }
        )
    )
    assert standardized["volume"].iloc[0] == 0.0
    assert standardized["timestamp"].dtype.kind in ("i", "u")

    missing_meta = provider._cache_paths("aapl.us", "1d")[1]
    assert provider._is_cache_fresh(missing_meta) is False
    assert provider._load_cache(provider._cache_paths("aapl.us", "1d")[0]) is None


def test_stooq_provider_download_fetch_with_cache_and_fallback(tmp_path, monkeypatch):
    provider = StooqEodProvider(
        cache_dir=tmp_path, ttl_seconds=60, max_retries=1, retry_backoff_seconds=0.0
    )
    csv_payload = "Date,Open,High,Low,Close,Volume\n" "2026-04-18,100,110,90,105,1000\n"

    def success_get(*_args, **_kwargs):
        return _FakeResponse(csv_payload)

    monkeypatch.setattr(providers.httpx, "get", success_get)
    parsed = provider.fetch_ohlcv("AAPL", "1d", since_str="2026-04-10", limit=1)
    assert not parsed.empty
    assert len(parsed) == 1

    # Fresh cache should skip network
    called = {"count": 0}

    def fail_get(*_args, **_kwargs):
        called["count"] += 1
        raise AssertionError("download should not happen")

    monkeypatch.setattr(providers.httpx, "get", fail_get)
    warm = provider.fetch_ohlcv("AAPL", "1d", since_str="2026-04-10", limit=1)
    assert not warm.empty
    assert called["count"] == 0

    # Make cache stale and force stale fallback path
    stale = provider._cache_paths("aapl.us", "1d")[1]
    meta = json.loads(stale.read_text(encoding="utf-8"))
    meta["fetched_at"] = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    stale.write_text(json.dumps(meta), encoding="utf-8")
    with pytest.raises(ValueError, match="Stooq request failed"):
        provider.fetch_ohlcv("NEWONE", "1d")

    # stale cache should return data and avoid raising when stale data exists and refresh fails
    def no_data_get(*_args, **_kwargs):
        raise httpx.RequestError("offline")

    monkeypatch.setattr(providers.httpx, "get", no_data_get)
    fallback = provider.fetch_ohlcv("AAPL", "1d", limit=1)
    assert not fallback.empty


def test_stooq_download_retry_behaviour(tmp_path, monkeypatch):
    provider = StooqEodProvider(cache_dir=tmp_path, max_retries=2, retry_backoff_seconds=0.0)
    counters = {"calls": 0}

    def retry(*_args, **_kwargs):
        counters["calls"] += 1
        return _FakeResponse("   ", status_code=200)

    monkeypatch.setattr(providers.httpx, "get", retry)

    with pytest.raises(ValueError, match="Stooq request failed"):
        provider._download_csv("aapl.us")
    assert counters["calls"] == 2


def test_yahoo_provider_parse_and_fetch(monkeypatch):
    payload = {
        "chart": {
            "result": [
                {
                    "timestamp": [1710000000, 1710003600],
                    "indicators": {
                        "quote": [
                            {
                                "open": [100, 101],
                                "high": [110, 112],
                                "low": [99, 100],
                                "close": [108, 109],
                                "volume": [10, 20],
                            }
                        ]
                    },
                }
            ]
        }
    }

    def yahoo_ok(url, params, timeout):
        assert params["interval"] in {"60m", "15m"}
        if params["interval"] == "60m":
            assert params["range"] in {"1mo", "1y", "6mo"}
        else:
            assert params["interval"] == "15m"
            assert params["range"] == "1mo"
        return _FakeResponse(payload)

    monkeypatch.setattr(providers.httpx, "get", yahoo_ok)
    provider = YahooMarketDataProvider()
    assert provider._normalize_symbol("aapl") == "AAPL"
    with pytest.raises(ValueError, match="must not be empty"):
        provider._normalize_symbol("")
    with pytest.raises(ValueError, match="without '/'"):
        provider._normalize_symbol("AAPL/USD")

    assert provider._normalize_timeframe("15m") == "15m"
    assert provider._normalize_timeframe("1d") == "1d"
    with pytest.raises(ValueError, match="Unsupported Yahoo timeframe"):
        provider._normalize_timeframe("5m")

    assert provider._range_for_since("2026-01-01T00:00:00Z", "1y") == "6mo"

    parsed = provider.fetch_ohlcv("AAPL", "15m", limit=1)
    assert set(parsed.columns) >= {
        "timestamp",
        "timestamp_utc",
        "time",
        "open",
        "high",
        "low",
        "close",
        "volume",
    }
    assert len(parsed) == 1

    payload_4h = payload.copy()
    out_4h = provider.fetch_ohlcv("AAPL", "4h", limit=2)
    assert set(out_4h.columns) >= set(parsed.columns)

    with pytest.raises(ValueError, match="Unsupported Yahoo timeframe"):
        provider._normalize_timeframe("2h")

    def parse_empty(*_a, **_k):
        raise ValueError("Yahoo returned no valid OHLC rows for 'AAPL'.")

    monkeypatch.setattr(provider, "_parse_payload", parse_empty)
    with pytest.raises(ValueError, match="Yahoo returned no valid OHLC rows"):
        provider.fetch_ohlcv("AAPL", "15m")

    provider = YahooMarketDataProvider()

    monkeypatch.setattr(
        providers.httpx,
        "get",
        lambda *_a, **_k: _FakeResponse({"chart": {"error": {"description": "blocked"}}}),
    )
    with pytest.raises(ValueError, match="Yahoo request failed"):
        provider.fetch_ohlcv("AAPL", "1d")


def test_alphavantage_provider_paths(monkeypatch):
    with pytest.raises(ValueError, match="ALPHAVANTAGE_API_KEY"):
        AlphaVantageMarketDataProvider("")

    av = AlphaVantageMarketDataProvider("demo")
    with pytest.raises(ValueError, match="does not support"):
        av.fetch_ohlcv("AAPL", "2h")

    def daily_success(*_args, **_kwargs):
        return _FakeResponse(
            {
                "Time Series (Daily)": {
                    "2026-04-18": {
                        "1. open": "1",
                        "2. high": "2",
                        "3. low": "0.5",
                        "4. close": "1.5",
                        "6. volume": "10",
                    }
                }
            }
        )

    monkeypatch.setattr(providers.httpx, "get", daily_success)
    daily = av.fetch_ohlcv("AAPL", "1d", limit=1)
    assert not daily.empty

    def rate_limited(*_args, **_kwargs):
        return _FakeResponse({}, status_code=429)

    monkeypatch.setattr(providers.httpx, "get", rate_limited)
    with pytest.raises(RuntimeError, match="rate limited"):
        av.fetch_ohlcv("AAPL", "15m")

    payload_note = {
        "Note": "rate limit on demo",
    }

    def note_response(*_args, **_kwargs):
        return _FakeResponse(payload_note)

    monkeypatch.setattr(providers.httpx, "get", note_response)
    with pytest.raises(RuntimeError, match="rate limit on demo"):
        av.fetch_ohlcv("AAPL", "15m")

    payload_missing = {"Other": {}}

    def missing_series(*_args, **_kwargs):
        return _FakeResponse(payload_missing)

    monkeypatch.setattr(providers.httpx, "get", missing_series)
    with pytest.raises(RuntimeError, match="no intraday data"):
        av.fetch_ohlcv("AAPL", "15m")
