"""Read-only progress/inventory snapshot for the contained original workload."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

ROOT = Path("/srv/apps/dev/criptofarol/crypto-worktrees/card-1093-discovery-memory")
EVIDENCE = ROOT / "openspec/changes/card-1093-discovery-memory"
UNIT = "card-1093-original-validation.service"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", action="store_true")
    args = parser.parse_args()
    properties = (
        "ActiveState",
        "MainPID",
        "InvocationID",
        "MemoryCurrent",
        "MemoryPeak",
        "MemorySwapCurrent",
        "MemoryHigh",
        "MemoryMax",
        "MemorySwapMax",
        "NRestarts",
        "CPUUsageNSec",
        "ActiveEnterTimestamp",
        "ControlGroup",
        "OOMPolicy",
        "KillMode",
    )
    command = ["systemctl", "show", UNIT] + [f"--property={key}" for key in properties]
    unit = dict(
        line.split("=", 1) for line in subprocess.check_output(command, text=True).splitlines()
    )
    progress = json.loads((EVIDENCE / "original_progress.json").read_text())
    snapshot = {"utc": datetime.now(timezone.utc).isoformat(), "unit": unit, "progress": progress}
    group = Path("/sys/fs/cgroup") / unit["ControlGroup"].lstrip("/")
    snapshot["memory.events"] = (group / "memory.events").read_text()
    with (EVIDENCE / "original_snapshots.jsonl").open("a") as target:
        target.write(json.dumps(snapshot, sort_keys=True) + "\n")
    if args.inventory:
        memory = {
            key: int(value.split()[0]) * 1024
            for key, value in (
                line.split(":", 1) for line in Path("/proc/meminfo").read_text().splitlines()
            )
        }
        charges = {}
        # Each listed child is disjoint: no parent+descendant double counting.
        for root in (Path("/sys/fs/cgroup/system.slice"), Path("/sys/fs/cgroup")):
            for child in sorted(root.iterdir()):
                if not child.is_dir() or child.name in ("system.slice", UNIT):
                    continue
                source = child / "memory.current"
                if source.exists():
                    charges[str(child.relative_to("/sys/fs/cgroup"))] = int(source.read_text())
        inventory = {
            "utc": snapshot["utc"],
            "host_memory_bytes": {
                key: memory[key] for key in ("MemTotal", "MemAvailable", "SwapTotal", "SwapFree")
            },
            "other_cgroup_memory_current_bytes": charges,
            "other_cgroups_total_bytes": sum(charges.values()),
            "reserved_outside_discovery_bytes": 17 * 1024**3,
            "discovery_max_bytes": 6 * 1024**3,
            "reservation_fits": memory["MemTotal"] >= 23 * 1024**3,
        }
        (EVIDENCE / "dev_inventory.json").write_text(json.dumps(inventory, indent=2) + "\n")
    print(json.dumps(snapshot, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
