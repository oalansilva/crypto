import pandas as pd
from src.strategy.base import Strategy

class BBMeanReversionStrategy(Strategy):
    def __init__(self, bb_period=20, bb_std=2.0, exit_mode='mid'):
        super().__init__(bb_period=bb_period, bb_std=bb_std, exit_mode=exit_mode)
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.exit_mode = exit_mode # 'mid' or 'upper'

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        # Calculate Bollinger Bands
        # Middle Band = SMA(20)
        df['bb_middle'] = df['close'].rolling(window=self.bb_period).mean()
        df['bb_std'] = df['close'].rolling(window=self.bb_period).std()
        df['bb_upper'] = df['bb_middle'] + (self.bb_std * df['bb_std'])
        df['bb_lower'] = df['bb_middle'] - (self.bb_std * df['bb_std'])
        
        df['signal'] = 0
        
        # Buy: Close < Lower Band
        # Strictly speaking, "closes below". 
        # Some mean reversion strategies buy as soon as it touches, or when it crosses back up.
        # "BUY quando close fecha abaixo da banda inferior" -> Buy immediately on the close that is below.
        buy_cond = df['close'] < df['bb_lower']
        
        # Sell: Close > Middle Band (or Upper)
        if self.exit_mode == 'upper':
            sell_cond = df['close'] > df['bb_upper']
        else: # default 'mid'
            sell_cond = df['close'] > df['bb_middle']
            
        df.loc[buy_cond, 'signal'] = 1
        df.loc[sell_cond, 'signal'] = -1
        
        # Return DataFrame with bollinger bands and signal columns
        return df[['bb_upper', 'bb_middle', 'bb_lower', 'signal']]
