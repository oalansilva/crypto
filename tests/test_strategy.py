import pytest
import pandas as pd
from src.strategy.sma_cross import SMACrossStrategy

def test_sma_cross_signals():
    # Construct a scenario where SMA behaves predictably
    # Fast (2) Slow (4)
    # Prices: 10, 20, 30, 40, 50, 60, 20, 10
    
    # SMA2: -, 15, 25, 35, 45, 55, 40, 15
    # SMA4: -, -, -, 25, 35, 45, 42.5, 35
    
    # Compare:
    # 3: SMA2(25) vs SMA4(25) -> Equal (Assume hold)
    # 4: SMA2(35) > SMA4(25) -> CROSS UP? No, prev was undef. 
    # Let's simple check logical outcome from code
    
    prices = [10, 10, 10, 10, 10, 20, 30, 40, 10, 10]
    df = pd.DataFrame({'close': prices})
    
    # Init strategy
    strategy = SMACrossStrategy(fast=2, slow=4)
    signals = strategy.generate_signals(df)
    
    # Just verify we get a series of length 10
    assert len(signals) == 10
    # Verify values are in {-1, 0, 1}
    assert signals.isin([-1, 0, 1]).all()
    
    # Manual verify:
    # SMA2: [NaN, 10, 10, 10, 10, 15, 25, 35, 25, 10]
    # SMA4: [NaN, NaN, NaN, 10, 10, 12.5, 17.5, 25, 25, 17.5]
    
    # Idx 5: SMA2(15) > SMA4(12.5). Prev Idx 4: SMA2(10) <= SMA4(10).
    # THIS IS CROSS OVER -> BUY (1)
    
    # Idx 8: SMA2(25) <= SMA4(25). Prev Idx 7: SMA2(35) > SMA4(25).
    # THIS IS CROSS UNDER -> SELL (-1) (Wait, code says < vs >. <= to < includes equality? 
    # Logic: sell_cond = (prev_fast >= prev_slow) & (df['sma_fast'] < df['sma_slow'])
    # prev(35) >= prev(25) True. curr(25) < curr(25) False. 
    # So Idx 8 is Hold (0).
    
    # Idx 9: SMA2(10) < SMA4(17.5). Prev Idx 8: SMA2(25) == SMA4(25).
    # sell_cond = (25 >= 25) & (10 < 17.5). True & True -> SELL (-1)
    
    assert signals.iloc[5] == 1
    assert signals.iloc[9] == -1
