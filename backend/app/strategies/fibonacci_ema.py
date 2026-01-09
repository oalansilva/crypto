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
        Detect swing highs and swing lows using rolling window.
        
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
        
        # Initialize series
        swing_highs = pd.Series(False, index=df.index)
        swing_lows = pd.Series(False, index=df.index)
        swing_high_prices = pd.Series(np.nan, index=df.index)
        swing_low_prices = pd.Series(np.nan, index=df.index)
        
        # Detect swing highs (local maxima)
        for i in range(lookback, len(df) - lookback):
            current_high = df['high'].iloc[i]
            
            # Check if current is higher than all bars in lookback window (before and after)
            window_before = df['high'].iloc[i-lookback:i]
            window_after = df['high'].iloc[i+1:i+lookback+1]
            
            if len(window_before) > 0 and len(window_after) > 0:
                if (current_high > window_before.max()) and (current_high > window_after.max()):
                    swing_highs.iloc[i] = True
                    swing_high_prices.iloc[i] = current_high
        
        # Detect swing lows (local minima)
        for i in range(lookback, len(df) - lookback):
            current_low = df['low'].iloc[i]
            
            # Check if current is lower than all bars in lookback window (before and after)
            window_before = df['low'].iloc[i-lookback:i]
            window_after = df['low'].iloc[i+1:i+lookback+1]
            
            if len(window_before) > 0 and len(window_after) > 0:
                if (current_low < window_before.min()) and (current_low < window_after.min()):
                    swing_lows.iloc[i] = True
                    swing_low_prices.iloc[i] = current_low
        
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
        
        # Track most recent swing high and low for Fibonacci calculation
        last_swing_high = None
        last_swing_low = None
        
        # Calculate Fibonacci levels dynamically as swings are detected
        for i in range(len(df_sim)):
            # Update last swing high if new one detected
            if swing_highs.iloc[i]:
                last_swing_high = swing_high_prices.iloc[i]
            
            # Update last swing low if new one detected
            if swing_lows.iloc[i]:
                last_swing_low = swing_low_prices.iloc[i]
            
            # Calculate Fibonacci levels if we have both swing high and low
            if last_swing_high is not None and last_swing_low is not None and last_swing_high > last_swing_low:
                fib_levels = self._calculate_fibonacci_levels(last_swing_high, last_swing_low)
                df_sim.loc[df_sim.index[i], 'fib_level_1'] = fib_levels['fib_level_1']
                df_sim.loc[df_sim.index[i], 'fib_level_2'] = fib_levels['fib_level_2']
                df_sim.loc[df_sim.index[i], 'current_swing_high'] = last_swing_high
                df_sim.loc[df_sim.index[i], 'current_swing_low'] = last_swing_low
        
        # Forward fill Fibonacci levels (they remain valid until new swing)
        df_sim['fib_level_1'] = df_sim['fib_level_1'].ffill()
        df_sim['fib_level_2'] = df_sim['fib_level_2'].ffill()
        df_sim['current_swing_high'] = df_sim['current_swing_high'].ffill()
        df_sim['current_swing_low'] = df_sim['current_swing_low'].ffill()
        
        # Initialize signals
        signals = pd.Series(0, index=df_sim.index)
        
        # Generate buy signals
        for i in range(1, len(df_sim)):
            current_price = df_sim['close'].iloc[i]
            ema_value = df_sim['ema'].iloc[i]
            fib_1 = df_sim['fib_level_1'].iloc[i]
            fib_2 = df_sim['fib_level_2'].iloc[i]
            
            # Skip if EMA not calculated yet or no Fibonacci levels
            if pd.isna(ema_value) or pd.isna(fib_1):
                continue
            
            # Trend filter: Only buy if price above EMA 200
            if current_price > ema_value:
                # Check if price is at Fibonacci level 1 or 2
                at_fib_1 = self._is_at_fib_level(current_price, fib_1)
                at_fib_2 = self._is_at_fib_level(current_price, fib_2)
                
                if at_fib_1 or at_fib_2:
                    # Check for bounce confirmation
                    if self._detect_bounce(df_sim, i):
                        signals.iloc[i] = 1
        
        # Generate sell signals
        for i in range(1, len(df_sim)):
            current_price = df_sim['close'].iloc[i]
            prev_price = df_sim['close'].iloc[i-1]
            ema_value = df_sim['ema'].iloc[i]
            prev_ema = df_sim['ema'].iloc[i-1]
            swing_high = df_sim['current_swing_high'].iloc[i]
            
            # Skip if EMA not calculated yet
            if pd.isna(ema_value) or pd.isna(prev_ema):
                continue
            
            # Sell Signal 1: Price crosses below EMA 200 (trend reversal)
            if prev_price >= prev_ema and current_price < ema_value:
                signals.iloc[i] = -1
            
            # Sell Signal 2: Price reaches swing high (take profit)
            elif not pd.isna(swing_high) and current_price >= swing_high:
                signals.iloc[i] = -1
        
        # Store simulation data for visualization
        self.simulation_data = df_sim
        
        buy_count = (signals == 1).sum()
        sell_count = (signals == -1).sum()
        logger.info(f"FIBONACCI_EMA generated {buy_count} buy signals and {sell_count} sell signals")
        
        return signals
