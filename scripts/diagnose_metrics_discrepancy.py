"""
Script para diagnosticar discrepâncias entre métricas da estratégia e Excel exportado.
Compara trades e métricas entre combo_optimizer e combo_routes.
"""

import sys
import os

# Add project root to path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'backend'))

import pandas as pd
from app.services.combo_service import ComboService
from app.services.combo_optimizer import extract_trades_from_signals
from src.data.incremental_loader import IncrementalLoader
from src.engine.backtester import Backtester

def diagnose_strategy(symbol="ETH/USDT", timeframe="1d", template_name="multi_ma_crossover", 
                     start_date="2017-01-01", end_date="2026-01-27",
                     parameters={"ema_short": 20, "sma_medium": 23, "sma_long": 43, "stop_loss": 0.059}):
    """
    Diagnostica discrepâncias entre combo_optimizer e Backtester.
    """
    print(f"\n{'='*80}")
    print(f"DIAGNÓSTICO: {symbol} {timeframe} - {template_name}")
    print(f"{'='*80}\n")
    
    # 1. Carregar dados
    loader = IncrementalLoader()
    df = loader.fetch_data(
        symbol=symbol,
        timeframe=timeframe,
        since_str=start_date,
        until_str=end_date
    )
    print(f"[OK] Dados carregados: {len(df)} candles")
    
    # 2. Criar estratégia
    service = ComboService()
    strategy = service.create_strategy(
        template_name=template_name,
        parameters=parameters
    )
    print(f"[OK] Estrategia criada")
    
    # 3. Gerar sinais
    df_with_signals = strategy.generate_signals(df.copy())
    print(f"[OK] Sinais gerados: {len(df_with_signals)} candles")
    
    # 4. Extrair trades usando combo_optimizer (método usado na otimização)
    stop_loss = parameters.get("stop_loss", 0.059)
    trades_optimizer = extract_trades_from_signals(df_with_signals, stop_loss)
    print(f"\n[METODO 1] combo_optimizer.extract_trades_from_signals()")
    print(f"   Total de trades: {len(trades_optimizer)}")
    
    # Verificar trades abertos
    open_trades_opt = [t for t in trades_optimizer if 'exit_time' not in t or t.get('exit_time') is None]
    closed_trades_opt = [t for t in trades_optimizer if 'exit_time' in t and t.get('exit_time') is not None]
    print(f"   - Trades fechados: {len(closed_trades_opt)}")
    print(f"   - Trades abertos: {len(open_trades_opt)}")
    
    if len(trades_optimizer) > 0:
        winning_opt = sum(1 for t in trades_optimizer if t.get('profit', 0) > 0)
        win_rate_opt = (winning_opt / len(trades_optimizer)) * 100
        
        # Compounded return
        compounded = 1.0
        for t in trades_optimizer:
            profit = t.get('profit', 0) if t.get('profit') is not None else 0
            compounded *= (1.0 + profit)
        total_return_opt = (compounded - 1.0) * 100.0
        
        # Max drawdown
        equity = 1.0
        peak = 1.0
        max_dd_opt = 0
        for t in trades_optimizer:
            equity *= (1.0 + t.get('profit', 0))
            if equity > peak:
                peak = equity
            drawdown = (peak - equity) / peak
            max_dd_opt = max(max_dd_opt, drawdown)
        max_dd_opt *= 100.0
        
        print(f"   - Win Rate: {win_rate_opt:.2f}%")
        print(f"   - Total Return: {total_return_opt:.2f}%")
        print(f"   - Max Drawdown: {max_dd_opt:.2f}%")
    
    # 5. Extrair trades usando Backtester (método usado em combo_routes)
    backtester = Backtester(
        initial_capital=10000,
        stop_loss_pct=stop_loss
    )
    df_results = backtester.run(df, strategy=strategy, record_force_close=False)
    trades_backtester = backtester.trades
    
    print(f"\n[METODO 2] Backtester.run()")
    print(f"   Total de trades: {len(trades_backtester)}")
    
    # Verificar trades abertos
    open_trades_bt = [t for t in trades_backtester if t.get('exit_time') is None]
    closed_trades_bt = [t for t in trades_backtester if t.get('exit_time') is not None]
    print(f"   - Trades fechados: {len(closed_trades_bt)}")
    print(f"   - Trades abertos: {len(open_trades_bt)}")
    
    if len(closed_trades_bt) > 0:
        winning_bt = sum(1 for t in closed_trades_bt if t.get('pnl_pct', 0) > 0)
        win_rate_bt = (winning_bt / len(closed_trades_bt)) * 100
        
        # Compounded return (apenas trades fechados)
        compounded = 1.0
        for t in closed_trades_bt:
            profit = t.get('pnl_pct', 0) if t.get('pnl_pct') is not None else 0
            compounded *= (1.0 + profit)
        total_return_bt = (compounded - 1.0) * 100.0
        
        # Max drawdown da equity curve
        if backtester.equity_curve and len(backtester.equity_curve) > 0:
            equity_df = pd.DataFrame(backtester.equity_curve)
            if 'equity' in equity_df.columns:
                equity_series = equity_df['equity']
                rolling_max = equity_series.cummax()
                drawdown = (equity_series - rolling_max) / rolling_max
                max_dd_bt = drawdown.min() * 100.0
            else:
                max_dd_bt = 0.0
        else:
            max_dd_bt = 0.0
        
        print(f"   - Win Rate (fechados): {win_rate_bt:.2f}%")
        print(f"   - Total Return (fechados): {total_return_bt:.2f}%")
        print(f"   - Max Drawdown: {max_dd_bt:.2f}%")
    
    # 6. Comparação
    print(f"\n{'='*80}")
    print(f"COMPARAÇÃO:")
    print(f"{'='*80}")
    print(f"Trades:")
    print(f"  Optimizer: {len(trades_optimizer)}")
    print(f"  Backtester (total): {len(trades_backtester)}")
    print(f"  Backtester (fechados): {len(closed_trades_bt)}")
    print(f"  Diferença: {len(trades_optimizer) - len(closed_trades_bt)}")
    
    if len(trades_optimizer) != len(closed_trades_bt):
        print(f"\n[WARN] DIFERENCA NO NUMERO DE TRADES!")
        print(f"   Possiveis causas:")
        print(f"   1. Trades abertos no Backtester: {len(open_trades_bt)}")
        print(f"   2. Diferenca na logica de extracao de trades")
        print(f"   3. Diferenca na logica de fechamento de posicoes")
    
    # 7. Verificar se há trades duplicados ou faltando
    if len(trades_optimizer) > 0 and len(closed_trades_bt) > 0:
        # Comparar entry_times
        entry_times_opt = {t.get('entry_time') for t in trades_optimizer}
        entry_times_bt = {t.get('entry_time') for t in closed_trades_bt}
        
        only_in_opt = entry_times_opt - entry_times_bt
        only_in_bt = entry_times_bt - entry_times_opt
        
        if only_in_opt:
            print(f"\n[WARN] Trades apenas no Optimizer ({len(only_in_opt)}):")
            for et in list(only_in_opt)[:5]:
                print(f"   - {et}")
        
        if only_in_bt:
            print(f"\n[WARN] Trades apenas no Backtester ({len(only_in_bt)}):")
            for et in list(only_in_bt)[:5]:
                print(f"   - {et}")
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    diagnose_strategy()
