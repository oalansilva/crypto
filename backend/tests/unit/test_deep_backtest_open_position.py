from __future__ import annotations

import pandas as pd

from app.services.deep_backtest import simulate_execution_with_15m
from app.services.favorite_backtest_refresh_service import (
    _ensure_trade_events_within_candles,
)


class _Favorite:
    symbol = "BTC/USDT"
    timeframe = "1d"


def _daily(signals: list[int]) -> pd.DataFrame:
    index = pd.date_range("2026-07-09", periods=len(signals), freq="1D", tz="UTC")
    return pd.DataFrame(
        {
            "open": [100.0 + offset for offset in range(len(signals))],
            "high": [101.0 + offset for offset in range(len(signals))],
            "low": [99.0 + offset for offset in range(len(signals))],
            "close": [100.5 + offset for offset in range(len(signals))],
            "signal": signals,
        },
        index=index,
    )


def test_open_position_does_not_create_end_of_period_exit() -> None:
    trades = simulate_execution_with_15m(_daily([0, 1, 0]), pd.DataFrame(), 0.05)

    assert trades == []


def test_real_intraday_stop_is_preserved_for_open_position() -> None:
    daily = _daily([0, 1, 0])
    intraday_index = pd.date_range("2026-07-10", periods=8, freq="15min", tz="UTC")
    intraday = pd.DataFrame(
        {
            "high": [102.0] * 8,
            "low": [100.0, 99.0, 95.0, 94.0, 94.0, 94.0, 94.0, 94.0],
        },
        index=intraday_index,
    )

    trades = simulate_execution_with_15m(daily, intraday, 0.05)

    assert len(trades) == 1
    assert trades[0]["exit_reason"] == "stop_loss_15m"
    assert trades[0]["exit_time"] == intraday_index[2].isoformat()


def test_refresh_rejects_trade_after_returned_candle_coverage() -> None:
    result = {
        "candles": [{"timestamp_utc": "2026-07-11T00:00:00Z"}],
        "trades": [
            {
                "entry_time": "2026-07-10T00:00:00Z",
                "exit_time": "2026-07-12T00:00:00Z",
            }
        ],
    }

    try:
        _ensure_trade_events_within_candles(result, _Favorite())
    except RuntimeError as exc:
        assert "exit_time=2026-07-12T00:00:00Z" in str(exc)
    else:
        raise AssertionError("future trade event should fail refresh validation")
