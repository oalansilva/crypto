"""
Multi-MA Crossover Combo Strategy

Based on CRUZAMENTOMEDIAS strategy:
- EMA Fast (3)
- SMA Long (37)
- SMA Intermediate (32)

Entry: (fast > long) AND (crossover(fast, long) OR crossover(fast, inter))
Exit: crossunder(fast, inter)
"""

from .combo_strategy import ComboStrategy


class MultiMaCrossoverCombo(ComboStrategy):
    """
    Multi-MA Crossover strategy combining 3 moving averages.
    
    Default parameters:
    - EMA Fast: 3
    - SMA Long: 37
    - SMA Intermediate: 32
    """
    
    def __init__(
        self,
        ema_fast: int = 3,
        sma_long: int = 37,
        sma_inter: int = 32,
        stop_loss: float = 0.015
    ):
        indicators = [
            {
                'type': 'ema',
                'alias': 'fast',
                'params': {'length': ema_fast}
            },
            {
                'type': 'sma',
                'alias': 'long',
                'params': {'length': sma_long}
            },
            {
                'type': 'sma',
                'alias': 'inter',
                'params': {'length': sma_inter}
            }
        ]
        
        entry_logic = "(fast > long) & (crossover(fast, long) | crossover(fast, inter))"
        exit_logic = "crossunder(fast, inter)"
        
        super().__init__(
            indicators=indicators,
            entry_logic=entry_logic,
            exit_logic=exit_logic,
            stop_loss=stop_loss
        )
        
        # Store parameters for optimization
        self.ema_fast = ema_fast
        self.sma_long = sma_long
        self.sma_inter = sma_inter
