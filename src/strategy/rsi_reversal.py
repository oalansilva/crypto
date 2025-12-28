import pandas as pd
import numpy as np
from src.strategy.base import Strategy

class RSIReversalStrategy(Strategy):
    def __init__(self, rsi_period=14, oversold=30, overbought=70):
        super().__init__(rsi_period=rsi_period, oversold=oversold, overbought=overbought)
        self.rsi_period = rsi_period
        self.oversold = oversold
        self.overbought = overbought

    def _calculate_rsi(self, series, period):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)
        
        avg_gain = gain.rolling(window=period, min_periods=period).mean()
        avg_loss = loss.rolling(window=period, min_periods=period).mean()
        
        # Using Wilder's Smoothing would be more standard but rolling mean is acceptable for simple backtest
        # Or implement Wilder's:
        # avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
        # avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
        # Let's use EWM for better accuracy with standard RSI
        
        avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        df = df.copy()
        
        # Calculate RSI
        df['rsi'] = self._calculate_rsi(df['close'], self.rsi_period)
        
        df['signal'] = 0
        
        prev_rsi = df['rsi'].shift(1)
        
        # Buy: Crosses ABOVE oversold (recovering)
        # Meaning: Was below 30, now above 30
        buy_cond = (prev_rsi < self.oversold) & (df['rsi'] >= self.oversold)
        
        # Sell: Crosses BELOW overbought (reversing down)
        # Meaning: Was above 70, now below 70
        sell_cond = (prev_rsi > self.overbought) & (df['rsi'] <= self.overbought)
        
        df.loc[buy_cond, 'signal'] = 1
        df.loc[sell_cond, 'signal'] = -1
        
        return df['signal']
