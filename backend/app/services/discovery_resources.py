"""Discovery resource envelope and telemetry; admission is fail closed."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from dataclasses import replace
from pathlib import Path
import os
import shutil
import tracemalloc
import json
import subprocess
import time

_SERVICE_SAMPLE = (0, {})

GiB = 1024**3
MiB = 1024**2


class OperationalFailure(RuntimeError):
    def __init__(self, code, counters=None):
        super().__init__(code)
        self.code = code
        self.counters = counters or {}


class CalculationFailure(OperationalFailure):
    pass


@dataclass(frozen=True)
class ResourceProfile:
    name: str = "dev"
    memory_high: int = 5 * GiB
    memory_max: int = 6 * GiB
    swap_max: int = 512 * MiB
    requested_workers: int = 1
    cache_bytes: int = 64 * MiB
    pending_bytes: int = 64 * MiB
    retention_bytes: int = 128 * MiB
    spool_bytes: int = 2 * GiB
    batch_size: int = 200
    unprofiled_workers: int | None = None

    @property
    def effective_workers(self):
        if self.unprofiled_workers is not None:
            if self.name != "unprofiled" or self.unprofiled_workers < 1:
                raise OperationalFailure("resource_budget_unavailable")
            return self.unprofiled_workers
        capacity = (self.memory_max - 2 * GiB) // (3 * GiB)
        if capacity < 1 or self.requested_workers < 1 or self.batch_size not in range(1, 201):
            raise OperationalFailure("resource_budget_unavailable")
        if self.name == "dev" and self.requested_workers != 1:
            raise OperationalFailure("resource_budget_unavailable")
        return min(self.requested_workers, capacity)

    @classmethod
    def configured(cls):
        return cls(
            name=os.getenv("DISCOVERY_RESOURCE_PROFILE", "dev"),
            requested_workers=int(os.getenv("DISCOVERY_INTERNAL_WORKERS", "1")),
        )

    @classmethod
    def optimizer(cls, default_workers=None):
        if os.getenv("DISCOVERY_RESOURCE_PROFILE"):
            return cls.configured()
        workers = (
            default_workers if default_workers is not None else max(1, (os.cpu_count() or 2) - 1)
        )
        return replace(cls(), name="unprofiled", unprofiled_workers=workers)


def cgroup_path():
    entry = next(
        (
            line[3:]
            for line in Path("/proc/self/cgroup").read_text().splitlines()
            if line.startswith("0::")
        ),
        None,
    )
    if entry is None:
        raise OperationalFailure("resource_budget_unavailable")
    return Path("/sys/fs/cgroup") / entry.lstrip("/")


def host_memory():
    return {
        k: int(v.split()[0]) * 1024
        for k, v in (line.split(":", 1) for line in Path("/proc/meminfo").read_text().splitlines())
    }


def admission(profile=None, spool_root=None, group=None, memory=None):
    profile = profile or ResourceProfile.configured()
    group = group or cgroup_path()
    memory = memory or host_memory()
    try:
        limits = {
            key: int((group / key).read_text().strip())
            for key in ("memory.high", "memory.max", "memory.swap.max", "memory.oom.group")
        }
        if (
            limits["memory.high"] != profile.memory_high
            or limits["memory.max"] != profile.memory_max
            or limits["memory.swap.max"] != profile.swap_max
            or limits["memory.oom.group"] != 1
            or memory["MemTotal"] < profile.memory_max + 17 * GiB
            or memory["MemAvailable"] < 8 * GiB
            or memory["SwapFree"] < GiB
            or shutil.disk_usage(spool_root or spool_directory()).free < 4 * GiB
        ):
            raise OperationalFailure("resource_budget_unavailable")
        profile.effective_workers
        return asdict(profile)
    except (OSError, ValueError, KeyError) as exc:
        raise OperationalFailure("resource_budget_unavailable") from exc


def spool_directory():
    # Explicit persistent filesystem, never /dev/shm or tmpfs.
    root = Path(
        os.getenv(
            "DISCOVERY_SPOOL_DIR", f"/var/tmp/criptofarol-{discovery_environment()}-discovery"
        )
    )
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    mount = max(
        (
            line.split()
            for line in Path("/proc/mounts").read_text().splitlines()
            if root.resolve().is_relative_to(Path(line.split()[1]))
        ),
        key=lambda item: len(item[1]),
    )
    if mount[2] in ("tmpfs", "ramfs"):
        raise OperationalFailure("spool_invalid")
    return root


def discovery_environment():
    explicit = os.getenv("DISCOVERY_RESOURCE_PROFILE") or os.getenv("APP_ENV")
    if explicit:
        return explicit
    # Dispatcher/backend and Discovery must select the same environment even
    # when only the Discovery service opted into the resource profile.
    return "prod" if cgroup_path().name.startswith("criptofarol-prod-") else "dev"


def _semaphore_record(queues):
    from multiprocessing import resource_tracker

    names = []
    for item in queues:
        for attribute in ("_rlock", "_wlock", "_sem"):
            lock = getattr(item, attribute, None)
            if lock is not None and lock._semlock.name:
                names.append(lock._semlock.name)
    return {"semaphores": names, "tracker_pipe": os.fstat(resource_tracker.getfd()).st_ino}


def mark_spool_owner(directory, queues=None):
    from app.services.discovery_supervisor import process_identity

    owner = {"pid": os.getpid(), "start": process_identity(os.getpid())}
    if queues is not None:
        owner.update(_semaphore_record(queues))
    (Path(directory) / "owner.json").write_text(json.dumps(owner))


def track_pool(executor):
    directory = os.getenv("DISCOVERY_SUPERVISOR_DIR")
    if not directory:
        return
    from app.services.discovery_supervisor import process_identity

    record = {
        "pid": os.getpid(),
        "start": process_identity(os.getpid()),
        **_semaphore_record((executor._call_queue, executor._result_queue)),
    }
    with (Path(directory) / "pool-semaphores.jsonl").open("a") as target:
        target.write(json.dumps(record) + "\n")


def cleanup_semaphores(directory, include_owner=False):
    from app.services.discovery_supervisor import process_identity
    from multiprocessing import resource_tracker
    import _multiprocessing

    root = Path(directory)
    records = []
    if (root / "pool-semaphores.jsonl").exists():
        records = [
            json.loads(line) for line in (root / "pool-semaphores.jsonl").read_text().splitlines()
        ]
    if include_owner:
        records.append(json.loads((root / "owner.json").read_text()))
    for record in records:
        actual = process_identity(record["pid"])
        if actual == record["start"]:
            try:
                state = Path(f"/proc/{record['pid']}/stat").read_text().rsplit(")", 1)[1].split()[0]
            except FileNotFoundError:
                state = "gone"
            if state != "Z":
                return False
        for name in record.get("semaphores", ()):
            try:
                _multiprocessing.sem_unlink(name)
            except FileNotFoundError:
                continue
            if os.fstat(resource_tracker.getfd()).st_ino == record.get("tracker_pipe"):
                resource_tracker.unregister(name, "semaphore")
    return True


def auxiliary_spool_bytes():
    """Frozen input plus supervisor IPC files share the attempt's disk quota."""
    roots = {os.getenv("DISCOVERY_FROZEN_INPUT_DIR"), os.getenv("DISCOVERY_SUPERVISOR_DIR")}
    return sum(
        path.stat().st_size
        for root in roots
        if root
        for path in Path(root).iterdir()
        if path.is_file()
    )


def cleanup_orphan_spools():
    """Only known private files whose recorded owner is proven gone."""
    from app.services.discovery_supervisor import process_identity

    for directory in spool_directory().iterdir():
        if (
            not directory.is_dir()
            or directory.is_symlink()
            or not directory.name.startswith(("attempt-", "supervisor-"))
        ):
            continue
        marker = directory / "owner.json"
        if not marker.exists():
            continue  # Never guess ownership of an unmarked directory.
        owner = json.loads(marker.read_text())
        if process_identity(owner["pid"]) == owner["start"]:
            continue
        if not cleanup_semaphores(directory, include_owner=True):
            continue
        allowed = {
            "owner.json",
            "results.sqlite",
            "result.pickle",
            "pool-workers.jsonl",
            "pool-semaphores.jsonl",
        }
        entries = list(directory.iterdir())
        if any(
            item.name not in allowed or not item.is_file() or item.is_symlink() for item in entries
        ):
            raise OperationalFailure("orphan_spool_unrecognized")
        for item in entries:
            item.unlink()
        directory.rmdir()


def telemetry(group=None):
    global _SERVICE_SAMPLE
    sample = {"pid": os.getpid()}
    for line in Path("/proc/self/smaps_rollup").read_text().splitlines():
        if line.startswith(("Rss:", "Pss:")):
            key, value, _ = line.split()
            sample[key[:-1].lower() + "_bytes"] = int(value) * 1024
    try:
        group = group or cgroup_path()
        for name in ("memory.current", "memory.peak", "memory.swap.current", "memory.events"):
            sample[name] = (group / name).read_text().strip()
    except OSError:
        sample["cgroup"] = "unavailable"
    if tracemalloc.is_tracing():
        sample["python_current"], sample["python_peak"] = tracemalloc.get_traced_memory()
    from app.services.discovery_budget_cache import BUDGET

    sample["cache_bytes"] = BUDGET.bytes
    sample["cache_entries"] = len(BUDGET.entries)
    sample["cache_evictions"] = BUDGET.evictions
    if time.monotonic() - _SERVICE_SAMPLE[0] >= 30:
        unit = (group or cgroup_path()).name
        if unit.endswith(".service"):
            try:
                result = subprocess.run(
                    ["systemctl", "show", unit, "--property=NRestarts", "--property=Result"],
                    text=True,
                    capture_output=True,
                    timeout=2,
                )
                service = dict(
                    line.split("=", 1) for line in result.stdout.splitlines() if "=" in line
                )
            except (OSError, subprocess.SubprocessError):
                # Telemetria é best-effort: systemctl ausente/lento não pode
                # derrubar o batch. Degrada para "ausente" e tenta de novo em 30 s.
                service = {}
            _SERVICE_SAMPLE = (time.monotonic(), service)
    sample["systemd"] = _SERVICE_SAMPLE[1]
    return sample
