
import sys
import os
import pandas as pd
import pandas_ta as ta

# Add project root and backend
current_dir = os.getcwd()
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'backend'))

from src.data.incremental_loader import IncrementalLoader

def check_indicators():
    loader = IncrementalLoader()
    # Need enough data for warm start (EMA 17 needs roughly 3-4x length for accuracy, SMA is exact)
    # Fetching from June 2025
    df = loader.fetch_data(
        symbol="BTC/USDT",
        timeframe="1d",
        since_str="2025-06-01",
        until_str="2025-10-15"
    )
    
    # Calculate indicators
    # Short: EMA 17
    # Medium: SMA 21
    # Long: SMA 34
    
    df['ema_short'] = ta.ema(df['close'], length=17)
    df['sma_medium'] = ta.sma(df['close'], length=21)
    df['sma_long'] = ta.sma(df['close'], length=34)
    
    print("\n=== INDICATOR VALUES (Sep 2025) ===")
    start_idx = df.index.get_loc(pd.Timestamp("2025-09-12 00:00:00+0000"))
    end_idx = df.index.get_loc(pd.Timestamp("2025-09-19 00:00:00+0000"))
    
    subset = df.iloc[start_idx:end_idx]
    
    for idx, row in subset.iterrows():
        short = row['ema_short']
        med = row['sma_medium']
        long_ma = row['sma_long']
        close = row['close']
        
        # Logic: Crossover(Short, Medium) OR Crossover(Short, Long)
        # AND Short > Long
        
        cond_cross_med = (short > med)
        cond_cross_long = (short > long_ma)
        cond_above_long = (short > long_ma) # Redundant but part of logic
        
        print(f"Date: {idx.date()} | Close: {close:.2f} | EMA17: {short:.2f} | SMA21: {med:.2f} | SMA34: {long_ma:.2f}")
        print(f"   Short > Med: {cond_cross_med} | Short > Long: {cond_cross_long}")

if __name__ == "__main__":
    check_indicators()
