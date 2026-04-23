from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.workflow_database import WorkflowBase, get_workflow_db


def _build_client():
    engine = create_engine(
        "postgresql://postgres:postgres@127.0.0.1:5432/postgres",
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


def test_audit_coordination_reports_missing_changes(monkeypatch):
    client = _build_client()

    # Seed DB with a project + 2 changes.
    assert (
        client.post("/api/workflow/projects", json={"slug": "crypto", "name": "Crypto"}).status_code
        == 200
    )
    assert (
        client.post(
            "/api/workflow/projects/crypto/changes",
            json={"change_id": "a", "title": "A", "status": "DEV"},
        ).status_code
        == 200
    )
    assert (
        client.post(
            "/api/workflow/projects/crypto/changes",
            json={"change_id": "c", "title": "C", "status": "DEV"},
        ).status_code
        == 200
    )

    # Coordination files say: a + b are active.
    from app.services import coordination_service

    monkeypatch.setattr(
        coordination_service,
        "list_coordination_changes",
        lambda: [
            {"id": "a", "archived": False},
            {"id": "b", "archived": False},
            {"id": "z", "archived": True},
        ],
    )

    res = client.get("/api/workflow/audit/coordination?project_slug=crypto")
    assert res.status_code == 200
    body = res.json()

    assert body["coordination_active"] == 2
    assert set(body["missing_in_db"]) == {"b"}
    assert set(body["missing_in_coordination"]) == {"c"}
