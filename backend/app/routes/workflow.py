"""Workflow DB-backed APIs (MVP).

This router exposes the runtime workflow entities that the DB-backed Kanban
will consume next: changes, work-item tasks, comments, approvals, and handoffs.

Cutover plan: the frontend Kanban will progressively switch from
`/api/coordination/*` (file-backed) to `/api/workflow/*` (DB-backed). For a
smooth transition we also provide a small set of Kanban-compat endpoints under
`/api/workflow/kanban/*` mirroring the legacy response shapes.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re
from contextlib import contextmanager
from typing import Dict, List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
import json
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.middleware.authMiddleware import get_current_admin
from app.services.change_tasks_service import toggle_task_checkbox
from app.services.coordination_service import resolve_change_relative_path
from app.services.workflow_auth import (
    WorkflowActor,
    design_approver_emails,
    get_trusted_qa_actor,
    get_workflow_actor,
    homologation_approver_emails,
    release_approver_emails,
)
from app.services.workflow_transition_service import (
    KANBAN_COLUMNS,
    canonicalize_status,
    approve_current_qa_round,
    invalidate_design_approval,
    invalidate_qa_round,
    transition_change,
    validate_work_item_transition,
)
from app.workflow_database import (
    bootstrap_project_workflow_db,
    get_project_workflow_sessionmaker,
    get_workflow_db,
    get_workflow_db_url,
    sync_project_to_workflow_db,
)
from app.workflow_models import (
    ApprovalScope,
    ApprovalState,
    Change,
    CommentScope,
    HandoffScope,
    Project,
    WorkItem,
    WorkItemState,
    WorkItemType,
    WorkflowApproval,
    WorkflowComment,
    WorkflowHandoff,
)

router = APIRouter(prefix="/api/workflow", tags=["workflow"])

REPO_ROOT = Path(__file__).resolve().parents[3]


def _parse_json_field(value: any) -> List[dict]:
    """Parse a JSON field that might be a string or list."""
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass
    return []


# --- tasks.md sync to workflow DB ---


def _get_tasks_file_path(change_id: str) -> Path:
    """Find tasks.md for a change (active or archived)."""
    # Active changes
    p = REPO_ROOT / "openspec" / "changes" / change_id / "tasks.md"
    if p.exists():
        return p

    # Archived changes: try common date prefix pattern
    archive_root = REPO_ROOT / "openspec" / "changes" / "archive"
    if archive_root.exists():
        # Try prefix pattern: YYYY-MM-DD-<change_id>
        matches = list(archive_root.glob(f"????-??-??-{change_id}/tasks.md"))
        if matches:
            return matches[0]
        # Try exact folder match
        p2 = archive_root / change_id / "tasks.md"
        if p2.exists():
            return p2

    return p


def _parse_tasks_code(text: str) -> Optional[str]:
    """Extract task code like '1.1' from task text."""
    # Match patterns like "1.1", "1.2.3", "2.1" at the start
    match = re.match(r"^(\d+(?:\.\d+)+)\s+(.+)$", text.strip())
    if match:
        return match.group(1)
    return None


def sync_tasks_to_workflow_db(db: Session, change_pk: str, change_id: str) -> List[WorkItem]:
    """Sync tasks.md to wf_work_items table.

    Creates Story work items for each section, and Task work items for each checklist item.
    Uses upsert logic: existing work items are updated (title/description) but their
    state is PRESERVED to avoid overwriting changes made via API (e.g., checkbox toggles).
    Only new items get their initial state from tasks.md.
    """
    tasks_path = _get_tasks_file_path(change_id)
    if not tasks_path.exists():
        return []

    try:
        md = tasks_path.read_text(encoding="utf-8")
    except Exception:
        return []

    # Import the parser from change_tasks_service
    from app.services.change_tasks_service import parse_tasks_markdown

    sections = parse_tasks_markdown(md)
    if not sections:
        return []

    # Build a map of existing work items keyed by (type, description/code) for upsert
    existing_by_code: Dict[tuple, WorkItem] = {}
    for item in db.query(WorkItem).filter(WorkItem.change_pk == change_pk).all():
        # Extract code from description (format: "code:1.1" or "code:1")
        code_match = re.search(r"code:([\d.]+)", item.description or "")
        if code_match:
            key = (item.type.value, code_match.group(1))
            existing_by_code[key] = item

    synced_items: List[WorkItem] = []
    section_code_to_story: Dict[str, WorkItem] = {}

    # First, upsert all stories (sections)
    for section in sections:
        section_title = section.title.strip() if section.title else f"Section"

        # Extract section code (e.g., "1" from "1. Runtime / Backend")
        section_code_match = re.match(r"^(\d+)", section_title)
        section_code = section_code_match.group(1) if section_code_match else None

        # Try to find existing story by code
        story = None
        if section_code:
            story = existing_by_code.get((WorkItemType.story.value, section_code))

        if story:
            # Update existing story title but PRESERVE state
            story.title = section_title
        else:
            # Create new story
            story = WorkItem(
                change_pk=change_pk,
                type=WorkItemType.story,
                state=WorkItemState.queued,
                title=section_title,
                description=f"code:{section_code}" if section_code else "",
                priority=0,
            )
            db.add(story)

        synced_items.append(story)
        if section_code:
            section_code_to_story[section_code] = story

    # Flush stories to get their IDs
    db.flush()

    # Now upsert tasks with proper parent references
    for section in sections:
        section_title = section.title.strip() if section.title else f"Section"
        section_code_match = re.match(r"^(\d+)", section_title)
        section_code = section_code_match.group(1) if section_code_match else None

        parent_story = section_code_to_story.get(section_code)

        for task_item in section.items:
            task_code = _parse_tasks_code(task_item.text)
            task_title = task_item.title or task_item.text

            if not task_code:
                continue

            # Try to find existing task by code
            task = existing_by_code.get((WorkItemType.task.value, task_code))

            if task:
                # Update existing task title but PRESERVE state
                task.title = task_title
                task.description = f"code:{task_code}"
                if parent_story:
                    task.parent_id = parent_story.id
            else:
                # Create new task with initial state from tasks.md
                task = WorkItem(
                    change_pk=change_pk,
                    type=WorkItemType.task,
                    state=WorkItemState.done if task_item.checked else WorkItemState.queued,
                    parent_id=parent_story.id if parent_story else None,
                    title=task_title,
                    description=f"code:{task_code}" if task_code else "",
                    priority=0,
                )
                db.add(task)

            synced_items.append(task)

    db.commit()

    # Refresh all items to get IDs
    for item in synced_items:
        db.refresh(item)

    return synced_items


WorkflowScope = Literal["change", "work_item"]


def _require_db_url() -> str:
    url = get_workflow_db_url()
    if not url:
        raise HTTPException(
            status_code=503, detail="Workflow DB disabled. Set WORKFLOW_DB_ENABLED=1."
        )
    return url


def _slugify_change_title(title: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", title.strip().lower()).strip("-")
    return base or "change"


@router.get("/health")
def workflow_health() -> dict:
    url = _require_db_url()
    return {"enabled": True, "db": "postgres"}


# --- Audit/sync helpers (Phase 1 transition) ---


class CoordinationAuditResponse(BaseModel):
    project_slug: str
    coordination_active: int
    db_changes: int
    missing_in_db: List[str]
    missing_in_coordination: List[str]


@router.get("/audit/coordination", response_model=CoordinationAuditResponse)
def audit_coordination(
    project_slug: str = Query(..., min_length=1), db: Session = Depends(get_workflow_db)
):
    """Audit drift between file-based coordination artifacts and the workflow DB.

    Policy: DB is operational source of truth. Legacy coordination markdown
    files were used as mirrored/audit artifacts during transition.

    This endpoint intentionally stays read-only; it helps detect missing seeds or
    accidentally-created DB-only changes.
    """

    from app.services.coordination_service import (
        list_coordination_changes,
    )  # local import to keep workflow router isolated

    p = _get_project_by_slug(db, project_slug)

    coord = list_coordination_changes()
    active_ids = sorted([it["id"] for it in coord if not bool(it.get("archived")) and it.get("id")])

    db_ids = sorted([c.change_id for c in db.query(Change).filter(Change.project_id == p.id).all()])

    missing_in_db = sorted([cid for cid in active_ids if cid not in set(db_ids)])
    missing_in_coordination = sorted([cid for cid in db_ids if cid not in set(active_ids)])

    return CoordinationAuditResponse(
        project_slug=project_slug,
        coordination_active=len(active_ids),
        db_changes=len(db_ids),
        missing_in_db=missing_in_db,
        missing_in_coordination=missing_in_coordination,
    )


class ProjectCreate(BaseModel):
    slug: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=128)
    root_directory: Optional[str] = Field(default=None, max_length=512)
    database_url: Optional[str] = Field(default=None, max_length=1024)
    frontend_url: Optional[str] = Field(default=None, max_length=512)
    backend_url: Optional[str] = Field(default=None, max_length=512)
    workflow_database_url: Optional[str] = Field(default=None, max_length=1024)
    tech_stack: Optional[str] = Field(default=None, max_length=512)


class ProjectOut(BaseModel):
    id: str
    slug: str
    name: str
    frontend_url: Optional[str] = None
    backend_url: Optional[str] = None
    tech_stack: Optional[str] = None


def _project_out(project: Project) -> ProjectOut:
    return ProjectOut(
        id=project.id,
        slug=project.slug,
        name=project.name,
        frontend_url=project.frontend_url,
        backend_url=project.backend_url,
        tech_stack=project.tech_stack,
    )


@router.get("/projects", response_model=List[ProjectOut])
def list_projects(
    db: Session = Depends(get_workflow_db),
    _admin_user_id: str = Depends(get_current_admin),
):
    items = db.query(Project).order_by(Project.created_at.asc()).all()
    return [_project_out(p) for p in items]


@router.post("/projects", response_model=ProjectOut)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_workflow_db),
    _workflow_actor: WorkflowActor = Depends(get_workflow_actor),
):
    slug = payload.slug.strip()
    name = payload.name.strip()
    workflow_database_url = (
        payload.workflow_database_url.strip() if payload.workflow_database_url else None
    )
    database_url = payload.database_url.strip() if payload.database_url else None
    registry_workflow_url = get_workflow_db_url()

    # Preserve legacy project-creation calls by defaulting to the registry workflow DB
    # when the runtime is already backed by PostgreSQL.
    if not workflow_database_url and registry_workflow_url:
        workflow_database_url = registry_workflow_url

    if workflow_database_url and not workflow_database_url.lower().startswith("postgresql"):
        raise HTTPException(
            status_code=400,
            detail="workflow_database_url must point to PostgreSQL",
        )
    if database_url and not database_url.lower().startswith("postgresql"):
        raise HTTPException(
            status_code=400,
            detail="database_url must point to PostgreSQL",
        )

    existing = db.query(Project).filter(Project.slug == slug).first()
    if existing:
        changed = False
        field_updates = {
            "name": name,
            "root_directory": (
                payload.root_directory.strip()
                if payload.root_directory
                else existing.root_directory
            ),
            "database_url": database_url or existing.database_url,
            "frontend_url": (
                payload.frontend_url.strip() if payload.frontend_url else existing.frontend_url
            ),
            "backend_url": (
                payload.backend_url.strip() if payload.backend_url else existing.backend_url
            ),
            "workflow_database_url": workflow_database_url or existing.workflow_database_url,
            "tech_stack": payload.tech_stack.strip() if payload.tech_stack else existing.tech_stack,
        }
        for field_name, value in field_updates.items():
            if getattr(existing, field_name) != value:
                setattr(existing, field_name, value)
                changed = True
        if changed:
            db.commit()
            db.refresh(existing)
            bootstrap_project_workflow_db(existing, registry_db=db)
        return _project_out(existing)

    p = Project(
        slug=slug,
        name=name,
        root_directory=payload.root_directory.strip() if payload.root_directory else None,
        database_url=database_url,
        frontend_url=payload.frontend_url.strip() if payload.frontend_url else None,
        backend_url=payload.backend_url.strip() if payload.backend_url else None,
        workflow_database_url=workflow_database_url,
        tech_stack=payload.tech_stack.strip() if payload.tech_stack else None,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    bootstrap_project_workflow_db(p, registry_db=db)
    return _project_out(p)


class ChangeCreate(BaseModel):
    change_id: str = Field(min_length=1, max_length=128)
    title: str = Field(default="", max_length=256)
    description: str = Field(default="", max_length=2000)
    status: str = Field(default="Todo", max_length=32)
    ui_impact: Literal["unknown", "affected", "none"] = "unknown"
    ui_impact_justification: str = Field(default="", max_length=4000)
    design_ref: str = Field(default="", max_length=2000)
    prototype_ref: str = Field(default="", max_length=2000)
    prototype_digest: Optional[str] = Field(default=None, max_length=64)
    design_critique_verdict: str = Field(default="", max_length=32)
    image_data: List[dict] = Field(default_factory=list)


class ChangeUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=256)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[str] = Field(default=None, max_length=32)
    reorder: Optional[Literal["up", "down"]] = None
    cancel_archive: bool = False
    image_data: Optional[List[dict]] = Field(default=None)
    ui_impact: Optional[Literal["unknown", "affected", "none"]] = None
    ui_impact_justification: Optional[str] = Field(default=None, max_length=4000)
    design_ref: Optional[str] = Field(default=None, max_length=2000)
    prototype_ref: Optional[str] = Field(default=None, max_length=2000)
    prototype_digest: Optional[str] = Field(default=None, max_length=64)
    design_critique_verdict: Optional[str] = Field(default=None, max_length=32)
    rework_reason: Optional[str] = Field(default=None, max_length=4000)


class ChangeOut(BaseModel):
    id: str
    project_id: str
    change_id: str
    title: str
    description: str
    status: str
    card_number: Optional[int] = None
    image_data: List[dict] = Field(default_factory=list)
    ui_impact: str
    ui_impact_justification: str
    design_ref: str
    design_digest: Optional[str] = None
    prototype_ref: str
    prototype_digest: Optional[str] = None
    design_critique_verdict: str
    design_delivered_at: Optional[datetime] = None
    design_approved_by_user_id: Optional[str] = None
    design_approved_by: Optional[str] = None
    design_approved_at: Optional[datetime] = None
    approved_design_digest: Optional[str] = None
    approved_prototype_digest: Optional[str] = None
    design_approval_valid: bool
    qa_round_id: Optional[str] = None
    qa_commit_sha: Optional[str] = None
    qa_round_started_at: Optional[datetime] = None
    qa_approved_round_id: Optional[str] = None
    qa_approved_commit_sha: Optional[str] = None
    qa_approved_at: Optional[datetime] = None
    publication_commit_sha: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class WorkItemCreate(BaseModel):
    type: WorkItemType
    title: str = Field(min_length=1, max_length=256)
    description: str = Field(default="", max_length=10000)
    state: WorkItemState = WorkItemState.queued
    priority: int = 0
    parent_id: Optional[str] = None


class WorkItemUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=256)
    description: Optional[str] = Field(default=None, max_length=10000)
    state: Optional[WorkItemState] = None
    priority: Optional[int] = None
    parent_id: Optional[str] = None


class WorkItemOut(BaseModel):
    id: str
    change_pk: str
    type: WorkItemType
    state: WorkItemState
    parent_id: Optional[str]
    title: str
    description: str
    priority: int
    owner_run_id: Optional[str]
    stage_started_at: Optional[datetime] = None
    stage_completed_at: Optional[datetime] = None
    last_agent_acted: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class CommentCreate(BaseModel):
    scope: WorkflowScope
    author: str = Field(min_length=1, max_length=64)
    body: str = Field(min_length=1, max_length=4000)
    work_item_id: Optional[str] = None


class CommentOut(BaseModel):
    id: str
    scope: CommentScope
    change_pk: Optional[str]
    work_item_id: Optional[str]
    author: str
    body: str
    created_at: datetime


class ApprovalCreate(BaseModel):
    scope: WorkflowScope = "change"
    gate: str = Field(min_length=1, max_length=64)
    state: ApprovalState
    actor: Optional[str] = Field(default=None, max_length=64)
    note: str = Field(default="", max_length=4000)
    work_item_id: Optional[str] = None


class TrustedQaApprovalCreate(BaseModel):
    round_id: str = Field(min_length=1, max_length=36)
    commit_sha: str = Field(min_length=7, max_length=40)
    evidence: str = Field(min_length=1, max_length=4000)


class ApprovalOut(BaseModel):
    id: str
    scope: ApprovalScope
    gate: str
    state: ApprovalState
    change_pk: Optional[str]
    work_item_id: Optional[str]
    actor: str
    note: str
    created_at: datetime


class HandoffCreate(BaseModel):
    scope: WorkflowScope = "change"
    from_role: str = Field(min_length=1, max_length=64)
    to_role: str = Field(min_length=1, max_length=64)
    summary: str = Field(min_length=1, max_length=4000)
    work_item_id: Optional[str] = None


class HandoffOut(BaseModel):
    id: str
    scope: HandoffScope
    change_pk: Optional[str]
    work_item_id: Optional[str]
    from_role: str
    to_role: str
    summary: str
    created_at: datetime


def _get_project_by_slug(db: Session, slug: str) -> Project:
    p = db.query(Project).filter(Project.slug == slug).first()
    if not p:
        raise HTTPException(status_code=404, detail=f"Unknown project '{slug}'")
    return p


@contextmanager
def _project_db_session(registry_db: Session, slug: str):
    registry_project = _get_project_by_slug(registry_db, slug)

    SessionLocal = get_project_workflow_sessionmaker(registry_project)
    db = SessionLocal()
    try:
        sync_project_to_workflow_db(registry_project, db)
        db.commit()
        yield registry_project, db
    finally:
        db.close()


def _get_change_by_slug_and_id(db: Session, project_slug: str, change_id: str) -> Change:
    project = _get_project_by_slug(db, project_slug)
    change = (
        db.query(Change)
        .filter(Change.project_id == project.id, Change.change_id == change_id)
        .first()
    )
    if not change:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown change '{change_id}' in project '{project_slug}'",
        )
    return change


def _get_change_by_pk(db: Session, change_pk: str) -> Change:
    change = db.query(Change).filter(Change.id == change_pk).first()
    if not change:
        raise HTTPException(status_code=404, detail=f"Unknown change pk '{change_pk}'")
    return change


def _get_work_item(db: Session, change_pk: str, work_item_id: str) -> WorkItem:
    item = (
        db.query(WorkItem)
        .filter(WorkItem.id == work_item_id, WorkItem.change_pk == change_pk)
        .first()
    )
    if not item:
        raise HTTPException(status_code=404, detail=f"Unknown work item '{work_item_id}'")
    return item


def _next_card_number(db: Session, project_id: str, exclude_change_pk: Optional[str] = None) -> int:
    query = db.query(Change).filter(
        Change.project_id == project_id, Change.card_number.is_not(None)
    )
    if exclude_change_pk:
        query = query.filter(Change.id != exclude_change_pk)
    latest = query.order_by(Change.card_number.desc()).first()
    return int(latest.card_number or 0) + 1 if latest and latest.card_number is not None else 1


def _ensure_change_card_number(db: Session, change: Change) -> int:
    if change.card_number is not None:
        return int(change.card_number)
    change.card_number = _next_card_number(db, change.project_id, exclude_change_pk=change.id)
    db.flush()
    return int(change.card_number)


def _backfill_project_card_numbers(db: Session, project_id: str) -> None:
    missing = (
        db.query(Change)
        .filter(Change.project_id == project_id, Change.card_number.is_(None))
        .order_by(Change.created_at.asc(), Change.change_id.asc())
        .all()
    )
    for change in missing:
        _ensure_change_card_number(db, change)


def _change_out(change: Change) -> ChangeOut:
    return ChangeOut(
        id=change.id,
        project_id=change.project_id,
        change_id=change.change_id,
        title=change.title,
        description=change.description,
        status=change.status,
        card_number=change.card_number,
        image_data=_parse_json_field(change.image_data),
        ui_impact=change.ui_impact,
        ui_impact_justification=change.ui_impact_justification,
        design_ref=change.design_ref,
        design_digest=change.design_digest,
        prototype_ref=change.prototype_ref,
        prototype_digest=change.prototype_digest,
        design_critique_verdict=change.design_critique_verdict,
        design_delivered_at=change.design_delivered_at,
        design_approved_by_user_id=change.design_approved_by_user_id,
        design_approved_by=change.design_approved_by,
        design_approved_at=change.design_approved_at,
        approved_design_digest=change.approved_design_digest,
        approved_prototype_digest=change.approved_prototype_digest,
        design_approval_valid=change.design_approval_valid,
        qa_round_id=change.qa_round_id,
        qa_commit_sha=change.qa_commit_sha,
        qa_round_started_at=change.qa_round_started_at,
        qa_approved_round_id=change.qa_approved_round_id,
        qa_approved_commit_sha=change.qa_approved_commit_sha,
        qa_approved_at=change.qa_approved_at,
        publication_commit_sha=change.publication_commit_sha,
        created_at=change.created_at,
        updated_at=change.updated_at,
    )


def _validate_parent(
    db: Session, change_pk: str, parent_id: Optional[str], child_type: WorkItemType
) -> Optional[str]:
    if parent_id is None:
        return None

    parent = _get_work_item(db, change_pk, parent_id)
    if child_type == WorkItemType.story:
        raise HTTPException(status_code=400, detail="Stories cannot have parents in MVP")
    if child_type == WorkItemType.bug and parent.type != WorkItemType.story:
        raise HTTPException(status_code=400, detail="Bug parent must be a story in MVP")
    return parent.id


def _comment_out(item: WorkflowComment) -> CommentOut:
    return CommentOut(
        id=item.id,
        scope=item.scope,
        change_pk=item.change_pk,
        work_item_id=item.work_item_id,
        author=item.author,
        body=item.body,
        created_at=item.created_at,
    )


def _approval_out(item: WorkflowApproval) -> ApprovalOut:
    return ApprovalOut(
        id=item.id,
        scope=item.scope,
        gate=item.gate,
        state=item.state,
        change_pk=item.change_pk,
        work_item_id=item.work_item_id,
        actor=item.actor,
        note=item.note,
        created_at=item.created_at,
    )


def _handoff_out(item: WorkflowHandoff) -> HandoffOut:
    return HandoffOut(
        id=item.id,
        scope=item.scope,
        change_pk=item.change_pk,
        work_item_id=item.work_item_id,
        from_role=item.from_role,
        to_role=item.to_role,
        summary=item.summary,
        created_at=item.created_at,
    )


@router.get("/projects/{project_slug}/changes", response_model=List[ChangeOut])
def list_changes(project_slug: str, db: Session = Depends(get_workflow_db)):
    with _project_db_session(db, project_slug) as (registry_project, project_db):
        p = _get_project_by_slug(project_db, project_slug)
        _backfill_project_card_numbers(project_db, p.id)
        project_db.commit()
        items = (
            project_db.query(Change)
            .filter(Change.project_id == p.id)
            .order_by(Change.created_at.asc())
            .all()
        )
        return [_change_out(c) for c in items]


@router.post("/projects/{project_slug}/changes", response_model=ChangeOut)
def create_change(
    project_slug: str,
    payload: ChangeCreate,
    db: Session = Depends(get_workflow_db),
    _workflow_actor: WorkflowActor = Depends(get_workflow_actor),
):
    with _project_db_session(db, project_slug) as (_project, project_db):
        p = _get_project_by_slug(project_db, project_slug)
        change_id = payload.change_id.strip()

        existing = (
            project_db.query(Change)
            .filter(Change.project_id == p.id, Change.change_id == change_id)
            .first()
        )
        if existing:
            _ensure_change_card_number(project_db, existing)
            project_db.commit()
            project_db.refresh(existing)
            return _change_out(existing)

        initial_status = canonicalize_status(payload.status)
        if initial_status != "Todo":
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "initial_status_must_be_todo",
                    "message": "New workflow cards must be created in Todo and advance through transitions.",
                    "requested_status": initial_status,
                },
            )

        c = Change(
            project_id=p.id,
            change_id=change_id,
            title=payload.title.strip(),
            description=payload.description.strip(),
            status="Todo",
            ui_impact=payload.ui_impact,
            ui_impact_justification=payload.ui_impact_justification.strip(),
            design_ref=payload.design_ref.strip(),
            prototype_ref=payload.prototype_ref.strip(),
            prototype_digest=(payload.prototype_digest or "").strip().lower() or None,
            design_critique_verdict=payload.design_critique_verdict.strip().upper(),
            card_number=_next_card_number(project_db, p.id),
            image_data=payload.image_data or [],
        )
        project_db.add(c)
        project_db.commit()
        project_db.refresh(c)
        return _change_out(c)


@router.get("/projects/{project_slug}/changes/{change_id}", response_model=ChangeOut)
def get_change(project_slug: str, change_id: str, db: Session = Depends(get_workflow_db)):
    with _project_db_session(db, project_slug) as (_project, project_db):
        c = _get_change_by_slug_and_id(project_db, project_slug, change_id)
        _ensure_change_card_number(project_db, c)
        project_db.commit()
        project_db.refresh(c)
        return _change_out(c)


@router.patch("/projects/{project_slug}/changes/{change_id}", response_model=ChangeOut)
def update_change(
    project_slug: str,
    change_id: str,
    payload: ChangeUpdate,
    db: Session = Depends(get_workflow_db),
    workflow_actor: WorkflowActor = Depends(get_workflow_actor),
):
    with _project_db_session(db, project_slug) as (_project, project_db):
        c = _get_change_by_slug_and_id(project_db, project_slug, change_id)
        _ensure_change_card_number(project_db, c)
        current_column = canonicalize_status(c.status)

        if payload.title is not None:
            c.title = payload.title.strip()
        if payload.description is not None:
            c.description = payload.description.strip()
        if payload.image_data is not None:
            c.image_data = payload.image_data
        normalized_evidence_updates: dict[str, str | None] = {}
        design_updates = {
            "design_ref": payload.design_ref,
            "prototype_ref": payload.prototype_ref,
            "prototype_digest": payload.prototype_digest,
            "design_critique_verdict": payload.design_critique_verdict,
        }
        for field_name, raw_value in design_updates.items():
            if raw_value is None:
                continue
            normalized = raw_value.strip()
            if field_name in {"prototype_digest", "design_critique_verdict"}:
                normalized = (
                    normalized.lower() if field_name == "prototype_digest" else normalized.upper()
                )
            normalized_value = normalized or (None if field_name == "prototype_digest" else "")
            if getattr(c, field_name) != normalized_value:
                normalized_evidence_updates[field_name] = normalized_value
        if payload.ui_impact is not None and c.ui_impact != payload.ui_impact:
            normalized_evidence_updates["ui_impact"] = payload.ui_impact
        if payload.ui_impact_justification is not None:
            justification = payload.ui_impact_justification.strip()
            if c.ui_impact_justification != justification:
                normalized_evidence_updates["ui_impact_justification"] = justification

        evidence_changed = bool(normalized_evidence_updates)
        if evidence_changed and current_column in {"Done", "Homologado", "Pronto"}:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "design_evidence_immutable_after_done",
                    "message": "Design and bypass evidence cannot be edited after Done.",
                    "status": current_column,
                },
            )
        for field_name, normalized_value in normalized_evidence_updates.items():
            setattr(c, field_name, normalized_value)

        approval_invalidated = invalidate_design_approval(c) if evidence_changed else False
        had_design_approval = bool(c.approved_design_digest or c.approved_prototype_digest)
        if approval_invalidated or (evidence_changed and had_design_approval):
            project_db.add(
                WorkflowApproval(
                    scope=ApprovalScope.change,
                    gate="Design Approval",
                    state=ApprovalState.rejected,
                    change_pk=c.id,
                    work_item_id=None,
                    actor=workflow_actor.email,
                    note="Approval obsolete: design or prototype evidence changed.",
                )
            )
            if current_column in {
                "Pronto para Dev",
                "Em desenvolvimento",
                "Code Review",
                "QA",
            }:
                previous_column = current_column
                if previous_column == "QA":
                    invalidate_qa_round(
                        project_db,
                        c,
                        actor=workflow_actor.email,
                        reason="design evidence changed",
                    )
                c.status = "Aprovação de Design"
                _normalize_column_sort_orders(project_db, c.project_id, previous_column)
                c.sort_order = _next_sort_order(
                    project_db,
                    c.project_id,
                    "Aprovação de Design",
                    exclude_change_pk=c.id,
                )
                current_column = "Aprovação de Design"
        if payload.reorder is not None:
            _reorder_change_within_column(project_db, c, payload.reorder)
        if payload.status is not None:
            new_status = canonicalize_status(payload.status)
            if new_status != current_column:
                is_rework = (current_column, new_status) in {
                    ("Aprovação de Design", "Design"),
                    ("Code Review", "Em desenvolvimento"),
                    ("QA", "Em desenvolvimento"),
                }
                if is_rework and not (payload.rework_reason or "").strip():
                    raise HTTPException(
                        status_code=409,
                        detail={
                            "code": "rework_reason_required",
                            "message": "Controlled rework requires a non-empty reason.",
                        },
                    )
                try:
                    transition_change(
                        project_db,
                        change=c,
                        target_status=new_status,
                        actor=workflow_actor,
                        repo_root=REPO_ROOT,
                        design_approver_emails=design_approver_emails(),
                        homologation_approver_emails=homologation_approver_emails(),
                        release_approver_emails=release_approver_emails(),
                    )
                except HTTPException as exc:
                    detail = exc.detail if isinstance(exc.detail, dict) else {}
                    if (
                        detail.get("code") == "design_approval_obsolete"
                        and not c.design_approval_valid
                    ):
                        project_db.add(
                            WorkflowApproval(
                                scope=ApprovalScope.change,
                                gate="Design Approval",
                                state=ApprovalState.rejected,
                                change_pk=c.id,
                                work_item_id=None,
                                actor=workflow_actor.email,
                                note="Approval obsolete: current evidence no longer matches the approved digest.",
                            )
                        )
                        # Persist the obsolete marker/regression even though
                        # the requested status move is rejected.
                        project_db.commit()
                    raise
                if is_rework:
                    project_db.add(
                        WorkflowComment(
                            scope=CommentScope.change,
                            change_pk=c.id,
                            work_item_id=None,
                            author=workflow_actor.email,
                            body=f"Rework: {(payload.rework_reason or '').strip()}",
                        )
                    )
                _normalize_column_sort_orders(project_db, c.project_id, current_column)
                c.sort_order = _next_sort_order(
                    project_db, c.project_id, new_status, exclude_change_pk=c.id
                )
        project_db.commit()
        project_db.refresh(c)
        return _change_out(c)


@router.get(
    "/projects/{project_slug}/changes/{change_id}/tasks",
    response_model=List[WorkItemOut],
)
def list_tasks(project_slug: str, change_id: str, db: Session = Depends(get_workflow_db)):
    with _project_db_session(db, project_slug) as (_project, project_db):
        change = _get_change_by_slug_and_id(project_db, project_slug, change_id)
        items = (
            project_db.query(WorkItem)
            .filter(WorkItem.change_pk == change.id)
            .order_by(WorkItem.priority.desc(), WorkItem.created_at.asc())
            .all()
        )
        return [WorkItemOut.model_validate(item, from_attributes=True) for item in items]


@router.post("/projects/{project_slug}/changes/{change_id}/tasks", response_model=WorkItemOut)
def create_task(
    project_slug: str,
    change_id: str,
    payload: WorkItemCreate,
    db: Session = Depends(get_workflow_db),
    _workflow_actor: WorkflowActor = Depends(get_workflow_actor),
):
    with _project_db_session(db, project_slug) as (_project, project_db):
        change = _get_change_by_slug_and_id(project_db, project_slug, change_id)
        parent_id = _validate_parent(project_db, change.id, payload.parent_id, payload.type)
        item = WorkItem(
            change_pk=change.id,
            type=payload.type,
            state=payload.state,
            parent_id=parent_id,
            title=payload.title.strip(),
            description=payload.description.strip(),
            priority=payload.priority,
        )
        project_db.add(item)
        project_db.commit()
        project_db.refresh(item)
        return WorkItemOut.model_validate(item, from_attributes=True)


@router.patch("/work-items/{work_item_id}", response_model=WorkItemOut)
def update_task(
    work_item_id: str,
    payload: WorkItemUpdate,
    project_slug: Optional[str] = Query(default=None),
    db: Session = Depends(get_workflow_db),
    _workflow_actor: WorkflowActor = Depends(get_workflow_actor),
):
    target_slug = project_slug
    if not target_slug:
        raise HTTPException(
            status_code=400,
            detail="project_slug is required for work item updates in multi-project mode",
        )

    with _project_db_session(db, target_slug) as (_project, project_db):
        item = project_db.query(WorkItem).filter(WorkItem.id == work_item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail=f"Unknown work item '{work_item_id}'")

        old_state = item.state
        new_state = payload.state if payload.state is not None else old_state
        state_changed = payload.state is not None and old_state != payload.state

        if payload.parent_id is not None:
            item.parent_id = _validate_parent(
                project_db, item.change_pk, payload.parent_id, item.type
            )
        if payload.title is not None:
            item.title = payload.title.strip()
        if payload.description is not None:
            item.description = payload.description.strip()
        if payload.state is not None:
            validate_work_item_transition(project_db, item, payload.state)
            item.state = payload.state
        if payload.priority is not None:
            item.priority = payload.priority

        file_sync_ok = True
        if state_changed and new_state in (WorkItemState.done, WorkItemState.queued):
            task_code_match = re.search(r"code:\s*(\d+(?:\.\d+)+)", item.description or "")
            if task_code_match:
                task_code = task_code_match.group(1)
                change = project_db.query(Change).filter(Change.id == item.change_pk).first()
                if change:
                    checked = new_state == WorkItemState.done
                    file_sync_ok = toggle_task_checkbox(change.change_id, task_code, checked)
                    if not file_sync_ok:
                        project_db.rollback()
                        raise HTTPException(
                            status_code=409,
                            detail=f"Failed to sync checkbox in tasks.md for task '{task_code}'",
                        )

        if file_sync_ok:
            project_db.commit()
            project_db.refresh(item)

        return WorkItemOut.model_validate(item, from_attributes=True)


@router.get(
    "/projects/{project_slug}/changes/{change_id}/comments",
    response_model=List[CommentOut],
)
def list_comments(
    project_slug: str,
    change_id: str,
    work_item_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_workflow_db),
):
    with _project_db_session(db, project_slug) as (_project, project_db):
        change = _get_change_by_slug_and_id(project_db, project_slug, change_id)
        query = project_db.query(WorkflowComment)
        if work_item_id:
            _get_work_item(project_db, change.id, work_item_id)
            query = query.filter(WorkflowComment.work_item_id == work_item_id)
        else:
            query = query.filter(
                WorkflowComment.change_pk == change.id,
                WorkflowComment.scope == CommentScope.change,
            )
        items = query.order_by(WorkflowComment.created_at.asc()).all()
        return [_comment_out(item) for item in items]


@router.post("/projects/{project_slug}/changes/{change_id}/comments", response_model=CommentOut)
def create_comment(
    project_slug: str,
    change_id: str,
    payload: CommentCreate,
    db: Session = Depends(get_workflow_db),
    workflow_actor: WorkflowActor = Depends(get_workflow_actor),
):
    with _project_db_session(db, project_slug) as (_project, project_db):
        change = _get_change_by_slug_and_id(project_db, project_slug, change_id)
        work_item_id = None
        if payload.scope == "work_item":
            if not payload.work_item_id:
                raise HTTPException(
                    status_code=400,
                    detail="work_item_id is required for work_item scoped comments",
                )
            work_item_id = _get_work_item(project_db, change.id, payload.work_item_id).id
        item = WorkflowComment(
            scope=CommentScope(payload.scope),
            change_pk=change.id if payload.scope == "change" else None,
            work_item_id=work_item_id,
            author=workflow_actor.email,
            body=payload.body.strip(),
        )
        project_db.add(item)
        project_db.commit()
        project_db.refresh(item)
        return _comment_out(item)


@router.get(
    "/projects/{project_slug}/changes/{change_id}/approvals",
    response_model=List[ApprovalOut],
)
def list_approvals(
    project_slug: str,
    change_id: str,
    work_item_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_workflow_db),
):
    with _project_db_session(db, project_slug) as (_project, project_db):
        change = _get_change_by_slug_and_id(project_db, project_slug, change_id)
        query = project_db.query(WorkflowApproval)
        if work_item_id:
            _get_work_item(project_db, change.id, work_item_id)
            query = query.filter(WorkflowApproval.work_item_id == work_item_id)
        else:
            query = query.filter(
                WorkflowApproval.change_pk == change.id,
                WorkflowApproval.scope == ApprovalScope.change,
            )
        items = query.order_by(WorkflowApproval.created_at.asc()).all()
        return [_approval_out(item) for item in items]


@router.post("/projects/{project_slug}/changes/{change_id}/approvals", response_model=ApprovalOut)
def create_approval(
    project_slug: str,
    change_id: str,
    payload: ApprovalCreate,
    db: Session = Depends(get_workflow_db),
    workflow_actor: WorkflowActor = Depends(get_workflow_actor),
):
    with _project_db_session(db, project_slug) as (_project, project_db):
        change = _get_change_by_slug_and_id(project_db, project_slug, change_id)
        work_item_id = None
        if payload.scope == "work_item":
            if not payload.work_item_id:
                raise HTTPException(
                    status_code=400,
                    detail="work_item_id is required for work_item scoped approvals",
                )
            work_item_id = _get_work_item(project_db, change.id, payload.work_item_id).id
        gate = payload.gate.strip()
        protected_gates = {"design approval", "qa", "homologation", "publication"}
        if gate.casefold() in protected_gates:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "approval_requires_transition",
                    "message": f"Record {gate} through its authenticated canonical transition.",
                },
            )
        item = WorkflowApproval(
            scope=ApprovalScope(payload.scope),
            gate=gate,
            state=payload.state,
            change_pk=change.id if payload.scope == "change" else None,
            work_item_id=work_item_id,
            actor=workflow_actor.email,
            note=payload.note.strip(),
        )
        project_db.add(item)
        project_db.commit()
        project_db.refresh(item)
        return _approval_out(item)


@router.post(
    "/projects/{project_slug}/changes/{change_id}/qa-approvals",
    response_model=ApprovalOut,
)
def create_trusted_qa_approval(
    project_slug: str,
    change_id: str,
    payload: TrustedQaApprovalCreate,
    db: Session = Depends(get_workflow_db),
    trusted_actor: WorkflowActor = Depends(get_trusted_qa_actor),
):
    with _project_db_session(db, project_slug) as (_project, project_db):
        change = _get_change_by_slug_and_id(project_db, project_slug, change_id)
        approval = approve_current_qa_round(
            project_db,
            change=change,
            actor=trusted_actor,
            round_id=payload.round_id,
            commit_sha=payload.commit_sha,
            note=payload.evidence,
            repo_root=REPO_ROOT,
        )
        project_db.commit()
        project_db.refresh(approval)
        return _approval_out(approval)


@router.get(
    "/projects/{project_slug}/changes/{change_id}/handoffs",
    response_model=List[HandoffOut],
)
def list_handoffs(
    project_slug: str,
    change_id: str,
    work_item_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_workflow_db),
):
    with _project_db_session(db, project_slug) as (_project, project_db):
        change = _get_change_by_slug_and_id(project_db, project_slug, change_id)
        query = project_db.query(WorkflowHandoff)
        if work_item_id:
            _get_work_item(project_db, change.id, work_item_id)
            query = query.filter(WorkflowHandoff.work_item_id == work_item_id)
        else:
            query = query.filter(
                WorkflowHandoff.change_pk == change.id,
                WorkflowHandoff.scope == HandoffScope.change,
            )
        items = query.order_by(WorkflowHandoff.created_at.asc()).all()
        return [_handoff_out(item) for item in items]


@router.post("/projects/{project_slug}/changes/{change_id}/handoffs", response_model=HandoffOut)
def create_handoff(
    project_slug: str,
    change_id: str,
    payload: HandoffCreate,
    db: Session = Depends(get_workflow_db),
    _workflow_actor: WorkflowActor = Depends(get_workflow_actor),
):
    with _project_db_session(db, project_slug) as (_project, project_db):
        change = _get_change_by_slug_and_id(project_db, project_slug, change_id)
        work_item_id = None
        if payload.scope == "work_item":
            if not payload.work_item_id:
                raise HTTPException(
                    status_code=400,
                    detail="work_item_id is required for work_item scoped handoffs",
                )
            work_item_id = _get_work_item(project_db, change.id, payload.work_item_id).id
        item = WorkflowHandoff(
            scope=HandoffScope(payload.scope),
            change_pk=change.id if payload.scope == "change" else None,
            work_item_id=work_item_id,
            from_role=payload.from_role.strip(),
            to_role=payload.to_role.strip(),
            summary=payload.summary.strip(),
        )
        project_db.add(item)
        project_db.commit()
        project_db.refresh(item)
        return _handoff_out(item)


# --- Kanban cutover compatibility endpoints ---

# These endpoints intentionally mirror the legacy `/api/coordination/*` response
# shapes so the Kanban UI can run exclusively on the DB-backed workflow model.


class KanbanChangeItem(BaseModel):
    id: str
    title: Optional[str] = None
    description: Optional[str] = None
    card_number: Optional[int] = None
    path: str
    status: Dict[str, str]
    archived: bool
    column: str
    position: int = 0
    has_bugs: bool = False
    item_type: str = "change"  # "change" or "bug"
    parent_story_id: Optional[str] = None
    parent_story_title: Optional[str] = None
    image_data: List[dict] = Field(default_factory=list)
    # Days since the card was moved to Archived (None if not archived)
    days_in_archived: Optional[int] = None
    ui_impact: str = "unknown"
    ui_impact_justification: str = ""
    design_ref: str = ""
    design_digest: Optional[str] = None
    prototype_ref: str = ""
    prototype_digest: Optional[str] = None
    design_critique_verdict: str = ""
    design_delivered_at: Optional[datetime] = None
    design_approved_by: Optional[str] = None
    design_approved_at: Optional[datetime] = None
    design_approval_valid: bool = False


class KanbanChangeListResponse(BaseModel):
    items: List[KanbanChangeItem]


class TaskChecklistItem(BaseModel):
    text: str
    checked: Optional[bool] = None
    code: Optional[str] = None
    title: Optional[str] = None
    children: List["TaskChecklistItem"] = Field(default_factory=list)


TaskChecklistItem.model_rebuild()


class TaskChecklistSection(BaseModel):
    title: str
    items: List[TaskChecklistItem]


class KanbanTasksChecklistResponse(BaseModel):
    change_id: str
    path: str
    sections: List[TaskChecklistSection]


class KanbanCommentItem(BaseModel):
    id: str
    change: str
    author: str
    created_at: str
    body: str


class KanbanCommentsListResponse(BaseModel):
    change_id: str
    items: List[KanbanCommentItem]


class KanbanCommentCreateRequest(BaseModel):
    author: str = Field(min_length=1, max_length=64)
    body: str = Field(min_length=1, max_length=2000)


class KanbanChangeCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=256)
    description: str = Field(default="", max_length=2000)
    image_data: List[dict] = Field(default_factory=list)


class KanbanCommentCreateResponse(BaseModel):
    item: KanbanCommentItem


class KanbanChangeCreateResponse(BaseModel):
    item: KanbanChangeItem


def _kanban_project_slug(db: Session, project_slug: Optional[str]) -> str:
    if project_slug:
        _get_project_by_slug(db, project_slug)
        return project_slug

    first = db.query(Project).order_by(Project.created_at.asc()).first()
    if not first:
        raise HTTPException(status_code=404, detail="No projects in workflow DB")
    return first.slug


def _kanban_change_by_id(db: Session, project_slug: str, change_id: str) -> Change:
    return _get_change_by_slug_and_id(db, project_slug, change_id)


def _latest_change_gate_status(db: Session, change_pk: str) -> Dict[str, str]:
    # Map gate -> latest approval state.
    out: Dict[str, str] = {}
    approvals = (
        db.query(WorkflowApproval)
        .filter(
            WorkflowApproval.scope == ApprovalScope.change,
            WorkflowApproval.change_pk == change_pk,
        )
        .order_by(WorkflowApproval.created_at.asc())
        .all()
    )
    for a in approvals:
        gate = "Homologation" if a.gate == "Alan homologation" else a.gate
        out[gate] = a.state.value
    return out


def _kanban_change_status(db: Session, change: Change) -> Dict[str, str]:
    gate_status = _latest_change_gate_status(db, change.id)
    column = _normalize_column(change.status)
    out = dict(gate_status)
    out["Runtime stage"] = column
    out["Design approval"] = "valid" if change.design_approval_valid else "pending"
    return out


def _normalize_column(raw: Optional[str]) -> str:
    return canonicalize_status(raw)


def _next_sort_order(
    db: Session, project_id: str, column: str, exclude_change_pk: Optional[str] = None
) -> int:
    query = db.query(Change).filter(Change.project_id == project_id, Change.status == column)
    if exclude_change_pk:
        query = query.filter(Change.id != exclude_change_pk)
    peers = query.order_by(Change.sort_order.desc(), Change.created_at.desc()).all()
    return (peers[0].sort_order + 1) if peers else 0


def _normalize_column_sort_orders(db: Session, project_id: str, column: str) -> None:
    peers = (
        db.query(Change)
        .filter(Change.project_id == project_id, Change.status == column)
        .order_by(Change.sort_order.asc(), Change.created_at.asc(), Change.change_id.asc())
        .all()
    )
    for idx, peer in enumerate(peers):
        peer.sort_order = idx
    # Workflow sessions run with autoflush disabled, so callers that immediately
    # re-query this column (like intra-column reorder) must persist the normalized
    # sequence first or they will read the stale legacy order again.
    db.flush()


def _reorder_change_within_column(
    db: Session, change: Change, direction: Literal["up", "down"]
) -> None:
    column = _normalize_column(change.status)
    _normalize_column_sort_orders(db, change.project_id, column)
    peers = (
        db.query(Change)
        .filter(Change.project_id == change.project_id, Change.status == column)
        .order_by(Change.sort_order.asc(), Change.created_at.asc(), Change.change_id.asc())
        .all()
    )
    idx = next((i for i, peer in enumerate(peers) if peer.id == change.id), None)
    if idx is None:
        return
    swap_idx = idx - 1 if direction == "up" else idx + 1
    if swap_idx < 0 or swap_idx >= len(peers):
        return
    current_order = int(peers[idx].sort_order or 0)
    swap_order = int(peers[swap_idx].sort_order or 0)
    peers[idx].sort_order = swap_order
    peers[swap_idx].sort_order = current_order
    db.flush()
    _normalize_column_sort_orders(db, change.project_id, column)


@router.post("/kanban/changes", response_model=KanbanChangeCreateResponse)
def kanban_create_change(
    payload: KanbanChangeCreateRequest,
    project_slug: Optional[str] = Query(default=None),
    db: Session = Depends(get_workflow_db),
    _workflow_actor: WorkflowActor = Depends(get_workflow_actor),
) -> KanbanChangeCreateResponse:
    slug = _kanban_project_slug(db, project_slug)
    with _project_db_session(db, slug) as (_project, project_db):
        project = _get_project_by_slug(project_db, slug)

        base_id = _slugify_change_title(payload.title)
        change_id = base_id
        suffix = 2
        while (
            project_db.query(Change)
            .filter(Change.project_id == project.id, Change.change_id == change_id)
            .first()
        ):
            change_id = f"{base_id}-{suffix}"
            suffix += 1

        change = Change(
            project_id=project.id,
            change_id=change_id,
            title=payload.title.strip(),
            description=payload.description.strip(),
            status="Todo",
            sort_order=_next_sort_order(project_db, project.id, "Todo"),
            card_number=_next_card_number(project_db, project.id),
            image_data=payload.image_data or [],
        )
        project_db.add(change)
        project_db.commit()
        project_db.refresh(change)

        return KanbanChangeCreateResponse(
            item=KanbanChangeItem(
                id=change.change_id,
                title=change.title or None,
                description=change.description or None,
                card_number=change.card_number,
                path=f"openspec/changes/{change.change_id}/proposal",
                status=_kanban_change_status(project_db, change),
                archived=False,
                column="Todo",
                position=change.sort_order,
                image_data=_parse_json_field(change.image_data),
                ui_impact=change.ui_impact,
                ui_impact_justification=change.ui_impact_justification,
            )
        )


@router.get("/kanban/changes", response_model=KanbanChangeListResponse)
def kanban_list_changes(
    project_slug: Optional[str] = Query(default=None),
    db: Session = Depends(get_workflow_db),
) -> KanbanChangeListResponse:
    slug = _kanban_project_slug(db, project_slug)
    with _project_db_session(db, slug) as (_project, project_db):
        project = _get_project_by_slug(project_db, slug)

        _backfill_project_card_numbers(project_db, project.id)
        project_db.commit()
        items = (
            project_db.query(Change)
            .filter(Change.project_id == project.id)
            .order_by(Change.created_at.asc())
            .all()
        )
        out: List[KanbanChangeItem] = []

        change_map = {c.id: c for c in items}

        for c in items:
            status = _kanban_change_status(project_db, c)
            col = _normalize_column(c.status)
            archived = col in {"Pronto", "Cancelado"}
            days_in_archived: Optional[int] = None
            if archived:
                days_in_archived = (datetime.utcnow() - c.updated_at.replace(tzinfo=None)).days
            has_bugs = (
                project_db.query(WorkItem)
                .filter(WorkItem.change_pk == c.id, WorkItem.type == WorkItemType.bug)
                .first()
                is not None
            )
            out.append(
                KanbanChangeItem(
                    id=c.change_id,
                    title=c.title or None,
                    description=c.description or None,
                    card_number=c.card_number,
                    path=resolve_change_relative_path(c.change_id, "proposal"),
                    status=status,
                    archived=archived,
                    column=col,
                    position=int(c.sort_order or 0),
                    has_bugs=has_bugs,
                    item_type="change",
                    parent_story_id=None,
                    parent_story_title=None,
                    image_data=_parse_json_field(c.image_data),
                    days_in_archived=days_in_archived,
                    ui_impact=c.ui_impact,
                    ui_impact_justification=c.ui_impact_justification,
                    design_ref=c.design_ref,
                    design_digest=c.design_digest,
                    prototype_ref=c.prototype_ref,
                    prototype_digest=c.prototype_digest,
                    design_critique_verdict=c.design_critique_verdict,
                    design_delivered_at=c.design_delivered_at,
                    design_approved_by=c.design_approved_by,
                    design_approved_at=c.design_approved_at,
                    design_approval_valid=c.design_approval_valid,
                )
            )

        active_change_ids = [
            c.id for c in items if _normalize_column(c.status) not in {"Pronto", "Cancelado"}
        ]
        bugs = (
            project_db.query(WorkItem)
            .filter(WorkItem.type == WorkItemType.bug)
            .filter(WorkItem.change_pk.in_(active_change_ids))
            .all()
        )

        for bug in bugs:
            if bug.change_pk not in change_map:
                continue

            parent_story = None
            parent_story_title = None
            if bug.parent_id:
                parent_story = (
                    project_db.query(WorkItem).filter(WorkItem.id == bug.parent_id).first()
                )
                if parent_story:
                    parent_story_title = parent_story.title

            parent_change = change_map.get(bug.change_pk)
            if not parent_change:
                continue

            bug_col = _normalize_column(parent_change.status)

            bug_status = {
                "status": bug.state.value if bug.state else "unknown",
                "story": parent_change.change_id,
            }

            out.append(
                KanbanChangeItem(
                    id=f"{parent_change.change_id}-bug-{bug.id[:8]}",
                    title=bug.title,
                    description=bug.description or None,
                    card_number=None,
                    path=resolve_change_relative_path(parent_change.change_id, "tasks.md"),
                    status=bug_status,
                    archived=bug_col in {"Pronto", "Cancelado"},
                    column=bug_col,
                    position=999,
                    has_bugs=False,
                    item_type="bug",
                    parent_story_id=bug.parent_id,
                    parent_story_title=parent_story_title,
                    image_data=_parse_json_field(parent_change.image_data),
                )
            )

        column_index = {name: idx for idx, name in enumerate(KANBAN_COLUMNS)}
        out.sort(
            key=lambda item: (
                column_index.get(item.column, 999),
                item.position,
                (item.title or item.id).lower(),
                item.id,
            )
        )
        return KanbanChangeListResponse(items=out)


def _kanban_task_checked(state: WorkItemState) -> bool:
    return state in (WorkItemState.done, WorkItemState.canceled)


def _extract_task_code(description: str) -> Optional[str]:
    """Extract task code from description (e.g., 'code:1.1' -> '1.1')."""
    if description:
        # Look for code: prefix
        for line in description.split("\n"):
            if line.strip().startswith("code:"):
                return line.replace("code:", "").strip()
    return None


def _kanban_task_item(
    it: WorkItem, children: Optional[List[TaskChecklistItem]] = None
) -> TaskChecklistItem:
    # Extract task code from description
    task_code = _extract_task_code(it.description)
    # Use title without the code prefix if present
    title = it.title
    # For stories, extract the section name (e.g., "1. Runtime / Backend" -> "Runtime / Backend")
    if it.type == WorkItemType.story:
        # Remove leading number prefix like "1. "
        match = re.match(r"^\d+\.\s+(.+)$", title)
        if match:
            title = match.group(1)

    return TaskChecklistItem(
        text=it.title,
        checked=_kanban_task_checked(it.state),
        code=task_code,
        title=title,
        children=children or [],
    )


@router.get("/kanban/changes/{change_id}/tasks", response_model=KanbanTasksChecklistResponse)
def kanban_change_tasks(
    change_id: str,
    project_slug: Optional[str] = Query(default=None),
    db: Session = Depends(get_workflow_db),
) -> KanbanTasksChecklistResponse:
    """DB-backed replacement for `/api/coordination/changes/{id}/tasks`.

    We expose a checklist/tree so the existing Kanban UI can render work-items
    without needing to understand the full workflow schema yet.

    This endpoint syncs tasks.md to the database before returning results.
    """

    slug = _kanban_project_slug(db, project_slug)
    with _project_db_session(db, slug) as (_project, project_db):
        change = _kanban_change_by_id(project_db, slug, change_id)
        sync_tasks_to_workflow_db(project_db, change.id, change_id)

        items = (
            project_db.query(WorkItem)
            .filter(WorkItem.change_pk == change.id)
            .order_by(WorkItem.priority.desc(), WorkItem.created_at.asc())
            .all()
        )

        stories = [it for it in items if it.type == WorkItemType.story]
        bugs = [it for it in items if it.type == WorkItemType.bug]

        bugs_by_parent: Dict[Optional[str], List[WorkItem]] = {}
        for b in bugs:
            bugs_by_parent.setdefault(b.parent_id, []).append(b)

        for k in list(bugs_by_parent.keys()):
            bugs_by_parent[k] = sorted(
                bugs_by_parent[k],
                key=lambda x: (-int(x.priority or 0), x.created_at),
            )

        out_items: List[TaskChecklistItem] = []

        for s in stories:
            children = [_kanban_task_item(b) for b in bugs_by_parent.get(s.id, [])]
            out_items.append(_kanban_task_item(s, children=children))

        for b in bugs_by_parent.get(None, []):
            out_items.append(_kanban_task_item(b))

        sections = [TaskChecklistSection(title="Tasks", items=out_items)]

        return KanbanTasksChecklistResponse(
            change_id=change_id,
            path=resolve_change_relative_path(change_id, "tasks.md"),
            sections=sections,
        )


@router.get("/kanban/changes/{change_id}/comments", response_model=KanbanCommentsListResponse)
def kanban_list_comments(
    change_id: str,
    project_slug: Optional[str] = Query(default=None),
    db: Session = Depends(get_workflow_db),
) -> KanbanCommentsListResponse:
    slug = _kanban_project_slug(db, project_slug)
    with _project_db_session(db, slug) as (_project, project_db):
        change = _kanban_change_by_id(project_db, slug, change_id)
        try:
            from app.services.workflow_coordination_bridge import (
                migrate_coordination_comments_into_workflow_db,
            )

            migrate_coordination_comments_into_workflow_db(
                project_db, change_pk=change.id, change_id=change_id
            )
        except Exception:
            pass

        items = (
            project_db.query(WorkflowComment)
            .filter(
                WorkflowComment.scope == CommentScope.change,
                WorkflowComment.change_pk == change.id,
            )
            .order_by(WorkflowComment.created_at.asc())
            .all()
        )

        out = [
            KanbanCommentItem(
                id=it.id,
                change=change_id,
                author=it.author,
                created_at=it.created_at.isoformat(),
                body=it.body,
            )
            for it in items
        ]

        return KanbanCommentsListResponse(change_id=change_id, items=out)


@router.post("/kanban/changes/{change_id}/comments", response_model=KanbanCommentCreateResponse)
def kanban_post_comment(
    change_id: str,
    payload: KanbanCommentCreateRequest,
    project_slug: Optional[str] = Query(default=None),
    db: Session = Depends(get_workflow_db),
    workflow_actor: WorkflowActor = Depends(get_workflow_actor),
) -> KanbanCommentCreateResponse:
    slug = _kanban_project_slug(db, project_slug)
    with _project_db_session(db, slug) as (_project, project_db):
        change = _kanban_change_by_id(project_db, slug, change_id)

        item = WorkflowComment(
            scope=CommentScope.change,
            change_pk=change.id,
            work_item_id=None,
            author=workflow_actor.email,
            body=payload.body.strip(),
        )
        project_db.add(item)
        project_db.commit()
        project_db.refresh(item)

        return KanbanCommentCreateResponse(
            item=KanbanCommentItem(
                id=item.id,
                change=change_id,
                author=item.author,
                created_at=item.created_at.isoformat(),
                body=item.body,
            )
        )


# --- Scheduler Polling Suppression (reduce-workflow-scheduler-polling) ---


class SchedulerDecisionResponse(BaseModel):
    should_run: bool
    suppressed_count: int
    material_changes: List[str]
    state_changed: bool
    suppressed_since: Optional[str] = None
    last_hash: str
    current_hash: str


class SuppressorStatusResponse(BaseModel):
    suppression_enabled: bool
    suppressed_count: int
    last_turn_at: Optional[str] = None
    suppressed_since: Optional[str] = None
    max_suppressed_turns: int
    suppression_timeout_minutes: int


@router.get("/scheduler/should-run", response_model=SchedulerDecisionResponse)
def scheduler_should_run(
    db: Session = Depends(get_workflow_db),
) -> SchedulerDecisionResponse:
    """Decision endpoint for workflow scheduler.

    The scheduler should call this before running a turn. Returns whether
    the scheduler should proceed based on material workflow state changes.

    This implements the reduce-workflow-scheduler-polling change:
    - Suppresses redundant turns when no material state changed
    - Breaks suppression on meaningful events (approvals, handoffs, blockers)
    - Forces periodic runs to avoid getting stuck in suppression
    """
    from app.services.workflow_polling_suppressor import get_suppressor

    suppressor = get_suppressor()
    should_run, metadata = suppressor.should_scheduler_run(db)

    return SchedulerDecisionResponse(
        should_run=should_run,
        suppressed_count=metadata["suppressed_count"],
        material_changes=metadata["material_changes"],
        state_changed=metadata["state_changed"],
        suppressed_since=metadata["suppressed_since"],
        last_hash=metadata["last_hash"],
        current_hash=metadata["current_hash"],
    )


@router.get("/scheduler/status", response_model=SuppressorStatusResponse)
def scheduler_status() -> SuppressorStatusResponse:
    """Get current suppression status for monitoring/debugging."""
    from app.services.workflow_polling_suppressor import get_suppressor

    suppressor = get_suppressor()
    status = suppressor.get_status()

    return SuppressorStatusResponse(
        suppression_enabled=status["suppression_enabled"],
        suppressed_count=status["suppressed_count"],
        last_turn_at=status["last_turn_at"],
        suppressed_since=status["suppressed_since"],
        max_suppressed_turns=status["max_suppressed_turns"],
        suppression_timeout_minutes=status["suppression_timeout_minutes"],
    )


@router.post("/scheduler/force-run")
def scheduler_force_run(
    _workflow_actor: WorkflowActor = Depends(get_workflow_actor),
) -> dict:
    """Force the next scheduler turn to run (ignore suppression).

    Use this to override suppression behavior when needed.
    """
    from app.services.workflow_polling_suppressor import get_suppressor

    suppressor = get_suppressor()
    suppressor.force_run_next()

    return {"status": "ok", "message": "Next scheduler run forced"}


@router.post("/scheduler/configure")
def scheduler_configure(
    suppression_enabled: bool = True,
    max_suppressed_turns: int = 5,
    suppression_timeout_minutes: int = 60,
    _workflow_actor: WorkflowActor = Depends(get_workflow_actor),
) -> dict:
    """Configure suppression behavior."""
    from app.services.workflow_polling_suppressor import get_suppressor

    suppressor = get_suppressor()
    suppressor.configure(
        suppression_enabled=suppression_enabled,
        max_suppressed_turns=max_suppressed_turns,
        suppression_timeout_minutes=suppression_timeout_minutes,
    )

    return {
        "status": "ok",
        "configured": {
            "suppression_enabled": suppression_enabled,
            "max_suppressed_turns": max_suppressed_turns,
            "suppression_timeout_minutes": suppression_timeout_minutes,
        },
    }
