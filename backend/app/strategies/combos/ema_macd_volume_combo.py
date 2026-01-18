"""
EMA + MACD + Volume Combo Strategy

Combines trend (EMA), momentum (MACD), and volume confirmation.

Entry: Price above EMA AND MACD histogram positive AND volume above average
Exit: MACD crossunder OR price below EMA
"""

from .combo_strategy import ComboStrategy


class EmaMacdVolumeCombo(ComboStrategy):
    """
    EMA + MACD + Volume combo for confirmed trend moves.
    
    Default parameters:
    - EMA: 20
    - MACD Fast: 12
    - MACD Slow: 26
    - MACD Signal: 9
    - Volume SMA: 20
    """
    
    def __init__(
        self,
        ema_length: int = 20,
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
        volume_sma: int = 20,
        stop_loss: float = 0.015
    ):
        indicators = [
            {
                'type': 'ema',
                'alias': 'trend',
                'params': {'length': ema_length}
            },
            {
                'type': 'macd',
                'alias': 'macd',
                'params': {
                    'fast': macd_fast,
                    'slow': macd_slow,
                    'signal': macd_signal
                }
            },
            {
                'type': 'volume_sma',
                'alias': 'vol_avg',
                'params': {'length': volume_sma}
            }
        ]
        
        entry_logic = "(close > trend) & (macd_histogram > 0) & (volume > vol_avg)"
        exit_logic = "crossunder(macd_macd, macd_signal) | (close < trend)"
        
        super().__init__(
            indicators=indicators,
            entry_logic=entry_logic,
            exit_logic=exit_logic,
            stop_loss=stop_loss
        )
        
        self.ema_length = ema_length
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.volume_sma = volume_sma
