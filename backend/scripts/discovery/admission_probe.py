"""Read-only admission probe against the cgroup of a Discovery unit (#1110).

Checks that the limits installed on ``criptofarol-{dev,prod}-discovery-worker.service``
equal the resource profile of the environment, plus the host reserve
(MemTotal, MemAvailable, SwapFree, disk). Proves that code and unit match.

Usage: ``admission_probe.py --env prod`` (exit 0 = admitted, 1 = refused).
"""

import argparse
import json
import sys
from pathlib import Path

from app.services.discovery_resources import (
    OperationalFailure,
    PROFILE_TABLE,
    ResourceProfile,
    admission,
    unit_cgroup,
)


def probe(env, group=None, spool_root=None, memory=None):
    profile = ResourceProfile.named(env)
    group = Path(group) if group else unit_cgroup(env)
    if spool_root is None:
        private = Path(f"/var/tmp/criptofarol-{env}-discovery")
        spool_root = private if private.is_dir() else Path("/var/tmp")
    return admission(profile, spool_root=spool_root, group=group, memory=memory)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=True, choices=sorted(PROFILE_TABLE))
    parser.add_argument("--group", help="cgroup directory; default: the environment's unit")
    args = parser.parse_args(argv)
    try:
        result = {"admitted": True, "env": args.env, "profile": probe(args.env, args.group)}
        code = 0
    except OperationalFailure as exc:
        result = {"admitted": False, "env": args.env, "code": exc.code}
        code = 1
    print(json.dumps(result, sort_keys=True))
    return code


if __name__ == "__main__":
    sys.exit(main())
