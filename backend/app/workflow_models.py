# file: backend/app/workflow_models.py
"""SQLAlchemy models for the workflow core (multi-project).

MVP scope:
- Multi-project support from day one.
- `change` as the root container (maps 1:1 with an OpenSpec change_id).
- Work items: `story` and `bug`.
- Parent-child: only story -> bug is required/blocked in MVP.
- Dependencies between work items.
- Agent runs and exclusive locks at the story scope.
- Append-only comments (initially change/work_item scoped).

Notes:
- We intentionally keep the schema minimal and evolvable while still covering
  the MVP runtime surfaces needed by the Kanban/API layer.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.workflow_database import WorkflowBase


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class WorkItemType(str, enum.Enum):
    story = "story"
    task = "task"
    bug = "bug"


class WorkItemState(str, enum.Enum):
    queued = "queued"
    active = "active"
    blocked = "blocked"
    done = "done"
    canceled = "canceled"


class AgentRunStatus(str, enum.Enum):
    active = "active"
    completed = "completed"
    failed = "failed"
    canceled = "canceled"


class Project(WorkflowBase):
    __tablename__ = "wf_projects"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    slug: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True
    )  # e.g. "crypto"
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    root_directory: Mapped[str | None] = mapped_column(String(512), nullable=True)
    database_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    frontend_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    backend_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    workflow_database_url: Mapped[str | None] = mapped_column(
        String(1024), nullable=True
    )
    tech_stack: Mapped[str | None] = mapped_column(String(512), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    changes = relationship("Change", back_populates="project")


class Change(WorkflowBase):
    __tablename__ = "wf_changes"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("wf_projects.id", ondelete="CASCADE"), nullable=False
    )

    # OpenSpec change_id, e.g. "centralize-workflow-state-db"
    change_id: Mapped[str] = mapped_column(String(128), nullable=False)

    title: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="in_progress"
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    card_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Image attachments stored as JSON: [{"filename": "xxx.jpg", "data": "base64..."}]
    image_data: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    project = relationship("Project", back_populates="changes")
    work_items = relationship(
        "WorkItem", back_populates="change", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint(
            "project_id", "change_id", name="uq_wf_changes_project_change"
        ),
        Index("ix_wf_changes_project", "project_id"),
    )


class WorkItem(WorkflowBase):
    __tablename__ = "wf_work_items"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    change_pk: Mapped[str] = mapped_column(
        String(36), ForeignKey("wf_changes.id", ondelete="CASCADE"), nullable=False
    )

    type: Mapped[WorkItemType] = mapped_column(
        Enum(WorkItemType, name="wf_work_item_type"), nullable=False
    )
    state: Mapped[WorkItemState] = mapped_column(
        Enum(WorkItemState, name="wf_work_item_state"),
        nullable=False,
        default=WorkItemState.queued,
    )

    # Parent-child: MVP focuses on story -> bug, but we model it generically.
    parent_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("wf_work_items.id", ondelete="SET NULL"), nullable=True
    )

    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")

    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    owner_run_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("wf_agent_runs.id", ondelete="SET NULL"), nullable=True
    )

    stage_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    stage_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_agent_acted: Mapped[str | None] = mapped_column(String(64), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )

    change = relationship("Change", back_populates="work_items")
    parent = relationship("WorkItem", remote_side=[id], back_populates="children")
    children = relationship("WorkItem", back_populates="parent")

    dependencies = relationship(
        "WorkItemDependency",
        foreign_keys="WorkItemDependency.work_item_id",
        cascade="all, delete-orphan",
        back_populates="work_item",
    )
    dependents = relationship(
        "WorkItemDependency",
        foreign_keys="WorkItemDependency.depends_on_id",
        cascade="all, delete-orphan",
        back_populates="depends_on",
    )

    owner_run = relationship(
        "AgentRun", foreign_keys=[owner_run_id], back_populates="owned_work_items"
    )
    lock = relationship(
        "WorkItemLock",
        uselist=False,
        back_populates="work_item",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("ix_wf_work_items_change", "change_pk"),
        Index("ix_wf_work_items_parent", "parent_id"),
        Index("ix_wf_work_items_owner_run", "owner_run_id"),
        CheckConstraint(
            "NOT (type = 'story' AND parent_id IS NOT NULL)",
            name="ck_wf_story_has_no_parent",
        ),
    )


class WorkItemDependency(WorkflowBase):
    __tablename__ = "wf_work_item_deps"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    work_item_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("wf_work_items.id", ondelete="CASCADE"), nullable=False
    )
    depends_on_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("wf_work_items.id", ondelete="CASCADE"), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    work_item = relationship(
        "WorkItem", foreign_keys=[work_item_id], back_populates="dependencies"
    )
    depends_on = relationship(
        "WorkItem", foreign_keys=[depends_on_id], back_populates="dependents"
    )

    __table_args__ = (
        UniqueConstraint("work_item_id", "depends_on_id", name="uq_wf_dep_pair"),
        CheckConstraint("work_item_id <> depends_on_id", name="ck_wf_dep_not_self"),
    )


class AgentRun(WorkflowBase):
    __tablename__ = "wf_agent_runs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    change_pk: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("wf_changes.id", ondelete="CASCADE"), nullable=True
    )
    agent: Mapped[str] = mapped_column(
        String(64), nullable=False
    )  # e.g. "dev", "po", etc.
    label: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    status: Mapped[AgentRunStatus] = mapped_column(
        Enum(AgentRunStatus, name="wf_agent_run_status"),
        nullable=False,
        default=AgentRunStatus.active,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    meta: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    change = relationship("Change")
    owned_work_items = relationship(
        "WorkItem", foreign_keys="WorkItem.owner_run_id", back_populates="owner_run"
    )

    __table_args__ = (
        Index("ix_wf_agent_runs_change", "change_pk"),
        Index("ix_wf_agent_runs_status", "status"),
    )


class WorkItemLock(WorkflowBase):
    __tablename__ = "wf_work_item_locks"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    work_item_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("wf_work_items.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    owner_run_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("wf_agent_runs.id", ondelete="SET NULL"), nullable=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    acquired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )
    released_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    work_item = relationship("WorkItem", back_populates="lock")
    owner_run = relationship("AgentRun")

    __table_args__ = (Index("ix_wf_locks_owner", "owner_run_id"),)


class CommentScope(str, enum.Enum):
    change = "change"
    work_item = "work_item"


class WorkflowComment(WorkflowBase):
    __tablename__ = "wf_comments"

    # Legacy coordination comment ids are not always UUIDs (can be ~45 chars),
    # so we allow a wider PK.
    id: Mapped[str] = mapped_column(
        String(64), primary_key=True, default=lambda: str(uuid.uuid4())
    )

    scope: Mapped[CommentScope] = mapped_column(
        Enum(CommentScope, name="wf_comment_scope"), nullable=False
    )

    # Scope targets
    change_pk: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("wf_changes.id", ondelete="CASCADE"), nullable=True
    )
    work_item_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("wf_work_items.id", ondelete="CASCADE"), nullable=True
    )

    author: Mapped[str] = mapped_column(String(64), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "(scope = 'change' AND change_pk IS NOT NULL AND work_item_id IS NULL) OR "
            "(scope = 'work_item' AND work_item_id IS NOT NULL)",
            name="ck_wf_comment_scope_target",
        ),
        Index("ix_wf_comments_change", "change_pk"),
        Index("ix_wf_comments_work_item", "work_item_id"),
    )


class ApprovalScope(str, enum.Enum):
    change = "change"
    work_item = "work_item"


class ApprovalState(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class WorkflowApproval(WorkflowBase):
    __tablename__ = "wf_approvals"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    scope: Mapped[ApprovalScope] = mapped_column(
        Enum(ApprovalScope, name="wf_approval_scope"), nullable=False
    )
    gate: Mapped[str] = mapped_column(String(64), nullable=False)
    state: Mapped[ApprovalState] = mapped_column(
        Enum(ApprovalState, name="wf_approval_state"), nullable=False
    )

    change_pk: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("wf_changes.id", ondelete="CASCADE"), nullable=True
    )
    work_item_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("wf_work_items.id", ondelete="CASCADE"), nullable=True
    )

    actor: Mapped[str] = mapped_column(String(64), nullable=False)
    note: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "(scope = 'change' AND change_pk IS NOT NULL AND work_item_id IS NULL) OR "
            "(scope = 'work_item' AND work_item_id IS NOT NULL)",
            name="ck_wf_approval_scope_target",
        ),
        Index("ix_wf_approvals_change", "change_pk"),
        Index("ix_wf_approvals_work_item", "work_item_id"),
        Index("ix_wf_approvals_gate", "gate"),
    )


class HandoffScope(str, enum.Enum):
    change = "change"
    work_item = "work_item"


class WorkflowHandoff(WorkflowBase):
    __tablename__ = "wf_handoffs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    scope: Mapped[HandoffScope] = mapped_column(
        Enum(HandoffScope, name="wf_handoff_scope"), nullable=False
    )

    change_pk: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("wf_changes.id", ondelete="CASCADE"), nullable=True
    )
    work_item_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("wf_work_items.id", ondelete="CASCADE"), nullable=True
    )

    from_role: Mapped[str] = mapped_column(String(64), nullable=False)
    to_role: Mapped[str] = mapped_column(String(64), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "(scope = 'change' AND change_pk IS NOT NULL AND work_item_id IS NULL) OR "
            "(scope = 'work_item' AND work_item_id IS NOT NULL)",
            name="ck_wf_handoff_scope_target",
        ),
        Index("ix_wf_handoffs_change", "change_pk"),
        Index("ix_wf_handoffs_work_item", "work_item_id"),
        Index("ix_wf_handoffs_to_role", "to_role"),
    )
