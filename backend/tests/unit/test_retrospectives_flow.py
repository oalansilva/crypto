from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.workflow_database import WorkflowBase
from app.workflow_models import (
    ApprovalScope,
    ApprovalState,
    Change,
    HandoffScope,
    Project,
    WorkItem,
    WorkItemState,
    WorkItemType,
    WorkflowApproval,
    WorkflowHandoff,
)
import app.routes.retrospectives as retrospectives_route
import app.services.retrospective_service as retrospective_service


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


def _seed_change(workflow_session):
    project = Project(slug="crypto", name="Crypto")
    workflow_session.add(project)
    workflow_session.flush()

    started = datetime(2026, 4, 10, 9, 0, 0, tzinfo=timezone.utc)
    updated = datetime(2026, 4, 14, 18, 0, 0, tzinfo=timezone.utc)
    change = Change(
        project_id=project.id,
        change_id="coverage-ratchet",
        title="Coverage Ratchet",
        status="Homologation",
        card_number=22,
        created_at=started,
        updated_at=updated,
    )
    workflow_session.add(change)
    workflow_session.flush()

    story = WorkItem(
        change_pk=change.id,
        type=WorkItemType.story,
        state=WorkItemState.done,
        title="Main story",
        created_at=started,
        updated_at=updated,
    )
    blocked_bug = WorkItem(
        change_pk=change.id,
        type=WorkItemType.bug,
        state=WorkItemState.blocked,
        title="Blocked bug",
        created_at=started + timedelta(hours=3),
        updated_at=updated,
    )
    open_bug = WorkItem(
        change_pk=change.id,
        type=WorkItemType.bug,
        state=WorkItemState.active,
        title="Open bug",
        created_at=started + timedelta(hours=5),
        updated_at=updated,
    )
    workflow_session.add_all([story, blocked_bug, open_bug])

    handoffs = [
        WorkflowHandoff(
            scope=HandoffScope.change,
            change_pk=change.id,
            from_role="Alan",
            to_role="PO",
            summary="Start",
            created_at=started,
        ),
        WorkflowHandoff(
            scope=HandoffScope.change,
            change_pk=change.id,
            from_role="PO",
            to_role="DESIGN",
            summary="Design handoff",
            created_at=started + timedelta(hours=2),
        ),
        WorkflowHandoff(
            scope=HandoffScope.change,
            change_pk=change.id,
            from_role="DESIGN",
            to_role="DEV",
            summary="Dev handoff",
            created_at=started + timedelta(days=1),
        ),
        WorkflowHandoff(
            scope=HandoffScope.change,
            change_pk=change.id,
            from_role="DEV",
            to_role="QA",
            summary="QA handoff",
            created_at=started + timedelta(days=2),
        ),
        WorkflowHandoff(
            scope=HandoffScope.change,
            change_pk=change.id,
            from_role="QA",
            to_role="DEV",
            summary="Rework",
            created_at=started + timedelta(days=2, hours=4),
        ),
        WorkflowHandoff(
            scope=HandoffScope.change,
            change_pk=change.id,
            from_role="DEV",
            to_role="QA",
            summary="QA retry",
            created_at=started + timedelta(days=3),
        ),
    ]
    approvals = [
        WorkflowApproval(
            scope=ApprovalScope.change,
            change_pk=change.id,
            gate="PO",
            state=ApprovalState.approved,
            actor="po",
            note="ok",
            created_at=started + timedelta(hours=1),
        ),
        WorkflowApproval(
            scope=ApprovalScope.change,
            change_pk=change.id,
            gate="Approval",
            state=ApprovalState.approved,
            actor="alan",
            note="approved",
            created_at=started + timedelta(days=1, hours=1),
        ),
        WorkflowApproval(
            scope=ApprovalScope.change,
            change_pk=change.id,
            gate="Approval",
            state=ApprovalState.approved,
            actor="alan",
            note="re-approved",
            created_at=started + timedelta(days=1, hours=2),
        ),
        WorkflowApproval(
            scope=ApprovalScope.change,
            change_pk=change.id,
            gate="QA",
            state=ApprovalState.approved,
            actor="qa",
            note="done",
            created_at=started + timedelta(days=3, hours=1),
        ),
    ]
    workflow_session.add_all(handoffs + approvals)
    workflow_session.commit()
    return project, change


def test_retrospective_service_collect_classify_render_and_persist(
    monkeypatch, tmp_path, workflow_session
):
    class FrozenDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return cls(2026, 4, 18, 12, 0, 0, tzinfo=timezone.utc)

    monkeypatch.setattr(retrospective_service, "datetime", FrozenDateTime)
    monkeypatch.setattr(retrospective_service, "RETRO_DIR", tmp_path)

    (tmp_path / "2026-04-01-old-feature.md").write_text(
        "# Old\n🟡\n**Card:** #12\n",
        encoding="utf-8",
    )
    (tmp_path / "2026-04-02-risky-feature.md").write_text(
        "# Old\n🔴\n**Card:** #13\n",
        encoding="utf-8",
    )

    _project, change = _seed_change(workflow_session)
    data = retrospective_service.collect_retrospective_data(workflow_session, change)
    assert data["change_id"] == "coverage-ratchet"
    assert data["card_number"] == 22
    assert data["stage_times"]["PO"]["cycles"] == 1
    assert data["stage_times"]["QA"]["cycles"] == 2
    assert data["gate_cycles"]["Approval"] == 2
    assert len(data["blocker_events"]) == 1
    assert len(data["open_bugs"]) == 2

    problematic = retrospective_service.classify_retrospective(
        {
            "gate_cycles": {"Approval": 1},
            "total_blocker_seconds": 49 * 3600,
            "open_bugs": [],
            "stage_times": {},
        }
    )
    assert problematic == "problemática"
    assert (
        retrospective_service.classify_retrospective(
            {
                "gate_cycles": {"Approval": 4},
                "total_blocker_seconds": 0,
                "open_bugs": [],
                "stage_times": {},
            }
        )
        == "com_ressalvas"
    )
    assert (
        retrospective_service.classify_retrospective(
            {
                "gate_cycles": {"Approval": 1},
                "total_blocker_seconds": 0,
                "open_bugs": [{"id": "bug-1"}, {"id": "bug-2"}, {"id": "bug-3"}],
                "stage_times": {},
            }
        )
        == "problemática"
    )
    assert retrospective_service.classification_badge("sem_problemas") == "🟢 Sem Problemas"
    assert retrospective_service.classification_badge("unknown") == "unknown"
    assert retrospective_service.format_duration(30) == "30s"
    assert retrospective_service.format_duration(90) == "0h 1m"
    assert retrospective_service.format_duration(26 * 3600) == "1d 2h"

    prev_data = {
        "total_seconds": 200000,
        "classification": "sem_problemas",
        "stage_times": {},
        "gate_cycles": {},
        "open_bugs": [],
    }
    insights = retrospective_service._generate_heuristic_insights(data, prev_data)
    assert "Ciclos de revisão por stage" in insights["process_analysis"]
    assert "bug(s) aberto(s)" in insights["actionable_recommendation_for_orchestrator"]

    stage_table = retrospective_service._render_stage_table(data)
    risk_table = retrospective_service._render_risk_table(data, "com_ressalvas")
    blocker_table = retrospective_service._render_blocker_events(data)
    assert "| PO |" in stage_table
    assert "Resultado" in risk_table
    assert "Blocked bug" in blocker_table
    assert (
        retrospective_service._render_blocker_events({"blocker_events": []})
        == "| Nenhum blocker registrado |"
    )

    markdown = retrospective_service.build_retrospective_markdown(data, insights, "com_ressalvas")
    assert "# 📋 Retrospective" in markdown
    assert "Histórico de Retrospectivas" in markdown
    assert "🟡 Com Ressalvas" in markdown

    persisted = retrospective_service.persist_retrospective(markdown, "coverage-ratchet")
    assert persisted.exists()
    assert retrospective_service.retrospective_file_path("coverage-ratchet") == persisted

    listed = retrospective_service.list_retrospectives(page=1, per_page=10)
    assert listed["total"] >= 1
    assert any(item["slug"] == "coverage-ratchet" for item in listed["retrospectives"])
    assert retrospective_service._build_history_lines().count("|") > 3


def test_retrospective_service_llm_and_generation_entrypoint(
    monkeypatch, tmp_path, workflow_session
):
    monkeypatch.setattr(retrospective_service, "RETRO_DIR", tmp_path)
    monkeypatch.setattr(retrospective_service, "REPO_ROOT", tmp_path)

    _project, change = _seed_change(workflow_session)
    data = retrospective_service.collect_retrospective_data(workflow_session, change)

    prompt = retrospective_service._build_llm_prompt(
        data,
        {
            "total_seconds": 1000,
            "classification": "sem_problemas",
            "stage_times": {},
            "gate_cycles": {},
            "open_bugs": [],
        },
    )
    assert "Retrospectiva Anterior" in prompt
    assert "Change ID: coverage-ratchet" in prompt

    monkeypatch.setattr(
        retrospective_service.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=0,
            stdout='{"process_analysis":"ok","improvement_from_previous":"better","regression_from_previous":"none","actionable_recommendation_for_orchestrator":"do this"}',
        ),
    )
    llm = retrospective_service.generate_llm_insights(data)
    assert llm["process_analysis"] == "ok"

    monkeypatch.setattr(
        retrospective_service.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=1, stdout=""),
    )
    fallback = retrospective_service.generate_llm_insights(data)
    assert "process_analysis" in fallback

    def workflow_db_gen():
        yield workflow_session

    monkeypatch.setattr(retrospective_service, "get_workflow_db", workflow_db_gen)
    monkeypatch.setattr(
        retrospective_service,
        "generate_llm_insights",
        lambda current, prev_data=None: {
            "process_analysis": "stable",
            "improvement_from_previous": "faster",
            "regression_from_previous": "none",
            "actionable_recommendation_for_orchestrator": "keep going",
        },
    )
    generated = retrospective_service.generate_retrospective_for_change(
        "crypto", "coverage-ratchet"
    )
    assert generated is not None
    assert generated.exists()
    assert "keep going" in generated.read_text(encoding="utf-8")

    assert (
        retrospective_service.generate_retrospective_for_change("missing", "coverage-ratchet")
        is None
    )
    assert (
        retrospective_service.generate_retrospective_for_change("crypto", "missing-change") is None
    )


@pytest.mark.asyncio
async def test_retrospectives_routes_cover_badges_markdown_html_and_errors(monkeypatch, tmp_path):
    assert "badge-warning" in retrospectives_route._badge_html("com_ressalvas")
    assert "badge-success" in retrospectives_route._badge_html("unknown")

    html = retrospectives_route._markdown_to_html(
        "# Title\n\n**bold**\n\n| Campo | Valor |\n|---|---|\n| A | B |\n\n---\n"
    )
    assert "<h1>Title</h1>" in html
    assert "<strong>bold</strong>" in html
    assert "<table>" in html
    assert "<hr>" in html

    monkeypatch.setattr(
        retrospectives_route,
        "_list_retrospectives",
        lambda page, per_page: {
            "retrospectives": [
                {
                    "slug": "coverage-ratchet",
                    "card_id": 22,
                    "feature_name": "Coverage Ratchet",
                    "date": "2026-04-18",
                    "classification": "com_ressalvas",
                    "filename": "2026-04-18-coverage-ratchet.md",
                }
            ],
            "total": 1,
            "page": page,
            "per_page": per_page,
        },
    )
    listed = retrospectives_route.list_retrospectives(page=1, per_page=10)
    assert listed["total"] == 1

    with pytest.raises(HTTPException) as not_found_exc:
        retrospectives_route.get_retrospective("missing", format="markdown")
    assert not_found_exc.value.status_code == 404

    retro_file = tmp_path / "2026-04-18-coverage-ratchet.md"
    retro_file.write_text(
        "# 📋 Retrospective — Coverage Ratchet\n\n**Card:** #22\n**Data:** 2026-04-18\n\n🟡 Warning\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(retrospectives_route, "retrospective_file_path", lambda slug: retro_file)

    markdown_response = retrospectives_route.get_retrospective(
        "coverage-ratchet", format="markdown"
    )
    assert markdown_response["format"] == "markdown"
    assert "Coverage Ratchet" in markdown_response["content"]

    html_response = retrospectives_route.get_retrospective("coverage-ratchet", format="html")
    assert html_response["format"] == "html"
    assert "Retrospective — Coverage Ratchet" in html_response["content"]
    assert "Voltar ao Histórico" in html_response["content"]
