import pandas as pd
from src.strategy.base import Strategy

class SMACrossStrategy(Strategy):
    def __init__(self, fast=20, slow=50):
        super().__init__(fast=fast, slow=slow)
        self.fast = fast
        self.slow = slow

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        df = df.copy()
        # Calculate Indicators
        df['sma_fast'] = df['close'].rolling(window=self.fast).mean()
        df['sma_slow'] = df['close'].rolling(window=self.slow).mean()
        
        # Initialize signals
        df['signal'] = 0
        
        # Detect Crossovers
        # Buy: Fast crosses ABOVE Slow
        # Sell: Fast crosses BELOW Slow
        
        # Logic:
        # prev_fast < prev_slow AND curr_fast > curr_slow => BUY
        # prev_fast > prev_slow AND curr_fast < curr_slow => SELL
        
        prev_fast = df['sma_fast'].shift(1)
        prev_slow = df['sma_slow'].shift(1)
        
        # Buyers
        buy_cond = (prev_fast <= prev_slow) & (df['sma_fast'] > df['sma_slow'])
        
        # Sellers
        sell_cond = (prev_fast >= prev_slow) & (df['sma_fast'] < df['sma_slow'])
        
        df.loc[buy_cond, 'signal'] = 1
        df.loc[sell_cond, 'signal'] = -1
        
        # Return the full dataframe with indicators and signal
        # We perform a forward fill to handle NaN values at the beginning (though for backtest logic, strict NaN handling might be better, for viz it's fine)
        # Actually, let's just return the columns we need.
        return df[['sma_fast', 'sma_slow', 'signal']]
