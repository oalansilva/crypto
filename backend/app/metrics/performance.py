"""
Cálculo de métricas de performance.
"""

import pandas as pd
from datetime import datetime


def calculate_cagr(equity_curve: pd.Series) -> float:
    """
    Calcula o CAGR (Compound Annual Growth Rate).
    
    CAGR = (Final Value / Initial Value)^(1/Years) - 1
    
    Args:
        equity_curve: Série temporal do valor da conta
        
    Returns:
        CAGR como decimal (ex: 0.45 para 45%)
        
    Raises:
        ValueError: Se equity curve muito curta ou dados inválidos
    """
    if len(equity_curve) < 2:
        raise ValueError("Equity curve deve ter pelo menos 2 pontos")
    
    initial_value = equity_curve.iloc[0]
    final_value = equity_curve.iloc[-1]
    
    if initial_value <= 0:
        raise ValueError("Valor inicial deve ser positivo")
    
    # Calcular número de anos
    if isinstance(equity_curve.index, pd.DatetimeIndex):
        days = (equity_curve.index[-1] - equity_curve.index[0]).days
        years = days / 365.25
    else:
        # Se não tiver index datetime, assumir que cada ponto é 1 dia
        years = len(equity_curve) / 365.25
    
    if years <= 0:
        raise ValueError("Período deve ser maior que zero")
    
    # CAGR = (FV / IV)^(1/years) - 1
    cagr = (final_value / initial_value) ** (1 / years) - 1
    
    return cagr


def calculate_monthly_return(equity_curve: pd.Series) -> float:
    """
    Calcula o retorno médio mensal.
    
    Args:
        equity_curve: Série temporal do valor da conta com DatetimeIndex
        
    Returns:
        Retorno médio mensal como decimal
        
    Raises:
        ValueError: Se não houver DatetimeIndex ou dados insuficientes
    """
    if not isinstance(equity_curve.index, pd.DatetimeIndex):
        raise ValueError("Equity curve deve ter DatetimeIndex para cálculo mensal")
    
    if len(equity_curve) < 2:
        raise ValueError("Equity curve deve ter pelo menos 2 pontos")
    
    # Resample para mensal e calcular retornos
    monthly_equity = equity_curve.resample('M').last()
    
    if len(monthly_equity) < 2:
        # Se menos de 2 meses, calcular retorno total e anualizar
        total_return = (equity_curve.iloc[-1] / equity_curve.iloc[0]) - 1
        days = (equity_curve.index[-1] - equity_curve.index[0]).days
        months = days / 30.44  # Média de dias por mês
        if months > 0:
            return total_return / months
        return 0.0
    
    # Calcular retornos mensais
    monthly_returns = monthly_equity.pct_change().dropna()
    
    if len(monthly_returns) == 0:
        return 0.0
    
    # Retorno médio mensal
    avg_monthly_return = monthly_returns.mean()
    
    return avg_monthly_return
