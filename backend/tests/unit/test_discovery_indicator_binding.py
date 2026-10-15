"""Exact strategy coverage and producer identity, including all 121 grid pairs."""

import copy
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from app.services.combo_service import ComboService
from app.services import combo_optimizer as opt
from app.strategies.combos.indicator_binding import capture_binding, IndicatorReferenceError
from app.strategies.combos import ComboStrategy
from tests.oracles.card_945_legacy import LegacyComboStrategy, extract_trades_from_signals

ROOT = Path(__file__).parents[1] / "fixtures/discovery_memory"
FROZEN = json.loads((ROOT / "original_template.json").read_text())
spec = importlib.util.spec_from_file_location("semantic_oracle", ROOT / "semantic_oracle.py")
oracle = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oracle)


def strategy(parameters, metadata=None):
    metadata = copy.deepcopy(metadata or {"name": FROZEN["name"], **FROZEN["template_data"]})
    service = object.__new__(ComboService)
    service.get_template_metadata = lambda _: metadata
    return service.create_strategy(metadata["name"], parameters)


@pytest.mark.parametrize("rsi", range(10, 21))
@pytest.mark.parametrize("adx", range(10, 21))
def test_every_grid_pair_exact_indicators_masks_trades_and_holdout(rsi, adx):
    parameters = {"rsi_length": rsi, "adx_length": adx, "rsi_oversold": 45, "adx_threshold": 18}
    original = oracle.frame_fixture()
    for frame in (original.iloc[:560], original.iloc[310:]):
        expected = oracle.masks(frame, parameters)
        actual = strategy(parameters)
        calculated = actual.calculate_indicators(frame)
        np.testing.assert_array_equal(calculated[f"RSI_{rsi}"], expected["rsi"])
        np.testing.assert_array_equal(calculated[f"ADX_{adx}"], expected["adx"])
        np.testing.assert_array_equal(
            actual._evaluate_logic_vectorized(calculated, actual.entry_logic), expected["entry"]
        )
        np.testing.assert_array_equal(
            actual._evaluate_logic_vectorized(calculated, actual.exit_logic), expected["exit"]
        )
        historical = LegacyComboStrategy(
            actual.indicators, "entry", "exit", stop_loss=actual.stop_loss
        )
        historical._evaluate_logic_vectorized = lambda _, logic: expected[logic]
        wanted = historical.generate_signals(frame.copy())
        signals = actual.generate_signals(frame.copy())
        np.testing.assert_array_equal(signals.signal, wanted.signal)
        assert opt.extract_trades_from_signals(
            signals, actual.stop_loss
        ) == extract_trades_from_signals(wanted, actual.stop_loss)


def test_valid_14_14_matches_frozen_historical_path():
    frame = oracle.frame_fixture()
    actual = strategy({})
    legacy = LegacyComboStrategy(**FROZEN["template_data"])
    expected = legacy.generate_signals(frame.copy())
    observed = actual.generate_signals(frame.copy())
    pd.testing.assert_frame_equal(observed, expected, check_exact=True)
    assert opt.extract_trades_from_signals(
        observed, actual.stop_loss
    ) == extract_trades_from_signals(expected, legacy.stop_loss)


@pytest.mark.parametrize(
    "mutation", ["duplicate", "alias", "original_length", "unknown", "collision"]
)
def test_invalid_identity_or_reference_never_yields_false_success(mutation):
    metadata = {"name": FROZEN["name"], **copy.deepcopy(FROZEN["template_data"])}
    if mutation == "duplicate":
        metadata["indicators"].append(copy.deepcopy(metadata["indicators"][1]))
    if mutation == "alias":
        metadata["indicators"][1]["alias"] = "relative"
    if mutation == "original_length":
        metadata["indicators"][1]["params"]["length"] = 20
    if mutation == "unknown":
        metadata["entry_logic"] += " & (RSI_140 > 0)"
    if mutation == "collision":
        metadata["indicators"][0]["alias"] = "RSI_14"
    with pytest.raises(IndicatorReferenceError):
        strategy({"rsi_length": 10}, metadata).generate_signals(oracle.frame_fixture())


def test_other_templates_aliases_dotted_references_and_literal_semantics():
    assert capture_binding("another", FROZEN["template_data"]["indicators"]) is None
    metadata = {
        "name": "another",
        "indicators": [{"type": "rsi", "alias": "osc", "params": {"length": 10}}],
        "entry_logic": "osc < 45",
        "exit_logic": "osc > 65",
    }
    current = strategy({}, metadata)
    frame = current.calculate_indicators(oracle.frame_fixture())
    np.testing.assert_array_equal(
        current._evaluate_logic_vectorized(frame, "osc < 45"), frame.osc < 45
    )
    with pytest.raises(RuntimeError):
        current._evaluate_logic_vectorized(frame, "RSI_14 < 45")
    assert current.indicator_binding is None


def test_optimizer_cache_A_B_A_and_policy_identity():
    template = {"name": FROZEN["name"], **FROZEN["template_data"]}
    opt.BUDGET.clear()

    frame = oracle.frame_fixture()

    def run(rsi, adx):
        return opt._run_backtest_logic(
            template,
            {"rsi_length": rsi, "adx_length": adx, "timeframe": "15m"},
            frame,
            False,
            "BTC/USDT",
            None,
            None,
        )

    first = run(10, 20)
    assert "error" not in first[0]
    assert "error" not in run(20, 10)[0]
    assert run(10, 20) == first
    opt.BUDGET.clear()
    assert run(10, 20) == first
    opt.BUDGET.clear()


def test_missing_effective_series_collision_and_unrelated_literals_are_explicit():
    current = strategy({"rsi_length": 10, "adx_length": 20})
    frame = current.calculate_indicators(oracle.frame_fixture())
    np.testing.assert_array_equal(
        current._evaluate_logic_vectorized(frame, "RSI_10 < 45"), frame.RSI_10 < 45
    )
    with pytest.raises(IndicatorReferenceError):
        current._evaluate_logic_vectorized(frame.drop(columns=["ADX_20"]), current.entry_logic)
    with pytest.raises(IndicatorReferenceError):
        current._evaluate_logic_vectorized(frame.assign(ADX_14=1), current.entry_logic)
    with pytest.raises(IndicatorReferenceError):
        current._evaluate_logic_vectorized(frame, "ADX_99 > 0")
    with pytest.raises(IndicatorReferenceError):
        capture_binding(
            FROZEN["name"],
            FROZEN["template_data"]["indicators"],
            [{"name": "RSI_14", "source": "close", "transform": "lag"}],
        )


def _three_worker_batch(batch):
    import time

    time.sleep(1)  # Occupy each real spawn worker while the other two start.
    return opt._worker_run_batch(batch)


def test_three_isolated_spawn_workers_preserve_complete_oracle_ranking(tmp_path, monkeypatch):
    from app.services.discovery_resources import cgroup_path, GiB

    group = cgroup_path()
    if (group / "memory.max").read_text().strip() != str(2 * GiB):
        pytest.skip("Three-worker load requires the isolated 2GiB cgroup")
    assert (group / "memory.oom.group").read_text().strip() == "1"
    import multiprocessing
    from concurrent.futures import ProcessPoolExecutor
    from dataclasses import replace
    from app.services.discovery_resources import ResourceProfile
    from app.services import discovery_stream

    monkeypatch.delenv("DISCOVERY_RESOURCE_PROFILE", raising=False)
    monkeypatch.delenv("DISCOVERY_SUPERVISOR_DIR", raising=False)
    monkeypatch.setenv("DISCOVERY_SPOOL_DIR", str(tmp_path))
    original_profile = ResourceProfile.optimizer
    monkeypatch.setattr(
        ResourceProfile,
        "optimizer",
        lambda workers=None: replace(original_profile(workers), batch_size=2),
    )
    events = []
    monkeypatch.setattr(discovery_stream, "PROGRESS_CALLBACK", events.append)
    monkeypatch.setattr(opt, "_worker_run_batch", _three_worker_batch)
    metadata = {"name": FROZEN["name"], **FROZEN["template_data"]}
    frame = oracle.frame_fixture()
    optimizer = object.__new__(opt.ComboOptimizer)
    parameters = {"direction": "long", "timeframe": "15m", "rsi_oversold": 45, "adx_threshold": 18}
    stage = {
        "parameter": ["rsi_length", "adx_length"],
        "values": [[10, 14, 20], [10, 14, 20]],
        "grid_mode": True,
    }
    with ProcessPoolExecutor(
        3, mp_context=multiprocessing.get_context("spawn"), initializer=opt._init_worker_logging
    ) as pool:
        actual = optimizer._execute_opt_stages(
            [stage],
            parameters,
            1,
            3,
            FROZEN["name"],
            "BTC/USDT",
            "15m",
            True,
            None,
            None,
            False,
            metadata,
            frame,
            return_top_n=5,
            executor=pool,
        )
    workers = {
        event["worker_telemetry"]["pid"] for event in events if event.get("worker_telemetry")
    }
    assert len(workers) == 3
    prepared = opt._optimizer_context(frame.copy(), metadata)
    expected = []
    for trial, (rsi, adx) in enumerate((rsi, adx) for rsi in (10, 14, 20) for adx in (10, 14, 20)):
        effective = {**parameters, "rsi_length": rsi, "adx_length": adx}
        metrics, _, _ = oracle.evaluate(prepared, effective)
        expected.append({"trial_index": trial, "params": effective, "metrics": metrics})
    sharpes = [row["metrics"]["sharpe_ratio"] for row in expected]
    returns = [row["metrics"]["total_return"] for row in expected]
    low_s, high_s = min(sharpes), max(sharpes)
    low_r, high_r = min(returns), max(returns)
    for row in expected:
        s, r = row["metrics"]["sharpe_ratio"], row["metrics"]["total_return"]
        ns = (s - low_s) / (high_s - low_s) if high_s - low_s > 0 else 0
        nr = (r - low_r) / (high_r - low_r) if high_r - low_r > 0 else 0
        row["score"] = (0.7 * ns) + (0.3 * nr)
    expected.sort(key=lambda row: (-row["score"], row["trial_index"]))
    assert actual == expected
