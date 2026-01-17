import pandas as pd
import pandas_ta as ta
import numpy as np
import logging

logger = logging.getLogger(__name__)

class FibonacciEmaStrategy:
    """
    Fibonacci (0.5 / 0.618) + EMA 200 Strategy
    
    Professional institutional pullback strategy that combines:
    - Trend Filter: EMA 200 (only trade in direction of long-term trend)
    - Swing Detection: Identify recent swing highs and lows
    - Fibonacci Retracement: Enter on pullbacks to institutional levels (0.5 and 0.618)
    
    Buy Logic:
    - Price above EMA 200 (bullish trend filter)
    - Recent swing high and swing low identified
    - Price retraces to 0.5 or 0.618 Fibonacci level (within tolerance)
    - Price shows bounce confirmation (reversal)
    
    Sell Logic:
    - Price crosses below EMA 200 (trend reversal)
    - OR price reaches swing high (take profit at resistance)
    """
    
    def __init__(self, config: dict):
        """
        Initialize Fibonacci EMA strategy.
        
        Args:
            config: Dictionary with parameters:
                - ema_period: EMA period for trend filter (default: 200)
                - swing_lookback: Bars to look back for swing detection (default: 20)
                - fib_level_1: First Fibonacci retracement level (default: 0.5)
                - fib_level_2: Second Fibonacci retracement level (default: 0.618)
                - level_tolerance: Tolerance for price touching Fibonacci level (default: 0.005 = 0.5%)
        """
        self.config = config
        self.name = "FIBONACCI_EMA"
        
        # Extract parameters with defaults
        self.ema_period = config.get('ema_period', 200)
        self.swing_lookback = config.get('swing_lookback', 20)
        self.fib_level_1 = config.get('fib_level_1', 0.5)
        self.fib_level_2 = config.get('fib_level_2', 0.618)
        self.level_tolerance = config.get('level_tolerance', 0.005)
        
        # Convert float to int if needed (from optimization)
        if isinstance(self.ema_period, float) and self.ema_period.is_integer():
            self.ema_period = int(self.ema_period)
        if isinstance(self.swing_lookback, float) and self.swing_lookback.is_integer():
            self.swing_lookback = int(self.swing_lookback)
        
        logger.info(f"FIBONACCI_EMA initialized: ema_period={self.ema_period}, swing_lookback={self.swing_lookback}, "
                   f"fib_levels=[{self.fib_level_1}, {self.fib_level_2}], tolerance={self.level_tolerance}")
        
        # Store simulation data for visualization
        self.simulation_data = None
    
    def _detect_swings(self, df: pd.DataFrame) -> tuple:
        """
        Detect swing highs and swing lows using vectorized rolling window operations.
        
        A swing high is a local maximum where the price is higher than
        all bars in the lookback window before and after it.
        
        A swing low is a local minimum where the price is lower than
        all bars in the lookback window before and after it.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            tuple: (swing_highs_series, swing_lows_series, swing_high_prices, swing_low_prices)
        """
        lookback = self.swing_lookback
        window_size = lookback * 2 + 1  # Total window: lookback before + current + lookback after
        
        # Vectorized swing high detection
        # A swing high is where the high equals the rolling max over the centered window
        rolling_max = df['high'].rolling(window=window_size, center=True, min_periods=window_size).max()
        swing_highs = (df['high'] == rolling_max) & (df['high'].notna())
        swing_high_prices = df['high'].where(swing_highs, np.nan)
        
        # Vectorized swing low detection
        # A swing low is where the low equals the rolling min over the centered window
        rolling_min = df['low'].rolling(window=window_size, center=True, min_periods=window_size).min()
        swing_lows = (df['low'] == rolling_min) & (df['low'].notna())
        swing_low_prices = df['low'].where(swing_lows, np.nan)
        
        return swing_highs, swing_lows, swing_high_prices, swing_low_prices
    
    def _calculate_fibonacci_levels(self, swing_high: float, swing_low: float) -> dict:
        """
        Calculate Fibonacci retracement levels.
        
        Args:
            swing_high: Recent swing high price
            swing_low: Recent swing low price
            
        Returns:
            dict: Fibonacci levels with their prices
        """
        price_range = swing_high - swing_low
        
        return {
            'swing_high': swing_high,
            'swing_low': swing_low,
            'fib_level_1': swing_low + (price_range * self.fib_level_1),
            'fib_level_2': swing_low + (price_range * self.fib_level_2),
            'range': price_range
        }
    
    def _is_at_fib_level(self, price: float, fib_level: float) -> bool:
        """
        Check if price is within tolerance of a Fibonacci level.
        
        Args:
            price: Current price
            fib_level: Fibonacci level to check
            
        Returns:
            bool: True if price is at the Fibonacci level (within tolerance)
        """
        if pd.isna(fib_level) or fib_level == 0:
            return False
        
        # Calculate percentage difference
        diff_pct = abs(price - fib_level) / price
        
        return diff_pct <= self.level_tolerance
    
    def _detect_bounce(self, df: pd.DataFrame, index: int) -> bool:
        """
        Detect if price is bouncing (reversing) at current bar.
        
        Bounce confirmation:
        - Current candle closes higher than it opened (bullish candle)
        - OR current close > previous close (upward momentum)
        
        Args:
            df: DataFrame with OHLCV data
            index: Current bar index
            
        Returns:
            bool: True if bounce is detected
        """
        if index < 1:
            return False
        
        current = df.iloc[index]
        previous = df.iloc[index - 1]
        
        # Bullish candle (close > open)
        bullish_candle = current['close'] > current['open']
        
        # Upward momentum (close > previous close)
        upward_momentum = current['close'] > previous['close']
        
        return bullish_candle or upward_momentum
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Generate buy/sell signals based on Fibonacci retracement and EMA trend filter.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Series with signals: 1 for buy, -1 for sell, 0 for hold
        """
        df_sim = df.copy()
        
        # Calculate EMA 200
        df_sim['ema'] = ta.ema(df_sim['close'], length=self.ema_period)
        
        # Detect swing points
        swing_highs, swing_lows, swing_high_prices, swing_low_prices = self._detect_swings(df_sim)
        
        # Store swing data for visualization
        df_sim['swing_high'] = swing_high_prices
        df_sim['swing_low'] = swing_low_prices
        
        # Initialize Fibonacci level columns
        df_sim['fib_level_1'] = np.nan
        df_sim['fib_level_2'] = np.nan
        df_sim['current_swing_high'] = np.nan
        df_sim['current_swing_low'] = np.nan
        
        # Vectorized: Forward fill swing high and low prices to get "last known" values
        df_sim['current_swing_high'] = swing_high_prices.ffill()
        df_sim['current_swing_low'] = swing_low_prices.ffill()
        
        # Vectorized: Calculate Fibonacci levels for all rows at once
        # Only calculate where we have both swing high and low, and high > low
        valid_swings = (df_sim['current_swing_high'].notna() & 
                       df_sim['current_swing_low'].notna() & 
                       (df_sim['current_swing_high'] > df_sim['current_swing_low']))
        
        price_range = df_sim['current_swing_high'] - df_sim['current_swing_low']
        df_sim.loc[valid_swings, 'fib_level_1'] = df_sim.loc[valid_swings, 'current_swing_low'] + (price_range[valid_swings] * self.fib_level_1)
        df_sim.loc[valid_swings, 'fib_level_2'] = df_sim.loc[valid_swings, 'current_swing_low'] + (price_range[valid_swings] * self.fib_level_2)
        
        # Initialize signals
        signals = pd.Series(0, index=df_sim.index)
        
        # Vectorized: Calculate bounce detection for all rows
        # Bounce = bullish candle OR upward momentum
        bullish_candle = df_sim['close'] > df_sim['open']
        upward_momentum = df_sim['close'] > df_sim['close'].shift(1)
        bounce_detected = bullish_candle | upward_momentum
        
        # Vectorized: Check if price is at Fibonacci levels
        # Calculate percentage difference from fib levels
        diff_fib1_pct = (df_sim['close'] - df_sim['fib_level_1']).abs() / df_sim['close']
        diff_fib2_pct = (df_sim['close'] - df_sim['fib_level_2']).abs() / df_sim['close']
        
        at_fib_1 = (diff_fib1_pct <= self.level_tolerance) & df_sim['fib_level_1'].notna()
        at_fib_2 = (diff_fib2_pct <= self.level_tolerance) & df_sim['fib_level_2'].notna()
        at_fib_level = at_fib_1 | at_fib_2
        
        # Vectorized: Generate buy signals
        # Conditions: price > EMA AND at fib level AND bounce detected
        buy_conditions = (
            (df_sim['close'] > df_sim['ema']) &  # Trend filter
            df_sim['ema'].notna() &  # EMA calculated
            at_fib_level &  # At Fibonacci level
            bounce_detected  # Bounce confirmation
        )
        signals[buy_conditions] = 1
        
        # Vectorized: Generate sell signals
        # Sell Signal 1: Price crosses below EMA 200
        prev_price = df_sim['close'].shift(1)
        prev_ema = df_sim['ema'].shift(1)
        cross_below_ema = (prev_price >= prev_ema) & (df_sim['close'] < df_sim['ema']) & df_sim['ema'].notna()
        
        # Sell Signal 2: Price reaches swing high (take profit)
        at_swing_high = (df_sim['close'] >= df_sim['current_swing_high']) & df_sim['current_swing_high'].notna()
        
        sell_conditions = cross_below_ema | at_swing_high
        signals[sell_conditions] = -1
        
        # Store simulation data for visualization
        self.simulation_data = df_sim
        
        buy_count = (signals == 1).sum()
        sell_count = (signals == -1).sum()
        logger.info(f"FIBONACCI_EMA generated {buy_count} buy signals and {sell_count} sell signals")
        
        return signals
