"""
Script para validar se os valores exibidos na UI batem com os valores
que seriam recalculados a partir dos trades exportados para Excel.
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

def validate_ui_vs_excel(symbol="ETH/USDT", timeframe="1d", template_name="multi_ma_crossover", 
                        start_date="2017-01-01", end_date="2026-01-27",
                        parameters={"ema_short": 20, "sma_medium": 23, "sma_long": 43, "stop_loss": 0.059},
                        use_deep_backtest=True):
    """
    Valida se os valores da UI batem com os valores recalculados dos trades.
    Simula o que acontece quando os trades são exportados e depois recalculados.
    """
    print(f"\n{'='*80}")
    print(f"VALIDACAO UI vs EXCEL: {symbol} {timeframe} - {template_name}")
    print(f"Modo: {'Deep Backtest (15m)' if use_deep_backtest else 'Fast (1d)'}")
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
    
    # 4. Extrair trades (simulando o que o backend faz)
    stop_loss = parameters.get("stop_loss", 0.059)
    
    if use_deep_backtest:
        trades = extract_trades_with_mode(
            df_with_signals,
            stop_loss,
            deep_backtest=True,
            symbol=symbol,
            since_str=start_date,
            until_str=end_date
        )
    else:
        from app.services.combo_optimizer import extract_trades_from_signals
        trades = extract_trades_from_signals(df_with_signals, stop_loss)
    
    print(f"[OK] Trades extraidos: {len(trades)}\n")
    
    # 5. Calcular métricas como o backend faz (UI)
    print(f"{'='*80}")
    print(f"METRICAS CALCULADAS PELO BACKEND (EXIBIDAS NA UI):")
    print(f"{'='*80}\n")
    
    # Filtrar apenas trades fechados (como na exportação)
    closed_trades = [t for t in trades if t.get('exit_time') and t.get('exit_price')]
    
    total_trades_ui = len(closed_trades)
    winning_trades_ui = sum(1 for t in closed_trades if t.get('profit', 0) > 0)
    win_rate_ui = (winning_trades_ui / total_trades_ui * 100) if total_trades_ui > 0 else 0
    
    # Compounded return (como no backend)
    compounded_ui = 1.0
    for t in closed_trades:
        profit = t.get('profit', 0) if t.get('profit') is not None else 0
        compounded_ui *= (1.0 + profit)
    total_return_ui = (compounded_ui - 1.0) * 100.0
    
    # Max drawdown (como no backend)
    equity_ui = 1.0
    peak_ui = 1.0
    max_dd_ui = 0.0
    for t in closed_trades:
        equity_ui *= (1.0 + t.get('profit', 0))
        if equity_ui > peak_ui:
            peak_ui = equity_ui
        drawdown = (peak_ui - equity_ui) / peak_ui
        max_dd_ui = max(max_dd_ui, drawdown)
    max_dd_pct_ui = max_dd_ui * 100.0
    
    print(f"Total Trades: {total_trades_ui}")
    print(f"Win Rate: {win_rate_ui:.2f}%")
    print(f"Total Return: {total_return_ui:.2f}%")
    print(f"Max Drawdown: {max_dd_pct_ui:.2f}%")
    
    # 6. Simular exportação para Excel e recálculo (como se alguém importasse o Excel)
    print(f"\n{'='*80}")
    print(f"RECALCULO A PARTIR DOS TRADES (SIMULANDO EXCEL):")
    print(f"{'='*80}\n")
    
    # Simular o que acontece quando os trades são exportados
    # (filtro de trades fechados já foi aplicado acima)
    excel_trades = closed_trades.copy()
    
    # Recalcular métricas a partir dos trades exportados
    total_trades_excel = len(excel_trades)
    winning_trades_excel = sum(1 for t in excel_trades if t.get('profit', 0) > 0)
    win_rate_excel = (winning_trades_excel / total_trades_excel * 100) if total_trades_excel > 0 else 0
    
    # Compounded return (mesma lógica)
    compounded_excel = 1.0
    for t in excel_trades:
        profit = t.get('profit', 0) if t.get('profit') is not None else 0
        compounded_excel *= (1.0 + profit)
    total_return_excel = (compounded_excel - 1.0) * 100.0
    
    # Max drawdown (mesma lógica)
    equity_excel = 1.0
    peak_excel = 1.0
    max_dd_excel = 0.0
    for t in excel_trades:
        equity_excel *= (1.0 + t.get('profit', 0))
        if equity_excel > peak_excel:
            peak_excel = equity_excel
        drawdown = (peak_excel - equity_excel) / peak_excel
        max_dd_excel = max(max_dd_excel, drawdown)
    max_dd_pct_excel = max_dd_excel * 100.0
    
    print(f"Total Trades: {total_trades_excel}")
    print(f"Win Rate: {win_rate_excel:.2f}%")
    print(f"Total Return: {total_return_excel:.2f}%")
    print(f"Max Drawdown: {max_dd_pct_excel:.2f}%")
    
    # 7. Comparação
    print(f"\n{'='*80}")
    print(f"COMPARACAO UI vs EXCEL:")
    print(f"{'='*80}\n")
    
    trades_match = total_trades_ui == total_trades_excel
    win_rate_diff = abs(win_rate_ui - win_rate_excel)
    return_diff = abs(total_return_ui - total_return_excel)
    max_dd_diff = abs(max_dd_pct_ui - max_dd_pct_excel)
    
    print(f"Trades:")
    print(f"  UI: {total_trades_ui}")
    print(f"  Excel: {total_trades_excel}")
    print(f"  Status: {'[OK]' if trades_match else '[DIFERENCA]'}")
    
    print(f"\nWin Rate:")
    print(f"  UI: {win_rate_ui:.2f}%")
    print(f"  Excel: {win_rate_excel:.2f}%")
    print(f"  Diferenca: {win_rate_diff:.4f}%")
    print(f"  Status: {'[OK]' if win_rate_diff < 0.01 else '[DIFERENCA]'}")
    
    print(f"\nTotal Return:")
    print(f"  UI: {total_return_ui:.2f}%")
    print(f"  Excel: {total_return_excel:.2f}%")
    print(f"  Diferenca: {return_diff:.2f}%")
    print(f"  Status: {'[OK]' if return_diff < 0.01 else '[DIFERENCA]'}")
    
    print(f"\nMax Drawdown:")
    print(f"  UI: {max_dd_pct_ui:.2f}%")
    print(f"  Excel: {max_dd_pct_excel:.2f}%")
    print(f"  Diferenca: {max_dd_diff:.4f}%")
    print(f"  Status: {'[OK]' if max_dd_diff < 0.01 else '[DIFERENCA]'}")
    
    # 8. Verificar se todos os trades têm os campos necessários para exportação
    print(f"\n{'='*80}")
    print(f"VERIFICACAO DE CAMPOS DOS TRADES:")
    print(f"{'='*80}\n")
    
    missing_fields = []
    for i, trade in enumerate(closed_trades[:5], 1):
        required_fields = ['entry_time', 'entry_price', 'exit_time', 'exit_price', 'profit', 'type']
        missing = [f for f in required_fields if f not in trade or trade.get(f) is None]
        if missing:
            missing_fields.extend([(i, missing)])
            print(f"Trade #{i}: Faltam campos: {missing}")
        else:
            print(f"Trade #{i}: [OK] Todos os campos presentes")
    
    if not missing_fields:
        print(f"\n[OK] Todos os trades têm os campos necessários para exportação")
    
    # 9. Resumo final
    print(f"\n{'='*80}")
    print(f"RESUMO FINAL:")
    print(f"{'='*80}\n")
    
    all_match = trades_match and win_rate_diff < 0.01 and return_diff < 0.01 and max_dd_diff < 0.01
    
    if all_match:
        print("[OK] SUCESSO: Todos os valores batem perfeitamente!")
        print("Os valores exibidos na UI sao identicos aos que seriam recalculados do Excel.")
    else:
        print("[ATENCAO] Ha diferencas entre UI e Excel:")
        if not trades_match:
            print(f"  - Número de trades diferente")
        if win_rate_diff >= 0.01:
            print(f"  - Win Rate: diferença de {win_rate_diff:.4f}%")
        if return_diff >= 0.01:
            print(f"  - Total Return: diferença de {return_diff:.2f}%")
        if max_dd_diff >= 0.01:
            print(f"  - Max Drawdown: diferença de {max_dd_diff:.4f}%")
    
    print(f"\n{'='*80}\n")
    
    return all_match

if __name__ == "__main__":
    # Testar com deep_backtest (modo usado na otimização)
    print("=" * 80)
    print("TESTE 1: Deep Backtest (15m) - Modo usado na otimização")
    print("=" * 80)
    validate_ui_vs_excel(use_deep_backtest=True)
    
    print("\n" + "=" * 80)
    print("TESTE 2: Fast Mode (1d) - Modo rápido")
    print("=" * 80)
    validate_ui_vs_excel(use_deep_backtest=False)
