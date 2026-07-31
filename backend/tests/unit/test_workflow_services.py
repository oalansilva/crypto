from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.services.stage_gate_service import validate_stage_transition
from app.services.workflow_auth import WorkflowActor
from app.services import workflow_reconcile_service, workflow_transition_service
from app.services.upstream_guard import MainPublicationEvidence
from app.services.workflow_reconcile_service import reconcile_change_forward
from app.services.workflow_transition_service import (
    KANBAN_COLUMNS,
    LEGACY_STATUS_ALIASES,
    approval_matches_current_evidence,
    canonicalize_status,
    transition_change,
    validate_kanban_transition,
    validate_work_item_transition,
)
from app.workflow_database import (
    WorkflowBase,
    init_workflow_schema_for_url,
    migrate_legacy_workflow_statuses,
)
from app.workflow_models import (
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
    url = "postgresql://postgres:postgres@127.0.0.1:5432/postgres"
    init_workflow_schema_for_url(url)
    engine = create_engine(url)
    WorkflowBase.metadata.create_all(bind=engine)
    connection = engine.connect()
    transaction = connection.begin()
    db = Session(bind=connection, autoflush=False)
    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()
        engine.dispose()


def _make_change(db: Session, *, status: str = "Todo", change_id: str | None = None) -> Change:
    project = Project(slug=f"crypto-{uuid4().hex[:8]}", name="Crypto")
    db.add(project)
    db.flush()
    change = Change(
        project_id=project.id,
        change_id=change_id or f"change-{uuid4().hex[:8]}",
        title="Workflow",
        status=status,
    )
    db.add(change)
    db.flush()
    return change


def _write_design_delivery(root: Path, change: Change) -> None:
    design = root / "openspec" / "changes" / change.change_id / "design.md"
    design.parent.mkdir(parents=True)
    design.write_text(
        "# Design\n\n## Prototype\nVersioned HTML\n\n## Design Critique\nPASS\n",
        encoding="utf-8",
    )
    prototype = root / "frontend" / "public" / "prototypes" / change.change_id / "index.html"
    prototype.parent.mkdir(parents=True)
    prototype.write_text("<main>prototype v1</main>", encoding="utf-8")
    change.ui_impact = "affected"
    change.design_ref = str(design.relative_to(root))
    change.prototype_ref = str(prototype.relative_to(root))
    change.design_critique_verdict = "PASS"


def test_canonical_statuses_aliases_and_unknown_rejection():
    assert KANBAN_COLUMNS == [
        "Todo",
        "Design",
        "Aprovação de Design",
        "Pronto para Dev",
        "Em desenvolvimento",
        "Code Review",
        "QA",
        "Done",
        "Homologado",
        "Pronto",
        "Cancelado",
    ]
    assert canonicalize_status("Todo") == "Todo"
    for legacy, canonical in LEGACY_STATUS_ALIASES.items():
        assert canonicalize_status(legacy, allow_legacy=True) == canonical
    with pytest.raises(HTTPException) as exc:
        canonicalize_status("mystery")
    assert exc.value.status_code == 422
    assert exc.value.detail["code"] == "unknown_workflow_status"


def test_legacy_status_migration_is_idempotent_and_rejects_unknown():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE wf_changes ("
                "id TEXT PRIMARY KEY, status TEXT NOT NULL, "
                "ui_impact TEXT NOT NULL DEFAULT 'unknown', "
                "ui_impact_justification TEXT NOT NULL DEFAULT '')"
            )
        )
        conn.execute(
            text(
                "INSERT INTO wf_changes (id, status) VALUES ('1', 'Pending'), ('2', 'DEV'), ('3', 'Archived')"
            )
        )
        migrate_legacy_workflow_statuses(conn)
        migrate_legacy_workflow_statuses(conn)
        rows = {
            str(row[0]): str(row[1])
            for row in conn.execute(text("SELECT id, status FROM wf_changes"))
        }
        assert rows == {"1": "Todo", "2": "Em desenvolvimento", "3": "Homologado"}
        legacy_ui = conn.execute(
            text("SELECT ui_impact, ui_impact_justification FROM wf_changes WHERE id = '2'")
        ).one()
        assert legacy_ui[0] == "none"
        assert "Grandfathered" in legacy_ui[1]
        conn.execute(text("INSERT INTO wf_changes (id, status) VALUES ('4', 'Mystery')"))
        with pytest.raises(RuntimeError, match="Mystery"):
            migrate_legacy_workflow_statuses(conn)
    engine.dispose()


def test_canonical_transition_matrix_rework_and_terminals():
    for current, target in zip(KANBAN_COLUMNS[:9], KANBAN_COLUMNS[1:10]):
        assert validate_kanban_transition(current_column=current, target_column=target) == (
            current,
            target,
        )

    for current, target in [
        ("Aprovação de Design", "Design"),
        ("Code Review", "Em desenvolvimento"),
        ("QA", "Em desenvolvimento"),
    ]:
        assert validate_kanban_transition(current_column=current, target_column=target) == (
            current,
            target,
        )

    with pytest.raises(HTTPException):
        validate_kanban_transition(current_column="Todo", target_column="QA")
    with pytest.raises(HTTPException):
        validate_kanban_transition(current_column="Done", target_column="QA")
    with pytest.raises(HTTPException):
        validate_kanban_transition(current_column="Pronto", target_column="Homologado")
    with pytest.raises(HTTPException):
        validate_kanban_transition(current_column="Cancelado", target_column="Todo")

    assert validate_stage_transition("Todo", "Design").allowed is True
    assert validate_stage_transition("Todo", "QA").allowed is False


def test_non_ui_bypass_requires_justification(workflow_session, tmp_path):
    change = _make_change(workflow_session)
    actor = WorkflowActor(user_id=str(uuid4()), email="dev@example.com")
    with pytest.raises(HTTPException) as exc:
        transition_change(
            workflow_session,
            change=change,
            target_status="Pronto para Dev",
            actor=actor,
            repo_root=tmp_path,
            design_approver_emails={"alan@example.com"},
        )
    assert exc.value.detail["code"] == "ui_bypass_requires_justification"

    change.ui_impact = "none"
    change.ui_impact_justification = "Backend-only database migration."
    transition_change(
        workflow_session,
        change=change,
        target_status="Pronto para Dev",
        actor=actor,
        repo_root=tmp_path,
        design_approver_emails={"alan@example.com"},
    )
    assert change.status == "Pronto para Dev"


def test_design_delivery_approval_is_server_actor_and_digest_bound(workflow_session, tmp_path):
    change = _make_change(workflow_session, status="Design")
    _write_design_delivery(tmp_path, change)
    agent = WorkflowActor(user_id=str(uuid4()), email="agent@example.com")
    alan = WorkflowActor(user_id=str(uuid4()), email="alan@example.com")

    transition_change(
        workflow_session,
        change=change,
        target_status="Aprovação de Design",
        actor=agent,
        repo_root=tmp_path,
        design_approver_emails={alan.email},
    )
    assert change.design_digest
    assert change.prototype_digest
    delivered_at = change.design_delivered_at
    assert delivered_at is not None

    with pytest.raises(HTTPException) as exc:
        transition_change(
            workflow_session,
            change=change,
            target_status="Pronto para Dev",
            actor=agent,
            repo_root=tmp_path,
            design_approver_emails={alan.email},
        )
    assert exc.value.status_code == 403
    assert change.status == "Aprovação de Design"

    result = transition_change(
        workflow_session,
        change=change,
        target_status="Pronto para Dev",
        actor=alan,
        repo_root=tmp_path,
        design_approver_emails={alan.email},
    )
    workflow_session.flush()
    assert result.approval_created is True
    assert change.design_approved_by == alan.email
    assert change.design_approved_by_user_id == alan.user_id
    assert change.design_approval_valid is True
    assert change.design_delivered_at == delivered_at
    assert change.approved_design_digest == change.design_digest
    assert change.approved_prototype_digest == change.prototype_digest
    approval = (
        workflow_session.query(WorkflowApproval)
        .filter(WorkflowApproval.change_pk == change.id)
        .one()
    )
    assert approval.actor == alan.email
    assert approval.state == ApprovalState.approved


def test_changed_evidence_invalidates_approval_and_blocks_development(
    workflow_session, tmp_path, monkeypatch
):
    change = _make_change(workflow_session, status="Design")
    _write_design_delivery(tmp_path, change)
    alan = WorkflowActor(user_id=str(uuid4()), email="alan@example.com")
    transition_change(
        workflow_session,
        change=change,
        target_status="Aprovação de Design",
        actor=alan,
        repo_root=tmp_path,
        design_approver_emails={alan.email},
    )
    transition_change(
        workflow_session,
        change=change,
        target_status="Pronto para Dev",
        actor=alan,
        repo_root=tmp_path,
        design_approver_emails={alan.email},
    )
    assert approval_matches_current_evidence(change, tmp_path) is True

    prototype = tmp_path / change.prototype_ref
    prototype.write_text("<main>prototype v2</main>", encoding="utf-8")
    with pytest.raises(HTTPException) as exc:
        transition_change(
            workflow_session,
            change=change,
            target_status="Em desenvolvimento",
            actor=alan,
            repo_root=tmp_path,
            design_approver_emails={alan.email},
        )
    assert exc.value.detail["code"] == "design_approval_obsolete"
    assert change.design_approval_valid is False
    assert change.status == "Aprovação de Design"

    # Reconciliation never approves or advances; it only returns stale evidence
    # to the human approval gate.
    change.status = "Pronto para Dev"
    change.design_approval_valid = True
    monkeypatch.setattr(workflow_reconcile_service, "project_root", lambda: tmp_path)
    assert reconcile_change_forward(workflow_session, change=change) is True
    assert change.status == "Aprovação de Design"


def test_story_completion_still_blocks_open_child_bugs(workflow_session):
    change = _make_change(workflow_session, status="Em desenvolvimento")
    story = WorkItem(
        change_pk=change.id,
        type=WorkItemType.story,
        state=WorkItemState.active,
        title="Story",
    )
    workflow_session.add(story)
    workflow_session.flush()
    bug = WorkItem(
        change_pk=change.id,
        parent_id=story.id,
        type=WorkItemType.bug,
        state=WorkItemState.active,
        title="Bug",
    )
    workflow_session.add(bug)
    workflow_session.flush()
    with pytest.raises(HTTPException) as exc:
        validate_work_item_transition(workflow_session, story, WorkItemState.done)
    assert exc.value.detail["code"] == "blocking_child_bugs"

    bug.state = WorkItemState.done
    workflow_session.flush()
    validate_work_item_transition(workflow_session, story, WorkItemState.done)


def test_done_and_homologado_do_not_revalidate_or_regress_design_evidence(
    workflow_session, tmp_path, monkeypatch
):
    alan = WorkflowActor(user_id=str(uuid4()), email="alan@example.com")
    change = _make_change(workflow_session, status="Done", change_id="card-340-archived-design")
    change.ui_impact = "affected"
    change.design_approval_valid = True
    change.design_ref = "openspec/changes/archive/moved-design.md"
    change.prototype_ref = "frontend/public/prototypes/removed/index.html"

    assert reconcile_change_forward(workflow_session, change=change) is False
    assert change.status == "Done"
    assert change.design_approval_valid is True
    transition_change(
        workflow_session,
        change=change,
        target_status="Homologado",
        actor=alan,
        repo_root=tmp_path,
        design_approver_emails={alan.email},
        homologation_approver_emails={alan.email},
    )
    assert change.status == "Homologado"
    assert change.design_approval_valid is True

    monkeypatch.setattr(
        workflow_transition_service,
        "require_card_main_publication",
        lambda _root, **_kwargs: MainPublicationEvidence(
            head_sha="c" * 40,
            main_sha="d" * 40,
            main_ref="origin/main",
        ),
    )
    transition_change(
        workflow_session,
        change=change,
        target_status="Pronto",
        actor=alan,
        repo_root=tmp_path,
        design_approver_emails={alan.email},
        release_approver_emails={alan.email},
    )
    assert change.status == "Pronto"
    assert change.publication_commit_sha == "c" * 40
