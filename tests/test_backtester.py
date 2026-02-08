import asyncio
import json
import sys
from pathlib import Path

import pytest
import pandas as pd
from fastapi import BackgroundTasks
from src.engine.backtester import Backtester
from src.strategy.base import Strategy

# Access backend route tests from root pytest invocation.
BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.routes import lab as lab_routes

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
    # NOTE: Backtester only records a trade when it is CLOSED.
    # So we must also emit a sell signal to close the position.
    strategy = MockStrategy([1, 0, 0, 0, -1]) # Buy first candle, sell last candle

    backtester.run(sample_data, strategy)

    trade = backtester.trades[0]

    # Commission stored on trade is total (entry + exit)
    entry_commission = trade['size'] * trade['entry_price'] * 0.1
    exit_commission = trade['size'] * trade['exit_price'] * 0.1
    expected_total_commission = entry_commission + exit_commission
    assert abs(trade['commission'] - expected_total_commission) < 0.01

def test_slippage_application(sample_data):
    # Test if slippage increases buy price
    # Slippage 10% (0.1)
    # Buy Price (Close) = 101
    # Exec price should be 101 * 1.1 = 111.1
    backtester = Backtester(initial_capital=10000, fee=0, slippage=0.1, position_size_pct=0.2)
    # Close the trade so Backtester records it
    strategy = MockStrategy([1, 0, 0, 0, -1])

    backtester.run(sample_data, strategy)
    trade = backtester.trades[0]
    assert abs(trade['entry_price'] - (101 * 1.1)) < 0.01

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


class _FixedUUID:
    hex = "fixedrunid1234567890"


def test_create_run_returns_needs_user_input_when_missing_required_fields(tmp_path, monkeypatch):
    monkeypatch.setattr(lab_routes, "_run_path", lambda run_id: tmp_path / f"{run_id}.json")
    monkeypatch.setattr(lab_routes, "_trace_path", lambda run_id: tmp_path / f"{run_id}.jsonl")

    req = lab_routes.LabRunCreateRequest(objective="rodar lab")
    resp = asyncio.run(lab_routes.create_run(req, BackgroundTasks()))

    assert isinstance(resp, lab_routes.LabRunNeedsUserInputResponse)
    assert resp.status == "needs_user_input"
    assert resp.missing == ["symbol", "timeframe"]
    assert "symbol" in resp.question
    assert "timeframe" in resp.question
    assert list(tmp_path.iterdir()) == []


def test_create_run_accepts_when_symbol_and_timeframe_are_present(tmp_path, monkeypatch):
    monkeypatch.setattr(lab_routes, "_run_path", lambda run_id: tmp_path / f"{run_id}.json")
    monkeypatch.setattr(lab_routes, "_trace_path", lambda run_id: tmp_path / f"{run_id}.jsonl")
    monkeypatch.setattr(lab_routes.uuid, "uuid4", lambda: _FixedUUID())

    req = lab_routes.LabRunCreateRequest(
        symbol="BTC/USDT",
        timeframe="1h",
        objective="rodar com foco em robustez",
    )
    resp = asyncio.run(lab_routes.create_run(req, BackgroundTasks()))

    assert isinstance(resp, lab_routes.LabRunCreateResponse)
    assert resp.status == "accepted"
    assert resp.run_id == _FixedUUID.hex

    run_file = tmp_path / f"{_FixedUUID.hex}.json"
    trace_file = tmp_path / f"{_FixedUUID.hex}.jsonl"
    assert run_file.exists()
    assert trace_file.exists()

    payload = json.loads(run_file.read_text(encoding="utf-8"))
    assert payload["status"] == "accepted"
    assert payload["input"]["symbol"] == "BTC/USDT"
    assert payload["input"]["timeframe"] == "1h"
    assert "base_template" not in payload["input"]
