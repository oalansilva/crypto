#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "backend"))

from app.services.upstream_guard import evaluate_upstream_guard  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Block workflow progression until relevant local changes are published upstream.")
    ap.add_argument("--for-status", action="append", default=[], help="Target workflow status being entered (repeatable)")
    ap.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = ap.parse_args()

    result = evaluate_upstream_guard(REPO_ROOT, target_statuses=args.for_status)
    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(f"repo: {result.repo_root}")
        print(f"branch: {result.branch}")
        print(f"targets: {', '.join(result.target_statuses) if result.target_statuses else '-'}")
        print(f"upstream: {result.upstream_ref or '(missing)'}")
        if result.ignored_ephemeral_changes:
            print(f"ignored ephemeral: {', '.join(result.ignored_ephemeral_changes)}")
        if result.ok:
            print("OK: no relevant local changes or unpushed commits are blocking workflow progression.")
        else:
            if result.relevant_tracked_changes:
                print(f"BLOCK tracked: {', '.join(result.relevant_tracked_changes)}")
            if result.relevant_untracked_changes:
                print(f"BLOCK untracked: {', '.join(result.relevant_untracked_changes)}")
            if result.unpushed_commits:
                print(f"BLOCK unpushed commits ({len(result.unpushed_commits)}):")
                for line in result.unpushed_commits:
                    print(f"  - {line}")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
