"""
Script para validar se a lógica unificada está gerando resultados consistentes.
Compara métricas calculadas com os dados esperados.
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

def validate_strategy(symbol="ETH/USDT", timeframe="1d", template_name="multi_ma_crossover", 
                     start_date="2017-01-01", end_date="2026-01-27",
                     parameters={"ema_short": 20, "sma_medium": 23, "sma_long": 43, "stop_loss": 0.059}):
    """
    Valida se a lógica unificada está gerando resultados corretos.
    """
    print(f"\n{'='*80}")
    print(f"VALIDACAO: {symbol} {timeframe} - {template_name}")
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
    
    # 4. Extrair trades usando lógica unificada
    stop_loss = parameters.get("stop_loss", 0.059)
    trades = extract_trades_from_signals(df_with_signals, stop_loss)
    
    print(f"[OK] Trades extraidos: {len(trades)}\n")
    
    # 5. Verificar execução no OPEN (próximo dia)
    print(f"{'='*80}")
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
    
    # 6. Calcular métricas
    print(f"{'='*80}")
    print(f"METRICAS CALCULADAS:")
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
    stop_loss_trades = [t for t in trades if t.get('exit_reason') == 'stop_loss']
    
    print(f"Total Trades: {total_trades}")
    print(f"Win Rate: {win_rate:.2f}%")
    print(f"Total Return: {total_return:.2f}%")
    print(f"Max Drawdown: {max_dd_pct:.2f}%")
    print(f"Stop Loss Trades: {len(stop_loss_trades)}")
    print(f"Signal Trades: {total_trades - len(stop_loss_trades)}")
    
    # 7. Verificar fees
    print(f"\n{'='*80}")
    print(f"VERIFICACAO DE FEES:")
    print(f"{'='*80}\n")
    
    # Verificar alguns trades com stop loss (devem ter profit próximo de -6.04%)
    stop_loss_sample = stop_loss_trades[:3] if len(stop_loss_trades) >= 3 else stop_loss_trades
    expected_stop_loss_return = -((stop_loss * 100) + (0.075 * 2))  # Stop loss + fees entrada + saída
    
    print(f"Stop Loss configurado: {stop_loss*100:.2f}%")
    print(f"Fee por operacao: 0.075%")
    print(f"Fee total (entrada + saida): 0.15%")
    print(f"Retorno esperado em stop loss: {expected_stop_loss_return:.2f}%")
    print(f"\nTrades com stop loss (amostra):")
    
    for i, trade in enumerate(stop_loss_sample, 1):
        profit_pct = trade.get('profit', 0) * 100
        print(f"  Trade #{i}: {profit_pct:.2f}%")
        if abs(profit_pct - expected_stop_loss_return) < 0.1:
            print(f"    [OK] Fee aplicado corretamente")
        else:
            print(f"    [ATENCAO] Diferenca: {abs(profit_pct - expected_stop_loss_return):.2f}%")
    
    # 8. Comparação com valores esperados (da imagem)
    print(f"\n{'='*80}")
    print(f"COMPARACAO COM VALORES ESPERADOS:")
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
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    validate_strategy()
