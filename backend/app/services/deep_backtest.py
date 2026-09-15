"""
Deep Backtesting Module - 15m Intraday Execution Simulation

This module provides the core logic for Deep Backtesting, which simulates
trade execution using 15-minute candles to resolve temporal ambiguity in
daily OHLC data.
"""

import os
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

TRADING_FEE = 0.00075  # Binance 0.075%


def simulate_execution_with_15m(
    df_daily_signals: pd.DataFrame, df_15m: pd.DataFrame, stop_loss: float, direction: str = "long"
) -> List[Dict]:
    if os.environ.get("COMBO_OPTIMIZER_LEGACY") == "1":
        return _legacy_simulate_execution_with_15m(
            df_daily_signals, df_15m, stop_loss, direction
        )
    return _fast_simulate_execution_with_15m(
        df_daily_signals, df_15m, stop_loss, direction
    )


def _legacy_simulate_execution_with_15m(
    df_daily_signals: pd.DataFrame, df_15m: pd.DataFrame, stop_loss: float, direction: str = "long"
) -> List[Dict]:
    """
    Simulate trade execution using 15-minute candles for realistic stop/target validation.

    direction: "long" (default) or "short". Short = stop above entry (high >= stop_price), PnL when price falls.

    CRITICAL PRIORITY RULES:
    - STOP LOSS ALWAYS has priority over exit signals
    - Stop loss is checked FIRST in the period between entry and exit signal

    Args:
        df_daily_signals: DataFrame with 1D candles and signals (indexed by timestamp_utc)
        df_15m: DataFrame with 15m candles (indexed by timestamp_utc)
        stop_loss: Stop loss percentage (e.g., 0.015 for 1.5%)
        direction: "long" or "short"

    Returns:
        List of trade dictionaries with accurate entry/exit times and prices
    """
    trades = []
    stop_loss_pct = float(stop_loss) if stop_loss is not None else 0.0
    is_short = (direction or "long").lower() == "short"

    if df_15m.empty:
        times_15m = np.array([])
        lows_15m = np.array([])
        highs_15m = np.array([])
    else:
        times_15m = df_15m.index
        lows_15m = df_15m["low"].values
        highs_15m = df_15m["high"].values

    # Pre-calculate entry signals
    entry_signals = df_daily_signals[df_daily_signals["signal"] == 1]

    # Pre-calculate ALL exit signals (signal == -1) to avoid repeated filtering
    exit_signals = df_daily_signals[df_daily_signals["signal"] == -1]
    exit_times = exit_signals.index
    # Exit executes at OPEN of daily candle (signal detected at CLOSE of previous candle → execute at OPEN of next day)
    exit_prices = exit_signals["open"].values

    last_exit_time = None

    for entry_time, entry_row in entry_signals.iterrows():
        # 1. Skip if we are still in a position (simulated strictly sequential trades)
        if last_exit_time is not None and entry_time < last_exit_time:
            continue

        entry_price = float(entry_row["open"])
        if is_short:
            exact_stop_price = entry_price * (1 + stop_loss_pct)  # short: stop above entry
        else:
            exact_stop_price = entry_price * (1 - stop_loss_pct)  # long: stop below entry

        next_exit_idx = exit_times.searchsorted(entry_time, side="right")
        if next_exit_idx < len(exit_times):
            signal_exit_time = exit_times[next_exit_idx]
            signal_exit_price = float(exit_prices[next_exit_idx])
            reason_end = "signal"
        else:
            signal_exit_time = df_daily_signals.index[-1] + pd.Timedelta(days=1)
            signal_exit_price = float(df_daily_signals.iloc[-1]["close"])
            reason_end = "end_of_period"

        # 3. PRIORIDADE 1: Intraday stop loss check (high for short, low for long)
        if len(times_15m) > 0:
            start_idx = times_15m.searchsorted(entry_time)
            end_idx = times_15m.searchsorted(signal_exit_time)
            if is_short:
                chunk_ohlc = highs_15m[start_idx:end_idx]
                hit_stop = (
                    stop_loss_pct > 0
                    and chunk_ohlc.size > 0
                    and np.any(chunk_ohlc >= exact_stop_price)
                )
            else:
                chunk_ohlc = lows_15m[start_idx:end_idx]
                hit_stop = (
                    stop_loss_pct > 0
                    and chunk_ohlc.size > 0
                    and np.any(chunk_ohlc <= exact_stop_price)
                )

            if hit_stop and stop_loss_pct > 0 and chunk_ohlc.size > 0:
                if is_short:
                    hit_indices = np.where(chunk_ohlc >= exact_stop_price)[0]
                else:
                    hit_indices = np.where(chunk_ohlc <= exact_stop_price)[0]
                if hit_indices.size > 0:
                    hit_offset = hit_indices[0]
                    first_hit_time = times_15m[start_idx + hit_offset]
                    final_exit_time = pd.Timestamp(first_hit_time)
                    if final_exit_time.tz is None and entry_time.tz is not None:
                        final_exit_time = final_exit_time.tz_localize(entry_time.tz)
                    final_exit_price = exact_stop_price
                    exit_reason = "stop_loss"
                else:
                    final_exit_time = signal_exit_time
                    final_exit_price = signal_exit_price
                    exit_reason = reason_end
            else:
                final_exit_time = signal_exit_time
                final_exit_price = signal_exit_price
                exit_reason = reason_end
        else:
            final_exit_time = signal_exit_time
            final_exit_price = signal_exit_price
            exit_reason = reason_end

        # An open position is not a completed trade.  The old implementation
        # fabricated an exit on the day after the last candle, which could be
        # cached and exposed as a future sell signal by the monitor.
        if exit_reason == "end_of_period":
            continue

        last_exit_time = final_exit_time
        if is_short:
            profit = (
                entry_price * (1 - TRADING_FEE) - float(final_exit_price) * (1 + TRADING_FEE)
            ) / (entry_price * (1 - TRADING_FEE))
        else:
            profit = (
                (final_exit_price * (1 - TRADING_FEE)) - (entry_price * (1 + TRADING_FEE))
            ) / (entry_price * (1 + TRADING_FEE))

        signal_type = "Stop" if exit_reason == "stop_loss" else "Close entry(s) order..."
        trades.append(
            {
                "entry_time": entry_time.isoformat(),
                "entry_price": entry_price,
                "type": "short" if is_short else "long",
                "exit_time": final_exit_time.isoformat(),
                "exit_price": float(final_exit_price),
                "profit": profit,
                "exit_reason": "stop_loss_15m" if exit_reason == "stop_loss" else "signal_15m",
                "signal_type": signal_type,
                "entry_signal_type": "Vender" if is_short else "Comprar",
            }
        )

    # logger.info(f"Deep Backtest complete: {len(trades)} trades extracted")
    return trades


_ISO_CACHE: dict = {}


def _iso_array(index: pd.Index) -> np.ndarray:
    if len(index) == 0:
        return np.array([], dtype=object)
    key = (int(pd.Timestamp(index[0]).value), int(pd.Timestamp(index[-1]).value), len(index))
    cached = _ISO_CACHE.get(key)
    if cached is not None:
        return cached
    arr = np.array([pd.Timestamp(ts).isoformat() for ts in index], dtype=object)
    _ISO_CACHE[key] = arr
    return arr


def _asi8(index: pd.Index) -> np.ndarray:
    if hasattr(index, "asi8"):
        return np.asarray(index.asi8)
    return pd.DatetimeIndex(index).asi8


def _fast_simulate_execution_with_15m(
    df_daily_signals: pd.DataFrame, df_15m: pd.DataFrame, stop_loss: float, direction: str = "long"
) -> List[Dict]:
    trades = []
    stop_loss_pct = float(stop_loss) if stop_loss is not None else 0.0
    is_short = (direction or "long").lower() == "short"

    daily_index = df_daily_signals.index
    daily_iso = _iso_array(daily_index)
    daily_asi8 = _asi8(daily_index)
    opens = df_daily_signals["open"].to_numpy(dtype=np.float64, copy=False)
    closes = df_daily_signals["close"].to_numpy(dtype=np.float64, copy=False)
    signals = df_daily_signals["signal"].to_numpy(copy=False)
    entry_pos = np.flatnonzero(signals == 1)
    exit_pos = np.flatnonzero(signals == -1)
    exit_asi8 = daily_asi8[exit_pos] if exit_pos.size else np.array([], dtype=np.int64)
    exit_opens = opens[exit_pos] if exit_pos.size else np.array([], dtype=np.float64)

    if df_15m.empty:
        times_15_asi8 = np.array([], dtype=np.int64)
        lows_15m = np.array([], dtype=np.float64)
        highs_15m = np.array([], dtype=np.float64)
        iso_15 = np.array([], dtype=object)
    else:
        times_15_asi8 = _asi8(df_15m.index)
        lows_15m = df_15m["low"].to_numpy(dtype=np.float64, copy=False)
        highs_15m = df_15m["high"].to_numpy(dtype=np.float64, copy=False)
        iso_15 = _iso_array(df_15m.index)

    last_exit_asi8 = None
    last_daily_close = float(closes[-1]) if len(closes) else 0.0
    last_daily_asi8 = int(daily_asi8[-1]) if len(daily_asi8) else 0
    day_ns = int(pd.Timedelta(days=1).value)

    for eidx in entry_pos:
        entry_asi8 = int(daily_asi8[eidx])
        if last_exit_asi8 is not None and entry_asi8 < last_exit_asi8:
            continue

        entry_price = float(opens[eidx])
        if is_short:
            exact_stop_price = entry_price * (1 + stop_loss_pct)
        else:
            exact_stop_price = entry_price * (1 - stop_loss_pct)

        next_exit_idx = int(exit_asi8.searchsorted(entry_asi8, side="right")) if exit_asi8.size else 0
        if next_exit_idx < len(exit_asi8):
            signal_exit_asi8 = int(exit_asi8[next_exit_idx])
            signal_exit_price = float(exit_opens[next_exit_idx])
            signal_exit_iso = daily_iso[exit_pos[next_exit_idx]]
            reason_end = "signal"
        else:
            signal_exit_asi8 = last_daily_asi8 + day_ns
            signal_exit_price = last_daily_close
            signal_exit_iso = None
            reason_end = "end_of_period"

        exit_reason = reason_end
        final_exit_iso = signal_exit_iso
        final_exit_price = signal_exit_price
        final_exit_asi8 = signal_exit_asi8

        if times_15_asi8.size > 0:
            start_idx = int(times_15_asi8.searchsorted(entry_asi8))
            end_idx = int(times_15_asi8.searchsorted(signal_exit_asi8))
            if is_short:
                chunk_ohlc = highs_15m[start_idx:end_idx]
                hit_stop = (
                    stop_loss_pct > 0
                    and chunk_ohlc.size > 0
                    and np.any(chunk_ohlc >= exact_stop_price)
                )
            else:
                chunk_ohlc = lows_15m[start_idx:end_idx]
                hit_stop = (
                    stop_loss_pct > 0
                    and chunk_ohlc.size > 0
                    and np.any(chunk_ohlc <= exact_stop_price)
                )
            if hit_stop and stop_loss_pct > 0 and chunk_ohlc.size > 0:
                if is_short:
                    hit_indices = np.where(chunk_ohlc >= exact_stop_price)[0]
                else:
                    hit_indices = np.where(chunk_ohlc <= exact_stop_price)[0]
                if hit_indices.size > 0:
                    hit_offset = int(hit_indices[0])
                    final_exit_iso = iso_15[start_idx + hit_offset]
                    final_exit_price = exact_stop_price
                    final_exit_asi8 = int(times_15_asi8[start_idx + hit_offset])
                    exit_reason = "stop_loss"

        if exit_reason == "end_of_period":
            continue

        last_exit_asi8 = final_exit_asi8
        if is_short:
            profit = (
                entry_price * (1 - TRADING_FEE) - float(final_exit_price) * (1 + TRADING_FEE)
            ) / (entry_price * (1 - TRADING_FEE))
        else:
            profit = (
                (final_exit_price * (1 - TRADING_FEE)) - (entry_price * (1 + TRADING_FEE))
            ) / (entry_price * (1 + TRADING_FEE))

        signal_type = "Stop" if exit_reason == "stop_loss" else "Close entry(s) order..."
        if final_exit_iso is None:
            final_exit_iso = pd.Timestamp(final_exit_asi8).isoformat()
        trades.append(
            {
                "entry_time": daily_iso[eidx],
                "entry_price": entry_price,
                "type": "short" if is_short else "long",
                "exit_time": final_exit_iso,
                "exit_price": float(final_exit_price),
                "profit": profit,
                "exit_reason": "stop_loss_15m" if exit_reason == "stop_loss" else "signal_15m",
                "signal_type": signal_type,
                "entry_signal_type": "Vender" if is_short else "Comprar",
            }
        )

    return trades
