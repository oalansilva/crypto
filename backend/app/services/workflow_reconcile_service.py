"""Workflow runtime reconciliation helpers.

Problem
-------
Agents often complete OpenSpec artifacts (proposal/specs/design/tasks) and/or leave
comments/evidence, but forget to update the workflow DB (wf_changes.status and
wf_approvals). The Kanban UI is DB-backed, so cards can get stuck in an earlier
column even though the work is effectively past that gate.

Goal
----
Provide a minimal reconciliation mechanism that never advances a card or
approves a human gate from file presence. It only invalidates an already-issued
design approval when its immutable evidence no longer matches.

This is intentionally best-effort and idempotent.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.orm import Session

from app.services.coordination_service import project_root
from app.workflow_models import ApprovalScope, ApprovalState, Change, WorkflowApproval
from app.services.workflow_transition_service import (
    KANBAN_COLUMNS,
    approval_matches_current_evidence,
    canonicalize_status,
    invalidate_design_approval,
    invalidate_qa_round,
)

KANBAN_FLOW_ORDER = KANBAN_COLUMNS


def _flow_index(col: str) -> int:
    return KANBAN_FLOW_ORDER.index(canonicalize_status(col))


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


def reconcile_change_forward(db: Session, *, change: Change) -> bool:
    """Reconcile a single change.

    Returns True if any DB mutation occurred.
    """

    current = canonicalize_status(change.status)
    monitored = {
        "Pronto para Dev",
        "Em desenvolvimento",
        "Code Review",
        "QA",
    }
    if current not in monitored or not change.design_approval_valid:
        return False
    if change.ui_impact == "none" and (change.ui_impact_justification or "").strip():
        return False
    if approval_matches_current_evidence(change, project_root()):
        return False
    invalidate_design_approval(change)
    if current == "QA":
        invalidate_qa_round(db, change, actor="reconcile", reason="design evidence changed")
    change.status = "Aprovação de Design"
    db.add(
        WorkflowApproval(
            scope=ApprovalScope.change,
            gate="Design Approval",
            state=ApprovalState.rejected,
            change_pk=change.id,
            work_item_id=None,
            actor="reconcile",
            note="Approval obsolete: current evidence no longer matches the approved digest.",
        )
    )
    db.commit()
    db.refresh(change)
    return True
