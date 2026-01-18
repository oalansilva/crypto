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
        return False
    
    current = series_a.iloc[-1] > series_b.iloc[-1]
    previous = series_a.iloc[-2] <= series_b.iloc[-2]
    
    return current and previous


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
        return False
    
    current = series_a.iloc[-1] < series_b.iloc[-1]
    previous = series_a.iloc[-2] >= series_b.iloc[-2]
    
    return current and previous


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
        return False
    
    return all(series_a.iloc[-periods:] > series_b.iloc[-periods:])


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
        return False
    
    return all(series_a.iloc[-periods:] < series_b.iloc[-periods:])


# Export helper functions for use in logic evaluation
HELPER_FUNCTIONS = {
    'crossover': crossover,
    'crossunder': crossunder,
    'above': above,
    'below': below
}
