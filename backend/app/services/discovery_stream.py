"""Bounded trial admission, honest counters and exact two-pass global scoring."""

from __future__ import annotations

from concurrent.futures import wait, FIRST_COMPLETED
from dataclasses import dataclass, asdict
from pathlib import Path
import itertools
import logging
import math
import pickle
import sqlite3
import tempfile
import uuid

from app.services.discovery_resources import (
    ResourceProfile,
    OperationalFailure,
    CalculationFailure,
    spool_directory,
    mark_spool_owner,
    auxiliary_spool_bytes,
)

PROGRESS_CALLBACK = None


def report(event):
    logging.getLogger(__name__).info("Discovery progress %s", event)
    if PROGRESS_CALLBACK is not None:
        PROGRESS_CALLBACK(event)


@dataclass
class Counters:
    planned: int
    executed: int = 0
    succeeded: int = 0
    failed: int = 0
    unknown: int = 0
    remaining: int = 0

    def snapshot(self, submitted):
        self.unknown = submitted - self.executed
        self.remaining = self.planned - submitted
        assert self.executed == self.succeeded + self.failed
        assert self.planned == self.executed + self.unknown + self.remaining
        return asdict(self)


class ResultSpool:
    """Private on-disk rows; SQLite cache bounded and floats pickled losslessly."""

    def __init__(self, profile=None, root=None):
        self.profile = profile or ResourceProfile.configured()
        self.directory = tempfile.TemporaryDirectory(
            prefix="attempt-", dir=root or spool_directory()
        )
        mark_spool_owner(self.directory.name)
        self.path = Path(self.directory.name) / "results.sqlite"
        self.db = sqlite3.connect(self.path)
        self.path.chmod(0o600)
        self.db.execute("PRAGMA journal_mode=OFF")
        self.db.execute("PRAGMA cache_size=-8192")
        self.db.execute("PRAGMA temp_store=FILE")
        page_size = self.db.execute("PRAGMA page_size").fetchone()[0]
        available = self.profile.spool_bytes - auxiliary_spool_bytes() - page_size
        self.db.execute(f"PRAGMA max_page_count={max(1, available // page_size)}")
        try:
            self.db.execute(
                "CREATE TABLE rows (domain INTEGER, trial INTEGER, payload BLOB, score REAL, PRIMARY KEY(domain, trial))"
            )
            self.db.execute("CREATE INDEX ranking_order ON rows (domain, score DESC, trial ASC)")
        except sqlite3.Error as exc:
            self.db.close()
            self.directory.cleanup()
            raise OperationalFailure("spool_quota_or_io_error") from exc
        self.payload_bytes = 0
        self.count = 0

    def quota(self):
        self.db.commit()
        actual = (
            sum(p.stat().st_size for p in Path(self.directory.name).iterdir() if p.is_file())
            + auxiliary_spool_bytes()
        )
        if actual > self.profile.spool_bytes:
            raise OperationalFailure("spool_quota_exceeded")
        return actual

    def add(self, domain, row):
        data = pickle.dumps(row, protocol=5)
        if (
            len(data) > self.profile.retention_bytes
            or self.payload_bytes + len(data) > self.profile.spool_bytes
        ):
            raise OperationalFailure("spool_quota_exceeded")
        self.db.execute(
            "INSERT INTO rows VALUES (?, ?, ?, NULL)", (domain, row["trial_index"], data)
        )
        self.payload_bytes += len(data)
        self.count += 1

    def rows(self, domain):
        for trial, data in self.db.execute(
            "SELECT trial, payload FROM rows WHERE domain=? ORDER BY trial", (domain,)
        ):
            yield trial, pickle.loads(data)

    def ranked(self, domain, params, stage, limit):
        # Python min/max, in original trial order, including NaN/inf semantics.
        first = True
        for _, row in self.rows(domain):
            s, r = row["metrics"]["sharpe_ratio"], row["metrics"]["total_return"]
            if first:
                min_s = max_s = s
                min_r = max_r = r
                first = False
            else:
                if s < min_s:
                    min_s = s
                if s > max_s:
                    max_s = s
                if r < min_r:
                    min_r = r
                if r > max_r:
                    max_r = r
        if first:
            return []
        range_s, range_r = max_s - min_s, max_r - min_r
        nonfinite = False
        for trial, row in self.rows(domain):
            s, r = row["metrics"]["sharpe_ratio"], row["metrics"]["total_return"]
            ns = (s - min_s) / range_s if range_s > 0 else 0
            nr = (r - min_r) / range_r if range_r > 0 else 0
            score = (0.7 * ns) + (0.3 * nr)
            nonfinite |= not math.isfinite(score)
            self.db.execute(
                "UPDATE rows SET score=? WHERE domain=? AND trial=?", (score, domain, trial)
            )
        self.quota()
        if nonfinite:
            # NaN comparison is non-transitive: preserve CPython's sort exactly.
            # Only compact keys are retained; full result objects stay on disk.
            count = self.db.execute(
                "SELECT count(*) FROM rows WHERE domain=?", (domain,)
            ).fetchone()[0]
            if count * 192 > self.profile.retention_bytes - 16 * 1024**2:
                raise OperationalFailure("ranking_retention_exceeded")
            keys = []
            for trial, row in self.rows(domain):
                s, r = row["metrics"]["sharpe_ratio"], row["metrics"]["total_return"]
                ns = (s - min_s) / range_s if range_s > 0 else 0
                nr = (r - min_r) / range_r if range_r > 0 else 0
                keys.append(((0.7 * ns) + (0.3 * nr), trial))
            keys.sort(key=lambda x: (-x[0], x[1]))
            chosen = keys[:limit]
        else:
            chosen = self.db.execute(
                "SELECT score,trial FROM rows WHERE domain=? ORDER BY score DESC, trial ASC LIMIT ?",
                (domain, limit),
            ).fetchall()
        results = []
        for score, trial in chosen:
            row = pickle.loads(
                self.db.execute(
                    "SELECT payload FROM rows WHERE domain=? AND trial=?", (domain, trial)
                ).fetchone()[0]
            )
            result_params = params.copy()
            if stage.get("grid_mode", False):
                result_params.update(row["value"])
            else:
                result_params[stage["parameter"]] = row["value"]
            results.append(
                {
                    "params": result_params,
                    "metrics": row["metrics"],
                    "score": score,
                    "trial_index": trial,
                }
            )
            from app.services.discovery_budget_cache import retained

            if retained(results) > self.profile.retention_bytes:
                raise OperationalFailure("ranking_retention_exceeded")
        return results

    def close(self):
        self.db.close()
        self.directory.cleanup()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def batches(arguments, profile):
    """Incremental memoized size estimate; exact measurement before admission.

    Do not serialize the entire shared DataFrame for every prefix of a batch.
    The estimate only decides when to flush; the emitted batch's exact pickle
    length is authoritative, with stable splitting at a byte boundary.
    """

    class Counter:
        size = 0

        def write(self, value):
            self.size += memoryview(value).nbytes

    def measured(items):
        size = len(pickle.dumps(items, protocol=5))
        if size <= profile.pending_bytes:
            yield items, size
        elif len(items) == 1:
            raise OperationalFailure("pending_bytes_exceeded")
        else:
            midpoint = len(items) // 2
            yield from measured(items[:midpoint])
            yield from measured(items[midpoint:])

    batch = []
    counter = Counter()
    pickler = pickle.Pickler(counter, protocol=5)
    for args in arguments:
        pickler.dump(args)
        batch.append(args)
        if len(batch) == profile.batch_size or counter.size * 2 >= profile.pending_bytes:
            yield from measured(batch)
            batch = []
            counter = Counter()
            pickler = pickle.Pickler(counter, protocol=5)
    if batch:
        yield from measured(batch)


def execute_stream(executor, worker, arguments_factory, planned, spool, profile=None):
    """Consume at most 2W futures/64MiB; every row has one confirmed outcome."""
    profile = profile or ResourceProfile.configured()
    counters = Counters(planned)
    stage_id = uuid.uuid4().hex
    submitted = 0
    pending = {}
    pending_bytes = 0
    iterator = iter(batches(arguments_factory(), profile))
    next_batch = None
    exhausted = False
    window = 2 * profile.effective_workers
    try:
        while pending or not exhausted or next_batch is not None:
            while len(pending) < window and not exhausted:
                if next_batch is None:
                    try:
                        next_batch = next(iterator)
                    except StopIteration:
                        exhausted = True
                        break
                batch, size = next_batch
                if pending_bytes + size > profile.pending_bytes:
                    break
                # Persist admission intent before dispatch; unconfirmed work is unknown.
                submitted += len(batch)
                report(
                    {
                        "stage_id": stage_id,
                        "counters": counters.snapshot(submitted),
                        "pending_futures": len(pending) + 1,
                        "pending_bytes": pending_bytes + size,
                    }
                )
                future = executor.submit(worker, batch)
                pending[future] = (
                    [(arg[10] if len(arg) > 10 else 0, arg[9]) for arg in batch],
                    size,
                )
                pending_bytes += size
                next_batch = None
            if not pending:
                if next_batch is not None:
                    raise OperationalFailure("pending_bytes_exceeded")
                continue
            done, _ = wait(pending, return_when=FIRST_COMPLETED)
            for future in done:
                expected, size = pending.pop(future)
                pending_bytes -= size
                rows = future.result()
                if len(rows) != len(expected) or [r.get("trial_index") for r in rows] != [
                    trial for _, trial in expected
                ]:
                    raise OperationalFailure("incomplete_batch")
                for (domain, _), row in zip(expected, rows):
                    counters.executed += 1
                    if row.get("success"):
                        counters.succeeded += 1
                        spool.add(domain, row)
                    else:
                        counters.failed += 1
                event = {
                    "stage_id": stage_id,
                    "counters": counters.snapshot(submitted),
                    "pending_futures": len(pending),
                    "pending_bytes": pending_bytes,
                    "spool_bytes": spool.quota(),
                }
                if rows and rows[0].get("worker_telemetry"):
                    event["worker_telemetry"] = rows[0]["worker_telemetry"]
                report(event)
                if counters.failed:
                    raise CalculationFailure("calculation_error", counters.snapshot(submitted))
        final = counters.snapshot(submitted)
        if (
            counters.executed != planned
            or counters.failed
            or counters.unknown
            or counters.remaining
        ):
            raise OperationalFailure("incomplete_stage", final)
        return final
    except BaseException as exc:
        for future in pending:
            future.cancel()
        snapshot = counters.snapshot(submitted)
        report(
            {
                "stage_id": stage_id,
                "counters": snapshot,
                "failure": getattr(exc, "code", type(exc).__name__),
            }
        )
        if isinstance(exc, OperationalFailure):
            exc.counters = snapshot
            raise
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        raise OperationalFailure("pool_or_spool_failure", snapshot) from exc
