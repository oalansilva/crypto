import pandas as pd
import numpy as np
import talib


def calculate_regime_classification(
    df: pd.DataFrame, sma_period: int = 200, adx_threshold: float = 25.0
) -> pd.DataFrame:
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

    # Ensure necessary columns exist or calculate them when missing.

    # NOTE: The BacktestService is responsible for computing these indicators if they don't exist.
    # Here we just use them.

    close = df["close"]

    # Check for SMA_200 (or similar)
    sma_col = f"SMA_{sma_period}"
    if sma_col not in df.columns:
        # Fallback if upstream does not provide regime-ready columns.
        try:
            sma_series = talib.SMA(close, timeperiod=sma_period)
        except Exception:
            sma_series = close.rolling(window=sma_period).mean()
    else:
        sma_series = df[sma_col]

    # Classify
    conditions = [(close > sma_series), (close < sma_series)]
    choices = ["Bull", "Bear"]

    # If using ADX for Sideways/Trending differentiation (Not explicitly in simple Bull/Bear requirement but good for "Sideways")
    # For now, adhering to Spec: Bull (Price > SMA) vs Bear (Price < SMA)
    # The spec mention "Sideways: Optional refinement". We will stick to Bull/Bear for strict PnL first.

    df["regime"] = np.select(conditions, choices, default="Unknown")

    return df[["regime"]]
