"""
Base ComboStrategy class for multi-indicator strategies.

This class provides the foundation for combo strategies that combine
multiple indicators with custom entry/exit logic.
"""

import pandas as pd
import pandas_ta as ta
import numpy as np
from typing import Dict, List, Any, Optional
import re
from .helpers import HELPER_FUNCTIONS


class ComboStrategy:
    """
    Base class for combo strategies that combine multiple indicators.
    
    Supports:
    - Multiple instances of the same indicator
    - Indicator aliases for clear logic
    - Custom entry/exit logic evaluation
    - Helper functions (crossover, crossunder, etc.)
    """
    
    def __init__(
        self,
        indicators: List[Dict[str, Any]],
        entry_logic: str,
        exit_logic: str,
        stop_loss: float = 0.015,
        stop_gain: Optional[float] = None
    ):
        """
        Initialize combo strategy.
        
        Args:
            indicators: List of indicator configs with type, alias, and params
            entry_logic: Entry logic expression (e.g., "(close > fast) AND (RSI < 30)")
            exit_logic: Exit logic expression
            stop_loss: Stop loss percentage (default 1.5%)
            stop_gain: Stop gain percentage (optional)
        """
        self.indicators = indicators
        self.entry_logic = entry_logic
        self.exit_logic = exit_logic
        self.stop_loss = stop_loss
        self.stop_gain = stop_gain
        
        self._indicator_cache = {}
        self._validate_aliases()
    
    def _validate_aliases(self):
        """Validate that all aliases are unique."""
        aliases = [ind.get('alias') for ind in self.indicators if ind.get('alias')]
        if len(aliases) != len(set(aliases)):
            duplicates = [a for a in aliases if aliases.count(a) > 1]
            raise ValueError(f"Duplicate aliases found: {set(duplicates)}")
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all indicators and add them to the dataframe.
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            DataFrame with calculated indicators
        """
        # Check cache
        if 'calculated' in self._indicator_cache:
            return self._indicator_cache['calculated'].copy()
        
        df = df.copy()
        
        for indicator in self.indicators:
            ind_type = indicator['type'].lower()
            params = indicator.get('params', {})
            alias = indicator.get('alias')
            
            try:
                if ind_type == 'ema':
                    length = params.get('length', 9)
                    col_name = alias if alias else f'EMA_{length}'
                    df[col_name] = ta.ema(df['close'], length=length)
                
                elif ind_type == 'sma':
                    length = params.get('length', 20)
                    col_name = alias if alias else f'SMA_{length}'
                    df[col_name] = ta.sma(df['close'], length=length)
                
                elif ind_type == 'rsi':
                    length = params.get('length', 14)
                    col_name = f'RSI_{length}'
                    df[col_name] = ta.rsi(df['close'], length=length)
                
                elif ind_type == 'macd':
                    fast = params.get('fast', 12)
                    slow = params.get('slow', 26)
                    signal = params.get('signal', 9)
                    alias_prefix = alias if alias else 'MACD'
                    
                    macd_result = ta.macd(df['close'], fast=fast, slow=slow, signal=signal)
                    df[f'{alias_prefix}_macd'] = macd_result[f'MACD_{fast}_{slow}_{signal}']
                    df[f'{alias_prefix}_signal'] = macd_result[f'MACDs_{fast}_{slow}_{signal}']
                    df[f'{alias_prefix}_histogram'] = macd_result[f'MACDh_{fast}_{slow}_{signal}']
                
                elif ind_type == 'bbands' or ind_type == 'bollinger':
                    length = params.get('length', 20)
                    std = params.get('std', 2)
                    alias_prefix = alias if alias else 'BB'
                    
                    bbands_result = ta.bbands(df['close'], length=length, std=std)
                    # Handle potential column name variations (e.g. with .0 suffix)
                    cols = bbands_result.columns.tolist()
                    lower_col = next(c for c in cols if c.startswith(f'BBL_{length}_{std}'))
                    mid_col = next(c for c in cols if c.startswith(f'BBM_{length}_{std}'))
                    upper_col = next(c for c in cols if c.startswith(f'BBU_{length}_{std}'))
                    
                    df[f'{alias_prefix}_upper'] = bbands_result[upper_col]
                    df[f'{alias_prefix}_middle'] = bbands_result[mid_col]
                    df[f'{alias_prefix}_lower'] = bbands_result[lower_col]
                
                elif ind_type == 'atr':
                    length = params.get('length', 14)
                    col_name = f'ATR_{length}'
                    df[col_name] = ta.atr(df['high'], df['low'], df['close'], length=length)
                
                elif ind_type == 'adx':
                    length = params.get('length', 14)
                    col_name = f'ADX_{length}'
                    adx_result = ta.adx(df['high'], df['low'], df['close'], length=length)
                    df[col_name] = adx_result[f'ADX_{length}']
                
                elif ind_type == 'volume_sma':
                    length = params.get('length', 20)
                    col_name = alias if alias else f'VOL_SMA_{length}'
                    df[col_name] = ta.sma(df['volume'], length=length)
            
            except Exception as e:
                raise RuntimeError(f"Error calculating {ind_type}: {str(e)}")
        
        # Cache the result
        self._indicator_cache['calculated'] = df.copy()
        
        return df
    
    def _evaluate_logic(self, df: pd.DataFrame, logic: str, row_idx: int) -> bool:
        """
        Evaluate entry/exit logic for a specific row.
        
        Args:
            df: DataFrame with indicators
            logic: Logic expression to evaluate (must use & and | instead of and/or)
            row_idx: Row index to evaluate
        
        Returns:
            True if logic evaluates to True, False otherwise
        """
        try:
            # Create local context with helper functions
            local_context = HELPER_FUNCTIONS.copy()
            
            # Add all dataframe columns as Series up to current row
            for col in df.columns:
                if row_idx < len(df):
                    local_context[col] = df[col].iloc[:row_idx+1]
            
            # Evaluate the logic
            result = eval(logic, {"__builtins__": {}}, local_context)
            
            # If result is a Series, get the last value
            if isinstance(result, pd.Series):
                return bool(result.iloc[-1]) if len(result) > 0 else False
            
            return bool(result)
        
        except Exception as e:
            raise RuntimeError(f"Error evaluating logic '{logic}': {str(e)}")
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate buy/sell signals based on entry/exit logic AND stop loss.
        
        CRITICAL: Signals are generated AFTER candle close confirmation (TradingView style).
        - Crossover detected on day N → Signal applied on day N+1
        - This ensures we only trade on confirmed crossovers after candle close
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            DataFrame with 'signal' column (1=buy, -1=sell, 0=hold)
        """
        # Use empty check
        if df.empty:
            df['signal'] = 0
            return df

        # Calculate indicators
        df = self.calculate_indicators(df)
        
        # Initialize signal column
        df['signal'] = 0
        
        # Track position state for stop loss simulation
        in_position = False
        entry_price = None
        pending_entry = False  # Flag for confirmed entry on next candle
        pending_exit = False   # Flag for confirmed exit on next candle
        
        # Evaluate logic for each row WITH stop loss simulation and confirmed signals
        for i in range(len(df)):
            try:
                current_price = df.iloc[i]['close']
                
                # CRITICAL: Check stop loss FIRST before any other signals
                # This ensures stop loss has priority over pending exit signals
                if in_position and entry_price is not None:
                    # Check if LOW dropped below stop price (intra-candle stop)
                    # We use LOW because a wick can trigger stop loss even if close is higher
                    current_low = df.iloc[i]['low']
                    low_pnl = (current_low - entry_price) / entry_price
                    
                    if low_pnl <= -self.stop_loss:
                        # Stop loss hit - immediate sell signal (no confirmation needed)
                        df.loc[df.index[i], 'signal'] = -1
                        in_position = False
                        entry_price = None
                        pending_exit = False  # Cancel any pending exit
                        continue
                
                # Apply pending signals (from previous candle's confirmation)
                if pending_entry and not in_position:
                    df.loc[df.index[i], 'signal'] = 1
                    in_position = True
                    entry_price = current_price
                    pending_entry = False
                    continue  # Don't check other conditions this candle
                
                if pending_exit and in_position:
                    df.loc[df.index[i], 'signal'] = -1
                    in_position = False
                    entry_price = None
                    pending_exit = False
                    continue  # Don't check other conditions this candle
                
                # Check for crossovers/conditions on current candle
                # If detected, set pending flag for NEXT candle
                if i > 0:  # Need previous candle for crossover detection
                    # Check entry logic (only if not in position)
                    if not in_position and self._evaluate_logic(df, self.entry_logic, i):
                        # Crossover detected - set pending entry for next candle
                        pending_entry = True
                    
                    # Check exit logic (only if in position)
                    elif in_position and self._evaluate_logic(df, self.exit_logic, i):
                        # Exit condition detected - set pending exit for next candle
                        pending_exit = True
            
            except Exception as e:
                # Log error but continue
                print(f"Warning: Error at row {i}: {str(e)}")
                continue
        
        return df
    
    def get_indicator_columns(self) -> List[str]:
        """
        Get list of indicator column names for chart visualization.
        
        Returns:
            List of column names
        """
        columns = []
        
        for indicator in self.indicators:
            ind_type = indicator['type'].lower()
            params = indicator.get('params', {})
            alias = indicator.get('alias')
            
            if ind_type in ['ema', 'sma']:
                length = params.get('length', 9 if ind_type == 'ema' else 20)
                columns.append(alias if alias else f'{ind_type.upper()}_{length}')
            
            elif ind_type == 'rsi':
                length = params.get('length', 14)
                columns.append(f'RSI_{length}')
            
            elif ind_type == 'macd':
                alias_prefix = alias if alias else 'MACD'
                columns.extend([
                    f'{alias_prefix}_macd',
                    f'{alias_prefix}_signal',
                    f'{alias_prefix}_histogram'
                ])
            
            elif ind_type in ['bbands', 'bollinger']:
                alias_prefix = alias if alias else 'BB'
                columns.extend([
                    f'{alias_prefix}_upper',
                    f'{alias_prefix}_middle',
                    f'{alias_prefix}_lower'
                ])
            
            elif ind_type == 'atr':
                length = params.get('length', 14)
                columns.append(f'ATR_{length}')
            
            elif ind_type == 'adx':
                length = params.get('length', 14)
                columns.append(f'ADX_{length}')
            
            elif ind_type == 'volume_sma':
                length = params.get('length', 20)
                columns.append(alias if alias else f'VOL_SMA_{length}')
        
        return columns
