"""Disposable spawn supervisor with an exclusive POSIX group and bounded IPC."""

from __future__ import annotations
import ctypes
import logging
import json
import multiprocessing
import os
from pathlib import Path
import pickle
import queue
import signal
import tempfile
import time

from app.services.discovery_resources import (
    ResourceProfile,
    OperationalFailure,
    CalculationFailure,
    host_memory,
    spool_directory,
    telemetry,
    MiB,
    GiB,
    mark_spool_owner,
    auxiliary_spool_bytes,
    cleanup_semaphores,
)

logger = logging.getLogger(__name__)


def process_identity(pid):
    try:
        fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
        return fields[19]  # field22 starttime (after comm)
    except (FileNotFoundError, ProcessLookupError):
        return None


def group_members(pgid):
    members = []
    for path in Path("/proc").iterdir():
        if not path.name.isdigit():
            continue
        try:
            fields = (path / "stat").read_text().rsplit(")", 1)[1].split()
            if int(fields[2]) == pgid:
                members.append((int(path.name), fields[0]))
        except (OSError, ValueError):
            pass
    return members


def parent_death_signal(signum=signal.SIGKILL):
    expected = os.getppid()
    if ctypes.CDLL(None, use_errno=True).prctl(1, int(signum), 0, 0, 0) != 0:
        raise OperationalFailure("parent_death_signal_unavailable")
    if os.getppid() != expected:
        os.kill(os.getpid(), signum)


def register_pool_worker():
    directory = os.getenv("DISCOVERY_SUPERVISOR_DIR")
    if not directory:
        return
    record = {"pid": os.getpid(), "start": process_identity(os.getpid()), "group": os.getpgrp()}
    descriptor = os.open(
        Path(directory) / "pool-workers.jsonl", os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600
    )
    try:
        os.write(descriptor, (json.dumps(record) + "\n").encode())
    finally:
        os.close(descriptor)


def pool_worker_lost(directory, supervisor_pid):
    roster = Path(directory) / "pool-workers.jsonl"
    if not roster.exists():
        return False
    for line in roster.read_text().splitlines():
        worker = json.loads(line)
        if worker["group"] != supervisor_pid:
            raise OperationalFailure("pool_group_identity_mismatch")
        actual = process_identity(worker["pid"])
        if actual != worker["start"]:
            return True
        try:
            state = Path(f"/proc/{worker['pid']}/stat").read_text().rsplit(")", 1)[1].split()[0]
        except FileNotFoundError:
            return True
        if state == "Z":
            return True
    return False


def _supervisor_entry(events, acknowledgements, directory, inputs):
    os.setsid()
    os.environ["DISCOVERY_SUPERVISOR_DIR"] = directory

    def terminate(*_):
        # The group is owned exclusively by this supervisor; includes its pool.
        os.killpg(os.getpid(), signal.SIGKILL)

    signal.signal(signal.SIGTERM, terminate)
    parent_death_signal(signal.SIGTERM)
    events.put({"ready": (os.getpid(), process_identity(os.getpid()))})
    if acknowledgements.get(timeout=60) is not True:
        raise OperationalFailure("supervisor_fence_rejected")
    try:
        import tracemalloc

        tracemalloc.start(1)
        from app.services import discovery_stream

        stage_manifest = {}

        def progress(event):
            if event.get("stage_id") and event.get("counters"):
                stage_manifest[event["stage_id"]] = event["counters"]
            events.put({"progress": event}, timeout=30)
            if acknowledgements.get(timeout=60) is not True:
                raise OperationalFailure("progress_fence_rejected")

        discovery_stream.PROGRESS_CALLBACK = progress
        from app.tasks.discovery_tasks import DISCOVERY_SPLIT_TRAIN_RATIO, MIN_ELIGIBLE_TRADES
        from app.services.combo_optimizer import ComboOptimizer

        frozen_metadata = inputs.pop("template_metadata", None)
        # The immutable metadata is private to this child, never changes catalogue.
        if frozen_metadata is not None:
            from app.services.combo_service import ComboService

            original = ComboService.get_template_metadata
            ComboService.get_template_metadata = lambda self, name: (
                frozen_metadata if name == inputs["template_name"] else original(self, name)
            )
        from app.services.discovery_inputs import activate, prepare, read

        manifest = prepare(inputs)
        activate(manifest)
        progress(
            {
                "phase_complete": "input_snapshot",
                "candle_manifest": manifest,
                "telemetry": telemetry(),
            }
        )
        inputs.pop("candle_manifest", None)
        listing_len = len(read("candles"))
        train_len = int(listing_len * DISCOVERY_SPLIT_TRAIN_RATIO)
        insufficient = listing_len < 2 or train_len < MIN_ELIGIBLE_TRADES
        progress({"phase_complete": "listing", "telemetry": telemetry()})
        if insufficient:
            result = {"insufficient": True, "listing_len": listing_len, "train_len": train_len}
        else:
            result = ComboOptimizer().run_optimization(
                **inputs,
                data_source="ccxt",
                deep_backtest=True,
                split_train_ratio=DISCOVERY_SPLIT_TRAIN_RATIO,
            )
            if not stage_manifest or any(
                counts["executed"] != counts["planned"]
                or counts["unknown"]
                or counts["remaining"]
                or counts["failed"]
                for counts in stage_manifest.values()
            ):
                raise OperationalFailure("incomplete_execution_manifest")
            result["execution_manifest"] = stage_manifest
        data = pickle.dumps(result, protocol=5)
        progress(
            {
                "phase_complete": "result_serialized",
                "telemetry": telemetry(),
                "serialized_bytes": len(data),
            }
        )
        if len(data) > 128 * MiB:
            raise OperationalFailure("result_retention_exceeded")
        if len(data) + auxiliary_spool_bytes() > ResourceProfile.configured().spool_bytes:
            raise OperationalFailure("spool_quota_exceeded")
        target = Path(directory) / "result.pickle"
        with target.open("xb") as out:
            os.chmod(target, 0o600)
            out.write(data)
            out.flush()
            os.fsync(out.fileno())
        events.put({"result": True, "telemetry": telemetry()}, timeout=30)
    except BaseException as exc:
        try:
            events.put(
                {
                    "error": getattr(exc, "code", type(exc).__name__),
                    "deterministic": isinstance(exc, CalculationFailure),
                    "counters": getattr(exc, "counters", {}),
                },
                timeout=2,
            )
        except Exception:
            pass
        raise


def cleanup(process, identity, timeout=20):
    """TERM at0, KILL at10, reap until20; no replacement before group empty."""
    pid = process.pid
    logger.info("Discovery cleanup begin pid=%s at=%s", pid, time.monotonic())
    if pid is None:
        return
    if identity is None:
        # No handshake yet: child cannot have started pool work.
        process.terminate()
        process.join(timeout)
        if process.is_alive():
            process.kill()
            process.join(1)
        if process.is_alive():
            raise OperationalFailure("cleanup_unproven")
        return
    actual = process_identity(pid)
    if actual is not None and actual != identity:
        raise OperationalFailure("cleanup_identity_mismatch")
    deadline = time.monotonic() + timeout
    try:
        os.killpg(pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    escalated = False
    while time.monotonic() < deadline:
        process.join(0.05)
        # Reap only this exclusive group's adopted grandchildren.
        try:
            while os.waitpid(-pid, os.WNOHANG)[0] > 0:
                pass
        except ChildProcessError:
            pass
        if not group_members(pid):
            logger.info("Discovery cleanup proven pid=%s at=%s", pid, time.monotonic())
            return
        if not escalated and time.monotonic() >= deadline - 10:
            try:
                os.killpg(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            escalated = True
        time.sleep(0.05)
    raise OperationalFailure("cleanup_unproven")


def run_supervised(inputs, beat, *, _target=None):
    # Adopt pool children only to reap this supervisor's group after loss.
    if ctypes.CDLL(None, use_errno=True).prctl(36, 1, 0, 0, 0) != 0:
        raise OperationalFailure("subreaper_unavailable")
    context = multiprocessing.get_context("spawn")
    events = context.Queue(maxsize=4)
    acknowledgements = context.Queue(maxsize=1)
    with tempfile.TemporaryDirectory(prefix="supervisor-", dir=spool_directory()) as directory:
        mark_spool_owner(directory, (events, acknowledgements))
        process = context.Process(
            target=_target or _supervisor_entry,
            args=(events, acknowledgements, directory, dict(inputs)),
        )
        identity = None
        pending = []
        result_ready = False
        next_beat = time.monotonic()
        low_memory_since = None
        pool_active = True
        process.start()
        try:
            while True:
                try:
                    event = events.get(timeout=1)
                    logger.info(
                        "Discovery supervisor event kind=%s at=%s", tuple(event), time.monotonic()
                    )
                    if "ready" in event:
                        pid, identity = event["ready"]
                        if pid != process.pid or process_identity(pid) != identity:
                            raise OperationalFailure("supervisor_identity_mismatch")
                        beat([], (process.pid, identity))
                        acknowledgements.put(True, timeout=2)
                    if "progress" in event:
                        counters = event["progress"].get("counters")
                        if counters:
                            pool_active = counters["unknown"] > 0 or counters["remaining"] > 0
                        beat([event["progress"]], (process.pid, identity))
                        failure = event["progress"].get("failure")
                        if failure:
                            cls = (
                                CalculationFailure
                                if failure == "calculation_error"
                                else OperationalFailure
                            )
                            raise cls(failure, event["progress"].get("counters"))
                        acknowledgements.put(True, timeout=2)
                        next_beat = time.monotonic() + 30
                    if "error" in event:
                        cls = CalculationFailure if event["deterministic"] else OperationalFailure
                        raise cls(event["error"], event.get("counters"))
                    if event.get("result"):
                        result_ready = True
                        break
                except queue.Empty:
                    if not process.is_alive():
                        raise OperationalFailure("supervisor_lost")
                current = time.monotonic()
                if identity and pool_active and pool_worker_lost(directory, process.pid):
                    raise OperationalFailure("pool_child_lost")
                if current >= next_beat:
                    beat(pending, (process.pid, identity) if identity else None)
                    pending.clear()
                    next_beat = current + 30
                    logger.info("Discovery telemetry %s", telemetry())
                if host_memory()["MemAvailable"] < 2 * GiB:
                    low_memory_since = low_memory_since or current
                    if current - low_memory_since >= 30:
                        raise OperationalFailure("host_memory_pressure")
                else:
                    low_memory_since = None
            beat(pending, (process.pid, identity))
            process.join(1)
            cleanup(process, identity)
            result = pickle.loads((Path(directory) / "result.pickle").read_bytes())
            return result
        finally:
            try:
                cleanup(process, identity)
            except OperationalFailure:
                logger.critical(
                    "Discovery cleanup unproven; service must fail for control-group cleanup"
                )
                # A solo worker must not survive to create another pool.
                os._exit(70)
            if not cleanup_semaphores(directory):
                os._exit(70)
            events.close()
            events.cancel_join_thread()
            acknowledgements.close()
            acknowledgements.cancel_join_thread()


def cleanup_recorded_group(pid, identity, timeout=20):
    """External reconciler cleanup of a durably recorded, exclusive group."""
    actual = process_identity(pid)
    if actual is not None and actual != identity:
        raise OperationalFailure("cleanup_identity_mismatch")
    if actual is not None and os.getpgid(pid) != pid:
        raise OperationalFailure("cleanup_group_mismatch")
    deadline = time.monotonic() + timeout
    try:
        os.killpg(pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    killed = False
    while time.monotonic() < deadline:
        if not any(state != "Z" for _, state in group_members(pid)):
            return
        if not killed and time.monotonic() >= deadline - 10:
            try:
                os.killpg(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            killed = True
        time.sleep(0.05)
    raise OperationalFailure("cleanup_unproven")
