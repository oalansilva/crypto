"""
Script para processar Excel completo e comparar com TradingView.

Uso:
    python process_excel_and_compare.py <arquivo.csv>
    
Ou cole os dados diretamente aqui.
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
    """Normaliza preço (suporta vírgula ou ponto como decimal)."""
    if isinstance(price_str, (int, float)):
        return float(price_str)
    # Substituir vírgula por ponto para números brasileiros
    price_str = str(price_str).replace('$', '').replace(' USDT', '').strip()
    # Se tem vírgula mas não tem ponto, provavelmente é decimal brasileiro
    if ',' in price_str and '.' not in price_str.replace(',', ''):
        price_str = price_str.replace(',', '.')
    # Remover separadores de milhar
    price_str = price_str.replace(',', '').replace('.', '', price_str.count('.') - 1) if price_str.count('.') > 1 else price_str.replace(',', '')
    try:
        return float(price_str)
    except:
        return 0.0

def normalize_percentage(perc_str) -> float:
    """Normaliza porcentagem."""
    if isinstance(perc_str, (int, float)):
        return float(perc_str)
    perc_str = str(perc_str).replace('%', '').replace(',', '.').strip()
    try:
        return float(perc_str)
    except:
        return 0.0

# Importar dados do TradingView
from compare_system_excel_vs_tradingview import TRADINGVIEW_ALL_TRADES

def read_csv_file(filepath: str) -> List[Dict]:
    """Lê arquivo CSV do Excel."""
    trades = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # Detectar delimitador
            sample = f.read(1024)
            f.seek(0)
            delimiter = '\t' if '\t' in sample else ';' if ';' in sample else ','
            
            reader = csv.DictReader(f, delimiter=delimiter)
            
            for row in reader:
                # Normalizar nomes de colunas
                normalized = {k.lower().strip().replace(' ', '_').replace('&', '').replace('(', '').replace(')', '').replace('%', ''): v for k, v in row.items()}
                
                trade = {
                    'entry_time': normalized.get('entry_time', normalized.get('entrytime', '')),
                    'entry_price': normalize_price(normalized.get('entry_price', normalized.get('entryprice', 0))),
                    'exit_time': normalized.get('exit_time', normalized.get('exittime', '')),
                    'exit_price': normalize_price(normalized.get('exit_price', normalized.get('exitprice', 0))),
                    'signal': normalized.get('signal', normalized.get('signal_type', '')),
                    'return_pct': normalize_percentage(normalized.get('return', normalized.get('return_pct', normalized.get('profit', 0)))),
                    'pnl_usd': normalize_price(normalized.get('p&l_usd', normalized.get('pnl_usd', normalized.get('pnl', 0)))),
                }
                
                if trade['entry_time'] and trade['entry_price']:
                    trades.append(trade)
        
        print(f"[OK] Lidos {len(trades)} trades de {filepath}")
        return trades
    
    except Exception as e:
        print(f"[ERRO] Falha ao ler {filepath}: {e}")
        return []

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
    perfect_matches = 0
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
            tv_exit_date = parse_date(tv_trade.get('exit_date', ''))
            tv_exit_price = tv_trade.get('exit_price', 0)
            tv_profit_pct = tv_trade.get('profit_pct', 0)
            tv_signal = tv_trade.get('signal', '')
            
            if not tv_entry_date:
                continue
            
            score = 0
            
            # Data de entrada
            if sys_entry_date and tv_entry_date:
                days_diff = abs((sys_entry_date - tv_entry_date).days)
                if days_diff == 0:
                    score += 5
                elif days_diff <= 1:
                    score += 3
            
            # Preço de entrada
            if sys_entry_price > 0 and tv_entry_price > 0:
                price_diff = abs(sys_entry_price - tv_entry_price) / sys_entry_price
                if price_diff < 0.01:
                    score += 3
                elif price_diff < 0.05:
                    score += 1
            
            if score > best_score:
                best_score = score
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
            
            # Verificar se é match perfeito
            is_perfect = (
                best_match['entry_date_diff'] == 0 and
                best_match['entry_price_diff'] < 0.01 and
                (not sys_exit_date or not tv_exit_date or best_match['exit_date_diff'] == 0) and
                (sys_exit_price == 0 or tv_exit_price == 0 or best_match['exit_price_diff'] < 0.01) and
                best_match['profit_diff'] < 0.1 and
                best_match['signal_match']
            )
            
            if is_perfect:
                perfect_matches += 1
            else:
                # Coletar diferenças
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
    print(f"RESUMO DA COMPARACAO:")
    print(f"{'='*100}")
    print(f"   Matches encontrados: {matches}/{len(system_trades)} ({matches/len(system_trades)*100:.1f}%)")
    print(f"   Matches perfeitos: {perfect_matches}/{len(system_trades)} ({perfect_matches/len(system_trades)*100:.1f}%)")
    print(f"   Com diferencas: {len(differences)}")
    print(f"   Nao encontrados: {len(not_found)}")
    
    if differences:
        print(f"\n{'='*100}")
        print(f"TRADES COM DIFERENCAS ({len(differences)}):")
        print(f"{'='*100}")
        for i, diff in enumerate(differences[:50], 1):
            sys_t = diff['sys']
            tv_t = diff['tv']
            entry_date_str = sys_t.get('entry_time', 'N/A')[:10] if sys_t.get('entry_time') else 'N/A'
            exit_date_str = sys_t.get('exit_time', 'N/A')[:10] if sys_t.get('exit_time') else 'N/A'
            print(f"\n[{i}] Sistema: {entry_date_str} @ ${sys_t.get('entry_price', 0):.2f} -> {exit_date_str} @ ${sys_t.get('exit_price', 0):.2f} ({sys_t.get('signal', 'N/A')}, {sys_t.get('return_pct', 0):.2f}%)")
            print(f"    TradingView #{tv_t.get('trade_num', '?')}: {tv_t.get('entry_date', 'N/A')} @ ${tv_t.get('entry_price', 0):.2f} -> {tv_t.get('exit_date', 'N/A')} @ ${tv_t.get('exit_price', 0):.2f} ({tv_t.get('signal', 'N/A')}, {tv_t.get('profit_pct', 0):.2f}%)")
            print(f"    Diferencas: {', '.join(diff['diffs'])}")
    
    if not_found:
        print(f"\n{'='*100}")
        print(f"TRADES NAO ENCONTRADOS NO TRADINGVIEW ({len(not_found)}):")
        print(f"{'='*100}")
        for i, trade in enumerate(not_found[:30], 1):
            entry_date_str = trade.get('entry_time', 'N/A')[:10] if trade.get('entry_time') else 'N/A'
            print(f"  [{i}] Entry: {entry_date_str} @ ${trade.get('entry_price', 0):.2f} ({trade.get('signal', 'N/A')}, {trade.get('return_pct', 0):.2f}%)")
    
    print("\n" + "="*100)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("COMPARACAO: Dados Excel (Sistema) vs TradingView")
        print("\nUso:")
        print(f"  python {sys.argv[0]} <arquivo.csv>")
        print("\nOu exporte o Excel para CSV e forneça o caminho do arquivo.")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    if not os.path.exists(filepath):
        print(f"[ERRO] Arquivo nao encontrado: {filepath}")
        sys.exit(1)
    
    print("="*100)
    print("PROCESSANDO ARQUIVO EXCEL/CSV")
    print("="*100)
    
    system_trades = read_csv_file(filepath)
    
    if not system_trades:
        print("[ERRO] Nenhum trade encontrado no arquivo!")
        sys.exit(1)
    
    compare_all_trades(system_trades, TRADINGVIEW_ALL_TRADES)
