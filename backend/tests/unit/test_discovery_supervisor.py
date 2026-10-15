"""Actual spawned process/pool loss and exclusive-group cleanup (#1093)."""

import ctypes
import multiprocessing
import os
from pathlib import Path
import signal
import time
from concurrent.futures import ProcessPoolExecutor
import pytest

from app.services import discovery_supervisor
from app.services.discovery_resources import (
    GiB,
    OperationalFailure,
    track_pool,
    cleanup_orphan_spools,
)
from app.services.discovery_supervisor import (
    run_supervised,
    parent_death_signal,
    process_identity,
    group_members,
    register_pool_worker,
)


def _pool_child(action):
    parent_death_signal()
    register_pool_worker()
    print("test pool child", os.getpid(), action, time.monotonic(), flush=True)
    if action == "kill":
        time.sleep(0.2)
        os.kill(os.getpid(), signal.SIGKILL)
    time.sleep(30)
    return 1


def _isolated_target(events, acknowledgements, directory, inputs):
    os.setsid()
    os.environ["DISCOVERY_SUPERVISOR_DIR"] = directory
    signal.signal(signal.SIGTERM, lambda *_: os.killpg(os.getpid(), signal.SIGKILL))
    parent_death_signal(signal.SIGTERM)
    events.put({"ready": (os.getpid(), process_identity(os.getpid()))})
    assert acknowledgements.get(timeout=10) is True
    marker = inputs.get("marker")
    if marker:
        Path(marker).write_text(str(os.getpid()))
    if inputs["action"] == "supervisor":
        os.kill(os.getpid(), signal.SIGKILL)
    with ProcessPoolExecutor(2, mp_context=multiprocessing.get_context("spawn")) as pool:
        track_pool(pool)
        pool.submit(_pool_child, "wait")
        future = pool.submit(
            _pool_child, "kill" if inputs["action"] in ("child", "silent_child") else "wait"
        )
        if inputs["action"] == "silent_child":
            # The supervisor/executor cannot report the loss promptly. The
            # principal must detect the registered worker's death itself.
            time.sleep(30)
        try:
            future.result()
        except BaseException as exc:
            print("test pool lost", type(exc).__name__, time.monotonic(), flush=True)
            events.put({"error": "pool_lost", "deterministic": False, "counters": {}}, timeout=2)
            raise


@pytest.mark.parametrize("action", ["child", "silent_child", "supervisor"])
def test_lost_process_cleans_entire_group_before_return(tmp_path, monkeypatch, action):
    monkeypatch.setenv("DISCOVERY_SPOOL_DIR", str(tmp_path))
    identities = []
    started = time.monotonic()

    def beat(events, supervisor):
        if supervisor:
            identities.append(supervisor)

    with pytest.raises(OperationalFailure) as failure:
        run_supervised({"action": action}, beat, _target=_isolated_target)
    if action == "silent_child":
        assert failure.value.code == "pool_child_lost"
    assert time.monotonic() - started < 20
    for pid, _ in identities:
        assert not group_members(pid)
    assert not list(tmp_path.iterdir())


def _principal(marker, root):
    os.environ["DISCOVERY_SPOOL_DIR"] = root
    run_supervised({"action": "wait", "marker": marker}, lambda *_: None, _target=_isolated_target)


def test_solo_principal_death_kills_supervisor_and_pool(tmp_path, monkeypatch):
    monkeypatch.setenv("DISCOVERY_SPOOL_DIR", str(tmp_path))
    # This outer test adopts descendants so it can also prove reap, like systemd.
    assert ctypes.CDLL(None).prctl(36, 1, 0, 0, 0) == 0
    marker = tmp_path / "group.pid"
    principal = multiprocessing.get_context("spawn").Process(
        target=_principal, args=(str(marker), str(tmp_path))
    )
    principal.start()
    deadline = time.monotonic() + 15
    while not marker.exists() and time.monotonic() < deadline:
        time.sleep(0.05)
    assert marker.exists()
    group = int(marker.read_text())
    # Allow actual pool spawn before loss of the solo principal.
    time.sleep(1)
    principal.kill()
    principal.join(3)
    deadline = time.monotonic() + 10
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
    cleanup_orphan_spools()


def _idle_target(events, acknowledgements, directory, inputs):
    os.setsid()
    os.environ["DISCOVERY_SUPERVISOR_DIR"] = directory
    parent_death_signal(signal.SIGTERM)
    events.put({"ready": (os.getpid(), process_identity(os.getpid()))})
    assert acknowledgements.get(timeout=10) is True
    time.sleep(60)


class _SimulatedClock:
    """Proxy of ``time`` whose monotonic clock jumps 12 s per MemAvailable probe."""

    def __init__(self):
        self.offset = 0.0

    def monotonic(self):
        return time.monotonic() + self.offset

    def __getattr__(self, name):
        return getattr(time, name)


def _simulate_host_memory(monkeypatch, tmp_path, samples):
    """Feed ``samples`` (MemAvailable bytes) to run_supervised; None stops the loop."""
    monkeypatch.setenv("DISCOVERY_SPOOL_DIR", str(tmp_path))
    clock = _SimulatedClock()
    calls = []

    def fake_host_memory():
        index = len(calls)
        calls.append(clock.offset)
        clock.offset += 12  # each probe happens 12 simulated seconds after the last
        if index >= len(samples) or samples[index] is None:
            raise RuntimeError("simulation finished")
        return {"MemAvailable": samples[index]}

    monkeypatch.setattr(discovery_supervisor, "time", clock)
    monkeypatch.setattr(discovery_supervisor, "host_memory", fake_host_memory)
    return calls


def test_host_memory_below_2gib_for_30s_aborts_attempt(tmp_path, monkeypatch):
    low = GiB - 1
    calls = _simulate_host_memory(monkeypatch, tmp_path, [low] * 10)
    with pytest.raises(OperationalFailure) as failure:
        run_supervised({}, lambda *_: None, _target=_idle_target)
    assert failure.value.code == "host_memory_pressure"
    # Probes at 0, 12 and 24 simulated seconds do not abort; the one at 36 does.
    assert len(calls) == 4
    assert not list(tmp_path.iterdir())


def test_host_memory_recovery_before_30s_does_not_abort(tmp_path, monkeypatch):
    low, ok = GiB - 1, 2 * GiB
    # low@0, low@12, recovered@24, low@36, low@48 would abort at 36 without the reset.
    calls = _simulate_host_memory(monkeypatch, tmp_path, [low, low, ok, low, low, None])
    with pytest.raises(RuntimeError, match="simulation finished"):
        run_supervised({}, lambda *_: None, _target=_idle_target)
    assert len(calls) == 6
    assert not list(tmp_path.iterdir())
