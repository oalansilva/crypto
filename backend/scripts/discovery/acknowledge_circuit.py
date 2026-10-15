"""Local authenticated administrative acknowledgement; never resets attempts."""

import argparse
import os
import pwd
import subprocess
from pathlib import Path
from app.database import SessionLocal
from app.services.discovery_recovery import acknowledge
from app.services.discovery_resources import admission

parser = argparse.ArgumentParser()
parser.add_argument("--reason", required=True)
parser.add_argument(
    "--group", default="/sys/fs/cgroup/system.slice/criptofarol-dev-discovery-worker.service"
)
args = parser.parse_args()
if os.geteuid() != 0:
    raise SystemExit("Local root authentication is required")
group = Path(args.group)
# Missing/unverified cgroup cannot count as a healthy admission check.
healthy = bool(admission())  # Run this command in a separate, bounded admission probe.
if (group / "cgroup.procs").exists():
    groups_empty = not (group / "cgroup.procs").read_text().strip()
else:
    # systemd removes an empty stopped service's cgroup. Check authoritative
    # service state as well; absence alone is not evidence of cleanup.
    properties = subprocess.check_output(
        [
            "systemctl",
            "show",
            "criptofarol-dev-discovery-worker.service",
            "--property=MainPID",
            "--property=ActiveState",
            "--property=ControlGroup",
        ],
        text=True,
    )
    values = dict(line.split("=", 1) for line in properties.splitlines())
    groups_empty = (
        values["MainPID"] == "0"
        and values["ActiveState"] in ("inactive", "failed")
        and not values["ControlGroup"]
    )
with SessionLocal() as db:
    acknowledge(db, pwd.getpwuid(os.geteuid()).pw_name, args.reason, healthy, groups_empty)
