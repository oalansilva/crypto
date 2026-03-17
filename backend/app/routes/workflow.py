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
from typing import Dict, List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
import json
import subprocess
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.services.coordination_service import resolve_change_relative_path
from app.services.upstream_guard import ENFORCED_STATUSES, UpstreamGuardError, require_upstream_published
from app.services.workflow_transition_service import KANBAN_COLUMNS, sync_change_gates_for_column
from app.workflow_database import get_workflow_db, get_workflow_db_url
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
    
    Creates Story work items for each section, and Bug work items for each task.
    This function clears existing work items and recreates them from tasks.md to ensure
    the database is in sync with the file.
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

    # Clear existing work items for this change to avoid duplicates
    # (tasks.md is the source of truth)
    db.query(WorkItem).filter(WorkItem.change_pk == change_pk).delete()
    db.commit()

    synced_items: List[WorkItem] = []
    section_code_to_story: Dict[str, WorkItem] = {}

    # First, create all stories
    for section in sections:
        section_title = section.title.strip() if section.title else f"Section"
        
        # Extract section code (e.g., "1" from "1. Runtime / Backend")
        section_code_match = re.match(r"^(\d+)", section_title)
        section_code = section_code_match.group(1) if section_code_match else None
        
        # Create story for this section
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

    # Now create tasks with proper parent references
    # Tasks from tasks.md should be work items linked to stories (not separate stories or bugs)
    # Bugs should only be created via UI when QA finds a real bug
    for section in sections:
        section_title = section.title.strip() if section.title else f"Section"
        section_code_match = re.match(r"^(\d+)", section_title)
        section_code = section_code_match.group(1) if section_code_match else None
        
        parent_story = section_code_to_story.get(section_code)

        for task_item in section.items:
            task_code = _parse_tasks_code(task_item.text)
            task_title = task_item.title or task_item.text
            
            # Create task linked to story (tasks are child items of stories)
            task = WorkItem(
                change_pk=change_pk,
                type=WorkItemType.task,  # task type, not story or bug
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
        raise HTTPException(status_code=503, detail="Workflow DB disabled. Set WORKFLOW_DB_ENABLED=1.")
    return url


def _slugify_change_title(title: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", title.strip().lower()).strip("-")
    return base or "change"


@router.get("/health")
def workflow_health() -> dict:
    url = _require_db_url()
    url_type = "sqlite" if url.startswith("sqlite") else "postgres"
    return {"enabled": True, "db": url_type}


# --- Audit/sync helpers (Phase 1 transition) ---

class CoordinationAuditResponse(BaseModel):
    project_slug: str
    coordination_active: int
    db_changes: int
    missing_in_db: List[str]
    missing_in_coordination: List[str]


@router.get("/audit/coordination", response_model=CoordinationAuditResponse)
def audit_coordination(project_slug: str = Query(..., min_length=1), db: Session = Depends(get_workflow_db)):
    """Audit drift between file-based coordination artifacts and the workflow DB.

    Policy (Phase 1): DB is operational source of truth. `docs/coordination/*.md`
    remains a mirrored/audit artifact for active changes.

    This endpoint intentionally stays read-only; it helps detect missing seeds or
    accidentally-created DB-only changes.
    """

    from app.services.coordination_service import list_coordination_changes  # local import to keep workflow router isolated

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


class ProjectOut(BaseModel):
    id: str
    slug: str
    name: str


@router.get("/projects", response_model=List[ProjectOut])
def list_projects(db: Session = Depends(get_workflow_db)):
    items = db.query(Project).order_by(Project.created_at.asc()).all()
    return [ProjectOut(id=p.id, slug=p.slug, name=p.name) for p in items]


@router.post("/projects", response_model=ProjectOut)
def create_project(payload: ProjectCreate, db: Session = Depends(get_workflow_db)):
    slug = payload.slug.strip()
    name = payload.name.strip()

    existing = db.query(Project).filter(Project.slug == slug).first()
    if existing:
        return ProjectOut(id=existing.id, slug=existing.slug, name=existing.name)

    p = Project(slug=slug, name=name)
    db.add(p)
    db.commit()
    db.refresh(p)
    return ProjectOut(id=p.id, slug=p.slug, name=p.name)


class ChangeCreate(BaseModel):
    change_id: str = Field(min_length=1, max_length=128)
    title: str = Field(default="", max_length=256)
    description: str = Field(default="", max_length=2000)
    status: str = Field(default="in_progress", max_length=32)
    image_data: List[dict] = Field(default_factory=list)


class ChangeUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=256)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[str] = Field(default=None, max_length=32)
    reorder: Optional[Literal["up", "down"]] = None
    cancel_archive: bool = False
    image_data: Optional[List[dict]] = Field(default=None)


class ChangeOut(BaseModel):
    id: str
    project_id: str
    change_id: str
    title: str
    description: str
    status: str
    card_number: Optional[int] = None
    image_data: List[dict] = Field(default_factory=list)
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
    actor: str = Field(min_length=1, max_length=64)
    note: str = Field(default="", max_length=4000)
    work_item_id: Optional[str] = None


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


def _get_change_by_slug_and_id(db: Session, project_slug: str, change_id: str) -> Change:
    project = _get_project_by_slug(db, project_slug)
    change = db.query(Change).filter(Change.project_id == project.id, Change.change_id == change_id).first()
    if not change:
        raise HTTPException(status_code=404, detail=f"Unknown change '{change_id}' in project '{project_slug}'")
    return change


def _get_change_by_pk(db: Session, change_pk: str) -> Change:
    change = db.query(Change).filter(Change.id == change_pk).first()
    if not change:
        raise HTTPException(status_code=404, detail=f"Unknown change pk '{change_pk}'")
    return change


def _get_work_item(db: Session, change_pk: str, work_item_id: str) -> WorkItem:
    item = db.query(WorkItem).filter(WorkItem.id == work_item_id, WorkItem.change_pk == change_pk).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Unknown work item '{work_item_id}'")
    return item


def _next_card_number(db: Session, project_id: str, exclude_change_pk: Optional[str] = None) -> int:
    query = db.query(Change).filter(Change.project_id == project_id, Change.card_number.is_not(None))
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
        created_at=change.created_at,
        updated_at=change.updated_at,
    )


def _validate_parent(db: Session, change_pk: str, parent_id: Optional[str], child_type: WorkItemType) -> Optional[str]:
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
    p = _get_project_by_slug(db, project_slug)
    _backfill_project_card_numbers(db, p.id)
    db.commit()
    items = db.query(Change).filter(Change.project_id == p.id).order_by(Change.created_at.asc()).all()
    return [_change_out(c) for c in items]


@router.post("/projects/{project_slug}/changes", response_model=ChangeOut)
def create_change(project_slug: str, payload: ChangeCreate, db: Session = Depends(get_workflow_db)):
    p = _get_project_by_slug(db, project_slug)
    change_id = payload.change_id.strip()

    existing = db.query(Change).filter(Change.project_id == p.id, Change.change_id == change_id).first()
    if existing:
        _ensure_change_card_number(db, existing)
        db.commit()
        db.refresh(existing)
        return _change_out(existing)

    c = Change(
        project_id=p.id,
        change_id=change_id,
        title=payload.title.strip(),
        description=payload.description.strip(),
        status=payload.status.strip(),
        card_number=_next_card_number(db, p.id),
        image_data=payload.image_data or [],
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return _change_out(c)


@router.get("/projects/{project_slug}/changes/{change_id}", response_model=ChangeOut)
def get_change(project_slug: str, change_id: str, db: Session = Depends(get_workflow_db)):
    c = _get_change_by_slug_and_id(db, project_slug, change_id)
    _ensure_change_card_number(db, c)
    db.commit()
    db.refresh(c)
    return _change_out(c)


@router.patch("/projects/{project_slug}/changes/{change_id}", response_model=ChangeOut)
def update_change(project_slug: str, change_id: str, payload: ChangeUpdate, db: Session = Depends(get_workflow_db)):
    c = _get_change_by_slug_and_id(db, project_slug, change_id)
    _ensure_change_card_number(db, c)
    current_column = _normalize_column(c.status)

    if payload.title is not None:
        c.title = payload.title.strip()
    if payload.description is not None:
        c.description = payload.description.strip()
    if payload.image_data is not None:
        c.image_data = payload.image_data
    if payload.reorder is not None:
        _reorder_change_within_column(db, c, payload.reorder)
    if payload.status is not None:
        new_status = _normalize_column(payload.status)
        
        # Validation: Cannot move to Alan approval, homologation, or archive without DEV and QA approval
        if new_status in {"Alan approval", "Alan homologation", "Archived"}:
            approvals = (
            approvals = (
            approvals = (
                db.query(WorkflowApproval)
                .filter(
                    WorkflowApproval.change_pk == c.id,
                    WorkflowApproval.scope == ApprovalScope.change,
                )
                .all()
            )
            gate_status = {a.gate: a.state.value for a in approvals}
            
            dev_approved = gate_status.get("DEV") == "approved"
            qa_approved = gate_status.get("QA") == "approved"
            
            if not dev_approved:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "code": "dev_not_approved",
                        "message": "Cannot move to Alan approval without DEV approval",
                    },
                )
            if not qa_approved:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "code": "qa_not_approved",
                        "message": f"Cannot move to {new_status} without QA approval",
                    },
                )
        
        # Validation: Cannot move to Alan approval without OpenSpec artifacts
        if new_status == "Alan approval":
            change_slug = c.change_id
            openspec_dir = Path(REPO_ROOT) / "openspec" / "changes" / change_slug
            
            required_files = ["proposal.md", "review-ptbr.md", "tasks.md"]
            missing_files = [f for f in required_files if not (openspec_dir / f).exists()]
            
            if missing_files:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "code": "missing_openspec_artifacts",
                        "message": f"Cannot move to Alan approval without required files: {', '.join(missing_files)}",
                        "missing_files": missing_files,
                        "target": new_status,
                    },
                )
        
        if new_status == "Archived" and current_column != "Archived":
            # Check for open bugs before allowing archive
            open_bugs = (
                db.query(WorkItem)
                .filter(
                    WorkItem.change_pk == c.id,
                    WorkItem.type == WorkItemType.bug,
                    WorkItem.state.not_in([WorkItemState.done, WorkItemState.canceled]),
                )
                .all()
            )
            if open_bugs:
                bug_titles = [b.title for b in open_bugs[:5]]
                raise HTTPException(
                    status_code=409,
                    detail={
                        "code": "open_bugs_block_archive",
                        "message": f"Cannot archive change with {len(open_bugs)} open bug(s). Close or cancel bugs first.",
                        "open_bugs": bug_titles,
                        "target": new_status,
                    },
                )
            
            if payload.cancel_archive:
                c.status = "Archived"
                c.sort_order = _next_sort_order(db, c.project_id, "Archived", exclude_change_pk=c.id)
                db.commit()
            else:
                try:
                    subprocess.run(
                        ["./scripts/archive_change_safe.sh", change_id],
                        cwd=REPO_ROOT,
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                except subprocess.CalledProcessError as exc:
                    stderr = (exc.stderr or "").strip()
                    stdout = (exc.stdout or "").strip()
                    message = stderr or stdout or "archive flow failed"
                    raise HTTPException(
                        status_code=409,
                        detail={
                            "code": "archive_flow_failed",
                            "message": message,
                            "target": new_status,
                        },
                    ) from exc
        else:
            if new_status in ENFORCED_STATUSES:
                try:
                    require_upstream_published(REPO_ROOT, target_statuses=[new_status])
                except UpstreamGuardError as exc:
                    raise HTTPException(
                        status_code=409,
                        detail={
                            "code": "upstream_guard_blocked",
                            "message": str(exc),
                            "target": new_status,
                        },
                    ) from exc
            sync_change_gates_for_column(db, change=c, target_column=new_status)
            if new_status != current_column:
                _normalize_column_sort_orders(db, c.project_id, current_column)
                c.sort_order = _next_sort_order(db, c.project_id, new_status, exclude_change_pk=c.id)
            db.commit()
    if payload.status is None or new_status == "Archived":
        db.commit()
    db.refresh(c)
    return _change_out(c)


@router.get("/projects/{project_slug}/changes/{change_id}/tasks", response_model=List[WorkItemOut])
def list_tasks(project_slug: str, change_id: str, db: Session = Depends(get_workflow_db)):
    change = _get_change_by_slug_and_id(db, project_slug, change_id)
    items = db.query(WorkItem).filter(WorkItem.change_pk == change.id).order_by(WorkItem.priority.desc(), WorkItem.created_at.asc()).all()
    return [WorkItemOut.model_validate(item, from_attributes=True) for item in items]


@router.post("/projects/{project_slug}/changes/{change_id}/tasks", response_model=WorkItemOut)
def create_task(project_slug: str, change_id: str, payload: WorkItemCreate, db: Session = Depends(get_workflow_db)):
    change = _get_change_by_slug_and_id(db, project_slug, change_id)
    parent_id = _validate_parent(db, change.id, payload.parent_id, payload.type)
    item = WorkItem(
        change_pk=change.id,
        type=payload.type,
        state=payload.state,
        parent_id=parent_id,
        title=payload.title.strip(),
        description=payload.description.strip(),
        priority=payload.priority,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return WorkItemOut.model_validate(item, from_attributes=True)


@router.patch("/work-items/{work_item_id}", response_model=WorkItemOut)
def update_task(work_item_id: str, payload: WorkItemUpdate, db: Session = Depends(get_workflow_db)):
    item = db.query(WorkItem).filter(WorkItem.id == work_item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail=f"Unknown work item '{work_item_id}'")

    if payload.parent_id is not None:
        item.parent_id = _validate_parent(db, item.change_pk, payload.parent_id, item.type)
    if payload.title is not None:
        item.title = payload.title.strip()
    if payload.description is not None:
        item.description = payload.description.strip()
    if payload.state is not None:
        item.state = payload.state
    if payload.priority is not None:
        item.priority = payload.priority

    db.commit()
    db.refresh(item)
    return WorkItemOut.model_validate(item, from_attributes=True)


@router.get("/projects/{project_slug}/changes/{change_id}/comments", response_model=List[CommentOut])
def list_comments(
    project_slug: str,
    change_id: str,
    work_item_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_workflow_db),
):
    change = _get_change_by_slug_and_id(db, project_slug, change_id)
    query = db.query(WorkflowComment)
    if work_item_id:
        _get_work_item(db, change.id, work_item_id)
        query = query.filter(WorkflowComment.work_item_id == work_item_id)
    else:
        query = query.filter(WorkflowComment.change_pk == change.id, WorkflowComment.scope == CommentScope.change)
    items = query.order_by(WorkflowComment.created_at.asc()).all()
    return [_comment_out(item) for item in items]


@router.post("/projects/{project_slug}/changes/{change_id}/comments", response_model=CommentOut)
def create_comment(project_slug: str, change_id: str, payload: CommentCreate, db: Session = Depends(get_workflow_db)):
    change = _get_change_by_slug_and_id(db, project_slug, change_id)
    work_item_id = None
    if payload.scope == "work_item":
        if not payload.work_item_id:
            raise HTTPException(status_code=400, detail="work_item_id is required for work_item scoped comments")
        work_item_id = _get_work_item(db, change.id, payload.work_item_id).id
    item = WorkflowComment(
        scope=CommentScope(payload.scope),
        change_pk=change.id if payload.scope == "change" else None,
        work_item_id=work_item_id,
        author=payload.author.strip(),
        body=payload.body.strip(),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return _comment_out(item)


@router.get("/projects/{project_slug}/changes/{change_id}/approvals", response_model=List[ApprovalOut])
def list_approvals(
    project_slug: str,
    change_id: str,
    work_item_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_workflow_db),
):
    change = _get_change_by_slug_and_id(db, project_slug, change_id)
    query = db.query(WorkflowApproval)
    if work_item_id:
        _get_work_item(db, change.id, work_item_id)
        query = query.filter(WorkflowApproval.work_item_id == work_item_id)
    else:
        query = query.filter(WorkflowApproval.change_pk == change.id, WorkflowApproval.scope == ApprovalScope.change)
    items = query.order_by(WorkflowApproval.created_at.asc()).all()
    return [_approval_out(item) for item in items]


@router.post("/projects/{project_slug}/changes/{change_id}/approvals", response_model=ApprovalOut)
def create_approval(project_slug: str, change_id: str, payload: ApprovalCreate, db: Session = Depends(get_workflow_db)):
    change = _get_change_by_slug_and_id(db, project_slug, change_id)
    work_item_id = None
    if payload.scope == "work_item":
        if not payload.work_item_id:
            raise HTTPException(status_code=400, detail="work_item_id is required for work_item scoped approvals")
        work_item_id = _get_work_item(db, change.id, payload.work_item_id).id
    item = WorkflowApproval(
        scope=ApprovalScope(payload.scope),
        gate=payload.gate.strip(),
        state=payload.state,
        change_pk=change.id if payload.scope == "change" else None,
        work_item_id=work_item_id,
        actor=payload.actor.strip(),
        note=payload.note.strip(),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return _approval_out(item)


@router.get("/projects/{project_slug}/changes/{change_id}/handoffs", response_model=List[HandoffOut])
def list_handoffs(
    project_slug: str,
    change_id: str,
    work_item_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_workflow_db),
):
    change = _get_change_by_slug_and_id(db, project_slug, change_id)
    query = db.query(WorkflowHandoff)
    if work_item_id:
        _get_work_item(db, change.id, work_item_id)
        query = query.filter(WorkflowHandoff.work_item_id == work_item_id)
    else:
        query = query.filter(WorkflowHandoff.change_pk == change.id, WorkflowHandoff.scope == HandoffScope.change)
    items = query.order_by(WorkflowHandoff.created_at.asc()).all()
    return [_handoff_out(item) for item in items]


@router.post("/projects/{project_slug}/changes/{change_id}/handoffs", response_model=HandoffOut)
def create_handoff(project_slug: str, change_id: str, payload: HandoffCreate, db: Session = Depends(get_workflow_db)):
    change = _get_change_by_slug_and_id(db, project_slug, change_id)
    work_item_id = None
    if payload.scope == "work_item":
        if not payload.work_item_id:
            raise HTTPException(status_code=400, detail="work_item_id is required for work_item scoped handoffs")
        work_item_id = _get_work_item(db, change.id, payload.work_item_id).id
    item = WorkflowHandoff(
        scope=HandoffScope(payload.scope),
        change_pk=change.id if payload.scope == "change" else None,
        work_item_id=work_item_id,
        from_role=payload.from_role.strip(),
        to_role=payload.to_role.strip(),
        summary=payload.summary.strip(),
    )
    db.add(item)
    db.commit()
    db.refresh(item)
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
        .filter(WorkflowApproval.scope == ApprovalScope.change, WorkflowApproval.change_pk == change_pk)
        .order_by(WorkflowApproval.created_at.asc())
        .all()
    )
    for a in approvals:
        out[a.gate] = a.state.value
    return out


def _publish_state_for_change(change: Change) -> str:
    try:
        result = require_upstream_published(REPO_ROOT, target_statuses=["Alan homologation"])
        return "ready" if result.ok else "blocked"
    except UpstreamGuardError:
        return "blocked"


def _homologation_readiness(change: Change, gate_status: Dict[str, str], column: str) -> str:
    qa_functional = gate_status.get("QA") or "pending"
    publish_state = _publish_state_for_change(change)

    if qa_functional != "approved":
        return "blocked: QA functional pending"
    if publish_state != "ready":
        return "blocked: publish/reconcile pending"
    if column not in {"Alan homologation", "Archived"}:
        return f"blocked: runtime stage still in {column}"
    return "ready"


def _kanban_change_status(db: Session, change: Change) -> Dict[str, str]:
    gate_status = _latest_change_gate_status(db, change.id)
    column = _normalize_column(change.status)
    out = dict(gate_status)
    out["QA functional"] = gate_status.get("QA") or "pending"
    out["Publish"] = _publish_state_for_change(change)
    out["Runtime stage"] = column
    out["Homologation readiness"] = _homologation_readiness(change, gate_status, column)
    return out


def _normalize_column(raw: Optional[str]) -> str:
    col = raw.strip() if raw else "DEV"
    if col.lower() == "archived":
        col = "Archived"
    if col not in KANBAN_COLUMNS:
        col = "DEV"
    return col


def _next_sort_order(db: Session, project_id: str, column: str, exclude_change_pk: Optional[str] = None) -> int:
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


def _reorder_change_within_column(db: Session, change: Change, direction: Literal["up", "down"]) -> None:
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
) -> KanbanChangeCreateResponse:
    slug = _kanban_project_slug(db, project_slug)
    project = _get_project_by_slug(db, slug)

    base_id = _slugify_change_title(payload.title)
    change_id = base_id
    suffix = 2
    while db.query(Change).filter(Change.project_id == project.id, Change.change_id == change_id).first():
        change_id = f"{base_id}-{suffix}"
        suffix += 1

    change = Change(
        project_id=project.id,
        change_id=change_id,
        title=payload.title.strip(),
        description=payload.description.strip(),
        status="Pending",
        sort_order=_next_sort_order(db, project.id, "Pending"),
        card_number=_next_card_number(db, project.id),
        image_data=payload.image_data or [],
    )
    db.add(change)
    db.commit()
    db.refresh(change)

    return KanbanChangeCreateResponse(
        item=KanbanChangeItem(
            id=change.change_id,
            title=change.title or None,
            description=change.description or None,
            card_number=change.card_number,
            path=f"openspec/changes/{change.change_id}/proposal",
            status=_kanban_change_status(db, change),
            archived=False,
            column="Pending",
            position=change.sort_order,
            image_data=_parse_json_field(change.image_data),
        )
    )


@router.get("/kanban/changes", response_model=KanbanChangeListResponse)
def kanban_list_changes(
    project_slug: Optional[str] = Query(default=None),
    db: Session = Depends(get_workflow_db),
) -> KanbanChangeListResponse:
    slug = _kanban_project_slug(db, project_slug)
    project = _get_project_by_slug(db, slug)

    _backfill_project_card_numbers(db, project.id)
    db.commit()
    items = (
        db.query(Change)
        .filter(Change.project_id == project.id)
        .order_by(Change.created_at.asc())
        .all()
    )
    out: List[KanbanChangeItem] = []

    # Best-effort reconciliation so the Kanban doesn't get stuck when agents
    # complete artifacts but forget to update workflow DB gates/status.
    from app.services.workflow_reconcile_service import reconcile_change_forward

    # Get OpenSpec archived IDs to ensure Kanban stays consistent
    from app.services.coordination_service import _archived_change_ids_from_openspec
    openspec_archived_ids = _archived_change_ids_from_openspec()

    # Build a map of change_pk to change for bug lookup
    change_map = {c.id: c for c in items}

    for c in items:
        reconcile_change_forward(db, change=c)
        status = _kanban_change_status(db, c)
        col = _normalize_column(c.status)
        # OpenSpec archive status wins to avoid inconsistencies
        archived = col == "Archived" or c.change_id in openspec_archived_ids
        if archived:
            col = "Archived"
        # Check if this change has any bugs
        has_bugs = (
            db.query(WorkItem)
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
            )
        )

    # Also include bugs as separate cards
    # Query only bugs from non-archived changes in this project
    active_change_ids = [c.id for c in items if c.change_id not in openspec_archived_ids]
    bugs = (
        db.query(WorkItem)
        .filter(WorkItem.type == WorkItemType.bug)
        .filter(WorkItem.change_pk.in_(active_change_ids))
        .all()
    )

    # Filter bugs that belong to changes in this project
    for bug in bugs:
        if bug.change_pk not in change_map:
            continue
        
        parent_story = None
        parent_story_title = None
        if bug.parent_id:
            parent_story = db.query(WorkItem).filter(WorkItem.id == bug.parent_id).first()
            if parent_story:
                parent_story_title = parent_story.title

        # Get the parent change to determine column and status
        parent_change = change_map.get(bug.change_pk)
        if not parent_change:
            continue

        # Bug column is based on the change's status
        bug_col = _normalize_column(parent_change.status)
        if parent_change.change_id in openspec_archived_ids:
            bug_col = "Archived"

        # Bug status shows its own state
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
                archived=bug_col == "Archived",
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
    out.sort(key=lambda item: (column_index.get(item.column, 999), item.position, (item.title or item.id).lower(), item.id))
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


def _kanban_task_item(it: WorkItem, children: Optional[List[TaskChecklistItem]] = None) -> TaskChecklistItem:
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
    change = _kanban_change_by_id(db, slug, change_id)

    # Sync tasks.md to database before fetching
    sync_tasks_to_workflow_db(db, change.id, change_id)

    items = (
        db.query(WorkItem)
        .filter(WorkItem.change_pk == change.id)
        .order_by(WorkItem.priority.desc(), WorkItem.created_at.asc())
        .all()
    )

    stories = [it for it in items if it.type == WorkItemType.story]
    bugs = [it for it in items if it.type == WorkItemType.bug]

    bugs_by_parent: Dict[Optional[str], List[WorkItem]] = {}
    for b in bugs:
        bugs_by_parent.setdefault(b.parent_id, []).append(b)

    # Maintain the overall ordering for children too (priority desc, then created).
    for k in list(bugs_by_parent.keys()):
        bugs_by_parent[k] = sorted(
            bugs_by_parent[k],
            key=lambda x: (-int(x.priority or 0), x.created_at),
        )

    out_items: List[TaskChecklistItem] = []

    for s in stories:
        children = [_kanban_task_item(b) for b in bugs_by_parent.get(s.id, [])]
        out_items.append(_kanban_task_item(s, children=children))

    # Orphan bugs (no parent story) show up as top-level items.
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
    change = _kanban_change_by_id(db, slug, change_id)

    # Forward-migrate any legacy JSONL comments into the workflow DB.
    # This prevents evidence loss in the Kanban drawer if an agent/tool still
    # writes to the old coordination surface.
    try:
        from app.services.workflow_coordination_bridge import (
            migrate_coordination_comments_into_workflow_db,
        )

        migrate_coordination_comments_into_workflow_db(db, change_pk=change.id, change_id=change_id)
    except Exception:
        # Never break Kanban if migration fails.
        pass

    items = (
        db.query(WorkflowComment)
        .filter(WorkflowComment.scope == CommentScope.change, WorkflowComment.change_pk == change.id)
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
) -> KanbanCommentCreateResponse:
    slug = _kanban_project_slug(db, project_slug)
    change = _kanban_change_by_id(db, slug, change_id)

    item = WorkflowComment(
        scope=CommentScope.change,
        change_pk=change.id,
        work_item_id=None,
        author=payload.author.strip(),
        body=payload.body.strip(),
    )
    db.add(item)
    db.commit()
    db.refresh(item)

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
def scheduler_force_run() -> dict:
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
) -> dict:
    """Configure suppression behavior."""
    from app.services.workflow_polling_suppressor import get_suppressor
    
    suppressor = get_suppressor()
    suppressor.configure(
        suppression_enabled=suppression_enabled,
        max_suppressed_turns=max_suppressed_turns,
        suppression_timeout_minutes=suppression_timeout_minutes,
    )
    
    return {"status": "ok", "configured": {
        "suppression_enabled": suppression_enabled,
        "max_suppressed_turns": max_suppressed_turns,
        "suppression_timeout_minutes": suppression_timeout_minutes,
    }}
