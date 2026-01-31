"""
Deep Backtesting Module - 15m Intraday Execution Simulation

This module provides the core logic for Deep Backtesting, which simulates
trade execution using 15-minute candles to resolve temporal ambiguity in
daily OHLC data.
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

TRADING_FEE = 0.00075  # Binance 0.075%


def simulate_execution_with_15m(
    df_daily_signals: pd.DataFrame,
    df_15m: pd.DataFrame,
    stop_loss: float,
    direction: str = "long"
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
        lows_15m = df_15m['low'].values
        highs_15m = df_15m['high'].values
        
    # Pre-calculate entry signals
    entry_signals = df_daily_signals[df_daily_signals['signal'] == 1]
    
    # Pre-calculate ALL exit signals (signal == -1) to avoid repeated filtering
    exit_signals = df_daily_signals[df_daily_signals['signal'] == -1]
    exit_times = exit_signals.index
    # Exit executes at OPEN of daily candle (signal detected at CLOSE of previous candle → execute at OPEN of next day)
    exit_prices = exit_signals['open'].values
    
    last_exit_time = None
    
    for entry_time, entry_row in entry_signals.iterrows():
        # 1. Skip if we are still in a position (simulated strictly sequential trades)
        if last_exit_time is not None and entry_time < last_exit_time:
            continue
            
        entry_price = float(entry_row['open'])
        if is_short:
            exact_stop_price = entry_price * (1 + stop_loss_pct)  # short: stop above entry
        else:
            exact_stop_price = entry_price * (1 - stop_loss_pct)  # long: stop below entry
        
        next_exit_idx = exit_times.searchsorted(entry_time, side='right')
        if next_exit_idx < len(exit_times):
            signal_exit_time = exit_times[next_exit_idx]
            signal_exit_price = float(exit_prices[next_exit_idx])
            reason_end = "signal"
        else:
            signal_exit_time = df_daily_signals.index[-1] + pd.Timedelta(days=1)
            signal_exit_price = float(df_daily_signals.iloc[-1]['close'])
            reason_end = "end_of_period"

        # 3. PRIORIDADE 1: Intraday stop loss check (high for short, low for long)
        if len(times_15m) > 0:
            start_idx = times_15m.searchsorted(entry_time)
            end_idx = times_15m.searchsorted(signal_exit_time)
            if is_short:
                chunk_ohlc = highs_15m[start_idx:end_idx]
                hit_stop = stop_loss_pct > 0 and chunk_ohlc.size > 0 and np.any(chunk_ohlc >= exact_stop_price)
            else:
                chunk_ohlc = lows_15m[start_idx:end_idx]
                hit_stop = stop_loss_pct > 0 and chunk_ohlc.size > 0 and np.any(chunk_ohlc <= exact_stop_price)
            
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

        last_exit_time = final_exit_time
        if is_short:
            profit = (entry_price * (1 - TRADING_FEE) - float(final_exit_price) * (1 + TRADING_FEE)) / (entry_price * (1 - TRADING_FEE))
        else:
            profit = (
                (final_exit_price * (1 - TRADING_FEE)) -
                (entry_price * (1 + TRADING_FEE))
            ) / (entry_price * (1 + TRADING_FEE))
        
        signal_type = "Stop" if exit_reason == "stop_loss" else "Close entry(s) order..."
        trades.append({
            'entry_time': entry_time.isoformat(),
            'entry_price': entry_price,
            'type': 'short' if is_short else 'long',
            'exit_time': final_exit_time.isoformat(),
            'exit_price': float(final_exit_price),
            'profit': profit,
            'exit_reason': "stop_loss_15m" if exit_reason == "stop_loss" else "signal_15m",
            'signal_type': signal_type,
            'entry_signal_type': 'Vender' if is_short else 'Comprar'
        })

    # logger.info(f"Deep Backtest complete: {len(trades)} trades extracted")
    return trades

