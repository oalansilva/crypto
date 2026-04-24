from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

import pandas as pd
import pytest

from app.services.market_indicator_service import MarketIndicatorService

PIVOT_COLUMNS = (
    "pivot_point",
    "support_1",
    "support_2",
    "support_3",
    "resistance_1",
    "resistance_2",
    "resistance_3",
)


def _ohlcv(rows: list[tuple[str, float, float, float]]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ts": pd.date_range("2026-04-24T00:00:00Z", periods=len(rows), freq="h"),
            "open": [close for _label, _high, _low, close in rows],
            "high": [high for _label, high, _low, _close in rows],
            "low": [low for _label, _high, low, _close in rows],
            "close": [close for _label, _high, _low, close in rows],
            "volume": [1000.0 + idx for idx in range(len(rows))],
        }
    )


def _classic_pivots(high: float, low: float, close: float) -> dict[str, float]:
    pivot = (high + low + close) / 3
    return {
        "pivot_point": pivot,
        "support_1": (2 * pivot) - high,
        "support_2": pivot - (high - low),
        "support_3": low - (2 * (high - pivot)),
        "resistance_1": (2 * pivot) - low,
        "resistance_2": pivot + (high - low),
        "resistance_3": high + (2 * (pivot - low)),
    }


def test_compute_indicators_calculates_classic_pivot_levels_from_previous_candle() -> None:
    rows = _ohlcv(
        [
            ("previous", 110.0, 90.0, 100.0),
            ("current", 115.0, 95.0, 105.0),
            ("next", 120.0, 100.0, 110.0),
        ]
    )

    output = MarketIndicatorService()._compute_indicators(rows, timeframe="1h", symbol="btcusdt")

    expected = _classic_pivots(high=110.0, low=90.0, close=100.0)
    for column, value in expected.items():
        assert output.loc[1, column] == pytest.approx(value)


def test_compute_indicators_keeps_first_row_pivot_levels_null() -> None:
    rows = _ohlcv(
        [
            ("first", 110.0, 90.0, 100.0),
            ("second", 115.0, 95.0, 105.0),
        ]
    )

    output = MarketIndicatorService()._compute_indicators(rows, timeframe="1h", symbol="btcusdt")

    for column in PIVOT_COLUMNS:
        assert math.isnan(output.loc[0, column])


@pytest.mark.parametrize("timeframe", ["1m", "5m", "15m", "1h", "4h", "1d"])
def test_compute_indicators_includes_pivot_levels_for_each_timeframe(timeframe: str) -> None:
    rows = _ohlcv(
        [
            ("first", 110.0, 90.0, 100.0),
            ("second", 115.0, 95.0, 105.0),
            ("third", 120.0, 100.0, 110.0),
        ]
    )

    output = MarketIndicatorService()._compute_indicators(
        rows, timeframe=timeframe, symbol="ethusdt"
    )

    assert len(output) == len(rows)
    assert output["timeframe"].tolist() == [timeframe] * len(rows)
    assert output["symbol"].tolist() == ["ETHUSDT"] * len(rows)
    pivot_columns = list(PIVOT_COLUMNS)
    assert list(output[pivot_columns].columns) == pivot_columns
    assert output.loc[1:, pivot_columns].notna().all().all()


def test_read_ohlcv_incremental_includes_previous_candle_for_pivot_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.services import market_indicator_service as target

    class FakeConn:
        def __init__(self) -> None:
            self.statement = ""
            self.params: dict[str, Any] | None = None

        def execute(self, statement, params=None):
            self.statement = str(statement)
            self.params = params
            return self

        def mappings(self):
            return self

        def all(self):
            return [
                {
                    "candle_time": datetime(2026, 4, 24, 0, 0, tzinfo=timezone.utc),
                    "open": 100,
                    "high": 110,
                    "low": 90,
                    "close": 100,
                    "volume": 1000,
                },
                {
                    "candle_time": datetime(2026, 4, 24, 1, 0, tzinfo=timezone.utc),
                    "open": 101,
                    "high": 115,
                    "low": 95,
                    "close": 105,
                    "volume": 1001,
                },
            ]

    class FakeBegin:
        def __init__(self, conn: FakeConn) -> None:
            self.conn = conn

        def __enter__(self) -> FakeConn:
            return self.conn

        def __exit__(self, exc_type, exc, tb) -> None:
            return None

    class FakeEngine:
        def __init__(self) -> None:
            self.conn = FakeConn()

        def begin(self) -> FakeBegin:
            return FakeBegin(self.conn)

    fake_engine = FakeEngine()
    monkeypatch.setattr(target, "engine", fake_engine)

    since = datetime(2026, 4, 24, 1, 0, tzinfo=timezone.utc)
    output = MarketIndicatorService()._read_ohlcv("BTCUSDT", "1h", since)

    assert "previous_candle" in fake_engine.conn.statement
    assert "candle_time < :since" in fake_engine.conn.statement
    assert fake_engine.conn.params == {
        "symbol": "BTCUSDT",
        "timeframe": "1h",
        "since": since,
    }
    assert output["ts"].dt.tz is not None
    assert output.shape[0] == 2


def test_get_time_series_returns_pivot_level_columns(monkeypatch: pytest.MonkeyPatch) -> None:
    expected_row = {
        "symbol": "BTCUSDT",
        "timeframe": "1h",
        "ts": datetime(2026, 4, 24, 1, 0, tzinfo=timezone.utc),
        "pivot_point": 100.0,
        "support_1": 90.0,
        "support_2": 80.0,
        "support_3": 70.0,
        "resistance_1": 110.0,
        "resistance_2": 120.0,
        "resistance_3": 130.0,
    }

    monkeypatch.setattr(
        MarketIndicatorService,
        "_fetch_latest_rows",
        lambda self, symbol, timeframe, limit: [expected_row],
    )

    rows = MarketIndicatorService().get_time_series("btcusdt", "1h", 1)

    assert rows == [expected_row]
    for column in PIVOT_COLUMNS:
        assert column in rows[0]
