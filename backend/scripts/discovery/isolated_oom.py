"""Only execute inside a pre-created disposable 512MiB cgroup, never globally."""

from pathlib import Path
import os
import sys
import time

# Standalone: no application/database import before verifying containment.
entry = next(
    line[3:]
    for line in Path("/proc/self/cgroup").read_text().splitlines()
    if line.startswith("0::")
)
if not entry.endswith("/card-1093-oom.service"):
    raise SystemExit("Refusing: not the disposable card-1093-oom.service cgroup")
root = Path("/sys/fs/cgroup") / entry.lstrip("/")
if (
    int((root / "memory.max").read_text()) != 512 * 1024**2
    or int((root / "memory.swap.max").read_text()) != 0
    or int((root / "memory.oom.group").read_text()) != 1
):
    raise SystemExit("Refusing: isolated cgroup limits not verified")
print("verified isolated cgroup512MiB/swap0/oomgroup1", flush=True)
buffers = []
while True:
    buffers.append(bytearray(32 * 1024**2))
    print("allocated", len(buffers) * 32, "MiB", flush=True)
    time.sleep(0.1)
