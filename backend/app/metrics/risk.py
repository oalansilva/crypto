"""
Cálculo de métricas de risco.
"""

import pandas as pd
import numpy as np


def calculate_drawdown_series(equity_curve: pd.Series) -> pd.Series:
    """
    Calcula a série de drawdowns.
    
    Args:
        equity_curve: Série temporal do valor da conta
        
    Returns:
        Série de drawdowns (valores negativos em decimal)
    """
    running_max = equity_curve.cummax()
    drawdown = (equity_curve - running_max) / running_max
    return drawdown


def calculate_avg_drawdown(equity_curve: pd.Series) -> float:
    """
    Calcula o drawdown médio.
    
    Args:
        equity_curve: Série temporal do valor da conta
        
    Returns:
        Drawdown médio como valor absoluto (ex: 0.15 para 15%)
    """
    if len(equity_curve) < 2:
        return 0.0
    
    drawdown_series = calculate_drawdown_series(equity_curve)
    
    # Apenas drawdowns negativos
    negative_dd = drawdown_series[drawdown_series < 0]
    
    if len(negative_dd) == 0:
        return 0.0
    
    avg_dd = abs(negative_dd.mean())
    return avg_dd


def calculate_max_dd_duration(equity_curve: pd.Series) -> int:
    """
    Calcula o tempo máximo em drawdown (em dias).
    
    Args:
        equity_curve: Série temporal do valor da conta com DatetimeIndex
        
    Returns:
        Número de dias do maior período em drawdown
    """
    if len(equity_curve) < 2:
        return 0
    
    drawdown_series = calculate_drawdown_series(equity_curve)
    
    # Identificar períodos em drawdown (DD < 0)
    in_drawdown = drawdown_series < 0
    
    if not in_drawdown.any():
        return 0
    
    # Identificar mudanças de estado (entrada/saída de drawdown)
    changes = in_drawdown.astype(int).diff().fillna(0)
    
    # Encontrar início de cada drawdown (mudança de 0 para 1)
    dd_starts = changes[changes == 1].index
    # Encontrar fim de cada drawdown (mudança de 1 para 0)
    dd_ends = changes[changes == -1].index
    
    # Se ainda estiver em drawdown no final, adicionar último índice
    if in_drawdown.iloc[-1]:
        dd_ends = dd_ends.append(pd.Index([equity_curve.index[-1]]))
    
    # Se começou em drawdown, adicionar primeiro índice
    if in_drawdown.iloc[0]:
        dd_starts = pd.Index([equity_curve.index[0]]).append(dd_starts)
    
    if len(dd_starts) == 0 or len(dd_ends) == 0:
        return 0
    
    # Calcular duração de cada drawdown
    max_duration = 0
    for start, end in zip(dd_starts, dd_ends):
        if isinstance(equity_curve.index, pd.DatetimeIndex):
            duration = (end - start).days
        else:
            # Se não for DatetimeIndex, contar número de pontos
            duration = len(equity_curve.loc[start:end])
        
        max_duration = max(max_duration, duration)
    
    return max_duration


def calculate_recovery_factor(total_return: float, max_drawdown: float) -> float:
    """
    Calcula o Recovery Factor.
    
    Recovery Factor = Total Return / Max Drawdown
    
    Args:
        total_return: Retorno total como decimal (ex: 1.0 para 100%)
        max_drawdown: Max drawdown como decimal positivo (ex: 0.30 para 30%)
        
    Returns:
        Recovery Factor (valores > 1.0 são bons)
    """
    if max_drawdown == 0:
        # Se não houve drawdown, retornar infinito (ou valor muito alto)
        return float('inf') if total_return > 0 else 0.0
    
    recovery_factor = total_return / max_drawdown
    return recovery_factor
