import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
sys.path.append(os.getcwd())

from app.services.combo_service import ComboService
from src.data.incremental_loader import IncrementalLoader
import pandas as pd

def compare_with_tradingview():
    service = ComboService()
    loader = IncrementalLoader()
    
    # Get data for the period covering the trades (expanded to Oct 2024)
    df = loader.fetch_data("BTC/USDT", "1d", "2024-10-01", "2026-01-19")
    
    # Optimized parameters from the system
    params = {
        "ema_short": 17,
        "sma_medium": 21,
        "sma_long": 34,
        "stop_loss": 0.019  # 1.9%
    }
    
    # Binance Fee: 0.075% per operation
    TRADING_FEE = 0.00075
    
    print("=== Parâmetros Otimizados ===")
    print(f"EMA Short: {params['ema_short']}")
    print(f"SMA Medium: {params['sma_medium']}")
    print(f"SMA Long: {params['sma_long']}")
    print(f"Stop Loss: {params['stop_loss']*100:.1f}%")
    print(f"Trading Fee: {TRADING_FEE*100:.3f}% per op")
    
    strategy = service.create_strategy("multi_ma_crossover", parameters=params)
    df_signals = strategy.generate_signals(df.copy())
    
    # Extract trades
    trades = []
    position = None
    
    for idx, row in df_signals.iterrows():
        # Check stop loss if we have an open position
        if position is not None:
            # Check intra-candle stop loss using LOW
            current_low = row['low']
            entry_price = position['entry_price']
            stop_price = entry_price * (1 - params['stop_loss'])
            
            if current_low <= stop_price:
                # Stop loss hit intra-candle
                position['exit_time'] = idx
                position['exit_price'] = stop_price  # Exit at stop price
                
                # Calculate Net Profit with Fees
                position['profit'] = ((stop_price * (1 - TRADING_FEE)) - (entry_price * (1 + TRADING_FEE))) / (entry_price * (1 + TRADING_FEE))
                
                trades.append(position)
                position = None
                continue
        
        if row['signal'] == 1 and position is None:
            position = {
                'entry_time': idx,
                'entry_price': row['close']
            }
        elif row['signal'] == -1 and position is not None:
            # Only process normal exit if stop loss wasn't hit
            position['exit_time'] = idx
            position['exit_price'] = row['close']
            
            # Calculate Net Profit with Fees
            exit_price = row['close']
            entry_price = position['entry_price']
            position['profit'] = ((exit_price * (1 - TRADING_FEE)) - (entry_price * (1 + TRADING_FEE))) / (entry_price * (1 + TRADING_FEE))
            
            trades.append(position)
            position = None
    
    # Focus on last 10 trades
    last_10_trades = trades[-10:] if len(trades) >= 10 else trades
    
    print(f"\n=== Últimos {len(last_10_trades)} Trades do Sistema ===\n")
    for i, trade in enumerate(last_10_trades, 1):
        print(f"Trade {i}:")
        print(f"  Entrada: {trade['entry_time'].strftime('%d/%m/%Y, %H:%M:%S')} @ ${trade['entry_price']:.2f}")
        print(f"  Saída:   {trade['exit_time'].strftime('%d/%m/%Y, %H:%M:%S')} @ ${trade['exit_price']:.2f}")
        print(f"  Lucro:   {trade['profit']*100:+.2f}%")
        print()
    
    # TradingView trades for comparison (last 10)
    tv_trades = [
        {"entry": "15/10/2024, 21:00:00", "entry_price": 67620.01, "exit": "04/11/2024, 21:00:00", "exit_price": 69372.01, "profit": 2.59},
        {"entry": "06/11/2024, 21:00:00", "entry_price": 75857.89, "exit": "01/12/2024, 21:00:00", "exit_price": 95840.62, "profit": 26.34},
        {"entry": "13/12/2024, 21:00:00", "entry_price": 101420.00, "exit": "18/12/2024, 21:00:00", "exit_price": 97461.86, "profit": -3.90},
        {"entry": "17/01/2025, 21:00:00", "entry_price": 104556.23, "exit": "18/01/2025, 21:00:00", "exit_price": 101331.57, "profit": -3.08},
        {"entry": "20/04/2025, 21:00:00", "entry_price": 87516.23, "exit": "30/05/2025, 21:00:00", "exit_price": 104591.88, "profit": 19.51},
        {"entry": "29/06/2025, 21:00:00", "entry_price": 107146.50, "exit": "28/07/2025, 21:00:00", "exit_price": 117950.76, "profit": 10.08},
        {"entry": "13/08/2025, 21:00:00", "entry_price": 118295.09, "exit": "18/08/2025, 21:00:00", "exit_price": 112872.94, "profit": -4.58},
        {"entry": "15/09/2025, 21:00:00", "entry_price": 116788.96, "exit": "21/09/2025, 21:00:00", "exit_price": 112650.99, "profit": -3.54},
        {"entry": "03/10/2025, 21:00:00", "entry_price": 122391.00, "exit": "09/10/2025, 21:00:00", "exit_price": 112774.50, "profit": -7.86},
        {"entry": "05/01/2026, 21:00:00", "entry_price": 93747.97, "exit": "07/01/2026, 21:00:00", "exit_price": 91177.49, "profit": -2.74}
    ]
    
    print("=== Últimos 10 Trades do TradingView ===\n")
    for i, trade in enumerate(tv_trades, 1):
        print(f"Trade {i}:")
        print(f"  Entrada: {trade['entry']} @ ${trade['entry_price']:.2f}")
        print(f"  Saída:   {trade['exit']} @ ${trade['exit_price']:.2f}")
        print(f"  Lucro:   {trade['profit']:+.2f}%")
        print()
    
    print("\n=== Comparação ===")
    print(f"Total de trades no sistema: {len(trades)}")
    print(f"Total de trades no TradingView: (não especificado)")
    
    # Check if any system trades match TradingView dates
    print("\n=== Verificando Correspondências ===")
    for tv_trade in tv_trades:
        entry_date = pd.to_datetime(tv_trade['entry'], format='%d/%m/%Y, %H:%M:%S').tz_localize('UTC')
        found = False
        for sys_trade in last_10_trades:
            if abs((sys_trade['entry_time'] - entry_date).days) <= 1:  # Allow 1 day difference
                print(f"✓ Match: TV {tv_trade['entry']} ≈ Sistema {sys_trade['entry_time'].strftime('%d/%m/%Y')}")
                print(f"  TV: Entry ${tv_trade['entry_price']:.2f} → Exit ${tv_trade['exit_price']:.2f} = {tv_trade['profit']:+.2f}%")
                print(f"  Sistema: Entry ${sys_trade['entry_price']:.2f} → Exit ${sys_trade['exit_price']:.2f} = {sys_trade['profit']*100:+.2f}%")
                if abs(tv_trade['profit'] - sys_trade['profit']*100) < 0.1:
                    print(f"  ✅ LUCRO IDÊNTICO!")
                print()
                found = True
                break
        if not found:
            print(f"✗ Não encontrado no sistema: TV {tv_trade['entry']}")

if __name__ == "__main__":
    compare_with_tradingview()
