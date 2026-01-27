"""
Script detalhado para investigar diferenças entre trades do Optimizer e Backtester.
Compara trades lado a lado para identificar qual método está correto.
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'backend'))

from app.services.combo_service import ComboService
from app.services.combo_optimizer import extract_trades_from_signals
from src.data.incremental_loader import IncrementalLoader
from src.engine.backtester import Backtester

def normalize_timestamp(ts):
    """Normaliza timestamp para comparação."""
    if isinstance(ts, (int, float)):
        # É timestamp em ms
        return pd.to_datetime(ts, unit='ms').isoformat()
    elif isinstance(ts, str):
        # Já é ISO string
        return ts
    elif hasattr(ts, 'isoformat'):
        return ts.isoformat()
    return str(ts)

def investigate_trades(symbol="ETH/USDT", timeframe="1d", template_name="multi_ma_crossover", 
                       start_date="2017-01-01", end_date="2026-01-27",
                       parameters={"ema_short": 20, "sma_medium": 23, "sma_long": 43, "stop_loss": 0.059}):
    """
    Investiga diferenças detalhadas entre trades.
    """
    print(f"\n{'='*80}")
    print(f"INVESTIGACAO DETALHADA: {symbol} {timeframe} - {template_name}")
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
    
    # 4. Extrair trades usando combo_optimizer
    stop_loss = parameters.get("stop_loss", 0.059)
    trades_optimizer = extract_trades_from_signals(df_with_signals, stop_loss)
    
    # 5. Extrair trades usando Backtester
    backtester = Backtester(
        initial_capital=10000,
        stop_loss_pct=stop_loss
    )
    df_results = backtester.run(df, strategy=strategy, record_force_close=False)
    trades_backtester = backtester.trades
    
    # Normalizar timestamps do Backtester para comparação
    trades_bt_normalized = []
    for t in trades_backtester:
        t_norm = t.copy()
        if 'entry_time' in t_norm:
            t_norm['entry_time_norm'] = normalize_timestamp(t_norm['entry_time'])
        if 'exit_time' in t_norm and t_norm.get('exit_time'):
            t_norm['exit_time_norm'] = normalize_timestamp(t_norm['exit_time'])
        trades_bt_normalized.append(t_norm)
    
    # Normalizar timestamps do Optimizer
    trades_opt_normalized = []
    for t in trades_optimizer:
        t_norm = t.copy()
        if 'entry_time' in t_norm:
            t_norm['entry_time_norm'] = normalize_timestamp(t_norm['entry_time'])
        if 'exit_time' in t_norm and t_norm.get('exit_time'):
            t_norm['exit_time_norm'] = normalize_timestamp(t_norm['exit_time'])
        trades_opt_normalized.append(t_norm)
    
    print(f"Trades Optimizer: {len(trades_optimizer)}")
    print(f"Trades Backtester: {len(trades_backtester)}\n")
    
    # 6. Comparar trades por entry_time
    print(f"{'='*80}")
    print(f"COMPARACAO TRADE POR TRADE (primeiros 10):")
    print(f"{'='*80}\n")
    
    # Criar dicionários indexados por entry_time normalizado
    opt_dict = {t['entry_time_norm']: t for t in trades_opt_normalized}
    bt_dict = {t['entry_time_norm']: t for t in trades_bt_normalized if t.get('exit_time_norm')}
    
    # Comparar os primeiros 10 trades
    count = 0
    differences = []
    
    for entry_time_norm in sorted(opt_dict.keys())[:10]:
        count += 1
        t_opt = opt_dict[entry_time_norm]
        t_bt = bt_dict.get(entry_time_norm)
        
        print(f"Trade #{count}: Entry {entry_time_norm}")
        print(f"  Optimizer:")
        print(f"    Entry Price: {t_opt.get('entry_price', 'N/A'):.2f}")
        print(f"    Exit Price: {t_opt.get('exit_price', 'N/A'):.2f}")
        print(f"    Profit: {t_opt.get('profit', 0)*100:.2f}%")
        print(f"    Exit Reason: {t_opt.get('exit_reason', 'N/A')}")
        
        if t_bt:
            print(f"  Backtester:")
            print(f"    Entry Price: {t_bt.get('entry_price', 'N/A'):.2f}")
            print(f"    Exit Price: {t_bt.get('exit_price', 'N/A'):.2f}")
            print(f"    Profit (pnl_pct): {t_bt.get('pnl_pct', 0)*100:.2f}%")
            print(f"    Exit Reason: {t_bt.get('reason', 'N/A')}")
            
            # Verificar diferenças
            entry_diff = abs(t_opt.get('entry_price', 0) - t_bt.get('entry_price', 0))
            exit_diff = abs(t_opt.get('exit_price', 0) - t_bt.get('exit_price', 0))
            profit_diff = abs(t_opt.get('profit', 0) - t_bt.get('pnl_pct', 0))
            
            if entry_diff > 0.01 or exit_diff > 0.01 or profit_diff > 0.0001:
                print(f"  [DIFERENCA DETECTADA]")
                print(f"    Entry Price Diff: {entry_diff:.4f}")
                print(f"    Exit Price Diff: {exit_diff:.4f}")
                print(f"    Profit Diff: {profit_diff*100:.4f}%")
                differences.append({
                    'entry_time': entry_time_norm,
                    'entry_diff': entry_diff,
                    'exit_diff': exit_diff,
                    'profit_diff': profit_diff
                })
        else:
            print(f"  [TRADE NAO ENCONTRADO NO BACKTESTER]")
            differences.append({
                'entry_time': entry_time_norm,
                'entry_diff': None,
                'exit_diff': None,
                'profit_diff': None
            })
        print()
    
    # 7. Análise de sinais
    print(f"{'='*80}")
    print(f"ANALISE DE SINAIS:")
    print(f"{'='*80}\n")
    
    # Verificar quantos sinais de entrada/saída foram gerados
    buy_signals = (df_with_signals['signal'] == 1).sum()
    sell_signals = (df_with_signals['signal'] == -1).sum()
    
    print(f"Total de sinais de compra (signal == 1): {buy_signals}")
    print(f"Total de sinais de venda (signal == -1): {sell_signals}")
    print(f"Total de trades Optimizer: {len(trades_optimizer)}")
    print(f"Total de trades Backtester: {len(trades_backtester)}")
    
    # 8. Verificar lógica de stop loss
    print(f"\n{'='*80}")
    print(f"VERIFICACAO DE STOP LOSS:")
    print(f"{'='*80}\n")
    
    stop_loss_trades_opt = [t for t in trades_optimizer if t.get('exit_reason') == 'stop_loss']
    stop_loss_trades_bt = [t for t in trades_backtester if t.get('reason') == 'SL']
    
    print(f"Trades com Stop Loss no Optimizer: {len(stop_loss_trades_opt)}")
    print(f"Trades com Stop Loss no Backtester: {len(stop_loss_trades_bt)}")
    
    # 9. Verificar cálculo de fees
    print(f"\n{'='*80}")
    print(f"VERIFICACAO DE FEES:")
    print(f"{'='*80}\n")
    
    # Optimizer usa TRADING_FEE = 0.00075 (0.075%)
    # Backtester usa fee = 0.001 (0.1%) por padrão
    print(f"Optimizer usa fee: 0.075% (0.00075)")
    print(f"Backtester usa fee: {backtester.fee*100:.3f}% ({backtester.fee})")
    
    if abs(backtester.fee - 0.00075) > 0.0001:
        print(f"[DIFERENCA] Fees sao diferentes!")
    
    # 10. Resumo das diferenças
    print(f"\n{'='*80}")
    print(f"RESUMO DAS DIFERENCAS:")
    print(f"{'='*80}\n")
    
    print(f"Total de trades diferentes: {len(differences)}")
    print(f"Trades apenas no Optimizer: {len(set(opt_dict.keys()) - set(bt_dict.keys()))}")
    print(f"Trades apenas no Backtester: {len(set(bt_dict.keys()) - set(opt_dict.keys()))}")
    
    # Calcular métricas finais
    if len(trades_optimizer) > 0:
        winning_opt = sum(1 for t in trades_optimizer if t.get('profit', 0) > 0)
        win_rate_opt = (winning_opt / len(trades_optimizer)) * 100
        
        compounded = 1.0
        for t in trades_optimizer:
            profit = t.get('profit', 0) if t.get('profit') is not None else 0
            compounded *= (1.0 + profit)
        total_return_opt = (compounded - 1.0) * 100.0
        
        print(f"\nMétricas Optimizer:")
        print(f"  Win Rate: {win_rate_opt:.2f}%")
        print(f"  Total Return: {total_return_opt:.2f}%")
    
    closed_bt = [t for t in trades_backtester if t.get('exit_time') is not None]
    if len(closed_bt) > 0:
        winning_bt = sum(1 for t in closed_bt if t.get('pnl_pct', 0) > 0)
        win_rate_bt = (winning_bt / len(closed_bt)) * 100
        
        compounded = 1.0
        for t in closed_bt:
            profit = t.get('pnl_pct', 0) if t.get('pnl_pct') is not None else 0
            compounded *= (1.0 + profit)
        total_return_bt = (compounded - 1.0) * 100.0
        
        print(f"\nMétricas Backtester:")
        print(f"  Win Rate: {win_rate_bt:.2f}%")
        print(f"  Total Return: {total_return_bt:.2f}%")
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    investigate_trades()
