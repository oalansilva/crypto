from __future__ import annotations

import pandas as pd

from app.services.combo_optimizer import extract_trades_from_signals


def test_extract_trades_from_signals_short_profits_when_price_falls():
    df = pd.DataFrame(
        {
            "open": [100.0, 99.0, 90.0],
            "high": [101.0, 100.0, 91.0],
            "low": [99.0, 89.0, 88.0],
            "close": [100.0, 90.0, 89.0],
            "signal": [1, 0, -1],
        },
        index=pd.date_range("2026-01-01", periods=3, freq="D", tz="UTC"),
    )

    trades = extract_trades_from_signals(df, stop_loss=0.05, direction="short")

    assert len(trades) == 1
    assert trades[0]["type"] == "short"
    assert trades[0]["entry_signal_type"] == "Vender"
    assert trades[0]["exit_reason"] == "signal"
    assert trades[0]["profit"] > 0


def test_extract_trades_from_signals_short_stops_above_entry():
    df = pd.DataFrame(
        {
            "open": [100.0, 100.0],
            "high": [101.0, 106.0],
            "low": [99.0, 98.0],
            "close": [100.0, 101.0],
            "signal": [1, 0],
        },
        index=pd.date_range("2026-01-01", periods=2, freq="D", tz="UTC"),
    )

    trades = extract_trades_from_signals(df, stop_loss=0.05, direction="short")

    assert len(trades) == 1
    assert trades[0]["exit_reason"] == "stop_loss"
    assert trades[0]["exit_price"] == 105.0
    assert trades[0]["profit"] < 0
