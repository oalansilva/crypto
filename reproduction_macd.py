
import pandas as pd
import pandas_ta as ta
from src.data.incremental_loader import IncrementalLoader
from src.strategy.generic import GenericStrategy
import sys

def test_debug():
    symbol = "BTC/USDT"
    timeframe = "1d"
    
    loader = IncrementalLoader(exchange_id="binance")
    df = loader.fetch_data(symbol, timeframe, since_str="2024-01-01") 
    # Shorter date range for speed
    
    if df.empty:
        print("Error: No data fetched")
        return

    print(f"Data shape: {df.shape}")
    
    # 1. Test Direct Call with INTs
    print("\n--- Test 1: Direct MACD(fast=6, slow=13, signal=5) ---")
    df1 = df.copy()
    try:
        df1.ta.macd(fast=6, slow=13, signal=5, append=True)
        cols = [c for c in df1.columns if 'MACD' in c]
        print(f"Columns: {cols}")
    except Exception as e:
        print(f"Error: {e}")

    # 2. Test Direct Call with FLOATs
    print("\n--- Test 2: Direct MACD(fast=6.0, slow=13.0, signal=5.0) ---")
    df2 = df.copy()
    try:
        df2.ta.macd(fast=6.0, slow=13.0, signal=5.0, append=True)
        cols = [c for c in df2.columns if 'MACD' in c]
        print(f"Columns: {cols}")
    except Exception as e:
        print(f"Error: {e}")

    # 3. Test Via Strategy Strategy (Wrapper) with Floats + Extra Params
    print("\n--- Test 3: GenericStrategy with Mixed Params ---")
    params = {
        'fast_period': 12, 
        'slow_period': 26, 
        'signal_period': 9, 
        'timeframe': '1d', 
        'signal': 5.0, 
        'slow': 13.0, 
        'fast': 6.0
    }
    strategy = GenericStrategy("macd", **params)
    df3 = strategy.generate_signals(df.copy())
    cols = [c for c in df3.columns if 'MACD' in c]
    print(f"Columns: {cols}")
    print(f"Signals: {df3['signal'].abs().sum()}")

if __name__ == "__main__":
    test_debug()
