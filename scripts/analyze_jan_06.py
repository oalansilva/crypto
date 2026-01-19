import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
sys.path.append(os.getcwd())

from app.services.combo_service import ComboService
from src.data.incremental_loader import IncrementalLoader
import pandas as pd

def analyze_jan_06():
    service = ComboService()
    loader = IncrementalLoader()
    
    # Get data with enough history
    df = loader.fetch_data("BTC/USDT", "1d", "2025-11-15", "2026-01-10")
    
    # TradingView parameters
    params = {
        "ema_short": 3,
        "sma_medium": 32,
        "sma_long": 37,
        "stop_loss": 0.027
    }
    
    strategy = service.create_strategy("multi_ma_crossover", parameters=params)
    df_signals = strategy.generate_signals(df.copy())
    
    # Focus on Jan 02-07
    focus = df_signals.loc['2026-01-02':'2026-01-07']
    
    print("=== Análise Detalhada 02-07 Jan ===\n")
    print("Data       | Close    | Short(EMA3) | Medium(SMA32) | Long(SMA37) | S>L | S>M | CrossS,L | CrossS,M | Signal")
    print("-" * 140)
    
    for i, (idx, row) in enumerate(focus.iterrows()):
        # Skip NaN
        if pd.isna(row['short']) or pd.isna(row['medium']) or pd.isna(row['long']):
            continue
        
        # Check conditions
        short_above_long = row['short'] > row['long']
        short_above_med = row['short'] > row['medium']
        
        # Check crossovers
        if i > 0:
            prev_row = focus.iloc[i-1]
            if not pd.isna(prev_row['short']):
                cross_long = (row['short'] > row['long']) and (prev_row['short'] <= prev_row['long'])
                cross_med = (row['short'] > row['medium']) and (prev_row['short'] <= prev_row['medium'])
            else:
                cross_long = False
                cross_med = False
        else:
            cross_long = False
            cross_med = False
        
        signal_str = ""
        if row['signal'] == 1:
            signal_str = "🟢 BUY"
        elif row['signal'] == -1:
            signal_str = "🔴 SELL"
        
        print(f"{idx.strftime('%Y-%m-%d')} | ${row['close']:8.2f} | {row['short']:11.2f} | {row['medium']:13.2f} | {row['long']:11.2f} | "
              f"{'Y' if short_above_long else 'N'} | {'Y' if short_above_med else 'N'} | "
              f"{'Y' if cross_long else 'N':8s} | {'Y' if cross_med else 'N':8s} | {signal_str}")
    
    print("\n=== Lógica de Entrada ===")
    print("BUY = (CrossS,L OR CrossS,M) AND (S > L)")
    print("\nOnde:")
    print("  CrossS,L = Short cruza ACIMA de Long")
    print("  CrossS,M = Short cruza ACIMA de Medium")
    print("  S > L = Short está ACIMA de Long")

if __name__ == "__main__":
    analyze_jan_06()
