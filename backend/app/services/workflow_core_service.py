from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.workflow_models import (
    AgentRun,
    AgentRunStatus,
    Change,
    WorkItem,
    WorkItemDependency,
    WorkItemLock,
    WorkItemState,
    WorkItemType,
)


class WorkflowRuleViolation(ValueError):
    pass


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class StoryAssignmentResult:
    work_item: WorkItem
    run: AgentRun
    lock: WorkItemLock


def _get_work_item(db: Session, work_item_id: str) -> WorkItem:
    item = db.query(WorkItem).filter(WorkItem.id == work_item_id).first()
    if not item:
        raise WorkflowRuleViolation(f"Unknown work item '{work_item_id}'")
    return item


def _get_run(db: Session, run_id: str) -> AgentRun:
    run = db.query(AgentRun).filter(AgentRun.id == run_id).first()
    if not run:
        raise WorkflowRuleViolation(f"Unknown agent run '{run_id}'")
    return run


def create_agent_run(
    db: Session,
    *,
    agent: str,
    change_pk: str | None = None,
    label: str = "",
    meta: dict | None = None,
) -> AgentRun:
    run = AgentRun(
        agent=agent,
        change_pk=change_pk,
        label=label,
        status=AgentRunStatus.active,
        meta=meta or {},
    )
    db.add(run)
    db.flush()
    return run


def add_dependency(db: Session, *, work_item_id: str, depends_on_id: str) -> WorkItemDependency:
    work_item = _get_work_item(db, work_item_id)
    depends_on = _get_work_item(db, depends_on_id)

    if work_item.change_pk != depends_on.change_pk:
        raise WorkflowRuleViolation("Dependencies must stay within the same change")

    if work_item.type != WorkItemType.story or depends_on.type != WorkItemType.story:
        raise WorkflowRuleViolation("MVP dependencies are only supported between stories")

    existing = (
        db.query(WorkItemDependency)
        .filter(WorkItemDependency.work_item_id == work_item_id)
        .filter(WorkItemDependency.depends_on_id == depends_on_id)
        .first()
    )
    if existing:
        return existing

    dep = WorkItemDependency(work_item_id=work_item_id, depends_on_id=depends_on_id)
    db.add(dep)
    db.flush()
    return dep


def assign_story_to_run(db: Session, *, work_item_id: str, run_id: str) -> StoryAssignmentResult:
    work_item = _get_work_item(db, work_item_id)
    run = _get_run(db, run_id)

    if work_item.type != WorkItemType.story:
        raise WorkflowRuleViolation("Only stories can be directly assigned to an agent run in MVP")

    if run.status != AgentRunStatus.active or run.ended_at is not None:
        raise WorkflowRuleViolation("Only active agent runs can own a story")

    if run.change_pk is not None and run.change_pk != work_item.change_pk:
        raise WorkflowRuleViolation("Agent run and story must belong to the same change")

    blocked_deps = [
        dep.depends_on_id
        for dep in work_item.dependencies
        if dep.depends_on.state != WorkItemState.done
    ]
    if blocked_deps:
        raise WorkflowRuleViolation(
            "Story cannot be assigned while dependency predecessors are still open"
        )

    active_story_count = (
        db.query(WorkItem)
        .filter(WorkItem.change_pk == work_item.change_pk)
        .filter(WorkItem.type == WorkItemType.story)
        .filter(WorkItem.state == WorkItemState.active)
        .filter(WorkItem.id != work_item.id)
        .count()
    )
    if work_item.state != WorkItemState.active and active_story_count >= 2:
        raise WorkflowRuleViolation("Change WIP limit exceeded: at most 2 active stories in MVP")

    run_active_story = (
        db.query(WorkItem)
        .filter(WorkItem.owner_run_id == run.id)
        .filter(WorkItem.type == WorkItemType.story)
        .filter(WorkItem.state == WorkItemState.active)
        .filter(WorkItem.id != work_item.id)
        .first()
    )
    if run_active_story:
        raise WorkflowRuleViolation("Agent run already owns another active story")

    existing_active_lock = (
        db.query(WorkItemLock)
        .filter(WorkItemLock.work_item_id == work_item.id)
        .filter(WorkItemLock.is_active.is_(True))
        .first()
    )
    if existing_active_lock and existing_active_lock.owner_run_id != run.id:
        raise WorkflowRuleViolation("Story already has an active lock owned by another run")

    if (
        work_item.owner_run_id
        and work_item.owner_run_id != run.id
        and work_item.state == WorkItemState.active
    ):
        raise WorkflowRuleViolation("Story already has another active owner")

    work_item.owner_run_id = run.id
    work_item.state = WorkItemState.active

    if existing_active_lock:
        lock = existing_active_lock
    else:
        lock = WorkItemLock(work_item_id=work_item.id, owner_run_id=run.id, is_active=True)
        db.add(lock)
        db.flush()

    lock.owner_run_id = run.id
    lock.is_active = True
    lock.released_at = None

    db.flush()
    return StoryAssignmentResult(work_item=work_item, run=run, lock=lock)


def release_story_assignment(
    db: Session, *, work_item_id: str, final_state: WorkItemState = WorkItemState.done
) -> WorkItem:
    work_item = _get_work_item(db, work_item_id)

    if work_item.type != WorkItemType.story:
        raise WorkflowRuleViolation("Only stories can be explicitly released in MVP")

    open_child_bug = next(
        (
            child
            for child in work_item.children
            if child.type == WorkItemType.bug and child.state != WorkItemState.done
        ),
        None,
    )
    if final_state == WorkItemState.done and open_child_bug is not None:
        raise WorkflowRuleViolation("Story cannot be completed while child bugs remain open")

    if work_item.lock and work_item.lock.is_active:
        work_item.lock.is_active = False
        work_item.lock.released_at = utcnow()

    work_item.owner_run_id = None
    work_item.state = final_state
    db.flush()
    return work_item
