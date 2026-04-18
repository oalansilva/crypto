#!/usr/bin/env python3
"""Set workflow DB change status (kanban column) and optionally approve gates.

Used by scripts/archive_change_safe.sh to make archiving atomic-ish across:
- Workflow DB (runtime source of truth)
- OpenSpec archive artifact

This script is intentionally small and side-effect limited.

Examples:
  WORKFLOW_DB_ENABLED=1 \
    .venv/bin/python backend/scripts/set_change_status.py \
      --project crypto --change my-change --status Archived \
      --approve-gates "PO,DEV,QA,Approval,Homologation"

Exit codes:
  0 success
  2 not found
  3 workflow db disabled/misconfigured
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Iterable

from sqlalchemy.orm import Session

from app.workflow_database import WorkflowSessionLocal, init_workflow_schema
from app.workflow_models import (
    ApprovalScope,
    ApprovalState,
    Change,
    Project,
    WorkflowApproval,
)


def _latest_gate_states(db: Session, *, change_pk: str) -> dict[str, str]:
    out: dict[str, str] = {}
    items = (
        db.query(WorkflowApproval)
        .filter(WorkflowApproval.scope == ApprovalScope.change)
        .filter(WorkflowApproval.change_pk == change_pk)
        .order_by(WorkflowApproval.created_at.asc())
        .all()
    )
    for a in items:
        out[str(a.gate)] = str(a.state.value)
    return out


def _ensure_gate_approved(db: Session, *, change_pk: str, gate: str, actor: str) -> bool:
    """Ensure latest gate state is approved; if not, append an approved record."""

    gate = (gate or "").strip()
    if not gate:
        return False

    latest = (
        db.query(WorkflowApproval)
        .filter(WorkflowApproval.scope == ApprovalScope.change)
        .filter(WorkflowApproval.change_pk == change_pk)
        .filter(WorkflowApproval.gate == gate)
        .order_by(WorkflowApproval.created_at.desc())
        .first()
    )

    if latest and latest.state == ApprovalState.approved:
        return False

    db.add(
        WorkflowApproval(
            scope=ApprovalScope.change,
            gate=gate,
            state=ApprovalState.approved,
            change_pk=change_pk,
            work_item_id=None,
            actor=actor,
            note="Set to approved by set_change_status.py",
        )
    )
    return True


def _parse_gates(raw: str | None) -> list[str]:
    if not raw:
        return []
    # allow comma-separated and/or repeated flags
    parts = [p.strip() for p in raw.split(",")]
    return [p for p in parts if p]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="crypto")
    ap.add_argument("--change", required=True, help="Change id (Change.change_id)")
    ap.add_argument("--status", required=True, help="New Change.status (e.g. Archived)")
    ap.add_argument(
        "--approve-gates",
        default=None,
        help="Comma-separated list of gates to force-approve (append approval records if needed)",
    )
    ap.add_argument("--actor", default=os.getenv("USER") or "archive-script")
    ap.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON with previous/new status and gate states",
    )
    args = ap.parse_args()

    init_workflow_schema()
    if WorkflowSessionLocal is None:
        print("ERROR: Workflow DB disabled. Set WORKFLOW_DB_ENABLED=1", flush=True)
        return 3

    with WorkflowSessionLocal() as db:
        p = db.query(Project).filter(Project.slug == args.project).first()
        if not p:
            print(f"ERROR: project not found: {args.project}")
            return 2

        c = (
            db.query(Change)
            .filter(Change.project_id == p.id, Change.change_id == args.change)
            .first()
        )
        if not c:
            print(f"ERROR: change not found in workflow DB: {args.project}/{args.change}")
            return 2

        prev = (c.status or "").strip() or "DEV"
        new = (args.status or "").strip()
        if not new:
            print("ERROR: empty --status")
            return 1

        c.status = new

        approved = []
        for g in _parse_gates(args.approve_gates):
            if _ensure_gate_approved(db, change_pk=c.id, gate=g, actor=args.actor):
                approved.append(g)

        db.commit()

        gates = _latest_gate_states(db, change_pk=c.id)

    if args.json:
        print(
            json.dumps(
                {
                    "project": args.project,
                    "change": args.change,
                    "previous_status": prev,
                    "new_status": new,
                    "approved_gates": approved,
                    "gate_states": gates,
                },
                ensure_ascii=False,
            )
        )
    else:
        # stdout is used by bash wrapper to capture previous status
        print(prev)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
