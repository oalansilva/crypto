from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.services import stage_gate_service, workflow_reconcile_service, workflow_transition_service
from app.services.stage_gate_service import (
    can_transition_to_stage,
    record_stage_completion,
    record_stage_start,
    require_handoff_fields,
    validate_stage_transition,
)
from app.services.workflow_reconcile_service import (
    infer_gates_from_artifacts,
    reconcile_change_forward,
)
from app.services.workflow_transition_service import (
    desired_gate_states_for_column,
    sync_change_gates_for_column,
    validate_kanban_transition,
    validate_transition_hooks,
    validate_work_item_transition,
)
from app.workflow_database import WorkflowBase
from app.workflow_models import (
    ApprovalScope,
    ApprovalState,
    Change,
    Project,
    WorkItem,
    WorkItemState,
    WorkItemType,
    WorkflowApproval,
)


@pytest.fixture
def workflow_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    WorkflowBase.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


def _make_change_with_story(db, *, status: str = "Approval") -> tuple[Project, Change, WorkItem]:
    project = Project(slug="crypto", name="Crypto")
    db.add(project)
    db.flush()

    change = Change(
        project_id=project.id, change_id="coverage-ratchet", title="Coverage", status=status
    )
    db.add(change)
    db.flush()

    story = WorkItem(
        change_pk=change.id,
        type=WorkItemType.story,
        state=WorkItemState.active,
        title="Improve coverage",
    )
    db.add(story)
    db.commit()
    db.refresh(project)
    db.refresh(change)
    db.refresh(story)
    return project, change, story


def test_stage_gate_validate_transition_and_handoff_fields():
    same = validate_stage_transition("PO", "PO")
    skipped = validate_stage_transition("PO", "Approval")
    backward = validate_stage_transition("DEV", "PO")
    archived = validate_stage_transition("QA", "Archived")
    canceled = validate_stage_transition("PO", "Canceled")
    normalized = validate_stage_transition("Alan homologation", "Archived")
    pending = validate_stage_transition(None, "PO")
    invalid = validate_stage_transition("mystery", "PO")
    backward_terminal = validate_stage_transition("Canceled", "Archived")

    assert same.allowed is True
    assert skipped.allowed is False and skipped.skipped_stage == "DESIGN"
    assert backward.allowed is False and "Backward transitions" in (backward.message or "")
    assert archived.allowed is True
    assert canceled.allowed is True
    assert normalized.current_stage == "Homologation"
    assert pending.current_stage == "Pending"
    assert invalid.current_stage == "Pending"
    assert backward_terminal.allowed is True

    with pytest.raises(HTTPException) as exc:
        require_handoff_fields({"status": "done", "evidence": ""})
    assert exc.value.detail["code"] == "missing_handoff_fields"

    assert (
        require_handoff_fields({"status": "done", "evidence": "link", "next_step": "QA"})[
            "next_step"
        ]
        == "QA"
    )


def test_stage_gate_can_transition_and_record_stage_timestamps(workflow_session):
    _project, change, story = _make_change_with_story(workflow_session, status="Approval")

    wrong_agent = can_transition_to_stage(workflow_session, story.id, "DEV", agent="PO")
    missing_work_item = can_transition_to_stage(workflow_session, "missing", "DEV", agent="DEV")
    orphan_story = WorkItem(
        change_pk="missing-change",
        type=WorkItemType.story,
        state=WorkItemState.active,
        title="Orphan",
    )
    workflow_session.add(orphan_story)
    workflow_session.commit()
    missing_change = can_transition_to_stage(workflow_session, orphan_story.id, "DEV", agent="DEV")
    skipped_stage = can_transition_to_stage(workflow_session, story.id, "Homologation", agent="DEV")
    allowed_stage = can_transition_to_stage(workflow_session, story.id, "DEV", agent="DEV")

    assert wrong_agent.allowed is False
    assert "requires agent 'DEV'" in (wrong_agent.message or "")
    assert missing_work_item.allowed is False
    assert missing_change.allowed is False
    assert skipped_stage.allowed is False and skipped_stage.skipped_stage == "DEV"
    assert allowed_stage.allowed is True and allowed_stage.target_stage == "DEV"

    started = record_stage_start(workflow_session, story.id, "DEV")
    completed = record_stage_completion(workflow_session, story.id, "DEV")

    assert started.stage_started_at is not None
    assert completed.stage_completed_at is not None
    assert completed.last_agent_acted == "DEV"
    assert change.status == "Approval"

    with pytest.raises(HTTPException) as start_exc:
        record_stage_start(workflow_session, "missing", "DEV")
    with pytest.raises(HTTPException) as complete_exc:
        record_stage_completion(workflow_session, "missing", "DEV")
    assert start_exc.value.status_code == 404
    assert complete_exc.value.status_code == 404


def test_workflow_transition_desired_states_sync_and_validation_hooks(
    workflow_session, monkeypatch
):
    _project, change, story = _make_change_with_story(workflow_session, status="PO")

    states = desired_gate_states_for_column("QA")
    assert [decision.gate for decision in states] == [
        "PO",
        "DESIGN",
        "Approval",
        "DEV",
        "QA",
        "Homologation",
    ]
    assert [decision.state for decision in states[:4]] == [ApprovalState.approved] * 4
    assert states[-1].state == ApprovalState.pending
    assert desired_gate_states_for_column("Pending")[0].state == ApprovalState.pending
    assert desired_gate_states_for_column("Approval")[1].state == ApprovalState.approved
    assert desired_gate_states_for_column("DEV")[2].state == ApprovalState.approved
    assert desired_gate_states_for_column("Alan homologation")[4].state == ApprovalState.approved
    assert desired_gate_states_for_column("Archived")[-1].state == ApprovalState.approved
    assert desired_gate_states_for_column("canceled")[-1].state == ApprovalState.approved
    assert desired_gate_states_for_column("unexpected")[2].state == ApprovalState.approved

    current, target = validate_kanban_transition(current_column="PO", target_column="DESIGN")
    assert (current, target) == ("PO", "DESIGN")
    assert validate_kanban_transition(current_column="DEV", target_column="DEV") == ("DEV", "DEV")

    with pytest.raises(HTTPException) as transition_exc:
        validate_kanban_transition(current_column="PO", target_column="QA")
    assert transition_exc.value.detail["code"] == "invalid_kanban_transition"
    with pytest.raises(HTTPException) as archived_exc:
        validate_kanban_transition(current_column="Archived", target_column="PO")
    assert archived_exc.value.detail["code"] == "invalid_kanban_transition"

    mutated = sync_change_gates_for_column(workflow_session, change=change, target_column="DESIGN")
    workflow_session.commit()

    approvals = (
        workflow_session.query(WorkflowApproval)
        .filter(WorkflowApproval.change_pk == change.id)
        .all()
    )
    latest_states = {approval.gate: approval.state for approval in approvals}

    assert mutated is True
    assert change.status == "DESIGN"
    assert latest_states["PO"] == ApprovalState.approved
    assert latest_states["DESIGN"] == ApprovalState.pending

    monkeypatch.setattr(
        workflow_transition_service,
        "_validate_dev_to_qa",
        lambda db, change: setattr(change, "_validated_dev_to_qa", True),
    )
    monkeypatch.setattr(
        workflow_transition_service,
        "_validate_qa_to_homologation",
        lambda db, change: setattr(change, "_validated_qa_to_homologation", True),
    )
    monkeypatch.setattr(
        workflow_transition_service,
        "_validate_homologation_to_archived",
        lambda db, change: setattr(change, "_validated_homologation_to_archived", True),
    )

    validate_transition_hooks(workflow_session, change, "QA")
    validate_transition_hooks(workflow_session, change, "Homologation")
    validate_transition_hooks(workflow_session, change, "Archived")

    assert getattr(change, "_validated_dev_to_qa") is True
    assert getattr(change, "_validated_qa_to_homologation") is True
    assert getattr(change, "_validated_homologation_to_archived") is True

    monkeypatch.setitem(
        __import__("sys").modules,
        "app.services.workflow_validation_service",
        SimpleNamespace(
            validate_story_closure=lambda db, story_id: SimpleNamespace(
                is_valid=False, blocking_bugs=["bug-1"]
            ),
            validate_approval_gate=lambda _change_id: SimpleNamespace(
                is_valid=True, missing_files=[]
            ),
        ),
    )

    with pytest.raises(HTTPException) as story_exc:
        validate_work_item_transition(workflow_session, story, WorkItemState.done)
    assert story_exc.value.detail["code"] == "blocking_child_bugs"

    bug = WorkItem(
        change_pk=change.id,
        type=WorkItemType.bug,
        state=WorkItemState.active,
        title="Bug item",
    )
    workflow_session.add(bug)
    workflow_session.commit()
    validate_work_item_transition(workflow_session, bug, WorkItemState.done)


def test_workflow_transition_validation_errors_for_qa_and_homologation(
    workflow_session, monkeypatch
):
    _project, change, story = _make_change_with_story(workflow_session, status="DEV")

    monkeypatch.setitem(
        __import__("sys").modules,
        "app.services.workflow_validation_service",
        SimpleNamespace(
            validate_approval_gate=lambda _change_id: SimpleNamespace(
                is_valid=False, missing_files=["proposal.md", "review-ptbr.md"]
            ),
            validate_story_closure=lambda db, story_id: SimpleNamespace(
                is_valid=True, blocking_bugs=[]
            ),
        ),
    )

    with pytest.raises(HTTPException) as qa_exc:
        validate_transition_hooks(workflow_session, change, "QA")
    assert qa_exc.value.detail["code"] == "approval_gate_not_met"

    change.status = "QA"
    workflow_session.commit()
    story.state = WorkItemState.active
    workflow_session.commit()
    with pytest.raises(HTTPException) as homologation_exc:
        validate_transition_hooks(workflow_session, change, "Homologation")
    assert homologation_exc.value.detail["code"] == "open_work_items"

    story.state = WorkItemState.done
    workflow_session.commit()
    validate_transition_hooks(workflow_session, change, "Homologation")
    validate_transition_hooks(workflow_session, change, "Archived")


def test_workflow_transition_sync_can_still_fill_missing_gate_history(workflow_session):
    _project, change, _story = _make_change_with_story(workflow_session, status="DEV")
    workflow_session.add(
        WorkflowApproval(
            scope=ApprovalScope.change,
            gate="PO",
            state=ApprovalState.approved,
            change_pk=change.id,
            actor="kanban",
            note="existing",
        )
    )
    workflow_session.add(
        WorkflowApproval(
            scope=ApprovalScope.change,
            gate="DESIGN",
            state=ApprovalState.approved,
            change_pk=change.id,
            actor="kanban",
            note="existing",
        )
    )
    workflow_session.add(
        WorkflowApproval(
            scope=ApprovalScope.change,
            gate="Approval",
            state=ApprovalState.approved,
            change_pk=change.id,
            actor="kanban",
            note="existing",
        )
    )
    for gate in ["DEV", "QA", "Homologation"]:
        workflow_session.add(
            WorkflowApproval(
                scope=ApprovalScope.change,
                gate=gate,
                state=ApprovalState.pending,
                change_pk=change.id,
                actor="kanban",
                note="existing",
            )
        )
    workflow_session.commit()

    mutated = sync_change_gates_for_column(workflow_session, change=change, target_column="DEV")
    approvals = (
        workflow_session.query(WorkflowApproval)
        .filter(WorkflowApproval.change_pk == change.id)
        .all()
    )
    assert change.status == "DEV"
    assert len(approvals) >= 6
    assert {approval.gate for approval in approvals}.issuperset(
        {"PO", "DESIGN", "Approval", "DEV", "QA", "Homologation"}
    )


def test_workflow_reconcile_infers_artifacts_and_advances_change(
    tmp_path, workflow_session, monkeypatch
):
    _project, change, _story = _make_change_with_story(workflow_session, status="PO")
    change.change_id = "coverage-ratchet"
    workflow_session.commit()

    base = tmp_path / "openspec" / "changes" / change.change_id
    (base / "specs").mkdir(parents=True)
    (base / "proposal.md").write_text("proposal", encoding="utf-8")
    (base / "tasks.md").write_text("tasks", encoding="utf-8")
    (base / "specs" / "delta.md").write_text("spec", encoding="utf-8")
    (base / "design.md").write_text("design", encoding="utf-8")
    (tmp_path / "frontend" / "public" / "prototypes" / change.change_id).mkdir(parents=True)

    monkeypatch.setattr(workflow_reconcile_service, "project_root", lambda: tmp_path)

    inferred = infer_gates_from_artifacts(change.change_id)
    mutated = reconcile_change_forward(workflow_session, change=change)

    approvals = (
        workflow_session.query(WorkflowApproval)
        .filter(WorkflowApproval.change_pk == change.id)
        .all()
    )
    latest_states = {approval.gate: approval.state for approval in approvals}

    assert inferred.po_done is True
    assert inferred.design_done is True
    assert mutated is True
    assert change.status == "Approval"
    assert latest_states["PO"] == ApprovalState.approved
    assert latest_states["DESIGN"] == ApprovalState.approved


def test_workflow_reconcile_does_not_touch_pending_or_canceled_changes(
    tmp_path, workflow_session, monkeypatch
):
    _project, change, _story = _make_change_with_story(workflow_session, status="Pending")
    change.change_id = "pending-change"
    workflow_session.commit()

    base = tmp_path / "openspec" / "changes" / change.change_id
    (base / "specs").mkdir(parents=True)
    (base / "proposal.md").write_text("proposal", encoding="utf-8")
    (base / "tasks.md").write_text("tasks", encoding="utf-8")
    (base / "specs" / "delta.md").write_text("spec", encoding="utf-8")
    monkeypatch.setattr(workflow_reconcile_service, "project_root", lambda: tmp_path)

    assert reconcile_change_forward(workflow_session, change=change) is False

    change.status = "Canceled"
    workflow_session.commit()
    assert reconcile_change_forward(workflow_session, change=change) is False


def test_workflow_reconcile_can_advance_from_homologation_to_archived(workflow_session):
    _project, change, _story = _make_change_with_story(workflow_session, status="Alan homologation")
    for gate in ["PO", "DESIGN", "Approval", "DEV", "QA", "Homologation"]:
        workflow_session.add(
            WorkflowApproval(
                scope=ApprovalScope.change,
                gate=gate,
                state=ApprovalState.approved,
                change_pk=change.id,
                actor="qa",
                note="approved",
            )
        )
    workflow_session.commit()

    assert reconcile_change_forward(workflow_session, change=change) is True
    assert change.status == "Archived"
