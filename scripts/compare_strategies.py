
import sys
import os
import logging
import pandas as pd
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from app.services.backtest_service import BacktestService
from app.services.deep_backtest import simulate_execution_with_15m
from src.data.incremental_loader import IncrementalLoader

def run_deep_comparison():
    # 1. Load Data ONCE
    symbol = "BTC/USDT"
    logger.info(f"Loading data for {symbol}...")
    
    loader = IncrementalLoader()
    # Load Daily for Signals
    df_daily = loader.fetch_data(symbol, "1d", since_str="2017-01-01")
    # Load 15m for Deep Validation (Intraday moves)
    df_15m = loader.fetch_data(symbol, "15m", since_str="2017-01-01")
    
    # 2. Define Strategies
    configs = [
        # Name, Parameters
        ("Nova", {"media_curta": 7, "media_inter": 21, "media_longa": 44, "stop_loss_pct": 0.015}),
        ("Antiga", {"media_curta": 3, "media_inter": 32, "media_longa": 37, "stop_loss_pct": 0.027}),
        ("Nova Deep", {"media_curta": 19, "media_inter": 21, "media_longa": 35, "stop_loss_pct": 0.043})
    ]
    
    service = BacktestService()
    
    results = []
    
    print(f"\n--- Running DEEP Backtest Comparison (15m granularity) ---")
    
    for name, params in configs:
        logger.info(f"Processing {name}...")
        
        # A. Run Standard Backtest to get Daily Signals
        config = {
            "exchange": "binance",
            "symbol": symbol,
            "timeframe": "1d", 
            "strategies": [{"name": "CRUZAMENTOMEDIAS", **params}],
            "stop_pct": params['stop_loss_pct']
        }
        
        # We need the DATAFRAME with signals, but run_backtest returns metrics.
        # So we instantiate strategy and generate signals manually.
        strategy = service._get_strategy("CRUZAMENTOMEDIAS", params)
        signals = strategy.generate_signals(df_daily)
        
        # Attach signals to a dataframe for the deep backtester
        df_with_signals = df_daily.copy()
        df_with_signals['signal'] = signals
        
        # B. Run Deep Backtest (Vectorized Check)
        # simulate_execution expects: df_daily_signals, df_15m, stop_loss
        
        start_time = datetime.now()
        deep_trades = simulate_execution_with_15m(
            df_daily_signals=df_with_signals,
            df_15m=df_15m,
            stop_loss=params['stop_loss_pct']
        )
        duration = (datetime.now() - start_time).total_seconds()
        
        # Calculate Metrics from Deep Trades
        total_pnl = sum(t['profit'] for t in deep_trades)
        wins = [t for t in deep_trades if t['profit'] > 0]
        losses = [t for t in deep_trades if t['profit'] <= 0]
        
        win_rate = (len(wins) / len(deep_trades) * 100) if deep_trades else 0
        
        # Calculate Drawdown (approximate from trade sequence)
        equity = 1.0
        peak = 1.0
        max_dd = 0.0
        
        # Sort trades by entry time
        deep_trades.sort(key=lambda x: x['entry_time'])
        
        for t in deep_trades:
            equity *= (1 + t['profit'])
            if equity > peak:
                peak = equity
            dd = (equity - peak) / peak
            if dd < max_dd:
                max_dd = dd
                
        results.append({
            "Name": name,
            "Trades": len(deep_trades),
            "Return %": (equity - 1) * 100,
            "Win Rate %": win_rate,
            "Max DD %": max_dd * 100,
            "Stop Loss": f"{params['stop_loss_pct']*100}%"
        })

    # Print Results
    print("\n{:<15} {:<10} {:<15} {:<15} {:<15} {:<10}".format(
        "Name", "Stop Loss", "Return %", "Max DD %", "Win Rate %", "Trades"
    ))
    print("-" * 85)
    
    for r in results:
        print("{:<15} {:<10} {:<15.2f} {:<15.2f} {:<15.2f} {:<10}".format(
            r["Name"],
            r["Stop Loss"],
            r["Return %"],
            r["Max DD %"],
            r["Win Rate %"],
            r["Trades"]
        ))

if __name__ == "__main__":
    run_deep_comparison()
