"""Local authenticated administrative acknowledgement; never resets attempts."""

import argparse
import os
import pwd
import subprocess
from pathlib import Path

from app.services.discovery_resources import (
    PROFILE_TABLE,
    ResourceProfile,
    admission,
    discovery_environment,
    discovery_unit,
    unit_cgroup,
)


def derive_target(env, group=None):
    """(profile, unit, cgroup) of the acknowledged environment (DEV or PROD)."""
    profile = ResourceProfile.named(env)
    return profile, discovery_unit(env), Path(group) if group else unit_cgroup(env)


def groups_are_empty(unit, group):
    if (group / "cgroup.procs").exists():
        return not (group / "cgroup.procs").read_text().strip()
    # systemd removes an empty stopped service's cgroup. Check authoritative
    # service state as well; absence alone is not evidence of cleanup.
    properties = subprocess.check_output(
        [
            "systemctl",
            "show",
            unit,
            "--property=MainPID",
            "--property=ActiveState",
            "--property=ControlGroup",
        ],
        text=True,
    )
    values = dict(line.split("=", 1) for line in properties.splitlines())
    return (
        values["MainPID"] == "0"
        and values["ActiveState"] in ("inactive", "failed")
        and not values["ControlGroup"]
    )


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--reason", required=True)
    parser.add_argument(
        "--env",
        choices=sorted(PROFILE_TABLE),
        help="environment whose circuit is acknowledged (default: DISCOVERY_RESOURCE_PROFILE or dev)",
    )
    parser.add_argument(
        "--group", help="cgroup directory to check; default: the environment's Discovery unit"
    )
    args = parser.parse_args(argv)
    if os.geteuid() != 0:
        raise SystemExit("Local root authentication is required")
    env = args.env or os.getenv("DISCOVERY_RESOURCE_PROFILE", "dev")
    if env not in PROFILE_TABLE:
        raise SystemExit(f"Unknown environment {env!r}; use --env dev|prod")
    # The circuit row is keyed by discovery_environment(): pin it to --env and
    # refuse if something else (a criptofarol-* cgroup) would override it.
    os.environ["DISCOVERY_RESOURCE_PROFILE"] = env
    if discovery_environment() != env:
        raise SystemExit(
            f"Environment resolves to {discovery_environment()!r}, not {env!r}; refusing"
        )
    profile, unit, group = derive_target(env, args.group)
    from app.database import SessionLocal
    from app.services.discovery_recovery import acknowledge

    # Missing/unverified cgroup cannot count as a healthy admission check.
    # Admission runs in this process's own (bounded) cgroup against the
    # environment's profile.
    healthy = bool(admission(profile))
    groups_empty = groups_are_empty(unit, group)
    with SessionLocal() as db:
        acknowledge(db, pwd.getpwuid(os.geteuid()).pw_name, args.reason, healthy, groups_empty)


if __name__ == "__main__":
    main()
