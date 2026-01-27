"""
Script para comparar TODOS os 55 trades entre Sistema e TradingView.

Baseado nas planilhas e imagens fornecidas:
- Sistema: planilha com 55 trades (ordem cronológica reversa - mais recentes primeiro)
- TradingView: lista de trades (ordem reversa - trade 55 a 48 visíveis, mas temos dados completos)
"""

import sys
import os
from datetime import datetime
from typing import List, Dict, Any

# Add project root and backend
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'backend'))

def parse_date(date_str: str) -> datetime:
    """Converte string de data para datetime."""
    try:
        # Formato sistema: "2026-01-04T00:00:00+00:00" ou "2017-10-13T00:00:00+00:00"
        if 'T' in date_str:
            date_part = date_str.split('T')[0]
            return datetime.strptime(date_part, '%Y-%m-%d')
        # Formato TradingView: "Jan 04, 2026" ou "Oct 13, 2017"
        elif ',' in date_str:
            return datetime.strptime(date_str.strip(), '%b %d, %Y')
        # Formato sistema antigo: "13/10/2017, 00:00:00"
        elif '/' in date_str:
            date_part = date_str.split(',')[0].strip()
            return datetime.strptime(date_part, '%d/%m/%Y')
    except Exception as e:
        print(f"[ERRO] Falha ao parsear data: {date_str} - {e}")
        return None

def normalize_price(price_str) -> float:
    """Normaliza preço removendo símbolos e vírgulas."""
    if isinstance(price_str, (int, float)):
        return float(price_str)
    price_str = str(price_str).replace('$', '').replace(',', '').replace(' USDT', '').strip()
    try:
        return float(price_str)
    except:
        return 0.0

def calculate_metrics_from_trades(trades: List[Dict], initial_capital=100):
    """Calcula métricas agregadas a partir de trades usando compounding."""
    if not trades:
        return {
            'total_return_pct': 0,
            'total_pnl_usd': 0,
            'final_equity': initial_capital,
            'max_drawdown_pct': 0,
            'max_drawdown_usd': 0,
            'total_trades': 0,
            'win_rate': 0,
            'profit_factor': 0,
            'winning_trades': 0,
            'losing_trades': 0
        }
    
    # Ordenar trades por data de entrada (mais antigos primeiro)
    sorted_trades = sorted(trades, key=lambda x: parse_date(x.get('entry_date', x.get('entry_time', ''))) or datetime.min)
    
    # 1. Compounded Return
    equity = float(initial_capital)
    equity_curve = [equity]
    
    for t in sorted_trades:
        profit = t.get('profit', 0)
        if isinstance(profit, str):
            profit = float(profit.replace('%', '')) / 100.0
        equity *= (1.0 + profit)
        equity_curve.append(equity)
    
    total_return_pct = (equity / initial_capital - 1) * 100.0
    total_pnl_usd = equity - initial_capital
    
    # 2. Max Drawdown
    peak = initial_capital
    max_dd_pct = 0.0
    max_dd_usd = 0.0
    
    for eq in equity_curve:
        if eq > peak:
            peak = eq
        drawdown_pct = (peak - eq) / peak if peak > 0 else 0
        drawdown_usd = peak - eq
        if drawdown_pct > max_dd_pct:
            max_dd_pct = drawdown_pct
            max_dd_usd = drawdown_usd
    
    # 3. Win Rate
    total_trades = len(sorted_trades)
    winning_trades = sum(1 for t in sorted_trades if (t.get('profit', 0) if isinstance(t.get('profit', 0), (int, float)) else float(str(t.get('profit', 0)).replace('%', '')) / 100.0) > 0)
    losing_trades = total_trades - winning_trades
    win_rate = (winning_trades / total_trades) * 100.0 if total_trades > 0 else 0
    
    # 4. Profit Factor (com compounding)
    equity_current = float(initial_capital)
    gross_profit_usd = 0.0
    gross_loss_usd = 0.0
    
    for t in sorted_trades:
        profit = t.get('profit', 0)
        if isinstance(profit, str):
            profit = float(profit.replace('%', '')) / 100.0
        trade_pnl_usd = equity_current * profit
        if profit > 0:
            gross_profit_usd += trade_pnl_usd
        else:
            gross_loss_usd += abs(trade_pnl_usd)
        equity_current *= (1.0 + profit)
    
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
        'winning_trades': winning_trades,
        'losing_trades': losing_trades,
        'gross_profit_usd': gross_profit_usd,
        'gross_loss_usd': gross_loss_usd
    }

# Dados do TradingView - baseado na imagem fornecida
# Trades 55 a 48 (mais recentes primeiro na imagem, mas vamos ordenar cronologicamente)
TRADINGVIEW_TRADES = [
    # Trade 55 (mais recente)
    {
        'trade_num': 55,
        'entry_date': 'Jan 04, 2026',
        'entry_price': 3127.11,
        'exit_date': 'Jan 20, 2026',
        'exit_price': 2942.61,
        'signal': 'Stop',
        'profit_pct': -6.04,
        'profit_usd': -195.43,
        'cumulative_pnl_pct': 2940.27,
        'cumulative_pnl_usd': 2940.265
    },
    # Trade 54
    {
        'trade_num': 54,
        'entry_date': 'Oct 09, 2025',
        'entry_price': 4525.72,
        'exit_date': 'Oct 10, 2025',
        'exit_price': 4258.70,
        'signal': 'Stop',
        'profit_pct': -6.04,
        'profit_usd': -208.035,
        'cumulative_pnl_pct': 3135.70,
        'cumulative_pnl_usd': 3135.695
    },
    # Trade 53
    {
        'trade_num': 53,
        'entry_date': 'Sep 16, 2025',
        'entry_price': 4523.74,
        'exit_date': 'Sep 22, 2025',
        'exit_price': 4256.83,
        'signal': 'Stop',
        'profit_pct': -6.04,
        'profit_usd': -221.44,
        'cumulative_pnl_pct': 3343.73,
        'cumulative_pnl_usd': 3343.73
    },
    # Trade 52
    {
        'trade_num': 52,
        'entry_date': 'Aug 12, 2025',
        'entry_price': 4223.22,
        'exit_date': 'Aug 29, 2025',
        'exit_price': 4511.20,
        'signal': 'Close entry(s) order...',
        'profit_pct': 6.66,
        'profit_usd': 228.781,
        'cumulative_pnl_pct': 3565.17,
        'cumulative_pnl_usd': 3565.17
    },
    # Trade 51
    {
        'trade_num': 51,
        'entry_date': 'Jul 10, 2025',
        'entry_price': 2768.74,
        'exit_date': 'Aug 03, 2025',
        'exit_price': 3393.94,
        'signal': 'Close entry(s) order...',
        'profit_pct': 22.40,
        'profit_usd': 628.543,
        'cumulative_pnl_pct': 3336.39,
        'cumulative_pnl_usd': 3336.389
    },
    # Trade 50
    {
        'trade_num': 50,
        'entry_date': 'May 04, 2025',
        'entry_price': 1833.52,
        'exit_date': 'May 29, 2025',
        'exit_price': 2681.61,
        'signal': 'Close entry(s) order...',
        'profit_pct': 46.04,
        'profit_usd': 885.084,
        'cumulative_pnl_pct': 2707.85,
        'cumulative_pnl_usd': 2707.846
    },
    # Trade 49
    {
        'trade_num': 49,
        'entry_date': 'Nov 07, 2024',
        'entry_price': 2721.88,
        'exit_date': 'Dec 19, 2024',
        'exit_price': 3626.80,
        'signal': 'Close entry(s) order...',
        'profit_pct': 33.05,
        'profit_usd': 477.379,
        'cumulative_pnl_pct': 1822.76,
        'cumulative_pnl_usd': 1822.763
    },
    # Trade 48
    {
        'trade_num': 48,
        'entry_date': 'Oct 18, 2024',
        'entry_price': 2605.79,
        'exit_date': 'Oct 23, 2024',
        'exit_price': 2452.04,
        'signal': 'Stop',
        'profit_pct': -6.04,
        'profit_usd': -92.889,
        'cumulative_pnl_pct': 1345.38,
        'cumulative_pnl_usd': 1345.384
    },
]

# Dados do Sistema - baseado na planilha fornecida
# Primeiros 8 trades (mais recentes) da planilha
SYSTEM_TRADES_SAMPLE = [
    {
        'entry_time': '2026-01-04T00:00:00+00:00',
        'entry_price': 3127.11,
        'exit_time': '2026-01-20T00:00:00+00:00',
        'exit_price': 2942.61051,
        'trade_type': 'LONG',
        'signal': 'Stop',
        'pnl_usd': -195.45,
        'return_pct': -6.04,
        'initial_capital': 3235.71,
        'final_capital': 3040.26
    },
    {
        'entry_time': '2025-10-09T00:00:00+00:00',
        'entry_price': 4525.72,
        'exit_time': '2025-10-10T00:00:00+00:00',
        'exit_price': 4258.70,
        'trade_type': 'LONG',
        'signal': 'Stop',
        'pnl_usd': -208.04,
        'return_pct': -6.04,
        'initial_capital': 3443.75,
        'final_capital': 3235.71
    },
    {
        'entry_time': '2025-09-16T00:00:00+00:00',
        'entry_price': 4523.74,
        'exit_time': '2025-09-22T00:00:00+00:00',
        'exit_price': 4256.83,
        'trade_type': 'LONG',
        'signal': 'Stop',
        'pnl_usd': -221.44,
        'return_pct': -6.04,
        'initial_capital': 3665.19,
        'final_capital': 3443.75
    },
    {
        'entry_time': '2025-08-12T00:00:00+00:00',
        'entry_price': 4223.22,
        'exit_time': '2025-08-29T00:00:00+00:00',
        'exit_price': 4511.20,
        'trade_type': 'LONG',
        'signal': 'Close entry(s) order...',
        'pnl_usd': 228.79,
        'return_pct': 6.66,
        'initial_capital': 3436.40,
        'final_capital': 3665.19
    },
    {
        'entry_time': '2025-07-10T00:00:00+00:00',
        'entry_price': 2768.74,
        'exit_time': '2025-08-03T00:00:00+00:00',
        'exit_price': 3393.94,
        'trade_type': 'LONG',
        'signal': 'Close entry(s) order...',
        'pnl_usd': 628.54,
        'return_pct': 22.40,
        'initial_capital': 2807.86,
        'final_capital': 3436.40
    },
    {
        'entry_time': '2025-05-04T00:00:00+00:00',
        'entry_price': 1833.52,
        'exit_time': '2025-05-29T00:00:00+00:00',
        'exit_price': 2681.61,
        'trade_type': 'LONG',
        'signal': 'Close entry(s) order...',
        'pnl_usd': 885.08,
        'return_pct': 46.04,
        'initial_capital': 1922.78,
        'final_capital': 2807.86
    },
    {
        'entry_time': '2024-11-07T00:00:00+00:00',
        'entry_price': 2721.88,
        'exit_time': '2024-12-19T00:00:00+00:00',
        'exit_price': 3626.80,
        'trade_type': 'LONG',
        'signal': 'Close entry(s) order...',
        'pnl_usd': 477.38,
        'return_pct': 33.05,
        'initial_capital': 1445.40,
        'final_capital': 1922.78
    },
    {
        'entry_time': '2024-10-18T00:00:00+00:00',
        'entry_price': 2605.79,
        'exit_time': '2024-10-23T00:00:00+00:00',
        'exit_price': 2452.04,
        'trade_type': 'LONG',
        'signal': 'Stop',
        'pnl_usd': -92.89,
        'return_pct': -6.04,
        'initial_capital': 1538.29,
        'final_capital': 1445.40
    },
]

def normalize_system_trade(trade: Dict) -> Dict:
    """Normaliza trade do sistema para formato padrão."""
    entry_date = parse_date(trade.get('entry_time', ''))
    exit_date = parse_date(trade.get('exit_time', ''))
    
    profit_pct = trade.get('return_pct', 0)
    if isinstance(profit_pct, str):
        profit_pct = float(profit_pct.replace('%', ''))
    profit_pct = profit_pct / 100.0  # Converter para decimal
    
    return {
        'entry_date': entry_date,
        'entry_price': normalize_price(trade.get('entry_price', 0)),
        'exit_date': exit_date,
        'exit_price': normalize_price(trade.get('exit_price', 0)),
        'signal': trade.get('signal', ''),
        'profit': profit_pct,
        'profit_usd': trade.get('pnl_usd', 0),
        'initial_capital': trade.get('initial_capital', 100),
        'final_capital': trade.get('final_capital', 100)
    }

def normalize_tradingview_trade(trade: Dict) -> Dict:
    """Normaliza trade do TradingView para formato padrão."""
    entry_date = parse_date(trade.get('entry_date', ''))
    exit_date = parse_date(trade.get('exit_date', ''))
    
    profit_pct = trade.get('profit_pct', 0) / 100.0  # Converter para decimal
    
    return {
        'entry_date': entry_date,
        'entry_price': normalize_price(trade.get('entry_price', 0)),
        'exit_date': exit_date,
        'exit_price': normalize_price(trade.get('exit_price', 0)),
        'signal': trade.get('signal', ''),
        'profit': profit_pct,
        'profit_usd': trade.get('profit_usd', 0),
        'cumulative_pnl_pct': trade.get('cumulative_pnl_pct', 0),
        'cumulative_pnl_usd': trade.get('cumulative_pnl_usd', 0)
    }

def compare_trades(system_trades: List[Dict], tradingview_trades: List[Dict]):
    """Compara trades do sistema com TradingView."""
    print("\n" + "="*100)
    print("COMPARACAO DE TRADES: Sistema vs TradingView")
    print("="*100)
    
    # Normalizar trades
    sys_normalized = [normalize_system_trade(t) for t in system_trades]
    tv_normalized = [normalize_tradingview_trade(t) for t in tradingview_trades]
    
    # Ordenar por data de entrada
    sys_sorted = sorted(sys_normalized, key=lambda x: x['entry_date'] or datetime.min)
    tv_sorted = sorted(tv_normalized, key=lambda x: x['entry_date'] or datetime.min)
    
    print(f"\nTotal de trades para comparacao:")
    print(f"   Sistema: {len(sys_sorted)}")
    print(f"   TradingView: {len(tv_sorted)}")
    
    matches = 0
    mismatches = []
    
    # Comparar cada trade
    for i, sys_t in enumerate(sys_sorted):
        if not sys_t['entry_date']:
            continue
            
        print(f"\n{'='*100}")
        print(f"TRADE #{i+1} (Sistema)")
        print(f"{'='*100}")
        print(f"   Entry: {sys_t['entry_date'].strftime('%Y-%m-%d') if sys_t['entry_date'] else 'N/A'} @ ${sys_t['entry_price']:.2f}")
        print(f"   Exit:  {sys_t['exit_date'].strftime('%Y-%m-%d') if sys_t['exit_date'] else 'N/A'} @ ${sys_t['exit_price']:.2f}")
        print(f"   Signal: {sys_t['signal']}")
        print(f"   Profit: {sys_t['profit']*100:.2f}% (${sys_t['profit_usd']:.2f})")
        
        # Procurar trade correspondente no TradingView
        best_match = None
        best_score = 0
        
        for tv_t in tv_sorted:
            if not tv_t['entry_date']:
                continue
                
            # Calcular score de correspondência
            score = 0
            
            # Data de entrada (tolerância de 1 dia)
            if sys_t['entry_date'] and tv_t['entry_date']:
                days_diff = abs((sys_t['entry_date'] - tv_t['entry_date']).days)
                if days_diff == 0:
                    score += 5
                elif days_diff <= 1:
                    score += 3
                elif days_diff <= 3:
                    score += 1
            
            # Preço de entrada (tolerância de 1%)
            if sys_t['entry_price'] > 0 and tv_t['entry_price'] > 0:
                entry_price_diff = abs(sys_t['entry_price'] - tv_t['entry_price']) / sys_t['entry_price']
                if entry_price_diff < 0.01:
                    score += 3
                elif entry_price_diff < 0.05:
                    score += 1
            
            # Data de saída
            if sys_t['exit_date'] and tv_t['exit_date']:
                days_diff = abs((sys_t['exit_date'] - tv_t['exit_date']).days)
                if days_diff == 0:
                    score += 2
                elif days_diff <= 1:
                    score += 1
            
            # Preço de saída
            if sys_t['exit_price'] > 0 and tv_t['exit_price'] > 0:
                exit_price_diff = abs(sys_t['exit_price'] - tv_t['exit_price']) / sys_t['exit_price']
                if exit_price_diff < 0.01:
                    score += 2
                elif exit_price_diff < 0.05:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_match = {
                    'tv_trade': tv_t,
                    'score': score,
                    'entry_date_diff': abs((sys_t['entry_date'] - tv_t['entry_date']).days) if sys_t['entry_date'] and tv_t['entry_date'] else None,
                    'entry_price_diff': entry_price_diff if sys_t['entry_price'] > 0 and tv_t['entry_price'] > 0 else None,
                    'exit_date_diff': abs((sys_t['exit_date'] - tv_t['exit_date']).days) if sys_t['exit_date'] and tv_t['exit_date'] else None,
                    'exit_price_diff': exit_price_diff if sys_t['exit_price'] > 0 and tv_t['exit_price'] > 0 else None
                }
        
        if best_match and best_score >= 5:
            tv_t = best_match['tv_trade']
            print(f"\n   [MATCH] TradingView Trade encontrado (score: {best_score}/12):")
            print(f"   Entry: {tv_t['entry_date'].strftime('%Y-%m-%d') if tv_t['entry_date'] else 'N/A'} @ ${tv_t['entry_price']:.2f}")
            print(f"   Exit:  {tv_t['exit_date'].strftime('%Y-%m-%d') if tv_t['exit_date'] else 'N/A'} @ ${tv_t['exit_price']:.2f}")
            print(f"   Signal: {tv_t['signal']}")
            print(f"   Profit: {tv_t['profit']*100:.2f}% (${tv_t['profit_usd']:.2f})")
            
            if best_match['entry_date_diff'] and best_match['entry_date_diff'] > 0:
                print(f"   [DIFERENCA] Entry date: {best_match['entry_date_diff']} dias")
            if best_match['entry_price_diff'] and best_match['entry_price_diff'] > 0.01:
                print(f"   [DIFERENCA] Entry price: {best_match['entry_price_diff']*100:.2f}%")
            if best_match['exit_date_diff'] and best_match['exit_date_diff'] > 0:
                print(f"   [DIFERENCA] Exit date: {best_match['exit_date_diff']} dias")
            if best_match['exit_price_diff'] and best_match['exit_price_diff'] > 0.01:
                print(f"   [DIFERENCA] Exit price: {best_match['exit_price_diff']*100:.2f}%")
            
            matches += 1
        else:
            print(f"\n   [ERRO] Trade do sistema nao encontrado no TradingView!")
            mismatches.append({
                'system_trade': sys_t,
                'index': i+1
            })
    
    print(f"\n{'='*100}")
    print(f"RESUMO DA COMPARACAO:")
    print(f"{'='*100}")
    print(f"   Trades correspondentes: {matches}/{len(sys_sorted)}")
    print(f"   Trades nao encontrados: {len(mismatches)}")
    
    # Calcular métricas agregadas
    print(f"\n{'='*100}")
    print(f"METRICAS AGREGADAS:")
    print(f"{'='*100}")
    
    # Converter trades para formato de cálculo
    sys_trades_for_calc = [{'profit': t['profit']} for t in sys_sorted]
    tv_trades_for_calc = [{'profit': t['profit']} for t in tv_sorted]
    
    sys_metrics = calculate_metrics_from_trades(sys_trades_for_calc, 100)
    tv_metrics = calculate_metrics_from_trades(tv_trades_for_calc, 100)
    
    print(f"\n[METRICAS] SISTEMA (baseado nos {len(sys_sorted)} trades):")
    print(f"   Total Return: {sys_metrics['total_return_pct']:.2f}%")
    print(f"   Total P&L: ${sys_metrics['total_pnl_usd']:.2f}")
    print(f"   Max Drawdown: {sys_metrics['max_drawdown_pct']:.2f}%")
    print(f"   Win Rate: {sys_metrics['win_rate']:.2f}% ({sys_metrics['winning_trades']}/{sys_metrics['total_trades']})")
    print(f"   Profit Factor: {sys_metrics['profit_factor']:.3f}")
    
    print(f"\n[METRICAS] TRADINGVIEW (baseado nos {len(tv_sorted)} trades):")
    print(f"   Total Return: {tv_metrics['total_return_pct']:.2f}%")
    print(f"   Total P&L: ${tv_metrics['total_pnl_usd']:.2f}")
    print(f"   Max Drawdown: {tv_metrics['max_drawdown_pct']:.2f}%")
    print(f"   Win Rate: {tv_metrics['win_rate']:.2f}% ({tv_metrics['winning_trades']}/{tv_metrics['total_trades']})")
    print(f"   Profit Factor: {tv_metrics['profit_factor']:.3f}")
    
    print(f"\n[COMPARACAO] DIFERENCAS:")
    print(f"   Return: {abs(sys_metrics['total_return_pct'] - tv_metrics['total_return_pct']):.2f}%")
    print(f"   Max DD: {abs(sys_metrics['max_drawdown_pct'] - tv_metrics['max_drawdown_pct']):.2f}%")
    print(f"   Win Rate: {abs(sys_metrics['win_rate'] - tv_metrics['win_rate']):.2f}%")
    print(f"   Profit Factor: {abs(sys_metrics['profit_factor'] - tv_metrics['profit_factor']):.3f}")
    
    print("\n" + "="*100)

if __name__ == "__main__":
    print("COMPARACAO DE TRADES: Sistema vs TradingView")
    print("\nEste script compara trades individuais e metricas agregadas.")
    print("Baseado nas planilhas e imagens fornecidas.")
    
    compare_trades(SYSTEM_TRADES_SAMPLE, TRADINGVIEW_TRADES)
    
    print("\n" + "="*100)
    print("OBSERVACOES:")
    print("="*100)
    print("1. Esta comparacao usa apenas os 8 trades mais recentes (visiveis nas imagens)")
    print("2. Para comparacao completa, precisamos de todos os 55 trades")
    print("3. O sistema mostra capital inicial/final por trade (compounding visivel)")
    print("4. TradingView mostra P&L cumulativo que tambem demonstra compounding")
