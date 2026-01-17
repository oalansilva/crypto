
import pandas as pd
import pandas_ta as ta
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)

def debug_ichimoku():
    print("Creating dummy data...")
    # Create dummy OHLC data (enough rows for Ichimoku 52 period)
    df = pd.DataFrame({
        'open': [100] * 100,
        'high': [110] * 100,
        'low': [90] * 100,
        'close': [100] * 100,
        'volume': [1000] * 100
    })
    
    # Params
    tenkan = 9
    kijun = 26
    senkou = 52
    
    print(f"Calculating Ichimoku with tenkan={tenkan}, kijun={kijun}, senkou={senkou}")
    
    # Calculate Ichimoku using pandas_ta strategy style (as used in dynamic_strategy)
    # OR direct call similar to dynamic_strategy use:
    # indicator_func(high=df_sim['high'], low=df_sim['low'], close=df_sim['close'], **converted_params)
    
    # Direct function call approach
    ichimoku_tuple = ta.ichimoku(df['high'], df['low'], df['close'], tenkan=tenkan, kijun=kijun, senkou=senkou)
    
    print("\n--- Result Structure ---")
    if isinstance(ichimoku_tuple, tuple):
        print(f"Result is a tuple of length {len(ichimoku_tuple)}")
        for i, item in enumerate(ichimoku_tuple):
            print(f"\nItem {i} Type: {type(item)}")
            if isinstance(item, pd.DataFrame):
                print(f"Item {i} Columns: {list(item.columns)}")
                
    else:
        print(f"Result type: {type(ichimoku_tuple)}")
        if isinstance(ichimoku_tuple, pd.DataFrame):
            print(f"Columns: {list(ichimoku_tuple.columns)}")

if __name__ == "__main__":
    debug_ichimoku()
