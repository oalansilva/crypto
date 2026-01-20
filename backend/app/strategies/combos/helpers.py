"""
Helper functions for combo strategy logic evaluation.

Provides common trading pattern functions like crossover, crossunder, etc.
"""

import pandas as pd
import numpy as np
from typing import Union


def crossover(series_a: pd.Series, series_b: pd.Series) -> bool:
    """
    Returns True when series_a crosses above series_b.
    
    Args:
        series_a: First series (e.g., fast EMA)
        series_b: Second series (e.g., slow EMA)
    
    Returns:
        True if series_a crossed above series_b in the last candle
    """
    if len(series_a) < 2 or len(series_b) < 2:
        return pd.Series([False] * len(series_a), index=series_a.index)
    
    # Vectorized check
    current = series_a > series_b
    previous = series_a.shift(1) <= series_b.shift(1)
    
    return current & previous


def crossunder(series_a: pd.Series, series_b: pd.Series) -> bool:
    """
    Returns True when series_a crosses below series_b.
    
    Args:
        series_a: First series (e.g., fast EMA)
        series_b: Second series (e.g., slow EMA)
    
    Returns:
        True if series_a crossed below series_b in the last candle
    """
    if len(series_a) < 2 or len(series_b) < 2:
        return pd.Series([False] * len(series_a), index=series_a.index)
    
    # Vectorized check
    current = series_a < series_b
    previous = series_a.shift(1) >= series_b.shift(1)
    
    return current & previous


def above(series_a: pd.Series, series_b: pd.Series, periods: int = 1) -> bool:
    """
    Returns True if series_a > series_b for N consecutive periods.
    
    Args:
        series_a: First series
        series_b: Second series
        periods: Number of consecutive periods to check
    
    Returns:
        True if series_a has been above series_b for the last N periods
    """
    if len(series_a) < periods or len(series_b) < periods:
        return pd.Series([False] * len(series_a), index=series_a.index)
    
    # Vectorized check using rolling min (if min > 0, then all were True)
    # (a > b) gives boolean series (0/1). Rolling min of 1s is 1.
    condition = (series_a > series_b).astype(int)
    return condition.rolling(window=periods).min() == 1


def below(series_a: pd.Series, series_b: pd.Series, periods: int = 1) -> bool:
    """
    Returns True if series_a < series_b for N consecutive periods.
    
    Args:
        series_a: First series
        series_b: Second series
        periods: Number of consecutive periods to check
    
    Returns:
        True if series_a has been below series_b for the last N periods
    """
    if len(series_a) < periods or len(series_b) < periods:
        return pd.Series([False] * len(series_a), index=series_a.index)
    
    # Vectorized check
    condition = (series_a < series_b).astype(int)
    return condition.rolling(window=periods).min() == 1


# Export helper functions for use in logic evaluation
HELPER_FUNCTIONS = {
    'crossover': crossover,
    'crossunder': crossunder,
    'above': above,
    'below': below
}
