"""
Cálculo de métricas de retorno ajustado ao risco.
"""

import pandas as pd
import numpy as np


def calculate_sortino_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 365
) -> float:
    """
    Calcula o Sortino Ratio (penaliza apenas volatilidade negativa).
    
    Sortino = (Retorno Médio - Risk Free) / Downside Deviation
    
    Args:
        returns: Série de retornos diários
        risk_free_rate: Taxa livre de risco anualizada (ex: 0.02 para 2%)
        periods_per_year: Número de períodos por ano (365 para diário)
        
    Returns:
        Sortino Ratio
    """
    if len(returns) < 2:
        return 0.0
    
    # Retorno médio anualizado
    avg_return = returns.mean() * periods_per_year
    
    # Downside deviation (apenas retornos negativos)
    negative_returns = returns[returns < 0]
    
    if len(negative_returns) == 0:
        # Sem retornos negativos = Sortino infinito
        return float('inf') if avg_return > risk_free_rate else 0.0
    
    downside_std = negative_returns.std() * np.sqrt(periods_per_year)
    
    if downside_std == 0:
        return 0.0
    
    sortino = (avg_return - risk_free_rate) / downside_std
    return sortino


def calculate_calmar_ratio(cagr: float, max_drawdown: float) -> float:
    """
    Calcula o Calmar Ratio.
    
    Calmar = CAGR / Max Drawdown
    
    Args:
        cagr: CAGR como decimal (ex: 0.45 para 45%)
        max_drawdown: Max drawdown como decimal positivo (ex: 0.30 para 30%)
        
    Returns:
        Calmar Ratio (valores ≥ 1.0 são bons, ≥ 1.5 são excelentes)
    """
    if max_drawdown == 0:
        # Se não houve drawdown
        return float('inf') if cagr > 0 else 0.0
    
    calmar = cagr / abs(max_drawdown)
    return calmar
