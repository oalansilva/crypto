"""
Cálculo de estatísticas de trades.
"""

from typing import List, Dict, Any
import numpy as np


def calculate_expectancy(trades: List[Dict[str, Any]]) -> float:
    """
    Calcula a expectativa por trade.
    
    Expectancy = (Win Rate × Avg Win) - (Loss Rate × Avg Loss)
    
    Args:
        trades: Lista de trades com campo 'pnl'
        
    Returns:
        Expectância em valor absoluto (ex: 15.5 para $15.50 por trade)
    """
    if not trades:
        return 0.0
    
    pnls = [t.get('pnl', 0) for t in trades]
    
    if len(pnls) == 0:
        return 0.0
    
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]
    
    total_trades = len(pnls)
    win_rate = len(wins) / total_trades if total_trades > 0 else 0
    loss_rate = len(losses) / total_trades if total_trades > 0 else 0
    
    avg_win = np.mean(wins) if wins else 0
    avg_loss = abs(np.mean(losses)) if losses else 0
    
    expectancy = (win_rate * avg_win) - (loss_rate * avg_loss)
    
    return expectancy


def calculate_max_consecutive_wins(trades: List[Dict[str, Any]]) -> int:
    """
    Calcula a maior sequência de trades vencedores consecutivos.
    
    Args:
        trades: Lista de trades com campo 'pnl'
        
    Returns:
        Número de wins consecutivos
    """
    if not trades:
        return 0
    
    pnls = [t.get('pnl', 0) for t in trades]
    
    max_streak = 0
    current_streak = 0
    
    for pnl in pnls:
        if pnl > 0:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0
    
    return max_streak


def calculate_max_consecutive_losses(trades: List[Dict[str, Any]]) -> int:
    """
    Calcula a maior sequência de trades perdedores consecutivos.
    
    Args:
        trades: Lista de trades com campo 'pnl'
        
    Returns:
        Número de losses consecutivos
    """
    if not trades:
        return 0
    
    pnls = [t.get('pnl', 0) for t in trades]
    
    max_streak = 0
    current_streak = 0
    
    for pnl in pnls:
        if pnl < 0:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0
    
    return max_streak


def calculate_trade_concentration(trades: List[Dict[str, Any]], top_n: int = 10) -> float:
    """
    Calcula a concentração de lucro nos top N trades.
    
    Args:
        trades: Lista de trades com campo 'pnl'
        top_n: Número de top trades a considerar
        
    Returns:
        Percentual do lucro total nos top N trades (ex: 0.80 para 80%)
    """
    if not trades:
        return 0.0
    
    pnls = [t.get('pnl', 0) for t in trades]
    
    # Apenas trades vencedores
    winning_pnls = [p for p in pnls if p > 0]
    
    if not winning_pnls:
        return 0.0
    
    total_profit = sum(winning_pnls)
    
    if total_profit <= 0:
        return 0.0
    
    # Ordenar do maior para o menor
    sorted_pnls = sorted(winning_pnls, reverse=True)
    
    # Pegar top N
    top_pnls = sorted_pnls[:min(top_n, len(sorted_pnls))]
    top_profit = sum(top_pnls)
    
    concentration = top_profit / total_profit
    
    return concentration
