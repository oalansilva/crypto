
import pandas as pd
import pandas_ta as ta
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)

def debug_ichimoku():
    print("Creating dummy data...")
    # Create dummy OHLC data
    df = pd.DataFrame({
        'open': [100] * 200,
        'high': [110] * 200,
        'low': [90] * 200,
        'close': [100] * 200,
        'volume': [1000] * 200
    })
    
    # Params DIFFERENT from previous test
    tenkan = 10
    kijun = 30
    senkou = 60
    
    print(f"Calculating Ichimoku with tenkan={tenkan}, kijun={kijun}, senkou={senkou}")
    
    # Direct function call approach
    ichimoku_tuple = ta.ichimoku(df['high'], df['low'], df['close'], tenkan=tenkan, kijun=kijun, senkou=senkou)
    
    print("\n--- Result Structure ---")
    if isinstance(ichimoku_tuple, tuple):
        print(f"Result is a tuple of length {len(ichimoku_tuple)}")
        for i, item in enumerate(ichimoku_tuple):
            if isinstance(item, pd.DataFrame):
                print(f"Item {i} Columns: {list(item.columns)}")

if __name__ == "__main__":
    debug_ichimoku()
