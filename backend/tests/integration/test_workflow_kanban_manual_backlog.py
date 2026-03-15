from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.routes import workflow as workflow_routes

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
    client = TestClient(app)
    client.session_local = SessionLocal  # type: ignore[attr-defined]
    return client


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
    assert item["card_number"] == 1

    listed = client.get("/api/workflow/kanban/changes?project_slug=crypto")
    assert listed.status_code == 200
    board_item = listed.json()["items"][0]
    assert board_item["column"] == "Pending"
    assert board_item["description"] == "Created directly from Kanban"
    assert board_item["card_number"] == 1

    fetched = client.get("/api/workflow/projects/crypto/changes/manual-backlog-card")
    assert fetched.status_code == 200
    assert fetched.json()["description"] == "Created directly from Kanban"
    assert fetched.json()["card_number"] == 1

    client.app.dependency_overrides.clear()


def test_kanban_move_syncs_runtime_gate_statuses():
    client = _build_client()
    assert client.post("/api/workflow/projects", json={"slug": "crypto", "name": "Crypto"}).status_code == 200
    assert client.post(
        "/api/workflow/kanban/changes?project_slug=crypto",
        json={"title": "Drag me", "description": "Desktop drag/drop path"},
    ).status_code == 200

    assert client.patch(
        "/api/workflow/projects/crypto/changes/drag-me",
        json={"status": "PO"},
    ).status_code == 200
    assert client.patch(
        "/api/workflow/projects/crypto/changes/drag-me",
        json={"status": "DESIGN"},
    ).status_code == 200
    assert client.patch(
        "/api/workflow/projects/crypto/changes/drag-me",
        json={"status": "Alan approval"},
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


def test_dev_to_qa_does_not_trigger_upstream_guard(monkeypatch):
    client = _build_client()
    assert client.post("/api/workflow/projects", json={"slug": "crypto", "name": "Crypto"}).status_code == 200
    assert client.post(
        "/api/workflow/kanban/changes?project_slug=crypto",
        json={"title": "Publish later", "description": "DEV -> QA should not be blocked by local unpublished work"},
    ).status_code == 200

    for column in ["PO", "DESIGN", "Alan approval", "DEV"]:
        moved = client.patch(
            "/api/workflow/projects/crypto/changes/publish-later",
            json={"status": column},
        )
        assert moved.status_code == 200

    def fail_if_called(*args, **kwargs):
        raise AssertionError("upstream guard should not run for DEV -> QA")

    monkeypatch.setattr(workflow_routes, "require_upstream_published", fail_if_called)

    moved = client.patch(
        "/api/workflow/projects/crypto/changes/publish-later",
        json={"status": "QA"},
    )
    assert moved.status_code == 200
    assert moved.json()["status"] == "QA"

    client.app.dependency_overrides.clear()



def test_kanban_rejects_skipping_workflow_gates_with_actionable_error():
    client = _build_client()
    assert client.post("/api/workflow/projects", json={"slug": "crypto", "name": "Crypto"}).status_code == 200
    assert client.post(
        "/api/workflow/kanban/changes?project_slug=crypto",
        json={"title": "Skip me", "description": "Should fail on invalid jump"},
    ).status_code == 200

    rejected = client.patch(
        "/api/workflow/projects/crypto/changes/skip-me",
        json={"status": "DEV"},
    )
    assert rejected.status_code == 409
    payload = rejected.json()["detail"]
    assert payload["code"] == "invalid_kanban_transition"
    assert payload["current"] == "Pending"
    assert payload["target"] == "DEV"
    assert payload["allowed_targets"] == ["PO"]

    client.app.dependency_overrides.clear()


def test_kanban_exposes_functional_publish_and_homologation_readiness_states(monkeypatch):
    client = _build_client()
    assert client.post("/api/workflow/projects", json={"slug": "crypto", "name": "Crypto"}).status_code == 200
    assert client.post(
        "/api/workflow/kanban/changes?project_slug=crypto",
        json={"title": "Operational states", "description": "Need explicit QA/publish/runtime distinction"},
    ).status_code == 200

    for column in ["PO", "DESIGN", "Alan approval", "DEV", "QA"]:
        moved = client.patch(
            "/api/workflow/projects/crypto/changes/operational-states",
            json={"status": column},
        )
        assert moved.status_code == 200

    approved = client.post(
        "/api/workflow/projects/crypto/changes/operational-states/approvals",
        json={"scope": "change", "gate": "QA", "state": "approved", "actor": "QA", "note": "functional green"},
    )
    assert approved.status_code == 200

    monkeypatch.setattr(workflow_routes, "require_upstream_published", lambda *args, **kwargs: (_ for _ in ()).throw(workflow_routes.UpstreamGuardError("publish blocked")))

    board = client.get("/api/workflow/kanban/changes?project_slug=crypto")
    assert board.status_code == 200
    item = board.json()["items"][0]
    assert item["status"]["QA functional"] == "approved"
    assert item["status"]["Publish"] == "blocked"
    assert item["status"]["Runtime stage"] == "Alan homologation"
    assert item["status"]["Homologation readiness"] == "blocked: publish/reconcile pending"

    client.app.dependency_overrides.clear()



def test_kanban_reorder_persists_within_same_column():
    client = _build_client()
    assert client.post("/api/workflow/projects", json={"slug": "crypto", "name": "Crypto"}).status_code == 200

    for title in ["First card", "Second card", "Third card"]:
        created = client.post(
            "/api/workflow/kanban/changes?project_slug=crypto",
            json={"title": title, "description": "Reorder test"},
        )
        assert created.status_code == 200

    board = client.get("/api/workflow/kanban/changes?project_slug=crypto")
    assert [item["id"] for item in board.json()["items"]] == ["first-card", "second-card", "third-card"]
    assert [item["card_number"] for item in board.json()["items"]] == [1, 2, 3]

    moved_up = client.patch(
        "/api/workflow/projects/crypto/changes/second-card",
        json={"reorder": "up"},
    )
    assert moved_up.status_code == 200
    assert moved_up.json()["card_number"] == 2

    board_after_up = client.get("/api/workflow/kanban/changes?project_slug=crypto")
    assert [item["id"] for item in board_after_up.json()["items"]] == ["second-card", "first-card", "third-card"]
    assert [item["card_number"] for item in board_after_up.json()["items"]] == [2, 1, 3]

    edited = client.patch(
        "/api/workflow/projects/crypto/changes/second-card",
        json={"title": "Second card renamed", "description": "Edited without renumbering"},
    )
    assert edited.status_code == 200
    assert edited.json()["card_number"] == 2

    moved_down = client.patch(
        "/api/workflow/projects/crypto/changes/second-card",
        json={"reorder": "down"},
    )
    assert moved_down.status_code == 200
    assert moved_down.json()["card_number"] == 2

    board_after_down = client.get("/api/workflow/kanban/changes?project_slug=crypto")
    assert [item["id"] for item in board_after_down.json()["items"]] == ["first-card", "second-card", "third-card"]
    assert [item["card_number"] for item in board_after_down.json()["items"]] == [1, 2, 3]

    client.app.dependency_overrides.clear()


def test_kanban_backfills_missing_card_numbers_for_legacy_rows():
    client = _build_client()
    assert client.post("/api/workflow/projects", json={"slug": "crypto", "name": "Crypto"}).status_code == 200

    assert client.post(
        "/api/workflow/projects/crypto/changes",
        json={"change_id": "legacy-a", "title": "Legacy A", "description": "old row", "status": "Pending"},
    ).status_code == 200
    assert client.post(
        "/api/workflow/projects/crypto/changes",
        json={"change_id": "legacy-b", "title": "Legacy B", "description": "old row", "status": "Pending"},
    ).status_code == 200

    session = client.session_local()
    try:
        session.execute(text("UPDATE wf_changes SET card_number = NULL"))
        session.commit()
    finally:
        session.close()

    board = client.get("/api/workflow/kanban/changes?project_slug=crypto")
    assert board.status_code == 200
    assert [(item["id"], item["card_number"]) for item in board.json()["items"]] == [("legacy-a", 1), ("legacy-b", 2)]

    next_created = client.post(
        "/api/workflow/kanban/changes?project_slug=crypto",
        json={"title": "Legacy C", "description": "after backfill"},
    )
    assert next_created.status_code == 200
    assert next_created.json()["item"]["card_number"] == 3

    client.app.dependency_overrides.clear()


def test_kanban_reorder_recovers_legacy_zeroed_positions():
    client = _build_client()
    assert client.post("/api/workflow/projects", json={"slug": "crypto", "name": "Crypto"}).status_code == 200

    for title in ["Legacy A", "Legacy B", "Legacy C"]:
        created = client.post(
            "/api/workflow/kanban/changes?project_slug=crypto",
            json={"title": title, "description": "Legacy zero sort_order regression"},
        )
        assert created.status_code == 200

    session = client.session_local()
    try:
        session.execute(text("UPDATE wf_changes SET sort_order = 0"))
        session.commit()
    finally:
        session.close()

    moved_up = client.patch(
        "/api/workflow/projects/crypto/changes/legacy-b",
        json={"reorder": "up"},
    )
    assert moved_up.status_code == 200

    board_after_up = client.get("/api/workflow/kanban/changes?project_slug=crypto")
    assert [item["id"] for item in board_after_up.json()["items"]] == ["legacy-b", "legacy-a", "legacy-c"]

    client.app.dependency_overrides.clear()


def test_reorder_does_not_move_between_columns():
    client = _build_client()
    assert client.post("/api/workflow/projects", json={"slug": "crypto", "name": "Crypto"}).status_code == 200

    for title in ["Pending A", "Pending B"]:
        assert client.post(
            "/api/workflow/kanban/changes?project_slug=crypto",
            json={"title": title, "description": "Pending reorder scope"},
        ).status_code == 200

    assert client.patch(
        "/api/workflow/projects/crypto/changes/pending-b",
        json={"status": "PO"},
    ).status_code == 200

    reordered = client.patch(
        "/api/workflow/projects/crypto/changes/pending-a",
        json={"reorder": "down"},
    )
    assert reordered.status_code == 200

    board = client.get("/api/workflow/kanban/changes?project_slug=crypto")
    items = board.json()["items"]
    pending_ids = [item["id"] for item in items if item["column"] == "Pending"]
    po_ids = [item["id"] for item in items if item["column"] == "PO"]
    assert pending_ids == ["pending-a"]
    assert po_ids == ["pending-b"]

    client.app.dependency_overrides.clear()


def test_cancel_archive_bypasses_formal_archive_gate_flow_but_preserves_history():
    client = _build_client()
    assert client.post("/api/workflow/projects", json={"slug": "crypto", "name": "Crypto"}).status_code == 200
    assert client.post(
        "/api/workflow/kanban/changes?project_slug=crypto",
        json={"title": "Cancel me", "description": "Runtime cancel should archive card without final archive flow"},
    ).status_code == 200

    for status in ["PO", "DESIGN", "Alan approval", "DEV"]:
        moved = client.patch(
            "/api/workflow/projects/crypto/changes/cancel-me",
            json={"status": status},
        )
        assert moved.status_code == 200

    canceled = client.patch(
        "/api/workflow/projects/crypto/changes/cancel-me",
        json={"status": "Archived", "cancel_archive": True},
    )
    assert canceled.status_code == 200
    assert canceled.json()["status"] == "Archived"

    board = client.get("/api/workflow/kanban/changes?project_slug=crypto")
    assert board.status_code == 200
    item = board.json()["items"][0]
    assert item["column"] == "Archived"
    assert item["archived"] is True
    assert item["status"]["PO"] == "approved"
    assert item["status"]["DESIGN"] == "approved"
    assert item["status"]["Alan approval"] == "approved"
    assert item["status"]["DEV"] == "pending"
    assert item["status"]["QA"] == "pending"
    assert item["status"]["Alan homologation"] == "pending"

    fetched = client.get("/api/workflow/projects/crypto/changes/cancel-me")
    assert fetched.status_code == 200
    assert fetched.json()["status"] == "Archived"

    client.app.dependency_overrides.clear()
