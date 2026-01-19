import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
sys.path.append(os.getcwd())

from app.services.combo_service import ComboService
from src.data.incremental_loader import IncrementalLoader
import pandas as pd

def analyze_all_signals():
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
    
    # Focus on recent period
    focus = df_signals.loc['2025-12-30':'2026-01-10']
    
    print("=== Todos os Sinais (Compra E Venda) ===\n")
    print("Data       | Close    | Short(EMA3) | Medium(SMA32) | Long(SMA37) | Signal")
    print("-" * 100)
    
    for idx, row in focus.iterrows():
        # Skip NaN
        if pd.isna(row['short']) or pd.isna(row['medium']) or pd.isna(row['long']):
            continue
        
        signal_str = ""
        if row['signal'] == 1:
            signal_str = "🟢 COMPRA"
        elif row['signal'] == -1:
            signal_str = "🔴 VENDA"
        
        print(f"{idx.strftime('%Y-%m-%d')} | ${row['close']:8.2f} | {row['short']:11.2f} | {row['medium']:13.2f} | {row['long']:11.2f} | {signal_str}")
    
    print("\n=== Resumo de Sinais ===")
    buy_signals = focus[focus['signal'] == 1]
    sell_signals = focus[focus['signal'] == -1]
    
    print(f"Total COMPRA: {len(buy_signals)}")
    print(f"Total VENDA: {len(sell_signals)}")
    
    print("\n=== Datas de COMPRA ===")
    for idx in buy_signals.index:
        print(f"  {idx.strftime('%Y-%m-%d (%a)')}")
    
    print("\n=== Datas de VENDA ===")
    for idx in sell_signals.index:
        print(f"  {idx.strftime('%Y-%m-%d (%a)')}")

if __name__ == "__main__":
    analyze_all_signals()
