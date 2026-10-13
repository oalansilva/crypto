"""Reproducible discovery equivalence and performance harness for card 1091."""

from __future__ import annotations

import argparse
import ast
import contextlib
import copy
import cProfile
import hashlib
import gzip
import importlib.metadata
import inspect
import io
import json
import logging
import os
from pathlib import Path
import platform
import pstats
import resource
import statistics
import subprocess
import sys
import threading
import textwrap
import time

ROOT = Path(__file__).resolve().parents[2]
PROCESS_STARTED = time.perf_counter()
BASELINE = "64c1b97aec75b250ad4f32c0fd20692cf7a5f5b5"
SOURCES = (
    "backend/app/services/combo_optimizer.py",
    "backend/app/services/deep_backtest.py",
    "backend/app/services/combo_cache.py",
    "backend/app/services/combo_acceleration.py",
    "backend/app/strategies/combos/combo_strategy.py",
    "backend/requirements.txt",
    "backend/requirements.lock",
    "backend/config/combo_templates_export.json",
)


def initialize(root, fixtures):
    global np, pd, co, deep, acceleration, cache, ComboStrategy, helpers, FIXTURES, TEMPLATES
    sys.path[:0] = [str(root), str(root / "backend"), str(root / "backend/tests")]
    # Import-only address. All market/metadata access uses the frozen providers below.
    os.environ.setdefault(
        "DATABASE_URL", "postgresql+psycopg2://unused:unused@127.0.0.1:1/crypto_app_test"
    )
    os.environ.setdefault("MARKET_OHLCV_VERIFY_POLICIES", "0")
    import numpy as np
    import pandas as pd
    from app.services import combo_optimizer as co, deep_backtest as deep
    from app.services import combo_acceleration as acceleration, combo_cache as cache
    from app.strategies.combos import ComboStrategy
    from oracles import _build_card_945 as helpers

    FIXTURES = fixtures
    rows = json.loads((root / "backend/config/combo_templates_export.json").read_text())
    TEMPLATES = {row["name"]: row for row in rows if row["name"] in helpers.CATALOG}
    assert len(TEMPLATES) == 14
    logging.getLogger().setLevel(logging.ERROR)


def exact(a, b, path="result"):
    """Compare complete structure; floats have no tolerance and NaNs retain position."""
    if isinstance(a, (pd.DataFrame, pd.Series, pd.Index)):
        assert type(a) is type(b), path
        if isinstance(a, pd.DataFrame):
            pd.testing.assert_frame_equal(a, b, check_exact=True, obj=path)
        elif isinstance(a, pd.Series):
            pd.testing.assert_series_equal(a, b, check_exact=True, obj=path)
        else:
            pd.testing.assert_index_equal(a, b, exact=True, obj=path)
    elif isinstance(a, np.ndarray):
        assert isinstance(b, np.ndarray) and a.dtype == b.dtype and a.shape == b.shape, path
        np.testing.assert_array_equal(a, b, err_msg=path, strict=True)
    elif isinstance(a, dict):
        assert isinstance(b, dict) and a.keys() == b.keys(), path
        for key in a:
            exact(a[key], b[key], f"{path}.{key}")
    elif isinstance(a, (tuple, list)):
        assert type(a) is type(b) and len(a) == len(b), path
        for i, (left, right) in enumerate(zip(a, b)):
            exact(left, right, f"{path}[{i}]")
    elif isinstance(a, (float, np.floating)) and np.isnan(a):
        assert isinstance(b, (float, np.floating)) and np.isnan(b), path
    else:
        assert a == b, f"{path}: {a!r} != {b!r}"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str, allow_nan=True) + "\n")


def manifest(args):
    expected = json.loads(
        (
            args.root / "openspec/changes/card-1091-discovery-cache-numba/evidence/manifest.json"
        ).read_text()
    )
    inventory = []
    for item in expected["fixture_inventory_at_design"]:
        path = args.fixtures / Path(item["path"]).relative_to("backend/tests/fixtures/card_945")
        assert path.stat().st_size == item["bytes"] and sha(path) == item["sha256"], str(path)
        inventory.append(
            dict(
                path=str(path.relative_to(args.fixtures)),
                bytes=path.stat().st_size,
                sha256=sha(path),
            )
        )
    git = lambda *cmd: subprocess.check_output(
        ["git", "-C", str(args.root), *cmd], text=True
    ).strip()
    baseline_hashes = {}
    reference_bodies = {}
    for source in SOURCES:
        if source.endswith(("combo_cache.py", "combo_acceleration.py")):
            continue
        raw = subprocess.check_output(
            ["git", "-C", str(args.root), "show", f"{args.baseline_revision}:{source}"]
        )
        baseline_hashes[source] = hashlib.sha256(raw).hexdigest()
        if source.endswith("deep_backtest.py"):
            definition = next(
                n
                for n in ast.parse(raw).body
                if isinstance(n, ast.FunctionDef) and n.name == "_fast_simulate_execution_with_15m"
            )
            candidate = ast.parse(
                textwrap.dedent(inspect.getsource(deep._fast_simulate_execution_with_15m))
            ).body[0]
            assert ast.dump(definition, include_attributes=False) == ast.dump(
                candidate, include_attributes=False
            )
            reference_bodies["post_945_deep_python"] = "identical AST to baseline revision"
        if source.endswith("combo_strategy.py"):
            cls = next(
                n
                for n in ast.parse(raw).body
                if isinstance(n, ast.ClassDef) and n.name == "ComboStrategy"
            )
            definition = next(
                n
                for n in cls.body
                if isinstance(n, ast.FunctionDef) and n.name == "_fast_position_loop"
            )
            candidate = ast.parse(
                textwrap.dedent(inspect.getsource(ComboStrategy._fast_position_loop))
            ).body[0]
            # Only the documented #1091 import/conditional adapter precedes
            # the preserved post-945 method; its rollback body must be literal.
            assert isinstance(candidate.body[1], ast.ImportFrom) and isinstance(
                candidate.body[2], ast.If
            )
            candidate.body = [candidate.body[0], *candidate.body[3:]]
            assert ast.dump(definition, include_attributes=False) == ast.dump(
                candidate, include_attributes=False
            )
            reference_bodies["post_945_position_python"] = (
                "identical rollback AST to baseline revision"
            )
    result = dict(
        baseline_revision=git("rev-parse", args.baseline_revision),
        candidate_head=git("rev-parse", "HEAD"),
        candidate_uncommitted=True,
        candidate_hashes={s: sha(args.root / s) for s in SOURCES},
        baseline_hashes=baseline_hashes,
        reference_bodies=reference_bodies,
        fixtures=inventory,
        template_export_sha256=sha(args.root / SOURCES[-1]),
        harness_sha256=sha(Path(__file__).resolve()),
        templates=sorted(TEMPLATES),
        volatile_result_fields=[],
        baseline_mode="post-945 rollback in same candidate; kernels also tested against preserved Python implementations",
        platform=platform.platform(),
        machine=platform.machine(),
        python=sys.version,
        cpu_count=os.cpu_count(),
        dependencies={
            name: importlib.metadata.version(name)
            for name in ("numpy", "pandas", "TA-Lib", "numba", "llvmlite", "pyarrow")
        },
    )
    write(
        args.output
        / (f"{args.label}.manifest.json" if args.action == "engine" else "input-manifest.json"),
        result,
    )
    return result


_FRAMES = {}
_PROFILES = {}


def profile_report(profiler, path):
    profiler.disable()
    output = io.StringIO()
    pstats.Stats(profiler, stream=output).strip_dirs().sort_stats("cumulative").print_stats(50)
    path.write_text(output.getvalue())


def frame(symbol, timeframe):
    key = symbol, timeframe
    if key not in _FRAMES:
        raw = pd.read_parquet(
            FIXTURES / "ohlcv" / f"{symbol.replace('/', '_')}_{timeframe}.parquet"
        )
        raw["timestamp_utc"] = pd.to_datetime(raw["timestamp_utc"], utc=True)
        raw = raw.set_index("timestamp_utc", drop=False).sort_index()
        for col in helpers.OHLCV_COLS:
            raw[col] = pd.to_numeric(raw[col], errors="coerce").astype("float64")
        _FRAMES[key] = raw
    return _FRAMES[key]


class FixtureService:
    def get_template_metadata(self, name):
        return helpers.metadata_from_export(TEMPLATES[name])

    def create_strategy(self, template_name, parameters=None):
        meta = self.get_template_metadata(template_name)
        return strategy(meta, parameters or {})


class FixtureProvider:
    def fetch_ohlcv(self, **kwargs):
        return frame(kwargs["symbol"], kwargs["timeframe"]).copy(deep=True)


class FixtureLoader:
    def __init__(self, profile=False):
        self.profile = profile

    def fetch_intraday_data(self, **kwargs):
        if self.profile and os.getpid() not in _PROFILES:
            profiler = cProfile.Profile()
            _PROFILES[os.getpid()] = profiler
            profiler.enable()
        return frame(kwargs["symbol"], "15m")

    def check_intraday_availability(self, symbol, *args, **kwargs):
        return {"available": True, "coverage": {"end": str(frame(symbol, "15m").index.max())}}

    def _get_parquet_path(self, symbol, timeframe):
        return str(FIXTURES / "ohlcv" / f"{symbol.replace('/', '_')}_{timeframe}.parquet")


class WorkerObserver:
    def __init__(self, output, label):
        self.output, self.label = output, label

    def __call__(self, results):
        profiler = _PROFILES.pop(os.getpid(), None)
        if profiler is not None:
            profile_report(profiler, self.output / f"{self.label}.profile-{os.getpid()}.txt")
        item = dict(
            trials=len(results),
            failures=sum(not r.get("success") for r in results),
            pid=os.getpid(),
            peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            retained_bytes=cache.BUDGET.bytes,
            entries=len(cache.BUDGET.entries),
            snapshots=cache.BUDGET.snapshots,
            evictions=cache.BUDGET.evictions,
        )
        with (self.output / f"{self.label}.worker-{os.getpid()}.jsonl").open("a") as out:
            out.write(json.dumps(item) + "\n")


def strategy(meta, params):
    inds, stop = helpers.apply_param_overrides(meta, params)
    return ComboStrategy(
        indicators=inds,
        entry_logic=meta["entry_logic"],
        exit_logic=meta["exit_logic"],
        stop_loss=stop,
        direction=params.get("direction", "long"),
        derived_features=meta.get("derived_features") or [],
    )


def select(mode):
    os.environ.pop("COMBO_OPTIMIZER_LEGACY", None)
    if mode == "baseline":
        os.environ["COMBO_OPTIMIZER_1091_DISABLED"] = "1"
    else:
        os.environ.pop("COMBO_OPTIMIZER_1091_DISABLED", None)
    cache.BUDGET.clear()
    co._WORKER_INDICATOR_CACHE.clear()
    co._WORKER_COVERAGE_CACHE.clear()
    co._WORKER_15M_CACHE.update(key=None, df=None)
    deep._ISO_CACHE.clear()


class LocalIndicatorCalls:
    """Test-only TA-Lib cache with complete effective arrays/kwargs and LRU budget.

    Bound into a private copy of the calculator function. No product module or
    TA-Lib function is monkeypatched; the delivered engine never uses this cache.
    """

    def __getattr__(self, name):
        import talib

        function = getattr(talib, name)

        def call(*arrays, **kwargs):
            inputs = []
            for array in arrays:
                values = np.ascontiguousarray(np.asarray(array))
                inputs.append(
                    (
                        str(values.dtype),
                        values.shape,
                        hashlib.sha256(values.tobytes()).hexdigest(),
                        cache.index_identity(array.index) if isinstance(array, pd.Series) else None,
                    )
                )
            key = name, tuple(inputs), tuple(sorted(kwargs.items()))
            value = cache.BUDGET.get("ablation-talib", key)
            if value is None:
                result = function(*arrays, **kwargs)

                def own(item):
                    arr = np.array(item, copy=True)
                    arr.flags.writeable = False
                    return arr

                value = tuple(own(x) for x in result) if isinstance(result, tuple) else own(result)
                cache.BUDGET.put("ablation-talib", key, value)
            return value

        return call


def local_function(function, namespace, name=None, strategy_override=False):
    """Copy a callable into a private harness namespace, leaving product intact."""
    tree = ast.parse(textwrap.dedent(inspect.getsource(function)))
    definition = tree.body[0]
    definition.name = name or definition.name
    if strategy_override:

        class ReplaceStrategy(ast.NodeTransformer):
            def visit_ImportFrom(self, node):
                if node.module == "app.strategies.combos":
                    return ast.Assign(
                        targets=[ast.Name(id="ComboStrategy", ctx=ast.Store())],
                        value=ast.Name(id="HarnessIndicatorStrategy", ctx=ast.Load()),
                    )
                return node

        tree = ReplaceStrategy().visit(tree)
    ast.fix_missing_locations(tree)
    exec(compile(tree, str(Path(__file__).resolve()), "exec"), namespace)
    return namespace[definition.name]


def ablation(args):
    """Five alternating frozen trial batches per scenario, fingerprint+Numba both sides."""
    calculate = local_function(
        ComboStrategy.calculate_indicators,
        dict(ComboStrategy.calculate_indicators.__globals__, talib=LocalIndicatorCalls()),
    )

    class HarnessIndicatorStrategy(ComboStrategy):
        calculate_indicators = calculate

    logic = local_function(
        co._run_backtest_logic,
        dict(co.__dict__, HarnessIndicatorStrategy=HarnessIndicatorStrategy),
        strategy_override=True,
    )
    parameters = json.loads((args.fixtures / "r1_params.json").read_text())
    acceleration.warm_kernels()
    scenarios = {}
    for label, template, symbol, direction in (
        ("primary", "multi_ma_crossover", "1INCH/USDT", "long"),
        ("aave", "multi_ma_crossover", "AAVE/USDT", "short"),
        ("ema-rsi", "ema_rsi", "1INCH/USDT", "long"),
    ):
        data, _ = co.split_train_holdout(frame(symbol, "1d"), 0.7)
        snapshot = cache.Snapshot(data, generation=f"ablation-{label}", source=(symbol, "1d"))
        meta = helpers.metadata_from_export(TEMPLATES[template])
        rows = [dict(p, direction=direction, timeframe="1d") for p in parameters[template][:50]]
        pairs = []
        for repetition in range(5):
            pair, reference = {}, None
            for mode in (
                ("without", "individual") if repetition % 2 == 0 else ("individual", "without")
            ):
                select("candidate")
                fn = logic if mode == "individual" else co._run_backtest_logic
                started = time.perf_counter()
                with contextlib.redirect_stdout(io.StringIO()):
                    values = [
                        fn(
                            meta,
                            p,
                            snapshot,
                            True,
                            symbol,
                            "2023-01-01",
                            "2025-01-01",
                            frame(symbol, "15m"),
                        )
                        for p in rows
                    ]
                pair[mode] = time.perf_counter() - started
                assert not any("error" in value[0] for value in values)
                if reference is None:
                    reference = values
                else:
                    exact(reference, values, f"indicator-ablation-{label}")
            pairs.append(pair)
        before = statistics.median(p["without"] for p in pairs)
        after = statistics.median(p["individual"] for p in pairs)
        wins = sum(p["individual"] < p["without"] for p in pairs)
        scenarios[label] = dict(
            pairs=pairs,
            without_median_s=before,
            individual_median_s=after,
            wins=wins,
            gain_pct=100 * (1 - after / before),
            exact=True,
        )
        print(json.dumps(dict(ablation=label, **scenarios[label])), flush=True)
    report = dict(
        scenarios=scenarios,
        scope="50 frozen trial batch, fingerprint+Numba both sides, single process",
        delivered=False,
        decision="Excluded: worse median and majority worse in all three repeated batch screenings; no full-engine inclusion justified",
        global_monkeypatch=False,
    )
    write(args.output / "indicator-ablation.json", report)
    return report


def trial(meta, params, data, intra):
    strat = strategy(meta, params)
    calculated = strat.calculate_indicators(data.copy(deep=True))
    masks = []
    for logic in (meta["entry_logic"], meta["exit_logic"]):
        try:
            masks.append(strat._evaluate_logic_vectorized(calculated, logic))
        except Exception:
            masks.append(pd.Series(False, index=calculated.index))
    signals = strat._fast_position_loop(calculated, *masks)
    stop = strat.stop_loss
    trades, execution = co.extract_trades_with_mode(
        signals,
        stop,
        True,
        "frozen/USDT",
        "2023-01-01",
        "2025-01-01",
        intra,
        params["direction"],
        True,
        slippage=0.001,
    )
    metrics = co._metrics_from_trades(trades, 100)
    logic_result = co._run_backtest_logic(
        meta, params, data, True, "frozen/USDT", "2023-01-01", "2025-01-01", intra
    )
    assert "error" not in logic_result[0], logic_result
    return calculated, masks, signals, trades, execution, metrics, logic_result


def validate(args):
    params = json.loads((args.fixtures / "r1_params.json").read_text())
    count = warnings = 0
    started = time.perf_counter()
    for symbol in ("1INCH/USDT", "AAVE/USDT"):
        data, _ = co.split_train_holdout(frame(symbol, "1d"), 0.7)
        intra = frame(symbol, "15m")
        for name in TEMPLATES:
            meta = helpers.metadata_from_export(TEMPLATES[name])
            capture = io.StringIO()
            with contextlib.redirect_stdout(capture):
                for direction in ("long", "short"):
                    rows = [dict(p, direction=direction, timeframe="1d") for p in params[name][:50]]
                    select("baseline")
                    references = [trial(meta, p, data, intra) for p in rows]
                    select("candidate")
                    for p, reference in zip(rows, references):
                        candidate = trial(meta, p, data, intra)
                        exact(reference, candidate, f"{symbol}/{name}/{direction}/{count}")
                        count += 1
            warnings += capture.getvalue().count("Error in vectorized logic:")
            print(json.dumps(dict(template=name, symbol=symbol, exact_trials=count)), flush=True)
    edges = validate_edges()
    report = dict(
        exact_trials=count,
        exact_edges=edges,
        complete_indicators_masks_signals_trades_metrics=True,
        preexisting_logic_warning_occurrences=warnings,
        elapsed_s=time.perf_counter() - started,
        tolerance=0,
        volatile_result_fields=[],
    )
    assert count == 2800 and edges >= 568
    write(args.output / "equivalence.json", report)
    return report


def validate_edges():
    rng = np.random.default_rng(1091)
    count = 0
    for i in range(568):
        n = i % 71
        idx = pd.date_range("2023-01-01", periods=n, freq="4h" if i % 2 else "1D", tz="UTC")
        prices = rng.uniform(1, 100, n)
        lows, highs = prices * 0.85, prices * 1.15
        if n and i % 11 == 0:
            prices[n // 2] = [np.nan, np.inf, 0.0][(i // 11) % 3]
        data = pd.DataFrame(
            dict(open=prices, low=lows, high=highs, close=prices, volume=1.0), index=idx
        )
        entries = pd.Series(rng.random(n) < 0.3, index=idx)
        exits = pd.Series(rng.random(n) < 0.3, index=idx)
        direction = "short" if i % 2 else "long"
        stop = [0.0, 0.01, 0.5, 2.0, np.nan][i % 5]
        strat = ComboStrategy(
            indicators=[], entry_logic="", exit_logic="", stop_loss=stop, direction=direction
        )
        with np.errstate(all="ignore"):
            select("baseline")
            expected = strat._fast_position_loop(data.copy(), entries, exits)
            select("candidate")
            actual = strat._fast_position_loop(data.copy(), entries, exits)
            exact(expected, actual, f"position-edge-{i}")
            intra_idx = pd.date_range("2023-01-01", periods=n * 96, freq="15min", tz="UTC")
            intra = pd.DataFrame(
                dict(
                    low=rng.uniform(0, 100, len(intra_idx)),
                    high=rng.uniform(1, 150, len(intra_idx)),
                ),
                index=intra_idx,
            )
            if i % 3 == 0:
                intra = intra.iloc[:0]
            select("baseline")
            a = deep._fast_simulate_execution_with_15m(expected, intra, stop, direction, 0.002)
            select("candidate")
            b = deep._compiled_simulate_execution_with_15m(actual, intra, stop, direction, 0.002)
            exact(a, b, f"deep-edge-{i}")
        count += 1
    return count


def rss_tree_kib(pid):
    total = 0
    pending = [pid]
    while pending:
        current = pending.pop()
        try:
            status = Path(f"/proc/{current}/status").read_text()
            total += int(
                next(line.split()[1] for line in status.splitlines() if line.startswith("VmRSS:"))
            )
            pending.extend(
                int(v) for v in Path(f"/proc/{current}/task/{current}/children").read_text().split()
            )
        except (OSError, StopIteration):
            pass
    return total


def jit(args):
    select("candidate")
    started = time.perf_counter()
    acceleration.warm_kernels()
    report = dict(
        label=args.label,
        preparation_jit_s=time.perf_counter() - started,
        startup_imports_manifest_s=started - PROCESS_STARTED,
        cache_directory=os.environ.get("NUMBA_CACHE_DIR", "Numba default"),
        position_compiled=acceleration.positions.compiled is not None,
        deep_compiled=acceleration.deep_execution.compiled is not None,
        peak_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    )
    assert report["position_compiled"] and report["deep_compiled"]
    write(args.output / f"{args.label}.jit.json", report)
    print(json.dumps(report), flush=True)


def engine(args):
    select(args.mode)
    frame(args.symbol, "1d")
    frame(args.symbol, "15m")
    inputs = {key: cache.frame_identity(df) for key, df in _FRAMES.items()}
    start = time.perf_counter()
    warm = 0.0
    if args.mode == "candidate" and not args.cold:
        acceleration.warm_kernels()
        warm = time.perf_counter() - start
    loader = FixtureLoader(profile=args.profile)
    opt = co.ComboOptimizer(
        str(args.output / "checkpoints"),
        combo_service=FixtureService(),
        provider=FixtureProvider(),
        loader=loader,
        worker_loader=loader,
        workers=3,
        worker_observer=WorkerObserver(args.output, args.label),
    )
    samples, stopped = [], threading.Event()

    def sample():
        while not stopped.wait(0.05):
            samples.append(rss_tree_kib(os.getpid()))

    monitor = threading.Thread(target=sample, daemon=True)
    monitor.start()
    started = time.perf_counter()
    try:
        result = opt.run_optimization(
            template_name=args.template,
            symbol=args.symbol,
            timeframe="1d",
            data_source="ccxt",
            start_date="2023-01-01",
            end_date="2025-01-01",
            direction=args.direction,
            deep_backtest=True,
            split_train_ratio=0.7,
            job_id="card-1091-frozen",
        )
    finally:
        stopped.set()
        monitor.join()
        final_profile = _PROFILES.pop(os.getpid(), None)
        if final_profile is not None:
            profile_report(final_profile, args.output / f"{args.label}.parent-final-profile.txt")
    elapsed = time.perf_counter() - started
    assert result["execution_mode"] == "deep_15m", result.get("execution_mode")
    assert result["oos_verdict"]["execution_mode"] == "deep_15m"
    assert result["oos_verdict"]["status"] in ("GO", "NO-GO")
    assert inputs == {key: cache.frame_identity(df) for key, df in _FRAMES.items()}
    workers = [
        json.loads(line)
        for path in args.output.glob(f"{args.label}.worker-*.jsonl")
        for line in path.read_text().splitlines()
    ]
    write(args.output / f"{args.label}.result.json", result)
    report = dict(
        label=args.label,
        mode=args.mode,
        elapsed_s=elapsed,
        preparation_jit_s=warm,
        profiled_diagnostic_run=args.profile,
        startup_imports_fixtures_manifest_s=started - PROCESS_STARTED - warm,
        cold=args.cold,
        workers=3,
        trials=sum(x["trials"] for x in workers),
        failed_trials=sum(x["failures"] for x in workers),
        template=args.template,
        symbol=args.symbol,
        direction=args.direction,
        rss_parent_workers_peak_kib=max(samples, default=0),
        parent_peak_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        worker_peaks_kib={
            str(x["pid"]): max(y["peak_rss_kib"] for y in workers if y["pid"] == x["pid"])
            for x in workers
        },
        max_retained_bytes=max((x["retained_bytes"] for x in workers), default=0),
        max_cache_entries=max((x["entries"] for x in workers), default=0),
        max_snapshots=max((x["snapshots"] for x in workers), default=0),
        evictions=max((x["evictions"] for x in workers), default=0),
        parent_retained_after_execution=cache.BUDGET.bytes,
        result_sha256=sha(args.output / f"{args.label}.result.json"),
        input_unchanged=True,
    )
    assert report["failed_trials"] == 0
    if (
        args.template == "multi_ma_crossover"
        and args.symbol == "1INCH/USDT"
        and args.direction == "long"
    ):
        assert report["trials"] == 21210, report
    if args.mode == "candidate":
        assert report["max_retained_bytes"] <= 64 * 1024 * 1024
        assert report["max_cache_entries"] <= 4096 and report["max_snapshots"] <= 32
        assert report["parent_retained_after_execution"] == 0
    write(args.output / f"{args.label}.summary.json", report)
    print(json.dumps(report), flush=True)
    return report


def suite(args):
    records, scenarios = [], {}
    existing = args.output / "performance.json"
    if args.scenario != "all" and existing.exists():
        previous = json.loads(existing.read_text())
        records, scenarios = previous["runs"], previous["scenarios"]
    for name, template, symbol, direction in (
        ("primary", "multi_ma_crossover", "1INCH/USDT", "long"),
        ("aave", "multi_ma_crossover", "AAVE/USDT", "short"),
        ("ema-rsi", "ema_rsi", "1INCH/USDT", "long"),
    ):
        if args.scenario not in ("all", name):
            continue
        pairs = []
        reference = None
        for rep in range(5):
            pair = {}
            for mode in (("baseline", "candidate") if rep % 2 == 0 else ("candidate", "baseline")):
                label = f"{name}-{rep + 1}-{mode}"
                command = [
                    sys.executable,
                    str(Path(__file__).resolve()),
                    "engine",
                    "--root",
                    str(args.root),
                    "--fixtures",
                    str(args.fixtures),
                    "--output",
                    str(args.output),
                    "--mode",
                    mode,
                    "--label",
                    label,
                    "--template",
                    template,
                    "--symbol",
                    symbol,
                    "--direction",
                    direction,
                ]
                print(json.dumps(dict(starting=label)), flush=True)
                with (args.output / f"{label}.log").open("w") as log:
                    subprocess.run(
                        command,
                        stdout=log,
                        stderr=subprocess.STDOUT,
                        check=True,
                        env=dict(os.environ, PYTHONHASHSEED="0"),
                    )
                report = json.loads((args.output / f"{label}.summary.json").read_text())
                result = json.loads((args.output / f"{label}.result.json").read_text())
                if reference is None:
                    reference = result
                else:
                    exact(reference, result, label)
                # Preserve raw bytes once per scenario; identical complete
                # outputs use relative links instead of ten duplicate blobs.
                raw_path = args.output / f"{label}.result.json"
                canonical_path = args.output / f"{name}.result.json.gz"
                compressed = gzip.compress(raw_path.read_bytes(), mtime=0)
                if canonical_path.exists():
                    assert gzip.decompress(canonical_path.read_bytes()) == raw_path.read_bytes()
                else:
                    canonical_path.write_bytes(compressed)
                (args.output / f"{label}.result.json.gz").symlink_to(canonical_path.name)
                raw_path.unlink()
                for raw in [
                    args.output / f"{label}.log",
                    *args.output.glob(f"{label}.worker-*.jsonl"),
                ]:
                    raw.with_suffix(raw.suffix + ".gz").write_bytes(
                        gzip.compress(raw.read_bytes(), mtime=0)
                    )
                    raw.unlink()
                pair[mode] = report["elapsed_s"]
                records.append(report)
                write(args.output / "performance-progress.json", records)
            pairs.append(pair)
        before = [p["baseline"] for p in pairs]
        after = [p["candidate"] for p in pairs]
        wins = sum(p["candidate"] < p["baseline"] for p in pairs)
        better = statistics.median(after) < statistics.median(before)
        summary = dict(
            pairs=pairs,
            baseline_median_s=statistics.median(before),
            candidate_median_s=statistics.median(after),
            wins=wins,
            gain_pct=100 * (1 - statistics.median(after) / statistics.median(before)),
            baseline_range_s=[min(before), max(before)],
            candidate_range_s=[min(after), max(after)],
            baseline_stdev_s=statistics.stdev(before),
            candidate_stdev_s=statistics.stdev(after),
            exact_complete_results=True,
            passed=(better and wins >= 3) if name == "primary" else not (not better and wins <= 2),
        )
        scenarios[name] = summary
        write(args.output / "performance.json", dict(scenarios=scenarios, runs=records))
        assert summary["passed"], (name, summary)
    return scenarios


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action", choices=("manifest", "validate", "engine", "suite", "ablation", "jit")
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--fixtures", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--baseline-revision", default=BASELINE)
    parser.add_argument("--mode", choices=("baseline", "candidate"), default="candidate")
    parser.add_argument("--label", default="initial")
    parser.add_argument("--template", default="multi_ma_crossover")
    parser.add_argument("--symbol", default="1INCH/USDT")
    parser.add_argument("--direction", default="long")
    parser.add_argument(
        "--scenario",
        choices=("all", "primary", "aave", "ema-rsi"),
        default="all",
        help="select a complete five-pair scenario; default runs all three",
    )
    parser.add_argument("--cold", action="store_true")
    parser.add_argument(
        "--profile",
        action="store_true",
        help="diagnostic cProfile for parent and first worker batches; excludes timing acceptance",
    )
    args = parser.parse_args()
    args.root = args.root.resolve()
    args.fixtures = (args.fixtures or args.root / "backend/tests/fixtures/card_945").resolve()
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    initialize(args.root, args.fixtures)
    manifest(args)
    if args.action != "manifest":
        globals()[args.action](args)


if __name__ == "__main__":
    main()
