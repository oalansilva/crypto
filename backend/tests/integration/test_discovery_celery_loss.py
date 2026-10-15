"""Actual solo Celery death with a private network-less Redis broker and PG."""

import ctypes
from datetime import timedelta
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import uuid

import pytest
from app.models_discovery import DiscoveryCombination, DiscoveryAttempt
from app.services import discovery_recovery as recovery
from app.services.discovery_supervisor import group_members
from tests.integration.test_discovery_memory_recovery import sessions, seed


def test_actual_celery_death_cleans_children_and_redelivery_obeys_backoff(sessions, tmp_path):
    if not os.getenv("CARD1093_BROKER"):
        pytest.skip("Requires the explicitly isolated Redis unix socket")
    from tests.fixtures.discovery_memory.celery_probe import app

    sweep = seed(sessions, 1)
    queue = "card1093-" + uuid.uuid4().hex
    marker = tmp_path / "group.pid"
    logfile = tmp_path / "celery.log"
    backend = Path(__file__).resolve().parents[2]
    env = {**os.environ, "DISCOVERY_SPOOL_DIR": str(tmp_path)}
    env["PYTHONPATH"] = os.pathsep.join([str(backend), *filter(None, [env.get("PYTHONPATH")])])
    env.pop("DISCOVERY_RESOURCE_PROFILE", None)
    assert ctypes.CDLL(None).prctl(36, 1, 0, 0, 0) == 0
    command = [
        sys.executable,
        "-m",
        "celery",
        "-A",
        "tests.fixtures.discovery_memory.celery_probe:app",
        "worker",
        "--pool=solo",
        "--concurrency=1",
        "--loglevel=INFO",
        "--without-gossip",
        "--without-mingle",
        "--without-heartbeat",
        "-Q",
        queue,
        "--hostname=" + queue + "@localhost",
    ]
    with logfile.open("w") as logs:
        worker = subprocess.Popen(
            command, env=env, cwd=backend, stdout=logs, stderr=logs, start_new_session=True
        )
        try:
            app.send_task("card1093.private_loss", args=[sweep, str(marker)], queue=queue)
            deadline = time.monotonic() + 20
            while not marker.exists() and time.monotonic() < deadline:
                assert worker.poll() is None, logfile.read_text()
                time.sleep(0.05)
            assert marker.exists(), logfile.read_text()
            group = int(marker.read_text())
            deadline = time.monotonic() + 10
            while len(group_members(group)) < 3 and time.monotonic() < deadline:
                time.sleep(0.05)
            assert len(group_members(group)) >= 3
            started = time.monotonic()
            worker.kill()
            worker.wait(5)
            deadline = started + 19
            while time.monotonic() < deadline:
                try:
                    while os.waitpid(-group, os.WNOHANG)[0] > 0:
                        pass
                except ChildProcessError:
                    pass
                if not group_members(group):
                    break
                time.sleep(0.05)
            assert not group_members(group)
            assert time.monotonic() - started < 20
            with sessions() as db:
                row = db.query(DiscoveryCombination).filter_by(sweep_id=sweep).one()
                assert row.attempts == 1 and row.state == "running"
                assert db.get(DiscoveryAttempt, (row.id, 1)).state == "running"
                row.lease_expires_at = recovery.now(db) - timedelta(seconds=1)
                db.commit()
            with sessions() as db:
                recovery.reconcile_expired(db, sweep)
            worker = subprocess.Popen(
                command, env=env, cwd=backend, stdout=logs, stderr=logs, start_new_session=True
            )
            retry = app.send_task("card1093.private_loss", args=[sweep, str(marker)], queue=queue)
            assert retry.get(timeout=20) == "no_claim"
            with sessions() as db:
                row = db.query(DiscoveryCombination).filter_by(sweep_id=sweep).one()
                assert row.attempts == 1 and row.state == "pending"
                assert (row.next_attempt_at - row.updated_at).total_seconds() == 60
        finally:
            if worker.poll() is None:
                worker.terminate()
                try:
                    worker.wait(5)
                except subprocess.TimeoutExpired:
                    worker.kill()
                    worker.wait(5)
