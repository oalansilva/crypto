"""Durable attempt budget, PostgreSQL-time fencing, heartbeat and external repair."""

from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
import logging
import os
import uuid

from sqlalchemy import func, or_
from app.models_discovery import (
    DiscoveryAttempt,
    DiscoveryCombination,
    DiscoveryCircuit,
    DiscoverySweep,
    DiscoveryResult,
)
from app.services.discovery_resources import (
    ResourceProfile,
    OperationalFailure,
    discovery_environment,
)

logger = logging.getLogger(__name__)
MAX_ATTEMPTS = 3
TTL = 300
HEARTBEAT = 30
BACKOFF = (60, 300)
TERMINAL = {"cancelled", "completed", "failed", "partial_failure"}


def now(db):
    stamp = db.query(func.clock_timestamp()).scalar()
    return stamp.replace(tzinfo=None)


def environment():
    return discovery_environment()


@dataclass(frozen=True)
class Possession:
    sweep_id: str
    combination_id: int
    owner: str
    attempt_seq: int
    generation: int

    @classmethod
    def of(cls, row):
        return cls(row.sweep_id, row.id, row.lease_owner, row.attempts, row.lease_generation)


class LostPossession(OperationalFailure):
    def __init__(self):
        super().__init__("lost_possession")


def locked_possession(db, token):
    sweep = (
        db.query(DiscoverySweep)
        .filter_by(id=token.sweep_id)
        .populate_existing()
        .with_for_update()
        .first()
    )
    row = (
        db.query(DiscoveryCombination)
        .filter_by(id=token.combination_id)
        .populate_existing()
        .with_for_update()
        .first()
    )
    stamp = now(db)
    if (
        sweep is None
        or sweep.state in TERMINAL
        or row is None
        or row.state != "running"
        or row.lease_owner != token.owner
        or row.attempts != token.attempt_seq
        or row.lease_generation != token.generation
        or row.lease_expires_at is None
        or row.lease_expires_at.replace(tzinfo=None) <= stamp
    ):
        raise LostPossession()
    return sweep, row, stamp


def circuit(db, stamp=None):
    env = environment()
    # Serialize first row creation and updates even across different sweeps.
    db.execute(
        __import__("sqlalchemy").text("SELECT pg_advisory_xact_lock(hashtext(:key))"),
        {"key": "discovery-circuit:" + env},
    )
    row = db.query(DiscoveryCircuit).filter_by(environment=env).with_for_update().first()
    if row is None:
        row = DiscoveryCircuit(environment=env, failures=[], acknowledgements=[])
        db.add(row)
        db.flush()
    return row


def claim_attempt(db, sweep, row, stamp):
    if row.attempts >= MAX_ATTEMPTS or (row.next_attempt_at and row.next_attempt_at > stamp):
        return False
    gate = circuit(db)
    if gate.opened_at:
        logger.error("resource_intervention_required environment=%s", gate.environment)
        return False
    row.attempts += 1
    row.lease_generation = (row.lease_generation or 0) + 1
    row.lease_owner = uuid.uuid4().hex
    row.lease_expires_at = stamp + timedelta(seconds=TTL)
    row.heartbeat_at = row.progress_at = stamp
    row.next_attempt_at = None
    row.state = "running"
    row.updated_at = stamp
    if row.input_snapshot is None:
        from app.tasks.discovery_tasks import resolve_optimizer_date_range

        start, end = resolve_optimizer_date_range(
            sweep.snapshot or {}, stamp.replace(tzinfo=timezone.utc)
        )
        start = start or "2017-01-01"
        end = end or stamp.date().isoformat()
        from app.services.combo_service import ComboService

        row.input_snapshot = {
            "snapshot": sweep.snapshot,
            "start_date": start,
            "end_date": end,
            "template_metadata": ComboService().get_template_metadata(row.template_id),
        }
    db.add(
        DiscoveryAttempt(
            combination_id=row.id,
            attempt_seq=row.attempts,
            owner=row.lease_owner,
            generation=row.lease_generation,
            state="running",
            started_at=stamp,
            heartbeat_at=stamp,
            progress_at=stamp,
            profile=asdict(ResourceProfile.configured()),
            counters={},
        )
    )
    return True


def heartbeat(db, token, events=(), supervisor=None):
    _, row, stamp = locked_possession(db, token)
    attempt = db.get(DiscoveryAttempt, (row.id, row.attempts))
    counts = dict(attempt.counters or {})
    progressed = False
    for event in events:
        if event.get("candle_manifest"):
            current_snapshot = dict(row.input_snapshot or {})
            if current_snapshot.get("candle_manifest") not in (None, event["candle_manifest"]):
                raise OperationalFailure("frozen_input_identity_changed")
            current_snapshot["candle_manifest"] = event["candle_manifest"]
            row.input_snapshot = current_snapshot
        key = event.get("stage_id")
        if key and "counters" in event:
            current = event["counters"]
            old = counts.get(key, {})
            if (
                current["executed"] != current["succeeded"] + current["failed"]
                or current["planned"]
                != current["executed"] + current["unknown"] + current["remaining"]
                or any(value < 0 for value in current.values())
                or current["executed"] < old.get("executed", 0)
            ):
                raise OperationalFailure("invalid_progress_counters")
            if current["executed"] > old.get("executed", 0):
                progressed = True
            counts[key] = current
        phase = event.get("phase_complete")
        if phase and "phase:" + phase not in counts:
            progressed = True
            counts["phase:" + phase] = {"completed_at": stamp.isoformat()}
        if event.get("telemetry") or event.get("worker_telemetry"):
            measured = {
                key: event[key] for key in ("telemetry", "worker_telemetry") if event.get(key)
            }
            attempt.profile = {**dict(attempt.profile), **measured}
    if progressed:
        row.progress_at = attempt.progress_at = stamp
    attempt.counters = counts
    row.heartbeat_at = attempt.heartbeat_at = stamp
    row.lease_expires_at = stamp + timedelta(seconds=TTL)
    if supervisor:
        attempt.supervisor_pid, attempt.supervisor_start = supervisor
    age = (stamp - row.progress_at).total_seconds()
    if age >= 120:
        logger.warning("discovery_no_progress age=%s attempt=%s", age, token)
    if age >= 600:
        raise OperationalFailure("progress_timeout", counts)
    db.commit()
    return counts


def settled(db, row, state):
    attempt = db.get(DiscoveryAttempt, (row.id, row.attempts))
    if attempt:
        attempt.state = state
        attempt.finished_at = now(db)
    row.lease_owner = None
    row.lease_expires_at = None


def failed_locked(db, sweep, row, code, operational=True, stamp=None):
    stamp = stamp or now(db)
    attempt = db.get(DiscoveryAttempt, (row.id, row.attempts))
    if attempt:
        attempt.state = "failed"
        attempt.finished_at = stamp
        attempt.failure_code = code
        counts = dict(attempt.counters or {})
        attempt.counters = counts
    row.last_failure_code = code
    row.lease_generation = (row.lease_generation or 0) + 1
    row.lease_owner = row.lease_expires_at = None
    row.updated_at = stamp
    if operational:
        gate = circuit(db)
        cutoff = (stamp - timedelta(seconds=900)).isoformat()
        history = [item for item in (gate.failures or []) if item["at"] >= cutoff]
        history.append(
            {"at": stamp.isoformat(), "combination": row.id, "attempt": row.attempts, "code": code}
        )
        gate.failures = history
        if len(history) >= 3:
            gate.opened_at = gate.opened_at or stamp
            logger.error(
                "resource_intervention_required environment=%s failures=%s",
                gate.environment,
                len(history),
            )
    if (
        operational
        and row.attempts < MAX_ATTEMPTS
        and sweep.state not in TERMINAL
        and sweep.state != "cancelling"
    ):
        row.state = "pending"
        row.next_attempt_at = stamp + timedelta(seconds=BACKOFF[max(0, row.attempts - 1)])
    else:
        row.state = "failed"
        if (
            operational
            and row.attempts >= MAX_ATTEMPTS
            and sweep.state not in TERMINAL
            and sweep.state != "cancelling"
        ):
            sweep.state = "failed"
            sweep.terminal_reason = "operational_failure"
            sweep.terminal_code = "resource_recovery_exhausted"
            sweep.completed_at = stamp
            logger.error(
                "Recuperação automática esgotada após 3 tentativas. Intervenção necessária; revise os recursos antes de iniciar nova busca."
            )


def fail(db, token, code, operational=True, counters=None):
    sweep, row, stamp = locked_possession(db, token)
    if counters:
        attempt = db.get(DiscoveryAttempt, (row.id, row.attempts))
        attempt.counters = {**dict(attempt.counters or {}), "failure_outcomes": counters}
    failed_locked(db, sweep, row, code, operational, stamp)
    from app.tasks.discovery_tasks import _reconcile_locked

    _reconcile_locked(sweep, db)
    db.commit()


def reconcile_expired(db, sweep_id=None, commit=True):
    """Called outside the Discovery cgroup; lock order matches all writers."""
    stamp = now(db)
    from app.services.discovery_resources import cleanup_orphan_spools

    cleanup_orphan_spools()
    from app.services.discovery_inputs import cleanup_unreferenced

    # Só o manifesto interessa (não o input_snapshot inteiro com os candles).
    snapshot = DiscoveryCombination.input_snapshot
    manifest_column = snapshot["candle_manifest"]
    manifests = [
        (owner, combination, manifest, cleaned)
        for owner, combination, manifest, cleaned in db.query(
            DiscoveryCombination.sweep_id,
            DiscoveryCombination.id,
            manifest_column,
            snapshot["inputs_cleaned"],
        ).filter(snapshot.isnot(None))
        if manifest
    ]
    cleanup_unreferenced(manifest for _, _, manifest, _ in manifests)
    # Sweeps terminais limpos não são travados nem reescritos a cada poll: só
    # entram os não terminais, com combinação running/pending ou com manifesto
    # ainda não limpo. Chamada explícita por sweep_id sempre reconcilia esse sweep.
    uncleaned = {}
    for owner, combination, _, cleaned in manifests:
        if not cleaned:
            uncleaned.setdefault(owner, []).append(combination)
    query = db.query(DiscoverySweep)
    if sweep_id:
        query = query.filter_by(id=sweep_id)
    else:
        active = (
            db.query(DiscoveryCombination.id)
            .filter(
                DiscoveryCombination.sweep_id == DiscoverySweep.id,
                DiscoveryCombination.state.in_(("running", "pending")),
            )
            .exists()
        )
        query = query.filter(
            or_(
                DiscoverySweep.state.notin_(tuple(TERMINAL)),
                active,
                DiscoverySweep.id.in_(list(uncleaned)),
            )
        )
    repaired = 0
    from app.services.discovery_service import DiscoveryService
    from app.tasks.discovery_tasks import _reconcile_locked

    for (sweep_id,) in query.with_entities(DiscoverySweep.id).all():
        sweep = (
            db.query(DiscoverySweep)
            .filter_by(id=sweep_id)
            .populate_existing()
            .with_for_update()
            .first()
        )
        rows = (
            db.query(DiscoveryCombination)
            .filter(
                DiscoveryCombination.sweep_id == sweep_id,
                DiscoveryCombination.state == "running",
                DiscoveryCombination.lease_expires_at <= stamp,
            )
            .populate_existing()
            .with_for_update()
            .all()
        )
        for row in rows:
            attempt = db.get(DiscoveryAttempt, (row.id, row.attempts))
            if attempt and attempt.supervisor_pid:
                from app.services.discovery_supervisor import cleanup_recorded_group

                cleanup_recorded_group(attempt.supervisor_pid, attempt.supervisor_start)
            result = db.query(DiscoveryResult).filter_by(combination_id=row.id).first()
            if result:
                row.result_id = result.id
                row.state = (
                    "insufficient_sample"
                    if result.eligibility == "insufficient_sample"
                    else "succeeded"
                )
                settled(db, row, "succeeded")
            elif sweep.state in TERMINAL or sweep.state == "cancelling":
                row.state = "skipped"
                settled(db, row, "interrupted")
                row.lease_generation = (row.lease_generation or 0) + 1
            else:
                failed_locked(db, sweep, row, "lease_interrupted", stamp=stamp)
            repaired += 1
        # Also reconcile migrated exhausted rows and terminal residuals at startup.
        _reconcile_locked(sweep, db)
        if commit:
            # Snapshot bytes survive retries/pause; terminal inputs are discarded
            # under the same sweep lock, preserving the manifest for audit.
            settled_rows = (
                db.query(DiscoveryCombination)
                .filter(
                    DiscoveryCombination.sweep_id == sweep_id,
                    DiscoveryCombination.id.in_(uncleaned.get(sweep_id, [])),
                    DiscoveryCombination.state.notin_(("running", "pending")),
                )
                .populate_existing()
                .all()
            )
            for row in settled_rows:
                snapshot = row.input_snapshot or {}
                manifest = snapshot.get("candle_manifest")
                if manifest and not snapshot.get("inputs_cleaned"):
                    from app.services.discovery_inputs import discard

                    directory = __import__("pathlib").Path(manifest["directory"])
                    if directory.exists():
                        discard(manifest)
                    row.input_snapshot = {**snapshot, "inputs_cleaned": True}
        if sweep.state == "running":
            DiscoveryService().ensure_sweep_wakeup(db, sweep_id, sweep=sweep)
        if commit:
            db.commit()
        else:
            db.flush()
    return repaired


def acknowledge(db, actor, reason, healthy, groups_empty):
    if not actor or not reason or not healthy or not groups_empty:
        raise OperationalFailure("resource_intervention_unverified")
    if db.query(DiscoveryCombination).filter_by(state="running").count():
        raise OperationalFailure("active_leases")
    gate = circuit(db)
    stamp = now(db)
    gate.acknowledgements = list(gate.acknowledgements or []) + [
        {"actor": actor, "reason": reason, "at": stamp.isoformat()}
    ]
    gate.acknowledged_at = stamp
    gate.opened_at = None
    gate.failures = []
    db.commit()
