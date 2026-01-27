"""
Script para comparar métricas agregadas entre Sistema (preto) e TradingView (branco).

Dados do TradingView (tela branca):
- Total P&L: +2,940.27 USD (+2,940.27%)
- Max equity drawdown: 624.90 USD (29.71%)
- Total trades: 55
- Profitable trades: 47.27% (26/55)
- Profit factor: 2.351

Dados do Sistema (tela preta):
- Total Trades: 55
- Win Rate: 63.6%
- Total Return: 2021807.75% (ou 20218.08% em outra tela)
- Avg Profit: 36760.14%
- Max Drawdown: 8.69%
- Profit Factor: 8.45 (ou 16.30)
"""

import sys
import os

# Add project root and backend
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'backend'))

def calculate_metrics_from_trades(trades, initial_capital=100):
    """
    Calcula métricas a partir de uma lista de trades usando compounding.
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

def compare_metrics(system_metrics: dict, tradingview_metrics: dict):
    """
    Compara métricas do sistema com TradingView.
    """
    print("\n" + "="*100)
    print("COMPARACAO DE METRICAS: Sistema vs TradingView")
    print("="*100)
    
    print(f"\n[METRICAS] SISTEMA (Tela Preta):")
    print(f"   Total Return: {system_metrics.get('total_return', 0):.2f}%")
    print(f"   Total P&L: ${system_metrics.get('total_pnl_usd', 0):.2f}")
    print(f"   Max Drawdown: {system_metrics.get('max_drawdown', 0):.2f}%")
    print(f"   Total Trades: {system_metrics.get('total_trades', 0)}")
    print(f"   Win Rate: {system_metrics.get('win_rate', 0):.2f}%")
    print(f"   Profit Factor: {system_metrics.get('profit_factor', 0):.3f}")
    
    print(f"\n[METRICAS] TRADINGVIEW (Tela Branca):")
    print(f"   Total Return: {tradingview_metrics.get('total_return_pct', 0):.2f}%")
    print(f"   Total P&L: ${tradingview_metrics.get('total_pnl_usd', 0):.2f}")
    print(f"   Max Drawdown: {tradingview_metrics.get('max_drawdown_pct', 0):.2f}%")
    print(f"   Total Trades: {tradingview_metrics.get('total_trades', 0)}")
    print(f"   Win Rate: {tradingview_metrics.get('win_rate', 0):.2f}%")
    print(f"   Profit Factor: {tradingview_metrics.get('profit_factor', 0):.3f}")
    
    print(f"\n[ANALISE] DIFERENCAS:")
    print(f"{'='*100}")
    
    return_diff = abs(system_metrics.get('total_return', 0) - tradingview_metrics.get('total_return_pct', 0))
    dd_diff = abs(system_metrics.get('max_drawdown', 0) - tradingview_metrics.get('max_drawdown_pct', 0))
    pf_diff = abs(system_metrics.get('profit_factor', 0) - tradingview_metrics.get('profit_factor', 0))
    wr_diff = abs(system_metrics.get('win_rate', 0) - tradingview_metrics.get('win_rate', 0))
    
    print(f"\n1. RETURN (Total Return):")
    print(f"   Sistema: {system_metrics.get('total_return', 0):.2f}%")
    print(f"   TradingView: {tradingview_metrics.get('total_return_pct', 0):.2f}%")
    print(f"   Diferenca: {return_diff:.2f}%")
    if return_diff > 100:
        print(f"   [ERRO CRITICO] Diferenca muito grande! Verifique calculo de compounding.")
    
    print(f"\n2. MAX DRAWDOWN:")
    print(f"   Sistema: {system_metrics.get('max_drawdown', 0):.2f}%")
    print(f"   TradingView: {tradingview_metrics.get('max_drawdown_pct', 0):.2f}%")
    print(f"   Diferenca: {dd_diff:.2f}%")
    
    print(f"\n3. PROFIT FACTOR:")
    print(f"   Sistema: {system_metrics.get('profit_factor', 0):.3f}")
    print(f"   TradingView: {tradingview_metrics.get('profit_factor', 0):.3f}")
    print(f"   Diferenca: {pf_diff:.3f}")
    
    print(f"\n4. WIN RATE:")
    print(f"   Sistema: {system_metrics.get('win_rate', 0):.2f}%")
    print(f"   TradingView: {tradingview_metrics.get('win_rate', 0):.2f}%")
    print(f"   Diferenca: {wr_diff:.2f}%")
    
    print(f"\n5. TOTAL TRADES:")
    print(f"   Sistema: {system_metrics.get('total_trades', 0)}")
    print(f"   TradingView: {tradingview_metrics.get('total_trades', 0)}")
    trades_diff = abs(system_metrics.get('total_trades', 0) - tradingview_metrics.get('total_trades', 0))
    if trades_diff > 0:
        print(f"   [ATENCAO] Numero de trades diferente!")
    
    print(f"\n{'='*100}")
    print(f"DIAGNOSTICO:")
    print(f"{'='*100}")
    
    issues = []
    if return_diff > 100:
        issues.append(f"Return tem diferenca critica de {return_diff:.2f}%")
    if dd_diff > 5:
        issues.append(f"Max Drawdown tem diferenca significativa de {dd_diff:.2f}%")
    if pf_diff > 1.0:
        issues.append(f"Profit Factor tem diferenca significativa de {pf_diff:.3f}")
    if wr_diff > 5:
        issues.append(f"Win Rate tem diferenca significativa de {wr_diff:.2f}%")
    if trades_diff > 0:
        issues.append(f"Numero de trades diferente: {trades_diff}")
    
    if issues:
        print(f"\n[ATENCAO] Problemas encontrados:")
        for issue in issues:
            print(f"   - {issue}")
    else:
        print(f"\n[OK] Metricas estao muito proximas!")
    
    print("\n" + "="*100)

# Dados do TradingView (tela branca) - baseado na imagem
TRADINGVIEW_METRICS = {
    'total_return_pct': 2940.27,
    'total_pnl_usd': 2940.27,
    'max_drawdown_pct': 29.71,
    'max_drawdown_usd': 624.90,
    'total_trades': 55,
    'win_rate': 47.27,  # 26/55
    'profit_factor': 2.351
}

# Dados do Sistema (tela preta) - baseado nas imagens
# Nota: Há duas versões diferentes nas imagens
SYSTEM_METRICS_V1 = {
    'total_return': 2021807.75,  # Primeira imagem
    'total_pnl_usd': 2021807.75,  # Assumindo capital inicial $100
    'max_drawdown': 8.69,
    'total_trades': 55,
    'win_rate': 63.6,
    'profit_factor': 8.45  # Primeira imagem
}

SYSTEM_METRICS_V2 = {
    'total_return': 20218.08,  # Segunda imagem (tabela)
    'total_pnl_usd': 20218.08,  # Assumindo capital inicial $100
    'max_drawdown': 8.69,
    'total_trades': 55,
    'win_rate': 63.64,
    'profit_factor': 16.30  # Segunda imagem
}

if __name__ == "__main__":
    print("COMPARACAO DE METRICAS: Sistema vs TradingView")
    print("\nEste script compara as metricas agregadas entre o sistema e TradingView.")
    print("Baseado nas imagens fornecidas.")
    
    print("\n" + "="*100)
    print("COMPARACAO 1: Sistema (V1) vs TradingView")
    print("="*100)
    compare_metrics(SYSTEM_METRICS_V1, TRADINGVIEW_METRICS)
    
    print("\n" + "="*100)
    print("COMPARACAO 2: Sistema (V2) vs TradingView")
    print("="*100)
    compare_metrics(SYSTEM_METRICS_V2, TRADINGVIEW_METRICS)
    
    print("\n" + "="*100)
    print("OBSERVACOES:")
    print("="*100)
    print("1. Sistema mostra Return muito maior que TradingView")
    print("2. Isso indica que o calculo de compounding pode estar incorreto")
    print("3. Ou o capital inicial usado e diferente")
    print("4. TradingView mostra 2,940.27% com capital inicial de $100")
    print("5. Sistema mostra 20,218% ou 2,021,807% (valores muito diferentes)")
    print("\n6. POSSIVEL CAUSA:")
    print("   - Sistema pode estar usando capital inicial diferente")
    print("   - Ou o calculo de compounding esta multiplicando errado")
    print("   - Ou ha um erro na formula de retorno")
