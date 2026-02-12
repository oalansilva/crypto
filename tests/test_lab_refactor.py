import json
import sys
import time
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

    def get_template_metadata(self, name):
        item = self.templates.get(name)
        if not item:
            return None
        return item.get("template_data")

    def update_template(self, template_name, description=None, optimization_schema=None, template_data=None):
        if template_name not in self.templates:
            raise ValueError("Template not found")
        current = self.templates[template_name]["template_data"]
        if template_data:
            merged = {**current, **template_data}
            self.templates[template_name]["template_data"] = merged
        return True


def test_convert_idea_to_logic():
    assert lab_routes._convert_idea_to_logic("RSI < 30 E preço > EMA(50)") == "rsi < 30 and close > ema"
    assert lab_routes._convert_idea_to_logic("ADX(14) > 20 OU volume alto") == "adx > 20 or volume alto"
    assert lab_routes._convert_idea_to_logic("close ≥ bb_upper") == "close >= bb_upper"


def test_extract_stop_loss_from_plan():
    assert lab_routes._extract_stop_loss_from_plan("stop-loss 3%") == 0.03
    assert lab_routes._extract_stop_loss_from_plan("stop_loss: 2.5%") == 0.025
    assert lab_routes._extract_stop_loss_from_plan("sem stop") is None


def test_normalize_timeframe_uppercase():
    normalized, changed = lab_routes._normalize_timeframe("4H")
    assert normalized == "4h"
    assert changed is True


def test_normalize_symbol_slash():
    normalized, exchange_symbol, changed = lab_routes._normalize_symbol("btc/usdt")
    assert normalized == "BTC/USDT"
    assert exchange_symbol == "BTCUSDT"
    assert changed is True


def test_classify_invalid_interval_error():
    diagnostic = lab_routes._classify_backtest_error(Exception("Invalid interval"))
    assert diagnostic["type"] == "invalid_interval"


def test_classify_duplicate_alias_error():
    diagnostic = lab_routes._classify_backtest_error(Exception("Duplicate aliases found: {'ema'}"))
    assert diagnostic["type"] == "duplicate_indicator_alias"


def test_run_lab_autonomous_async_wrapper(monkeypatch):
    called = {}

    def _fake_sync(run_id, req_dict):
        called["run_id"] = run_id

    monkeypatch.setattr(lab_routes, "_run_lab_autonomous_sync", _fake_sync)
    lab_routes._run_lab_autonomous("run-123", {"symbol": "BTC/USDT"})
    time.sleep(0.01)
    assert called.get("run_id") == "run-123"


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


def test_apply_dev_adjustments_relaxes_and_adds_atr():
    combo = _FakeCombo()
    combo.create_template(
        "tpl",
        {
            "indicators": [
                {"type": "ema", "alias": "ema50", "params": {"length": 50}},
                {"type": "adx", "alias": "adx14", "params": {"length": 14}},
                {"type": "rsi", "alias": "rsi14", "params": {"length": 14}},
            ],
            "entry_logic": "Entrar comprado quando: close > ema200 AND ema50 > ema200 AND adx14 > 20 AND rsi14 <= 50 AND close cruza acima da ema50.",
            "exit_logic": "Sair quando: trailing stop de 2*ATR.",
            "stop_loss": "Stop inicial em 1.5*ATR abaixo do preço de entrada.",
        },
    )

    changed, changes = lab_routes._apply_dev_adjustments(combo=combo, template_name="tpl", attempt=1)
    assert changed is True
    assert "relax_rsi_upper" in changes
    assert "relax_adx_threshold" in changes
    assert "remove_ema_cross" in changes
    assert "add_atr_indicator" in changes

    meta = combo.get_template_metadata("tpl")
    assert any(ind.get("type") == "atr" for ind in meta.get("indicators") or [])
    assert "rsi14 <= 55" in meta.get("entry_logic")


def test_needs_dev_adjustment_on_zero_trades():
    run = {
        "input": {"constraints": {"min_holdout_trades": 10, "min_sharpe": 0.4}},
        "backtest": {
            "walk_forward": {
                "holdout": {"metrics": {"total_trades": 0, "sharpe_ratio": 0.0, "max_drawdown": 0.0}},
                "in_sample": {"metrics": {"total_trades": 0}},
            }
        },
    }
    needs, ctx = lab_routes._needs_dev_adjustment(run)
    assert needs is True
    assert ctx["selection"]["approved"] is False


def test_needs_dev_adjustment_ok_when_metrics_pass():
    run = {
        "input": {"constraints": {"min_holdout_trades": 10, "min_sharpe": 0.4}},
        "backtest": {
            "walk_forward": {
                "holdout": {"metrics": {"total_trades": 12, "sharpe_ratio": 0.6, "max_drawdown": 0.1}},
                "in_sample": {"metrics": {"total_trades": 20}},
            }
        },
    }
    needs, ctx = lab_routes._needs_dev_adjustment(run)
    assert needs is False
    assert ctx["selection"]["approved"] is True
