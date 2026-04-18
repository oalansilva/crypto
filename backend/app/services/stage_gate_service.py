from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.workflow_models import Change, WorkItem

STAGE_ORDER = [
    "Pending",
    "PO",
    "DESIGN",
    "Approval",
    "DEV",
    "QA",
    "Homologation",
    "Archived",
    "Canceled",
]

STAGE_GATES = {
    "PO": {"required_agent": "PO", "previous_stage": "Pending"},
    "DESIGN": {"required_agent": "DESIGN", "previous_stage": "PO"},
    "Approval": {"required_agent": "DESIGN", "previous_stage": "DESIGN"},
    "DEV": {"required_agent": "DEV", "previous_stage": "Approval"},
    "QA": {"required_agent": "DEV", "previous_stage": "DEV"},
    "Homologation": {"required_agent": "QA", "previous_stage": "QA"},
    "Archived": {"required_agent": None, "previous_stage": "Homologation"},
    "Canceled": {"required_agent": None, "previous_stage": None},
}


@dataclass
class StageGateResult:
    allowed: bool
    current_stage: str
    target_stage: str
    skipped_stage: Optional[str] = None
    message: Optional[str] = None


def _normalize_stage(stage: Optional[str]) -> str:
    """Normalize stage string to a valid stage name."""
    if not stage:
        return "Pending"
    normalized = stage.strip()
    if normalized == "Alan homologation":
        return "Homologation"
    if normalized.lower() == "archived":
        return "Archived"
    if normalized.lower() == "canceled":
        return "Canceled"
    if normalized not in STAGE_ORDER:
        return "Pending"
    return normalized


def get_stage_index(stage: str) -> int:
    """Get the index of a stage in the stage order."""
    normalized = _normalize_stage(stage)
    return STAGE_ORDER.index(normalized)


def validate_stage_transition(current_stage: Optional[str], target_stage: str) -> StageGateResult:
    """Validate if a transition from current_stage to target_stage is allowed.

    This function validates stage transitions based on the workflow rules:
    - Cards cannot skip stages
    - Each stage requires proper agent handoff

    Args:
        current_stage: The current stage of the card
        target_stage: The target stage to transition to

    Returns:
        StageGateResult with validation result
    """
    current = _normalize_stage(current_stage)
    target = _normalize_stage(target_stage)

    if current == target:
        return StageGateResult(
            allowed=True,
            current_stage=current,
            target_stage=target,
        )

    current_idx = get_stage_index(current)
    target_idx = get_stage_index(target)

    if target_idx <= current_idx:
        if target in {"Archived", "Canceled"}:
            return StageGateResult(
                allowed=True,
                current_stage=current,
                target_stage=target,
            )
        return StageGateResult(
            allowed=False,
            current_stage=current,
            target_stage=target,
            message=f"Backward transitions are not allowed. Current: {current}, Target: {target}",
        )

    expected_stage_idx = current_idx + 1
    if target_idx != expected_stage_idx:
        # Backward moves to Canceled/Archived are always allowed
        if target in {"Archived", "Canceled"}:
            return StageGateResult(
                allowed=True,
                current_stage=current,
                target_stage=target,
            )
        skipped_stage = STAGE_ORDER[expected_stage_idx]
        return StageGateResult(
            allowed=False,
            current_stage=current,
            target_stage=target,
            skipped_stage=skipped_stage,
            message=f"Cannot skip stage '{skipped_stage}'. Move through stages sequentially.",
        )

    return StageGateResult(
        allowed=True,
        current_stage=current,
        target_stage=target,
    )


def can_transition_to_stage(
    db: Session,
    work_item_id: str,
    target_stage: str,
    agent: Optional[str] = None,
) -> StageGateResult:
    """Check if a work item can transition to a specific stage.

    This function checks both the stage gate validation and whether
    the appropriate agent has acted on the item.

    Args:
        db: Database session
        work_item_id: The ID of the work item
        target_stage: The target stage to transition to
        agent: The agent attempting the transition (optional)

    Returns:
        StageGateResult with validation result
    """
    work_item = db.query(WorkItem).filter(WorkItem.id == work_item_id).first()
    if not work_item:
        return StageGateResult(
            allowed=False,
            current_stage="Unknown",
            target_stage=target_stage,
            message=f"Work item '{work_item_id}' not found",
        )

    change = db.query(Change).filter(Change.id == work_item.change_pk).first()
    if not change:
        return StageGateResult(
            allowed=False,
            current_stage="Unknown",
            target_stage=target_stage,
            message=f"Change not found for work item '{work_item_id}'",
        )

    current_stage = change.status or "Pending"

    gate_result = validate_stage_transition(current_stage, target_stage)

    if not gate_result.allowed:
        return gate_result

    gate_config = STAGE_GATES.get(target_stage, {})
    required_agent = gate_config.get("required_agent")

    if required_agent and agent and agent != required_agent:
        return StageGateResult(
            allowed=False,
            current_stage=current_stage,
            target_stage=target_stage,
            message=f"Stage '{target_stage}' requires agent '{required_agent}', not '{agent}'",
        )

    return gate_result


def record_stage_start(
    db: Session,
    work_item_id: str,
    agent: str,
) -> WorkItem:
    """Record that an agent has started working on a stage.

    Args:
        db: Database session
        work_item_id: The ID of the work item
        agent: The agent starting the stage

    Returns:
        Updated work item
    """
    work_item = db.query(WorkItem).filter(WorkItem.id == work_item_id).first()
    if not work_item:
        raise HTTPException(status_code=404, detail=f"Work item '{work_item_id}' not found")

    from datetime import datetime, timezone

    work_item.stage_started_at = datetime.now(timezone.utc)
    work_item.last_agent_acted = agent
    db.commit()
    db.refresh(work_item)

    return work_item


def record_stage_completion(
    db: Session,
    work_item_id: str,
    agent: str,
) -> WorkItem:
    """Record that an agent has completed a stage.

    Args:
        db: Database session
        work_item_id: The ID of the work item
        agent: The agent completing the stage

    Returns:
        Updated work item
    """
    work_item = db.query(WorkItem).filter(WorkItem.id == work_item_id).first()
    if not work_item:
        raise HTTPException(status_code=404, detail=f"Work item '{work_item_id}' not found")

    from datetime import datetime, timezone

    work_item.stage_completed_at = datetime.now(timezone.utc)
    work_item.last_agent_acted = agent
    db.commit()
    db.refresh(work_item)

    return work_item


def require_handoff_fields(handoff_data: dict) -> dict:
    """Validate that handoff data contains required fields.

    Required fields: status, evidence, next_step

    Args:
        handoff_data: Dictionary containing handoff information

    Returns:
        Validated handoff data

    Raises:
        HTTPException: If required fields are missing
    """
    required_fields = ["status", "evidence", "next_step"]
    missing_fields = [f for f in required_fields if not handoff_data.get(f)]

    if missing_fields:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "missing_handoff_fields",
                "message": f"Missing required handoff fields: {', '.join(missing_fields)}",
                "missing_fields": missing_fields,
            },
        )

    return handoff_data
