"""Real isolated PostgreSQL claims, durable recovery and fencing (#1093)."""

from datetime import timedelta
import uuid
from concurrent.futures import ThreadPoolExecutor
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

from database_guard import assert_safe_test_database_url
from app.models_discovery import (
    DiscoverySweep,
    DiscoveryCombination,
    DiscoveryAttempt,
    DiscoveryCircuit,
    DiscoveryResult,
    DiscoveryOutbox,
)
from app.services.discovery_service import DiscoveryService
from app.services import discovery_recovery as recovery
from app.services.discovery_resources import OperationalFailure


@pytest.fixture
def sessions(monkeypatch):
    url = os.environ["DATABASE_URL"]
    assert_safe_test_database_url(url, variable_name="DATABASE_URL", allow_github_disposable=True)
    assert "card-1093-integration" in url or os.getenv("GITHUB_ACTIONS") == "true"
    engine = create_engine(url)
    for model in (
        DiscoverySweep,
        DiscoveryCombination,
        DiscoveryAttempt,
        DiscoveryCircuit,
        DiscoveryResult,
        DiscoveryOutbox,
    ):
        model.__table__.create(engine, checkfirst=True)
    with engine.begin() as conn:
        conn.execute(
            text(
                "TRUNCATE discovery_attempts, discovery_resource_circuits, discovery_outbox, discovery_results, discovery_combinations, discovery_sweeps"
            )
        )
    monkeypatch.setattr(
        "app.services.combo_service.ComboService.get_template_metadata",
        lambda *_: {"name": "frozen", "indicators": []},
    )
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    yield factory
    engine.dispose()


def seed(sessions, count=2):
    with sessions() as db:
        sweep = DiscoverySweep(
            id=uuid.uuid4().hex,
            actor="test",
            state="running",
            idempotency_key=uuid.uuid4().hex,
            payload_hash="hash",
            snapshot_token="token",
            snapshot_hash="hash",
            total=count,
            snapshot={"start_date": "2025-10-06", "end_date": "2026-10-06"},
        )
        db.add(sweep)
        db.flush()
        for i in range(count):
            db.add(
                DiscoveryCombination(
                    sweep_id=sweep.id,
                    template_id="frozen",
                    symbol=f"X{i}",
                    timeframe="1d",
                    direction="long",
                )
            )
        db.commit()
        return sweep.id


def claim(sessions, sweep):
    with sessions() as db:
        rows = DiscoveryService().claim_combinations(sweep, "caller", limit=20, db=db)
        return recovery.Possession.of(rows[0]) if rows else None


def due(sessions, token):
    with sessions() as db:
        row = db.get(DiscoveryCombination, token.combination_id)
        row.next_attempt_at = recovery.now(db) - timedelta(seconds=1)
        db.commit()


def test_claim_once_before_spawn_redelivery_does_not_consume_slot(sessions):
    sweep = seed(sessions)
    with ThreadPoolExecutor(2) as pool:
        claims = list(pool.map(lambda _: claim(sessions, sweep), range(2)))
    assert sum(c is not None for c in claims) == 1
    token = next(c for c in claims if c)
    assert claim(sessions, sweep) is None
    with sessions() as db:
        row = db.get(DiscoveryCombination, token.combination_id)
        assert row.attempts == 1
        attempt = db.get(DiscoveryAttempt, (row.id, 1))
        assert attempt.owner == token.owner
        assert attempt.started_at is not None
        assert row.input_snapshot["start_date"] == "2025-10-06"
        assert row.input_snapshot["template_metadata"]["name"] == "frozen"


def test_three_attempts_backoff_exhaustion_terminal_and_counter_recount(sessions):
    sweep = seed(sessions, 1)
    old = None
    for seq, delay in ((1, 60), (2, 300), (3, None)):
        token = claim(sessions, sweep)
        assert token.attempt_seq == seq
        if old:
            with sessions() as db, pytest.raises(recovery.LostPossession):
                recovery.heartbeat(db, old)
        with sessions() as db:
            if seq == 3:
                db.add(
                    DiscoveryCombination(
                        sweep_id=sweep,
                        template_id="frozen",
                        symbol="unstarted",
                        timeframe="1d",
                        direction="long",
                    )
                )
                db.get(DiscoverySweep, sweep).total = 2
                db.commit()
            recovery.fail(db, token, "pool_lost")
        with sessions() as db:
            row = db.get(DiscoveryCombination, token.combination_id)
            if delay:
                assert (row.next_attempt_at - row.updated_at).total_seconds() == delay
                assert row.attempts == seq
                assert row.state == "pending"
            else:
                terminal = db.get(DiscoverySweep, sweep)
                assert terminal.state == "failed"
                assert terminal.terminal_code == "resource_recovery_exhausted"
                assert terminal.processed == terminal.total == 2
                assert terminal.failed == 1 and terminal.skipped == 1
                assert len(db.query(DiscoveryAttempt).all()) == 3
        if delay:
            assert claim(sessions, sweep) is None
            due(sessions, token)
        old = token
    assert claim(sessions, sweep) is None


def test_expiration_external_repair_then_old_writer_is_rejected(sessions):
    sweep = seed(sessions, 1)
    token = claim(sessions, sweep)
    with sessions() as db:
        row = db.get(DiscoveryCombination, token.combination_id)
        row.lease_expires_at = recovery.now(db) - timedelta(seconds=1)
        db.commit()
    with sessions() as db:
        assert recovery.reconcile_expired(db, sweep) == 1
    with sessions() as db:
        row = db.get(DiscoveryCombination, token.combination_id)
        assert row.attempts == 1 and row.state == "pending"
        assert row.last_failure_code == "lease_interrupted"
        assert row.next_attempt_at is not None
    with sessions() as db, pytest.raises(recovery.LostPossession):
        recovery.fail(db, token, "late_success")
    assert claim(sessions, sweep) is None
    due(sessions, token)
    assert claim(sessions, sweep).attempt_seq == 2


def test_heartbeat_long_step_separates_alive_from_progress_and_timeout(sessions):
    sweep = seed(sessions)
    token = claim(sessions, sweep)
    with sessions() as db:
        attempt = db.get(DiscoveryAttempt, (token.combination_id, 1))
        attempt.started_at -= timedelta(minutes=31)
        db.commit()
    for executed in range(1, 8):
        with sessions() as db:
            recovery.heartbeat(
                db,
                token,
                [
                    {
                        "stage_id": "r1",
                        "counters": dict(
                            planned=10,
                            executed=executed,
                            succeeded=executed,
                            failed=0,
                            unknown=1,
                            remaining=9 - executed,
                        ),
                    }
                ],
            )
    assert claim(sessions, sweep) is None
    with sessions() as db:
        row = db.get(DiscoveryCombination, token.combination_id)
        row.progress_at = recovery.now(db) - timedelta(seconds=601)
        db.commit()
    with sessions() as db, pytest.raises(OperationalFailure, match="progress_timeout"):
        recovery.heartbeat(db, token)


@pytest.mark.parametrize("parent_state", ["paused", "cancelling", "cancelled"])
def test_parent_barrier_preserves_pause_cancel_and_never_restarts(sessions, parent_state):
    sweep = seed(sessions)
    token = claim(sessions, sweep)
    with sessions() as db:
        parent = db.get(DiscoverySweep, sweep)
        parent.state = parent_state
        row = db.get(DiscoveryCombination, token.combination_id)
        row.lease_expires_at = recovery.now(db) - timedelta(seconds=1)
        db.commit()
    with sessions() as db:
        recovery.reconcile_expired(db, sweep)
    assert claim(sessions, sweep) is None
    with sessions() as db:
        parent = db.get(DiscoverySweep, sweep)
        if parent_state == "paused":
            assert parent.state == "paused"
        else:
            assert parent.state == "cancelled" and parent.processed == parent.total


def test_deterministic_failure_has_no_operational_retry(sessions):
    sweep = seed(sessions, 1)
    token = claim(sessions, sweep)
    with sessions() as db:
        recovery.fail(db, token, "calculation_error", operational=False)
    assert claim(sessions, sweep) is None
    with sessions() as db:
        row = db.get(DiscoveryCombination, token.combination_id)
        assert row.attempts == 1 and row.state == "failed"
        assert db.query(DiscoveryCircuit).one().failures == []


def test_circuit_spans_sweeps_and_acknowledgement_does_not_reset_attempts(sessions):
    ids = []
    for _ in range(3):
        sweep = seed(sessions, 1)
        token = claim(sessions, sweep)
        ids.append(token)
        with sessions() as db:
            recovery.fail(db, token, "supervisor_lost")
    assert claim(sessions, seed(sessions, 1)) is None
    with sessions() as db, pytest.raises(OperationalFailure):
        recovery.acknowledge(db, "operator", "checked", healthy=False, groups_empty=True)
    with sessions() as db:
        recovery.acknowledge(
            db, "operator", "isolated checks healthy", healthy=True, groups_empty=True
        )
    with sessions() as db:
        assert db.query(DiscoveryCircuit).one().opened_at is None
        assert db.query(DiscoveryCircuit).one().acknowledgements[-1]["actor"] == "operator"
        for token in ids:
            assert db.get(DiscoveryCombination, token.combination_id).attempts == 1


def test_uncommitted_claim_rolls_back_before_start(sessions):
    sweep_id = seed(sessions, 1)
    with sessions() as db:
        sweep = db.get(DiscoverySweep, sweep_id)
        row = db.query(DiscoveryCombination).filter_by(sweep_id=sweep_id).one()
        assert recovery.claim_attempt(db, sweep, row, recovery.now(db))
        db.flush()
        db.rollback()  # Death before the claim transaction committed; no spawn authorized.
    token = claim(sessions, sweep_id)
    assert token.attempt_seq == 1
    with sessions() as db:
        assert db.query(DiscoveryAttempt).count() == 1


def test_commit_before_ack_is_reconciled_without_second_execution(sessions):
    sweep = seed(sessions, 1)
    token = claim(sessions, sweep)
    with sessions() as db:
        row = db.get(DiscoveryCombination, token.combination_id)
        stamp = recovery.now(db)
        db.add(
            DiscoveryResult(
                id="committed",
                sweep_id=sweep,
                combination_id=row.id,
                template_id="frozen",
                symbol=row.symbol,
                timeframe=row.timeframe,
                direction=row.direction,
                parameters={},
                start_at=stamp,
                end_at=stamp,
                metrics={},
                strategy_identity_key="identity",
                evidence_fingerprint="evidence",
                eligibility="low_sample",
            )
        )
        row.lease_expires_at = stamp - timedelta(seconds=1)
        db.commit()  # Simulate death after result commit and before ACK/settlement.
    with sessions() as db:
        recovery.reconcile_expired(db, sweep)
    assert claim(sessions, sweep) is None
    with sessions() as db:
        row = db.get(DiscoveryCombination, token.combination_id)
        assert row.result_id == "committed" and row.attempts == 1
        assert db.query(DiscoveryResult).count() == 1
        assert db.get(DiscoverySweep, sweep).processed == 1
        assert db.get(DiscoveryAttempt, (row.id, 1)).state == "succeeded"


def test_database_outage_blocks_writes_and_restart_recovers_durable_claim(sessions):
    import subprocess
    from sqlalchemy.exc import OperationalError

    if "card-1093-integration" not in os.environ["DATABASE_URL"]:
        pytest.skip("Requires the private PostgreSQL cluster that this test may stop/start")
    sweep = seed(sessions, 1)
    token = claim(sessions, sweep)
    with sessions() as db:
        row = db.get(DiscoveryCombination, token.combination_id)
        row.lease_expires_at = recovery.now(db) - timedelta(seconds=1)
        db.commit()
    # The private socket path assertion in sessions guards this control command.
    prefix = ["runuser", "-u", "ubuntu", "--"] if os.geteuid() == 0 else []
    command = prefix + [
        "/usr/lib/postgresql/16/bin/pg_ctl",
        "-D",
        "/tmp/card-1093-integration-20261013/pg",
    ]
    subprocess.run(command + ["stop", "-m", "fast"], check=True, capture_output=True)
    try:
        with sessions() as db, pytest.raises(OperationalError):
            recovery.heartbeat(db, token)
    finally:
        subprocess.run(
            command + ["-l", "/tmp/card-1093-integration-20261013/postgres.log", "start"],
            check=True,
            capture_output=True,
        )
    with sessions() as db:
        recovery.reconcile_expired(db, sweep)
    with sessions() as db:
        row = db.get(DiscoveryCombination, token.combination_id)
        assert row.attempts == 1 and row.state == "pending"
        assert row.last_failure_code == "lease_interrupted"
    assert claim(sessions, sweep) is None


def _age(sessions, sweep, state=None):
    """Pin updated_at far in the past so any rewrite by the poller is visible."""
    with sessions() as db:
        row = db.get(DiscoverySweep, sweep)
        row.updated_at = row.updated_at.replace(year=2020)
        if state:
            row.state = state
        db.commit()
        return row.updated_at


def test_poll_without_sweep_id_skips_clean_terminal_sweeps(sessions):
    sweep = seed(sessions, 1)
    with sessions() as db:
        row = db.query(DiscoveryCombination).filter_by(sweep_id=sweep).one()
        row.state = "succeeded"
        row.input_snapshot = {"start_date": "2025-10-06", "inputs_cleaned": True}
        db.commit()
    pinned = _age(sessions, sweep, "completed")
    # A concurrent holder of the terminal sweep's row lock must not block the poll.
    with sessions() as holder, sessions() as db:
        holder.query(DiscoverySweep).filter_by(id=sweep).with_for_update().one()
        db.execute(text("SET lock_timeout = '2s'"))
        assert recovery.reconcile_expired(db) == 0
        holder.rollback()
    with sessions() as db:
        assert db.get(DiscoverySweep, sweep).updated_at == pinned


def test_poll_does_not_rewrite_unchanged_running_sweep(sessions):
    sweep = seed(sessions, 2)
    assert claim(sessions, sweep) is not None
    pinned = _age(sessions, sweep)
    with sessions() as db:
        assert recovery.reconcile_expired(db) == 0
    with sessions() as db:
        assert db.get(DiscoverySweep, sweep).updated_at == pinned


def test_poll_still_reconciles_expired_lease_of_non_terminal_sweep(sessions):
    clean = seed(sessions, 1)
    with sessions() as db:
        db.query(DiscoveryCombination).filter_by(sweep_id=clean).update(
            {"state": "succeeded", "input_snapshot": {"inputs_cleaned": True}}
        )
        db.get(DiscoverySweep, clean).state = "completed"
        db.commit()
    sweep = seed(sessions, 1)
    token = claim(sessions, sweep)
    with sessions() as db:
        row = db.get(DiscoveryCombination, token.combination_id)
        row.lease_expires_at = recovery.now(db) - timedelta(seconds=1)
        db.commit()
    with sessions() as db:
        assert recovery.reconcile_expired(db) == 1
    with sessions() as db:
        row = db.get(DiscoveryCombination, token.combination_id)
        assert row.state == "pending" and row.last_failure_code == "lease_interrupted"


def test_poll_discards_uncleaned_inputs_of_terminal_sweep_once(sessions, tmp_path, monkeypatch):
    monkeypatch.setenv("DISCOVERY_SPOOL_DIR", str(tmp_path))
    from app.services.discovery_supervisor import process_identity

    directory = tmp_path / "inputs-test"
    directory.mkdir(mode=0o700)
    (directory / "candles.parquet").write_bytes(b"x")
    (directory / "owner.json").write_text(
        '{"pid": %d, "start": "%s"}' % (os.getpid(), process_identity(os.getpid()))
    )
    manifest = {"directory": str(directory), "files": {}}
    sweep = seed(sessions, 1)
    with sessions() as db:
        row = db.query(DiscoveryCombination).filter_by(sweep_id=sweep).one()
        row.state = "succeeded"
        row.input_snapshot = {"start_date": "2025-10-06", "candle_manifest": manifest}
        db.get(DiscoverySweep, sweep).state = "completed"
        db.commit()
    with sessions() as db:
        recovery.reconcile_expired(db)
    assert not directory.exists()
    with sessions() as db:
        row = db.query(DiscoveryCombination).filter_by(sweep_id=sweep).one()
        assert row.input_snapshot["inputs_cleaned"] is True
        # The manifest survives for audit; the frozen start_date is untouched.
        assert row.input_snapshot["candle_manifest"] == manifest
        assert row.input_snapshot["start_date"] == "2025-10-06"
    pinned = _age(sessions, sweep)
    with sessions() as db:
        recovery.reconcile_expired(db)
    with sessions() as db:
        assert db.get(DiscoverySweep, sweep).updated_at == pinned
