
import pandas as pd
import numpy as np

def calculate_regime_classification(df: pd.DataFrame, sma_period: int = 200, adx_threshold: float = 25.0) -> pd.DataFrame:
    """
    Classify market regime based on SMA 200 and ADX.
    
    Regimes:
    - Bull: Price > SMA200
    - Bear: Price < SMA200
    - Sideways (Optional refinement for future): ADX < Threshold
    
    Returns a DataFrame with 'regime' column.
    """
    if df.empty:
        return df
    
    # Ensure we are working with a copy to avoid SettingWithCopyWarning
    df = df.copy()
    
    # Ensure necessary columns exist or calculate them (simplification: assume they exist or are passed)
    # Ideally, this function receives a DF that *already* has the indicators computed 
    # to avoid re-calculation overhead if BacktestService did it.
    # But for robustness, we check.
    
    # NOTE: The BacktestService is responsible for computing these indicators if they don't exist.
    # Here we just use them.
    
    close = df['close']
    
    # Check for SMA_200 (or similar)
    sma_col = f'SMA_{sma_period}'
    if sma_col not in df.columns:
        # Fallback if not computed (should not happen with updated service)
        # Assuming we can't easily compute it here without pandas_ta import overhead or dependency
        # We will assume it's passed or try to use a generic 'sma' if available?
        # For now, let's assume strict requirement: Caller provides SMA column.
        # But to be safe, we can try to compute it simple:
        sma_series = close.rolling(window=sma_period).mean()
    else:
        sma_series = df[sma_col]
        
    # Classify
    conditions = [
        (close > sma_series),
        (close < sma_series)
    ]
    choices = ['Bull', 'Bear']
    
    # If using ADX for Sideways/Trending differentiation (Not explicitly in simple Bull/Bear requirement but good for "Sideways")
    # For now, adhering to Spec: Bull (Price > SMA) vs Bear (Price < SMA)
    # The spec mention "Sideways: Optional refinement". We will stick to Bull/Bear for strict PnL first.
    
    df['regime'] = np.select(conditions, choices, default='Unknown')
    
    return df[['regime']]
