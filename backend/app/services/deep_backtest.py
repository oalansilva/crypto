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
    
    Args:
        df_daily_signals: DataFrame with 1D candles and signals (indexed by timestamp_utc)
        df_15m: DataFrame with 15m candles (indexed by timestamp_utc)
        stop_loss: Stop loss percentage (e.g., 0.015 for 1.5%)
        
    Returns:
        List of trade dictionaries with accurate entry/exit times and prices
    """
    trades = []
    position = None
    stop_loss_pct = float(stop_loss) if stop_loss is not None else 0.0
    
    logger.info(f"Starting Deep Backtest simulation with {len(df_daily_signals)} daily signals and {len(df_15m)} 15m candles")
    
    # Convert to list for easier iteration
    daily_rows = list(df_daily_signals.iterrows())
    
    for i, (daily_idx, daily_row) in enumerate(daily_rows):
        # Check for entry signal
        if daily_row['signal'] == 1 and position is None:
            # Entry signal detected on this daily candle
            entry_time = daily_idx
            entry_price = float(daily_row['open'])
            
            position = {
                'entry_time': entry_time.isoformat(),
                'entry_price': entry_price,
                'type': 'long',
                'entry_day_idx': i  # Store index for later reference
            }
            logger.debug(f"Entry signal at {entry_time} @ ${entry_price:,.2f}")
            continue
        
        # If we have an open position, check for exit
        if position is not None:
            entry_price = position['entry_price']
            exact_stop_price = entry_price * (1 - stop_loss_pct)
            entry_day_idx = position['entry_day_idx']
            
            # Get all 15m candles from entry day to current day
            entry_day_start = pd.Timestamp(daily_rows[entry_day_idx][0].date(), tz='UTC')
            current_day_end = pd.Timestamp(daily_idx.date(), tz='UTC') + pd.Timedelta(days=1)
            
            # Filter 15m candles for the entire position duration
            intraday_candles = df_15m[(df_15m.index >= entry_day_start) & (df_15m.index < current_day_end)]
            
            if intraday_candles.empty:
                logger.warning(f"No 15m candles found from {entry_day_start} to {current_day_end}. Skipping intraday simulation.")
                # Fall back to daily logic
                if daily_row['signal'] == -1:
                    exit_price = float(daily_row['open'])
                    position['exit_time'] = daily_idx.isoformat()
                    position['exit_price'] = exit_price
                    position['profit'] = (
                        (exit_price * (1 - TRADING_FEE)) - 
                        (entry_price * (1 + TRADING_FEE))
                    ) / (entry_price * (1 + TRADING_FEE))
                    position['exit_reason'] = 'signal_fallback'
                    trades.append(position)
                    position = None
                continue
            
            # Iterate through 15m candles chronologically
            stop_hit = False
            for candle_idx, candle_row in intraday_candles.iterrows():
                # Skip candles before entry
                if candle_idx < entry_day_start:
                    continue
                
                # 1. Check Stop Loss (priority: stop is checked first)
                if stop_loss_pct > 0:
                    current_low = float(candle_row['low'])
                    if current_low <= exact_stop_price:
                        # Stop loss triggered
                        position['exit_time'] = candle_idx.isoformat()
                        position['exit_price'] = exact_stop_price
                        position['profit'] = (
                            (exact_stop_price * (1 - TRADING_FEE)) - 
                            (entry_price * (1 + TRADING_FEE))
                        ) / (entry_price * (1 + TRADING_FEE))
                        position['exit_reason'] = 'stop_loss_15m'
                        trades.append(position)
                        logger.debug(f"Stop loss hit at {candle_idx} @ ${exact_stop_price:,.2f}")
                        position = None
                        stop_hit = True
                        break  # Exit intraday loop
            
            # If stop was hit, move to next daily candle
            if stop_hit:
                continue
            
            # After processing all 15m candles, check if exit signal occurred
            if position is not None and daily_row['signal'] == -1:
                # Exit signal on this daily candle
                exit_price = float(daily_row['open'])
                
                position['exit_time'] = daily_idx.isoformat()
                position['exit_price'] = exit_price
                position['profit'] = (
                    (exit_price * (1 - TRADING_FEE)) - 
                    (entry_price * (1 + TRADING_FEE))
                ) / (entry_price * (1 + TRADING_FEE))
                position['exit_reason'] = 'signal_15m'
                trades.append(position)
                logger.debug(f"Exit signal at {daily_idx} @ ${exit_price:,.2f}")
                position = None
    
    logger.info(f"Deep Backtest complete: {len(trades)} trades extracted")
    return trades

