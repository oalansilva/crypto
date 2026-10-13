"""Exact #1091 cache/compilation invariants; no temporal acceptance in CI."""
from __future__ import annotations

import importlib.util
import json
import os
import pickle
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from app.services import combo_acceleration as acceleration, combo_cache as cache
from app.services import combo_optimizer as co, deep_backtest as deep
from oracles._build_card_945 import load_ohlcv, load_templates, metadata_from_export


@pytest.fixture(autouse=True)
def isolated(monkeypatch):
    monkeypatch.delenv("COMBO_OPTIMIZER_LEGACY", raising=False)
    monkeypatch.delenv("COMBO_OPTIMIZER_1091_DISABLED", raising=False)
    cache.BUDGET.clear()
    yield
    cache.BUDGET.clear()


def candles():
    return load_ohlcv("1INCH/USDT", "1d").iloc[:80].copy(deep=True)


def test_snapshot_private_complete_identity_and_transport():
    original = candles()
    a = cache.Snapshot(original, generation="run", source=("x", "1d"), role="train")
    before = a.copy_frame()
    original.iloc[10, original.columns.get_loc("close")] += 1
    pd.testing.assert_frame_equal(before, a.copy_frame(), check_exact=True)
    b = cache.Snapshot(original, generation="run", source=("x", "1d"), role="train")
    assert a.identity != b.identity
    original.attrs["snapshot"] = a.identity
    changed = original.copy()
    idx = changed.index.to_numpy(copy=True)
    idx[10] = idx[10] + pd.Timedelta(hours=1)
    changed.index = pd.DatetimeIndex(idx)
    assert cache.frame_identity(original) != cache.frame_identity(changed)
    assert cache.Snapshot(original, generation="run", role="holdout").identity != b.identity
    assert cache.Snapshot(original, generation="run", source=("y", "1d")).identity != b.identity
    category_a = original.assign(regime=pd.Categorical(["trend"] * len(original), categories=["trend", "flat"]))
    category_b = original.assign(regime=pd.Categorical(["trend"] * len(original), categories=["flat", "trend"]))
    assert cache.frame_identity(category_a) != cache.frame_identity(category_b)
    restored = pickle.loads(pickle.dumps(a))
    assert restored.identity == a.identity
    pd.testing.assert_frame_equal(cache.resolve(restored), before, check_exact=True)
    for block in restored._frame._mgr.blocks:
        if isinstance(block.values, np.ndarray):
            assert not block.values.flags.writeable
    with pytest.raises(ValueError):
        restored._frame["close"].to_numpy(copy=False)[10] = 99
    copy_frame = restored.copy_frame()
    copy_frame.iloc[10, copy_frame.columns.get_loc("close")] = 99
    pd.testing.assert_frame_equal(restored.copy_frame(), before, check_exact=True)


def test_iso_internal_timestamp_timezone_and_array_ownership():
    snapshot = cache.Snapshot(candles())
    a = snapshot._frame.index
    shallow = snapshot.copy_frame().index
    assert cache.index_identity(a) == cache.index_identity(shallow)
    assert cache.index_identity(a) != cache.index_identity(shallow.rename("changed-name"))
    raw = a.to_numpy(copy=True)
    raw[10] = raw[10] + pd.Timedelta(hours=1)
    b = pd.DatetimeIndex(raw)
    first = deep._iso_array(a)
    second = deep._iso_array(b)
    assert first[10] != second[10]
    assert deep._iso_array(a) is first
    with pytest.raises(ValueError):
        first[10] = "corrupt"
    assert cache.index_identity(a) != cache.index_identity(a.tz_convert("America/Sao_Paulo"))


def test_lru_limits_strong_refs_oversized_and_generation():
    budget = cache.Budget(max_bytes=2048, max_entries=3, max_snapshots=1)
    budget.begin("A")
    budget.put("x", "a", np.ones(20))
    budget.put("x", "b", np.ones(20))
    budget.put("x", "c", np.ones(20))
    assert budget.get("x", "a") is not None
    budget.put("x", "d", np.ones(20))
    assert budget.get("x", "b") is None and budget.evictions > 0
    budget.put("x", "large", np.ones(10000))
    assert budget.get("x", "large") is None
    large_base = np.ones(10000)
    budget.put("x", "small_view", large_base[:1])
    assert budget.get("x", "small_view") is None
    metadata = pd.DataFrame({"close": [1.]})
    metadata.attrs["large_buffer"] = large_base
    assert cache.retained_bytes(metadata) >= large_base.nbytes
    budget.put("x", "metadata", metadata)
    assert budget.get("x", "metadata") is None
    assert budget.bytes <= 2048 and len(budget.entries) <= 3
    budget.begin("B")
    assert budget.bytes == 0 and len(budget.entries) == 0
    budget.put("snapshots", "a", np.ones(2))
    budget.put("snapshots", "b", np.ones(2))
    assert budget.snapshots == 1 and budget.get("snapshots", "a") is None


def test_lifecycle_exception_and_success_release_references():
    @cache.execution_lifecycle
    def work(fail):
        cache.BUDGET.put("test", "retained", np.ones(10))
        if fail:
            raise ValueError("business error")
        return 3
    assert work(False) == 3 and cache.BUDGET.bytes == 0
    with pytest.raises(ValueError, match="business error"):
        work(True)
    assert cache.BUDGET.bytes == 0


def test_mutated_external_aba_aliases_and_eviction(monkeypatch):
    meta = metadata_from_export(load_templates()["multi_ma_crossover"])
    data = candles()
    def run(df, params):
        return co._run_backtest_logic(meta, params, df, False, "1INCH/USDT", "2023-01-01", "2025-01-01")
    params = {"direction": "long", "stop_loss": .05, "timeframe": "1d"}
    index_writable = data.index.asi8.flags.writeable
    a = run(data, params)
    assert data.index.asi8.flags.writeable == index_writable
    key = co._window_identity(data)
    b = data.copy(deep=True)
    b.attrs["snapshot"] = key
    b.iloc[30, b.columns.get_loc("close")] *= 3
    assert co._window_identity(b) != key
    run(b, params)
    assert run(data, params) == a
    cache.BUDGET.clear()
    assert run(data, params) == a
    alias = meta["indicators"][0]["alias"]
    kind = meta["indicators"][0]["type"]
    assert run(data, dict(params, **{alias: 10})) == run(data, dict(params, **{f"{kind}_{alias}": 10}))
    assert run(data, dict(params, **{f"{alias}_length": 10})) == run(data, dict(params, **{alias: 10}))
    before = set(cache.BUDGET.entries)
    run(data, dict(params, **{alias: 11}))
    assert set(cache.BUDGET.entries) != before
    cached = next(v[0] for k, v in cache.BUDGET.entries.items() if k[0] == "indicators")
    with pytest.raises(ValueError):
        cached["entry"][0] = True
    with pytest.raises(ValueError):
        cached["frame"]["close"].to_numpy(copy=False)[0] = 999


def test_optional_kernel_signature_missing_compiler_cache_denied_and_business_error(monkeypatch, caplog):
    import numba
    arr = np.ones(3, dtype=np.float64)
    kernel = acceleration.OptionalKernel(lambda x: x + 1, (np.dtype("float64"),))
    np.testing.assert_array_equal(kernel(arr[::2]), arr[::2] + 1)
    assert "ineligible numerical signature" in caplog.text
    def denied(*args, **kwargs):
        if kwargs["cache"]:
            raise RuntimeError("no writable cache")
        return lambda function: function
    monkeypatch.setattr(numba, "njit", denied)
    kernel = acceleration.OptionalKernel(lambda x: x + 1, (np.dtype("float64"),))
    np.testing.assert_array_equal(kernel(arr), arr + 1)
    assert kernel.compiled is not None
    def unavailable(*args, **kwargs):
        raise ImportError("compiler unavailable")
    monkeypatch.setattr(numba, "njit", unavailable)
    kernel = acceleration.OptionalKernel(lambda x: x + 1, (np.dtype("float64"),))
    np.testing.assert_array_equal(kernel(arr), arr + 1)
    assert kernel.unavailable and "compiler unavailable" in caplog.text
    def business(x):
        raise ValueError("business failure")
    kernel = acceleration.OptionalKernel(business, (np.dtype("float64"),))
    kernel.compiled = business
    with pytest.raises(ValueError, match="business failure"):
        kernel(arr)
    assert not kernel.unavailable


def test_rollback_precedence_and_no_numba(monkeypatch):
    assert acceleration.enabled()
    monkeypatch.setenv("COMBO_OPTIMIZER_1091_DISABLED", "1")
    assert not acceleration.enabled() and not co._combo_optimizer_legacy()
    monkeypatch.setenv("COMBO_OPTIMIZER_LEGACY", "1")
    assert not acceleration.enabled() and co._combo_optimizer_legacy()
    monkeypatch.delenv("COMBO_OPTIMIZER_1091_DISABLED")
    assert not acceleration.enabled() and co._combo_optimizer_legacy()


def test_rollback_fresh_process_and_unwritable_jit_cache():
    root = Path(__file__).resolve().parents[3]
    script = """
import contextlib, io, json, sys
from pathlib import Path
from app.services import combo_acceleration as acceleration, combo_cache as cache
from app.strategies.combos import ComboStrategy
from app.services.deep_backtest import simulate_execution_with_15m
from oracles._build_card_945 import load_ohlcv, load_templates, metadata_from_export
assert not cache.BUDGET.entries
if sys.argv[1] == 'missing':
    sys.modules['numba'] = None
data = load_ohlcv('1INCH/USDT', '1d')
intraday = load_ohlcv('1INCH/USDT', '15m')
meta = metadata_from_export(load_templates()['multi_ma_crossover'])
strategy = ComboStrategy(indicators=meta['indicators'], entry_logic=meta['entry_logic'],
                         exit_logic=meta['exit_logic'], stop_loss=.05)
with contextlib.redirect_stdout(io.StringIO()):
    signals = strategy.generate_signals(data.copy())
    trades = simulate_execution_with_15m(signals, intraday, .05, 'long', .001)
print(json.dumps({'signals': signals['signal'].tolist(), 'reasons': signals['signal_reason'].tolist(),
                  'trades': trades}, sort_keys=True, default=str, allow_nan=True))
"""
    values = []
    for disabled, legacy, mode in ((True, False, "normal"), (False, False, "normal"),
                (True, True, "normal"), (False, True, "normal"), (False, False, "missing")):
        env = dict(os.environ, PYTHONPATH=f"{root / 'backend'}:{root / 'backend/tests'}:{root}",
                   PYTHONDONTWRITEBYTECODE="1", NUMBA_CACHE_DIR="/proc/card-1091-no-write")
        env.pop("COMBO_OPTIMIZER_LEGACY", None)
        env.pop("COMBO_OPTIMIZER_1091_DISABLED", None)
        if disabled:
            env["COMBO_OPTIMIZER_1091_DISABLED"] = "1"
        if legacy:
            env["COMBO_OPTIMIZER_LEGACY"] = "1"
        result = subprocess.run([sys.executable, "-c", script, mode], cwd=root, env=env,
                                text=True, capture_output=True, check=True)
        values.append(json.loads(result.stdout))
    assert all(value == values[0] for value in values)


def test_exact_randomized_edges():
    path = Path(__file__).resolve().parents[2] / "scripts/discovery_benchmark_1091.py"
    spec = importlib.util.spec_from_file_location("benchmark_1091", path)
    harness = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(harness)
    root = Path(__file__).resolve().parents[3]
    harness.initialize(root, root / "backend/tests/fixtures/card_945")
    assert harness.validate_edges() == 568


def test_deep_end_boundary_int64_overflow_matches_python(monkeypatch):
    maximum = np.iinfo(np.int64).max
    index = pd.DatetimeIndex(np.array([maximum - 10, maximum - 2], dtype="datetime64[ns]"))
    intraday_index = pd.DatetimeIndex(np.array([maximum - 2, maximum], dtype="datetime64[ns]"))
    data = pd.DataFrame(dict(open=[100., 100.], close=[100., 100.], signal=[0, 1]), index=index)
    intra = pd.DataFrame(dict(low=[100., 50.], high=[100., 100.]), index=intraday_index)
    monkeypatch.setenv("COMBO_OPTIMIZER_1091_DISABLED", "1")
    expected = deep.simulate_execution_with_15m(data, intra, .05)
    monkeypatch.delenv("COMBO_OPTIMIZER_1091_DISABLED")
    actual = deep.simulate_execution_with_15m(data, intra, .05)
    assert actual == expected and len(actual) == 1


@pytest.mark.parametrize("timeframe", ["1d", "4h"])
@pytest.mark.parametrize("coverage", ["complete", "empty", "incomplete"])
def test_deep_daily_fallback_contracts(timeframe, coverage, monkeypatch):
    data = candles()
    if timeframe == "4h":
        data.index = pd.date_range(data.index[0], periods=len(data), freq="4h", tz="UTC")
    meta = metadata_from_export(load_templates()["multi_ma_crossover"])
    from app.strategies.combos import ComboStrategy
    strat = ComboStrategy(indicators=meta["indicators"], entry_logic=meta["entry_logic"], exit_logic=meta["exit_logic"], stop_loss=.05)
    intra = load_ohlcv("1INCH/USDT", "15m")
    if coverage == "empty":
        intra = intra.iloc[:0]
    elif coverage == "incomplete":
        intra = intra.iloc[:100]
    def run():
        signals = strat.generate_signals(data.copy())
        return co.extract_trades_with_mode(signals, .05, True, "1INCH/USDT", "2023-01-01", "2025-01-01", intra, return_mode=True, slippage=.001)
    monkeypatch.setenv("COMBO_OPTIMIZER_1091_DISABLED", "1")
    a = run()
    monkeypatch.delenv("COMBO_OPTIMIZER_1091_DISABLED")
    b = run()
    assert a == b
    assert b[1] == ("deep_15m" if coverage == "complete" else "fast_1d")
