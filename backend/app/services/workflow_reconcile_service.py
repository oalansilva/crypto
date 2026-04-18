"""Workflow runtime reconciliation helpers.

Problem
-------
Agents often complete OpenSpec artifacts (proposal/specs/design/tasks) and/or leave
comments/evidence, but forget to update the workflow DB (wf_changes.status and
wf_approvals). The Kanban UI is DB-backed, so cards can get stuck in an earlier
column even though the work is effectively past that gate.

Goal
----
Provide a *minimal, safe* auto-reconciliation mechanism that:
- infers **PO** and **DESIGN** completion from filesystem artifacts (OpenSpec + prototype)
- advances the workflow DB forward (never backward) to the earliest column that
  is still actually pending
- never auto-approves Alan gates (Approval / homologation)

This is intentionally best-effort and idempotent.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from sqlalchemy.orm import Session

from app.services.coordination_service import project_root
from app.workflow_models import ApprovalScope, ApprovalState, Change, WorkflowApproval

KANBAN_FLOW_ORDER = [
    "Pending",
    "PO",
    "DESIGN",
    "Approval",
    "DEV",
    "QA",
    "Homologation",
    "Archived",
]


def _flow_index(col: str) -> int:
    if col == "Alan homologation":
        col = "Homologation"
    try:
        return KANBAN_FLOW_ORDER.index(col)
    except Exception:
        return 0


def _openspec_change_dir(change_id: str) -> Path:
    return project_root() / "openspec" / "changes" / change_id


def _has_any_file(p: Path) -> bool:
    try:
        return p.exists() and any(x.is_file() for x in p.iterdir())
    except Exception:
        return False


@dataclass
class InferredGates:
    po_done: bool
    design_done: bool


def infer_gates_from_artifacts(change_id: str) -> InferredGates:
    """Infer gates based on OpenSpec/prototype artifacts.

    Heuristic (MVP):
    - PO is done when proposal + tasks exist and there's at least one spec file.
    - DESIGN is done when design.md exists OR a prototype folder exists.

    We avoid inferring DEV/QA or Alan gates.
    """

    base = _openspec_change_dir(change_id)
    proposal_ok = (base / "proposal.md").exists()
    tasks_ok = (base / "tasks.md").exists()

    specs_dir = base / "specs"
    specs_ok = specs_dir.exists() and _has_any_file(specs_dir)

    po_done = bool(proposal_ok and tasks_ok and specs_ok)

    design_ok = (base / "design.md").exists()
    proto_ok = (project_root() / "frontend" / "public" / "prototypes" / change_id).exists()
    design_done = bool(design_ok or proto_ok)

    return InferredGates(po_done=po_done, design_done=design_done)


def _latest_gate_states(db: Session, change_pk: str) -> Dict[str, ApprovalState]:
    out: Dict[str, ApprovalState] = {}
    items = (
        db.query(WorkflowApproval)
        .filter(
            WorkflowApproval.scope == ApprovalScope.change, WorkflowApproval.change_pk == change_pk
        )
        .order_by(WorkflowApproval.created_at.asc())
        .all()
    )
    for a in items:
        out[a.gate] = a.state
    return out


def _append_gate_state(
    db: Session,
    *,
    change_pk: str,
    gate: str,
    state: ApprovalState,
    actor: str,
    note: str,
) -> None:
    db.add(
        WorkflowApproval(
            scope=ApprovalScope.change,
            gate=gate,
            state=state,
            change_pk=change_pk,
            work_item_id=None,
            actor=actor,
            note=note,
        )
    )


def reconcile_change_forward(db: Session, *, change: Change) -> bool:
    """Reconcile a single change.

    Returns True if any DB mutation occurred.
    """

    inferred = infer_gates_from_artifacts(change.change_id)
    latest = _latest_gate_states(db, change.id)

    mutated = False

    # Auto-approve PO/DESIGN when artifacts exist.
    if inferred.po_done and latest.get("PO") != ApprovalState.approved:
        _append_gate_state(
            db,
            change_pk=change.id,
            gate="PO",
            state=ApprovalState.approved,
            actor="reconcile",
            note="auto: inferred PO done from openspec artifacts (proposal+tasks+specs)",
        )
        mutated = True

    if inferred.design_done and latest.get("DESIGN") != ApprovalState.approved:
        _append_gate_state(
            db,
            change_pk=change.id,
            gate="DESIGN",
            state=ApprovalState.approved,
            actor="reconcile",
            note="auto: inferred DESIGN done from openspec design/prototype artifacts",
        )
        mutated = True

    # Determine the *minimum* column consistent with gate approvals.
    # Never auto-approve Alan gates; we only read their current state.
    latest2 = latest.copy()
    if inferred.po_done:
        latest2["PO"] = ApprovalState.approved
    if inferred.design_done:
        latest2["DESIGN"] = ApprovalState.approved

    def ok(g: str) -> bool:
        return latest2.get(g) == ApprovalState.approved

    desired_col = "PO"
    if not ok("PO"):
        desired_col = "PO"
    elif not ok("DESIGN"):
        desired_col = "DESIGN"
    elif not ok("Approval"):
        desired_col = "Approval"
    elif not ok("DEV"):
        desired_col = "DEV"
    elif not ok("QA"):
        desired_col = "QA"
    elif not ok("Homologation"):
        desired_col = "Homologation"
    else:
        desired_col = "Archived"

    current = (change.status or "").strip() or "PO"
    if current == "Alan homologation":
        current = "Homologation"
    if current == "Pending":
        return False
    if current.lower() == "archived":
        current = "Archived"
    if current.lower() == "canceled":
        # Don't reconcile changes that were explicitly canceled
        return False

    # Advance forward only.
    if _flow_index(desired_col) > _flow_index(current):
        change.status = desired_col
        mutated = True

    if mutated:
        db.commit()
        db.refresh(change)

    return mutated
