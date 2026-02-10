import json
import sys
from pathlib import Path

import pytest

BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.routes import lab as lab_routes


class _FakeCombo:
    def __init__(self):
        self.templates = {}

    def create_template(self, name, template_data, category=None, metadata=None):
        self.templates[name] = {
            "template_data": template_data,
            "category": category,
            "metadata": metadata,
        }


def test_convert_idea_to_logic():
    assert lab_routes._convert_idea_to_logic("RSI < 30 E preço > EMA(50)") == "rsi < 30 and close > ema"
    assert lab_routes._convert_idea_to_logic("ADX(14) > 20 OU volume alto") == "adx > 20 or volume alto"
    assert lab_routes._convert_idea_to_logic("close ≥ bb_upper") == "close >= bb_upper"


def test_extract_stop_loss_from_plan():
    assert lab_routes._extract_stop_loss_from_plan("stop-loss 3%") == 0.03
    assert lab_routes._extract_stop_loss_from_plan("stop_loss: 2.5%") == 0.025
    assert lab_routes._extract_stop_loss_from_plan("sem stop") is None


def test_create_template_from_strategy_draft(monkeypatch):
    combo = _FakeCombo()

    monkeypatch.setattr(lab_routes, "_append_trace", lambda *args, **kwargs: None)
    monkeypatch.setattr(lab_routes, "_now_ms", lambda: 1)

    strategy_draft = {
        "indicators": [
            {"source": "pandas_ta", "name": "rsi", "params": {"length": 14}},
            {"source": "pandas_ta", "name": "ema", "params": {"length": 50}},
        ],
        "entry_idea": "RSI < 30 E preço > EMA(50)",
        "exit_idea": "RSI > 70 OU stop-loss 3%",
        "risk_plan": "Max drawdown 20%, stop-loss 3%",
    }

    template_name = lab_routes._create_template_from_strategy_draft(
        combo=combo,
        strategy_draft=strategy_draft,
        symbol="BTC/USDT",
        timeframe="4h",
        run_id="9a136922",
    )

    assert template_name == "lab_9a136922_draft_BTC_USDT_4h"
    meta = combo.templates[template_name]["template_data"]
    assert meta["entry_logic"] == "rsi < 30 and close > ema"
    assert meta["exit_logic"] == "rsi > 70 or stop-loss 3%"
    assert meta["stop_loss"] == 0.03
