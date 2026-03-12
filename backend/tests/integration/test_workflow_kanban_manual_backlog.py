from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
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


def test_kanban_create_change_starts_in_pending_with_description():
    client = _build_client()
    assert client.post("/api/workflow/projects", json={"slug": "crypto", "name": "Crypto"}).status_code == 200

    created = client.post(
        "/api/workflow/kanban/changes?project_slug=crypto",
        json={"title": "Manual backlog card", "description": "Created directly from Kanban"},
    )
    assert created.status_code == 200
    item = created.json()["item"]
    assert item["id"] == "manual-backlog-card"
    assert item["column"] == "Pending"
    assert item["description"] == "Created directly from Kanban"

    listed = client.get("/api/workflow/kanban/changes?project_slug=crypto")
    assert listed.status_code == 200
    board_item = listed.json()["items"][0]
    assert board_item["column"] == "Pending"
    assert board_item["description"] == "Created directly from Kanban"

    fetched = client.get("/api/workflow/projects/crypto/changes/manual-backlog-card")
    assert fetched.status_code == 200
    assert fetched.json()["description"] == "Created directly from Kanban"

    client.app.dependency_overrides.clear()


def test_kanban_move_syncs_runtime_gate_statuses():
    client = _build_client()
    assert client.post("/api/workflow/projects", json={"slug": "crypto", "name": "Crypto"}).status_code == 200
    assert client.post(
        "/api/workflow/kanban/changes?project_slug=crypto",
        json={"title": "Drag me", "description": "Desktop drag/drop path"},
    ).status_code == 200

    moved_to_dev = client.patch(
        "/api/workflow/projects/crypto/changes/drag-me",
        json={"status": "DEV"},
    )
    assert moved_to_dev.status_code == 200
    assert moved_to_dev.json()["status"] == "DEV"

    board = client.get("/api/workflow/kanban/changes?project_slug=crypto")
    assert board.status_code == 200
    item = board.json()["items"][0]
    assert item["column"] == "DEV"
    assert item["status"]["PO"] == "approved"
    assert item["status"]["DESIGN"] == "approved"
    assert item["status"]["Alan approval"] == "approved"
    assert item["status"]["DEV"] == "pending"
    assert item["status"]["QA"] == "pending"

    moved_back = client.patch(
        "/api/workflow/projects/crypto/changes/drag-me",
        json={"status": "PO"},
    )
    assert moved_back.status_code == 200
    assert moved_back.json()["status"] == "PO"

    board_after_back = client.get("/api/workflow/kanban/changes?project_slug=crypto")
    item_back = board_after_back.json()["items"][0]
    assert item_back["column"] == "PO"
    assert item_back["status"]["PO"] == "pending"
    assert item_back["status"]["DESIGN"] == "pending"
    assert item_back["status"]["Alan approval"] == "pending"

    client.app.dependency_overrides.clear()
