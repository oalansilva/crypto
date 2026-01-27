"""
Script para validar se as métricas do sistema batem com TradingView.

Dados corretos do TradingView:
- Total P&L: +6,360.42 USD (+6,360.42%)
- Max equity drawdown: 2,153.64 USD (26.74%)
- Total trades: 64
- Profitable trades: 45.31% (29/64)
- Profit factor: 2.025
"""

import sys
import os

# Add project root and backend
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'backend'))

def calculate_tradingview_metrics(trades, initial_capital=100):
    """
    Calcula métricas no estilo TradingView (compounding).
    """
    if not trades:
        return {
            'total_return_pct': 0,
            'total_pnl_usd': 0,
            'final_equity': initial_capital,
            'max_drawdown_pct': 0,
            'max_drawdown_usd': 0,
            'total_trades': 0,
            'win_rate': 0,
            'profit_factor': 0
        }
    
    # 1. Compounded Return (equity cresce a cada trade)
    equity = float(initial_capital)
    equity_curve = [equity]
    
    for t in trades:
        equity *= (1.0 + t['profit'])
        equity_curve.append(equity)
    
    total_return_pct = (equity / initial_capital - 1) * 100.0
    total_pnl_usd = equity - initial_capital
    
    # 2. Max Drawdown (baseado em equity curve)
    peak = initial_capital
    max_dd_pct = 0.0
    max_dd_usd = 0.0
    
    for eq in equity_curve:
        if eq > peak:
            peak = eq
        drawdown_pct = (peak - eq) / peak
        drawdown_usd = peak - eq
        if drawdown_pct > max_dd_pct:
            max_dd_pct = drawdown_pct
            max_dd_usd = drawdown_usd
    
    # 3. Win Rate
    total_trades = len(trades)
    winning_trades = sum(1 for t in trades if t['profit'] > 0)
    win_rate = (winning_trades / total_trades) * 100.0 if total_trades > 0 else 0
    
    # 4. Profit Factor (com compounding - cada trade usa equity atual)
    equity_current = float(initial_capital)
    gross_profit_usd = 0.0
    gross_loss_usd = 0.0
    
    for t in trades:
        trade_pnl_usd = equity_current * t['profit']
        if t['profit'] > 0:
            gross_profit_usd += trade_pnl_usd
        else:
            gross_loss_usd += abs(trade_pnl_usd)
        # Atualizar equity para próximo trade (compounding)
        equity_current *= (1.0 + t['profit'])
    
    profit_factor = gross_profit_usd / gross_loss_usd if gross_loss_usd > 0 else (999 if gross_profit_usd > 0 else 0)
    
    return {
        'total_return_pct': total_return_pct,
        'total_pnl_usd': total_pnl_usd,
        'final_equity': equity,
        'max_drawdown_pct': max_dd_pct * 100.0,
        'max_drawdown_usd': max_dd_usd,
        'total_trades': total_trades,
        'win_rate': win_rate,
        'profit_factor': profit_factor,
        'gross_profit_usd': gross_profit_usd,
        'gross_loss_usd': gross_loss_usd
    }

def validate_against_tradingview(system_metrics, tradingview_metrics):
    """
    Compara métricas do sistema com TradingView.
    """
    print("\n" + "="*80)
    print("VALIDACAO: Sistema vs TradingView")
    print("="*80)
    
    print(f"\n📊 METRICAS DO SISTEMA:")
    print(f"   Total Return: {system_metrics.get('total_return', 0):.2f}%")
    print(f"   Total P&L: ${system_metrics.get('total_pnl_usd', 0):.2f}")
    print(f"   Max Drawdown: {system_metrics.get('max_drawdown', 0):.2f}%")
    print(f"   Total Trades: {system_metrics.get('total_trades', 0)}")
    print(f"   Win Rate: {system_metrics.get('win_rate', 0):.2f}%")
    print(f"   Profit Factor: {system_metrics.get('profit_factor', 0):.3f}")
    
    print(f"\n✅ METRICAS CORRETAS DO TRADINGVIEW:")
    print(f"   Total Return: {tradingview_metrics['total_return_pct']:.2f}%")
    print(f"   Total P&L: ${tradingview_metrics['total_pnl_usd']:.2f}")
    print(f"   Max Drawdown: {tradingview_metrics['max_drawdown_pct']:.2f}%")
    print(f"   Total Trades: {tradingview_metrics['total_trades']}")
    print(f"   Win Rate: {tradingview_metrics['win_rate']:.2f}%")
    print(f"   Profit Factor: {tradingview_metrics['profit_factor']:.3f}")
    
    print(f"\n🔍 COMPARACAO:")
    return_diff = abs(system_metrics.get('total_return', 0) - tradingview_metrics['total_return_pct'])
    dd_diff = abs(system_metrics.get('max_drawdown', 0) - tradingview_metrics['max_drawdown_pct'])
    pf_diff = abs(system_metrics.get('profit_factor', 0) - tradingview_metrics['profit_factor'])
    
    print(f"   Return: Diferenca de {return_diff:.2f}%")
    print(f"   Max DD: Diferenca de {dd_diff:.2f}%")
    print(f"   Profit Factor: Diferenca de {pf_diff:.3f}")
    
    if return_diff < 1.0 and dd_diff < 1.0 and pf_diff < 0.1:
        print(f"\n[OK] Metricas estao muito proximas do TradingView!")
    else:
        print(f"\n[ATENCAO] Ha diferencas significativas. Verifique:")
        if return_diff >= 1.0:
            print(f"   - Return: diferenca de {return_diff:.2f}%")
        if dd_diff >= 1.0:
            print(f"   - Max Drawdown: diferenca de {dd_diff:.2f}%")
        if pf_diff >= 0.1:
            print(f"   - Profit Factor: diferenca de {pf_diff:.3f}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    print("Este script valida as metricas do sistema contra os dados corretos do TradingView.")
    print("\nPara usar:")
    print("  1. Execute um backtest no sistema")
    print("  2. Carregue os trades do resultado")
    print("  3. Calcule as metricas usando calculate_tradingview_metrics()")
    print("  4. Compare com os valores esperados do TradingView")
    
    # Exemplo com dados simulados
    print("\n" + "="*80)
    print("EXEMPLO COM DADOS SIMULADOS:")
    print("="*80)
    
    # Simular 64 trades com win rate de 45.31% (29 wins, 35 losses)
    example_trades = []
    for i in range(29):  # 29 winning trades
        example_trades.append({'profit': 0.15})  # +15% cada
    for i in range(35):  # 35 losing trades
        example_trades.append({'profit': -0.0694})  # -6.94% cada (stop loss)
    
    tv_metrics = calculate_tradingview_metrics(example_trades, initial_capital=100)
    
    print(f"\nMetricas calculadas (exemplo):")
    print(f"   Total Return: {tv_metrics['total_return_pct']:.2f}%")
    print(f"   Total P&L: ${tv_metrics['total_pnl_usd']:.2f}")
    print(f"   Max Drawdown: {tv_metrics['max_drawdown_pct']:.2f}%")
    print(f"   Total Trades: {tv_metrics['total_trades']}")
    print(f"   Win Rate: {tv_metrics['win_rate']:.2f}%")
    print(f"   Profit Factor: {tv_metrics['profit_factor']:.3f}")
