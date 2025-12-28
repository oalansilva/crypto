import pytest
import pandas as pd
from src.engine.backtester import Backtester
from src.strategy.base import Strategy

# Mock Strategy that returns specific signals
class MockStrategy(Strategy):
    def __init__(self, signals):
        super().__init__()
        self.signals = signals # List of signals matching DF length

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        return pd.Series(self.signals, index=df.index)

@pytest.fixture
def sample_data():
    dates = pd.date_range(start='2023-01-01', periods=5, freq='D')
    df = pd.DataFrame({
        'timestamp_utc': dates,
        'open': [100, 105, 110, 108, 112],
        'high': [102, 108, 115, 110, 115],
        'low': [98, 100, 105, 105, 108],
        'close': [101, 106, 112, 109, 113],
        'volume': [1000] * 5
    })
    return df

def test_fee_application(sample_data):
    # Test if fee is deducted correctly on BUY
    # Cash 10000. PosSize 20% = 2000.
    # Fee 10% (0.1) for easy math.
    # Buy 2000 worth. Fee should be 200.
    backtester = Backtester(initial_capital=10000, fee=0.1, slippage=0, position_size_pct=0.2)
    strategy = MockStrategy([1, 0, 0, 0, 0]) # Buy on first candle
    
    backtester.run(sample_data, strategy)
    
    trade = backtester.trades[0]
    expected_commission = trade['size'] * trade['price'] * 0.1
    assert abs(trade['commission'] - expected_commission) < 0.01

def test_slippage_application(sample_data):
    # Test if slippage increases buy price
    # Slippage 10% (0.1)
    # Buy Price (Close) = 101
    # Exec price should be 101 * 1.1 = 111.1
    backtester = Backtester(initial_capital=10000, fee=0, slippage=0.1, position_size_pct=0.2)
    strategy = MockStrategy([1, 0, 0, 0, 0])
    
    backtester.run(sample_data, strategy)
    trade = backtester.trades[0]
    assert abs(trade['price'] - (101 * 1.1)) < 0.01

def test_market_buy_long_only_no_cash(sample_data):
    # Try to buy with 0 cash
    backtester = Backtester(initial_capital=0, fee=0, slippage=0, position_size_pct=0.2)
    strategy = MockStrategy([1, 0, 0, 0, 0])
    
    backtester.run(sample_data, strategy)
    assert len(backtester.trades) == 0, "Should not trade with 0 details"

def test_market_sell_long_only_no_position(sample_data):
    # Try to sell without position
    backtester = Backtester(initial_capital=10000, fee=0, slippage=0, position_size_pct=0.2)
    strategy = MockStrategy([-1, 0, 0, 0, 0])
    
    backtester.run(sample_data, strategy)
    assert len(backtester.trades) == 0, "Should not sell with 0 position"
