import pandas as pd
from src.data.ccxt_loader import CCXTLoader
from src.engine.backtester import Backtester
from src.strategy.rsi_reversal import RSIReversalStrategy

def debug_rsi():
    loader = CCXTLoader()
    # Fetch ample data
    df = loader.fetch_data('BTC/USDT', '4h', '2023-01-01 00:00:00', '2023-06-01 00:00:00')
    
    strategy = RSIReversalStrategy() # Default params
    backtester = Backtester(initial_capital=10000)
    
    print("Running RSI Backtest...")
    backtester.run(df, strategy)
    
    print(f"Total Trades: {len(backtester.trades)}")
    
    for i, t in enumerate(backtester.trades):
        if t['side'] == 'SELL':
            print(f"Trade {i}: Sell at {t['price']:.2f}, Size {t['size']:.4f}, PnL {t['pnl']:.2f}, Reason: {t['reason']}")
        elif t['side'] == 'BUY':
             print(f"Trade {i}: Buy at {t['price']:.2f}, Size {t['size']:.4f}")

if __name__ == "__main__":
    debug_rsi()
