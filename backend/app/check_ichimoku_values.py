
import pandas as pd
import pandas_ta as ta
import numpy as np

def check_ichimoku_sensitivity():
    print("Creating dummy data...")
    # Create random but deterministic data
    np.random.seed(42)
    close = np.random.randn(200).cumsum() + 100
    high = close + 2
    low = close - 2
    
    df = pd.DataFrame({
        'open': close,
        'high': high,
        'low': low,
        'close': close,
        'volume': 1000
    })
    
    # Test 1: senkou=52
    print("Calculating senkou=52...")
    res1, _ = ta.ichimoku(df['high'], df['low'], df['close'], tenkan=9, kijun=26, senkou=52)
    isb1 = res1['ISB_26']
    
    # Test 2: senkou=60
    print("Calculating senkou=60...")
    res2, _ = ta.ichimoku(df['high'], df['low'], df['close'], tenkan=9, kijun=26, senkou=60)
    isb2 = res2['ISB_26']
    
    # Compare
    diff = (isb1 - isb2).abs().sum()
    print(f"\nDifference sum between ISB(52) and ISB(60): {diff}")
    
    if diff == 0:
        print("CRITICAL: ISB values are IDENTICAL! 'senkou' parameter is being IGNORED!")
    else:
        print("SUCCESS: ISB values are different. 'senkou' parameter is working.")

if __name__ == "__main__":
    check_ichimoku_sensitivity()
