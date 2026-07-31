from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.workflow_models import Change, WorkItem
from app.services.workflow_transition_service import (
    KANBAN_COLUMNS,
    canonicalize_status,
    validate_kanban_transition,
)

STAGE_ORDER = KANBAN_COLUMNS

STAGE_GATES = {
    "Design": {"required_agent": "DESIGN"},
    "Aprovação de Design": {"required_agent": "DESIGN"},
    "Pronto para Dev": {"required_agent": None},
    "Em desenvolvimento": {"required_agent": "DEV"},
    "Code Review": {"required_agent": "DEV"},
    "QA": {"required_agent": "QA"},
    "Done": {"required_agent": "QA"},
    "Homologado": {"required_agent": None},
    "Pronto": {"required_agent": None},
    "Cancelado": {"required_agent": None},
}


@dataclass
class StageGateResult:
    allowed: bool
    current_stage: str
    target_stage: str
    skipped_stage: Optional[str] = None
    message: Optional[str] = None


def _normalize_stage(stage: Optional[str]) -> str:
    return canonicalize_status(stage)


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
    try:
        current, target = validate_kanban_transition(
            current_column=current_stage, target_column=target_stage
        )
    except HTTPException as exc:
        detail = exc.detail if isinstance(exc.detail, dict) else {}
        current = str(detail.get("current") or current_stage or "")
        target = str(detail.get("target") or target_stage)
        allowed = detail.get("allowed_targets") or []
        return StageGateResult(
            allowed=False,
            current_stage=current,
            target_stage=target,
            skipped_stage=allowed[0] if allowed else None,
            message=str(detail.get("message") or exc.detail),
        )
    return StageGateResult(allowed=True, current_stage=current, target_stage=target)


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

    current_stage = change.status or "Todo"

    gate_result = validate_stage_transition(current_stage, target_stage)

    if not gate_result.allowed:
        return gate_result

    gate_config = STAGE_GATES.get(canonicalize_status(target_stage), {})
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
