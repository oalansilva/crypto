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


def test_create_run_initializes_upstream_chat_when_missing_required_fields(tmp_path, monkeypatch):
    monkeypatch.setattr(lab_routes, "_run_path", lambda run_id: tmp_path / f"{run_id}.json")
    monkeypatch.setattr(lab_routes, "_trace_path", lambda run_id: tmp_path / f"{run_id}.jsonl")
    monkeypatch.setattr(lab_routes.uuid, "uuid4", lambda: _FixedUUID())
    monkeypatch.setattr(lab_routes, "_try_trader_upstream_turn", lambda **kwargs: {"reply": "Qual symbol e timeframe?"})

    req = lab_routes.LabRunCreateRequest(objective="rodar lab")
    resp = asyncio.run(lab_routes.create_run(req, BackgroundTasks()))

    assert isinstance(resp, lab_routes.LabRunCreateResponse)
    assert resp.status == "needs_user_input"
    assert resp.run_id == _FixedUUID.hex

    run_file = tmp_path / f"{_FixedUUID.hex}.json"
    assert run_file.exists()
    payload = json.loads(run_file.read_text(encoding="utf-8"))

    assert payload["status"] == "needs_user_input"
    assert payload["phase"] == "upstream"
    assert payload["upstream_contract"]["approved"] is False
    assert payload["upstream"]["pending_question"] == "Qual symbol e timeframe?"
    assert payload["upstream"]["messages"][-1]["role"] == "trader"
    assert "symbol" in payload["upstream_contract"]["missing"]
    assert "timeframe" in payload["upstream_contract"]["missing"]


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
    assert resp.status == "ready_for_execution"
    assert resp.run_id == _FixedUUID.hex

    run_file = tmp_path / f"{_FixedUUID.hex}.json"
    trace_file = tmp_path / f"{_FixedUUID.hex}.jsonl"
    assert run_file.exists()
    assert trace_file.exists()

    payload = json.loads(run_file.read_text(encoding="utf-8"))
    assert payload["status"] == "ready_for_execution"
    assert payload["phase"] == "upstream"
    assert payload["upstream_contract"]["approved"] is True
    assert payload["upstream"]["messages"] == []
    assert payload["upstream"]["pending_question"] == ""
    assert payload["upstream_contract"]["inputs"]["symbol"] == "BTC/USDT"
    assert payload["upstream_contract"]["inputs"]["timeframe"] == "1h"
    assert payload["input"]["symbol"] == "BTC/USDT"
    assert payload["input"]["timeframe"] == "1h"
    assert "base_template" not in payload["input"]


def test_post_upstream_message_persists_history_and_updates_contract(tmp_path, monkeypatch):
    monkeypatch.setattr(lab_routes, "_run_path", lambda run_id: tmp_path / f"{run_id}.json")
    monkeypatch.setattr(lab_routes, "_trace_path", lambda run_id: tmp_path / f"{run_id}.jsonl")
    monkeypatch.setattr(lab_routes.uuid, "uuid4", lambda: _FixedUUID())

    # Initial turn: asks for missing symbol/timeframe.
    monkeypatch.setattr(lab_routes, "_try_trader_upstream_turn", lambda **kwargs: {"reply": "Qual symbol e timeframe?"})
    req = lab_routes.LabRunCreateRequest(objective="rodar lab")
    resp = asyncio.run(lab_routes.create_run(req, BackgroundTasks()))
    assert resp.run_id == _FixedUUID.hex

    # User answers with required fields; trader confirms.
    monkeypatch.setattr(lab_routes, "_try_trader_upstream_turn", lambda **kwargs: {"reply": "Perfeito, contrato aprovado."})
    msg_req = lab_routes.LabRunUpstreamMessageRequest(message="symbol=BTC/USDT timeframe=1h")
    msg_resp = asyncio.run(lab_routes.post_upstream_message(_FixedUUID.hex, msg_req))

    assert msg_resp.status == "ready_for_execution"
    assert msg_resp.phase == "upstream"
    assert msg_resp.upstream_contract["approved"] is True

    run_file = tmp_path / f"{_FixedUUID.hex}.json"
    payload = json.loads(run_file.read_text(encoding="utf-8"))
    assert payload["status"] == "ready_for_execution"
    assert payload["upstream_contract"]["approved"] is True
    assert payload["upstream_contract"]["inputs"]["symbol"] == "BTC/USDT"
    assert payload["upstream_contract"]["inputs"]["timeframe"] == "1h"
    assert payload["upstream"]["pending_question"] == ""
    assert payload["upstream"]["messages"][-2]["role"] == "user"
    assert payload["upstream"]["messages"][-1]["role"] == "trader"

    trace_file = tmp_path / f"{_FixedUUID.hex}.jsonl"
    trace_lines = [json.loads(line) for line in trace_file.read_text(encoding="utf-8").splitlines() if line.strip()]
    trace_types = [line.get("type") for line in trace_lines]
    assert "upstream_message" in trace_types
    assert "upstream_contract_updated" in trace_types
    assert "upstream_approved" in trace_types


class _FakeTwoPhaseGraph:
    def invoke(self, state):
        outputs = dict(state.get("outputs") or {})
        outputs["coordinator_summary"] = "ok"
        outputs["dev_summary"] = "{\"candidate_template_data\": {\"indicators\": []}}"
        outputs["validator_verdict"] = "{\"verdict\":\"approved\",\"reasons\":[],\"required_fixes\":[],\"notes\":\"ok\"}"
        outputs["tests_done"] = {"pass": True}
        outputs["final_decision"] = {"status": "done", "tests_pass": True}
        return {
            **state,
            "outputs": outputs,
            "budget": state.get("budget") or {},
            "upstream_contract": {
                "approved": True,
                "missing": [],
                "question": "",
                "inputs": {"symbol": "BTC/USDT", "timeframe": "1h"},
                "objective": "rodar com foco em robustez",
                "acceptance_criteria": ["a", "b"],
                "risk_notes": ["r1"],
            },
            "phase": "done",
            "status": "done",
        }


def test_cp4_two_phase_approved_updates_phase_and_status(tmp_path, monkeypatch):
    monkeypatch.setattr(lab_routes, "_run_path", lambda run_id: tmp_path / f"{run_id}.json")
    monkeypatch.setattr(lab_routes, "_trace_path", lambda run_id: tmp_path / f"{run_id}.jsonl")
    monkeypatch.setattr(lab_routes, "_cp8_save_candidate_template", lambda run_id, run, outputs: outputs)
    monkeypatch.setattr(lab_routes, "_cp5_autosave_if_approved", lambda run_id, run, outputs: outputs)

    import app.services.lab_graph as lab_graph

    monkeypatch.setattr(lab_graph, "build_cp7_graph", lambda: _FakeTwoPhaseGraph())

    run_id = "run_two_phase_ok"
    payload = {
        "run_id": run_id,
        "status": "running",
        "step": "upstream",
        "phase": "upstream",
        "created_at_ms": 1,
        "updated_at_ms": 1,
        "input": {"symbol": "BTC/USDT", "timeframe": "1h", "objective": "rodar com foco em robustez", "thinking": "low"},
        "session_key": f"lab-{run_id}",
        "budget": {"turns_used": 0, "turns_max": 12, "tokens_total": 0, "tokens_max": 60000, "on_limit": "ask_user"},
        "outputs": {"coordinator_summary": None, "dev_summary": None, "validator_verdict": None},
        "backtest": {},
        "needs_user_confirm": False,
    }
    (tmp_path / f"{run_id}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lab_routes._cp4_run_personas_if_possible(run_id)

    updated = json.loads((tmp_path / f"{run_id}.json").read_text(encoding="utf-8"))
    assert updated["status"] == "done"
    assert updated["phase"] == "done"
    assert updated["upstream_contract"]["approved"] is True
    assert updated["outputs"]["tests_done"]["pass"] is True
