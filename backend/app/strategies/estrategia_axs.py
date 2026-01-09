import pandas as pd
import pandas_ta as ta
import logging

logger = logging.getLogger(__name__)

class EstrategiaAXS:
    """
    ESTRATEGIAAXS - Moving Average Crossover Strategy
    
    Based on Pine Script logic:
    - Uses 3 moving averages: EMA (short), SMA (long), SMA (intermediate)
    - Buy: (Short > Long) AND (Crossover(Short, Long) OR Crossover(Short, Intermediate))
    - Sell: Crossunder(Short, Intermediate)
    """
    
    def __init__(self, config: dict):
        """
        Initialize ESTRATEGIAAXS strategy.
        
        Args:
            config: Dictionary with parameters:
                - media_curta: EMA period (default: 6)
                - media_longa: SMA period (default: 38)
                - media_inter: SMA period (default: 21)
        """
        self.config = config
        self.name = "ESTRATEGIAAXS"
        
        # Extract parameters with defaults
        self.media_curta = config.get('media_curta', 6)
        self.media_longa = config.get('media_longa', 38)
        self.media_inter = config.get('media_inter', 21)
        
        logger.info(f"ESTRATEGIAAXS initialized: curta={self.media_curta}, longa={self.media_longa}, inter={self.media_inter}")
        
        # Store simulation data for visualization
        self.simulation_data = None
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Generate buy/sell signals based on moving average crossovers.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Series with signals: 1 for buy, -1 for sell, 0 for hold
        """
        df_sim = df.copy()
        
        # Calculate moving averages
        df_sim['media_curta'] = ta.ema(df_sim['close'], length=self.media_curta)
        df_sim['media_longa'] = ta.sma(df_sim['close'], length=self.media_longa)
        df_sim['media_inter'] = ta.sma(df_sim['close'], length=self.media_inter)
        
        # Initialize signals
        signals = pd.Series(0, index=df_sim.index)
        
        # Calculate trend condition
        tendalta = df_sim['media_curta'] > df_sim['media_longa']
        
        # Calculate crossovers
        # Crossover: current > target AND previous <= target
        mediabuy = (df_sim['media_curta'] > df_sim['media_longa']) & (df_sim['media_curta'].shift(1) <= df_sim['media_longa'].shift(1))
        mediabuyinter = (df_sim['media_curta'] > df_sim['media_inter']) & (df_sim['media_curta'].shift(1) <= df_sim['media_inter'].shift(1))
        
        # Crossunder: current < target AND previous >= target
        mediasell = (df_sim['media_curta'] < df_sim['media_inter']) & (df_sim['media_curta'].shift(1) >= df_sim['media_inter'].shift(1))
        
        # Buy signal: (mediabuy OR mediabuyinter) AND tendalta
        buy_condition = (mediabuy | mediabuyinter) & tendalta
        signals[buy_condition] = 1
        
        # Sell signal: mediasell
        sell_condition = mediasell
        signals[sell_condition] = -1
        
        # Store simulation data for visualization
        self.simulation_data = df_sim
        
        logger.info(f"ESTRATEGIAAXS generated {buy_condition.sum()} buy signals and {sell_condition.sum()} sell signals")
        
        return signals
