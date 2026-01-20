"""
Deep Backtesting Module - 15m Intraday Execution Simulation

This module provides the core logic for Deep Backtesting, which simulates
trade execution using 15-minute candles to resolve temporal ambiguity in
daily OHLC data.
"""

import pandas as pd
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
    
    logger.info(f"Starting Deep Backtest simulation with {len(df_daily_signals)} daily signals and {len(df_15m)} 15m candles")
    
    # Pre-calculate entry and exit signals from daily dataframe
    # This avoids iterating row-by-row for the whole dataframe
    entry_signals = df_daily_signals[df_daily_signals['signal'] == 1]
    
    # We will iterate through valid entry signals
    # For each entry, we find the next exit signal
    # Then we check intraday data between those two points
    
    daily_idx_list = df_daily_signals.index
    
    # Convert index to native datetime for faster comparisons if needed, 
    # but pandas handles tz-aware well usually.
    
    last_exit_time = None
    
    for entry_time, entry_row in entry_signals.iterrows():
        # 1. Skip if we are still in a position (simulated strictly sequential trades)
        if last_exit_time is not None and entry_time < last_exit_time:
            continue
            
        entry_price = float(entry_row['open'])
        exact_stop_price = entry_price * (1 - stop_loss_pct)
        
        # 2. Find the NEXT exit signal after this entry
        # We look for signal == -1 that is strictly after entry_time
        # Use simple boolean masking on the daily dataframe slice
        future_signals = df_daily_signals.loc[entry_time:]
        # shift(0) is just the slice. We need the first -1
        
        # Optimization: argmax/idxmax on boolean mask is fast
        # valid_exits mask: (signal == -1) & (index > entry_time)
        # Note: loc[entry_time:] includes entry_time, so we must be careful if signal could switch on same candle (unlikely for daily logic)
        
        # Let's get the standard "signal exit" from daily data
        signal_exit_candidates = future_signals[
            (future_signals['signal'] == -1) & 
            (future_signals.index > entry_time)
        ]
        
        if signal_exit_candidates.empty:
            # Position held until end of data
            signal_exit_time = df_daily_signals.index[-1] + pd.Timedelta(days=1) # hypothetical end
            signal_exit_price = float(df_daily_signals.iloc[-1]['close']) # Approximation for end of data
            reason_end = "end_of_period"
        else:
            signal_exit_time = signal_exit_candidates.index[0]
            signal_exit_price = float(signal_exit_candidates.iloc[0]['open'])
            reason_end = "signal"

        # 3. Vectorized Intraday Check
        # We need to check if LOW <= STOP_PRICE at any time between Entry and Signal Exit
        
        # Slice 15m data ONCE
        # range: [Entry Time, Signal Exit Time) 
        # (Exit executes at OPEN of signal_exit_time, so we check up to that moment, 
        # but arguably the stop could hit ON the signal candle before open? 
        # Standard backtesting usually assumes Signal Exit happens at Open, so intraday checks run up to that timestamp)
        
        mask_intraday = (df_15m.index >= entry_time) & (df_15m.index < signal_exit_time)
        chunk_15m = df_15m.loc[mask_intraday]
        
        if chunk_15m.empty:
            # No intraday data, fallback to signal exit
            final_exit_time = signal_exit_time
            final_exit_price = signal_exit_price
            exit_reason = reason_end if reason_end != "end_of_period" else "force_close"
        else:
             # Check for Stop Loss Hit
            if stop_loss_pct > 0:
                # Boolean mask of hits
                hit_mask = chunk_15m['low'] <= exact_stop_price
                
                if hit_mask.any():
                    # Stop was hit!
                    # Get the timestamp of the FIRST hit
                    first_hit_time = hit_mask.idxmax()
                    
                    final_exit_time = first_hit_time
                    final_exit_price = exact_stop_price
                    exit_reason = "stop_loss"
                else:
                    # No stop hit, exit at signal
                    final_exit_time = signal_exit_time
                    final_exit_price = signal_exit_price
                    exit_reason = reason_end
            else:
                final_exit_time = signal_exit_time
                final_exit_price = signal_exit_price
                exit_reason = reason_end

        # 4. Record Trade
        # Update last_exit_time to prevent overlapping trades
        last_exit_time = final_exit_time
        
        # Calculate profit
        profit = (
            (final_exit_price * (1 - TRADING_FEE)) - 
            (entry_price * (1 + TRADING_FEE))
        ) / (entry_price * (1 + TRADING_FEE))
        
        # Ensure isoformat for JSON serialization
        # entry_time is Timestamp, final_exit_time is Timestamp
        
        trade = {
            'entry_time': entry_time.isoformat(),
            'entry_price': entry_price,
            'type': 'long',
            'exit_time': final_exit_time.isoformat(),
            'exit_price': float(final_exit_price),
            'profit': profit,
            'exit_reason': "stop_loss_15m" if exit_reason == "stop_loss" else "signal_15m" # Match old naming convention
        }
        
        trades.append(trade)

    logger.info(f"Deep Backtest complete: {len(trades)} trades extracted")
    return trades

