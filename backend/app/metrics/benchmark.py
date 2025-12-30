"""
Cálculo de métricas de benchmark (Buy & Hold).
"""

import pandas as pd
import numpy as np


def calculate_buy_and_hold(
    prices: pd.Series,
    initial_capital: float
) -> dict:
    """
    Simula estratégia Buy & Hold.
    
    Compra no primeiro preço e vende no último.
    
    Args:
        prices: Série de preços (close)
        initial_capital: Capital inicial
        
    Returns:
        Dict com métricas do B&H: {
            'return_pct': float,
            'cagr': float,
            'final_value': float
        }
    """
    if len(prices) < 2:
        return {
            'return_pct': 0.0,
            'cagr': 0.0,
            'final_value': initial_capital
        }
    
    entry_price = prices.iloc[0]
    exit_price = prices.iloc[-1]
    
    if entry_price <= 0:
        return {
            'return_pct': 0.0,
            'cagr': 0.0,
            'final_value': initial_capital
        }
    
    # Calcular quantas shares comprar
    shares = initial_capital / entry_price
    final_value = shares * exit_price
    
    return_pct = (final_value - initial_capital) / initial_capital
    
    # Calcular CAGR
    if isinstance(prices.index, pd.DatetimeIndex):
        days = (prices.index[-1] - prices.index[0]).days
        years = days / 365.25
    else:
        years = len(prices) / 365.25
    
    if years > 0:
        cagr = (final_value / initial_capital) ** (1 / years) - 1
    else:
        cagr = return_pct
    
    return {
        'return_pct': return_pct,
        'cagr': cagr,
        'final_value': final_value
    }


def calculate_alpha(strategy_return: float, benchmark_return: float) -> float:
    """
    Calcula o Alpha (excesso de retorno vs benchmark).
    
    Alpha = Strategy Return - Benchmark Return
    
    Args:
        strategy_return: Retorno da estratégia (decimal)
        benchmark_return: Retorno do benchmark (decimal)
        
    Returns:
        Alpha (decimal, ex: 0.15 para 15% de excesso)
    """
    return strategy_return - benchmark_return


def calculate_correlation(
    strategy_returns: pd.Series,
    benchmark_returns: pd.Series
) -> float:
    """
    Calcula a correlação entre estratégia e benchmark.
    
    Args:
        strategy_returns: Série de retornos da estratégia
        benchmark_returns: Série de retornos do benchmark
        
    Returns:
        Correlação de Pearson (-1 a 1)
    """
    if len(strategy_returns) < 2 or len(benchmark_returns) < 2:
        return 0.0
    
    # Alinhar índices
    aligned = pd.DataFrame({
        'strategy': strategy_returns,
        'benchmark': benchmark_returns
    }).dropna()
    
    if len(aligned) < 2:
        return 0.0
    
    correlation = aligned['strategy'].corr(aligned['benchmark'])
    
    return correlation if not np.isnan(correlation) else 0.0
