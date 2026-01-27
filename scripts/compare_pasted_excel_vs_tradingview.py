"""
Script para comparar dados colados do Excel (Sistema) com TradingView.

Uso:
    Cole os dados do Excel aqui no formato CSV ou use como argumento:
    python compare_pasted_excel_vs_tradingview.py "dados_colados.txt"
"""

import sys
import os
import csv
import io
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
        if 'T' in date_str:
            date_part = date_str.split('T')[0]
            return datetime.strptime(date_part, '%Y-%m-%d')
        elif ',' in date_str and len(date_str.split(',')) == 2:
            return datetime.strptime(date_str.strip(), '%b %d, %Y')
        elif '/' in date_str:
            date_part = date_str.split(',')[0].strip()
            return datetime.strptime(date_part, '%d/%m/%Y')
    except:
        return None

def normalize_price(price_str) -> float:
    """Normaliza preço."""
    if isinstance(price_str, (int, float)):
        return float(price_str)
    price_str = str(price_str).replace('$', '').replace(',', '').replace(' USDT', '').strip()
    try:
        return float(price_str)
    except:
        return 0.0

# Dados completos do TradingView extraídos das imagens
# Ordenados do mais antigo (1) para o mais recente (55)
TRADINGVIEW_ALL_TRADES = [
    # Trades 1-8 (mais antigos)
    {'trade_num': 1, 'entry_date': 'Oct 13, 2017', 'entry_price': 303.99, 'exit_date': 'Oct 18, 2017', 'exit_price': 286.05, 'signal': 'Stop', 'profit_pct': -6.04},
    {'trade_num': 2, 'entry_date': 'Nov 15, 2017', 'entry_price': 335.60, 'exit_date': 'Dec 11, 2017', 'exit_price': 427.40, 'signal': 'Close entry(s) order...', 'profit_pct': 27.16},
    {'trade_num': 3, 'entry_date': 'Dec 13, 2017', 'entry_price': 619.40, 'exit_date': 'Dec 13, 2017', 'exit_price': 582.85, 'signal': 'Stop', 'profit_pct': -6.04},
    {'trade_num': 4, 'entry_date': 'Jan 05, 2018', 'entry_price': 940.00, 'exit_date': 'Jan 16, 2018', 'exit_price': 884.54, 'signal': 'Stop', 'profit_pct': -6.04},
    {'trade_num': 5, 'entry_date': 'Apr 22, 2018', 'entry_price': 604.87, 'exit_date': 'May 13, 2018', 'exit_price': 684.56, 'signal': 'Close entry(s) order...', 'profit_pct': 13.01},
    {'trade_num': 6, 'entry_date': 'Dec 30, 2018', 'entry_price': 133.00, 'exit_date': 'Jan 10, 2019', 'exit_price': 125.15, 'signal': 'Stop', 'profit_pct': -6.04},
    {'trade_num': 7, 'entry_date': 'Feb 19, 2019', 'entry_price': 145.69, 'exit_date': 'Feb 24, 2019', 'exit_price': 137.09, 'signal': 'Stop', 'profit_pct': -6.04},
    {'trade_num': 8, 'entry_date': 'Mar 19, 2019', 'entry_price': 137.62, 'exit_date': 'Mar 28, 2019', 'exit_price': 139.46, 'signal': 'Close entry(s) order...', 'profit_pct': 1.19},
    # Trades 10-17 (intermediários antigos)
    {'trade_num': 10, 'entry_date': 'May 11, 2019', 'entry_price': 172.92, 'exit_date': 'Jun 04, 2019', 'exit_price': 250.02, 'signal': 'Close entry(s) order...', 'profit_pct': 44.37},
    {'trade_num': 11, 'entry_date': 'Jun 21, 2019', 'entry_price': 271.27, 'exit_date': 'Jul 07, 2019', 'exit_price': 288.29, 'signal': 'Close entry(s) order...', 'profit_pct': 6.11},
    {'trade_num': 12, 'entry_date': 'Sep 20, 2019', 'entry_price': 220.26, 'exit_date': 'Sep 22, 2019', 'exit_price': 207.26, 'signal': 'Stop', 'profit_pct': -6.04},
    {'trade_num': 13, 'entry_date': 'Nov 03, 2019', 'entry_price': 182.90, 'exit_date': 'Nov 17, 2019', 'exit_price': 182.37, 'signal': 'Close entry(s) order...', 'profit_pct': -0.44},
    {'trade_num': 14, 'entry_date': 'Jan 13, 2020', 'entry_price': 146.56, 'exit_date': 'Feb 27, 2020', 'exit_price': 223.98, 'signal': 'Close entry(s) order...', 'profit_pct': 52.60},
    {'trade_num': 15, 'entry_date': 'Apr 17, 2020', 'entry_price': 172.31, 'exit_date': 'May 12, 2020', 'exit_price': 185.80, 'signal': 'Close entry(s) order...', 'profit_pct': 7.67},
    {'trade_num': 16, 'entry_date': 'May 29, 2020', 'entry_price': 220.24, 'exit_date': 'Jun 17, 2020', 'exit_price': 235.31, 'signal': 'Close entry(s) order...', 'profit_pct': 6.68},
    {'trade_num': 17, 'entry_date': 'Jul 14, 2020', 'entry_price': 239.50, 'exit_date': 'Aug 22, 2020', 'exit_price': 301.99, 'signal': 'Close entry(s) order...', 'profit_pct': 61.73},
    # Trades 18-25 (intermediários)
    {'trade_num': 18, 'entry_date': 'Oct 15, 2020', 'entry_price': 378.69, 'exit_date': 'Nov 03, 2020', 'exit_price': 383.01, 'signal': 'Close entry(s) order...', 'profit_pct': 0.99},
    {'trade_num': 19, 'entry_date': 'Nov 06, 2020', 'entry_price': 416.73, 'exit_date': 'Dec 10, 2020', 'exit_price': 573.20, 'signal': 'Close entry(s) order...', 'profit_pct': 37.34},
    {'trade_num': 20, 'entry_date': 'Dec 18, 2020', 'entry_price': 642.71, 'exit_date': 'Dec 21, 2020', 'exit_price': 604.79, 'signal': 'Stop', 'profit_pct': -6.04},
    {'trade_num': 21, 'entry_date': 'Feb 02, 2021', 'entry_price': 1374.09, 'exit_date': 'Feb 24, 2021', 'exit_price': 1577.79, 'signal': 'Close entry(s) order...', 'profit_pct': 14.65},
    {'trade_num': 22, 'entry_date': 'Mar 13, 2021', 'entry_price': 1766.13, 'exit_date': 'Mar 22, 2021', 'exit_price': 1661.92, 'signal': 'Stop', 'profit_pct': -6.04},
    {'trade_num': 23, 'entry_date': 'Mar 30, 2021', 'entry_price': 1816.76, 'exit_date': 'May 20, 2021', 'exit_price': 2438.92, 'signal': 'Close entry(s) order...', 'profit_pct': 34.04},
    {'trade_num': 24, 'entry_date': 'Jul 29, 2021', 'entry_price': 2300.90, 'exit_date': 'Aug 25, 2021', 'exit_price': 3170.63, 'signal': 'Close entry(s) order...', 'profit_pct': 37.59},
    {'trade_num': 25, 'entry_date': 'Sep 03, 2021', 'entry_price': 3785.82, 'exit_date': 'Sep 07, 2021', 'exit_price': 3562.45, 'signal': 'Stop', 'profit_pct': -6.04},
    # Trades 42-49 (intermediários recentes)
    {'trade_num': 42, 'entry_date': 'Jan 02, 2024', 'entry_price': 2352.05, 'exit_date': 'Jan 03, 2024', 'exit_price': 2213.27, 'signal': 'Stop', 'profit_pct': -6.04},
    {'trade_num': 43, 'entry_date': 'Jan 11, 2024', 'entry_price': 2584.37, 'exit_date': 'Jan 18, 2024', 'exit_price': 2431.89, 'signal': 'Stop', 'profit_pct': -6.04},
    {'trade_num': 44, 'entry_date': 'Feb 11, 2024', 'entry_price': 2500.24, 'exit_date': 'Mar 19, 2024', 'exit_price': 3520.47, 'signal': 'Close entry(s) order...', 'profit_pct': 40.59},
    {'trade_num': 45, 'entry_date': 'May 22, 2024', 'entry_price': 3789.59, 'exit_date': 'May 23, 2024', 'exit_price': 3566.00, 'signal': 'Stop', 'profit_pct': -6.04},
    {'trade_num': 46, 'entry_date': 'Jul 24, 2024', 'entry_price': 3482.51, 'exit_date': 'Jul 25, 2024', 'exit_price': 3277.04, 'signal': 'Stop', 'profit_pct': -6.04},
    {'trade_num': 47, 'entry_date': 'Sep 27, 2024', 'entry_price': 2632.25, 'exit_date': 'Oct 01, 2024', 'exit_price': 2476.94, 'signal': 'Stop', 'profit_pct': -6.04},
    {'trade_num': 48, 'entry_date': 'Oct 18, 2024', 'entry_price': 2605.79, 'exit_date': 'Oct 23, 2024', 'exit_price': 2452.04, 'signal': 'Stop', 'profit_pct': -6.04},
    {'trade_num': 49, 'entry_date': 'Nov 07, 2024', 'entry_price': 2721.88, 'exit_date': 'Dec 19, 2024', 'exit_price': 3626.80, 'signal': 'Close entry(s) order...', 'profit_pct': 33.05},
    # Trades 50-55 (mais recentes)
    {'trade_num': 50, 'entry_date': 'May 04, 2025', 'entry_price': 1833.52, 'exit_date': 'May 29, 2025', 'exit_price': 2681.61, 'signal': 'Close entry(s) order...', 'profit_pct': 46.04},
    {'trade_num': 51, 'entry_date': 'Jul 10, 2025', 'entry_price': 2768.74, 'exit_date': 'Aug 03, 2025', 'exit_price': 3393.94, 'signal': 'Close entry(s) order...', 'profit_pct': 22.40},
    {'trade_num': 52, 'entry_date': 'Aug 12, 2025', 'entry_price': 4223.22, 'exit_date': 'Aug 29, 2025', 'exit_price': 4511.20, 'signal': 'Close entry(s) order...', 'profit_pct': 6.66},
    {'trade_num': 53, 'entry_date': 'Sep 16, 2025', 'entry_price': 4523.74, 'exit_date': 'Sep 22, 2025', 'exit_price': 4256.83, 'signal': 'Stop', 'profit_pct': -6.04},
    {'trade_num': 54, 'entry_date': 'Oct 09, 2025', 'entry_price': 4525.72, 'exit_date': 'Oct 10, 2025', 'exit_price': 4258.70, 'signal': 'Stop', 'profit_pct': -6.04},
    {'trade_num': 55, 'entry_date': 'Jan 04, 2026', 'entry_price': 3127.11, 'exit_date': 'Jan 20, 2026', 'exit_price': 2942.61, 'signal': 'Stop', 'profit_pct': -6.04},
]

def parse_pasted_data(data_text: str) -> List[Dict]:
    """Parse dados colados do Excel."""
    trades = []
    lines = data_text.strip().split('\n')
    
    # Tentar detectar se é CSV ou TSV
    delimiter = '\t' if '\t' in lines[0] else ','
    
    # Tentar ler como CSV
    reader = csv.DictReader(io.StringIO(data_text), delimiter=delimiter)
    
    for row in reader:
        # Normalizar nomes de colunas
        normalized = {k.lower().strip().replace(' ', '_').replace('&', '').replace('(', '').replace(')', ''): v for k, v in row.items()}
        
        trade = {
            'entry_time': normalized.get('entry_time', normalized.get('entrytime', '')),
            'entry_price': normalize_price(normalized.get('entry_price', normalized.get('entryprice', 0))),
            'exit_time': normalized.get('exit_time', normalized.get('exittime', '')),
            'exit_price': normalize_price(normalized.get('exit_price', normalized.get('exitprice', 0))),
            'signal': normalized.get('signal', normalized.get('signal_type', '')),
            'return_pct': normalized.get('return_%', normalized.get('return', normalized.get('profit', 0))),
            'pnl_usd': normalized.get('p&l_(usd)', normalized.get('pnl_usd', normalized.get('pnl', 0))),
        }
        
        # Converter return_pct para número
        if isinstance(trade['return_pct'], str):
            trade['return_pct'] = float(trade['return_pct'].replace('%', '').replace(',', '.'))
        
        trades.append(trade)
    
    return trades

def compare_all_trades(system_trades: List[Dict], tradingview_trades: List[Dict]):
    """Compara todos os trades."""
    print("\n" + "="*100)
    print("COMPARACAO COMPLETA: Sistema (Excel) vs TradingView")
    print("="*100)
    
    # Ordenar trades do TradingView por data
    tv_sorted = sorted(tradingview_trades, key=lambda x: parse_date(x.get('entry_date', '')) or datetime.min)
    
    print(f"\nTotal de trades:")
    print(f"   Sistema: {len(system_trades)}")
    print(f"   TradingView: {len(tv_sorted)}")
    
    matches = 0
    differences = []
    not_found = []
    
    for sys_trade in system_trades:
        sys_entry_date = parse_date(sys_trade.get('entry_time', ''))
        sys_entry_price = sys_trade.get('entry_price', 0)
        sys_exit_date = parse_date(sys_trade.get('exit_time', ''))
        sys_exit_price = sys_trade.get('exit_price', 0)
        sys_profit_pct = sys_trade.get('return_pct', 0)
        sys_signal = sys_trade.get('signal', '')
        
        if not sys_entry_date or not sys_entry_price:
            continue
        
        # Procurar match
        best_match = None
        best_score = 0
        
        for tv_trade in tv_sorted:
            tv_entry_date = parse_date(tv_trade.get('entry_date', ''))
            tv_entry_price = tv_trade.get('entry_price', 0)
            
            if not tv_entry_date:
                continue
            
            score = 0
            if sys_entry_date and tv_entry_date:
                days_diff = abs((sys_entry_date - tv_entry_date).days)
                if days_diff == 0:
                    score += 5
                elif days_diff <= 1:
                    score += 3
            
            if sys_entry_price > 0 and tv_entry_price > 0:
                price_diff = abs(sys_entry_price - tv_entry_price) / sys_entry_price
                if price_diff < 0.01:
                    score += 3
                elif price_diff < 0.05:
                    score += 1
            
            if score > best_score:
                best_score = score
                tv_exit_date = parse_date(tv_trade.get('exit_date', ''))
                tv_exit_price = tv_trade.get('exit_price', 0)
                tv_profit_pct = tv_trade.get('profit_pct', 0)
                tv_signal = tv_trade.get('signal', '')
                
                best_match = {
                    'tv_trade': tv_trade,
                    'score': score,
                    'entry_date_diff': abs((sys_entry_date - tv_entry_date).days) if sys_entry_date and tv_entry_date else None,
                    'entry_price_diff': abs(sys_entry_price - tv_entry_price) / sys_entry_price if sys_entry_price > 0 and tv_entry_price > 0 else None,
                    'exit_date_diff': abs((sys_exit_date - tv_exit_date).days) if sys_exit_date and tv_exit_date else None,
                    'exit_price_diff': abs(sys_exit_price - tv_exit_price) / sys_exit_price if sys_exit_price > 0 and tv_exit_price > 0 else None,
                    'profit_diff': abs(sys_profit_pct - tv_profit_pct),
                    'signal_match': sys_signal == tv_signal
                }
        
        if best_match and best_score >= 5:
            matches += 1
            tv_t = best_match['tv_trade']
            
            # Verificar diferenças
            diffs = []
            if best_match['entry_date_diff'] and best_match['entry_date_diff'] > 0:
                diffs.append(f"Entry date: {best_match['entry_date_diff']}d")
            if best_match['entry_price_diff'] and best_match['entry_price_diff'] > 0.01:
                diffs.append(f"Entry price: {best_match['entry_price_diff']*100:.2f}%")
            if best_match['exit_date_diff'] and best_match['exit_date_diff'] > 0:
                diffs.append(f"Exit date: {best_match['exit_date_diff']}d")
            if best_match['exit_price_diff'] and best_match['exit_price_diff'] > 0.01:
                diffs.append(f"Exit price: {best_match['exit_price_diff']*100:.2f}%")
            if best_match['profit_diff'] > 0.1:
                diffs.append(f"Profit: {best_match['profit_diff']:.2f}%")
            if not best_match['signal_match']:
                diffs.append(f"Signal: '{sys_signal}' vs '{tv_t.get('signal', '')}'")
            
            if diffs:
                differences.append({
                    'sys': sys_trade,
                    'tv': tv_t,
                    'diffs': diffs
                })
        else:
            not_found.append(sys_trade)
    
    print(f"\n{'='*100}")
    print(f"RESUMO:")
    print(f"{'='*100}")
    print(f"   Matches: {matches}/{len(system_trades)} ({matches/len(system_trades)*100:.1f}%)")
    print(f"   Com diferencas: {len(differences)}")
    print(f"   Nao encontrados: {len(not_found)}")
    
    if differences:
        print(f"\n{'='*100}")
        print(f"TRADES COM DIFERENCAS ({len(differences)}):")
        print(f"{'='*100}")
        for i, diff in enumerate(differences[:30], 1):
            sys_t = diff['sys']
            tv_t = diff['tv']
            print(f"\n[{i}] Trade Sistema: {sys_t.get('entry_time', 'N/A')} @ ${sys_t.get('entry_price', 0):.2f}")
            print(f"    Trade TradingView #{tv_t.get('trade_num', '?')}: {tv_t.get('entry_date', 'N/A')} @ ${tv_t.get('entry_price', 0):.2f}")
            print(f"    Diferencas: {', '.join(diff['diffs'])}")
    
    if not_found:
        print(f"\n{'='*100}")
        print(f"TRADES NAO ENCONTRADOS ({len(not_found)}):")
        print(f"{'='*100}")
        for i, trade in enumerate(not_found[:20], 1):
            print(f"  [{i}] Entry: {trade.get('entry_time', 'N/A')} @ ${trade.get('entry_price', 0):.2f}")
    
    print("\n" + "="*100)

if __name__ == "__main__":
    print("COMPARACAO: Dados Excel (Sistema) vs TradingView")
    print("\nPara usar:")
    print("1. Cole os dados do Excel aqui no formato CSV")
    print("2. Ou salve como arquivo e passe como argumento")
    print("\nExemplo de formato esperado:")
    print("Entry Time,Entry Price,Exit Time,Exit Price,Signal,Return %")
    print("2026-01-04T00:00:00+00:00,3127.11,2026-01-20T00:00:00+00:00,2942.61,Stop,-6.04")
    
    # Se houver argumento, ler do arquivo
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            data = f.read()
        system_trades = parse_pasted_data(data)
        compare_all_trades(system_trades, TRADINGVIEW_ALL_TRADES)
    else:
        print("\n[AVISO] Nenhum arquivo fornecido. Use:")
        print(f"  python {sys.argv[0]} <arquivo.csv>")
        print("\nOu cole os dados diretamente no script.")
