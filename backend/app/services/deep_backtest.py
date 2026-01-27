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
    stop_loss: float
) -> List[Dict]:
    """
    Simulate trade execution using 15-minute candles for realistic stop/target validation.
    
    This function implements "Deep Backtesting" by:
    1. Generating signals on daily (1D) candles
    2. Simulating execution using 15m candles to determine exact exit timing
    3. Checking stop/target/reversal candle-by-candle in chronological order
    
    OPTIMIZATION NOTE:
    Uses vectorized operations for finding intraday stop losses to avoid
    slow line-by-line iteration over DataFrame rows (~10-100x speedup).
    
    Args:
        df_daily_signals: DataFrame with 1D candles and signals (indexed by timestamp_utc)
        df_15m: DataFrame with 15m candles (indexed by timestamp_utc)
        stop_loss: Stop loss percentage (e.g., 0.015 for 1.5%)
        
    Returns:
        List of trade dictionaries with accurate entry/exit times and prices
    """

    trades = []
    stop_loss_pct = float(stop_loss) if stop_loss is not None else 0.0
    
    # logger.info(f"Starting Deep Backtest simulation with {len(df_daily_signals)} daily signals and {len(df_15m)} 15m candles")
    
    # -------------------------------------------------------------------------
    # OPTIMIZATION: Convert 15m data to Numpy arrays for O(1) access
    # -------------------------------------------------------------------------
    if df_15m.empty:
        times_15m = np.array([])
        lows_15m = np.array([])
    else:
        times_15m = df_15m.index # Keep as Index for robust searchsorted
        lows_15m = df_15m['low'].values # float array
        
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
            
        # Entry executes at OPEN of daily candle (signal detected at CLOSE of previous candle → execute at OPEN of next day)
        # Note: 15m data is used ONLY for stop loss detection (can execute immediately), not for signal execution
        entry_price = float(entry_row['open'])
        exact_stop_price = entry_price * (1 - stop_loss_pct)
        
        # 2. Find the NEXT exit signal after this entry
        # Use searchsorted on the pre-fetched exit_times (O(log M))
        # strictly greater than entry_time
        next_exit_idx = exit_times.searchsorted(entry_time, side='right')
        
        if next_exit_idx < len(exit_times):
            signal_exit_time = exit_times[next_exit_idx]
            signal_exit_price = float(exit_prices[next_exit_idx])
            reason_end = "signal"
        else:
            # Position held until end of data
            signal_exit_time = df_daily_signals.index[-1] + pd.Timedelta(days=1)
            signal_exit_price = float(df_daily_signals.iloc[-1]['close'])
            reason_end = "end_of_period"

        # 3. Vectorized Intraday Check (Numpy) - ONLY for stop loss detection
        # 15m data is used to detect if stop loss was hit during the day
        # Stop loss can execute immediately when detected (simulating real broker behavior)
        # Entry/exit signals execute at OPEN of daily candles (next day after signal detection)
        # Find range in 15m data: [Entry Time, Signal Exit Time)
        
        if len(times_15m) > 0:
            # Use searchsorted to find indices (O(log N))
            start_idx = times_15m.searchsorted(entry_time)
            end_idx = times_15m.searchsorted(signal_exit_time)
            
            # Slice numpy array (O(1) view)
            chunk_lows = lows_15m[start_idx:end_idx]
            
            # Check for Stop Loss Hit
            if stop_loss_pct > 0 and chunk_lows.size > 0:
                # Find indices where low <= stop_price
                hit_indices = np.where(chunk_lows <= exact_stop_price)[0]
                
                if hit_indices.size > 0:
                    # Stop was hit!
                    hit_offset = hit_indices[0]
                    first_hit_time = times_15m[start_idx + hit_offset]
                    
                    # Convert numpy datetime64 back to Timestamp for consistency
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
             # No 15m data
            final_exit_time = signal_exit_time
            final_exit_price = signal_exit_price
            exit_reason = reason_end

        # 4. Record Trade
        last_exit_time = final_exit_time
        
        # Calculate profit
        profit = (
            (final_exit_price * (1 - TRADING_FEE)) - 
            (entry_price * (1 + TRADING_FEE))
        ) / (entry_price * (1 + TRADING_FEE))
        
        trades.append({
            'entry_time': entry_time.isoformat(),
            'entry_price': entry_price,
            'type': 'long',
            'exit_time': final_exit_time.isoformat(),
            'exit_price': float(final_exit_price),
            'profit': profit,
            'exit_reason': "stop_loss_15m" if exit_reason == "stop_loss" else "signal_15m"
        })

    # logger.info(f"Deep Backtest complete: {len(trades)} trades extracted")
    return trades

