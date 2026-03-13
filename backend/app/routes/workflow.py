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
import subprocess
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

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


class ChangeUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=256)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[str] = Field(default=None, max_length=32)


class ChangeOut(BaseModel):
    id: str
    project_id: str
    change_id: str
    title: str
    description: str
    status: str
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
    items = db.query(Change).filter(Change.project_id == p.id).order_by(Change.created_at.asc()).all()
    return [
        ChangeOut(
            id=c.id,
            project_id=c.project_id,
            change_id=c.change_id,
            title=c.title,
            description=c.description,
            status=c.status,
            created_at=c.created_at,
            updated_at=c.updated_at,
        )
        for c in items
    ]


@router.post("/projects/{project_slug}/changes", response_model=ChangeOut)
def create_change(project_slug: str, payload: ChangeCreate, db: Session = Depends(get_workflow_db)):
    p = _get_project_by_slug(db, project_slug)
    change_id = payload.change_id.strip()

    existing = db.query(Change).filter(Change.project_id == p.id, Change.change_id == change_id).first()
    if existing:
        return ChangeOut(
            id=existing.id,
            project_id=existing.project_id,
            change_id=existing.change_id,
            title=existing.title,
            description=existing.description,
            status=existing.status,
            created_at=existing.created_at,
            updated_at=existing.updated_at,
        )

    c = Change(
        project_id=p.id,
        change_id=change_id,
        title=payload.title.strip(),
        description=payload.description.strip(),
        status=payload.status.strip(),
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return ChangeOut(
        id=c.id,
        project_id=c.project_id,
        change_id=c.change_id,
        title=c.title,
        description=c.description,
        status=c.status,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


@router.get("/projects/{project_slug}/changes/{change_id}", response_model=ChangeOut)
def get_change(project_slug: str, change_id: str, db: Session = Depends(get_workflow_db)):
    c = _get_change_by_slug_and_id(db, project_slug, change_id)
    return ChangeOut(
        id=c.id,
        project_id=c.project_id,
        change_id=c.change_id,
        title=c.title,
        description=c.description,
        status=c.status,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


@router.patch("/projects/{project_slug}/changes/{change_id}", response_model=ChangeOut)
def update_change(project_slug: str, change_id: str, payload: ChangeUpdate, db: Session = Depends(get_workflow_db)):
    c = _get_change_by_slug_and_id(db, project_slug, change_id)
    if payload.title is not None:
        c.title = payload.title.strip()
    if payload.description is not None:
        c.description = payload.description.strip()
    if payload.status is not None:
        new_status = payload.status.strip()
        if new_status == "Archived" and (c.status or "").strip() != "Archived":
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
            db.commit()
    if payload.status is None or new_status == "Archived":
        db.commit()
    db.refresh(c)
    return ChangeOut(
        id=c.id,
        project_id=c.project_id,
        change_id=c.change_id,
        title=c.title,
        description=c.description,
        status=c.status,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


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
    path: str
    status: Dict[str, str]
    archived: bool
    column: str


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
    )
    db.add(change)
    db.commit()
    db.refresh(change)

    return KanbanChangeCreateResponse(
        item=KanbanChangeItem(
            id=change.change_id,
            title=change.title or None,
            description=change.description or None,
            path=f"openspec/changes/{change.change_id}/proposal",
            status=_latest_change_gate_status(db, change.id),
            archived=False,
            column="Pending",
        )
    )


@router.get("/kanban/changes", response_model=KanbanChangeListResponse)
def kanban_list_changes(
    project_slug: Optional[str] = Query(default=None),
    db: Session = Depends(get_workflow_db),
) -> KanbanChangeListResponse:
    slug = _kanban_project_slug(db, project_slug)
    project = _get_project_by_slug(db, slug)

    items = db.query(Change).filter(Change.project_id == project.id).order_by(Change.created_at.asc()).all()
    out: List[KanbanChangeItem] = []

    # Best-effort reconciliation so the Kanban doesn't get stuck when agents
    # complete artifacts but forget to update workflow DB gates/status.
    from app.services.workflow_reconcile_service import reconcile_change_forward

    for c in items:
        reconcile_change_forward(db, change=c)
        status = _latest_change_gate_status(db, c.id)
        col = c.status.strip() if c.status else "DEV"
        if col.lower() == "archived":
            col = "Archived"
        if col not in KANBAN_COLUMNS:
            col = "DEV"
        archived = col == "Archived"
        out.append(
            KanbanChangeItem(
                id=c.change_id,
                title=c.title or None,
                description=c.description or None,
                path=f"openspec/changes/{c.change_id}/proposal",
                status=status,
                archived=archived,
                column=col,
            )
        )

    return KanbanChangeListResponse(items=out)


def _kanban_task_checked(state: WorkItemState) -> bool:
    return state in (WorkItemState.done, WorkItemState.canceled)


def _kanban_task_item(it: WorkItem, children: Optional[List[TaskChecklistItem]] = None) -> TaskChecklistItem:
    label = "Story" if it.type == WorkItemType.story else "Bug"
    return TaskChecklistItem(
        text=it.title,
        checked=_kanban_task_checked(it.state),
        code=it.id,
        title=label,
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
    """

    slug = _kanban_project_slug(db, project_slug)
    change = _kanban_change_by_id(db, slug, change_id)

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
        path=f"openspec/changes/{change_id}/tasks.md",
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
