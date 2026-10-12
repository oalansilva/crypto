"""Smoke backtests for card #1074 templates and VWAP indicators."""

from __future__ import annotations

import numpy as np
import pandas as pd

import json
from pathlib import Path

from app.strategies.combos.combo_strategy import ComboStrategy

_EXPORT = Path(__file__).resolve().parents[2] / "config" / "combo_templates_export.json"


def _template_bundle(name: str) -> dict:
    data = json.loads(_EXPORT.read_text(encoding="utf-8"))
    row = next(item for item in data if item["name"] == name)
    td = row["template_data"]
    return {
        "indicators": td["indicators"],
        "entry_logic": td["entry_logic"],
        "exit_logic": td["exit_logic"],
        "stop_loss": td.get("stop_loss", 0.02),
    }


def _strategy_from_export(name: str) -> ComboStrategy:
    return ComboStrategy(**_template_bundle(name))


def _synthetic_ohlcv(rows: int = 400, freq: str = "4h") -> pd.DataFrame:
    idx = pd.date_range("2024-01-01", periods=rows, freq=freq, tz="UTC")
    close = 100 + np.cumsum(np.random.default_rng(42).normal(0, 0.5, rows))
    high = close + 1.0
    low = close - 1.0
    open_ = close + np.random.default_rng(1).normal(0, 0.2, rows)
    vol = np.random.default_rng(7).integers(1000, 5000, rows).astype(float)
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": vol},
        index=idx,
    )


def test_vwap_daily_resets_at_utc_midnight():
    idx = pd.date_range("2024-06-01 20:00", periods=6, freq="1h", tz="UTC")
    df = pd.DataFrame(
        {
            "open": [10, 11, 12, 13, 14, 15],
            "high": [11, 12, 13, 14, 15, 16],
            "low": [9, 10, 11, 12, 13, 14],
            "close": [10, 11, 12, 13, 14, 15],
            "volume": [100, 100, 100, 200, 200, 200],
        },
        index=idx,
    )
    strat = ComboStrategy(
        indicators=[{"type": "vwap_daily", "alias": "vwap_d", "params": {}}],
        entry_logic="close > 0",
        exit_logic="close < 0",
        stop_loss=0.01,
    )
    out = strat.calculate_indicators(df)
    # Last bar of day 1 and first bar of day 2 must not share cumulative state.
    assert out["vwap_d"].iloc[3] != out["vwap_d"].iloc[4]


def test_new_templates_generate_signals_without_error():
    df = _synthetic_ohlcv(450)
    for name in (
        "donchian_volume_breakout",
        "bollinger_squeeze",
        "long_ma_pullback_rsi_adx",
        "Bollinger_Breakout",
    ):
        strategy = _strategy_from_export(name)
        enriched = strategy.calculate_indicators(df)
        signals = strategy.generate_signals(enriched)
        assert len(signals) == len(df)
        assert "signal" in signals.columns


def test_templates_smoke_on_1h_and_15m_series():
    cases = (
        ("donchian_volume_breakout", 500, "1h"),
        ("donchian_volume_breakout", 600, "15min"),
        ("bollinger_squeeze", 500, "1h"),
        ("bollinger_squeeze", 600, "15min"),
        ("long_ma_pullback_rsi_adx", 500, "1h"),
        ("long_ma_pullback_rsi_adx", 600, "15min"),
        ("Bollinger_Breakout", 500, "1h"),
        ("Bollinger_Breakout", 600, "15min"),
    )
    for name, rows, freq in cases:
        df = _synthetic_ohlcv(rows, freq=freq)
        strategy = _strategy_from_export(name)
        enriched = strategy.calculate_indicators(df)
        signals = strategy.generate_signals(enriched)
        assert len(signals) == len(df)
        assert "signal" in signals.columns


def test_vwap_rolling_and_daily_on_same_frame():
    strat = ComboStrategy(
        indicators=[
            {"type": "vwap_daily", "alias": "vwap_d", "params": {}},
            {"type": "vwap_rolling", "alias": "vwap_r", "params": {"length": 10}},
        ],
        entry_logic="(close > vwap_d) & (close > vwap_r)",
        exit_logic="close < vwap_d",
        stop_loss=0.02,
    )
    df = _synthetic_ohlcv(200)
    out = strat.calculate_indicators(df)
    assert out["vwap_d"].notna().any()
    assert out["vwap_r"].notna().any()
    signals = strat.generate_signals(out)
    assert "signal" in signals.columns
