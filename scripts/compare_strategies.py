
import sys
import os
import logging
from pathlib import Path
import pandas as pd

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from app.services.combo_service import ComboService
from app.services.backtest_service import BacktestService
from src.data.incremental_loader import IncrementalLoader
from app.services.combo_optimizer import ComboOptimizer

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

def run_comparison():
    print("Initializing Services...")
    # Initialize real services to get accurate backtest logic
    optimizer = ComboOptimizer() 
    loader = IncrementalLoader()
    combo_service = ComboService()
    
    symbol = "BTC/USDT"
    timeframe = "1d" 
    start_date = "2017-01-01"
    from datetime import datetime
    end_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"\nFetching Data for {symbol} {timeframe} ({start_date} to {end_date})...")
    df = loader.fetch_data(symbol, timeframe, start_date, end_date)
    
    # 1. Configuration: Antiga Coarse Neighbor (What the Grid SEES)
    # Grid Step 5.
    # Closest to 3, 32, 37, 0.027 are:
    # 3 (Exact)
    # 30 (32 rounded to 5 step from 10: 10,15,20,25,30,35)
    # 35 (37 rounded to 5 step from 20: 20,25,30,35,40)
    # 0.025 (0.027 rounded to 0.0025 step? No, step 0.005. 0.005, 0.01... 0.025, 0.030)
    antiga_coarse = {
        'ema_short': 3,
        'sma_medium': 30,
        'sma_long': 35,
        'stop_loss': 0.025
    }
    
    # 2. Configuration: Nova Winner (From Log - Round 1 Best)
    nova_coarse = {
        'ema_short': 8,
        'sma_medium': 40, 
        'sma_long': 25, 
        'stop_loss': 0.03
    }
    
    configs = [("ANTIGA (Coarse View)", antiga_coarse), ("NOVA (Coarse View)", nova_coarse)]
    
    template_name = "multi_ma_crossover"
    template_metadata = combo_service.get_template_metadata(template_name)
    
    print("\n--- RUNNING COMPARISON ---")
    
    for name, params in configs:
        print(f"\nTesting {name} with params: {params}")
        
        # We can use the helper method _execute_opt_stages logic, but simplified,
        # or better: instantiate the strategy and run generate_signals + extract_trades directly
        # to ensure we use the exact same logic as the optimizer worker.
        
        # Reusing the logic from verify script / worker
        # 1. Create Strategy
        strategy = combo_service.create_strategy(template_name, params)
        
        # 2. Generate Signals
        df_signals = strategy.generate_signals(df.copy())
        
        # 3. Extract Trades (Deep Backtest Logic)
        # We need to simulate 15m execution if we were doing daily, but here we ARE on 15m.
        # Wait, usually we optimize on 1H or 4H or Daily and use 15m for Deep.
        # Here I loaded 15m directly. 
        # If I load 15m directly, `extract_trades_from_signals` is sufficient 
        # because the signals are already on 15m resolution.
        # Does 'Antiga' rely on 1D signals refined by 15? Or native 15m?
        # The user didn't specify timeframe for Antiga, but usually these are Swing strategies.
        # Let's assume standard behavior: The signals are generated on `timeframe` (15m in this script).
        
        from app.services.combo_optimizer import extract_trades_from_signals
        trades = extract_trades_from_signals(df_signals, params['stop_loss'])
        
        # 4. Metrics
        total_trades = len(trades)
        if total_trades > 0:
            returns = [t['profit'] for t in trades]
            total_return = sum(returns) * 100 # percentage
            win_rate = len([t for t in trades if t['profit'] > 0]) / total_trades
            
            import numpy as np
            std_dev = np.std(returns)
            sharpe = np.mean(returns) / std_dev if std_dev > 0 else 0
            
            # Drawdown
            cumulative = np.cumsum(returns)
            peak = np.maximum.accumulate(cumulative)
            drawdown = (cumulative - peak)
            max_drawdown = np.min(drawdown) * 100
            
            avg_profit = (total_return / total_trades)
        else:
            total_return, win_rate, sharpe, max_drawdown, avg_profit = 0,0,0,0,0

        print(f"  > Total Trades: {total_trades}")
        print(f"  > Sharpe Ratio: {sharpe:.4f}")
        print(f"  > Total Return: {total_return:.2f}%")
        print(f"  > Win Rate:     {win_rate*100:.1f}%")
        print(f"  > Max Drawdown: {max_drawdown:.2f}%")
        print(f"  > Avg Profit:   {avg_profit:.2f}%")

if __name__ == "__main__":
    run_comparison()
