from __future__ import annotations

from uuid import uuid4

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
    client = TestClient(app)
    client.engine = engine  # type: ignore[attr-defined]
    return client


def _close_client(client: TestClient) -> None:
    client.close()
    client.app.dependency_overrides.clear()
    client.engine.dispose()  # type: ignore[attr-defined]


def test_audit_coordination_reports_missing_changes(monkeypatch):
    client = _build_client()
    project_slug = f"crypto-{uuid4().hex[:8]}"

    # Seed DB with a project + 2 changes.
    assert (
        client.post(
            "/api/workflow/projects", json={"slug": project_slug, "name": "Crypto"}
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"/api/workflow/projects/{project_slug}/changes",
            json={"change_id": "a", "title": "A", "status": "DEV"},
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"/api/workflow/projects/{project_slug}/changes",
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

    res = client.get(f"/api/workflow/audit/coordination?project_slug={project_slug}")
    assert res.status_code == 200
    body = res.json()

    assert body["coordination_active"] == 2
    assert set(body["missing_in_db"]) == {"b"}
    assert set(body["missing_in_coordination"]) == {"c"}
    _close_client(client)
