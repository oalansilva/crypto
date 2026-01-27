"""
Script para validar com deep_backtest (15m) para comparar com valores esperados.
"""

import sys
import os

project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'backend'))

import pandas as pd
from app.services.combo_service import ComboService
from app.services.combo_optimizer import extract_trades_with_mode
from src.data.incremental_loader import IncrementalLoader

def validate_with_deep_backtest(symbol="ETH/USDT", timeframe="1d", template_name="multi_ma_crossover", 
                                start_date="2017-01-01", end_date="2026-01-27",
                                parameters={"ema_short": 20, "sma_medium": 23, "sma_long": 43, "stop_loss": 0.059}):
    """
    Valida usando deep_backtest (15m) para comparar com valores esperados da otimização.
    """
    print(f"\n{'='*80}")
    print(f"VALIDACAO COM DEEP BACKTEST (15m): {symbol} {timeframe} - {template_name}")
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
    
    # 4. Extrair trades usando deep_backtest (15m)
    stop_loss = parameters.get("stop_loss", 0.059)
    print(f"[INFO] Usando deep_backtest=True (15m) para validacao...\n")
    
    trades = extract_trades_with_mode(
        df_with_signals,
        stop_loss,
        deep_backtest=True,  # Usar deep backtest como na otimização
        symbol=symbol,
        since_str=start_date,
        until_str=end_date
    )
    
    print(f"[OK] Trades extraidos: {len(trades)}\n")
    
    # 5. Calcular métricas
    print(f"{'='*80}")
    print(f"METRICAS CALCULADAS (DEEP BACKTEST):")
    print(f"{'='*80}\n")
    
    total_trades = len(trades)
    winning_trades = sum(1 for t in trades if t.get('profit', 0) > 0)
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    # Compounded return
    compounded = 1.0
    for t in trades:
        profit = t.get('profit', 0) if t.get('profit') is not None else 0
        compounded *= (1.0 + profit)
    total_return = (compounded - 1.0) * 100.0
    
    # Max drawdown
    equity = 1.0
    peak = 1.0
    max_dd = 0.0
    for t in trades:
        equity *= (1.0 + t.get('profit', 0))
        if equity > peak:
            peak = equity
        drawdown = (peak - equity) / peak
        max_dd = max(max_dd, drawdown)
    max_dd_pct = max_dd * 100.0
    
    # Stop loss trades
    stop_loss_trades = [t for t in trades if 'stop_loss' in t.get('exit_reason', '').lower()]
    
    print(f"Total Trades: {total_trades}")
    print(f"Win Rate: {win_rate:.2f}%")
    print(f"Total Return: {total_return:.2f}%")
    print(f"Max Drawdown: {max_dd_pct:.2f}%")
    print(f"Stop Loss Trades: {len(stop_loss_trades)}")
    print(f"Signal Trades: {total_trades - len(stop_loss_trades)}")
    
    # 6. Comparação com valores esperados (da imagem/otimização)
    print(f"\n{'='*80}")
    print(f"COMPARACAO COM VALORES ESPERADOS (OTIMIZACAO):")
    print(f"{'='*80}\n")
    
    expected_trades = 55
    expected_win_rate = 63.64
    expected_return = 20218.08
    expected_max_dd = 8.69
    
    print(f"Trades:")
    print(f"  Esperado: {expected_trades}")
    print(f"  Calculado: {total_trades}")
    print(f"  Status: {'[OK]' if total_trades == expected_trades else '[DIFERENCA]'}")
    
    print(f"\nWin Rate:")
    print(f"  Esperado: {expected_win_rate:.2f}%")
    print(f"  Calculado: {win_rate:.2f}%")
    print(f"  Diferenca: {abs(win_rate - expected_win_rate):.2f}%")
    print(f"  Status: {'[OK]' if abs(win_rate - expected_win_rate) < 1.0 else '[DIFERENCA]'}")
    
    print(f"\nTotal Return:")
    print(f"  Esperado: {expected_return:.2f}%")
    print(f"  Calculado: {total_return:.2f}%")
    print(f"  Diferenca: {abs(total_return - expected_return):.2f}%")
    print(f"  Status: {'[OK]' if abs(total_return - expected_return) < 100 else '[DIFERENCA]'}")
    
    print(f"\nMax Drawdown:")
    print(f"  Esperado: {expected_max_dd:.2f}%")
    print(f"  Calculado: {max_dd_pct:.2f}%")
    print(f"  Diferenca: {abs(max_dd_pct - expected_max_dd):.2f}%")
    print(f"  Status: {'[OK]' if abs(max_dd_pct - expected_max_dd) < 1.0 else '[DIFERENCA]'}")
    
    # Verificar execução no OPEN (próximo dia)
    print(f"\n{'='*80}")
    print(f"VERIFICACAO DE EXECUCAO NO OPEN (PROXIMO DIA):")
    print(f"{'='*80}\n")
    
    # Verificar primeiros 5 trades
    for i, trade in enumerate(trades[:5], 1):
        entry_time = trade.get('entry_time', '')
        entry_price = trade.get('entry_price', 0)
        
        # Buscar o candle correspondente
        entry_dt = pd.to_datetime(entry_time)
        candle = df_with_signals.loc[df_with_signals.index == entry_dt]
        
        if not candle.empty:
            candle_close = float(candle.iloc[0]['close'])
            candle_open = float(candle.iloc[0]['open'])
            
            print(f"Trade #{i}:")
            print(f"  Entry Time: {entry_time}")
            print(f"  Entry Price: {entry_price:.2f}")
            print(f"  Candle CLOSE: {candle_close:.2f}")
            print(f"  Candle OPEN: {candle_open:.2f}")
            
            if abs(entry_price - candle_open) < 0.01:
                print(f"  [OK] Executado no OPEN (proximo dia apos sinal no CLOSE)")
            elif abs(entry_price - candle_close) < 0.01:
                print(f"  [ATENCAO] Executado no CLOSE (deveria ser OPEN)")
            else:
                print(f"  [ATENCAO] Preco nao corresponde exatamente (pode ser stop loss)")
        print()
    
    print(f"{'='*80}\n")

if __name__ == "__main__":
    validate_with_deep_backtest()
