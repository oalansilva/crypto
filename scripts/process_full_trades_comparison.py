"""
Script para processar planilha completa do sistema e comparar com TradingView.

Uso:
    python process_full_trades_comparison.py <arquivo_sistema.csv> [arquivo_tradingview.csv]

Se não fornecer arquivo TradingView, usará os dados conhecidos.
"""

import sys
import os
import csv
from datetime import datetime
from typing import List, Dict, Any

# Add project root and backend
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)
sys.path.append(os.path.join(project_root, 'backend'))

# Importar funções do script de comparação
from compare_all_trades_system_vs_tradingview import (
    parse_date, normalize_price, normalize_system_trade, 
    normalize_tradingview_trade, calculate_metrics_from_trades, compare_trades
)

def read_csv_trades(filepath: str) -> List[Dict]:
    """Lê trades de um arquivo CSV."""
    trades = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # Tentar detectar delimitador
            sample = f.read(1024)
            f.seek(0)
            delimiter = ',' if ',' in sample else ';' if ';' in sample else '\t'
            
            reader = csv.DictReader(f, delimiter=delimiter)
            
            for row in reader:
                # Normalizar nomes de colunas (case-insensitive)
                normalized_row = {k.lower().strip(): v for k, v in row.items()}
                trades.append(normalized_row)
        
        print(f"[OK] Lidos {len(trades)} trades de {filepath}")
        return trades
    
    except Exception as e:
        print(f"[ERRO] Falha ao ler {filepath}: {e}")
        return []

def map_system_columns(row: Dict) -> Dict:
    """Mapeia colunas do CSV do sistema para formato padrão."""
    # Tentar diferentes nomes de colunas
    entry_time = (row.get('entry time') or row.get('entry_time') or 
                  row.get('entrytime') or row.get('entry')).strip()
    exit_time = (row.get('exit time') or row.get('exit_time') or 
                 row.get('exittime') or row.get('exit')).strip()
    entry_price = (row.get('entry price') or row.get('entry_price') or 
                   row.get('entryprice')).strip()
    exit_price = (row.get('exit price') or row.get('exit_price') or 
                  row.get('exitprice')).strip()
    signal = (row.get('signal') or row.get('signal type') or 
              row.get('signaltype') or row.get('type')).strip()
    return_pct = (row.get('return %') or row.get('return_pct') or 
                  row.get('return') or row.get('profit %') or 
                  row.get('profit_pct') or row.get('profit')).strip()
    pnl_usd = (row.get('p&l (usd)') or row.get('pnl_usd') or 
               row.get('pnl') or row.get('profit_usd')).strip()
    initial_capital = (row.get('initial capital') or row.get('initial_capital') or 
                       row.get('initialcapital') or '100').strip()
    final_capital = (row.get('final capital') or row.get('final_capital') or 
                     row.get('finalcapital') or '').strip()
    
    return {
        'entry_time': entry_time,
        'entry_price': entry_price,
        'exit_time': exit_time,
        'exit_price': exit_price,
        'trade_type': row.get('trade type', 'LONG'),
        'signal': signal,
        'return_pct': return_pct,
        'pnl_usd': pnl_usd,
        'initial_capital': initial_capital,
        'final_capital': final_capital
    }

def main():
    """Função principal."""
    print("="*100)
    print("PROCESSAMENTO DE PLANILHA COMPLETA: Sistema vs TradingView")
    print("="*100)
    
    if len(sys.argv) < 2:
        print("\n[ERRO] Uso: python process_full_trades_comparison.py <arquivo_sistema.csv> [arquivo_tradingview.csv]")
        print("\nExemplo:")
        print("   python process_full_trades_comparison.py trades_sistema.csv")
        print("   python process_full_trades_comparison.py trades_sistema.csv trades_tradingview.csv")
        return
    
    system_file = sys.argv[1]
    
    if not os.path.exists(system_file):
        print(f"\n[ERRO] Arquivo não encontrado: {system_file}")
        return
    
    # Ler trades do sistema
    print(f"\n[1/3] Lendo trades do sistema de {system_file}...")
    system_csv_rows = read_csv_trades(system_file)
    
    if not system_csv_rows:
        print("[ERRO] Nenhum trade encontrado no arquivo do sistema!")
        return
    
    # Mapear para formato padrão
    system_trades = [map_system_columns(row) for row in system_csv_rows]
    
    print(f"[OK] {len(system_trades)} trades processados do sistema")
    
    # Ler trades do TradingView (se fornecido)
    tradingview_trades = []
    
    if len(sys.argv) >= 3:
        tv_file = sys.argv[2]
        print(f"\n[2/3] Lendo trades do TradingView de {tv_file}...")
        tradingview_csv_rows = read_csv_trades(tv_file)
        
        if tradingview_csv_rows:
            # Mapear colunas do TradingView
            for row in tradingview_csv_rows:
                tv_trade = {
                    'trade_num': row.get('trade #', row.get('trade_num', '')),
                    'entry_date': row.get('entry date', row.get('entry_date', '')),
                    'entry_price': row.get('entry price', row.get('entry_price', '')),
                    'exit_date': row.get('exit date', row.get('exit_date', '')),
                    'exit_price': row.get('exit price', row.get('exit_price', '')),
                    'signal': row.get('signal', ''),
                    'profit_pct': row.get('net p&l %', row.get('profit_pct', '')),
                    'profit_usd': row.get('net p&l (usd)', row.get('profit_usd', '')),
                }
                tradingview_trades.append(tv_trade)
            
            print(f"[OK] {len(tradingview_trades)} trades processados do TradingView")
        else:
            print("[AVISO] Nenhum trade encontrado no arquivo do TradingView, usando dados conhecidos")
    else:
        print("\n[2/3] Usando dados conhecidos do TradingView (8 trades mais recentes)")
        # Importar dados conhecidos
        from compare_all_trades_system_vs_tradingview import TRADINGVIEW_TRADES
        tradingview_trades = TRADINGVIEW_TRADES
    
    # Comparar trades
    print(f"\n[3/3] Comparando {len(system_trades)} trades do sistema com {len(tradingview_trades)} trades do TradingView...")
    compare_trades(system_trades, tradingview_trades)
    
    print("\n" + "="*100)
    print("PROCESSAMENTO CONCLUIDO")
    print("="*100)

if __name__ == "__main__":
    main()
