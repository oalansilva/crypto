from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable, Optional

from fastapi import HTTPException

from sqlalchemy.orm import Session

from app.workflow_models import (
    ApprovalScope,
    ApprovalState,
    Change,
    WorkItem,
    WorkItemState,
    WorkItemType,
    WorkflowApproval,
)

if TYPE_CHECKING:
    from app.services.workflow_validation_service import (
        ApprovalGateStatus,
        StoryClosureStatus,
    )

KANBAN_COLUMNS = [
    "Pending",
    "PO",
    "DESIGN",
    "Alan approval",
    "DEV",
    "QA",
    "Homologation",
    "Archived",
    "Canceled",
]

GATED_COLUMNS = {
    "PO",
    "DESIGN",
    "Alan approval",
    "DEV",
    "QA",
    "Homologation",
    "Archived",
}

GATE_SEQUENCE = ["PO", "DESIGN", "Alan approval", "DEV", "QA", "Homologation"]

_ALLOWED_FORWARD_MOVES = {
    "Pending": {"PO", "Canceled"},
    "PO": {"DESIGN", "Canceled"},
    "DESIGN": {"Alan approval", "Canceled"},
    "Alan approval": {"DEV", "Canceled"},
    "DEV": {"QA", "Canceled"},
    "QA": {"Homologation", "Canceled"},
    "Homologation": {"Archived", "Canceled"},
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
    if value == "Alan homologation":
        return "Homologation"
    if value.lower() == "archived":
        return "Archived"
    if value.lower() == "canceled":
        return "Canceled"
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
    elif target == "Homologation":
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


# --- Validation Hooks ---


def validate_transition_hooks(
    db: Session,
    change: Change,
    target_column: str,
) -> None:
    """Run validation hooks before allowing a transition.
    
    This function checks all relevant validations before a change
    can move to the target column.
    
    Args:
        db: Database session
        change: The change being transitioned
        target_column: The target Kanban column
        
    Raises:
        HTTPException: If any validation fails
    """
    target = _normalize_status(target_column)
    
    # Validate DEV -> QA transition
    if target == "QA":
        _validate_dev_to_qa(db, change)
    
    # Validate QA -> Homologation transition  
    if target == "Homologation":
        _validate_qa_to_homologation(db, change)
    
    # Validate Homologation -> Archived transition
    if target == "Archived":
        _validate_homologation_to_archived(db, change)


def _validate_dev_to_qa(db: Session, change: Change) -> None:
    """Validate DEV -> QA transition.
    
    Requires:
    - Approval gate files exist (proposal.md, review-ptbr.md, tasks.md)
    
    Args:
        db: Database session
        change: The change being transitioned
        
    Raises:
        HTTPException: If validation fails
    """
    # Import here to avoid circular imports
    from app.services.workflow_validation_service import validate_approval_gate
    
    gate_status = validate_approval_gate(change.change_id)
    
    if not gate_status.is_valid:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "approval_gate_not_met",
                "message": f"Cannot move to QA. Missing required files: {', '.join(gate_status.missing_files)}",
                "current": change.status,
                "target": "QA",
                "missing_files": gate_status.missing_files,
            },
        )


def _validate_qa_to_homologation(db: Session, change: Change) -> None:
    """Validate QA -> Homologation transition.
    
    Requires:
    - All work items (stories/bugs) are done or canceled
    
    Args:
        db: Database session
        change: The change being transitioned
        
    Raises:
        HTTPException: If validation fails
    """
    # Check that all work items are done or canceled
    open_items = db.query(WorkItem).filter(
        WorkItem.change_pk == change.id,
        WorkItem.state.notin_([WorkItemState.done, WorkItemState.canceled]),
    ).count()
    
    if open_items > 0:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "open_work_items",
                "message": f"Cannot move to Homologation. There are {open_items} open work items.",
                "current": change.status,
                "target": "Homologation",
                "open_items_count": open_items,
            },
        )


def _validate_homologation_to_archived(db: Session, change: Change) -> None:
    """Validate Homologation -> Archived transition.
    
    No additional requirements - this is the final state.
    
    Args:
        db: Database session
        change: The change being transitioned
    """
    # No additional validation needed for archived
    pass


def validate_work_item_transition(
    db: Session,
    work_item: WorkItem,
    target_state: WorkItemState,
) -> None:
    """Validate work item state transition.
    
    Args:
        db: Database session
        work_item: The work item being transitioned
        target_state: The target state
        
    Raises:
        HTTPException: If validation fails
    """
    # Validate story -> done transition
    if work_item.type == WorkItemType.story and target_state == WorkItemState.done:
        _validate_story_done(db, work_item)


def _validate_story_done(db: Session, story: WorkItem) -> None:
    """Validate that a story can be marked as done.
    
    Requires:
    - All child bugs are done or canceled
    
    Args:
        db: Database session
        story: The story being marked done
        
    Raises:
        HTTPException: If validation fails
    """
    # Import here to avoid circular imports
    from app.services.workflow_validation_service import validate_story_closure
    
    closure_status = validate_story_closure(db, story.id)
    
    if not closure_status.is_valid:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "blocking_child_bugs",
                "message": f"Cannot close story. {len(closure_status.blocking_bugs)} child bug(s) are still open.",
                "story_id": story.id,
                "blocking_bugs": closure_status.blocking_bugs,
            },
        )
