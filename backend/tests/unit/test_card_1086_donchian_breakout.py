"""Real Donchian entries, strict rejection and causal execution for #1086."""

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal, assert_series_equal

from app.services.combo_optimizer import extract_trades_from_signals
from app.strategies.combos.combo_strategy import ComboStrategy

BACKEND = Path(__file__).resolve().parents[2]
EXPORT = BACKEND / "config/combo_templates_export.json"
BASELINE = BACKEND / "tests/fixtures/card_1086/templates_before.json"
NAME = "donchian_volume_breakout"


def templates(path=EXPORT):
    return {row["name"]: row for row in json.loads(path.read_text(encoding="utf-8"))}


def strategy(row=None, *, length=20):
    td = deepcopy((row or templates()[NAME])["template_data"])
    if (row or templates()[NAME])["name"] == NAME:
        td["indicators"][0]["params"]["length"] = length
    return ComboStrategy(**td)


@pytest.fixture(params=("4h", "1h", "15min"))
def timeframe(request):
    return request.param


@pytest.fixture(params=("fast", "legacy"))
def execution_mode(request, monkeypatch):
    monkeypatch.setenv("COMBO_OPTIMIZER_LEGACY", "1" if request.param == "legacy" else "0")
    return request.param


def candles(timeframe, *, evaluated=20, close=101.0, high=102.0, volume=200.0):
    """Flat preceding channel, breakout, then exit above the unchanged stop."""
    df = pd.DataFrame(
        {"open": 99.5, "high": 100.0, "low": 99.0, "close": 99.5, "volume": 100.0},
        index=pd.date_range("2024-01-01", periods=evaluated + 5, freq=timeframe, tz="UTC"),
    )
    df.iloc[evaluated] = [99.5, high, 99.0, close, volume]
    # Execution at t+1 must be distinguishable from the decision close.
    df.iloc[evaluated + 1] = [101.25, 102.0, 99.5, 101.0, 100.0]
    # t+2 confirms close < dc_middle; t+3 executes the pending exit.
    df.iloc[evaluated + 2] = [100.0, 101.0, 99.0, 99.25, 100.0]
    return df


def backtest(df, strat=None):
    strat = strat or strategy()
    signals = strat.generate_signals(df.copy())
    trades = extract_trades_from_signals(signals, strat.stop_loss)
    return signals, trades


def assert_no_purchase(signals, trades, evaluated):
    # An empty closed-trade list alone can hide an erroneous open position.
    assert signals["signal"].iloc[evaluated + 1] == 0
    assert not signals["signal"].eq(1).any()
    assert trades == []


def test_valid_breakout_records_actual_long_at_next_open(timeframe, execution_mode):
    df = candles(timeframe)
    signals, trades = backtest(df)
    assert len(trades) == 1
    trade = trades[0]
    assert trade["type"] == "long"
    assert trade["entry_signal_type"] == "Comprar"
    assert trade["entry_time"] == df.index[21].isoformat()
    assert trade["entry_price"] == df["open"].iloc[21] == 101.25
    assert trade["exit_time"] == df.index[23].isoformat()
    assert trade["exit_reason"] == "signal"
    assert signals["signal_reason"].iloc[23] == "exit_logic"
    assert signals["signal"].iloc[20] == 0
    assert signals["signal"].iloc[21] == 1
    assert signals["vol_avg"].iloc[20] == 126.0
    assert signals["dc_upper"].shift(1).iloc[20] == 100.0


def test_new_breakout_does_not_buy_while_long_is_open(timeframe, execution_mode):
    df = candles(timeframe)
    df.iloc[22] = [101.0, 104.0, 99.0, 103.0, 400.0]
    strat = strategy()
    signals, trades = backtest(df, strat)
    assert strat._evaluate_logic_vectorized(signals, strat.entry_logic).iloc[22]
    assert signals["signal"].iloc[21] == 1
    assert signals["signal"].iloc[23] == 0
    assert signals["signal"].eq(1).sum() == 1
    assert len(trades) == 1
    assert trades[0]["entry_time"] == df.index[21].isoformat()


@pytest.mark.parametrize(
    "close,high,volume",
    (
        (100.0, 102.0, 200.0),
        (99.5, 100.0, 200.0),
        (99.5, 110.0, 200.0),
        (101.0, 102.0, 100.0),
        (101.0, 102.0, 0.0),
        (101.0, 102.0, 200.0),
    ),
    ids=(
        "equal-close",
        "lower-close",
        "intrabar-high-only",
        "low-volume",
        "zero-volume",
        "equal-volume-threshold",
    ),
)
def test_rejected_breakout_has_no_entry_signal_or_trade(
    timeframe, execution_mode, close, high, volume, request
):
    df = candles(timeframe, close=close, high=high, volume=volume)
    if request.node.callspec.id.endswith("equal-volume-threshold"):
        # Keep multiplier=1.2: mean([150]*18 + [120] + [180]) * 1.2 == 180.
        df.iloc[1:19, df.columns.get_loc("volume")] = 150.0
        df.iloc[19, df.columns.get_loc("volume")] = 120.0
        df.iloc[20, df.columns.get_loc("volume")] = 180.0
    signals, trades = backtest(df)
    if request.node.callspec.id.endswith("equal-volume-threshold"):
        assert signals["vol_avg"].iloc[20] == df["volume"].iloc[20]
    assert_no_purchase(signals, trades, 20)


@pytest.mark.parametrize("evaluated,length", ((19, 20), (20, 25), (25, 25)))
def test_history_and_first_eligible_candle(timeframe, execution_mode, evaluated, length):
    df = candles(timeframe, evaluated=evaluated)
    signals, trades = backtest(df, strategy(length=length))
    if evaluated < length:
        assert pd.isna(signals["dc_upper"].shift(1).iloc[evaluated])
        assert_no_purchase(signals, trades, evaluated)
    else:
        assert signals["signal"].iloc[: evaluated + 1].eq(0).all()
        assert signals["signal"].iloc[evaluated + 1] == 1
        assert len(trades) == 1
        assert trades[0]["entry_time"] == df.index[evaluated + 1].isoformat()


def test_incomplete_volume_history_rejects_entry(timeframe, execution_mode):
    df = candles(timeframe, evaluated=10)
    signals, trades = backtest(df, strategy(length=10))
    assert signals["dc_upper"].shift(1).iloc[10] == 100.0
    assert pd.isna(signals["vol_avg"].iloc[10])
    assert_no_purchase(signals, trades, 10)


def test_nondefault_period_uses_exactly_n_preceding_candles(timeframe, execution_mode):
    df = candles(timeframe, evaluated=35)
    df.iloc[10, df.columns.get_loc("high")] = 110.0  # Outside N=25's [11:36] at t=36.
    blocked, trades = backtest(df, strategy(length=25))
    assert_no_purchase(blocked, trades, 35)  # [10:35] still includes the older high.
    df.iloc[35] = [99.5, 100.0, 99.0, 99.5, 100.0]
    df.iloc[36] = [99.5, 102.0, 99.0, 101.0, 200.0]
    df.iloc[37] = [101.25, 102.0, 99.5, 101.0, 100.0]
    signals, trades = backtest(df, strategy(length=25))
    assert signals["dc_upper"].shift(1).iloc[36] == 100.0
    assert signals["signal"].iloc[37] == 1
    assert len(trades) == 1
    assert trades[0]["entry_time"] == df.index[37].isoformat()


def test_last_candle_decision_cannot_execute_without_next_candle(timeframe, execution_mode):
    df = candles(timeframe).iloc[:21]
    strat = strategy()
    signals, trades = backtest(df, strat)
    assert strat._evaluate_logic_vectorized(signals, strat.entry_logic).iloc[-1]
    assert not signals["signal"].eq(1).any()
    assert trades == []


def test_evaluated_high_does_not_change_its_entry(timeframe, execution_mode):
    df = candles(timeframe)
    altered = df.copy()
    altered.iloc[20, altered.columns.get_loc("high")] = 1000.0
    original, original_trades = backtest(df)
    changed, changed_trades = backtest(altered)
    assert original["dc_upper"].iloc[20] != changed["dc_upper"].iloc[20]
    assert original["dc_upper"].shift(1).iloc[20] == changed["dc_upper"].shift(1).iloc[20]
    assert_series_equal(original["signal"].iloc[:22], changed["signal"].iloc[:22])
    for trade in (original_trades[0], changed_trades[0]):
        assert trade["entry_time"] == df.index[21].isoformat()
        assert trade["entry_price"] == 101.25


def test_future_changes_preserve_decisions_and_next_open_execution(timeframe, execution_mode):
    df = candles(timeframe)
    future = df.copy()
    future.iloc[21:] = [100.0, 120.0, 99.0, 119.0, 800.0]
    future.iloc[21, future.columns.get_loc("open")] = df["open"].iloc[21]
    # Still close the real trade, without requiring identical exit or profit.
    future.iloc[23:] = [100.0, 101.0, 99.0, 99.25, 100.0]
    strat = strategy()
    original, trades = backtest(df, strat)
    changed, changed_trades = backtest(future)
    assert_series_equal(
        strat._evaluate_logic_vectorized(original, strat.entry_logic).iloc[:21],
        strat._evaluate_logic_vectorized(changed, strat.entry_logic).iloc[:21],
    )
    assert_frame_equal(
        original[["signal", "signal_reason"]].iloc[:22],
        changed[["signal", "signal_reason"]].iloc[:22],
    )
    assert trades[0]["entry_time"] == changed_trades[0]["entry_time"]
    assert trades[0]["entry_price"] == changed_trades[0]["entry_price"] == 101.25
    prefix, _ = backtest(df.iloc[:22])
    assert_frame_equal(
        original[["signal", "signal_reason"]].iloc[:22], prefix[["signal", "signal_reason"]]
    )


def test_export_changes_only_donchian_entry():
    old, current = templates(BASELINE), templates()
    expected = deepcopy(old[NAME])
    expected["template_data"]["entry_logic"] = "(close > dc_upper.shift(1)) & (volume > vol_avg)"
    assert current[NAME] == expected
    for name in old.keys() - {NAME}:
        assert current[name] == old[name]


def test_bands_and_exit_remain_equal_to_baseline(timeframe, execution_mode):
    df = candles(timeframe)
    old, new = strategy(templates(BASELINE)[NAME]), strategy()
    before, after = old.calculate_indicators(df.copy()), new.calculate_indicators(df.copy())
    assert_frame_equal(before, after)
    assert_series_equal(after["dc_upper"], df["high"].rolling(20).max(), check_names=False)
    assert_series_equal(after["dc_lower"], df["low"].rolling(20).min(), check_names=False)
    assert_series_equal(
        after["dc_middle"], (after["dc_upper"] + after["dc_lower"]) / 2, check_names=False
    )
    assert_series_equal(
        old._evaluate_logic_vectorized(before, old.exit_logic),
        new._evaluate_logic_vectorized(after, new.exit_logic),
    )


@pytest.mark.parametrize(
    "name", ("bollinger_squeeze", "long_ma_pullback_rsi_adx", "Bollinger_Breakout")
)
def test_other_templates_keep_indicators_and_signals(timeframe, execution_mode, name):
    rng = np.random.default_rng(1086)
    close = 100 + np.cumsum(rng.normal(0, 0.5, 450))
    df = pd.DataFrame(
        {
            "open": close,
            "high": close + 1,
            "low": close - 1,
            "close": close,
            "volume": rng.integers(100, 500, 450).astype(float),
        },
        index=pd.date_range("2024-01-01", periods=450, freq=timeframe, tz="UTC"),
    )
    old, new = strategy(templates(BASELINE)[name]), strategy(templates()[name])
    assert_frame_equal(old.calculate_indicators(df.copy()), new.calculate_indicators(df.copy()))
    assert_frame_equal(old.generate_signals(df.copy()), new.generate_signals(df.copy()))
