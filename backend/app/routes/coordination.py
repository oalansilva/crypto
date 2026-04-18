"""Coordination/Kanban endpoints (MVP).

- Changes list + status/column are derived from docs/coordination/*.md.
- Tasks checklist is parsed from openspec/changes/<change>/tasks.md.
- Comments are persisted server-side (append-only JSONL per change).
"""

from __future__ import annotations

from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.change_tasks_service import get_change_tasks_checklist
from app.services.coordination_comments_service import add_comment, list_comments
from app.services.coordination_service import list_coordination_changes
from app.workflow_database import get_registry_workflow_sessionmaker
from app.workflow_models import Change, Project

router = APIRouter(prefix="/api/coordination", tags=["coordination"])


class CoordinationChangeItem(BaseModel):
    id: str
    title: Optional[str] = None
    path: str
    status: Dict[str, str]
    archived: bool
    column: str


class CoordinationChangeListResponse(BaseModel):
    items: List[CoordinationChangeItem]


@router.get("/changes", response_model=CoordinationChangeListResponse)
async def list_changes() -> CoordinationChangeListResponse:
    items = list_coordination_changes()
    return CoordinationChangeListResponse(items=items)


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


class ChangeTasksChecklistResponse(BaseModel):
    change_id: str
    path: str
    sections: List[TaskChecklistSection]


@router.get("/changes/{change_id}/tasks", response_model=ChangeTasksChecklistResponse)
async def change_tasks(change_id: str) -> ChangeTasksChecklistResponse:
    payload = get_change_tasks_checklist(change_id)
    return ChangeTasksChecklistResponse(**payload)


class CoordinationCommentItem(BaseModel):
    id: str
    change: str
    author: str
    created_at: str
    body: str


class CoordinationCommentsListResponse(BaseModel):
    change_id: str
    items: List[CoordinationCommentItem]


@router.get("/changes/{change_id}/comments", response_model=CoordinationCommentsListResponse)
async def get_comments(change_id: str) -> CoordinationCommentsListResponse:
    try:
        items = list_comments(change_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Unknown change '{change_id}'")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return CoordinationCommentsListResponse(change_id=change_id, items=items)


class CoordinationCommentCreateRequest(BaseModel):
    author: str
    body: str = Field(max_length=2000)


class CoordinationCommentCreateResponse(BaseModel):
    item: CoordinationCommentItem


@router.post("/changes/{change_id}/comments", response_model=CoordinationCommentCreateResponse)
async def post_comment(
    change_id: str,
    payload: CoordinationCommentCreateRequest,
) -> CoordinationCommentCreateResponse:
    try:
        item = add_comment(change_id=change_id, author=payload.author, body=payload.body)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Unknown change '{change_id}'")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # Best-effort dual-write into the workflow DB so the Kanban drawer (which
    # reads wf_comments) always renders evidence even if a client posts to the
    # legacy coordination endpoint.
    try:
        workflow_session_local = get_registry_workflow_sessionmaker()
        if workflow_session_local is not None:
            from app.services.workflow_coordination_bridge import (
                dual_write_coordination_comment_to_workflow_db,
            )

            with workflow_session_local() as db:
                project = db.query(Project).order_by(Project.created_at.asc()).first()
                if project is not None:
                    change = (
                        db.query(Change)
                        .filter(Change.project_id == project.id, Change.change_id == change_id)
                        .first()
                    )
                    if change is not None:
                        dual_write_coordination_comment_to_workflow_db(
                            db,
                            change_pk=change.id,
                            comment_id=str(item.get("id") or ""),
                            author=str(item.get("author") or ""),
                            body=str(item.get("body") or ""),
                            created_at_iso=str(item.get("created_at") or ""),
                        )
    except Exception:
        # Never break legacy endpoint if workflow DB write fails.
        pass

    return CoordinationCommentCreateResponse(item=item)
