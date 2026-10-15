"""Original BTC window, unchanged grid/rounds; cgroup verified before work."""

import argparse
import hashlib
import itertools
import json
import logging
import os
from pathlib import Path
import time
import tracemalloc
import tempfile
import uuid
import copy

import pandas as pd

from app.services import combo_optimizer as opt
from app.services.discovery_resources import admission, telemetry, spool_directory, mark_spool_owner
from tests.fixtures.discovery_memory import semantic_oracle
from app.services import discovery_stream
from app.services.discovery_stream import ResultSpool
from app.services import discovery_supervisor

PRODUCTION_BATCH = opt._worker_run_batch
PRODUCTION_SUPERVISOR = discovery_supervisor._supervisor_entry
PRODUCTION_REPORT = discovery_stream.report


def validation_supervisor(events, acknowledgements, directory, inputs):
    opt._worker_run_batch = verified_batch
    opt.ResultSpool = VerifiedSpool
    manifest = {}
    printed = set()

    def report(event):
        if event.get("stage_id") and event.get("counters"):
            manifest[event["stage_id"]] = event["counters"]
            counters = event["counters"]
            mark = (event["stage_id"], counters["executed"])
            if (
                counters["executed"] % 10000 == 0 or counters["executed"] == counters["planned"]
            ) and mark not in printed:
                printed.add(mark)
                print(
                    "RUN_PROGRESS "
                    + json.dumps(
                        {
                            "run": os.getenv("CARD1093_VALIDATION_RUN"),
                            "stage": event["stage_id"],
                            "counters": counters,
                        }
                    ),
                    flush=True,
                )
        kind = os.getenv("CARD1093_VALIDATION_KIND", "original")
        (EVIDENCE / f"{kind}_progress.json").write_text(
            json.dumps(
                {
                    "run": os.getenv("CARD1093_VALIDATION_RUN"),
                    "stage_manifest": manifest,
                    "latest": event,
                },
                default=str,
                indent=2,
            )
            + "\n"
        )
        PRODUCTION_REPORT(event)

    discovery_stream.report = report
    PRODUCTION_SUPERVISOR(events, acknowledgements, directory, inputs)


def verified_batch(batch):
    rows = PRODUCTION_BATCH(batch)
    intraday = opt._worker_get_15m_cache("BTC/USDT", "2025-10-06", "2026-10-06")
    for args, row in zip(batch, rows):
        expected, _, _ = semantic_oracle.evaluate(args[2], args[1], deep=args[5], intraday=intraday)
        assert row["success"], row
        assert row["metrics"] == expected, (args[1], row["metrics"], expected)
    return rows


class VerifiedSpool(ResultSpool):
    def ranked(self, domain, params, stage, limit):
        result = super().ranked(domain, params, stage, limit)
        # Independent compact global ranking; every trial's metrics were checked
        # against the corrected oracle before entering this spool.
        sharpes, returns = [], []
        for _, row in self.rows(domain):
            sharpes.append(row["metrics"]["sharpe_ratio"])
            returns.append(row["metrics"]["total_return"])
        if not sharpes:
            return result
        lo_s, hi_s = min(sharpes), max(sharpes)
        lo_r, hi_r = min(returns), max(returns)
        width_s, width_r = hi_s - lo_s, hi_r - lo_r
        keys = []
        for index, (s, r) in enumerate(zip(sharpes, returns)):
            ns = (s - lo_s) / width_s if width_s > 0 else 0
            nr = (r - lo_r) / width_r if width_r > 0 else 0
            keys.append(((0.7 * ns) + (0.3 * nr), index))
        keys.sort(key=lambda item: (-item[0], item[1]))
        actual_trials = [row["trial_index"] for row in result]
        trials = [trial for trial, _ in self.rows(domain)]
        assert actual_trials == [trials[index] for _, index in keys[:limit]]
        for row, (score, _) in zip(result, keys[:limit]):
            assert row["score"] == score or (pd.isna(row["score"]) and pd.isna(score))
        print(
            "ORACLE_RANKING_PASS "
            + json.dumps({"domain": domain, "trials": len(keys), "limit": limit}),
            flush=True,
        )
        return result


ROOT = Path(
    "/srv/apps/dev/criptofarol/crypto-worktrees/card-1093-discovery-memory/backend/tests/fixtures/discovery_memory"
)
EVIDENCE = Path(
    "/srv/apps/dev/criptofarol/crypto-worktrees/card-1093-discovery-memory/openspec/changes/card-1093-discovery-memory"
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=int, default=0)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    profile = admission()
    print(
        "VERIFIED_CGROUP " + json.dumps({"profile": profile, "telemetry": telemetry()}), flush=True
    )
    frozen = json.loads((ROOT / "original_template.json").read_text())
    metadata = {
        "name": frozen["name"],
        **frozen["template_data"],
        "optimization_schema": frozen["optimization_schema"],
    }
    manifest = json.loads((ROOT / "original_manifest.json").read_text())
    source = ROOT / "original_candles.parquet"
    assert hashlib.sha256(source.read_bytes()).hexdigest() == manifest["parquet_sha256"]
    frame = pd.read_parquet(source).set_index("timestamp_utc")
    frame = frame.sort_index()
    # Isolated immutable inputs; the child/pool read the same frozen window.
    directory = ROOT / "runtime_inputs"
    directory.mkdir(exist_ok=True)
    for name in ("candles", "intraday"):
        frame.to_parquet(directory / f"{name}.parquet", index=True)
    os.environ["DISCOVERY_FROZEN_INPUT_DIR"] = str(directory)
    optimizer = opt.ComboOptimizer()
    optimizer.combo_service.get_template_metadata = lambda _: metadata
    stages = optimizer.generate_stages(metadata["name"], "BTC/USDT", fixed_timeframe="15m")
    assert optimizer._calculate_grid_size(stages[0]) == 492480
    train, holdout = opt.split_train_holdout(frame, 0.7)
    assert (len(train), len(holdout)) == (24528, 10513)
    if args.sample:
        arguments = itertools.islice(
            optimizer._stage_worker_args(
                stages[0],
                {"direction": "long", "timeframe": "15m"},
                train,
                True,
                "BTC/USDT",
                "2025-10-06",
                "2026-10-06",
                metadata,
            ),
            args.sample,
        )
        started = time.monotonic()
        rows = verified_batch([arg[:9] + (trial,) for trial, arg in enumerate(arguments)])
        assert len(rows) == args.sample and all(row["success"] for row in rows)
        elapsed = time.monotonic() - started
        report = {
            "sample_trials": len(rows),
            "seconds": elapsed,
            "trials_per_second": len(rows) / elapsed,
            "r1_estimate_seconds": 492480 * elapsed / len(rows),
            "telemetry": telemetry(),
        }
        (EVIDENCE / "original_throughput.json").write_text(json.dumps(report, indent=2) + "\n")
        print("THROUGHPUT " + json.dumps(report), flush=True)
        return
    from app.database import SessionLocal
    from app.models_discovery import (
        DiscoverySweep,
        DiscoveryCombination,
        DiscoveryAttempt,
        DiscoveryResult,
    )
    from app.services.discovery_service import DiscoveryService
    from app.services.discovery_recovery import reconcile_expired
    from app.tasks.discovery_tasks import run_combination
    from sqlalchemy import text

    assert "card-1093-integration" in os.environ["DATABASE_URL"], "Private PostgreSQL required"
    kind = "pilot" if args.pilot else "original"
    os.environ["CARD1093_VALIDATION_KIND"] = kind
    if args.pilot:
        metadata = copy.deepcopy(metadata)
        for name, definition in metadata["optimization_schema"]["parameters"].items():
            value = definition["default"]
            definition.update(min=value, max=value, step=1)
            if name in ("rsi_length", "adx_length"):
                definition.update(min=10, max=20, step=10)
    opt.ComboService.get_template_metadata = lambda *_: metadata
    discovery_supervisor._supervisor_entry = validation_supervisor
    reports = []
    source_root = ROOT.parents[3]
    code_paths = [
        source_root / "backend/app/services/combo_optimizer.py",
        source_root / "backend/app/services/combo_service.py",
        source_root / "backend/app/strategies/combos/combo_strategy.py",
        source_root / "backend/app/strategies/combos/indicator_binding.py",
        source_root / "backend/app/tasks/discovery_tasks.py",
    ]
    code_paths += sorted((source_root / "backend/app/services").glob("discovery_*.py"))
    code_paths += [ROOT / "semantic_oracle.py", ROOT / "position_reference.py", Path(__file__)]
    runtime_manifest = {
        "profile": profile,
        "candle_manifest": manifest,
        "golden_sha256": hashlib.sha256((ROOT / "semantic_goldens.json").read_bytes()).hexdigest(),
        "code": {
            str(path.relative_to(source_root)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in code_paths
        },
    }
    (EVIDENCE / f"{kind}_runtime_manifest.json").write_text(
        json.dumps(runtime_manifest, indent=2) + "\n"
    )
    with SessionLocal() as db:
        # The earlier isolated schema was created before the SHA field widened.
        db.execute(
            text("ALTER TABLE discovery_results ALTER COLUMN candle_version TYPE varchar(64)")
        )
        db.commit()
    for run in range(args.runs):
        os.environ["CARD1093_VALIDATION_RUN"] = str(run + 1)
        input_directory = Path(tempfile.mkdtemp(prefix="inputs-", dir=spool_directory()))
        mark_spool_owner(input_directory)
        candle_manifest = {"directory": str(input_directory), "files": {}}
        for name in ("candles", "intraday"):
            target = input_directory / f"{name}.parquet"
            frame.to_parquet(target, index=True)
            target.chmod(0o600)
            candle_manifest["files"][name] = {
                "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
                "rows": len(frame),
            }
        sweep_id = uuid.uuid4().hex
        with SessionLocal() as db:
            snapshot = {"start_date": "2025-10-06", "end_date": "2026-10-06"}
            db.add(
                DiscoverySweep(
                    id=sweep_id,
                    actor="card1093-isolated",
                    state="running",
                    total=1,
                    idempotency_key=sweep_id,
                    payload_hash=manifest["candle_values_sha256"],
                    snapshot_token=sweep_id,
                    snapshot_hash=manifest["candle_values_sha256"],
                    snapshot=snapshot,
                )
            )
            db.flush()
            db.add(
                DiscoveryCombination(
                    sweep_id=sweep_id,
                    template_id=metadata["name"],
                    symbol="BTC/USDT",
                    timeframe="15m",
                    direction="long",
                    input_snapshot={
                        "snapshot": snapshot,
                        **snapshot,
                        "template_metadata": metadata,
                        "candle_manifest": candle_manifest,
                    },
                )
            )
            db.commit()
            claimed = DiscoveryService().claim_combinations(sweep_id, "original-harness", db=db)
            assert len(claimed) == 1
            combination_id = claimed[0].id
        started = time.monotonic()
        print(
            "RUN_STARTED "
            + json.dumps(
                {"kind": kind, "run": run + 1, "sweep": sweep_id, "combination": combination_id}
            ),
            flush=True,
        )
        with SessionLocal() as db:
            combination = db.get(DiscoveryCombination, combination_id)
            run_combination(db, combination, combination.lease_owner)
        with SessionLocal() as db:
            reconcile_expired(db, sweep_id)
            row = db.get(DiscoveryCombination, combination_id)
            attempt = db.get(DiscoveryAttempt, (combination_id, 1))
            assert row.state in ("succeeded", "insufficient_sample"), (
                row.state,
                row.last_failure_code,
            )
            assert row.attempts == 1 and attempt.state == "succeeded"
            stage_manifest = {
                key: value
                for key, value in attempt.counters.items()
                if not key.startswith("phase:") and key != "failure_outcomes"
            }
            result = db.get(DiscoveryResult, row.result_id)
            result_payload = {
                "parameters": result.parameters,
                "metrics": result.metrics,
                "eligibility": result.eligibility,
                "candle_version": result.candle_version,
                "evidence_fingerprint": result.evidence_fingerprint,
            }
        report = {
            "run": run + 1,
            "seconds": time.monotonic() - started,
            "telemetry": telemetry(),
            "cache_bytes": opt.BUDGET.bytes,
            "sweep": sweep_id,
            "stage_manifest": stage_manifest.copy(),
            "result": result_payload,
        }
        assert stage_manifest and all(
            c["executed"] == c["planned"]
            and not c["unknown"]
            and not c["remaining"]
            and not c["failed"]
            for c in stage_manifest.values()
        )
        reports.append(report)
        (EVIDENCE / f"{kind}_run_{run+1}.json").write_text(
            json.dumps(report, default=str, indent=2) + "\n"
        )
        print(
            "RUN_COMPLETE " + json.dumps({k: v for k, v in report.items() if k != "result"}),
            flush=True,
        )
    assert all(item["cache_bytes"] == 0 for item in reports)
    if len(reports) >= 3:
        assert (
            reports[2]["telemetry"]["rss_bytes"] - reports[0]["telemetry"]["rss_bytes"]
            <= 128 * 1024**2
        )


if __name__ == "__main__":
    main()
