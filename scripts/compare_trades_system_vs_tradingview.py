"""
Script para comparar trades individuais entre Sistema (preto) e TradingView (branco).

Baseado nas imagens fornecidas:
- Sistema mostra trades em ordem cronológica (mais antigos primeiro)
- TradingView mostra trades em ordem reversa (mais recentes primeiro)
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
    # Formato: "13/10/2017, 00:00:00" ou "Oct 04, 2017"
    try:
        if '/' in date_str:
            # Formato sistema: "13/10/2017, 00:00:00"
            date_part = date_str.split(',')[0].strip()
            return datetime.strptime(date_part, '%d/%m/%Y')
        else:
            # Formato TradingView: "Oct 04, 2017"
            return datetime.strptime(date_str, '%b %d, %Y')
    except:
        return None

def normalize_price(price_str: str) -> float:
    """Normaliza preço removendo símbolos."""
    if isinstance(price_str, (int, float)):
        return float(price_str)
    return float(str(price_str).replace('$', '').replace(',', '').strip())

def compare_trades(system_trades: List[Dict], tradingview_trades: List[Dict]):
    """
    Compara trades do sistema com TradingView.
    
    Args:
        system_trades: Lista de trades do sistema (ordem cronológica)
        tradingview_trades: Lista de trades do TradingView (ordem reversa)
    """
    print("\n" + "="*100)
    print("COMPARACAO DE TRADES: Sistema vs TradingView")
    print("="*100)
    
    # Reverter ordem do TradingView para comparar
    tv_trades_sorted = sorted(tradingview_trades, key=lambda x: parse_date(x.get('entry_date', '')) or datetime.min)
    
    print(f"\nTotal de trades:")
    print(f"   Sistema: {len(system_trades)}")
    print(f"   TradingView: {len(tradingview_trades)}")
    
    matches = 0
    mismatches = []
    
    # Comparar cada trade
    for i, sys_trade in enumerate(system_trades):
        sys_entry_date = parse_date(sys_trade.get('entry_time', ''))
        sys_entry_price = normalize_price(sys_trade.get('entry_price', 0))
        sys_exit_date = parse_date(sys_trade.get('exit_time', ''))
        sys_exit_price = normalize_price(sys_trade.get('exit_price', 0))
        sys_profit = sys_trade.get('profit', 0)
        sys_signal = sys_trade.get('signal_type', '')
        
        # Procurar trade correspondente no TradingView
        best_match = None
        best_score = 0
        
        for tv_trade in tv_trades_sorted:
            tv_entry_date = parse_date(tv_trade.get('entry_date', ''))
            tv_entry_price = normalize_price(tv_trade.get('entry_price', 0))
            tv_exit_date = parse_date(tv_trade.get('exit_date', ''))
            tv_exit_price = normalize_price(tv_trade.get('exit_price', 0))
            tv_profit_pct = tv_trade.get('profit_pct', 0)
            tv_signal = tv_trade.get('signal', '')
            
            if not all([sys_entry_date, tv_entry_date, sys_exit_date, tv_exit_date]):
                continue
            
            # Calcular score de correspondência
            score = 0
            
            # Data de entrada (tolerância de 1 dia)
            if abs((sys_entry_date - tv_entry_date).days) <= 1:
                score += 3
            elif abs((sys_entry_date - tv_entry_date).days) <= 3:
                score += 1
            
            # Preço de entrada (tolerância de 1%)
            entry_price_diff = abs(sys_entry_price - tv_entry_price) / sys_entry_price if sys_entry_price > 0 else 1
            if entry_price_diff < 0.01:
                score += 3
            elif entry_price_diff < 0.05:
                score += 1
            
            # Data de saída
            if abs((sys_exit_date - tv_exit_date).days) <= 1:
                score += 2
            elif abs((sys_exit_date - tv_exit_date).days) <= 3:
                score += 1
            
            # Preço de saída
            exit_price_diff = abs(sys_exit_price - tv_exit_price) / sys_exit_price if sys_exit_price > 0 else 1
            if exit_price_diff < 0.01:
                score += 2
            elif exit_price_diff < 0.05:
                score += 1
            
            if score > best_score:
                best_score = score
                best_match = {
                    'tv_trade': tv_trade,
                    'score': score,
                    'entry_date_diff': abs((sys_entry_date - tv_entry_date).days) if sys_entry_date and tv_entry_date else None,
                    'entry_price_diff': entry_price_diff,
                    'exit_date_diff': abs((sys_exit_date - tv_exit_date).days) if sys_exit_date and tv_exit_date else None,
                    'exit_price_diff': exit_price_diff
                }
        
        # Exibir comparação
        print(f"\n{'='*100}")
        print(f"TRADE #{i+1} (Sistema)")
        print(f"{'='*100}")
        print(f"   Entry: {sys_trade.get('entry_time', 'N/A')} @ ${sys_entry_price:.2f}")
        print(f"   Exit:  {sys_trade.get('exit_time', 'N/A')} @ ${sys_exit_price:.2f}")
        print(f"   Signal: {sys_signal}")
        print(f"   Profit: {sys_profit*100:.2f}%")
        
        if best_match and best_score >= 5:
            tv_t = best_match['tv_trade']
            print(f"\n   [MATCH] TradingView Trade encontrado (score: {best_score}/10):")
            print(f"   Entry: {tv_t.get('entry_date', 'N/A')} @ ${normalize_price(tv_t.get('entry_price', 0)):.2f}")
            print(f"   Exit:  {tv_t.get('exit_date', 'N/A')} @ ${normalize_price(tv_t.get('exit_price', 0)):.2f}")
            print(f"   Signal: {tv_t.get('signal', 'N/A')}")
            print(f"   Profit: {tv_t.get('profit_pct', 0):.2f}%")
            
            if best_match['entry_date_diff']:
                print(f"   [DIFERENCA] Entry date: {best_match['entry_date_diff']} dias")
            if best_match['entry_price_diff'] > 0.01:
                print(f"   [DIFERENCA] Entry price: {best_match['entry_price_diff']*100:.2f}%")
            if best_match['exit_date_diff']:
                print(f"   [DIFERENCA] Exit date: {best_match['exit_date_diff']} dias")
            if best_match['exit_price_diff'] > 0.01:
                print(f"   [DIFERENCA] Exit price: {best_match['exit_price_diff']*100:.2f}%")
            
            matches += 1
        else:
            print(f"\n   [ERRO] Trade do sistema nao encontrado no TradingView!")
            mismatches.append({
                'system_trade': sys_trade,
                'index': i+1
            })
    
    print(f"\n{'='*100}")
    print(f"RESUMO DA COMPARACAO:")
    print(f"{'='*100}")
    print(f"   Trades correspondentes: {matches}/{len(system_trades)}")
    print(f"   Trades nao encontrados: {len(mismatches)}")
    
    if mismatches:
        print(f"\n   Trades do sistema nao encontrados no TradingView:")
        for mm in mismatches:
            print(f"      Trade #{mm['index']}: Entry {mm['system_trade'].get('entry_time', 'N/A')}")
    
    print("\n" + "="*100)

# Dados do Sistema (tela preta) - baseado na imagem do sistema
SYSTEM_TRADES = [
    {
        'entry_time': '13/10/2017, 00:00:00',
        'entry_price': 303.52,
        'exit_time': '18/10/2017, 00:00:00',
        'exit_price': 285.61,
        'signal_type': 'Stop',
        'profit': -0.0604
    },
    {
        'entry_time': '15/11/2017, 00:00:00',
        'entry_price': 335.60,
        'exit_time': '11/12/2017, 00:00:00',
        'exit_price': 427.35,
        'signal_type': 'Close entry(s) order...',
        'profit': 0.2715
    },
    {
        'entry_time': '13/12/2017, 00:00:00',
        'entry_price': 622.00,
        'exit_time': '22/12/2017, 00:00:00',
        'exit_price': 585.30,
        'signal_type': 'Stop',
        'profit': -0.0604
    },
    {
        'entry_time': '05/01/2018, 00:00:00',
        'entry_price': 940.00,
        'exit_time': '16/01/2018, 00:00:00',
        'exit_price': 884.54,
        'signal_type': 'Stop',
        'profit': -0.0604
    },
    {
        'entry_time': '22/04/2018, 00:00:00',
        'entry_price': 604.87,
        'exit_time': '13/05/2018, 00:00:00',
        'exit_price': 684.56,
        'signal_type': 'Close entry(s) order...',
        'profit': 0.1301
    },
    {
        'entry_time': '30/12/2018, 00:00:00',
        'entry_price': 133.00,
        'exit_time': '10/01/2019, 00:00:00',
        'exit_price': 125.15,
        'signal_type': 'Stop',
        'profit': -0.0604
    },
    {
        'entry_time': '19/02/2019, 00:00:00',
        'entry_price': 145.69,
        'exit_time': '24/02/2019, 00:00:00',
        'exit_price': 137.09,
        'signal_type': 'Stop',
        'profit': -0.0604
    },
    {
        'entry_time': '19/03/2019, 00:00:00',
        'entry_price': 137.62,
        'exit_time': '28/03/2019, 00:00:00',
        'exit_price': 139.46,
        'signal_type': 'Close entry(s) order...',
        'profit': 0.0119
    }
]

# Dados do TradingView (tela branca) - CORRETOS baseado na nova imagem
# Ordem cronológica (mais antigos primeiro)
TRADINGVIEW_TRADES = [
    {
        'trade_num': 1,
        'entry_date': 'Oct 13, 2017',
        'entry_price': 303.99,
        'exit_date': 'Oct 18, 2017',
        'exit_price': 286.05,
        'signal': 'Stop',
        'profit_pct': -6.04,
        'profit_usd': -6.042
    },
    {
        'trade_num': 2,
        'entry_date': 'Nov 15, 2017',
        'entry_price': 335.60,
        'exit_date': 'Dec 11, 2017',
        'exit_price': 427.40,
        'signal': 'Close entry(s) order...',
        'profit_pct': 27.16,
        'profit_usd': 25.516
    },
    {
        'trade_num': 3,
        'entry_date': 'Dec 13, 2017',
        'entry_price': 619.40,
        'exit_date': 'Dec 13, 2017',  # Mesmo dia (stop loss imediato)
        'exit_price': 582.85,
        'signal': 'Stop',
        'profit_pct': -6.04,
        'profit_usd': -7.217
    },
    {
        'trade_num': 4,
        'entry_date': 'Jan 05, 2018',
        'entry_price': 940.00,
        'exit_date': 'Jan 16, 2018',
        'exit_price': 884.54,
        'signal': 'Stop',
        'profit_pct': -6.04,
        'profit_usd': -6.78
    },
    {
        'trade_num': 5,
        'entry_date': 'Apr 22, 2018',
        'entry_price': 604.87,
        'exit_date': 'May 13, 2018',
        'exit_price': 684.56,
        'signal': 'Close entry(s) order...',
        'profit_pct': 13.01,
        'profit_usd': 13.714
    },
    {
        'trade_num': 6,
        'entry_date': 'Dec 30, 2018',
        'entry_price': 133.00,
        'exit_date': 'Jan 10, 2019',
        'exit_price': 125.15,
        'signal': 'Stop',
        'profit_pct': -6.04,
        'profit_usd': -7.209
    },
    {
        'trade_num': 7,
        'entry_date': 'Feb 19, 2019',
        'entry_price': 145.69,
        'exit_date': 'Feb 24, 2019',
        'exit_price': 137.09,
        'signal': 'Stop',
        'profit_pct': -6.04,
        'profit_usd': -6.768
    },
    {
        'trade_num': 8,
        'entry_date': 'Mar 19, 2019',
        'entry_price': 137.62,
        'exit_date': 'Mar 28, 2019',
        'exit_price': 139.46,
        'signal': 'Close entry(s) order...',
        'profit_pct': 1.19,
        'profit_usd': 1.247
    }
]

if __name__ == "__main__":
    print("COMPARACAO DE TRADES: Sistema vs TradingView")
    print("\nEste script compara trades individuais entre o sistema e TradingView.")
    print("Baseado nas imagens fornecidas.")
    
    compare_trades(SYSTEM_TRADES, TRADINGVIEW_TRADES)
    
    print("\n" + "="*100)
    print("OBSERVACOES:")
    print("="*100)
    print("1. TradingView mostra comissões muito altas (60-90% do P&L bruto)")
    print("2. Isso faz com que muitos trades com P&L bruto positivo tenham Net P&L negativo")
    print("3. O sistema pode estar usando taxas diferentes (0.075% vs comissões altas do TV)")
    print("4. Alguns trades do TradingView têm datas inconsistentes (exit antes de entry)")
    print("5. As ordens podem estar diferentes (sistema: cronológica, TV: reversa)")
