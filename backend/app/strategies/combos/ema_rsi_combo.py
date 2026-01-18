"""
EMA + RSI Combo Strategy (Trend + Momentum)

Combines trend following (EMAs) with momentum confirmation (RSI).

Entry: Price above both EMAs AND RSI in range (30-50)
Exit: RSI overbought (>70) OR price below fast EMA
"""

from .combo_strategy import ComboStrategy


class EmaRsiCombo(ComboStrategy):
    """
    EMA + RSI combo for trend following with momentum confirmation.
    
    Default parameters:
    - EMA Fast: 9
    - EMA Slow: 21
    - RSI Period: 14
    - RSI Min: 30
    - RSI Max: 50
    """
    
    def __init__(
        self,
        ema_fast: int = 9,
        ema_slow: int = 21,
        rsi_period: int = 14,
        rsi_min: int = 30,
        rsi_max: int = 50,
        stop_loss: float = 0.015
    ):
        indicators = [
            {
                'type': 'ema',
                'alias': 'fast',
                'params': {'length': ema_fast}
            },
            {
                'type': 'ema',
                'alias': 'slow',
                'params': {'length': ema_slow}
            },
            {
                'type': 'rsi',
                'params': {'length': rsi_period}
            }
        ]
        
        entry_logic = f"(close > fast) & (close > slow) & (RSI_{rsi_period} > {rsi_min}) & (RSI_{rsi_period} < {rsi_max})"
        exit_logic = f"(RSI_{rsi_period} > 70) | (close < fast)"
        
        super().__init__(
            indicators=indicators,
            entry_logic=entry_logic,
            exit_logic=exit_logic,
            stop_loss=stop_loss
        )
        
        # Store parameters
        self.ema_fast = ema_fast
        self.ema_slow = ema_slow
        self.rsi_period = rsi_period
        self.rsi_min = rsi_min
        self.rsi_max = rsi_max
    
    @classmethod
    def get_optimization_schema(cls):
        """
        Get optimization parameters schema.
        
        Returns:
            Dict[str, Dict]: Schema for each parameter with range and default
        """
        return {
            "ema_fast": {"min": 5, "max": 20, "step": 1, "default": 9},
            "ema_slow": {"min": 15, "max": 50, "step": 1, "default": 21},
            "rsi_period": {"min": 7, "max": 21, "step": 1, "default": 14},
            "rsi_min": {"min": 20, "max": 40, "step": 2, "default": 30},
            "rsi_max": {"min": 60, "max": 80, "step": 2, "default": 50},
            "stop_loss": {"min": 0.01, "max": 0.05, "step": 0.005, "default": 0.015}
        }
