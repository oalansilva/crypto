"""
Script para comparar dados completos do Excel (Sistema) com TradingView (Imagens).

Baseado nas imagens fornecidas:
- Sistema: Planilha Excel com 55 trades
- TradingView: Múltiplas imagens com trades de diferentes períodos
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
        # Formato sistema Excel: "2026-01-04T00:00:00+00:00"
        if 'T' in date_str:
            date_part = date_str.split('T')[0]
            return datetime.strptime(date_part, '%Y-%m-%d')
        # Formato TradingView: "Jan 04, 2026" ou "Oct 13, 2017"
        elif ',' in date_str and len(date_str.split(',')) == 2:
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

# Dados do TradingView extraídos das imagens
# Trades mais recentes (55-48)
TRADINGVIEW_TRADES_RECENT = [
    {'trade_num': 55, 'entry_date': 'Jan 04, 2026', 'entry_price': 3127.11, 'exit_date': 'Jan 20, 2026', 'exit_price': 2942.61, 'signal': 'Stop', 'profit_pct': -6.04},
    {'trade_num': 54, 'entry_date': 'Oct 09, 2025', 'entry_price': 4525.72, 'exit_date': 'Oct 10, 2025', 'exit_price': 4258.70, 'signal': 'Stop', 'profit_pct': -6.04},
    {'trade_num': 53, 'entry_date': 'Sep 16, 2025', 'entry_price': 4523.74, 'exit_date': 'Sep 22, 2025', 'exit_price': 4256.83, 'signal': 'Stop', 'profit_pct': -6.04},
    {'trade_num': 52, 'entry_date': 'Aug 12, 2025', 'entry_price': 4223.22, 'exit_date': 'Aug 29, 2025', 'exit_price': 4511.20, 'signal': 'Close entry(s) order...', 'profit_pct': 6.66},
    {'trade_num': 51, 'entry_date': 'Jul 10, 2025', 'entry_price': 2768.74, 'exit_date': 'Aug 03, 2025', 'exit_price': 3393.94, 'signal': 'Close entry(s) order...', 'profit_pct': 22.40},
    {'trade_num': 50, 'entry_date': 'May 04, 2025', 'entry_price': 1833.52, 'exit_date': 'May 29, 2025', 'exit_price': 2681.61, 'signal': 'Close entry(s) order...', 'profit_pct': 46.04},
    {'trade_num': 49, 'entry_date': 'Nov 07, 2024', 'entry_price': 2721.88, 'exit_date': 'Dec 19, 2024', 'exit_price': 3626.80, 'signal': 'Close entry(s) order...', 'profit_pct': 33.05},
    {'trade_num': 48, 'entry_date': 'Oct 18, 2024', 'entry_price': 2605.79, 'exit_date': 'Oct 23, 2024', 'exit_price': 2452.04, 'signal': 'Stop', 'profit_pct': -6.04},
]

# Trades intermediários (42-49) - baseado na segunda imagem
TRADINGVIEW_TRADES_MID = [
    {'trade_num': 49, 'entry_date': 'Nov 07, 2024', 'entry_price': 2721.88, 'exit_date': 'Dec 17, 2024', 'exit_price': 3199.25, 'signal': 'Close entry(s) order...', 'profit_pct': 17.54},  # Nota: data de saída diferente
    {'trade_num': 48, 'entry_date': 'Oct 18, 2024', 'entry_price': 2605.79, 'exit_date': 'Oct 23, 2024', 'exit_price': 2452.04, 'signal': 'Stop', 'profit_pct': -6.04},
    {'trade_num': 47, 'entry_date': 'Sep 27, 2024', 'entry_price': 2632.25, 'exit_date': 'Oct 01, 2024', 'exit_price': 2476.94, 'signal': 'Stop', 'profit_pct': -6.04},
    {'trade_num': 46, 'entry_date': 'Jul 24, 2024', 'entry_price': 3482.51, 'exit_date': 'Jul 25, 2024', 'exit_price': 3277.04, 'signal': 'Stop', 'profit_pct': -6.04},
    {'trade_num': 45, 'entry_date': 'May 22, 2024', 'entry_price': 3789.59, 'exit_date': 'May 23, 2024', 'exit_price': 3566.00, 'signal': 'Stop', 'profit_pct': -6.04},
    {'trade_num': 44, 'entry_date': 'Feb 11, 2024', 'entry_price': 2500.24, 'exit_date': 'Mar 19, 2024', 'exit_price': 3520.47, 'signal': 'Close entry(s) order...', 'profit_pct': 40.59},
    {'trade_num': 43, 'entry_date': 'Jan 11, 2024', 'entry_price': 2584.37, 'exit_date': 'Jan 18, 2024', 'exit_price': 2431.89, 'signal': 'Stop', 'profit_pct': -6.04},
    {'trade_num': 42, 'entry_date': 'Jan 02, 2024', 'entry_price': 2352.05, 'exit_date': 'Jan 03, 2024', 'exit_price': 2213.27, 'signal': 'Stop', 'profit_pct': -6.04},
]

# Trades antigos (1-8) - baseado nas imagens mais antigas
TRADINGVIEW_TRADES_OLD = [
    {'trade_num': 8, 'entry_date': 'Mar 19, 2019', 'entry_price': 137.62, 'exit_date': 'Mar 28, 2019', 'exit_price': 139.46, 'signal': 'Close entry(s) order...', 'profit_pct': 1.19},
    {'trade_num': 7, 'entry_date': 'Feb 19, 2019', 'entry_price': 145.69, 'exit_date': 'Feb 24, 2019', 'exit_price': 137.09, 'signal': 'Stop', 'profit_pct': -6.04},
    {'trade_num': 6, 'entry_date': 'Dec 30, 2018', 'entry_price': 133.00, 'exit_date': 'Jan 10, 2019', 'exit_price': 125.15, 'signal': 'Stop', 'profit_pct': -6.04},
    {'trade_num': 5, 'entry_date': 'Apr 22, 2018', 'entry_price': 604.87, 'exit_date': 'May 13, 2018', 'exit_price': 684.56, 'signal': 'Close entry(s) order...', 'profit_pct': 13.01},
    {'trade_num': 4, 'entry_date': 'Jan 05, 2018', 'entry_price': 940.00, 'exit_date': 'Jan 16, 2018', 'exit_price': 884.54, 'signal': 'Stop', 'profit_pct': -6.04},
    {'trade_num': 3, 'entry_date': 'Dec 13, 2017', 'entry_price': 619.40, 'exit_date': 'Dec 13, 2017', 'exit_price': 582.85, 'signal': 'Stop', 'profit_pct': -6.04},
    {'trade_num': 2, 'entry_date': 'Nov 15, 2017', 'entry_price': 335.60, 'exit_date': 'Dec 11, 2017', 'exit_price': 427.40, 'signal': 'Close entry(s) order...', 'profit_pct': 27.16},
    {'trade_num': 1, 'entry_date': 'Oct 13, 2017', 'entry_price': 303.99, 'exit_date': 'Oct 18, 2017', 'exit_price': 286.05, 'signal': 'Stop', 'profit_pct': -6.04},
]

# Combinar todos os trades do TradingView
ALL_TRADINGVIEW_TRADES = TRADINGVIEW_TRADES_RECENT + TRADINGVIEW_TRADES_MID[2:] + TRADINGVIEW_TRADES_OLD

def read_excel_data_from_user():
    """
    Lê dados do Excel colados pelo usuário.
    Como o usuário colou os dados, vou criar uma estrutura para ele colar aqui.
    """
    print("\n" + "="*100)
    print("INSTRUCOES PARA COMPARACAO:")
    print("="*100)
    print("\nPor favor, cole os dados do Excel aqui no formato:")
    print("Entry Time, Entry Price, Exit Time, Exit Price, Signal, P&L (USD), Return %")
    print("\nOu salve o Excel como CSV e use o script process_full_trades_comparison.py")
    print("\n" + "="*100)
    
    # Por enquanto, vou usar dados de exemplo baseados na descrição da imagem
    # O usuário precisa colar os dados reais
    return []

def compare_trades_detailed(system_trades: List[Dict], tradingview_trades: List[Dict]):
    """Compara trades do sistema com TradingView em detalhes."""
    print("\n" + "="*100)
    print("COMPARACAO DETALHADA: Sistema (Excel) vs TradingView")
    print("="*100)
    
    # Normalizar e ordenar trades
    tv_sorted = sorted(tradingview_trades, key=lambda x: parse_date(x.get('entry_date', '')) or datetime.min)
    
    print(f"\nTotal de trades:")
    print(f"   Sistema: {len(system_trades)}")
    print(f"   TradingView: {len(tv_sorted)}")
    
    matches = 0
    mismatches = []
    differences = []
    
    for i, sys_trade in enumerate(system_trades):
        sys_entry_date = parse_date(sys_trade.get('entry_time', ''))
        sys_entry_price = normalize_price(sys_trade.get('entry_price', 0))
        sys_exit_date = parse_date(sys_trade.get('exit_time', ''))
        sys_exit_price = normalize_price(sys_trade.get('exit_price', 0))
        sys_profit_pct = sys_trade.get('return_pct', 0) if isinstance(sys_trade.get('return_pct', 0), (int, float)) else float(str(sys_trade.get('return_pct', 0)).replace('%', ''))
        sys_signal = sys_trade.get('signal', '')
        
        if not all([sys_entry_date, sys_entry_price]):
            continue
        
        # Procurar trade correspondente
        best_match = None
        best_score = 0
        
        for tv_trade in tv_sorted:
            tv_entry_date = parse_date(tv_trade.get('entry_date', ''))
            tv_entry_price = normalize_price(tv_trade.get('entry_price', 0))
            tv_exit_date = parse_date(tv_trade.get('exit_date', ''))
            tv_exit_price = normalize_price(tv_trade.get('exit_price', 0))
            
            if not tv_entry_date:
                continue
            
            # Calcular score
            score = 0
            
            # Data de entrada (tolerância de 1 dia)
            if sys_entry_date and tv_entry_date:
                days_diff = abs((sys_entry_date - tv_entry_date).days)
                if days_diff == 0:
                    score += 5
                elif days_diff <= 1:
                    score += 3
                elif days_diff <= 3:
                    score += 1
            
            # Preço de entrada (tolerância de 1%)
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
                    'entry_price_diff': price_diff if sys_entry_price > 0 and tv_entry_price > 0 else None,
                    'exit_date_diff': abs((sys_exit_date - tv_exit_date).days) if sys_exit_date and tv_exit_date else None,
                    'exit_price_diff': abs(sys_exit_price - tv_exit_price) / sys_exit_price if sys_exit_price > 0 and tv_exit_price > 0 else None,
                    'profit_diff': abs(sys_profit_pct - tv_trade.get('profit_pct', 0)),
                    'signal_match': sys_signal == tv_trade.get('signal', '')
                }
        
        if best_match and best_score >= 5:
            tv_t = best_match['tv_trade']
            matches += 1
            
            # Verificar se há diferenças significativas
            has_diff = False
            diff_details = []
            
            if best_match['entry_date_diff'] and best_match['entry_date_diff'] > 0:
                has_diff = True
                diff_details.append(f"Entry date: {best_match['entry_date_diff']} dias")
            
            if best_match['entry_price_diff'] and best_match['entry_price_diff'] > 0.01:
                has_diff = True
                diff_details.append(f"Entry price: {best_match['entry_price_diff']*100:.2f}%")
            
            if best_match['exit_date_diff'] and best_match['exit_date_diff'] > 0:
                has_diff = True
                diff_details.append(f"Exit date: {best_match['exit_date_diff']} dias")
            
            if best_match['exit_price_diff'] and best_match['exit_price_diff'] > 0.01:
                has_diff = True
                diff_details.append(f"Exit price: {best_match['exit_price_diff']*100:.2f}%")
            
            if best_match['profit_diff'] > 0.1:
                has_diff = True
                diff_details.append(f"Profit: {best_match['profit_diff']:.2f}%")
            
            if not best_match['signal_match']:
                has_diff = True
                diff_details.append(f"Signal: Sistema='{sys_signal}' vs TV='{tv_t.get('signal', '')}'")
            
            if has_diff:
                differences.append({
                    'system_trade': sys_trade,
                    'tv_trade': tv_t,
                    'differences': diff_details
                })
        else:
            mismatches.append({
                'system_trade': sys_trade,
                'index': i+1
            })
    
    print(f"\n{'='*100}")
    print(f"RESUMO DA COMPARACAO:")
    print(f"{'='*100}")
    print(f"   Trades correspondentes: {matches}/{len(system_trades)}")
    print(f"   Trades com diferencas: {len(differences)}")
    print(f"   Trades nao encontrados: {len(mismatches)}")
    
    if differences:
        print(f"\n{'='*100}")
        print(f"TRADES COM DIFERENCAS ({len(differences)}):")
        print(f"{'='*100}")
        for diff in differences[:20]:  # Mostrar primeiros 20
            sys_t = diff['system_trade']
            tv_t = diff['tv_trade']
            print(f"\nTrade Sistema: Entry {sys_t.get('entry_time', 'N/A')} @ ${normalize_price(sys_t.get('entry_price', 0)):.2f}")
            print(f"Trade TradingView: Entry {tv_t.get('entry_date', 'N/A')} @ ${normalize_price(tv_t.get('entry_price', 0)):.2f}")
            print(f"   Diferencas: {', '.join(diff['differences'])}")
    
    if mismatches:
        print(f"\n{'='*100}")
        print(f"TRADES DO SISTEMA NAO ENCONTRADOS NO TRADINGVIEW ({len(mismatches)}):")
        print(f"{'='*100}")
        for mm in mismatches[:10]:  # Mostrar primeiros 10
            print(f"   Trade #{mm['index']}: Entry {mm['system_trade'].get('entry_time', 'N/A')}")
    
    print("\n" + "="*100)

if __name__ == "__main__":
    print("COMPARACAO: Dados Excel (Sistema) vs TradingView (Imagens)")
    print("\nEste script compara os dados do Excel exportado do sistema")
    print("com os dados extraídos das imagens do TradingView.")
    
    print("\n[AVISO] Para usar este script completamente:")
    print("1. Cole os dados do Excel aqui ou")
    print("2. Salve o Excel como CSV e use: python process_full_trades_comparison.py <arquivo.csv>")
    print("\nPor enquanto, vou mostrar a estrutura dos dados do TradingView encontrados:")
    
    print(f"\nTotal de trades do TradingView encontrados nas imagens: {len(ALL_TRADINGVIEW_TRADES)}")
    print(f"\nTrades mais recentes (55-48): {len(TRADINGVIEW_TRADES_RECENT)}")
    print(f"Trades intermediários (42-49): {len(TRADINGVIEW_TRADES_MID)}")
    print(f"Trades antigos (1-8): {len(TRADINGVIEW_TRADES_OLD)}")
    
    print("\n" + "="*100)
    print("EXEMPLO DE DADOS DO TRADINGVIEW (primeiros 5 trades mais recentes):")
    print("="*100)
    for trade in TRADINGVIEW_TRADES_RECENT[:5]:
        print(f"Trade #{trade['trade_num']}: {trade['entry_date']} @ ${trade['entry_price']:.2f} -> {trade['exit_date']} @ ${trade['exit_price']:.2f} ({trade['signal']}, {trade['profit_pct']:.2f}%)")
    
    print("\n" + "="*100)
    print("PARA COMPARAR COM DADOS DO EXCEL:")
    print("="*100)
    print("1. Exporte o Excel para CSV")
    print("2. Execute: python process_full_trades_comparison.py <arquivo.csv>")
    print("\nOu cole os dados diretamente aqui no script.")
