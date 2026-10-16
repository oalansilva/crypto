"""Exact ranking and bounded-admission regression fixtures for #1093."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import math
import pickle
import subprocess
import pytest
import numpy as np

from app.services.discovery_resources import (
    ResourceProfile,
    OperationalFailure,
    CalculationFailure,
    GiB,
    admission,
)
from app.services.discovery_stream import ResultSpool, execute_stream, batches
from app.services.discovery_budget_cache import Cache, BUDGET
from app.services import combo_optimizer as opt
from app.services import discovery_resources as resources


def trial_row(trial, value, branch=0):
    return {
        "trial_index": trial,
        "value": value,
        "success": True,
        "metrics": {
            "sharpe_ratio": (value % 7) - branch,
            "total_return": value if value == 400 else value % 13,
            "total_trades": 0,
        },
    }


def reference(rows, params, stage, limit):
    sharpes = [r["metrics"]["sharpe_ratio"] for r in rows]
    returns = [r["metrics"]["total_return"] for r in rows]
    min_s, max_s = min(sharpes), max(sharpes)
    min_r, max_r = min(returns), max(returns)
    range_s, range_r = max_s - min_s, max_r - min_r
    scored = []
    for res in rows:
        m = res["metrics"]
        s, r = m["sharpe_ratio"], m["total_return"]
        ns = (s - min_s) / range_s if range_s > 0 else 0
        nr = (r - min_r) / range_r if range_r > 0 else 0
        score = (0.7 * ns) + (0.3 * nr)
        result_params = params.copy()
        if stage.get("grid_mode"):
            result_params.update(res["value"])
        else:
            result_params[stage["parameter"]] = res["value"]
        scored.append(
            {
                "params": result_params,
                "metrics": m,
                "score": score,
                "trial_index": res["trial_index"],
            }
        )
    scored.sort(key=lambda x: (-x["score"], x["trial_index"]))
    return scored[:limit]


@pytest.mark.parametrize("special", [None, float("nan"), float("inf"), -float("inf")])
def test_exact_last_batch_extrema_ties_and_nonfinite(tmp_path, special):
    rows = [trial_row(i, i) for i in range(401)]
    if special is not None:
        rows[-1]["metrics"]["sharpe_ratio"] = special
    stage = {"parameter": "x"}
    with ResultSpool(root=tmp_path) as spool:
        for row in reversed(rows):
            spool.add(0, row)
        actual = spool.ranked(0, {"direction": "long"}, stage, 401)
    expected = reference(rows, {"direction": "long"}, stage, 401)
    assert [r["trial_index"] for r in actual] == [r["trial_index"] for r in expected]
    np.testing.assert_array_equal([r["score"] for r in actual], [r["score"] for r in expected])
    assert [r["params"] for r in actual] == [r["params"] for r in expected]
    assert not list(tmp_path.iterdir())


def test_spool_quota_never_publishes_truncated_winner(tmp_path):
    with pytest.raises(OperationalFailure, match="spool_quota"):
        with ResultSpool(replace(ResourceProfile(), spool_bytes=32), tmp_path) as spool:
            spool.add(0, trial_row(0, 1))
    assert not list(tmp_path.iterdir())


def test_stream_window_and_honest_pool_loss(tmp_path, monkeypatch):
    from app.services import discovery_stream

    events = []
    monkeypatch.setattr(discovery_stream, "PROGRESS_CALLBACK", events.append)
    args = lambda: (({}, {}, None, "x", i, False, "BTC/USDT", None, None, i) for i in range(451))

    def worker(batch):
        return [trial_row(arg[9], arg[4]) for arg in batch]

    with ThreadPoolExecutor(1) as pool, ResultSpool(root=tmp_path) as spool:
        counts = execute_stream(pool, worker, args, 451, spool)
    assert counts == dict(
        planned=451, executed=451, succeeded=451, failed=0, unknown=0, remaining=0
    )
    assert max(e.get("pending_futures", 0) for e in events) <= 2
    assert max(e.get("pending_bytes", 0) for e in events) <= 64 * 1024**2
    calls = 0

    def die(batch):
        nonlocal calls
        calls += 1
        if calls > 1:
            raise RuntimeError("pool lost")
        return worker(batch)

    with ThreadPoolExecutor(1) as pool, ResultSpool(root=tmp_path) as spool:
        with pytest.raises(OperationalFailure) as failure:
            execute_stream(pool, die, args, 451, spool)
    counts = failure.value.counters
    assert counts["executed"] == counts["succeeded"] == 200
    assert counts["unknown"] + counts["remaining"] == 251
    assert counts["planned"] == 451


def test_calculation_error_prevents_round_advance(tmp_path):
    args = lambda: (({}, {}, None, "x", i, False, "X", None, None, i) for i in range(4))

    def worker(batch):
        rows = [trial_row(arg[9], arg[4]) for arg in batch]
        rows[-1] = {"trial_index": 3, "success": False, "error": "bad indicator"}
        return rows

    with ThreadPoolExecutor(1) as pool, ResultSpool(root=tmp_path) as spool:
        with pytest.raises(CalculationFailure) as failure:
            execute_stream(pool, worker, args, 4, spool)
    assert failure.value.counters["executed"] == 4
    assert failure.value.counters["succeeded"] == 3
    assert failure.value.counters["failed"] == 1


def test_cache_cold_warm_eviction_oversize_and_execution_cleanup():
    BUDGET.clear()
    cache = Cache("indicators")
    array = np.arange(8)
    cache["x"] = array
    assert cache.get("x") is array
    for i in range(4100):
        cache[i] = (i,)
    assert BUDGET.bytes <= 64 * 1024**2
    assert len(BUDGET.entries) <= 4096
    assert cache.get("x") is None
    cache["oversize"] = np.empty(65 * 1024**2, dtype=np.uint8)
    assert cache.get("oversize") is None
    BUDGET.clear()
    assert BUDGET.bytes == 0


def test_configured_worker_is_not_cpu_count(monkeypatch):
    monkeypatch.setattr("os.cpu_count", lambda: 192)
    assert ResourceProfile().effective_workers == 1
    with pytest.raises(OperationalFailure):
        replace(ResourceProfile(), requested_workers=3).effective_workers
    assert (
        replace(
            ResourceProfile(), name="test", memory_max=11 * GiB, requested_workers=3
        ).effective_workers
        == 3
    )


def test_admission_refuses_unverified_and_requires_reserve(tmp_path, monkeypatch):
    profile = ResourceProfile()
    for key, value in {
        "memory.high": profile.memory_high,
        "memory.max": profile.memory_max,
        "memory.swap.max": profile.swap_max,
        "memory.oom.group": 1,
    }.items():
        (tmp_path / key).write_text(str(value))
    memory = {"MemTotal": 24 * GiB, "MemAvailable": 9 * GiB, "SwapFree": 2 * GiB}
    assert admission(profile, tmp_path, tmp_path, memory)["requested_workers"] == 1
    with pytest.raises(OperationalFailure):
        admission(profile, tmp_path, tmp_path, {**memory, "SwapFree": 0})
    (tmp_path / "memory.max").write_text("max")
    with pytest.raises(OperationalFailure):
        admission(profile, tmp_path, tmp_path, memory)


def _write_limits(group, profile, **override):
    group.mkdir(parents=True, exist_ok=True)
    values = {
        "memory.high": profile.memory_high,
        "memory.max": profile.memory_max,
        "memory.swap.max": profile.swap_max,
        "memory.oom.group": 1,
        **override,
    }
    for key, value in values.items():
        (group / key).write_text(str(value))


HEALTHY_HOST = {"MemTotal": 23 * GiB, "MemAvailable": 9 * GiB, "SwapFree": 2 * GiB}


def test_environment_profiles_match_approved_limits():
    dev, prod = ResourceProfile.named("dev"), ResourceProfile.named("prod")
    assert (dev.memory_high, dev.memory_max, dev.swap_max) == (3 * GiB, 4 * GiB, 512 * 1024**2)
    assert (prod.memory_high, prod.memory_max, prod.swap_max) == (4 * GiB, 5 * GiB, 512 * 1024**2)
    assert ResourceProfile() == dev
    assert dev.effective_workers == 1 and prod.effective_workers == 1


def test_configured_profile_selected_by_environment_variable(monkeypatch):
    monkeypatch.delenv("DISCOVERY_INTERNAL_WORKERS", raising=False)
    monkeypatch.delenv("DISCOVERY_RESOURCE_PROFILE", raising=False)
    assert ResourceProfile.configured().name == "dev"
    monkeypatch.setenv("DISCOVERY_RESOURCE_PROFILE", "prod")
    assert ResourceProfile.configured() == ResourceProfile.named("prod")
    monkeypatch.setenv("DISCOVERY_RESOURCE_PROFILE", "staging")
    with pytest.raises(OperationalFailure) as raised:
        ResourceProfile.configured()
    assert raised.value.code == "resource_budget_unavailable"
    with pytest.raises(OperationalFailure):
        admission(ResourceProfile(name="staging"), None, None, HEALTHY_HOST)


@pytest.mark.parametrize("name", ["dev", "prod"])
def test_named_profiles_require_exactly_one_worker(monkeypatch, name):
    monkeypatch.setenv("DISCOVERY_RESOURCE_PROFILE", name)
    monkeypatch.setenv("DISCOVERY_INTERNAL_WORKERS", "3")
    with pytest.raises(OperationalFailure):
        ResourceProfile.configured().effective_workers
    monkeypatch.setenv("DISCOVERY_INTERNAL_WORKERS", "x")
    with pytest.raises(OperationalFailure):
        ResourceProfile.configured()


@pytest.mark.parametrize(
    "memory_max, expected",
    [(4 * GiB, 1), (5 * GiB, 1), (7 * GiB, 2), (10 * GiB, 3)],
)
def test_worker_formula_uses_memory_max_minus_one_gib(memory_max, expected):
    profile = replace(
        ResourceProfile(), name="test", memory_max=memory_max, requested_workers=expected + 1
    )
    assert profile.effective_workers == expected


def test_worker_formula_refuses_below_four_gib():
    for memory_max in (3 * GiB, 4 * GiB - 1):
        with pytest.raises(OperationalFailure):
            replace(ResourceProfile(), memory_max=memory_max).effective_workers
    with pytest.raises(OperationalFailure):
        replace(ResourceProfile(), batch_size=0).effective_workers


@pytest.mark.parametrize("name", ["dev", "prod"])
def test_admission_accepts_each_profile_with_its_own_limits(tmp_path, name):
    profile = ResourceProfile.named(name)
    _write_limits(tmp_path, profile)
    assert admission(profile, tmp_path, tmp_path, HEALTHY_HOST)["name"] == name


@pytest.mark.parametrize("name", ["dev", "prod"])
def test_admission_reserves_both_envelopes_plus_fourteen_gib(tmp_path, name):
    profile = ResourceProfile.named(name)
    _write_limits(tmp_path, profile)
    assert resources.ENVELOPE_TOTAL == 9 * GiB
    assert resources.HOST_RESERVE == 14 * GiB
    # The real host has 23.41 GiB: it fits, and one byte less than 23 GiB does not.
    assert admission(profile, tmp_path, tmp_path, {**HEALTHY_HOST, "MemTotal": 25_137_336_320})
    with pytest.raises(OperationalFailure) as raised:
        admission(profile, tmp_path, tmp_path, {**HEALTHY_HOST, "MemTotal": 23 * GiB - 1})
    assert raised.value.code == "resource_budget_unavailable"


@pytest.mark.parametrize("unit, expected", [("dev", "prod"), ("prod", "dev")])
def test_admission_refuses_when_unit_and_profile_diverge(tmp_path, unit, expected):
    _write_limits(tmp_path, ResourceProfile.named(unit))
    with pytest.raises(OperationalFailure) as raised:
        admission(ResourceProfile.named(expected), tmp_path, tmp_path, HEALTHY_HOST)
    assert raised.value.code == "resource_budget_unavailable"
    # Each single limit is compared exactly, not only the envelope.
    profile = ResourceProfile.named("prod")
    for key, value in (
        ("memory.high", 5 * GiB),
        ("memory.swap.max", 0),
        ("memory.oom.group", 0),
    ):
        _write_limits(tmp_path, profile, **{key: value})
        with pytest.raises(OperationalFailure):
            admission(profile, tmp_path, tmp_path, HEALTHY_HOST)


def test_admission_prod_waits_for_host_memory(tmp_path):
    profile = ResourceProfile.named("prod")
    _write_limits(tmp_path, profile)
    with pytest.raises(OperationalFailure) as raised:
        admission(profile, tmp_path, tmp_path, {**HEALTHY_HOST, "MemAvailable": 8 * GiB - 1})
    assert raised.value.code == "resource_budget_unavailable"
    assert admission(profile, tmp_path, tmp_path, {**HEALTHY_HOST, "MemAvailable": 8 * GiB})


@pytest.mark.parametrize(
    "cgroup, app_env, profile_env, expected",
    [
        ("criptofarol-prod-discovery-worker.service", "development", None, "prod"),
        ("criptofarol-prod-runtime-worker.service", "development", "dev", "prod"),
        ("criptofarol-dev-backend.service", "production", None, "dev"),
        ("criptofarol-dev-discovery-worker.service", None, "prod", "dev"),
        ("session-1.scope", "staging", None, "staging"),
        ("session-1.scope", "staging", "dev", "dev"),
        ("session-1.scope", None, None, "dev"),
    ],
)
def test_discovery_environment_prefers_unit_name(
    monkeypatch, tmp_path, cgroup, app_env, profile_env, expected
):
    monkeypatch.setattr(resources, "cgroup_path", lambda: tmp_path / "system.slice" / cgroup)
    for variable, value in (("APP_ENV", app_env), ("DISCOVERY_RESOURCE_PROFILE", profile_env)):
        if value is None:
            monkeypatch.delenv(variable, raising=False)
        else:
            monkeypatch.setenv(variable, value)
    assert resources.discovery_environment() == expected


def test_discovery_environment_without_cgroup_info_falls_back(monkeypatch):
    def unavailable():
        raise OperationalFailure("resource_budget_unavailable")

    monkeypatch.setattr(resources, "cgroup_path", unavailable)
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("DISCOVERY_RESOURCE_PROFILE", raising=False)
    assert resources.discovery_environment() == "dev"
    monkeypatch.setenv("APP_ENV", "prod")
    assert resources.discovery_environment() == "prod"


def test_prod_admission_refusal_does_not_claim_attempt_or_ack(tmp_path, monkeypatch):
    """MemAvailable < 8 GiB: no combination reserved, no attempt/circuit failure, no ack."""
    from unittest.mock import MagicMock
    from app.tasks import discovery_celery_tasks as tasks
    from app.services import discovery_recovery

    profile = ResourceProfile.named("prod")
    _write_limits(tmp_path, profile)
    monkeypatch.setenv("DISCOVERY_RESOURCE_PROFILE", "prod")
    monkeypatch.delenv("DISCOVERY_INTERNAL_WORKERS", raising=False)
    monkeypatch.setattr(resources, "cgroup_path", lambda: tmp_path)
    monkeypatch.setattr(
        resources, "host_memory", lambda: {**HEALTHY_HOST, "MemAvailable": 7 * GiB}
    )
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    service = MagicMock()
    monkeypatch.setattr(tasks, "SessionLocal", lambda: db)
    monkeypatch.setattr(tasks, "DiscoveryService", lambda: service)
    monkeypatch.setattr(discovery_recovery, "reconcile_expired", lambda *_: None)
    recorded = MagicMock()
    for name in ("claim_attempt", "failed_locked", "fail"):
        monkeypatch.setattr(discovery_recovery, name, recorded)

    result = tasks.run_sweep_orchestrator("sweep-1", 1)

    assert result == {"state": "resource_budget_unavailable", "sweep_id": "sweep-1"}
    service.claim_combinations.assert_not_called()
    service.ack_outbox.assert_not_called()
    service.ensure_sweep_wakeup.assert_not_called()
    recorded.assert_not_called()
    db.add.assert_not_called()
    db.commit.assert_not_called()
    db.close.assert_called_once()


def test_r1_and_r2_r4_exact_same_domains(tmp_path, monkeypatch):
    monkeypatch.setenv("DISCOVERY_SPOOL_DIR", str(tmp_path))
    optimizer = object.__new__(opt.ComboOptimizer)

    def worker(batch):
        return [
            {
                **trial_row(
                    a[9], a[4]["x"] if isinstance(a[4], dict) else a[4], a[1].get("branch", 0)
                ),
                "value": a[4],
            }
            for a in batch
        ]

    monkeypatch.setattr(opt, "_worker_run_batch", worker)
    stage = {"parameter": ["x"], "values": [list(range(401))], "grid_mode": True}
    with ThreadPoolExecutor(1) as pool:
        actual = optimizer._execute_opt_stages(
            [stage],
            {"branch": 0},
            1,
            1,
            "t",
            "X",
            "1d",
            True,
            None,
            None,
            False,
            {},
            None,
            return_top_n=5,
            executor=pool,
        )
        expected = reference(
            [{**trial_row(i, i), "value": {"x": i}} for i in range(401)], {"branch": 0}, stage, 10
        )
        assert actual == expected
        candidates = [{"params": {"branch": b, "x": 1}, "meta": {}, "score": 1} for b in range(3)]
        stage2 = {"parameter": "x", "values": list(range(401))}
        for round_num in (2, 3, 4):
            refined = optimizer._execute_r2r4_pooled(
                candidates,
                [stage2],
                round_num,
                1,
                "t",
                "X",
                "1d",
                True,
                None,
                None,
                False,
                {},
                None,
                pool,
            )
            for b, row in enumerate(refined):
                expected = reference(
                    [trial_row(i, i, b) for i in range(401)], candidates[b]["params"], stage2, 1
                )[0]
                assert row["params"] == expected["params"]
                assert row["metrics"] == expected["metrics"]


def test_original_492480_template_has_deterministic_invalid_length_trial():
    """The original grid varies lengths while referencing fixed RSI_14/ADX_14."""
    from pathlib import Path
    import json
    import pandas as pd

    frozen = json.loads(
        (Path(__file__).parents[1] / "fixtures/discovery_memory/original_template.json").read_text()
    )
    n = 400
    close = 100 + np.sin(np.arange(n) / 11) * 8 + np.arange(n) / 20
    frame = pd.DataFrame(
        {
            "open": close,
            "high": close + 2,
            "low": close - 2,
            "close": close,
            "volume": np.full(n, 1000),
        },
        index=pd.date_range("2025-10-06", periods=n, freq="15min", tz="UTC"),
    )
    template = {
        "name": frozen["name"],
        **frozen["template_data"],
        "optimization_schema": frozen["optimization_schema"],
    }
    metrics, _ = opt._run_backtest_logic(
        template,
        {"rsi_length": 10, "adx_length": 10, "timeframe": "15m"},
        frame,
        False,
        "BTC/USDT",
        "2025-10-06",
        "2026-10-06",
    )
    assert "error" not in metrics
    valid, _ = opt._run_backtest_logic(
        template,
        {"rsi_length": 14, "adx_length": 14, "timeframe": "15m"},
        frame,
        False,
        "BTC/USDT",
        "2025-10-06",
        "2026-10-06",
    )
    assert "error" not in valid
    optimizer = object.__new__(opt.ComboOptimizer)
    from types import SimpleNamespace

    optimizer.combo_service = SimpleNamespace(get_template_metadata=lambda _: template)
    stages = optimizer.generate_stages(
        "long_ma_pullback_rsi_adx", "BTC/USDT", fixed_timeframe="15m"
    )
    assert optimizer._calculate_grid_size(stages[0]) == 492480


@pytest.mark.parametrize(
    "failure",
    [
        subprocess.TimeoutExpired(["systemctl"], 2),
        FileNotFoundError("systemctl"),
        PermissionError("systemctl"),
        subprocess.SubprocessError("boom"),
    ],
    ids=["timeout", "missing_binary", "oserror", "subprocess_error"],
)
def test_telemetry_degrades_when_systemctl_fails(tmp_path, monkeypatch, failure):
    """systemctl is best-effort telemetry; it must never fail the batch."""
    calls = []

    def broken(*args, **kwargs):
        calls.append(args)
        raise failure

    monkeypatch.setattr(resources.subprocess, "run", broken)
    monkeypatch.setattr(resources, "_SERVICE_SAMPLE", (0, {"stale": "x"}))
    sample = resources.telemetry(tmp_path / "discovery.service")
    assert calls
    assert sample["systemd"] == {}
    assert sample["pid"] > 0
    # Failure is remembered for the 30 s window, so systemctl is not retried per call.
    resources.telemetry(tmp_path / "discovery.service")
    assert len(calls) == 1


def test_telemetry_reports_systemd_when_available(tmp_path, monkeypatch):
    class Result:
        stdout = "NRestarts=1\nResult=success\n"

    monkeypatch.setattr(resources.subprocess, "run", lambda *a, **k: Result())
    monkeypatch.setattr(resources, "_SERVICE_SAMPLE", (0, {}))
    sample = resources.telemetry(tmp_path / "discovery.service")
    assert sample["systemd"] == {"NRestarts": "1", "Result": "success"}
