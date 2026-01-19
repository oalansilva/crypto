import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
sys.path.append(os.getcwd())

import logging
from app.services.combo_service import ComboService
from src.data.incremental_loader import IncrementalLoader
from app.strategies.combos import ComboStrategy

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

def run_comparison():
    service = ComboService()
    loader = IncrementalLoader()
    
    symbol = "BTC/USDT"
    timeframe = "1d"
    # Using a wide range to ensure we capture the same data context
    start_date = "2020-01-01" 
    end_date = "2023-12-31"

    print(f"--- Loading Data for {symbol} {timeframe} ({start_date} to {end_date}) ---")
    df = loader.fetch_data(symbol, timeframe, start_date, end_date)
    print(f"Loaded {len(df)} candles.\n")

    # Define the two comparison sets
    sets = [
        {
            "name": "Old System Best",
            "params": {
                "sma_short": 3,
                "sma_medium": 32,
                "sma_long": 37,
                "stop_loss": 0.027
            }
        },
        {
            "name": "New Optimizer Result",
            "params": {
                "sma_short": 3,
                "sma_medium": 20,
                "sma_long": 29,
                "stop_loss": 0.005
            }
        }
    ]

    results = []

    for s in sets:
        print(f"Testing: {s['name']} - {s['params']}")
        
        # Create strategy using the service to ensure consistent logic
        # We need to map flat params to the structure expected by create_strategy if needed,
        # but create_strategy handles the flat params -> indicator params mapping internally.
        
        # NOTE: create_strategy expects params dict to match 'alias' keys or 'type'
        # based on our recent fixes.
        # "sma_short" needs to map to the indicator with alias "short" params "length"
        # The service.create_strategy uses the dictionary update logic.
        
        strategy = service.create_strategy(
            template_name="multi_ma_crossover",
            parameters=s['params']
        )
        
        df_signals = strategy.generate_signals(df.copy())
        
        # Calculate simplfied metrics manually to trust the output
        trades = []
        position = None
        
        for idx, row in df_signals.iterrows():
            if row['signal'] == 1 and position is None:
                position = {'entry_price': row['close'], 'time': idx}
            elif row['signal'] == -1 and position is not None:
                profit = (row['close'] - position['entry_price']) / position['entry_price']
                trades.append(profit)
                position = None
                
        total_trades = len(trades)
        total_return = sum(trades)
        win_rate = len([t for t in trades if t > 0]) / total_trades if total_trades > 0 else 0
        
        import numpy as np
        std_dev = np.std(trades) if trades else 0
        avg_return = np.mean(trades) if trades else 0
        sharpe = avg_return / std_dev if std_dev > 0 else 0
        
        # Normalize Sharpe (assuming risky free rate 0 for simplicity in comparison)
        
        res = {
            "name": s['name'],
            "metrics": {
                "Sharpe": sharpe,
                "Return": total_return,
                "Trades": total_trades,
                "WinRate": win_rate
            }
        }
        results.append(res)
        print(f"  -> Sharpe: {sharpe:.4f} | Return: {total_return:.4f} | Trades: {total_trades}\n")

    print("--- Final Comparison ---")
    best_sharpe = max(results, key=lambda x: x['metrics']['Sharpe'])
    best_return = max(results, key=lambda x: x['metrics']['Return'])
    
    print(f"Highest Sharpe: {best_sharpe['name']} ({best_sharpe['metrics']['Sharpe']:.4f})")
    print(f"Highest Return: {best_return['name']} ({best_return['metrics']['Return']:.4f})")

if __name__ == "__main__":
    run_comparison()
