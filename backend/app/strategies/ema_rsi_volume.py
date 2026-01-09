import pandas as pd
import pandas_ta as ta
import logging

logger = logging.getLogger(__name__)

class EmaRsiVolumeStrategy:
    """
    EMA 50/200 + RSI + Volume Strategy
    
    The most popular Bitcoin trading strategy that combines:
    - Trend Filter: EMA 200 (only trade in direction of long-term trend)
    - Entry Timing: EMA 50 (enter on pullbacks to fast MA)
    - Momentum Confirmation: RSI (ensure pullback is healthy, not oversold)
    
    Buy Logic:
    - Price above EMA 200 (bullish trend filter)
    - Price crosses above EMA 50 (recovering from pullback)
    - RSI between rsi_min and rsi_max (default 40-50, healthy pullback zone)
    
    Sell Logic:
    - Price crosses below EMA 50 (trend break)
    - OR RSI drops below rsi_min (momentum loss)
    """
    
    def __init__(self, config: dict):
        """
        Initialize EMA RSI Volume strategy.
        
        Args:
            config: Dictionary with parameters:
                - ema_fast: Fast EMA period (default: 50)
                - ema_slow: Slow EMA period (default: 200)
                - rsi_period: RSI calculation period (default: 14)
                - rsi_min: Minimum RSI for buy signal (default: 40)
                - rsi_max: Maximum RSI for buy signal (default: 50)
        """
        self.config = config
        self.name = "EMA_RSI_VOLUME"
        
        # Extract parameters with defaults
        self.ema_fast = config.get('ema_fast', 50)
        self.ema_slow = config.get('ema_slow', 200)
        self.rsi_period = config.get('rsi_period', 14)
        self.rsi_min = config.get('rsi_min', 40)
        self.rsi_max = config.get('rsi_max', 50)
        
        # Convert float to int if needed (from optimization)
        if isinstance(self.ema_fast, float) and self.ema_fast.is_integer():
            self.ema_fast = int(self.ema_fast)
        if isinstance(self.ema_slow, float) and self.ema_slow.is_integer():
            self.ema_slow = int(self.ema_slow)
        if isinstance(self.rsi_period, float) and self.rsi_period.is_integer():
            self.rsi_period = int(self.rsi_period)
        
        logger.info(f"EMA_RSI_VOLUME initialized: ema_fast={self.ema_fast}, ema_slow={self.ema_slow}, "
                   f"rsi_period={self.rsi_period}, rsi_range=[{self.rsi_min}, {self.rsi_max}]")
        
        # Store simulation data for visualization
        self.simulation_data = None
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Generate buy/sell signals based on EMA crossovers and RSI confirmation.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Series with signals: 1 for buy, -1 for sell, 0 for hold
        """
        df_sim = df.copy()
        
        # Calculate EMAs
        df_sim['ema_fast'] = ta.ema(df_sim['close'], length=self.ema_fast)
        df_sim['ema_slow'] = ta.ema(df_sim['close'], length=self.ema_slow)
        
        # Calculate RSI
        df_sim['rsi'] = ta.rsi(df_sim['close'], length=self.rsi_period)
        
        # Initialize signals
        signals = pd.Series(0, index=df_sim.index)
        
        # Trend filter: Only trade when price is above EMA 200
        bullish_trend = df_sim['close'] > df_sim['ema_slow']
        
        # Entry: Price crosses above EMA 50 (pullback recovery)
        # AND RSI is in healthy pullback zone (not oversold)
        price_above_fast = df_sim['close'] > df_sim['ema_fast']
        price_was_below_fast = df_sim['close'].shift(1) <= df_sim['ema_fast'].shift(1)
        pullback_recovery = price_above_fast & price_was_below_fast
        
        rsi_in_range = (df_sim['rsi'] >= self.rsi_min) & (df_sim['rsi'] <= self.rsi_max)
        
        # Buy signal: Trend filter + Pullback recovery + RSI confirmation
        buy_condition = bullish_trend & pullback_recovery & rsi_in_range
        signals[buy_condition] = 1
        
        # Exit Signal 1: Price crosses below EMA 50
        price_below_fast = df_sim['close'] < df_sim['ema_fast']
        price_was_above_fast = df_sim['close'].shift(1) >= df_sim['ema_fast'].shift(1)
        trend_break = price_below_fast & price_was_above_fast
        
        # Exit Signal 2: RSI drops below minimum (momentum loss)
        momentum_loss = df_sim['rsi'] < self.rsi_min
        
        # Sell signal: Trend break OR momentum loss
        sell_condition = trend_break | momentum_loss
        signals[sell_condition] = -1
        
        # Store simulation data for visualization
        self.simulation_data = df_sim
        
        logger.info(f"EMA_RSI_VOLUME generated {buy_condition.sum()} buy signals and {sell_condition.sum()} sell signals")
        
        return signals
