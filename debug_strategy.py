import pandas as pd
from src.data.ccxt_loader import CCXTLoader
from src.engine.backtester import Backtester
from src.strategy.sma_cross import SMACrossStrategy

def debug_run():
    # 1. Fetch small amount of data ensuring volatility
    print("Fetching data...")
    loader = CCXTLoader()
    # Puxar dados de 2023 (onde sabemos que houve movimento)
    df = loader.fetch_data('BTC/USDT', '4h', '2023-01-01 00:00:00', '2023-03-01 00:00:00')
    
    print(f"Data fetched: {len(df)} rows")
    
    # 2. Generate Signals directly and inspect
    print("\nGenerating SMA signals (Fast=20, Slow=50)...")
    strategy = SMACrossStrategy(fast=20, slow=50)
    signals = strategy.generate_signals(df)
    
    # Check if we have ANY signals
    buy_signals = signals[signals == 1]
    sell_signals = signals[signals == -1]
    
    print(f"Total Buy Signals: {len(buy_signals)}")
    print(f"Total Sell Signals: {len(sell_signals)}")
    
    if not buy_signals.empty:
        print("First buy signal at:", df.loc[buy_signals.index[0], 'timestamp_utc'])
        
    if not sell_signals.empty:
        print("First sell signal at:", df.loc[sell_signals.index[0], 'timestamp_utc'])

    # 3. Run Backtester with verbose prints (we need to modify Backtester or just trust the trace)
    # Let's run standard backtest and check trades list directly
    print("\nRunning Backtester...")
    backtester = Backtester(initial_capital=10000, fee=0.001, slippage=0.0005, position_size_pct=0.9) # 90% size to ensure entry
    backtester.run(df, strategy)
    
    print(f"\nTrades recorded: {len(backtester.trades)}")
    for t in backtester.trades:
        print(t)
        
    print(f"Final Position: {backtester.position}")
    print(f"Final Cash: {backtester.cash}")

if __name__ == "__main__":
    debug_run()
