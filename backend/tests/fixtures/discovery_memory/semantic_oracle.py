"""Independent intended-series oracle; never imports the runtime resolver."""

import numpy as np
import pandas as pd
import talib


def masks(frame, parameters):
    close = frame.close.to_numpy(dtype=float)
    high = frame.high.to_numpy(dtype=float)
    low = frame.low.to_numpy(dtype=float)
    ma = pd.Series(
        talib.SMA(close, timeperiod=parameters.get("ma_long_length", 200)), index=frame.index
    )
    rsi = pd.Series(
        talib.RSI(close, timeperiod=parameters.get("rsi_length", 14)), index=frame.index
    )
    adx = pd.Series(
        talib.ADX(high, low, close, timeperiod=parameters.get("adx_length", 14)), index=frame.index
    )
    pullback = ma * (1 + parameters.get("ma_long_pullback_pct", 2.0) / 100)
    entry = (
        (frame.close > ma)
        & (frame.close < pullback)
        & (rsi < parameters.get("rsi_oversold", 40))
        & (adx > parameters.get("adx_threshold", 22))
    )
    exit_ = (frame.close < ma) | (rsi > parameters.get("rsi_overbought", 65))
    return {"ma_long": ma, "rsi": rsi, "adx": adx, "entry": entry, "exit": exit_}


def frame_fixture(n=800):
    close = 100 + np.sin(np.arange(n) / 11) * 8 + np.arange(n) / 20
    return pd.DataFrame(
        {
            "open": close,
            "high": close + 2,
            "low": close - 2,
            "close": close,
            "volume": np.full(n, 1000),
        },
        index=pd.date_range("2025-10-06", periods=n, freq="15min", tz="UTC"),
    )


def evaluate(frame, parameters, deep=False, intraday=None):
    """Independent TA-Lib series/masks and frozen baseline position loop.

    Execution-cost/Deep and metrics functions are shared unchanged contracts;
    separate tests compare them exactly with the frozen historical oracle.
    No runtime indicator resolver or cache is used here.
    """
    from tests.fixtures.discovery_memory.position_reference import signals
    from app.services.combo_optimizer import extract_trades_with_mode, _metrics_from_trades
    from app.metrics.backtest_execution_costs import slippage_for_timeframe

    intended = masks(frame, parameters)
    stop = parameters.get("stop_loss", 0.02)
    direction = parameters.get("direction", "long")
    signalled = signals(frame.copy(), intended["entry"], intended["exit"], stop, direction)
    trades = extract_trades_with_mode(
        signalled,
        stop,
        deep_backtest=deep,
        symbol="BTC/USDT",
        since_str="2025-10-06",
        until_str="2026-10-06",
        df_15m_cache=intraday,
        direction=direction,
        slippage=slippage_for_timeframe(parameters.get("timeframe", "15m")),
    )
    metrics = _metrics_from_trades(trades, 100)
    atr_cols = [column for column in frame if str(column).startswith("ATR")]
    metrics["avg_atr"] = float(frame[atr_cols[0]].dropna().mean()) if atr_cols else None
    mean_adx = intended["adx"].dropna().mean()
    metrics["avg_adx"] = float(mean_adx) if mean_adx == mean_adx else None
    return metrics, trades, signalled
