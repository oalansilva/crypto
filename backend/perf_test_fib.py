"""
Performance test for optimized Fibonacci EMA strategy
"""
import pandas as pd
import time
import sys
sys.path.insert(0, 'app')

from strategies.fibonacci_ema import FibonacciEmaStrategy

# Load test data
print("Loading BTC/USDT 5m data...")
df = pd.read_parquet('data/storage/binance/BTC_USDT_5m.parquet')
print(f"Loaded {len(df):,} candles")
print(f"Period: {df.index[0]} to {df.index[-1]}")

# Initialize strategy
config = {
    'ema_period': 200,
    'swing_lookback': 20,
    'fib_level_1': 0.5,
    'fib_level_2': 0.618,
    'level_tolerance': 0.005
}

strategy = FibonacciEmaStrategy(config)

# Test performance
print("\n" + "="*60)
print("PERFORMANCE TEST")
print("="*60)

start_time = time.time()
signals = strategy.generate_signals(df)
elapsed_time = time.time() - start_time

# Results
buy_signals = (signals == 1).sum()
sell_signals = (signals == -1).sum()
hold_signals = (signals == 0).sum()

print(f"\n✓ Backtest completed successfully!")
print(f"\nExecution time: {elapsed_time:.2f} seconds")
print(f"Processing speed: {len(df)/elapsed_time:,.0f} candles/second")
print(f"\nSignals generated:")
print(f"  - Buy signals:  {buy_signals:,}")
print(f"  - Sell signals: {sell_signals:,}")
print(f"  - Hold signals: {hold_signals:,}")
print(f"\nTotal candles processed: {len(df):,}")
print("="*60)
