import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
sys.path.append(os.getcwd())

from app.services.combo_service import ComboService
from src.data.incremental_loader import IncrementalLoader
import pandas as pd

def analyze_crossover():
    service = ComboService()
    loader = IncrementalLoader()
    
    # Get data with enough history for SMA(37) warmup
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
    
    # Focus on Dec 30 - Jan 05
    focus = df_signals.loc['2025-12-30':'2026-01-05']
    
    print("=== Análise Detalhada do Crossover ===\n")
    print("Data       | Close    | Short(EMA3) | Medium(SMA32) | Long(SMA37) | Short>Long | Cross(S,L) | Cross(S,M) | Signal")
    print("-" * 130)
    
    for i, (idx, row) in enumerate(focus.iterrows()):
        # Skip rows with NaN values (warmup period)
        if pd.isna(row['short']) or pd.isna(row['medium']) or pd.isna(row['long']):
            continue
            
        # Check crossover conditions manually
        if i > 0:
            prev_row = focus.iloc[i-1]
            
            # Skip if previous row has NaN
            if pd.isna(prev_row['short']) or pd.isna(prev_row['medium']) or pd.isna(prev_row['long']):
                cross_long = False
                cross_med = False
                short_above_long = row['short'] > row['long']
                signal_str = ""
            else:
                # Crossover short with long
                cross_long = (row['short'] > row['long']) and (prev_row['short'] <= prev_row['long'])
                
                # Crossover short with medium
                cross_med = (row['short'] > row['medium']) and (prev_row['short'] <= prev_row['medium'])
                
                short_above_long = row['short'] > row['long']
                
                signal_str = ""
                if row['signal'] == 1:
                    signal_str = "🟢 BUY"
        else:
            cross_long = False
            cross_med = False
            short_above_long = row['short'] > row['long']
            signal_str = ""
        
        print(f"{idx.strftime('%Y-%m-%d')} | ${row['close']:8.2f} | {row['short']:11.2f} | {row['medium']:13.2f} | {row['long']:11.2f} | "
              f"{'YES' if short_above_long else 'NO ':3s} | {'YES' if cross_long else 'NO ':3s} | "
              f"{'YES' if cross_med else 'NO ':3s} | {signal_str}")
    
    print("\n=== Legenda ===")
    print("Cross(S,L) = Crossover de Short com Long")
    print("Cross(S,M) = Crossover de Short com Medium")
    print("BUY Signal = (Cross(S,L) OR Cross(S,M)) AND (Short > Long)")

if __name__ == "__main__":
    analyze_crossover()
