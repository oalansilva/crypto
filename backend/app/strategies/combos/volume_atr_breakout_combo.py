"""
Volume + ATR Breakout Combo Strategy

Confirms breakouts with volume and volatility.

Entry: Price breaks high AND volume > 2x average AND ATR shows volatility
Exit: Price falls below breakout level
"""

from .combo_strategy import ComboStrategy


class VolumeAtrBreakoutCombo(ComboStrategy):
    """
    Volume + ATR combo for breakout confirmation.
    
    Default parameters:
    - Volume SMA: 20
    - ATR Period: 14
    - Volume Multiplier: 2.0
    """
    
    def __init__(
        self,
        volume_sma: int = 20,
        atr_period: int = 14,
        volume_multiplier: float = 2.0,
        stop_loss: float = 0.015
    ):
        indicators = [
            {
                'type': 'volume_sma',
                'alias': 'vol_avg',
                'params': {'length': volume_sma}
            },
            {
                'type': 'atr',
                'params': {'length': atr_period}
            }
        ]
        
        entry_logic = f"(volume > vol_avg * {volume_multiplier}) and (ATR_{atr_period} > ATR_{atr_period}.shift(1))"
        exit_logic = "(close < close.shift(1).rolling(5).max())"
        
        super().__init__(
            indicators=indicators,
            entry_logic=entry_logic,
            exit_logic=exit_logic,
            stop_loss=stop_loss
        )
        
        self.volume_sma = volume_sma
        self.atr_period = atr_period
        self.volume_multiplier = volume_multiplier
