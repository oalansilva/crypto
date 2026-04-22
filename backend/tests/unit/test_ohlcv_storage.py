from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pandas as pd
import pytest

import app.services.ohlcv_storage as ohlcv_storage
from app.services.ohlcv_storage import (
    CCXT_SOURCE,
    STOOQ_SOURCE,
    MarketOhlcvRepository,
    OhlcvIngestionService,
)


class _ScalarResult:
    def __init__(self, value):
        self._value = value

    def scalar(self):
        return self._value


class _RowsResult:
    def __init__(self, rows):
        self._rows = rows

    def mappings(self):
        return self

    def all(self):
        return self._rows


class _FakeConnection:
    def __init__(self, *, latest: datetime | None, rows, count: int = 0, explain_plan=None):
        self._latest = latest
        self._rows = rows
        self._count = count
        self._explain_plan = explain_plan
        self.selects = []
        self.inserts = []
        self.others = []

    def execute(self, statement, params=None):
        sql = str(statement)
        if "SELECT MAX(candle_time)" in sql:
            return (self._latest,) if self._latest else None
        if "EXPLAIN" in sql:
            return _ScalarResult(self._explain_plan)
        if "COUNT(" in sql and "market_ohlcv" in sql:
            self.selects.append((sql, params))
            return _ScalarResult(self._count)
        if "SELECT candle_time" in sql and "FROM market_ohlcv" in sql:
            return _RowsResult(self._rows)
        if "INSERT INTO market_ohlcv" in sql:
            self.inserts.append(params)
            return _ScalarResult(None)
        self.others.append(sql)
        return _ScalarResult(None)


class _FakeBegin:
    def __init__(self, conn):
        self.conn = conn

    def __enter__(self):
        return self.conn

    def __exit__(self, exc_type, exc, tb):
        return False


class _FakeEngine:
    def __init__(self, conn):
        self.conn = conn

    def begin(self):
        return _FakeBegin(self.conn)


def _new_service(monkeypatch):
    monkeypatch.setattr(ohlcv_storage.OhlcvIngestionService, "_instance", None)
    return OhlcvIngestionService()


def test_ohlcv_repository_disabled_branches_short_circuit(monkeypatch):
    monkeypatch.setattr(ohlcv_storage, "DB_URL", "sqlite:///:memory:")
    repo = MarketOhlcvRepository()
    assert repo.enabled is False
    assert repo.get_latest_candle_time("BTC/USDT", "1m") is None
    assert repo.read_recent_candles("BTC/USDT", "1m", 10) == []
    assert repo.write_candles("BTC/USDT", "1m", "ccxt", None) == 0


def test_ohlcv_repository_reads_and_inserts_with_fake_connection(monkeypatch):
    latest = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    rows = [
        {
            "candle_time": latest + timedelta(minutes=1),
            "open": 2.0,
            "high": 2.2,
            "low": 1.8,
            "close": 2.1,
            "volume": 10.0,
            "source": "ccxt",
        },
        {
            "candle_time": latest,
            "open": 1.0,
            "high": 1.2,
            "low": 0.8,
            "close": 1.1,
            "volume": 9.0,
            "source": "ccxt",
        },
    ]
    conn = _FakeConnection(latest=latest, rows=rows, count=1, explain_plan='[{"Plan": {}}]')
    monkeypatch.setattr(ohlcv_storage, "DB_URL", "postgresql://unit")
    monkeypatch.setattr(ohlcv_storage, "engine", _FakeEngine(conn))
    monkeypatch.setattr(ohlcv_storage, "_INDEX_ASSERTION_ENABLED", True)

    repo = MarketOhlcvRepository()
    assert repo.enabled is True

    assert repo.get_latest_candle_time("BTC/USDT", "1m") == latest

    candles = repo.read_recent_candles("BTC/USDT", "1m", 2)
    assert len(candles) == 2
    assert candles[0]["timestamp_utc"] == latest.isoformat()
    assert candles[1]["timestamp_utc"] == (latest + timedelta(minutes=1)).isoformat()

    frame = pd.DataFrame(
        {
            "open": [1.0, 1.0, 2.0],
            "high": [1.1, 1.1, 2.1],
            "low": [0.9, 0.9, 1.9],
            "close": [1.0, 1.0, 2.0],
            "volume": [10, 10, 11],
        }
    )
    frame = frame.set_index(
        pd.to_datetime([latest, latest, latest + timedelta(minutes=1)])
    )
    frame.index.name = "timestamp_utc"

    assert repo.write_candles("btc/usdt", "1m", "ccxt", frame) == 2
    assert len(conn.inserts) == 1
    assert len(conn.inserts[0]) == 2


def test_ohlcv_repository_write_rejects_missing_timestamp():
    repo = MarketOhlcvRepository()
    with pytest.raises(ValueError, match="timestamp_utc"):
        repo.write_candles(
            "BTC/USDT",
            "1m",
            "ccxt",
            pd.DataFrame({"open": [1.0], "high": [2.0], "low": [0.5], "close": [1.8]}),
        )


def test_ohlcv_plan_parser_helpers_handle_dict_list_and_json_string():
    assert MarketOhlcvRepository._read_plan_uses_timeframe_index(
        [
            {
                "Plan": {
                    "Node Type": "Index Scan",
                    "Index Name": "idx_market_ohlcv_symbol_timeframe_time",
                }
            }
        ]
    )
    assert not MarketOhlcvRepository._read_plan_uses_timeframe_index(
        [{"Plan": {"Node Type": "Seq Scan", "Index Name": "idx_other"}}]
    )
    assert MarketOhlcvRepository._read_plan_uses_timeframe_index(
        '[{"Plan": {"Node Type": "Index Scan", "Index Name": "idx_market_ohlcv_symbol_timeframe_time"}}]'
    )
    assert not MarketOhlcvRepository._read_plan_uses_timeframe_index("not-json")


def test_ohlcv_ingestion_service_resolve_symbols_and_timeframes(monkeypatch):
    monkeypatch.setenv("MARKET_OHLCV_SYMBOLS", "btcusdt,ethusdt, ,")
    monkeypatch.setenv("MARKET_OHLCV_TIMEFRAMES", "1m,15m,99m,1m")
    service = _new_service(monkeypatch)
    assert service._symbols == ["BTCUSDT", "ETHUSDT"]
    assert service._timeframes == ["1m", "15m"]

    monkeypatch.delenv("MARKET_OHLCV_SYMBOLS", raising=False)
    monkeypatch.delenv("MARKET_OHLCV_TIMEFRAMES", raising=False)
    service = _new_service(monkeypatch)
    assert service._symbols == [
        "BTC/USDT",
        "ETH/USDT",
        "SOL/USDT",
        "BNB/USDT",
        "XRP/USDT",
    ]
    assert service._timeframes == sorted(
        ["1m", "5m", "1h", "4h", "1d"], reverse=False
    )


def test_ohlcv_ingestion_service_helpers_and_fallbacks(monkeypatch):
    service = _new_service(monkeypatch)
    assert service._is_enabled() is True
    assert service._ingestion_lag_warning_threshold("1m") >= 60

    monkeypatch.setattr(ohlcv_storage, "resolve_data_source_for_symbol", lambda _: STOOQ_SOURCE)
    assert service._resolve_source("AAPL/USDT", "1d") == STOOQ_SOURCE
    assert service._resolve_source("AAPL/USDT", "5m") == CCXT_SOURCE

    calls = []

    class _Provider:
        def fetch_ohlcv(self, symbol, timeframe, **kwargs):
            calls.append(kwargs)
            if "full_history_if_empty" in kwargs:
                raise TypeError("legacy provider")
            return pd.DataFrame(
                {
                    "timestamp_utc": [datetime(2026, 1, 1, tzinfo=timezone.utc)],
                    "open": [1.0],
                    "high": [1.1],
                    "low": [0.9],
                    "close": [1.0],
                }
            )

    monkeypatch.setattr(ohlcv_storage, "get_market_data_provider", lambda *_: _Provider())
    payload = service._fetch_provider_df("BTC/USDT", "1m", CCXT_SOURCE, datetime(2026, 1, 1, tzinfo=timezone.utc))
    assert not payload.empty
    assert len(calls) == 2
    assert "full_history_if_empty" in calls[0]
    assert "full_history_if_empty" not in calls[1]


def test_ohlcv_ingestion_lag_threshold_reads_env_or_defaults(monkeypatch):
    service = _new_service(monkeypatch)
    assert service._ingestion_lag_warning_threshold("1m") >= 60

    monkeypatch.setenv("MARKET_OHLCV_MAX_LAG_SECONDS_1M", "invalid")
    assert service._ingestion_lag_warning_threshold("1m") >= 60

    monkeypatch.setenv("MARKET_OHLCV_MAX_LAG_SECONDS_1M", "180")
    assert service._ingestion_lag_warning_threshold("1m") == 180


def test_ohlcv_ingestion_symbol_skips_stooq_non_1d_and_runs_loop(monkeypatch):
    service = _new_service(monkeypatch)
    service._resolve_source = lambda _symbol, _timeframe: STOOQ_SOURCE

    def _should_not_be_called(*_args, **_kwargs):
        raise AssertionError("fetch path should not execute for stooq non-1d timeframe")

    service._fetch_provider_df = _should_not_be_called
    service._repo._enabled = True
    service._timeframes = ["1m"]
    service._symbols = ["AAPL"]

    ingested = []
    original_stop = service._stop_event.is_set

    def _ingest(symbol, timeframe):
        ingested.append((symbol, timeframe))
        service._stop_event.set()

    monkeypatch.setattr(service, "_ingest_symbol", _ingest)
    service._run_loop()
    assert ingested == [("AAPL", "1m")]
    assert service._stop_event.is_set() is True
    assert original_stop() is False
