import json
import copy
import sys
import time
from pathlib import Path

import pandas as pd
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
            "optimization_schema": None,
        }

    def get_template_metadata(self, name):
        item = self.templates.get(name)
        if not item:
            return None
        data = copy.deepcopy(item.get("template_data") or {})
        data["optimization_schema"] = copy.deepcopy(item.get("optimization_schema"))
        return data

    def update_template(self, template_name, description=None, optimization_schema=None, template_data=None):
        if template_name not in self.templates:
            raise ValueError("Template not found")
        current = self.templates[template_name]["template_data"]
        if template_data:
            merged = {**current, **template_data}
            self.templates[template_name]["template_data"] = merged
        if optimization_schema is not None:
            self.templates[template_name]["optimization_schema"] = copy.deepcopy(optimization_schema)
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
    schema = combo.templates[template_name]["optimization_schema"]
    assert isinstance(schema, dict)
    assert "parameters" in schema
    assert "correlated_groups" in schema
    assert isinstance(schema["correlated_groups"], list)
    assert schema["parameters"]["stop_loss"]["min"] == 0.005
    assert schema["parameters"]["stop_loss"]["max"] == 0.13
    assert schema["parameters"]["stop_loss"]["step"] == 0.002


def test_cp8_save_candidate_template_stages_in_run_outputs_only(monkeypatch):
    traces = []
    monkeypatch.setattr(lab_routes, "_append_trace", lambda run_id, event: traces.append(event))
    monkeypatch.setattr(lab_routes, "_now_ms", lambda: 1)

    run = {
        "input": {"base_template": "seed_tpl", "symbol": "BTC/USDT", "timeframe": "1h"},
        "backtest": {"template": "seed_tpl", "symbol": "BTC/USDT", "timeframe": "1h"},
    }
    outputs = {
        "dev_summary": json.dumps(
            {
                "candidate_template_data": {
                    "indicators": [{"type": "ema", "alias": "ema20", "params": {"length": 20}}],
                    "entry_logic": "close > ema20",
                    "exit_logic": "close < ema20",
                    "stop_loss": 0.03,
                },
                "description": "candidate memory-only",
            },
            ensure_ascii=False,
        )
    }

    result = lab_routes._cp8_save_candidate_template("run-cp8", run, outputs)

    assert result["candidate_template_name"].startswith("lab_run-cp8")
    assert isinstance(result.get("candidate_template_data"), dict)
    assert result["candidate_template_data"]["entry_logic"] == "close > ema20"
    assert result.get("saved_template_name") is None
    assert any(evt.get("type") == "candidate_staged" for evt in traces)


@pytest.mark.asyncio
async def test_post_run_approve_persists_template_on_explicit_trader_approval(monkeypatch, tmp_path):
    import app.services.combo_service as combo_service

    class _FakeComboService:
        created: dict = {}

        def __init__(self):
            pass

        def get_template_metadata(self, name):
            return copy.deepcopy(self.created.get(name))

        def create_template(self, name, template_data, category="custom", metadata=None):
            payload = copy.deepcopy(template_data)
            payload["name"] = name
            payload["description"] = (metadata or {}).get("description", "")
            self.created[name] = payload
            return payload

        def clone_template(self, template_name, new_name):
            if template_name not in self.created:
                raise ValueError("missing source")
            cloned = copy.deepcopy(self.created[template_name])
            cloned["name"] = new_name
            self.created[new_name] = cloned
            return cloned

        def update_template(self, template_name, description=None, optimization_schema=None, template_data=None):
            payload = self.created.get(template_name)
            if not payload:
                raise ValueError("missing")
            if isinstance(template_data, dict):
                payload.update(copy.deepcopy(template_data))
            if optimization_schema is not None:
                payload["optimization_schema"] = copy.deepcopy(optimization_schema)
            self.created[template_name] = payload
            return True

    monkeypatch.setattr(combo_service, "ComboService", _FakeComboService)
    monkeypatch.setattr(lab_routes, "_append_trace", lambda *args, **kwargs: None)
    monkeypatch.setattr(lab_routes, "_runs_dir", lambda: tmp_path)

    run_id = "run_approve_only"
    payload = {
        "run_id": run_id,
        "status": "ready_for_review",
        "step": "trader_review",
        "phase": "execution",
        "created_at_ms": 1,
        "updated_at_ms": 1,
        "input": {"symbol": "BTC/USDT", "timeframe": "1h", "base_template": "seed_tpl"},
        "backtest": {"symbol": "BTC/USDT", "timeframe": "1h", "template": "seed_tpl"},
        "outputs": {
            "gate_decision": {"approved": True, "verdict": "approved"},
            "candidate_template_name": "lab_seed_candidate",
            "candidate_template_description": "approved candidate",
            "candidate_template_data": {
                "indicators": [{"type": "ema", "alias": "ema20", "params": {"length": 20}}],
                "entry_logic": "close > ema20",
                "exit_logic": "close < ema20",
                "stop_loss": 0.03,
            },
            "saved_template_name": None,
        },
    }
    (tmp_path / f"{run_id}.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    response = await lab_routes.post_run_approve(run_id)

    assert response.decision == "approved"
    assert response.template_name

    updated = json.loads((tmp_path / f"{run_id}.json").read_text(encoding="utf-8"))
    assert updated["status"] == "approved"
    assert updated["outputs"]["saved_template_name"] == response.template_name
    assert updated["outputs"]["trader_review_decision"] == "approved"
    assert response.template_name in _FakeComboService.created


@pytest.mark.asyncio
async def test_post_run_reject_marks_rejected_without_persisting_template(monkeypatch, tmp_path):
    import app.services.combo_service as combo_service

    class _FailComboService:
        def __init__(self):
            raise AssertionError("ComboService should not be instantiated on reject")

    monkeypatch.setattr(combo_service, "ComboService", _FailComboService)
    monkeypatch.setattr(lab_routes, "_append_trace", lambda *args, **kwargs: None)
    monkeypatch.setattr(lab_routes, "_runs_dir", lambda: tmp_path)

    run_id = "run_reject_only"
    payload = {
        "run_id": run_id,
        "status": "ready_for_review",
        "step": "trader_review",
        "phase": "execution",
        "created_at_ms": 1,
        "updated_at_ms": 1,
        "input": {"symbol": "BTC/USDT", "timeframe": "1h"},
        "outputs": {
            "gate_decision": {"approved": True, "verdict": "approved"},
            "candidate_template_name": "lab_seed_candidate",
            "candidate_template_data": {
                "indicators": [{"type": "ema", "alias": "ema20", "params": {"length": 20}}],
                "entry_logic": "close > ema20",
                "exit_logic": "close < ema20",
                "stop_loss": 0.03,
            },
            "saved_template_name": None,
        },
    }
    (tmp_path / f"{run_id}.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    response = await lab_routes.post_run_reject(run_id, lab_routes.LabRunRejectRequest(reason="risk too high"))

    assert response.decision == "rejected"
    updated = json.loads((tmp_path / f"{run_id}.json").read_text(encoding="utf-8"))
    assert updated["status"] == "rejected"
    assert updated["outputs"].get("saved_template_name") is None
    assert updated["outputs"]["trader_review_decision"] == "rejected"


def test_build_lab_optimization_schema_multi_ma_contract():
    schema = lab_routes._build_lab_optimization_schema(
        {
            "indicators": [
                {"type": "ema", "alias": "short", "params": {"length": 9}},
                {"type": "sma", "alias": "medium", "params": {"length": 21}},
                {"type": "sma", "alias": "long", "params": {"length": 50}},
            ],
            "entry_logic": "ema_short > sma_medium",
            "exit_logic": "ema_short < sma_medium",
            "stop_loss": 0.03,
        }
    )
    params = schema["parameters"]
    assert params["ema_short"] == {"default": 9, "min": 3, "max": 20, "step": 1}
    assert params["sma_medium"] == {"default": 21, "min": 10, "max": 40, "step": 1}
    assert params["sma_long"] == {"default": 50, "min": 20, "max": 100, "step": 1}
    assert params["stop_loss"] == {"default": 0.0, "min": 0.005, "max": 0.13, "step": 0.002}
    assert schema["correlated_groups"] == [["ema_short", "sma_medium", "sma_long", "stop_loss"]]


def test_apply_best_parameters_only_updates_allowed_params_and_preserves_logic():
    combo = _FakeCombo()
    combo.create_template(
        "tpl",
        {
            "indicators": [
                {"type": "ema", "alias": "short", "params": {"length": 9}},
                {"type": "sma", "alias": "long", "params": {"length": 50}},
            ],
            "entry_logic": "ema_short > sma_long",
            "exit_logic": "ema_short < sma_long",
            "stop_loss": 0.03,
        },
    )
    schema = {
        "parameters": {
            "ema_short": {"default": 9, "min": 3, "max": 20, "step": 1},
            "sma_long": {"default": 50, "min": 20, "max": 100, "step": 1},
            "stop_loss": {"default": 0.03, "min": 0.005, "max": 0.13, "step": 0.002},
        },
        "correlated_groups": [["ema_short", "sma_long", "stop_loss"]],
    }
    combo.update_template("tpl", optimization_schema=schema)

    applied = lab_routes._apply_best_parameters_to_template(
        combo=combo,
        template_name="tpl",
        best_parameters={"ema_short": 12, "sma_long": 80, "stop_loss": 0.015, "direction": "short"},
        allowed_parameters=schema["parameters"],
    )
    meta = combo.get_template_metadata("tpl")

    assert applied == {"ema_short": 12, "sma_long": 80, "stop_loss": 0.015}
    assert meta["entry_logic"] == "ema_short > sma_long"
    assert meta["exit_logic"] == "ema_short < sma_long"
    assert meta["indicators"][0]["params"]["length"] == 12
    assert meta["indicators"][1]["params"]["length"] == 80
    assert meta["stop_loss"] == 0.015


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


def test_build_fallback_logic_uses_shortest_and_longest_ema():
    entry, exit_logic = lab_routes._build_fallback_logic(
        [
            {"type": "ema", "alias": "ema200", "params": {"length": 200}},
            {"type": "ema", "alias": "ema20", "params": {"length": 20}},
            {"type": "ema", "alias": "ema50", "params": {"length": 50}},
        ]
    )

    assert entry.startswith("ema20 > ema200")
    assert exit_logic.startswith("ema20 < ema200")


def test_logic_preflight_uses_length_based_sample_window():
    class _SampleSpy:
        def __init__(self):
            self.tail_n = None

        def tail(self, n):
            self.tail_n = n
            return self

        def copy(self):
            return self

    class _FakeStrategy:
        entry_logic = "close > ema20"
        exit_logic = "close < ema20"

        def calculate_indicators(self, sample):
            return sample

        def _evaluate_logic_vectorized(self, sample, logic):
            return None

    class _FakePreflightCombo:
        def create_strategy(self, template_name):
            return _FakeStrategy()

        def get_template_metadata(self, template_name):
            return {"indicators": [{"type": "ema", "params": {"length": 400}}]}

    sample = _SampleSpy()
    ok, errors = lab_routes._logic_preflight(combo=_FakePreflightCombo(), template_name="tpl", df_sample=sample)
    assert ok is True
    assert errors == []
    assert sample.tail_n == 1200


def test_run_lab_autonomous_emits_logic_preflight_and_correction_traces(monkeypatch):
    import app.services.combo_optimizer as combo_optimizer
    import app.services.combo_service as combo_service
    import app.services.job_manager as job_manager
    import app.services.lab_graph as lab_graph
    import src.data.incremental_loader as incremental_loader

    traces = []
    run_state = {
        "run_id": "run_logic_trace",
        "status": "running",
        "step": "execution",
        "phase": "execution",
        "input": {
            "symbol": "BTC/USDT",
            "timeframe": "1h",
            "objective": "teste",
            "thinking": "low",
            "max_iterations": 1,
            "constraints": {},
        },
        "budget": {"turns_used": 0, "turns_max": 20, "tokens_total": 0, "tokens_max": 100000},
        "outputs": {"coordinator_summary": None, "dev_summary": None, "validator_verdict": None, "trader_verdict": None},
        "upstream_contract": {"approved": True, "inputs": {"symbol": "BTC/USDT", "timeframe": "1h"}},
    }

    monkeypatch.setattr(lab_routes, "_append_trace", lambda run_id, event: traces.append(event))
    monkeypatch.setattr(lab_routes, "_now_ms", lambda: 1)
    monkeypatch.setattr(lab_routes, "_load_run_json", lambda run_id: copy.deepcopy(run_state))

    def _fake_update_run(run_id, patch):
        run_state.update(copy.deepcopy(patch))

    monkeypatch.setattr(lab_routes, "_update_run_json", _fake_update_run)
    monkeypatch.setattr(lab_routes, "_cp8_save_candidate_template", lambda run_id, run, outputs: {**outputs, "candidate_template_name": "seed_tpl"})
    monkeypatch.setattr(lab_routes, "_cp5_autosave_if_approved", lambda run_id, run, outputs: outputs)
    monkeypatch.setattr(lab_routes, "_needs_dev_adjustment", lambda run: (False, {"preflight": {"ok": True}}))
    monkeypatch.setattr(lab_routes, "_metrics_preflight", lambda run: {"ok": True, "errors": []})
    monkeypatch.setattr(lab_routes, "_cp10_selection_gate", lambda run: {"approved": False})
    monkeypatch.setattr(lab_routes, "_gate_decision", lambda outputs, selection, preflight: {"verdict": "rejected"})
    monkeypatch.setattr(lab_routes, "_persona_call_sync", lambda **kwargs: {"text": "{\"verdict\":\"rejected\"}", "tokens": 1})

    preflight_calls = {"n": 0}

    def _fake_logic_preflight(*, combo, template_name, df_sample):
        preflight_calls["n"] += 1
        if preflight_calls["n"] == 1:
            return False, ["invalid_logic"]
        return True, []

    monkeypatch.setattr(lab_routes, "_logic_preflight", _fake_logic_preflight)
    monkeypatch.setattr(lab_routes, "_apply_logic_correction", lambda **kwargs: (True, ["fallback_logic_applied"]))

    class _FakeComboService:
        def __init__(self):
            base = {
                "indicators": [
                    {"type": "ema", "alias": "ema20", "params": {"length": 20}},
                    {"type": "ema", "alias": "ema200", "params": {"length": 200}},
                ],
                "entry_logic": "ema20 > ema200",
                "exit_logic": "ema20 < ema200",
                "stop_loss": 0.03,
            }
            self.templates = {"seed_tpl": copy.deepcopy(base)}

        def get_template_metadata(self, name):
            return copy.deepcopy(self.templates.get(name) or self.templates["seed_tpl"])

        def update_template(self, template_name, description=None, optimization_schema=None, template_data=None):
            merged = self.get_template_metadata(template_name)
            if template_data:
                merged.update(template_data)
            self.templates[template_name] = merged
            return True

    class _FakeJobManager:
        def __init__(self):
            self.states = {}
            self._seq = 0

        def create_job(self, payload):
            self._seq += 1
            job_id = f"job-{self._seq}"
            self.states[job_id] = {"payload": payload}
            return job_id

        def load_state(self, job_id):
            return copy.deepcopy(self.states.get(job_id, {}))

        def save_state(self, job_id, state):
            self.states[job_id] = copy.deepcopy(state)

    class _FakeLoader:
        def fetch_data(self, symbol, timeframe, since_str, until_str):
            idx = pd.date_range("2024-01-01", periods=1200, freq="h")
            return pd.DataFrame(
                {
                    "open": [100.0] * len(idx),
                    "high": [101.0] * len(idx),
                    "low": [99.0] * len(idx),
                    "close": [100.0] * len(idx),
                    "volume": [1000.0] * len(idx),
                },
                index=idx,
            )

    class _FakeGraph:
        def invoke(self, state):
            outputs = dict(state.get("outputs") or {})
            outputs["coordinator_summary"] = "{\"needs_intervention\": false}"
            outputs["dev_summary"] = json.dumps(
                {
                    "template_data": {"entry_logic": "ema20 > ema200", "exit_logic": "ema20 < ema200"},
                    "backtest_job_id": "job-1",
                    "backtest_summary": {
                        "all": {"total_trades": 12},
                        "in_sample": {"total_trades": 8},
                        "holdout": {"total_trades": 4},
                    },
                },
                ensure_ascii=False,
            )
            return {**state, "outputs": outputs, "status": "done", "phase": "done"}

    monkeypatch.setattr(job_manager, "JobManager", _FakeJobManager)
    monkeypatch.setattr(combo_service, "ComboService", _FakeComboService)
    monkeypatch.setattr(incremental_loader, "IncrementalLoader", _FakeLoader)
    monkeypatch.setattr(combo_optimizer, "_run_backtest_logic", lambda **kwargs: ({"total_trades": 12, "sharpe_ratio": 1.1, "max_drawdown": 0.1}, {"direction": "long"}))
    class _FakeComboOptimizer:
        def run_optimization(self, **kwargs):
            return {
                "best_parameters": {"ema_ema20": 18, "ema_ema200": 180, "stop_loss": 0.02, "direction": "long"},
                "best_metrics": {"sharpe_ratio": 1.4, "total_trades": 18},
                "stages": [{"stage_num": 1, "stage_name": "Grid Search"}],
            }

    monkeypatch.setattr(combo_optimizer, "ComboOptimizer", _FakeComboOptimizer)
    monkeypatch.setattr(lab_graph, "build_trader_dev_graph", lambda: _FakeGraph())

    lab_routes._run_lab_autonomous_sync(
        "run_logic_trace",
        {"symbol": "BTC/USDT", "timeframe": "1h", "objective": "teste", "base_template": "seed_tpl", "direction": "long", "deep_backtest": False},
    )

    trace_types = [evt.get("type") for evt in traces]
    assert "logic_preflight_failed" in trace_types
    assert "logic_correction_applied" in trace_types
    assert "combo_optimization_started" in trace_types
    assert "combo_optimization_applied" in trace_types
    assert run_state["backtest"]["combo_optimization"]["status"] == "completed"
    assert run_state["backtest"]["combo_optimization"]["best_parameters"]["stop_loss"] == 0.02


def test_run_lab_autonomous_persists_combo_optimization_failure(monkeypatch):
    import app.services.combo_optimizer as combo_optimizer
    import app.services.combo_service as combo_service
    import app.services.job_manager as job_manager
    import app.services.lab_graph as lab_graph
    import src.data.incremental_loader as incremental_loader

    traces = []
    run_state = {
        "run_id": "run_combo_fail",
        "status": "running",
        "step": "execution",
        "phase": "execution",
        "input": {
            "symbol": "BTC/USDT",
            "timeframe": "1h",
            "objective": "teste",
            "thinking": "low",
            "max_iterations": 1,
            "constraints": {},
        },
        "budget": {"turns_used": 0, "turns_max": 20, "tokens_total": 0, "tokens_max": 100000},
        "outputs": {"coordinator_summary": None, "dev_summary": None, "validator_verdict": None, "trader_verdict": None},
        "upstream_contract": {"approved": True, "inputs": {"symbol": "BTC/USDT", "timeframe": "1h"}},
    }

    monkeypatch.setattr(lab_routes, "_append_trace", lambda run_id, event: traces.append(event))
    monkeypatch.setattr(lab_routes, "_now_ms", lambda: 1)
    monkeypatch.setattr(lab_routes, "_load_run_json", lambda run_id: copy.deepcopy(run_state))

    def _fake_update_run(run_id, patch):
        run_state.update(copy.deepcopy(patch))

    monkeypatch.setattr(lab_routes, "_update_run_json", _fake_update_run)
    monkeypatch.setattr(lab_routes, "_cp8_save_candidate_template", lambda run_id, run, outputs: {**outputs, "candidate_template_name": "seed_tpl"})
    monkeypatch.setattr(lab_routes, "_cp5_autosave_if_approved", lambda run_id, run, outputs: outputs)
    monkeypatch.setattr(lab_routes, "_needs_dev_adjustment", lambda run: (False, {"preflight": {"ok": True}}))
    monkeypatch.setattr(lab_routes, "_metrics_preflight", lambda run: {"ok": True, "errors": []})
    monkeypatch.setattr(lab_routes, "_cp10_selection_gate", lambda run: {"approved": False})
    monkeypatch.setattr(lab_routes, "_gate_decision", lambda outputs, selection, preflight: {"verdict": "rejected"})
    monkeypatch.setattr(lab_routes, "_persona_call_sync", lambda **kwargs: {"text": "{\"verdict\":\"rejected\"}", "tokens": 1})
    monkeypatch.setattr(lab_routes, "_logic_preflight", lambda **kwargs: (True, []))

    class _FakeComboService:
        def __init__(self):
            base = {
                "indicators": [
                    {"type": "ema", "alias": "ema20", "params": {"length": 20}},
                    {"type": "ema", "alias": "ema200", "params": {"length": 200}},
                ],
                "entry_logic": "ema20 > ema200",
                "exit_logic": "ema20 < ema200",
                "stop_loss": 0.03,
            }
            self.templates = {"seed_tpl": copy.deepcopy(base)}

        def get_template_metadata(self, name):
            return copy.deepcopy(self.templates.get(name) or self.templates["seed_tpl"])

        def update_template(self, template_name, description=None, optimization_schema=None, template_data=None):
            merged = self.get_template_metadata(template_name)
            if template_data:
                merged.update(template_data)
            if optimization_schema is not None:
                merged["optimization_schema"] = optimization_schema
            self.templates[template_name] = merged
            return True

    class _FakeJobManager:
        def __init__(self):
            self.states = {}
            self._seq = 0

        def create_job(self, payload):
            self._seq += 1
            job_id = f"job-{self._seq}"
            self.states[job_id] = {"payload": payload}
            return job_id

        def load_state(self, job_id):
            return copy.deepcopy(self.states.get(job_id, {}))

        def save_state(self, job_id, state):
            self.states[job_id] = copy.deepcopy(state)

    class _FakeLoader:
        def fetch_data(self, symbol, timeframe, since_str, until_str):
            idx = pd.date_range("2024-01-01", periods=1200, freq="h")
            return pd.DataFrame(
                {
                    "open": [100.0] * len(idx),
                    "high": [101.0] * len(idx),
                    "low": [99.0] * len(idx),
                    "close": [100.0] * len(idx),
                    "volume": [1000.0] * len(idx),
                },
                index=idx,
            )

    class _FakeGraph:
        def invoke(self, state):
            outputs = dict(state.get("outputs") or {})
            outputs["coordinator_summary"] = "{\"needs_intervention\": false}"
            outputs["dev_summary"] = json.dumps(
                {
                    "template_data": {"entry_logic": "ema20 > ema200", "exit_logic": "ema20 < ema200"},
                    "backtest_job_id": "job-1",
                    "backtest_summary": {
                        "all": {"total_trades": 12},
                        "in_sample": {"total_trades": 8},
                        "holdout": {"total_trades": 4},
                    },
                },
                ensure_ascii=False,
            )
            return {**state, "outputs": outputs, "status": "done", "phase": "done"}

    class _BrokenComboOptimizer:
        def run_optimization(self, **kwargs):
            raise RuntimeError("optimizer down")

    monkeypatch.setattr(job_manager, "JobManager", _FakeJobManager)
    monkeypatch.setattr(combo_service, "ComboService", _FakeComboService)
    monkeypatch.setattr(incremental_loader, "IncrementalLoader", _FakeLoader)
    monkeypatch.setattr(combo_optimizer, "_run_backtest_logic", lambda **kwargs: ({"total_trades": 12, "sharpe_ratio": 1.1, "max_drawdown": 0.1}, {"direction": "long"}))
    monkeypatch.setattr(combo_optimizer, "ComboOptimizer", _BrokenComboOptimizer)
    monkeypatch.setattr(lab_graph, "build_trader_dev_graph", lambda: _FakeGraph())

    lab_routes._run_lab_autonomous_sync(
        "run_combo_fail",
        {"symbol": "BTC/USDT", "timeframe": "1h", "objective": "teste", "base_template": "seed_tpl", "direction": "long", "deep_backtest": False},
    )

    assert run_state["status"] == "needs_adjustment"
    assert run_state["step"] == "combo_optimization_failed"
    assert run_state["backtest"]["combo_optimization"]["status"] == "failed"
    assert "optimizer down" in run_state["backtest"]["combo_optimization"]["error"]
    trace_types = [evt.get("type") for evt in traces]
    assert "combo_optimization_started" in trace_types
    assert "combo_optimization_failed" in trace_types


def test_implementation_rejects_dev_summary_when_backtest_job_id_is_empty():
    import app.services.lab_graph as lab_graph

    traces = []

    def _append_trace(run_id, event):
        traces.append(event)

    def _persona_call(run_id, session_key, persona, system_prompt, message, thinking):
        if persona == "coordinator":
            return {"text": "{\"needs_intervention\": false}", "tokens": 1}
        if persona == "dev_senior":
            return {
                "text": json.dumps(
                    {
                        "template_data": {"entry_logic": "ema20 > ema200", "exit_logic": "ema20 < ema200"},
                        "backtest_job_id": "",
                        "backtest_summary": {
                            "all": {"total_trades": 10},
                            "in_sample": {"total_trades": 6},
                            "holdout": {"total_trades": 4},
                        },
                    },
                    ensure_ascii=False,
                ),
                "tokens": 1,
            }
        raise AssertionError(f"Unexpected persona: {persona}")

    deps = lab_graph.LabGraphDeps(
        persona_call=_persona_call,
        append_trace=_append_trace,
        now_ms=lambda: 1,
        inc_budget=lambda budget, turns=0, tokens=0: {
            **budget,
            "turns_used": int(budget.get("turns_used", 0)) + int(turns),
            "tokens_total": int(budget.get("tokens_total", 0)) + int(tokens),
        },
        budget_ok=lambda budget: int(budget.get("turns_used", 0)) < int(budget.get("turns_max", 0))
        and int(budget.get("tokens_total", 0)) < int(budget.get("tokens_max", 0)),
    )

    state = {
        "run_id": "run-dev-missing-job",
        "session_key": "lab-run-dev-missing-job",
        "thinking": "low",
        "deps": deps,
        "budget": {"turns_used": 0, "turns_max": 10, "tokens_total": 0, "tokens_max": 1000},
        "outputs": {},
        "context": {
            "backtest_job_id": "job-ctx",
            "backtest_job_status": "COMPLETED",
            "walk_forward": {
                "metrics_all": {"total_trades": 10},
                "metrics_in_sample": {"total_trades": 6},
                "metrics_holdout": {"total_trades": 4},
            },
            "input": {"max_iterations": 3},
        },
    }

    out = lab_graph._implementation_node(state)
    outputs = out.get("outputs") or {}

    assert outputs.get("dev_needs_retry") is True
    assert outputs.get("dev_summary") is None
    assert out.get("status") == "needs_adjustment"
    reasons = [e.get("data", {}).get("reason") for e in traces if e.get("type") == "dev_summary_rejected"]
    assert "missing_job_id" in reasons


def test_implementation_rejects_dev_summary_when_metrics_diverge_from_context():
    import app.services.lab_graph as lab_graph

    traces = []

    def _append_trace(run_id, event):
        traces.append(event)

    def _persona_call(run_id, session_key, persona, system_prompt, message, thinking):
        if persona == "coordinator":
            return {"text": "{\"needs_intervention\": false}", "tokens": 1}
        if persona == "dev_senior":
            return {
                "text": json.dumps(
                    {
                        "template_data": {"entry_logic": "ema20 > ema200", "exit_logic": "ema20 < ema200"},
                        "backtest_job_id": "job-ctx",
                        "backtest_summary": {
                            "all": {"total_trades": 99},
                            "in_sample": {"total_trades": 88},
                            "holdout": {"total_trades": 77},
                        },
                    },
                    ensure_ascii=False,
                ),
                "tokens": 1,
            }
        raise AssertionError(f"Unexpected persona: {persona}")

    deps = lab_graph.LabGraphDeps(
        persona_call=_persona_call,
        append_trace=_append_trace,
        now_ms=lambda: 1,
        inc_budget=lambda budget, turns=0, tokens=0: {
            **budget,
            "turns_used": int(budget.get("turns_used", 0)) + int(turns),
            "tokens_total": int(budget.get("tokens_total", 0)) + int(tokens),
        },
        budget_ok=lambda budget: int(budget.get("turns_used", 0)) < int(budget.get("turns_max", 0))
        and int(budget.get("tokens_total", 0)) < int(budget.get("tokens_max", 0)),
    )

    state = {
        "run_id": "run-dev-metrics-mismatch",
        "session_key": "lab-run-dev-metrics-mismatch",
        "thinking": "low",
        "deps": deps,
        "budget": {"turns_used": 0, "turns_max": 10, "tokens_total": 0, "tokens_max": 1000},
        "outputs": {},
        "context": {
            "backtest_job_id": "job-ctx",
            "backtest_job_status": "COMPLETED",
            "walk_forward": {
                "metrics_all": {"total_trades": 10},
                "metrics_in_sample": {"total_trades": 6},
                "metrics_holdout": {"total_trades": 4},
            },
            "input": {"max_iterations": 3},
        },
    }

    out = lab_graph._implementation_node(state)
    outputs = out.get("outputs") or {}

    assert outputs.get("dev_needs_retry") is True
    assert outputs.get("dev_summary") is None
    assert out.get("status") == "needs_adjustment"
    reasons = [e.get("data", {}).get("reason") for e in traces if e.get("type") == "dev_summary_rejected"]
    assert "metrics_mismatch" in reasons


def test_trader_retry_started_when_rejected_with_required_fixes():
    import app.services.lab_graph as lab_graph

    traces = []

    def _append_trace(run_id, event):
        traces.append(event)

    def _persona_call(run_id, session_key, persona, system_prompt, message, thinking):
        assert persona == "trader"
        return {
            "text": json.dumps(
                {
                    "verdict": "rejected",
                    "required_fixes": ["corrigir stop_loss", "reduzir overfitting"],
                    "reasons": ["drawdown alto"],
                },
                ensure_ascii=False,
            ),
            "tokens": 7,
        }

    deps = lab_graph.LabGraphDeps(
        persona_call=_persona_call,
        append_trace=_append_trace,
        now_ms=lambda: 1,
        inc_budget=lambda budget, turns=0, tokens=0: {
            **budget,
            "turns_used": int(budget.get("turns_used", 0)) + int(turns),
            "tokens_total": int(budget.get("tokens_total", 0)) + int(tokens),
        },
        budget_ok=lambda budget: int(budget.get("turns_used", 0)) < int(budget.get("turns_max", 0))
        and int(budget.get("tokens_total", 0)) < int(budget.get("tokens_max", 0)),
    )

    out = lab_graph._trader_validation_node(
        {
            "run_id": "run-trader-retry-started",
            "session_key": "lab-run-trader-retry-started",
            "thinking": "low",
            "deps": deps,
            "budget": {"turns_used": 0, "turns_max": 10, "tokens_total": 0, "tokens_max": 1000},
            "outputs": {},
            "context": {"input": {"max_retries": 2, "max_iterations": 5}},
            "upstream_contract": {},
        }
    )

    outputs = out.get("outputs") or {}
    assert out.get("status") == "needs_adjustment"
    assert outputs.get("dev_needs_retry") is True
    assert outputs.get("trader_retry_count") == 1

    started = [e for e in traces if e.get("type") == "trader_retry_started"]
    assert started
    assert started[-1].get("data", {}).get("attempt") == 1
    assert started[-1].get("data", {}).get("limit") == 2
    assert started[-1].get("data", {}).get("reasons") == ["corrigir stop_loss", "reduzir overfitting"]


def test_trader_retry_limit_trace_when_retries_exhausted():
    import app.services.lab_graph as lab_graph

    traces = []

    def _append_trace(run_id, event):
        traces.append(event)

    def _persona_call(run_id, session_key, persona, system_prompt, message, thinking):
        assert persona == "trader"
        return {
            "text": json.dumps(
                {
                    "verdict": "needs_adjustment",
                    "required_fixes": ["melhorar robustez no holdout"],
                    "reasons": ["consistência baixa"],
                },
                ensure_ascii=False,
            ),
            "tokens": 5,
        }

    deps = lab_graph.LabGraphDeps(
        persona_call=_persona_call,
        append_trace=_append_trace,
        now_ms=lambda: 1,
        inc_budget=lambda budget, turns=0, tokens=0: {
            **budget,
            "turns_used": int(budget.get("turns_used", 0)) + int(turns),
            "tokens_total": int(budget.get("tokens_total", 0)) + int(tokens),
        },
        budget_ok=lambda budget: int(budget.get("turns_used", 0)) < int(budget.get("turns_max", 0))
        and int(budget.get("tokens_total", 0)) < int(budget.get("tokens_max", 0)),
    )

    out = lab_graph._trader_validation_node(
        {
            "run_id": "run-trader-retry-limit",
            "session_key": "lab-run-trader-retry-limit",
            "thinking": "low",
            "deps": deps,
            "budget": {"turns_used": 0, "turns_max": 10, "tokens_total": 0, "tokens_max": 1000},
            "outputs": {"trader_retry_count": 2},
            "context": {"input": {"max_retries": 2, "max_iterations": 5}},
            "upstream_contract": {},
            "trader_retry_count": 2,
        }
    )

    outputs = out.get("outputs") or {}
    assert out.get("status") == "needs_adjustment"
    assert outputs.get("trader_retry_count") == 2
    assert outputs.get("dev_needs_retry") is not True

    limit_events = [e for e in traces if e.get("type") == "trader_retry_limit"]
    assert limit_events
    assert limit_events[-1].get("data", {}).get("attempt") == 2
    assert limit_events[-1].get("data", {}).get("limit") == 2
    assert limit_events[-1].get("data", {}).get("reasons") == ["melhorar robustez no holdout"]
