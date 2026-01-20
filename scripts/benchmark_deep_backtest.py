
import sys
import os
import time
import pandas as pd
import numpy as np
import logging

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Benchmark")

def generate_synthetic_data(days=365):
    """Generates synthetic daily and 15m data for testing."""
    logger.info(f"Generating synthetic data for {days} days...")
    
    # Date range
    start_date = pd.Timestamp("2023-01-01", tz="UTC")
    end_date = start_date + pd.Timedelta(days=days)
    
    # 1. Daily Data
    dates_daily = pd.date_range(start=start_date, end=end_date, freq="D")
    df_daily = pd.DataFrame(index=dates_daily)
    df_daily['open'] = 100 + np.random.randn(len(dates_daily)).cumsum()
    df_daily['high'] = df_daily['open'] + abs(np.random.randn(len(dates_daily)))
    df_daily['low'] = df_daily['open'] - abs(np.random.randn(len(dates_daily)))
    df_daily['close'] = df_daily['open'] + np.random.randn(len(dates_daily))
    
    # Generate signals (buy every ~20 days, sell every ~5 days after buy)
    df_daily['signal'] = 0
    in_position = False
    days_since_entry = 0
    
    for i in range(len(df_daily)):
        if not in_position:
            if np.random.random() < 0.05: # 5% chance to buy
                df_daily.iloc[i, df_daily.columns.get_loc('signal')] = 1
                in_position = True
                days_since_entry = 0
        else:
            days_since_entry += 1
            # Sell if held for too long or random chance
            if days_since_entry > 10 or np.random.random() < 0.1:
                df_daily.iloc[i, df_daily.columns.get_loc('signal')] = -1
                in_position = False

    # 2. 15m Data
    dates_15m = pd.date_range(start=start_date, end=end_date + pd.Timedelta(days=1), freq="15min")
    df_15m = pd.DataFrame(index=dates_15m)
    # Simulate valid price movement relative to daily
    # For simplicity in benchmark, just random walk, but ensure integrity with daily is not strictly required for perf test
    # However, to test stop-loss logic, we need 'low'
    df_15m['open'] = 100 + np.random.randn(len(dates_15m)).cumsum()
    df_15m['low'] = df_15m['open'] - abs(np.random.randn(len(dates_15m)) * 0.5) 
    
    logger.info(f"Generated {len(df_daily)} daily rows and {len(df_15m)} 15m rows.")
    return df_daily, df_15m

def compare_results(trades_a, trades_b):
    """Compares two trade lists for equality."""
    if len(trades_a) != len(trades_b):
        logger.error(f"Mismatch in trade count: {len(trades_a)} vs {len(trades_b)}")
        return False
        
    for i, (t_a, t_b) in enumerate(zip(trades_a, trades_b)):
        # Check tolerance for floats
        keys_to_check = ['entry_price', 'exit_price', 'profit']
        
        # entry_time key might vary if optimized version picks slightly different isoformat precision, 
        # but generally should be identical.
        if t_a['entry_time'] != t_b['entry_time']:
             logger.error(f"Trade {i} entry_time mismatch: {t_a['entry_time']} vs {t_b['entry_time']}")
             return False

        if t_a['exit_time'] != t_b['exit_time']:
             logger.error(f"Trade {i} exit_time mismatch: {t_a['exit_time']} vs {t_b['exit_time']}")
             # Return False only if strict, but maybe logging is enough if it's very close?
             # For deep backtest, 15m candle exit time should be exact match.
             return False

        if t_a['exit_reason'] != t_b['exit_reason']:
            logger.error(f"Trade {i} exit_reason mismatch: {t_a['exit_reason']} vs {t_b['exit_reason']}")
            return False

        for k in keys_to_check:
            if abs(t_a[k] - t_b[k]) > 1e-9:
                logger.error(f"Trade {i} {k} mismatch: {t_a[k]} vs {t_b[k]}")
                return False
                
    return True

def run_benchmark():
    df_daily, df_15m = generate_synthetic_data(days=365)
    stop_loss = 0.02 # 2%
    
    try:
        from app.services import deep_backtest_old
        logger.info("Loaded legacy deep_backtest_old for comparison.")
        has_old = True
    except ImportError:
        logger.warning("Could not load deep_backtest_old. Skipping comparison, running only performance test of current.")
        has_old = False

    from app.services import deep_backtest
    
    if has_old:
        logger.info("--- Running Original Implementation ---")
        start_time = time.time()
        trades_old = deep_backtest_old.simulate_execution_with_15m(df_daily, df_15m, stop_loss)
        time_old = time.time() - start_time
        logger.info(f"Original: {len(trades_old)} trades in {time_old:.4f}s")

    logger.info("--- Running Optimized Implementation ---")
    start_time = time.time()
    trades_new = deep_backtest.simulate_execution_with_15m(df_daily, df_15m, stop_loss)
    time_new = time.time() - start_time
    logger.info(f"Optimized: {len(trades_new)} trades in {time_new:.4f}s")
    
    if has_old:
        logger.info(f"Speedup: {time_old / time_new:.2f}x")
        
        logger.info("--- Verifying Results ---")
        if compare_results(trades_old, trades_new):
            logger.info("✅ SUCCESS: Results are identical!")
        else:
            logger.error("❌ FAILURE: Results differ!")
            
if __name__ == "__main__":
    run_benchmark()
