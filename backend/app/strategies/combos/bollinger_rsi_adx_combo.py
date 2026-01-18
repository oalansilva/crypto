"""
Bollinger Bands + RSI + ADX Combo Strategy

Statistical combo for ranging and trending markets.

Entry: Price at lower Bollinger AND RSI oversold AND ADX shows trend/range
Exit: Price returns to middle Bollinger
"""

from .combo_strategy import ComboStrategy


class BollingerRsiAdxCombo(ComboStrategy):
    """
    Bollinger + RSI + ADX combo for statistical reversions.
    
    Default parameters:
    - Bollinger Length: 20
    - Bollinger Std: 2
    - RSI Period: 14
    - ADX Period: 14
    """
    
    def __init__(
        self,
        bb_length: int = 20,
        bb_std: int = 2,
        rsi_period: int = 14,
        adx_period: int = 14,
        stop_loss: float = 0.015
    ):
        indicators = [
            {
                'type': 'bbands',
                'alias': 'bb',
                'params': {'length': bb_length, 'std': bb_std}
            },
            {
                'type': 'rsi',
                'params': {'length': rsi_period}
            },
            {
                'type': 'adx',
                'params': {'length': adx_period}
            }
        ]
        
        # Entry: Oversold in ranging market OR breakout in trending market
        entry_logic = f"((close < bb_lower) & (RSI_{rsi_period} < 30) & (ADX_{adx_period} < 20)) | ((close > bb_upper) & (RSI_{rsi_period} > 70) & (ADX_{adx_period} > 20))"
        exit_logic = "(close > bb_middle)"
        
        super().__init__(
            indicators=indicators,
            entry_logic=entry_logic,
            exit_logic=exit_logic,
            stop_loss=stop_loss
        )
        
        self.bb_length = bb_length
        self.bb_std = bb_std
        self.rsi_period = rsi_period
        self.adx_period = adx_period
