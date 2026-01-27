"""
Script para analisar diferenças entre métricas do sistema e TradingView.

Este script compara:
1. Return (Compounding vs Simple)
2. Profit Factor (Percentuais vs USD)
"""

import sys
import os
import pandas as pd
import numpy as np

# Add project root and backend
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'backend'))

def calculate_system_metrics(trades):
    """
    Calcula métricas como o sistema atual (compounding + percentuais).
    """
    if not trades:
        return {
            'total_return_compounded': 0,
            'profit_factor_pct': 0,
            'total_trades': 0
        }
    
    # 1. Compounded Return (sistema atual)
    compounded_capital = 1.0
    for t in trades:
        compounded_capital *= (1.0 + t['profit'])
    total_return_compounded = (compounded_capital - 1.0) * 100.0
    
    # 2. Profit Factor (percentuais)
    gross_profit_pct = sum([t['profit'] for t in trades if t['profit'] > 0])
    gross_loss_pct = abs(sum([t['profit'] for t in trades if t['profit'] < 0]))
    profit_factor_pct = gross_profit_pct / gross_loss_pct if gross_loss_pct > 0 else (999 if gross_profit_pct > 0 else 0)
    
    return {
        'total_return_compounded': total_return_compounded,
        'profit_factor_pct': profit_factor_pct,
        'total_trades': len(trades),
        'gross_profit_pct': gross_profit_pct,
        'gross_loss_pct': gross_loss_pct
    }

def calculate_tradingview_metrics(trades, initial_capital=1000):
    """
    Calcula métricas como TradingView (simple return + USD).
    """
    if not trades:
        return {
            'total_return_simple': 0,
            'profit_factor_usd': 0,
            'final_equity': initial_capital,
            'total_trades': 0
        }
    
    # 1. Simple Return (baseado em equity)
    equity = initial_capital
    for t in trades:
        equity *= (1.0 + t['profit'])
    
    total_return_simple = (equity / initial_capital - 1) * 100.0
    
    # 2. Profit Factor (USD absoluto)
    gross_profit_usd = sum([
        initial_capital * t['profit'] 
        for t in trades if t['profit'] > 0
    ])
    gross_loss_usd = abs(sum([
        initial_capital * t['profit'] 
        for t in trades if t['profit'] < 0
    ]))
    profit_factor_usd = gross_profit_usd / gross_loss_usd if gross_loss_usd > 0 else (999 if gross_profit_usd > 0 else 0)
    
    return {
        'total_return_simple': total_return_simple,
        'profit_factor_usd': profit_factor_usd,
        'final_equity': equity,
        'total_trades': len(trades),
        'gross_profit_usd': gross_profit_usd,
        'gross_loss_usd': gross_loss_usd
    }

def analyze_trades(trades, initial_capital=1000):
    """
    Analisa trades e compara métricas do sistema vs TradingView.
    """
    print("\n" + "="*80)
    print("ANÁLISE DE MÉTRICAS: Sistema vs TradingView")
    print("="*80)
    
    if not trades:
        print("Nenhum trade encontrado!")
        return
    
    # Métricas do sistema atual
    system_metrics = calculate_system_metrics(trades)
    
    # Métricas TradingView-style
    tv_metrics = calculate_tradingview_metrics(trades, initial_capital)
    
    # Estatísticas dos trades
    df_trades = pd.DataFrame(trades)
    winning_trades = df_trades[df_trades['profit'] > 0]
    losing_trades = df_trades[df_trades['profit'] < 0]
    
    print(f"\n📊 ESTATÍSTICAS DOS TRADES:")
    print(f"   Total Trades: {len(trades)}")
    print(f"   Winning Trades: {len(winning_trades)} ({len(winning_trades)/len(trades)*100:.2f}%)")
    print(f"   Losing Trades: {len(losing_trades)} ({len(losing_trades)/len(trades)*100:.2f}%)")
    print(f"   Avg Profit (Winners): {winning_trades['profit'].mean()*100:.2f}%")
    print(f"   Avg Loss (Losers): {losing_trades['profit'].mean()*100:.2f}%")
    
    print(f"\n💰 RETURN (Total Return):")
    print(f"   Sistema (Compounding): {system_metrics['total_return_compounded']:.2f}%")
    print(f"   TradingView (Simple):   {tv_metrics['total_return_simple']:.2f}%")
    print(f"   Diferença:              {system_metrics['total_return_compounded'] - tv_metrics['total_return_simple']:.2f}%")
    print(f"   Ratio:                  {system_metrics['total_return_compounded'] / tv_metrics['total_return_simple']:.2f}x")
    
    print(f"\n📈 PROFIT FACTOR:")
    print(f"   Sistema (Percentuais): {system_metrics['profit_factor_pct']:.2f}")
    print(f"   TradingView (USD):      {tv_metrics['profit_factor_usd']:.2f}")
    print(f"   Diferença:              {system_metrics['profit_factor_pct'] - tv_metrics['profit_factor_usd']:.2f}")
    print(f"   Ratio:                  {system_metrics['profit_factor_pct'] / tv_metrics['profit_factor_usd']:.2f}x")
    
    print(f"\n💵 GROSS PROFIT/LOSS:")
    print(f"   Sistema (Pct):")
    print(f"      Gross Profit: {system_metrics['gross_profit_pct']*100:.2f}%")
    print(f"      Gross Loss:   {system_metrics['gross_loss_pct']*100:.2f}%")
    print(f"   TradingView (USD):")
    print(f"      Gross Profit: ${tv_metrics['gross_profit_usd']:.2f}")
    print(f"      Gross Loss:   ${tv_metrics['gross_loss_usd']:.2f}")
    print(f"   Equity Final: ${tv_metrics['final_equity']:.2f}")
    
    print(f"\n🔍 ANÁLISE:")
    print(f"   O sistema usa COMPOUNDING para Return, gerando valores exponenciais.")
    print(f"   O TradingView usa SIMPLE RETURN baseado em equity final/inicial.")
    print(f"   O sistema usa PERCENTUAIS para Profit Factor.")
    print(f"   O TradingView usa PnL ABSOLUTO EM USD para Profit Factor.")
    
    print("\n" + "="*80)

def main():
    """
    Exemplo de uso: analisar trades de um backtest.
    """
    # Exemplo com trades simulados
    # Em produção, você carregaria trades reais do banco de dados
    
    print("⚠️  Este script é um exemplo.")
    print("Para usar com dados reais, carregue trades do banco de dados.")
    print("\nExemplo de uso:")
    print("  from app.database import SessionLocal")
    print("  from app.models import BacktestResult")
    print("  db = SessionLocal()")
    print("  result = db.query(BacktestResult).filter(...).first()")
    print("  trades = result.trades  # Lista de trades")
    print("  analyze_trades(trades, initial_capital=1000)")
    
    # Exemplo com trades simulados
    example_trades = [
        {'profit': 0.10},   # +10%
        {'profit': 0.15},   # +15%
        {'profit': -0.05},  # -5%
        {'profit': 0.20},   # +20%
        {'profit': -0.03},  # -3%
    ]
    
    print("\n" + "="*80)
    print("EXEMPLO COM TRADES SIMULADOS:")
    print("="*80)
    analyze_trades(example_trades, initial_capital=1000)

if __name__ == "__main__":
    main()
