
import pandas as pd

def calculate_avg_indicators(df: pd.DataFrame) -> dict:
    """
    Calculate the average value of ATR and ADX over the period.
    """
    if df.empty:
        return {'avg_atr': 0.0, 'avg_adx': 0.0}
    
    avg_atr = 0.0
    avg_adx = 0.0
    
    # Check for ATR columns (pandas_ta usually names them ATR_14 or similar)
    # We search for any column starting with ATRe or ATR
    atr_cols = [c for c in df.columns if c.startswith('ATR')]
    if atr_cols:
        # Take the first one found (usually the standard one used)
        avg_atr = df[atr_cols[0]].mean()
    
    # Check for ADX columns
    adx_cols = [c for c in df.columns if c.startswith('ADX')]
    if adx_cols:
        avg_adx = df[adx_cols[0]].mean()
        
    return {
        'avg_atr': float(avg_atr),
        'avg_adx': float(avg_adx)
    }
