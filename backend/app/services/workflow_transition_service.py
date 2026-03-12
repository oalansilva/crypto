from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from sqlalchemy.orm import Session

from app.workflow_models import ApprovalScope, ApprovalState, Change, WorkflowApproval

KANBAN_COLUMNS = [
    "Pending",
    "PO",
    "DESIGN",
    "Alan approval",
    "DEV",
    "QA",
    "Alan homologation",
    "Archived",
]

GATED_COLUMNS = {
    "PO",
    "DESIGN",
    "Alan approval",
    "DEV",
    "QA",
    "Alan homologation",
    "Archived",
}

GATE_SEQUENCE = ["PO", "DESIGN", "Alan approval", "DEV", "QA", "Alan homologation"]


@dataclass(frozen=True)
class GateDecision:
    gate: str
    state: ApprovalState
    note: str


def _normalize_status(status: str | None) -> str:
    value = (status or "").strip()
    if value.lower() == "archived":
        return "Archived"
    if value not in KANBAN_COLUMNS:
        return "DEV"
    return value


def desired_gate_states_for_column(column: str) -> list[GateDecision]:
    target = _normalize_status(column)

    if target == "Pending":
        approved_until = -1
    elif target == "PO":
        approved_until = -1
    elif target == "DESIGN":
        approved_until = 0
    elif target == "Alan approval":
        approved_until = 1
    elif target == "DEV":
        approved_until = 2
    elif target == "QA":
        approved_until = 3
    elif target == "Alan homologation":
        approved_until = 4
    else:  # Archived
        approved_until = 5

    out: list[GateDecision] = []
    for idx, gate in enumerate(GATE_SEQUENCE):
        desired = ApprovalState.approved if idx <= approved_until else ApprovalState.pending
        out.append(
            GateDecision(
                gate=gate,
                state=desired,
                note=f"auto: synced gate state after Kanban transition to {target}",
            )
        )
    return out


def sync_change_gates_for_column(
    db: Session,
    *,
    change: Change,
    target_column: str,
    actor: str = "kanban",
) -> bool:
    target = _normalize_status(target_column)
    mutated = False

    latest: dict[str, ApprovalState] = {}
    approvals = (
        db.query(WorkflowApproval)
        .filter(WorkflowApproval.scope == ApprovalScope.change, WorkflowApproval.change_pk == change.id)
        .order_by(WorkflowApproval.created_at.asc())
        .all()
    )
    for approval in approvals:
        latest[approval.gate] = approval.state

    for decision in desired_gate_states_for_column(target):
        if latest.get(decision.gate) == decision.state:
            continue
        db.add(
            WorkflowApproval(
                scope=ApprovalScope.change,
                gate=decision.gate,
                state=decision.state,
                change_pk=change.id,
                work_item_id=None,
                actor=actor,
                note=decision.note,
            )
        )
        mutated = True

    current_status = (change.status or "").strip()
    normalized_current = _normalize_status(current_status)
    if current_status != target or normalized_current != target:
        change.status = target
        mutated = True

    return mutated
