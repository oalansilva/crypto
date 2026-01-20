import sys
import os
import pandas as pd
import numpy as np

# Add project root and backend
current_dir = os.getcwd()
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'backend'))

from src.data.incremental_loader import IncrementalLoader
from app.services.combo_service import ComboService
from app.services.combo_optimizer import extract_trades_from_signals

def calc_metrics(trades, initial_capital=1000):
    if not trades:
        return {
            "Total Return": 0.0,
            "Trades": 0,
            "Win Rate": 0.0,
            "Profit Factor": 0.0
        }
        
    df_trades = pd.DataFrame(trades)
    
    # Calculate cumulative profit
    # Assuming fixed position size or compounding?
    # Optimizer logic usually sums simple returns or compounds. 
    # Let's use simple sum of percentages for quick comparison, 
    # or actual PnL if we simulate an account.
    
    # Simple Return (Sum of %s)
    simple_return_pct = df_trades['profit'].sum() * 100
    
    # Compounded Return (Cumulative)
    # Start with 1.0 (100%), multiply by (1 + profit_pct) for each trade
    # e.g., +10% -> * 1.10, -5% -> * 0.95
    final_equity_multiplier = (1 + df_trades['profit']).prod()
    compounded_return_pct = (final_equity_multiplier - 1) * 100
    
    win_rate = (len(df_trades[df_trades['profit'] > 0]) / len(df_trades)) * 100
    
    wins = df_trades[df_trades['profit'] > 0]['profit'].sum()
    losses = abs(df_trades[df_trades['profit'] < 0]['profit'].sum())
    profit_factor = wins / losses if losses > 0 else float('inf')
    
    return {
        "Simple Return %": simple_return_pct,
        "Compounded Return %": compounded_return_pct, # Added this
        "Trades": len(trades),
        "Win Rate %": win_rate,
        "Profit Factor": profit_factor
    }

def run_comparison():
    print("\n" + "="*80)
    print("COMPARATIVO DE PARÂMETROS: ATUAL (Otimizado) vs ANTIGO")
    print("="*80)
    
    loader = IncrementalLoader()
    # Fetch ample data to strictly cover the user's test period (e.g. last 1-2 years or full history)
    # User's screenshots show 2025 trades, assuming we are backtesting on the generated/future data 
    # or the dataset the user implied. I will fetch a large range.
    df = loader.fetch_data(
        symbol="BTC/USDT",
        timeframe="1d",
        since_str="2017-08-17",  # Binance Start Date
        until_str="2025-10-15"
    )
    
    combo_service = ComboService()
    template = "multi_ma_crossover"
    
    # --- SET A: ATUAL (Otimizado) ---
    params_actual = {
        "short_length": 7,
        "medium_length": 21,
        "long_length": 44,
        "stop_loss": 0.015
    }
    
    # --- SET B: ANTIGO ---
    params_old = {
        "short_length": 3,
        "medium_length": 32,
        "long_length": 37,
        "stop_loss": 0.027
    }
    
    # Run Validations
    results = []
    
    for name, params in [("ATUAL (Sistema)", params_actual), ("ANTIGO (Manual)", params_old)]:
        print(f"\n⚡ Rodando: {name}")
        print(f"   Params: {params}")
        
        strategy = combo_service.create_strategy(template, params)
        df_signals = strategy.generate_signals(df.copy())
        trades = extract_trades_from_signals(df_signals, stop_loss=params['stop_loss'])
        
        metrics = calc_metrics(trades)
        metrics['Name'] = name
        results.append(metrics)
        
        if metrics['Trades'] > 0:
            print(f"   Trades: {metrics['Trades']}")
            print(f"   Simple: {metrics['Simple Return %']:.2f}%")
            print(f"   Compound: {metrics['Compounded Return %']:.2f}%")
        else:
             print("   No trades found.")

    # Final Comparison Table
    print("\n" + "="*80)
    print("RELATÓRIO FINAL DE EVIDÊNCIAS")
    print("="*80)
    print(f"{'METRIC':<20} | {'ATUAL (7/21/44)':<20} | {'ANTIGO (3/32/37)':<20}")
    print("-" * 70)
    
    keys = ["Simple Return %", "Compounded Return %", "Trades", "Win Rate %", "Profit Factor"]
    for k in keys:
        val_actual = results[0][k]
        val_old = results[1][k]
        
        # Format
        if isinstance(val_actual, float):
            str_a = f"{val_actual:.2f}"
            str_b = f"{val_old:.2f}"
        else:
            str_a = str(val_actual)
            str_b = str(val_old)
            
        # Highlight winner
        better = ""
        if k != "Trades": # For return/wr/pf, higher is better
            if val_actual > val_old: better = "<< VENCEDOR"
            elif val_old > val_actual: better = "VENCEDOR >>"
            
        print(f"{k:<20} | {str_a:<20} | {str_b:<20} {better}")
        
    print("="*80)

if __name__ == "__main__":
    run_comparison()
