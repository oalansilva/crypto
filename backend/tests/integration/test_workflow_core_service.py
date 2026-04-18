from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.workflow_database import WorkflowBase
from app.workflow_models import Change, Project, WorkItem, WorkItemState, WorkItemType
from app.services.workflow_core_service import (
    WorkflowRuleViolation,
    add_dependency,
    assign_story_to_run,
    create_agent_run,
    release_story_assignment,
)


def _session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    WorkflowBase.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()


def _seed_change(db):
    project = Project(slug="crypto", name="Crypto")
    db.add(project)
    db.flush()

    change = Change(
        project_id=project.id, change_id="centralize-workflow-state-db", title="Workflow DB"
    )
    db.add(change)
    db.flush()
    return change


def _story(db, change, title: str, state: WorkItemState = WorkItemState.queued):
    item = WorkItem(change_pk=change.id, type=WorkItemType.story, title=title, state=state)
    db.add(item)
    db.flush()
    return item


def _bug(db, change, parent, title: str, state: WorkItemState = WorkItemState.queued):
    item = WorkItem(
        change_pk=change.id, type=WorkItemType.bug, parent_id=parent.id, title=title, state=state
    )
    db.add(item)
    db.flush()
    return item


def test_assign_story_enforces_change_wip_limit_of_two_active_stories():
    db = _session()
    change = _seed_change(db)
    story1 = _story(db, change, "Story 1")
    story2 = _story(db, change, "Story 2")
    story3 = _story(db, change, "Story 3")

    run1 = create_agent_run(db, agent="dev", change_pk=change.id, label="run-1")
    run2 = create_agent_run(db, agent="dev", change_pk=change.id, label="run-2")
    run3 = create_agent_run(db, agent="dev", change_pk=change.id, label="run-3")

    assign_story_to_run(db, work_item_id=story1.id, run_id=run1.id)
    assign_story_to_run(db, work_item_id=story2.id, run_id=run2.id)

    try:
        assign_story_to_run(db, work_item_id=story3.id, run_id=run3.id)
        assert False, "expected WIP rule violation"
    except WorkflowRuleViolation as exc:
        assert "WIP limit" in str(exc)


def test_assign_story_enforces_one_active_story_per_agent_run():
    db = _session()
    change = _seed_change(db)
    story1 = _story(db, change, "Story 1")
    story2 = _story(db, change, "Story 2")
    run = create_agent_run(db, agent="dev", change_pk=change.id, label="shared-run")

    assign_story_to_run(db, work_item_id=story1.id, run_id=run.id)

    try:
        assign_story_to_run(db, work_item_id=story2.id, run_id=run.id)
        assert False, "expected agent-run ownership violation"
    except WorkflowRuleViolation as exc:
        assert "already owns another active story" in str(exc)


def test_assign_story_rejects_open_dependencies_until_predecessor_done():
    db = _session()
    change = _seed_change(db)
    predecessor = _story(db, change, "Predecessor", state=WorkItemState.active)
    successor = _story(db, change, "Successor")
    add_dependency(db, work_item_id=successor.id, depends_on_id=predecessor.id)
    run = create_agent_run(db, agent="dev", change_pk=change.id, label="run-1")

    try:
        assign_story_to_run(db, work_item_id=successor.id, run_id=run.id)
        assert False, "expected dependency violation"
    except WorkflowRuleViolation as exc:
        assert "dependency predecessors" in str(exc)

    predecessor.state = WorkItemState.done
    assign_story_to_run(db, work_item_id=successor.id, run_id=run.id)
    assert successor.state == WorkItemState.active
    assert successor.owner_run_id == run.id


def test_add_dependency_rejects_cross_change_links():
    db = _session()
    change1 = _seed_change(db)
    change2 = Change(project_id=change1.project_id, change_id="other-change", title="Other")
    db.add(change2)
    db.flush()

    story1 = _story(db, change1, "Story 1")
    story2 = _story(db, change2, "Story 2")

    try:
        add_dependency(db, work_item_id=story1.id, depends_on_id=story2.id)
        assert False, "expected cross-change dependency violation"
    except WorkflowRuleViolation as exc:
        assert "same change" in str(exc)


def test_story_lock_is_exclusive_and_bug_completion_blocks_story_done():
    db = _session()
    change = _seed_change(db)
    story = _story(db, change, "Story")
    bug = _bug(db, change, story, "Bug", state=WorkItemState.active)
    run1 = create_agent_run(db, agent="dev", change_pk=change.id, label="run-1")
    run2 = create_agent_run(db, agent="dev", change_pk=change.id, label="run-2")

    result = assign_story_to_run(db, work_item_id=story.id, run_id=run1.id)
    assert result.lock.is_active is True
    assert result.lock.owner_run_id == run1.id

    try:
        assign_story_to_run(db, work_item_id=story.id, run_id=run2.id)
        assert False, "expected exclusive lock violation"
    except WorkflowRuleViolation as exc:
        assert "active lock" in str(exc)

    try:
        release_story_assignment(db, work_item_id=story.id, final_state=WorkItemState.done)
        assert False, "expected child bug blocking violation"
    except WorkflowRuleViolation as exc:
        assert "child bugs remain open" in str(exc)

    bug.state = WorkItemState.done
    release_story_assignment(db, work_item_id=story.id, final_state=WorkItemState.done)
    assert story.state == WorkItemState.done
    assert story.owner_run_id is None
    assert story.lock.is_active is False
    assert story.lock.released_at is not None
