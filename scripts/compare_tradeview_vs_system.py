"""
Script para comparar os dados do Tradeview com a lista de trades do sistema.
Valida se os trades individuais batem entre as duas fontes.
"""

import sys
import os
from datetime import datetime

project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'backend'))

import pandas as pd
from app.services.combo_service import ComboService
from app.services.combo_optimizer import extract_trades_with_mode
from src.data.incremental_loader import IncrementalLoader

def parse_tradeview_date(date_str):
    """Converte data do Tradeview para formato datetime"""
    # Formato: "Jan 04, 2026" ou "Oct 09, 2025"
    try:
        return pd.to_datetime(date_str, format='%b %d, %Y')
    except:
        return None

def normalize_datetime(dt):
    """Normaliza datetime removendo timezone awareness"""
    if dt is None:
        return None
    if isinstance(dt, pd.Timestamp):
        if dt.tz is not None:
            return dt.tz_localize(None)
        return dt
    dt_parsed = pd.to_datetime(dt)
    if hasattr(dt_parsed, 'tz') and dt_parsed.tz is not None:
        return dt_parsed.tz_localize(None)
    return dt_parsed

def compare_tradeview_vs_system(symbol="ETH/USDT", timeframe="1d", template_name="multi_ma_crossover", 
                                start_date="2017-01-01", end_date="2026-01-27",
                                parameters={"ema_short": 20, "sma_medium": 23, "sma_long": 43, "stop_loss": 0.059}):
    """
    Compara os trades do sistema com os dados do Tradeview.
    """
    print(f"\n{'='*80}")
    print(f"COMPARACAO TRADEVIEW vs SISTEMA: {symbol} {timeframe} - {template_name}")
    print(f"{'='*80}\n")
    
    # 1. Carregar dados e extrair trades do sistema
    loader = IncrementalLoader()
    df = loader.fetch_data(
        symbol=symbol,
        timeframe=timeframe,
        since_str=start_date,
        until_str=end_date
    )
    
    service = ComboService()
    strategy = service.create_strategy(
        template_name=template_name,
        parameters=parameters
    )
    
    df_with_signals = strategy.generate_signals(df.copy())
    stop_loss = parameters.get("stop_loss", 0.059)
    
    # Usar deep_backtest como na otimização
    trades = extract_trades_with_mode(
        df_with_signals,
        stop_loss,
        deep_backtest=True,
        symbol=symbol,
        since_str=start_date,
        until_str=end_date
    )
    
    # Ordenar trades por entry_time (mais recente primeiro, como no Tradeview)
    trades_sorted = sorted(trades, key=lambda t: t.get('entry_time', ''), reverse=True)
    
    print(f"[OK] Trades extraidos do sistema: {len(trades_sorted)}\n")
    
    # Debug: mostrar primeiros 3 trades do sistema
    print(f"DEBUG - Primeiros 3 trades do sistema:")
    for i, t in enumerate(trades_sorted[:3], 1):
        entry_time = normalize_datetime(t.get('entry_time', ''))
        exit_time = normalize_datetime(t.get('exit_time', '')) if t.get('exit_time') else None
        print(f"  Trade #{i}:")
        print(f"    Entry: {entry_time} @ ${t.get('entry_price', 0):.2f}")
        if exit_time:
            print(f"    Exit: {exit_time} @ ${t.get('exit_price', 0):.2f}")
        print()
    
    # 2. Dados do Tradeview (da imagem fornecida)
    tradeview_trades = [
        {
            'trade_number': 55,
            'entry_date': 'Jan 04, 2026',
            'entry_price': 3127.11,
            'exit_date': 'Jan 20, 2026',
            'exit_price': 2942.61,
            'exit_signal': 'Stop',
            'net_pnl_usd': -195.43,
            'net_pnl_pct': -6.04,
            'position_size': 1.03,
            'position_value_usd': 3230,  # 3.23 K USD
            'favorable_excursion_usd': 282.666,
            'favorable_excursion_pct': 8.74,
            'adverse_excursion_usd': -193.148,
            'adverse_excursion_pct': -5.97,
            'cumulative_pnl_usd': 2940.265,
            'cumulative_pnl_pct': 2940.27
        },
        {
            'trade_number': 54,
            'entry_date': 'Oct 09, 2025',
            'entry_price': 4525.72,
            'exit_date': 'Oct 10, 2025',
            'exit_price': 4258.70,
            'exit_signal': 'Stop',
            'net_pnl_usd': -208.035,
            'net_pnl_pct': -6.04,
            'position_size': 0.76,
            'position_value_usd': 3440,  # 3.44 K USD
            'favorable_excursion_usd': 1.829,
            'favorable_excursion_pct': 0.05,
            'adverse_excursion_usd': -205.606,
            'adverse_excursion_pct': -5.97,
            'cumulative_pnl_usd': 3135.695,
            'cumulative_pnl_pct': 3135.70
        }
    ]
    
    print(f"{'='*80}")
    print(f"COMPARACAO TRADE POR TRADE:")
    print(f"{'='*80}\n")
    
    # 3. Comparar cada trade do Tradeview com o sistema
    for tv_trade in tradeview_trades:
        trade_num = tv_trade['trade_number']
        print(f"{'='*80}")
        print(f"TRADE #{trade_num} (Tradeview)")
        print(f"{'='*80}\n")
        
        # Encontrar trade correspondente no sistema
        tv_entry_date = normalize_datetime(parse_tradeview_date(tv_trade['entry_date']))
        tv_exit_date = normalize_datetime(parse_tradeview_date(tv_trade['exit_date']))
        
        matching_trade = None
        for sys_trade in trades_sorted:
            sys_entry_time = normalize_datetime(sys_trade.get('entry_time', ''))
            sys_exit_time = normalize_datetime(sys_trade.get('exit_time', '')) if sys_trade.get('exit_time') else None
            
            # Comparar datas (permitir diferença de até 1 dia devido a timezone)
            if sys_exit_time:
                entry_diff = abs((sys_entry_time - tv_entry_date).days) if tv_entry_date else 999
                exit_diff = abs((sys_exit_time - tv_exit_date).days) if tv_exit_date else 999
                
                if entry_diff <= 1 and exit_diff <= 1:
                    # Verificar se os preços de entrada batem
                    entry_price_match = abs(sys_trade.get('entry_price', 0) - tv_trade['entry_price']) < 1.0
                    
                    if entry_price_match:
                        # Aceitar trade mesmo se exit_price for diferente
                        # (pode ser que Tradeview mostre stop loss mas sistema mostre saída por sinal)
                        matching_trade = sys_trade
                        break
        
        if not matching_trade:
            print(f"[ERRO] Trade #{trade_num} do Tradeview nao encontrado no sistema!")
            print(f"  Procurando: Entry {tv_trade['entry_date']} @ {tv_trade['entry_price']}")
            print(f"  Procurando: Exit {tv_trade['exit_date']} @ {tv_trade['exit_price']}")
            
            # Procurar trades com mesmo entry_price para debug
            print(f"\n  DEBUG - Trades do sistema com entry_price similar:")
            for sys_trade in trades_sorted[:10]:
                sys_entry_time = normalize_datetime(sys_trade.get('entry_time', ''))
                sys_entry_price = sys_trade.get('entry_price', 0)
                sys_exit_price = sys_trade.get('exit_price', 0)
                sys_exit_reason = sys_trade.get('exit_reason', '')
                
                if abs(sys_entry_price - tv_trade['entry_price']) < 1.0:
                    print(f"    Entry: {sys_entry_time.strftime('%Y-%m-%d')} @ ${sys_entry_price:.2f}")
                    print(f"    Exit: ${sys_exit_price:.2f} (reason: {sys_exit_reason})")
                    print()
            print()
            continue
        
        # Comparar campos
        print(f"TRADEVIEW:")
        print(f"  Entry Date: {tv_trade['entry_date']}")
        print(f"  Entry Price: ${tv_trade['entry_price']:.2f}")
        print(f"  Exit Date: {tv_trade['exit_date']}")
        print(f"  Exit Price: ${tv_trade['exit_price']:.2f}")
        print(f"  Exit Signal: {tv_trade['exit_signal']}")
        print(f"  Net P&L: ${tv_trade['net_pnl_usd']:.2f} ({tv_trade['net_pnl_pct']:.2f}%)")
        print(f"  Position Size: {tv_trade['position_size']} unidades")
        print(f"  Position Value: ${tv_trade['position_value_usd']:.0f}")
        
        print(f"\nSISTEMA:")
        sys_entry_time = normalize_datetime(matching_trade.get('entry_time', ''))
        sys_exit_time = normalize_datetime(matching_trade.get('exit_time', '')) if matching_trade.get('exit_time') else None
        sys_entry_price = matching_trade.get('entry_price', 0)
        sys_exit_price = matching_trade.get('exit_price', 0)
        sys_profit = matching_trade.get('profit', 0)
        sys_profit_pct = sys_profit * 100
        sys_pnl = matching_trade.get('pnl', 0)
        sys_initial_capital = matching_trade.get('initial_capital', 0)
        sys_final_capital = matching_trade.get('final_capital', 0)
        sys_exit_reason = matching_trade.get('exit_reason', 'signal')
        
        print(f"  Entry Time: {sys_entry_time.strftime('%d/%m/%Y, %H:%M:%S')}")
        print(f"  Entry Price: ${sys_entry_price:.2f}")
        if sys_exit_time:
            print(f"  Exit Time: {sys_exit_time.strftime('%d/%m/%Y, %H:%M:%S')}")
        print(f"  Exit Price: ${sys_exit_price:.2f}")
        print(f"  Exit Reason: {sys_exit_reason}")
        print(f"  P&L: ${sys_pnl:.2f} ({sys_profit_pct:.2f}%)")
        print(f"  Initial Capital: ${sys_initial_capital:.2f}")
        print(f"  Final Capital: ${sys_final_capital:.2f}")
        
        # Calcular position size aproximado
        if sys_initial_capital > 0 and sys_entry_price > 0:
            position_size = sys_initial_capital / sys_entry_price
            position_value = sys_initial_capital
            print(f"  Position Size (calc): {position_size:.2f} unidades")
            print(f"  Position Value: ${position_value:.0f}")
        
        # Comparações
        print(f"\n{'='*80}")
        print(f"COMPARACAO:")
        print(f"{'='*80}\n")
        
        # Entry Date
        entry_date_match = abs((sys_entry_time - tv_entry_date).days) <= 1 if tv_entry_date else False
        print(f"Entry Date: {'[OK]' if entry_date_match else '[DIFERENCA]'}")
        if not entry_date_match and tv_entry_date:
            print(f"  Tradeview: {tv_entry_date.strftime('%d/%m/%Y')}")
            print(f"  Sistema: {sys_entry_time.strftime('%d/%m/%Y')}")
            print(f"  Diferenca: {abs((sys_entry_time - tv_entry_date).days)} dias")
        
        # Entry Price
        entry_price_diff = abs(sys_entry_price - tv_trade['entry_price'])
        entry_price_match = entry_price_diff < 0.1
        print(f"Entry Price: {'[OK]' if entry_price_match else '[DIFERENCA]'}")
        if not entry_price_match:
            print(f"  Tradeview: ${tv_trade['entry_price']:.2f}")
            print(f"  Sistema: ${sys_entry_price:.2f}")
            print(f"  Diferenca: ${entry_price_diff:.2f}")
        
        # Exit Date
        if sys_exit_time and tv_exit_date:
            exit_date_match = abs((sys_exit_time - tv_exit_date).days) <= 1
            print(f"Exit Date: {'[OK]' if exit_date_match else '[DIFERENCA]'}")
            if not exit_date_match:
                print(f"  Tradeview: {tv_exit_date.strftime('%d/%m/%Y')}")
                print(f"  Sistema: {sys_exit_time.strftime('%d/%m/%Y')}")
                print(f"  Diferenca: {abs((sys_exit_time - tv_exit_date).days)} dias")
        
        # Exit Price
        exit_price_diff = abs(sys_exit_price - tv_trade['exit_price'])
        exit_price_match = exit_price_diff < 0.1
        print(f"Exit Price: {'[OK]' if exit_price_match else '[DIFERENCA - POSSIVEL STOP vs SINAL]'}")
        if not exit_price_match:
            print(f"  Tradeview: ${tv_trade['exit_price']:.2f} ({tv_trade['exit_signal']})")
            print(f"  Sistema: ${sys_exit_price:.2f} ({sys_exit_reason})")
            print(f"  Diferenca: ${exit_price_diff:.2f}")
            print(f"  NOTA: Tradeview mostra {tv_trade['exit_signal']}, sistema mostra {sys_exit_reason}")
            print(f"        Isso pode indicar que o Tradeview capturou o stop loss,")
            print(f"        enquanto o sistema saiu por sinal antes do stop ser atingido.")
        
        # Exit Signal/Reason
        exit_signal_match = (
            (tv_trade['exit_signal'].lower() == 'stop' and 'stop' in sys_exit_reason.lower()) or
            (tv_trade['exit_signal'].lower() != 'stop' and 'stop' not in sys_exit_reason.lower())
        )
        print(f"Exit Signal: {'[OK]' if exit_signal_match else '[DIFERENCA]'}")
        if not exit_signal_match:
            print(f"  Tradeview: {tv_trade['exit_signal']}")
            print(f"  Sistema: {sys_exit_reason}")
        
        # P&L USD
        pnl_diff = abs(sys_pnl - tv_trade['net_pnl_usd'])
        pnl_match = pnl_diff < 1.0  # Permitir diferença de até $1
        print(f"P&L (USD): {'[OK]' if pnl_match else '[DIFERENCA]'}")
        if not pnl_match:
            print(f"  Tradeview: ${tv_trade['net_pnl_usd']:.2f}")
            print(f"  Sistema: ${sys_pnl:.2f}")
            print(f"  Diferenca: ${pnl_diff:.2f}")
        
        # P&L %
        pnl_pct_diff = abs(sys_profit_pct - tv_trade['net_pnl_pct'])
        pnl_pct_match = pnl_pct_diff < 0.1  # Permitir diferença de até 0.1%
        print(f"P&L (%): {'[OK]' if pnl_pct_match else '[DIFERENCA]'}")
        if not pnl_pct_match:
            print(f"  Tradeview: {tv_trade['net_pnl_pct']:.2f}%")
            print(f"  Sistema: {sys_profit_pct:.2f}%")
            print(f"  Diferenca: {pnl_pct_diff:.2f}%")
        
        # Position Size (aproximado)
        if sys_initial_capital > 0 and sys_entry_price > 0:
            calc_position_size = sys_initial_capital / sys_entry_price
            position_size_diff = abs(calc_position_size - tv_trade['position_size'])
            position_size_match = position_size_diff < 0.1
            print(f"Position Size: {'[OK]' if position_size_match else '[DIFERENCA]'}")
            if not position_size_match:
                print(f"  Tradeview: {tv_trade['position_size']:.2f} unidades")
                print(f"  Sistema (calc): {calc_position_size:.2f} unidades")
                print(f"  Diferenca: {position_size_diff:.2f} unidades")
        
        # Position Value
        if sys_initial_capital > 0:
            position_value_diff = abs(sys_initial_capital - tv_trade['position_value_usd'])
            position_value_match = position_value_diff < 50  # Permitir diferença de até $50
            print(f"Position Value: {'[OK]' if position_value_match else '[DIFERENCA]'}")
            if not position_value_match:
                print(f"  Tradeview: ${tv_trade['position_value_usd']:.0f}")
                print(f"  Sistema: ${sys_initial_capital:.0f}")
                print(f"  Diferenca: ${position_value_diff:.0f}")
        
        print()
    
    # 4. Resumo geral
    print(f"{'='*80}")
    print(f"RESUMO GERAL:")
    print(f"{'='*80}\n")
    
    print(f"Total de trades no sistema: {len(trades_sorted)}")
    print(f"Trades comparados do Tradeview: {len(tradeview_trades)}")
    print(f"\nNota: Esta comparacao valida se os dados do Tradeview correspondem")
    print(f"aos trades gerados pelo sistema. Se houver diferencas, pode ser devido a:")
    print(f"  - Diferencas de timezone nas datas")
    print(f"  - Arredondamentos nos calculos")
    print(f"  - Diferencas na forma de calcular position size")
    print(f"  - Diferencas na aplicacao de fees")
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    compare_tradeview_vs_system()
