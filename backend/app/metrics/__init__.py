"""
Módulo de cálculo de métricas avançadas para backtesting.

Este módulo fornece funções para calcular métricas de performance, risco,
retorno ajustado ao risco, estatísticas de trades, benchmark e critérios GO/NO-GO.
"""

from .performance import calculate_cagr, calculate_monthly_return
from .risk import (
    calculate_avg_drawdown,
    calculate_max_dd_duration,
    calculate_recovery_factor
)
from .risk_adjusted import calculate_sortino_ratio, calculate_calmar_ratio
from .trade_stats import (
    calculate_expectancy,
    calculate_max_consecutive_wins,
    calculate_max_consecutive_losses,
    calculate_trade_concentration
)
from .benchmark import calculate_buy_and_hold, calculate_alpha, calculate_correlation
from .criteria import evaluate_go_nogo

__all__ = [
    # Performance
    'calculate_cagr',
    'calculate_monthly_return',
    # Risk
    'calculate_avg_drawdown',
    'calculate_max_dd_duration',
    'calculate_recovery_factor',
    # Risk-Adjusted
    'calculate_sortino_ratio',
    'calculate_calmar_ratio',
    # Trade Stats
    'calculate_expectancy',
    'calculate_max_consecutive_wins',
    'calculate_max_consecutive_losses',
    'calculate_trade_concentration',
    # Benchmark
    'calculate_buy_and_hold',
    'calculate_alpha',
    'calculate_correlation',
    # Criteria
    'evaluate_go_nogo',
]
