"""Workflow validation API endpoints.

Provides endpoints for:
- Sync verification: Compare DB with OpenSpec files
- Approval gate validation
- Story closure validation
- Handoff comment validation
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.services.workflow_validation_service import (
    ApprovalGateStatus,
    HandoffCommentStatus,
    StoryClosureStatus,
    SyncVerificationResult,
    validate_approval_gate,
    validate_handoff_comment,
    validate_story_closure,
    verify_sync,
)
from app.workflow_database import get_workflow_db

router = APIRouter(prefix="/api/workflow", tags=["workflow-validation"])


# --- Request/Response Models ---


class ApprovalGateResponse(BaseModel):
    """Response for approval gate validation."""

    change_id: str
    has_proposal: bool
    has_review: bool
    has_tasks: bool
    is_valid: bool
    missing_files: list[str]


class StoryClosureRequest(BaseModel):
    """Request for story closure validation."""

    story_id: str


class StoryClosureResponse(BaseModel):
    """Response for story closure validation."""

    story_id: str
    child_bugs: list[dict]
    is_valid: bool
    blocking_bugs: list[dict]


class HandoffCommentRequest(BaseModel):
    """Request for handoff comment validation."""

    comment: str


class HandoffCommentResponse(BaseModel):
    """Response for handoff comment validation."""

    is_valid: bool
    missing_fields: list[str]
    errors: list[str]


class SyncDiscrepancyResponse(BaseModel):
    """Response for a sync discrepancy."""

    type: str
    location: str
    description: str
    expected: str
    actual: str


class SyncVerificationResponse(BaseModel):
    """Response for sync verification."""

    change_id: str
    is_synced: bool
    discrepancies: list[SyncDiscrepancyResponse]
    db_status: str | None
    file_status: str | None


# --- Endpoints ---


@router.get("/verify-sync/{change_id}", response_model=SyncVerificationResponse)
def verify_sync_endpoint(
    change_id: str,
    db: Session = Depends(get_workflow_db),
) -> SyncVerificationResponse:
    """Verify that the DB state matches the OpenSpec files.

    Compares:
    - Change status in DB vs meta.yaml
    - Work items in DB vs tasks.md

    Returns a list of discrepancies if any exist.
    """
    result = verify_sync(change_id, db)

    return SyncVerificationResponse(
        change_id=result.change_id,
        is_synced=result.is_synced,
        discrepancies=[
            SyncDiscrepancyResponse(
                type=d.type,
                location=d.location,
                description=d.description,
                expected=d.expected,
                actual=d.actual,
            )
            for d in result.discrepancies
        ],
        db_status=result.db_status,
        file_status=result.file_status,
    )


@router.get("/approval-gate/{change_id}", response_model=ApprovalGateResponse)
def approval_gate_endpoint(change_id: str) -> ApprovalGateResponse:
    """Validate approval gate requirements for a change.

    Checks for:
    - proposal.md: Change proposal document
    - review-ptbr.md: PO approval document
    - tasks.md: Task list

    Returns validation status and any missing files.
    """
    result = validate_approval_gate(change_id)

    return ApprovalGateResponse(
        change_id=result.change_id,
        has_proposal=result.has_proposal,
        has_review=result.has_review,
        has_tasks=result.has_tasks,
        is_valid=result.is_valid,
        missing_files=result.missing_files,
    )


@router.post("/validate-story-closure", response_model=StoryClosureResponse)
def validate_story_closure_endpoint(
    request: StoryClosureRequest,
    db: Session = Depends(get_workflow_db),
) -> StoryClosureResponse:
    """Validate that a story can be closed.

    A story can only be closed when all child bugs are either done or canceled.

    Returns validation status and any blocking bugs.
    """
    result = validate_story_closure(db, request.story_id)

    return StoryClosureResponse(
        story_id=result.story_id,
        child_bugs=result.child_bugs,
        is_valid=result.is_valid,
        blocking_bugs=result.blocking_bugs,
    )


@router.post("/validate-handoff-comment", response_model=HandoffCommentResponse)
def validate_handoff_comment_endpoint(
    request: HandoffCommentRequest,
) -> HandoffCommentResponse:
    """Validate that a handoff comment has required fields.

    Required fields:
    - status: Current status of work
    - evidence: Evidence of completion (links, screenshots, etc.)
    - next_step: What should happen next

    Returns validation status and any missing fields.
    """
    result = validate_handoff_comment(request.comment)

    return HandoffCommentResponse(
        is_valid=result.is_valid,
        missing_fields=result.missing_fields,
        errors=result.errors,
    )
