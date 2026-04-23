import pandas as pd
import talib


def calculate_avg_indicators(df: pd.DataFrame) -> dict:
    """
    Calculate the average value of ATR and ADX over the period.
    """
    if df.empty:
        return {"avg_atr": 0.0, "avg_adx": 0.0}

    avg_atr = 0.0
    avg_adx = 0.0

    # TA-Lib convention for rolling averages uses ATR_14 and ADX_14.
    atr_cols = [c for c in df.columns if c.startswith("ATR")]
    if atr_cols:
        avg_atr = df[atr_cols[0]].mean()

    adx_cols = [c for c in df.columns if c.startswith("ADX")]
    if adx_cols:
        avg_adx = df[adx_cols[0]].mean()

    return {"avg_atr": float(avg_atr), "avg_adx": float(avg_adx)}


def ensure_ta_lib_context_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure common context indicators exist on the DataFrame, using TA-Lib.
    Adds columns only when missing:
    - ATR_14
    - ADX_14
    - SMA_50
    - SMA_200
    """
    if df is None or df.empty:
        return df

    close = pd.to_numeric(df["close"], errors="coerce")
    high = pd.to_numeric(df["high"], errors="coerce")
    low = pd.to_numeric(df["low"], errors="coerce")

    try:
        if "ATR_14" not in df.columns:
            df["ATR_14"] = talib.ATR(high, low, close, timeperiod=14)
        if "ADX_14" not in df.columns:
            df["ADX_14"] = talib.ADX(high, low, close, timeperiod=14)
        if "SMA_50" not in df.columns:
            df["SMA_50"] = talib.SMA(close, timeperiod=50)
        if "SMA_200" not in df.columns:
            df["SMA_200"] = talib.SMA(close, timeperiod=200)
    except Exception:
        return df

    return df
