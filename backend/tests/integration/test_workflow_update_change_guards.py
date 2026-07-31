from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.routes import workflow as workflow_routes
from app.services import workflow_transition_service
from app.services.upstream_guard import MainPublicationEvidence, UpstreamGuardError
from app.services.workflow_auth import WorkflowActor, get_workflow_actor
from app.workflow_database import get_workflow_db, init_workflow_schema_for_url

ALAN = WorkflowActor(
    user_id="44444444-4444-4444-4444-444444444444",
    email="o.alan.silva@gmail.com",
)
AGENT = WorkflowActor(
    user_id="55555555-5555-5555-5555-555555555555",
    email="agent@example.com",
)
QA_SHA = "a" * 40
QA_TOKEN = "trusted-test-qa-token"


@pytest.fixture(autouse=True)
def _trusted_qa_environment(monkeypatch):
    monkeypatch.setenv("WORKFLOW_QA_APPROVAL_TOKEN", QA_TOKEN)
    monkeypatch.setattr(workflow_transition_service, "current_commit_sha", lambda _root: QA_SHA)


def _build_client(actor: WorkflowActor | None = ALAN) -> TestClient:
    url = "postgresql://postgres:postgres@127.0.0.1:5432/postgres"
    init_workflow_schema_for_url(url)
    engine = create_engine(url)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_workflow_db] = override_get_db
    if actor is not None:
        app.dependency_overrides[get_workflow_actor] = lambda: actor
    else:
        app.dependency_overrides.pop(get_workflow_actor, None)
    client = TestClient(app)
    client.engine = engine  # type: ignore[attr-defined]
    return client


def _close_client(client: TestClient) -> None:
    client.close()
    client.app.dependency_overrides.clear()
    client.engine.dispose()  # type: ignore[attr-defined]


def _set_actor(client: TestClient, actor: WorkflowActor) -> None:
    client.app.dependency_overrides[get_workflow_actor] = lambda: actor


def _create_project_and_change(
    client: TestClient,
    *,
    change_id: str,
    status: str = "Todo",
    extra: dict | None = None,
) -> str:
    project_slug = f"crypto-{uuid4().hex[:8]}"
    response = client.post("/api/workflow/projects", json={"slug": project_slug, "name": "Crypto"})
    assert response.status_code == 200
    payload = {"change_id": change_id, "title": change_id, "status": status}
    payload["status"] = "Todo"
    payload.update(extra or {})
    response = client.post(
        f"/api/workflow/projects/{project_slug}/changes",
        json=payload,
    )
    assert response.status_code == 200
    if status != "Todo":
        response = client.patch(
            f"/api/workflow/projects/{project_slug}/changes/{change_id}",
            json={"status": status},
        )
        assert response.status_code == 200
    return project_slug


def _write_design_delivery(root: Path, change_id: str) -> tuple[str, str]:
    design_ref = f"openspec/changes/{change_id}/design.md"
    design = root / design_ref
    design.parent.mkdir(parents=True)
    design.write_text(
        "# Design\n\n## Prototype\nVersioned HTML\n\n## Design Critique\nPASS\n",
        encoding="utf-8",
    )
    prototype_ref = f"frontend/public/prototypes/{change_id}/index.html"
    prototype = root / prototype_ref
    prototype.parent.mkdir(parents=True)
    prototype.write_text("<main>approved prototype</main>", encoding="utf-8")
    return design_ref, prototype_ref


def _advance_non_ui_to(
    client: TestClient,
    *,
    slug: str,
    change_id: str,
    target: str,
) -> None:
    stages = [
        "Pronto para Dev",
        "Em desenvolvimento",
        "Code Review",
        "QA",
        "Done",
        "Homologado",
    ]
    for stage in stages:
        if stage == "Done":
            current = client.get(f"/api/workflow/projects/{slug}/changes/{change_id}").json()
            approval = client.post(
                f"/api/workflow/projects/{slug}/changes/{change_id}/qa-approvals",
                headers={"X-Workflow-QA-Token": QA_TOKEN},
                json={
                    "round_id": current["qa_round_id"],
                    "commit_sha": current["qa_commit_sha"],
                    "evidence": "qa-gate and visual checks green",
                },
            )
            assert approval.status_code == 200
        if stage == "Homologado":
            _set_actor(client, ALAN)
        response = client.patch(
            f"/api/workflow/projects/{slug}/changes/{change_id}",
            json={"status": stage},
        )
        assert response.status_code == 200, response.text
        if stage == target:
            return
    raise AssertionError(f"Unsupported target stage: {target}")


def test_workflow_mutation_requires_authentication():
    client = _build_client(actor=None)
    response = client.post(
        "/api/workflow/projects",
        json={"slug": f"crypto-{uuid4().hex[:8]}", "name": "Crypto"},
    )
    assert response.status_code == 401
    _close_client(client)


def test_new_change_cannot_start_in_advanced_status():
    client = _build_client(actor=AGENT)
    slug = f"crypto-{uuid4().hex[:8]}"
    assert (
        client.post("/api/workflow/projects", json={"slug": slug, "name": "Crypto"}).status_code
        == 200
    )
    rejected = client.post(
        f"/api/workflow/projects/{slug}/changes",
        json={"change_id": "skip-gates", "title": "Skip", "status": "QA"},
    )
    assert rejected.status_code == 409
    assert rejected.json()["detail"]["code"] == "initial_status_must_be_todo"
    assert client.get(f"/api/workflow/projects/{slug}/changes").json() == []
    _close_client(client)


def test_design_delivery_rejects_missing_evidence(monkeypatch, tmp_path):
    monkeypatch.setattr(workflow_routes, "REPO_ROOT", tmp_path)
    client = _build_client(actor=AGENT)
    slug = _create_project_and_change(
        client,
        change_id="missing-evidence",
        status="Design",
        extra={"ui_impact": "affected"},
    )

    response = client.patch(
        f"/api/workflow/projects/{slug}/changes/missing-evidence",
        json={"status": "Aprovação de Design"},
    )
    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["code"] == "incomplete_design_delivery"
    assert "design.md" in detail["missing_items"]
    _close_client(client)


def test_unauthorized_actor_cannot_approve_design(monkeypatch, tmp_path):
    monkeypatch.setattr(workflow_routes, "REPO_ROOT", tmp_path)
    change_id = "unauthorized-design"
    design_ref, prototype_ref = _write_design_delivery(tmp_path, change_id)
    client = _build_client(actor=AGENT)
    slug = _create_project_and_change(
        client,
        change_id=change_id,
        status="Design",
        extra={
            "ui_impact": "affected",
            "design_ref": design_ref,
            "prototype_ref": prototype_ref,
            "design_critique_verdict": "PASS",
        },
    )
    delivered = client.patch(
        f"/api/workflow/projects/{slug}/changes/{change_id}",
        json={"status": "Aprovação de Design"},
    )
    assert delivered.status_code == 200

    rejected = client.patch(
        f"/api/workflow/projects/{slug}/changes/{change_id}",
        json={"status": "Pronto para Dev"},
    )
    assert rejected.status_code == 403
    assert rejected.json()["detail"]["code"] == "design_approver_required"
    current = client.get(f"/api/workflow/projects/{slug}/changes/{change_id}")
    assert current.json()["status"] == "Aprovação de Design"
    assert current.json()["design_approval_valid"] is False
    _close_client(client)


def test_authenticated_approver_is_derived_and_bound_to_evidence(monkeypatch, tmp_path):
    monkeypatch.setattr(workflow_routes, "REPO_ROOT", tmp_path)
    change_id = "approved-design"
    design_ref, prototype_ref = _write_design_delivery(tmp_path, change_id)
    client = _build_client(actor=ALAN)
    slug = _create_project_and_change(
        client,
        change_id=change_id,
        status="Design",
        extra={
            "ui_impact": "affected",
            "design_ref": design_ref,
            "prototype_ref": prototype_ref,
            "design_critique_verdict": "PASS",
        },
    )
    delivered = client.patch(
        f"/api/workflow/projects/{slug}/changes/{change_id}",
        json={"status": "Aprovação de Design"},
    )
    assert delivered.status_code == 200
    delivered_at = delivered.json()["design_delivered_at"]

    approved = client.patch(
        f"/api/workflow/projects/{slug}/changes/{change_id}",
        # Unknown client identity fields cannot grant or replace server identity.
        json={"status": "Pronto para Dev", "actor": "attacker@example.com"},
    )
    assert approved.status_code == 200
    body = approved.json()
    assert body["status"] == "Pronto para Dev"
    assert body["design_approved_by"] == ALAN.email
    assert body["design_approved_by_user_id"] == ALAN.user_id
    assert body["design_approval_valid"] is True
    assert body["approved_design_digest"] == body["design_digest"]
    assert body["approved_prototype_digest"] == body["prototype_digest"]
    assert body["design_delivered_at"] == delivered_at
    approvals = client.get(f"/api/workflow/projects/{slug}/changes/{change_id}/approvals").json()
    assert approvals[-1]["actor"] == ALAN.email
    _close_client(client)


def test_changed_approved_evidence_is_persistently_marked_obsolete(monkeypatch, tmp_path):
    monkeypatch.setattr(workflow_routes, "REPO_ROOT", tmp_path)
    change_id = "obsolete-design"
    design_ref, prototype_ref = _write_design_delivery(tmp_path, change_id)
    client = _build_client(actor=ALAN)
    slug = _create_project_and_change(
        client,
        change_id=change_id,
        status="Design",
        extra={
            "ui_impact": "affected",
            "design_ref": design_ref,
            "prototype_ref": prototype_ref,
            "design_critique_verdict": "PASS",
        },
    )
    assert (
        client.patch(
            f"/api/workflow/projects/{slug}/changes/{change_id}",
            json={"status": "Aprovação de Design"},
        ).status_code
        == 200
    )
    assert (
        client.patch(
            f"/api/workflow/projects/{slug}/changes/{change_id}",
            json={"status": "Pronto para Dev"},
        ).status_code
        == 200
    )

    (tmp_path / prototype_ref).write_text("<main>changed prototype</main>", encoding="utf-8")
    rejected = client.patch(
        f"/api/workflow/projects/{slug}/changes/{change_id}",
        json={"status": "Em desenvolvimento"},
    )
    assert rejected.status_code == 409
    assert rejected.json()["detail"]["code"] == "design_approval_obsolete"

    current = client.get(f"/api/workflow/projects/{slug}/changes/{change_id}").json()
    assert current["status"] == "Aprovação de Design"
    assert current["design_approval_valid"] is False
    approvals = client.get(f"/api/workflow/projects/{slug}/changes/{change_id}/approvals").json()
    assert approvals[-1]["state"] == "rejected"
    assert "obsolete" in approvals[-1]["note"].lower()
    _close_client(client)


@pytest.mark.parametrize("target_status", ["Em desenvolvimento", "Code Review", "QA"])
def test_patch_evidence_after_development_returns_to_design_approval(
    monkeypatch, tmp_path, target_status
):
    monkeypatch.setattr(workflow_routes, "REPO_ROOT", tmp_path)
    change_id = f"active-evidence-{target_status.lower().replace(' ', '-')}"
    design_ref, prototype_ref = _write_design_delivery(tmp_path, change_id)
    client = _build_client(actor=ALAN)
    slug = _create_project_and_change(
        client,
        change_id=change_id,
        status="Design",
        extra={
            "ui_impact": "affected",
            "design_ref": design_ref,
            "prototype_ref": prototype_ref,
            "design_critique_verdict": "PASS",
        },
    )
    for stage in [
        "Aprovação de Design",
        "Pronto para Dev",
        "Em desenvolvimento",
        "Code Review",
        "QA",
    ]:
        moved = client.patch(
            f"/api/workflow/projects/{slug}/changes/{change_id}",
            json={"status": stage},
        )
        assert moved.status_code == 200, moved.text
        if stage == target_status:
            break

    changed = client.patch(
        f"/api/workflow/projects/{slug}/changes/{change_id}",
        json={"prototype_digest": "0" * 64},
    )
    assert changed.status_code == 200
    assert changed.json()["status"] == "Aprovação de Design"
    assert changed.json()["design_approval_valid"] is False
    if target_status == "QA":
        assert changed.json()["qa_round_id"] is None
    approvals = client.get(f"/api/workflow/projects/{slug}/changes/{change_id}/approvals").json()
    assert approvals[-1]["state"] == "rejected"
    _close_client(client)


def test_non_ui_bypass_requires_and_preserves_justification(monkeypatch, tmp_path):
    monkeypatch.setattr(workflow_routes, "REPO_ROOT", tmp_path)
    client = _build_client(actor=AGENT)
    missing_slug = _create_project_and_change(
        client,
        change_id="bypass-missing-reason",
        extra={"ui_impact": "none"},
    )
    rejected = client.patch(
        f"/api/workflow/projects/{missing_slug}/changes/bypass-missing-reason",
        json={"status": "Pronto para Dev"},
    )
    assert rejected.status_code == 409
    assert rejected.json()["detail"]["code"] == "ui_bypass_requires_justification"

    slug = _create_project_and_change(
        client,
        change_id="backend-only",
        extra={
            "ui_impact": "none",
            "ui_impact_justification": "Migração exclusivamente no backend.",
        },
    )
    ready = client.patch(
        f"/api/workflow/projects/{slug}/changes/backend-only",
        json={"status": "Pronto para Dev"},
    )
    assert ready.status_code == 200
    assert ready.json()["ui_impact_justification"] == "Migração exclusivamente no backend."
    developing = client.patch(
        f"/api/workflow/projects/{slug}/changes/backend-only",
        json={"status": "Em desenvolvimento"},
    )
    assert developing.status_code == 200
    assert developing.json()["status"] == "Em desenvolvimento"
    _close_client(client)


def test_qa_done_requires_qa_evidence_and_no_open_bugs(monkeypatch, tmp_path):
    monkeypatch.setattr(workflow_routes, "REPO_ROOT", tmp_path)
    client = _build_client(actor=AGENT)
    slug = _create_project_and_change(
        client,
        change_id="qa-gated",
        extra={"ui_impact": "none", "ui_impact_justification": "Backend only."},
    )
    _advance_non_ui_to(client, slug=slug, change_id="qa-gated", target="QA")

    missing_qa = client.patch(
        f"/api/workflow/projects/{slug}/changes/qa-gated", json={"status": "Done"}
    )
    assert missing_qa.status_code == 409
    assert missing_qa.json()["detail"]["code"] == "qa_gate_not_approved"

    bug = client.post(
        f"/api/workflow/projects/{slug}/changes/qa-gated/tasks",
        json={"type": "bug", "title": "Blocking regression"},
    )
    assert bug.status_code == 200
    forged = client.post(
        f"/api/workflow/projects/{slug}/changes/qa-gated/approvals",
        json={"scope": "change", "gate": "QA", "state": "approved", "note": "qa-gate green"},
    )
    assert forged.status_code == 409
    current_qa = client.get(f"/api/workflow/projects/{slug}/changes/qa-gated").json()
    approval = client.post(
        f"/api/workflow/projects/{slug}/changes/qa-gated/qa-approvals",
        headers={"X-Workflow-QA-Token": QA_TOKEN},
        json={
            "round_id": current_qa["qa_round_id"],
            "commit_sha": current_qa["qa_commit_sha"],
            "evidence": "qa-gate green",
        },
    )
    assert approval.status_code == 200
    blocked = client.patch(
        f"/api/workflow/projects/{slug}/changes/qa-gated", json={"status": "Done"}
    )
    assert blocked.status_code == 409
    assert blocked.json()["detail"]["code"] == "blocking_child_bugs"

    closed = client.patch(
        f"/api/workflow/work-items/{bug.json()['id']}?project_slug={slug}",
        json={"state": "done"},
    )
    assert closed.status_code == 200
    done = client.patch(f"/api/workflow/projects/{slug}/changes/qa-gated", json={"status": "Done"})
    assert done.status_code == 200
    assert done.json()["status"] == "Done"
    _close_client(client)


def test_qa_approval_is_bound_to_current_round_and_commit(monkeypatch, tmp_path):
    monkeypatch.setattr(workflow_routes, "REPO_ROOT", tmp_path)
    client = _build_client(actor=AGENT)
    slug = _create_project_and_change(
        client,
        change_id="qa-round-binding",
        extra={"ui_impact": "none", "ui_impact_justification": "Backend only."},
    )
    _advance_non_ui_to(client, slug=slug, change_id="qa-round-binding", target="QA")
    first = client.get(f"/api/workflow/projects/{slug}/changes/qa-round-binding").json()
    approved = client.post(
        f"/api/workflow/projects/{slug}/changes/qa-round-binding/qa-approvals",
        headers={"X-Workflow-QA-Token": QA_TOKEN},
        json={
            "round_id": first["qa_round_id"],
            "commit_sha": first["qa_commit_sha"],
            "evidence": "first run green",
        },
    )
    assert approved.status_code == 200

    rework = client.patch(
        f"/api/workflow/projects/{slug}/changes/qa-round-binding",
        json={"status": "Em desenvolvimento", "rework_reason": "QA found regression"},
    )
    assert rework.status_code == 200
    assert rework.json()["qa_round_id"] is None
    assert rework.json()["qa_approved_round_id"] is None
    assert (
        client.patch(
            f"/api/workflow/projects/{slug}/changes/qa-round-binding",
            json={"status": "Code Review"},
        ).status_code
        == 200
    )
    second_qa = client.patch(
        f"/api/workflow/projects/{slug}/changes/qa-round-binding",
        json={"status": "QA"},
    )
    assert second_qa.status_code == 200
    second = second_qa.json()
    assert second["qa_round_id"] != first["qa_round_id"]
    stale = client.post(
        f"/api/workflow/projects/{slug}/changes/qa-round-binding/qa-approvals",
        headers={"X-Workflow-QA-Token": QA_TOKEN},
        json={
            "round_id": first["qa_round_id"],
            "commit_sha": first["qa_commit_sha"],
            "evidence": "replayed approval",
        },
    )
    assert stale.status_code == 409
    assert stale.json()["detail"]["code"] == "qa_round_mismatch"

    current_approval = client.post(
        f"/api/workflow/projects/{slug}/changes/qa-round-binding/qa-approvals",
        headers={"X-Workflow-QA-Token": QA_TOKEN},
        json={
            "round_id": second["qa_round_id"],
            "commit_sha": second["qa_commit_sha"],
            "evidence": "second run green",
        },
    )
    assert current_approval.status_code == 200
    monkeypatch.setattr(workflow_transition_service, "current_commit_sha", lambda _root: "b" * 40)
    obsolete = client.patch(
        f"/api/workflow/projects/{slug}/changes/qa-round-binding",
        json={"status": "Done"},
    )
    assert obsolete.status_code == 409
    assert obsolete.json()["detail"]["code"] == "qa_gate_not_approved"
    _close_client(client)


def test_done_homologado_requires_authenticated_alan(monkeypatch, tmp_path):
    monkeypatch.setattr(workflow_routes, "REPO_ROOT", tmp_path)
    client = _build_client(actor=AGENT)
    slug = _create_project_and_change(
        client,
        change_id="human-homologation",
        extra={"ui_impact": "none", "ui_impact_justification": "Backend only."},
    )
    _advance_non_ui_to(client, slug=slug, change_id="human-homologation", target="Done")
    rejected = client.patch(
        f"/api/workflow/projects/{slug}/changes/human-homologation",
        json={"status": "Homologado", "actor": ALAN.email},
    )
    assert rejected.status_code == 403
    assert rejected.json()["detail"]["code"] == "homologation_approver_required"

    _set_actor(client, ALAN)
    approved = client.patch(
        f"/api/workflow/projects/{slug}/changes/human-homologation",
        json={"status": "Homologado", "actor": AGENT.email},
    )
    assert approved.status_code == 200
    approvals = client.get(
        f"/api/workflow/projects/{slug}/changes/human-homologation/approvals"
    ).json()
    assert approvals[-1]["gate"] == "Homologation"
    assert approvals[-1]["actor"] == ALAN.email
    _close_client(client)


def test_homologado_pronto_requires_main_publication(monkeypatch, tmp_path):
    monkeypatch.setattr(workflow_routes, "REPO_ROOT", tmp_path)
    client = _build_client(actor=AGENT)
    slug = _create_project_and_change(
        client,
        change_id="published-card",
        extra={"ui_impact": "none", "ui_impact_justification": "Backend only."},
    )
    _advance_non_ui_to(client, slug=slug, change_id="published-card", target="Homologado")

    def publication_missing(_root, **_kwargs):
        raise UpstreamGuardError("not in origin/main")

    monkeypatch.setattr(
        workflow_transition_service, "require_card_main_publication", publication_missing
    )
    _set_actor(client, AGENT)
    unauthorized = client.patch(
        f"/api/workflow/projects/{slug}/changes/published-card", json={"status": "Pronto"}
    )
    assert unauthorized.status_code == 403
    assert unauthorized.json()["detail"]["code"] == "release_approver_required"
    _set_actor(client, ALAN)
    rejected = client.patch(
        f"/api/workflow/projects/{slug}/changes/published-card", json={"status": "Pronto"}
    )
    assert rejected.status_code == 409
    assert rejected.json()["detail"]["code"] == "publication_not_verified"

    monkeypatch.setattr(
        workflow_transition_service,
        "require_card_main_publication",
        lambda _root, **_kwargs: MainPublicationEvidence(
            head_sha="a" * 40,
            main_sha="b" * 40,
            main_ref="origin/main",
        ),
    )
    ready = client.patch(
        f"/api/workflow/projects/{slug}/changes/published-card", json={"status": "Pronto"}
    )
    assert ready.status_code == 200
    assert ready.json()["status"] == "Pronto"
    approvals = client.get(f"/api/workflow/projects/{slug}/changes/published-card/approvals").json()
    assert approvals[-1]["gate"] == "Publication"
    assert "origin/main" in approvals[-1]["note"]
    _close_client(client)


def test_design_evidence_edit_after_done_is_rejected(monkeypatch, tmp_path):
    monkeypatch.setattr(workflow_routes, "REPO_ROOT", tmp_path)
    client = _build_client(actor=AGENT)
    slug = _create_project_and_change(
        client,
        change_id="immutable-done",
        extra={"ui_impact": "none", "ui_impact_justification": "Backend only."},
    )
    _advance_non_ui_to(client, slug=slug, change_id="immutable-done", target="Done")
    rejected = client.patch(
        f"/api/workflow/projects/{slug}/changes/immutable-done",
        json={"ui_impact_justification": "Changed after Done."},
    )
    assert rejected.status_code == 409
    assert rejected.json()["detail"]["code"] == "design_evidence_immutable_after_done"
    current = client.get(f"/api/workflow/projects/{slug}/changes/immutable-done").json()
    assert current["status"] == "Done"
    assert current["ui_impact_justification"] == "Backend only."
    _close_client(client)
