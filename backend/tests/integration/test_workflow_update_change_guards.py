from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.routes import workflow as workflow_routes
from app.services.upstream_guard import UpstreamGuardError
from app.workflow_database import WorkflowBase, get_workflow_db


def _build_client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    WorkflowBase.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_workflow_db] = override_get_db
    return TestClient(app)


def _create_change(client: TestClient, *, change_id: str, status: str):
    assert client.post(
        "/api/workflow/projects/crypto/changes",
        json={"change_id": change_id, "title": f"{change_id}", "status": status},
    ).status_code == 200


def test_update_change_rejects_approval_without_openspec_artifacts(monkeypatch, tmp_path):
    monkeypatch.setattr(workflow_routes, "REPO_ROOT", tmp_path)
    client = _build_client()
    client.post("/api/workflow/projects", json={"slug": "crypto", "name": "Crypto"})
    _create_change(client, change_id="missing-artifacts", status="DESIGN")

    response = client.patch(
        "/api/workflow/projects/crypto/changes/missing-artifacts",
        json={"status": "Approval"},
    )
    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["code"] == "missing_openspec_artifacts"
    assert set(detail["missing_files"]) == {"proposal.md", "review-ptbr.md", "tasks.md"}
    client.app.dependency_overrides.clear()


def test_update_change_rejects_homologation_when_qa_not_approved(monkeypatch, tmp_path):
    monkeypatch.setattr(workflow_routes, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        workflow_routes,
        "require_upstream_published",
        lambda *_args, **_kwargs: None,
    )

    client = _build_client()
    client.post("/api/workflow/projects", json={"slug": "crypto", "name": "Crypto"})
    _create_change(client, change_id="homologation-needs-qa", status="QA")
    client.post(
        "/api/workflow/projects/crypto/changes/homologation-needs-qa/approvals",
        json={"scope": "change", "gate": "DEV", "state": "approved", "actor": "dev", "note": "ok"},
    )

    response = client.patch(
        "/api/workflow/projects/crypto/changes/homologation-needs-qa",
        json={"status": "Homologation"},
    )
    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["code"] == "qa_not_approved"
    client.app.dependency_overrides.clear()


def test_update_change_rejects_homologation_when_upstream_guard_blocks(monkeypatch):
    client = _build_client()
    client.post("/api/workflow/projects", json={"slug": "crypto", "name": "Crypto"})
    _create_change(client, change_id="homologation-blocked", status="QA")

    client.post(
        "/api/workflow/projects/crypto/changes/homologation-blocked/approvals",
        json={"scope": "change", "gate": "DEV", "state": "approved", "actor": "dev", "note": "ok"},
    )
    client.post(
        "/api/workflow/projects/crypto/changes/homologation-blocked/approvals",
        json={"scope": "change", "gate": "QA", "state": "approved", "actor": "qa", "note": "ok"},
    )

    def _raise_upstream_block(*_args, **_kwargs):
        raise UpstreamGuardError("blocked")

    monkeypatch.setattr(
        workflow_routes,
        "require_upstream_published",
        _raise_upstream_block,
    )

    response = client.patch(
        "/api/workflow/projects/crypto/changes/homologation-blocked",
        json={"status": "Homologation"},
    )
    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["code"] == "upstream_guard_blocked"
    client.app.dependency_overrides.clear()


def test_update_change_rejects_archive_with_open_bugs():
    client = _build_client()
    client.post("/api/workflow/projects", json={"slug": "crypto", "name": "Crypto"})
    _create_change(client, change_id="archive-blocked", status="Homologation")

    client.post(
        "/api/workflow/projects/crypto/changes/archive-blocked/approvals",
        json={"scope": "change", "gate": "DEV", "state": "approved", "actor": "dev", "note": "ok"},
    )
    client.post(
        "/api/workflow/projects/crypto/changes/archive-blocked/approvals",
        json={"scope": "change", "gate": "QA", "state": "approved", "actor": "qa", "note": "ok"},
    )
    bug = client.post(
        "/api/workflow/projects/crypto/changes/archive-blocked/tasks",
        json={"type": "bug", "title": "Open bug"},
    )
    assert bug.status_code == 200

    response = client.patch(
        "/api/workflow/projects/crypto/changes/archive-blocked",
        json={"status": "Archived"},
    )
    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["code"] == "open_bugs_block_archive"
    assert "Open bug" in detail["open_bugs"]
    client.app.dependency_overrides.clear()
