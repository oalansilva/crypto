from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


@dataclass(frozen=True)
class TradingViewFixture:
    symbol: str
    timeframe: str
    filename: str


def _fixtures_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "fixtures" / "tradingview"


def _load_reference_df(filename: str) -> pd.DataFrame:
    path = _fixtures_dir() / filename
    df = pd.read_csv(path)
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], utc=True)
    return df.sort_values("timestamp_utc").reset_index(drop=True)


def _resolve_timeframe_delta(timeframe: str) -> pd.Timedelta:
    mapping = {
        "1m": pd.Timedelta(minutes=1),
        "5m": pd.Timedelta(minutes=5),
        "15m": pd.Timedelta(minutes=15),
        "1h": pd.Timedelta(hours=1),
        "4h": pd.Timedelta(hours=4),
        "1d": pd.Timedelta(days=1),
    }
    return mapping[timeframe]


def _assert_timeframe_regular_and_utc(df: pd.DataFrame, timeframe: str, *, require_no_gaps: bool = True) -> None:
    assert df["timestamp_utc"].dt.tz is not None
    deltas = df["timestamp_utc"].diff().dropna()
    if deltas.empty:
        return

    expected = _resolve_timeframe_delta(timeframe)
    assert deltas.min() >= expected

    if require_no_gaps:
        assert set(deltas.unique()) == {expected}


def _compute_fixture(service, df: pd.DataFrame, symbol: str, timeframe: str) -> pd.DataFrame:
    input_df = df[["timestamp_utc", "open", "high", "low", "close", "volume"]].rename(
        columns={"timestamp_utc": "ts"}
    )
    return service._compute_indicators(input_df, timeframe=timeframe, symbol=symbol)


def _assert_matching(
    computed: pd.Series,
    expected: pd.Series,
    indicator: str,
    rtol: float,
    atol: float,
) -> None:
    expected_values = expected.to_numpy(dtype=float)
    computed_values = computed.to_numpy(dtype=float)

    valid_mask = ~np.isnan(expected_values)
    if not np.any(valid_mask):
        return

    np.testing.assert_allclose(
        computed_values[valid_mask],
        expected_values[valid_mask],
        rtol=rtol,
        atol=atol,
        err_msg=f"{indicator} diverges beyond tolerance from TradingView fixture",
    )


@pytest.mark.parametrize(
    "fixture",
    [
        TradingViewFixture("BTCUSDT", "1d", "btcusdt_1d_tradingview_reference.csv"),
        TradingViewFixture("BTCUSDT", "1h", "btcusdt_1h_tradingview_reference.csv"),
        TradingViewFixture("NVDA", "1d", "nvda_1d_tradingview_reference.csv"),
        TradingViewFixture("NVDA", "1h", "nvda_1h_tradingview_reference.csv"),
    ],
)
def test_market_indicator_tradingview_fixture_parity_with_tolerance(fixture: TradingViewFixture) -> None:
    pytest.importorskip("talib", reason="TA-Lib required for indicator parity tests")

    from app.services.market_indicator_service import MarketIndicatorService

    service = MarketIndicatorService()
    df = _load_reference_df(fixture.filename)

    expected_cols = {
        "timestamp_utc",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "ema_9",
        "ema_21",
        "sma_20",
        "sma_50",
        "rsi_14",
        "macd_line",
        "macd_signal",
        "macd_histogram",
    }
    assert expected_cols.issubset(df.columns)
    assert df["timestamp_utc"].is_monotonic_increasing

    if df.shape[0] < 70:
        pytest.skip("fixture short for 50-period SMA validation")

    _assert_timeframe_regular_and_utc(df, fixture.timeframe)

    computed = _compute_fixture(service, df, fixture.symbol, fixture.timeframe)

    tolerance_by_indicator = {
        "ema_9": (1e-4, 1e-3),
        "ema_21": (1e-4, 1e-3),
        "sma_20": (1e-4, 1e-3),
        "sma_50": (1e-4, 1e-3),
        "rsi_14": (1e-4, 1e-4),
        "macd_line": (1e-4, 1e-3),
        "macd_signal": (1e-4, 1e-3),
        "macd_histogram": (1e-4, 1e-3),
    }

    for column, (rtol, atol) in tolerance_by_indicator.items():
        _assert_matching(computed[column], df[column], column, rtol=rtol, atol=atol)

    warmup_mask = df["ema_9"].isna() & df["sma_20"].isna() & df["rsi_14"].isna()
    assert warmup_mask.any()
