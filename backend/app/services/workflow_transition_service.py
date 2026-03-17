from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from fastapi import HTTPException

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
    "Canceled",
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

_ALLOWED_FORWARD_MOVES = {
    "Pending": {"PO", "Canceled"},
    "PO": {"DESIGN", "Canceled"},
    "DESIGN": {"Alan approval", "Canceled"},
    "Alan approval": {"DEV", "Canceled"},
    "DEV": {"QA", "Canceled"},
    "QA": {"Alan homologation", "Canceled"},
    "Alan homologation": {"Archived", "Canceled"},
    "Archived": set(),
    "Canceled": set(),
}


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


def validate_kanban_transition(*, current_column: str | None, target_column: str | None) -> tuple[str, str]:
    current = _normalize_status(current_column)
    target = _normalize_status(target_column)

    if current == target:
        return current, target

    current_idx = KANBAN_COLUMNS.index(current)
    target_idx = KANBAN_COLUMNS.index(target)

    if current == "Archived":
        raise HTTPException(
            status_code=409,
            detail={
                "code": "invalid_kanban_transition",
                "message": "Archived cards cannot be moved back into the active workflow.",
                "current": current,
                "target": target,
                "allowed_targets": [],
            },
        )

    is_backward = target_idx < current_idx
    is_allowed_forward = target in _ALLOWED_FORWARD_MOVES.get(current, set())
    if not is_backward and not is_allowed_forward:
        allowed_targets = sorted(set(_ALLOWED_FORWARD_MOVES.get(current, set())) | set(KANBAN_COLUMNS[:current_idx]))
        raise HTTPException(
            status_code=409,
            detail={
                "code": "invalid_kanban_transition",
                "message": f"Cannot move card directly from {current} to {target}. Move it through the next workflow gate or send it back to an earlier stage.",
                "current": current,
                "target": target,
                "allowed_targets": allowed_targets,
            },
        )

    return current, target


def sync_change_gates_for_column(
    db: Session,
    *,
    change: Change,
    target_column: str,
    actor: str = "kanban",
) -> bool:
    _current, target = validate_kanban_transition(current_column=change.status, target_column=target_column)
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
