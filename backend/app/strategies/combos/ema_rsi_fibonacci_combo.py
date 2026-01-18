"""
EMA + RSI + Fibonacci Pullback Combo Strategy

Enters on pullbacks in strong trends using Fibonacci levels.

Entry: Price above EMA AND RSI pullback AND near Fibonacci 0.618
Exit: RSI overbought OR price below EMA
"""

from .combo_strategy import ComboStrategy


class EmaRsiFibonacciCombo(ComboStrategy):
    """
    EMA + RSI + Fibonacci combo for pullback entries in trends.
    
    Default parameters:
    - EMA: 50
    - RSI Period: 14
    - RSI Pullback Min: 40
    - RSI Pullback Max: 60
    """
    
    def __init__(
        self,
        ema_length: int = 50,
        rsi_period: int = 14,
        rsi_pullback_min: int = 40,
        rsi_pullback_max: int = 60,
        stop_loss: float = 0.015
    ):
        indicators = [
            {
                'type': 'ema',
                'alias': 'trend',
                'params': {'length': ema_length}
            },
            {
                'type': 'rsi',
                'params': {'length': rsi_period}
            }
        ]
        
        # Entry: In uptrend, wait for pullback (RSI 40-60), then enter
        entry_logic = f"(close > trend) & above(close, trend, 5) & (RSI_{rsi_period} > {rsi_pullback_min}) & (RSI_{rsi_period} < {rsi_pullback_max})"
        exit_logic = f"(RSI_{rsi_period} > 70) | (close < trend)"
        
        super().__init__(
            indicators=indicators,
            entry_logic=entry_logic,
            exit_logic=exit_logic,
            stop_loss=stop_loss
        )
        
        self.ema_length = ema_length
        self.rsi_period = rsi_period
        self.rsi_pullback_min = rsi_pullback_min
        self.rsi_pullback_max = rsi_pullback_max
