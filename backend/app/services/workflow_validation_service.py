"""Workflow validation service.

Provides validation functions for:
- Approval gates (proposal.md, review-ptbr.md, tasks.md)
- Story closure (child bugs must be done/canceled)
- Handoff comments (require status, evidence, next_step)
- Sync verification (compare DB with OpenSpec files)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.workflow_models import (
    Change,
    WorkItem,
    WorkItemState,
    WorkItemType,
)


REPO_ROOT = Path(__file__).resolve().parents[3]


class ValidationError(Exception):
    """Raised when validation fails."""

    def __init__(self, code: str, message: str, details: dict | None = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


@dataclass
class ApprovalGateStatus:
    """Status of approval gate validation."""
    change_id: str
    has_proposal: bool
    has_review: bool
    has_tasks: bool
    is_valid: bool
    missing_files: list[str]


@dataclass
class StoryClosureStatus:
    """Status of story closure validation."""
    story_id: str
    child_bugs: list[dict]
    is_valid: bool
    blocking_bugs: list[dict]


@dataclass
class HandoffCommentStatus:
    """Status of handoff comment validation."""
    is_valid: bool
    missing_fields: list[str]
    errors: list[str]


@dataclass
class SyncDiscrepancy:
    """A discrepancy found during sync verification."""
    type: str  # "status", "work_item", "gate"
    location: str  # "db" or "file"
    description: str
    expected: str
    actual: str


@dataclass
class SyncVerificationResult:
    """Result of sync verification."""
    change_id: str
    is_synced: bool
    discrepancies: list[SyncDiscrepancy]
    db_status: str | None
    file_status: str | None


def validate_approval_gate(change_id: str) -> ApprovalGateStatus:
    """Validate approval gate requirements for a change.
    
    Checks for:
    - proposal.md: Change proposal document
    - review-ptbr.md: PO approval document
    - tasks.md: Task list
    
    Args:
        change_id: The change identifier (e.g., "workflow-backend-enforcement")
        
    Returns:
        ApprovalGateStatus with validation results
    """
    change_path = REPO_ROOT / "openspec" / "changes" / change_id
    
    if not change_path.exists():
        # Check archive
        archive_path = REPO_ROOT / "openspec" / "changes" / "archive"
        if archive_path.exists():
            # Try to find in archive by pattern
            matches = list(archive_path.glob(f"????-??-??-{change_id}/"))
            if matches:
                change_path = matches[0]
    
    has_proposal = (change_path / "proposal.md").exists()
    has_review = (change_path / "review-ptbr.md").exists()
    has_tasks = (change_path / "tasks.md").exists()
    
    missing_files = []
    if not has_proposal:
        missing_files.append("proposal.md")
    if not has_review:
        missing_files.append("review-ptbr.md")
    if not has_tasks:
        missing_files.append("tasks.md")
    
    is_valid = has_proposal and has_review and has_tasks
    
    return ApprovalGateStatus(
        change_id=change_id,
        has_proposal=has_proposal,
        has_review=has_review,
        has_tasks=has_tasks,
        is_valid=is_valid,
        missing_files=missing_files,
    )


def validate_story_closure(db: Session, story_id: str) -> StoryClosureStatus:
    """Validate that a story can be closed.
    
    A story can only be closed (done) when all child bugs are either done or canceled.
    
    Args:
        db: Database session
        story_id: The story work item ID
        
    Returns:
        StoryClosureStatus with validation results
    """
    story = db.query(WorkItem).filter(WorkItem.id == story_id).first()
    
    if not story:
        raise HTTPException(status_code=404, detail=f"Story {story_id} not found")
    
    if story.type != WorkItemType.story:
        raise HTTPException(status_code=400, detail=f"Work item {story_id} is not a story")
    
    # Get child bugs
    child_bugs = db.query(WorkItem).filter(
        WorkItem.parent_id == story_id,
        WorkItem.type == WorkItemType.bug
    ).all()
    
    child_bugs_data = []
    blocking_bugs = []
    
    for bug in child_bugs:
        bug_data = {
            "id": bug.id,
            "title": bug.title,
            "state": bug.state.value,
        }
        child_bugs_data.append(bug_data)
        
        if bug.state not in (WorkItemState.done, WorkItemState.canceled):
            blocking_bugs.append(bug_data)
    
    is_valid = len(blocking_bugs) == 0
    
    return StoryClosureStatus(
        story_id=story_id,
        child_bugs=child_bugs_data,
        is_valid=is_valid,
        blocking_bugs=blocking_bugs,
    )


def validate_handoff_comment(comment: str) -> HandoffCommentStatus:
    """Validate that a handoff comment has required fields.
    
    Required fields:
    - status: Current status of work
    - evidence: Evidence of completion (links, screenshots, etc.)
    - next_step: What should happen next
    
    Args:
        comment: The comment text to validate
        
    Returns:
        HandoffCommentStatus with validation results
    """
    import re
    
    # Normalize comment text
    text = comment.strip().lower()
    
    missing_fields = []
    errors = []
    
    # Check for status field
    status_patterns = [
        r"status[:\s]+",
        r"estado[:\s]+",
        r"feito[:\s]+",
        r"completed[:\s]+",
        r"status\s*=\s*",
    ]
    has_status = any(re.search(pattern, text) for pattern in status_patterns)
    if not has_status:
        missing_fields.append("status")
    
    # Check for evidence field
    evidence_patterns = [
        r"evidence[:\s]+",
        r"evidência[:\s]+",
        r"prova[:\s]+",
        r"link[:\s]+",
        r"screenshot[:\s]+",
        r"print[:\s]+",
    ]
    has_evidence = any(re.search(pattern, text) for pattern in evidence_patterns)
    if not has_evidence:
        missing_fields.append("evidence")
    
    # Check for next_step field
    next_step_patterns = [
        r"next\s*step[:\s]+",
        r"pr[óo]ximo\s+passo[:\s]+",
        r"下一步[:\s]+",
        r"下一步[:\s]+",
        r"what['\s]s\s+next",
        r"pending[:\s]+",
    ]
    has_next_step = any(re.search(pattern, text) for pattern in next_step_patterns)
    if not has_next_step:
        missing_fields.append("next_step")
    
    is_valid = len(missing_fields) == 0
    
    if is_valid and not (has_status and has_evidence and has_next_step):
        # Double check - if patterns matched but parsing failed
        errors.append("Comment has content but could not verify all required fields")
    
    return HandoffCommentStatus(
        is_valid=is_valid,
        missing_fields=missing_fields,
        errors=errors,
    )


def _get_change_status_from_meta(change_id: str) -> Optional[str]:
    """Get status from meta.yaml in OpenSpec."""
    change_path = REPO_ROOT / "openspec" / "changes" / change_id
    
    if not change_path.exists():
        # Check archive
        archive_path = REPO_ROOT / "openspec" / "changes" / "archive"
        if archive_path.exists():
            matches = list(archive_path.glob(f"????-??-??-{change_id}/"))
            if matches:
                change_path = matches[0]
    
    meta_file = change_path / "meta.yaml"
    if not meta_file.exists():
        return None
    
    import yaml
    try:
        with open(meta_file, "r") as f:
            meta = yaml.safe_load(f)
        return meta.get("status")
    except Exception:
        return None


def _get_tasks_from_file(change_id: str) -> list[dict]:
    """Get tasks from tasks.md in OpenSpec."""
    change_path = REPO_ROOT / "openspec" / "changes" / change_id
    
    if not change_path.exists():
        # Check archive
        archive_path = REPO_ROOT / "openspec" / "changes" / "archive"
        if archive_path.exists():
            matches = list(archive_path.glob(f"????-??-??-{change_id}/"))
            if matches:
                change_path = matches[0]
    
    tasks_file = change_path / "tasks.md"
    if not tasks_file.exists():
        return []
    
    tasks = []
    import re
    
    try:
        with open(tasks_file, "r") as f:
            content = f.read()
        
        # Parse task lines like "- [ ] 1.1 Task description" or "- [x] 1.1 Task description"
        for line in content.split("\n"):
            match = re.match(r"^-\s*\[([ x])\]\s+(\d+(?:\.\d+)*)\s+(.+)$", line.strip())
            if match:
                checked = match.group(1) == "x"
                code = match.group(2)
                description = match.group(3).strip()
                tasks.append({
                    "code": code,
                    "description": description,
                    "done": checked,
                })
    except Exception:
        pass
    
    return tasks


def verify_sync(change_id: str, db: Session) -> SyncVerificationResult:
    """Verify that the DB state matches the OpenSpec files.
    
    Compares:
    - Change status in DB vs meta.yaml
    - Work items in DB vs tasks.md
    
    Args:
        change_id: The change identifier
        db: Database session
        
    Returns:
        SyncVerificationResult with any discrepancies found
    """
    discrepancies: list[SyncDiscrepancy] = []
    
    # Get DB change
    change = db.query(Change).filter(Change.change_id == change_id).first()
    db_status = change.status if change else None
    
    # Get file status
    file_status = _get_change_status_from_meta(change_id)
    
    # Compare status
    if db_status and file_status and db_status.lower() != file_status.lower():
        discrepancies.append(SyncDiscrepancy(
            type="status",
            location="db",
            description=f"DB status '{db_status}' differs from meta.yaml status '{file_status}'",
            expected=file_status,
            actual=db_status,
        ))
    
    # Get tasks from file
    file_tasks = _get_tasks_from_file(change_id)
    
    # Get work items from DB
    if change:
        db_work_items = db.query(WorkItem).filter(WorkItem.change_pk == change.id).all()
        
        # Create maps
        db_tasks_by_code = {}
        for item in db_work_items:
            # Try to extract code from title (format: "1.1 Task name")
            match = re.match(r"^(\d+(?:\.\d+)*)\s+(.+)$", item.title.strip())
            if match:
                code = match.group(1)
                db_tasks_by_code[code] = {
                    "title": item.title,
                    "state": item.state.value,
                }
        
        # Check for missing in DB
        for task in file_tasks:
            code = task["code"]
            if code not in db_tasks_by_code:
                discrepancies.append(SyncDiscrepancy(
                    type="work_item",
                    location="db",
                    description=f"Task '{code}' exists in tasks.md but not in DB",
                    expected=f"Task {code} in DB with state",
                    actual="Not found in DB",
                ))
        
        # Check for extra in DB
        db_codes = set(db_tasks_by_code.keys())
        file_codes = {t["code"] for t in file_tasks}
        
        for code in db_codes - file_codes:
            discrepancies.append(SyncDiscrepancy(
                type="work_item",
                location="file",
                description=f"Task '{code}' exists in DB but not in tasks.md",
                expected="Not in tasks.md",
                actual=f"Task {code} in DB with state {db_tasks_by_code[code]['state']}",
            ))
    
    is_synced = len(discrepancies) == 0
    
    return SyncVerificationResult(
        change_id=change_id,
        is_synced=is_synced,
        discrepancies=discrepancies,
        db_status=db_status,
        file_status=file_status,
    )


# Import re at module level
import re
