from __future__ import annotations

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.services import workflow_validation_service as wvs
from app.workflow_database import WorkflowBase
from app.workflow_models import Change, Project, WorkItem, WorkItemState, WorkItemType


@pytest.fixture
def workflow_session(tmp_path):
    engine = create_engine("postgresql://postgres:postgres@127.0.0.1:5432/postgres")
    WorkflowBase.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


def _seed_change(db, change_id: str = "coverage-ratchet"):
    project = Project(
        slug="crypto",
        name="Crypto",
    )
    db.add(project)
    db.flush()
    change = Change(change_id=change_id, project_id=project.id, title="Change", status="DEV")
    db.add(change)
    db.flush()
    return change


def test_validation_gate_and_story_closure_paths(monkeypatch, workflow_session, tmp_path):
    change_dir = tmp_path / "openspec" / "changes" / "coverage-ratchet"
    change_dir.mkdir(parents=True)
    (change_dir / "tasks.md").write_text("- [x] 1.1 Do something\n", encoding="utf-8")

    monkeypatch.setattr(wvs, "REPO_ROOT", tmp_path)

    status = wvs.validate_approval_gate("coverage-ratchet")
    assert status.is_valid is False
    assert "proposal.md" in status.missing_files
    assert "review-ptbr.md" in status.missing_files
    assert status.has_tasks is True

    change = _seed_change(workflow_session, change_id="coverage-ratchet")
    story = WorkItem(
        change_pk=change.id,
        type=WorkItemType.story,
        title="Story",
        state=WorkItemState.active,
    )
    workflow_session.add(story)
    workflow_session.flush()
    bug_block = WorkItem(
        change_pk=change.id,
        parent_id=story.id,
        type=WorkItemType.bug,
        state=WorkItemState.active,
        title="Open bug",
    )
    bug_done = WorkItem(
        change_pk=change.id,
        parent_id=story.id,
        type=WorkItemType.bug,
        state=WorkItemState.done,
        title="Done bug",
    )
    workflow_session.add_all([bug_block, bug_done])
    workflow_session.flush()

    closure = wvs.validate_story_closure(workflow_session, str(story.id))
    assert closure.is_valid is False
    assert len(closure.blocking_bugs) == 1

    bug_block.state = WorkItemState.done
    bug_block_done = wvs.validate_story_closure(workflow_session, str(story.id))
    assert bug_block_done.is_valid is True

    with pytest.raises(HTTPException):
        wvs.validate_story_closure(workflow_session, "missing")

    not_story = WorkItem(
        change_pk=change.id,
        type=WorkItemType.bug,
        state=WorkItemState.active,
        title="Bug",
    )
    workflow_session.add(not_story)
    workflow_session.flush()
    with pytest.raises(HTTPException):
        wvs.validate_story_closure(workflow_session, str(not_story.id))


def test_validation_handoff_and_sync_comparison(monkeypatch, workflow_session, tmp_path):
    monkeypatch.setattr(wvs, "REPO_ROOT", tmp_path)

    valid = wvs.validate_handoff_comment(
        "Status: done\nEvidence: link https://example\nNext step: DEV\n"
    )
    assert valid.is_valid is True
    assert valid.missing_fields == []

    invalid = wvs.validate_handoff_comment("just some text")
    assert invalid.is_valid is False
    assert set(invalid.missing_fields) == {"status", "evidence", "next_step"}

    change = _seed_change(workflow_session, change_id="sync-change")
    story = WorkItem(
        change_pk=change.id, type=WorkItemType.story, title="One", state=WorkItemState.active
    )
    db_item = WorkItem(
        change_pk=change.id,
        type=WorkItemType.bug,
        title="1.1 Do task",
        state=WorkItemState.done,
    )
    workflow_session.add_all([story, db_item])
    workflow_session.commit()

    meta_dir = tmp_path / "openspec" / "changes" / "sync-change"
    meta_dir.mkdir(parents=True, exist_ok=True)
    (meta_dir / "meta.yaml").write_text("status: PO\n", encoding="utf-8")
    (meta_dir / "tasks.md").write_text("- [ ] 1.1 Do task\n- [x] 2.0 Another\n", encoding="utf-8")

    sync = wvs.verify_sync("sync-change", workflow_session)
    assert sync.is_synced is False
    assert sync.db_status == "DEV"
    assert sync.file_status == "PO"
    assert any(item.type == "status" for item in sync.discrepancies)
    assert any(item.type == "work_item" for item in sync.discrepancies)

    change.status = "PO"
    workflow_session.commit()
    sync2 = wvs.verify_sync("sync-change", workflow_session)
    assert sync2.is_synced is False
    assert any(item.type == "work_item" for item in sync2.discrepancies)
    assert any(item.location == "db" for item in sync2.discrepancies)
