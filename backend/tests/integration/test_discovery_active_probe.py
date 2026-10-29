"""Active-search probe against the private test PostgreSQL (#1110)."""

from datetime import timedelta
import importlib.util
import json
from pathlib import Path
import os
import uuid

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from database_guard import assert_safe_test_database_url
from app.models_discovery import (
    DiscoveryAttempt,
    DiscoveryCircuit,
    DiscoveryCombination,
    DiscoveryOutbox,
    DiscoveryResult,
    DiscoverySweep,
)
from app.services import discovery_recovery as recovery

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/discovery/active_search_probe.py"
spec = importlib.util.spec_from_file_location("active_search_probe", SCRIPT)
probe_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe_module)


@pytest.fixture
def sessions():
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
    yield sessionmaker(bind=engine, expire_on_commit=False)
    engine.dispose()


def seed(sessions, state, lease=None, attempt=None):
    """One sweep with one combination. lease: seconds from the DB clock (neg = expired)."""
    with sessions() as db:
        sweep = DiscoverySweep(
            id=uuid.uuid4().hex,
            actor="test",
            state=state,
            idempotency_key=uuid.uuid4().hex,
            payload_hash="hash",
            snapshot_token="token",
            snapshot_hash="hash",
            total=1,
            snapshot={},
        )
        db.add(sweep)
        db.flush()
        combination = DiscoveryCombination(
            sweep_id=sweep.id,
            template_id="frozen",
            symbol="X",
            timeframe="1d",
            direction="long",
        )
        db.add(combination)
        db.flush()
        stamp = recovery.now(db)
        if lease is not None:
            combination.lease_owner = "owner"
            combination.lease_expires_at = stamp + timedelta(seconds=lease)
        if attempt is not None:
            db.add(
                DiscoveryAttempt(
                    combination_id=combination.id,
                    attempt_seq=1,
                    owner="owner",
                    generation=1,
                    state=attempt,
                    started_at=stamp,
                    heartbeat_at=stamp,
                    progress_at=stamp,
                    finished_at=None if attempt == "running" else stamp,
                    profile={},
                )
            )
        db.commit()
        return sweep.id


def run(sessions):
    with sessions() as db:
        return probe_module.probe(db)


def test_idle_database_is_not_active(sessions):
    report = run(sessions)
    assert report["active"] is False and report["sweeps"] == [] and report["error"] is None


@pytest.mark.parametrize("state", ["running", "cancelling"])
def test_running_or_cancelling_sweep_is_active(sessions, state):
    sweep = seed(sessions, state)
    report = run(sessions)
    assert report["active"] is True
    assert report["sweeps"][0]["id"] == sweep
    assert report["sweeps"][0]["reasons"] == ["sweep_state"]


@pytest.mark.parametrize("state", ["pending", "paused"])
def test_pending_and_paused_are_listed_without_blocking(sessions, state):
    sweep = seed(sessions, state)
    report = run(sessions)
    assert report["active"] is False
    assert [(s["id"], s["state"], s["active"]) for s in report["sweeps"]] == [(sweep, state, False)]


def test_valid_lease_blocks_even_on_a_pending_sweep(sessions):
    sweep = seed(sessions, "pending", lease=300)
    report = run(sessions)
    assert report["active"] is True
    assert report["sweeps"][0]["id"] == sweep and report["sweeps"][0]["reasons"] == ["valid_lease"]


def test_expired_lease_uses_database_clock_and_does_not_block(sessions):
    seed(sessions, "pending", lease=-1)
    assert run(sessions)["active"] is False


def test_running_attempt_without_end_blocks_even_on_terminal_sweep(sessions):
    sweep = seed(sessions, "completed", attempt="running")
    report = run(sessions)
    assert report["active"] is True
    assert report["sweeps"][0]["id"] == sweep
    assert report["sweeps"][0]["reasons"] == ["running_attempt"]


def test_finished_attempt_does_not_block(sessions):
    seed(sessions, "failed", attempt="failed")
    assert run(sessions)["active"] is False


def test_report_merges_reasons_and_lists_queued_sweeps_next_to_active(sessions):
    active = seed(sessions, "running", lease=300, attempt="running")
    queued = seed(sessions, "pending")
    report = run(sessions)
    by_id = {s["id"]: s for s in report["sweeps"]}
    assert by_id[active]["reasons"] == ["running_attempt", "sweep_state", "valid_lease"]
    assert by_id[queued]["active"] is False
    assert report["active"] is True


def test_query_error_counts_as_active_and_exit_code(capsys, monkeypatch):
    class Broken:
        def __enter__(self):
            raise RuntimeError("database down")

        def __exit__(self, *_):
            return False

    report = probe_module.report_for(lambda: Broken())
    assert report["active"] is True and "database down" in report["error"]
    monkeypatch.setattr(probe_module, "report_for", lambda: report)
    assert probe_module.main() == probe_module.EXIT_ACTIVE == 3
    assert json.loads(capsys.readouterr().out)["active"] is True


def test_main_exits_zero_when_idle(capsys, monkeypatch):
    idle = {"active": False, "error": None, "checked_at": None, "sweeps": []}
    monkeypatch.setattr(probe_module, "report_for", lambda: idle)
    assert probe_module.main() == probe_module.EXIT_IDLE == 0
    assert json.loads(capsys.readouterr().out) == idle
