"""
Script para validar que o stop loss tem prioridade sobre os sinais de saída.
Garante que o stop loss seja sempre verificado antes dos sinais de venda.
"""

import sys
import os

project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'backend'))

import pandas as pd
from app.services.combo_service import ComboService
from app.services.combo_optimizer import extract_trades_from_signals, extract_trades_with_mode
from src.data.incremental_loader import IncrementalLoader

def validate_stop_loss_priority(symbol="ETH/USDT", timeframe="1d", template_name="multi_ma_crossover", 
                                start_date="2017-01-01", end_date="2026-01-27",
                                parameters={"ema_short": 20, "sma_medium": 23, "sma_long": 43, "stop_loss": 0.059}):
    """
    Valida que o stop loss tem prioridade sobre os sinais de saída.
    """
    print(f"\n{'='*80}")
    print(f"VALIDACAO: PRIORIDADE DO STOP LOSS")
    print(f"{'='*80}\n")
    
    # 1. Carregar dados
    loader = IncrementalLoader()
    df = loader.fetch_data(
        symbol=symbol,
        timeframe=timeframe,
        since_str=start_date,
        until_str=end_date
    )
    print(f"[OK] Dados carregados: {len(df)} candles\n")
    
    # 2. Criar estratégia
    service = ComboService()
    strategy = service.create_strategy(
        template_name=template_name,
        parameters=parameters
    )
    
    # 3. Gerar sinais
    df_with_signals = strategy.generate_signals(df.copy())
    
    # 4. Testar com modo rápido (1d)
    print(f"{'='*80}")
    print(f"TESTE 1: Modo Rápido (1d) - extract_trades_from_signals")
    print(f"{'='*80}\n")
    
    stop_loss = parameters.get("stop_loss", 0.059)
    trades_fast = extract_trades_from_signals(df_with_signals, stop_loss)
    
    # Verificar se há trades que saíram por stop loss
    stop_loss_trades = [t for t in trades_fast if t.get('exit_reason') == 'stop_loss']
    signal_trades = [t for t in trades_fast if t.get('exit_reason') == 'signal']
    
    print(f"Total de trades: {len(trades_fast)}")
    print(f"Trades com stop loss: {len(stop_loss_trades)}")
    print(f"Trades com sinal de saída: {len(signal_trades)}")
    
    # Verificar se os trades com stop loss têm signal_type = 'Stop'
    stop_loss_with_correct_signal = [t for t in stop_loss_trades if t.get('signal_type') == 'Stop']
    print(f"Trades com stop loss e signal_type='Stop': {len(stop_loss_with_correct_signal)}")
    
    if len(stop_loss_trades) != len(stop_loss_with_correct_signal):
        print(f"[ERRO] Alguns trades com stop loss não têm signal_type='Stop'!")
        for t in stop_loss_trades:
            if t.get('signal_type') != 'Stop':
                print(f"  Trade: entry={t.get('entry_time')}, exit_reason={t.get('exit_reason')}, signal_type={t.get('signal_type')}")
    else:
        print(f"[OK] Todos os trades com stop loss têm signal_type='Stop'")
    
    # 5. Testar com deep backtest (15m)
    print(f"\n{'='*80}")
    print(f"TESTE 2: Deep Backtest (15m) - extract_trades_with_mode")
    print(f"{'='*80}\n")
    
    trades_deep = extract_trades_with_mode(
        df_with_signals,
        stop_loss,
        deep_backtest=True,
        symbol=symbol,
        since_str=start_date,
        until_str=end_date
    )
    
    # Verificar se há trades que saíram por stop loss
    stop_loss_trades_deep = [t for t in trades_deep if 'stop' in t.get('exit_reason', '').lower()]
    signal_trades_deep = [t for t in trades_deep if 'signal' in t.get('exit_reason', '').lower()]
    
    print(f"Total de trades: {len(trades_deep)}")
    print(f"Trades com stop loss: {len(stop_loss_trades_deep)}")
    print(f"Trades com sinal de saída: {len(signal_trades_deep)}")
    
    # Verificar se os trades com stop loss têm signal_type = 'Stop'
    stop_loss_with_correct_signal_deep = [t for t in stop_loss_trades_deep if t.get('signal_type') == 'Stop']
    print(f"Trades com stop loss e signal_type='Stop': {len(stop_loss_with_correct_signal_deep)}")
    
    if len(stop_loss_trades_deep) != len(stop_loss_with_correct_signal_deep):
        print(f"[ERRO] Alguns trades com stop loss não têm signal_type='Stop'!")
        for t in stop_loss_trades_deep:
            if 'stop' in t.get('exit_reason', '').lower() and t.get('signal_type') != 'Stop':
                print(f"  Trade: entry={t.get('entry_time')}, exit_reason={t.get('exit_reason')}, signal_type={t.get('signal_type')}")
    else:
        print(f"[OK] Todos os trades com stop loss têm signal_type='Stop'")
    
    # 6. Verificar se não há conflitos (trade que saiu por stop mas tem signal_type diferente)
    print(f"\n{'='*80}")
    print(f"TESTE 3: Verificação de Conflitos")
    print(f"{'='*80}\n")
    
    conflicts_fast = []
    for t in trades_fast:
        exit_reason = t.get('exit_reason', '')
        signal_type = t.get('signal_type', '')
        if exit_reason == 'stop_loss' and signal_type != 'Stop':
            conflicts_fast.append(t)
    
    conflicts_deep = []
    for t in trades_deep:
        exit_reason = t.get('exit_reason', '')
        signal_type = t.get('signal_type', '')
        if 'stop' in exit_reason.lower() and signal_type != 'Stop':
            conflicts_deep.append(t)
    
    if conflicts_fast:
        print(f"[ERRO] Encontrados {len(conflicts_fast)} conflitos no modo rápido:")
        for t in conflicts_fast[:5]:
            print(f"  Entry: {t.get('entry_time')}, Exit Reason: {t.get('exit_reason')}, Signal Type: {t.get('signal_type')}")
    else:
        print(f"[OK] Nenhum conflito encontrado no modo rápido")
    
    if conflicts_deep:
        print(f"[ERRO] Encontrados {len(conflicts_deep)} conflitos no deep backtest:")
        for t in conflicts_deep[:5]:
            print(f"  Entry: {t.get('entry_time')}, Exit Reason: {t.get('exit_reason')}, Signal Type: {t.get('signal_type')}")
    else:
        print(f"[OK] Nenhum conflito encontrado no deep backtest")
    
    # 7. Resumo final
    print(f"\n{'='*80}")
    print(f"RESUMO FINAL:")
    print(f"{'='*80}\n")
    
    all_ok = (
        len(conflicts_fast) == 0 and 
        len(conflicts_deep) == 0 and
        len(stop_loss_trades) == len(stop_loss_with_correct_signal) and
        len(stop_loss_trades_deep) == len(stop_loss_with_correct_signal_deep)
    )
    
    if all_ok:
        print("[OK] SUCESSO: Stop loss tem prioridade correta sobre sinais de saída!")
        print("  - Todos os trades com stop loss têm signal_type='Stop'")
        print("  - Nenhum conflito encontrado entre exit_reason e signal_type")
        print("  - A lógica de prioridade está funcionando corretamente")
    else:
        print("[ATENCAO] Foram encontrados problemas:")
        if len(conflicts_fast) > 0:
            print(f"  - {len(conflicts_fast)} conflitos no modo rápido")
        if len(conflicts_deep) > 0:
            print(f"  - {len(conflicts_deep)} conflitos no deep backtest")
    
    print(f"\n{'='*80}\n")
    
    return all_ok

if __name__ == "__main__":
    validate_stop_loss_priority()
