
import asyncio
import sys
import os
from datetime import datetime
import pandas as pd

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.backtest_service import BacktestService

async def run_comparison():
    service = BacktestService()

    # Common settings
    exchange = "binance"
    symbol = "BTC/USDT"
    timeframe = "1d"
    start_date_str = "2017-01-01 00:00:00"
    end_date_str = "2026-01-20 00:00:00"
    initial_capital = 10000.0
    
    # Configuration 1: Antiga (User Provided)
    config_antiga = {
        "exchange": exchange,
        "symbol": symbol,
        "timeframe": timeframe,
        "since": start_date_str,
        "until": end_date_str,
        "cash": initial_capital,
        "strategies": [
            {
                "name": "cruzamentomedias",
                "media_curta": 3,
                "media_longa": 37,
                "media_inter": 32,
                "stop_loss": 0.027
            }
        ]
    }
    
    # Configuration 2: Nova (User Provided)
    config_nova = {
        "exchange": exchange,
        "symbol": symbol,
        "timeframe": timeframe,
        "since": start_date_str,
        "until": end_date_str,
        "cash": initial_capital,
        "strategies": [
            {
                "name": "cruzamentomedias",
                "ema_short": 15,
                "sma_medium": 37,
                "sma_long": 42,
                "stop_loss": 0.065
            }
        ]
    }

    # Configuration 3: Nova 2 (User Provided)
    config_nova2 = {
        "exchange": exchange,
        "symbol": symbol,
        "timeframe": timeframe,
        "since": start_date_str,
        "until": end_date_str,
        "cash": initial_capital,
        "strategies": [
            {
                "name": "cruzamentomedias",
                "ema_short": 13,
                "sma_medium": 39,
                "sma_long": 38,
                "stop_loss": 0.067
            }
        ]
    }
    
    print("=== Running Backtest for Configuration: Antiga ===")
    result_antiga_dict = service.run_backtest(config_antiga)
    
    print("\n=== Running Backtest for Configuration: Nova ===")
    result_nova_dict = service.run_backtest(config_nova)

    print("\n=== Running Backtest for Configuration: Nova 2 ===")
    result_nova2_dict = service.run_backtest(config_nova2)

    # Collect Results
    results = [
        ("Antiga", result_antiga_dict),
        ("Nova", result_nova_dict),
        ("Nova 2", result_nova2_dict)
    ]

    print("\n" + "="*60)
    print(f"{'STRATEGY':<15} | {'PnL ($)':<15} | {'WIN RATE':<10} | {'TRADES':<8} | {'PROFIT FACTOR':<15}")
    print("-" * 75)

    for name, res_dict in results:
        results_map = res_dict.get('results', {})
        # Handle case sensitivity
        res = results_map.get('cruzamentomedias') or results_map.get('CRUZAMENTOMEDIAS')
        
        if res:
            metrics = res.get('metrics', {})
            pnl = metrics.get('total_pnl', 0)
            win_rate = metrics.get('win_rate', 0) * 100
            trades = metrics.get('total_trades', 0)
            pf = metrics.get('profit_factor', 0)
            
            print(f"{name:<15} | ${pnl:,.2f}      | {win_rate:5.2f}%    | {trades:<8} | {pf:.3f}")
        else:
            print(f"{name:<15} | ERROR: No Results")
    print("="*60 + "\n")

def print_metrics(name, result_data):
    metrics = result_data.get('metrics', {})
    print(f"\n--- Results for {name} ---")
    print(f"Total Return: {metrics.get('total_return_percentage', 0):.2f}%")
    print(f"Total PnL: ${metrics.get('total_pnl', 0):.2f}")
    print(f"Max Drawdown: {metrics.get('max_drawdown_percentage', 0):.2f}%")
    print(f"Total Trades: {metrics.get('total_trades', 0)}")
    win_rate = metrics.get('win_rate', 0)
    if win_rate is None: win_rate = 0
    print(f"Win Rate: {win_rate * 100:.2f}%")
    print(f"Profit Factor: {metrics.get('profit_factor', 0):.3f}")

if __name__ == "__main__":
    asyncio.run(run_comparison())
