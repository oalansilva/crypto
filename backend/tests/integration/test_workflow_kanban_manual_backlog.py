from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.routes import workflow as workflow_routes

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
    client.session_local = SessionLocal  # type: ignore[attr-defined]
    return client


def _close_client(client: TestClient) -> None:
    client.close()
    client.app.dependency_overrides.clear()
    client.engine.dispose()  # type: ignore[attr-defined]


def _project_slug() -> str:
    return f"crypto-{uuid4().hex[:8]}"


def test_kanban_create_change_starts_in_pending_with_description():
    client = _build_client()
    project_slug = _project_slug()
    assert (
        client.post(
            "/api/workflow/projects", json={"slug": project_slug, "name": "Crypto"}
        ).status_code
        == 200
    )

    created = client.post(
        f"/api/workflow/kanban/changes?project_slug={project_slug}",
        json={"title": "Manual backlog card", "description": "Created directly from Kanban"},
    )
    assert created.status_code == 200
    item = created.json()["item"]
    assert item["id"] == "manual-backlog-card"
    assert item["column"] == "Pending"
    assert item["description"] == "Created directly from Kanban"
    assert item["card_number"] == 1

    listed = client.get(f"/api/workflow/kanban/changes?project_slug={project_slug}")
    assert listed.status_code == 200
    board_item = listed.json()["items"][0]
    assert board_item["column"] == "Pending"
    assert board_item["description"] == "Created directly from Kanban"
    assert board_item["card_number"] == 1

    fetched = client.get(f"/api/workflow/projects/{project_slug}/changes/manual-backlog-card")
    assert fetched.status_code == 200
    assert fetched.json()["description"] == "Created directly from Kanban"
    assert fetched.json()["card_number"] == 1

    _close_client(client)


def test_kanban_reorder_persists_within_same_column():
    client = _build_client()
    project_slug = _project_slug()
    assert (
        client.post(
            "/api/workflow/projects", json={"slug": project_slug, "name": "Crypto"}
        ).status_code
        == 200
    )

    for title in ["First card", "Second card", "Third card"]:
        created = client.post(
            f"/api/workflow/kanban/changes?project_slug={project_slug}",
            json={"title": title, "description": "Reorder test"},
        )
        assert created.status_code == 200

    board = client.get(f"/api/workflow/kanban/changes?project_slug={project_slug}")
    assert [item["id"] for item in board.json()["items"]] == [
        "first-card",
        "second-card",
        "third-card",
    ]
    assert [item["card_number"] for item in board.json()["items"]] == [1, 2, 3]

    moved_up = client.patch(
        f"/api/workflow/projects/{project_slug}/changes/second-card",
        json={"reorder": "up"},
    )
    assert moved_up.status_code == 200
    assert moved_up.json()["card_number"] == 2

    board_after_up = client.get(f"/api/workflow/kanban/changes?project_slug={project_slug}")
    assert [item["id"] for item in board_after_up.json()["items"]] == [
        "second-card",
        "first-card",
        "third-card",
    ]
    assert [item["card_number"] for item in board_after_up.json()["items"]] == [2, 1, 3]

    edited = client.patch(
        f"/api/workflow/projects/{project_slug}/changes/second-card",
        json={"title": "Second card renamed", "description": "Edited without renumbering"},
    )
    assert edited.status_code == 200
    assert edited.json()["card_number"] == 2

    moved_down = client.patch(
        f"/api/workflow/projects/{project_slug}/changes/second-card",
        json={"reorder": "down"},
    )
    assert moved_down.status_code == 200
    assert moved_down.json()["card_number"] == 2

    board_after_down = client.get(f"/api/workflow/kanban/changes?project_slug={project_slug}")
    assert [item["id"] for item in board_after_down.json()["items"]] == [
        "first-card",
        "second-card",
        "third-card",
    ]
    assert [item["card_number"] for item in board_after_down.json()["items"]] == [1, 2, 3]

    _close_client(client)


def test_kanban_backfills_missing_card_numbers_for_legacy_rows():
    client = _build_client()
    project_slug = _project_slug()
    assert (
        client.post(
            "/api/workflow/projects", json={"slug": project_slug, "name": "Crypto"}
        ).status_code
        == 200
    )

    assert (
        client.post(
            f"/api/workflow/projects/{project_slug}/changes",
            json={
                "change_id": "legacy-a",
                "title": "Legacy A",
                "description": "old row",
                "status": "Pending",
            },
        ).status_code
        == 200
    )
    assert (
        client.post(
            f"/api/workflow/projects/{project_slug}/changes",
            json={
                "change_id": "legacy-b",
                "title": "Legacy B",
                "description": "old row",
                "status": "Pending",
            },
        ).status_code
        == 200
    )

    session = client.session_local()
    try:
        session.execute(text("UPDATE wf_changes SET card_number = NULL"))
        session.commit()
    finally:
        session.close()

    board = client.get(f"/api/workflow/kanban/changes?project_slug={project_slug}")
    assert board.status_code == 200
    assert [(item["id"], item["card_number"]) for item in board.json()["items"]] == [
        ("legacy-a", 1),
        ("legacy-b", 2),
    ]

    next_created = client.post(
        f"/api/workflow/kanban/changes?project_slug={project_slug}",
        json={"title": "Legacy C", "description": "after backfill"},
    )
    assert next_created.status_code == 200
    assert next_created.json()["item"]["card_number"] == 3

    _close_client(client)


def test_kanban_reorder_recovers_legacy_zeroed_positions():
    client = _build_client()
    project_slug = _project_slug()
    assert (
        client.post(
            "/api/workflow/projects", json={"slug": project_slug, "name": "Crypto"}
        ).status_code
        == 200
    )

    for title in ["Legacy A", "Legacy B", "Legacy C"]:
        created = client.post(
            f"/api/workflow/kanban/changes?project_slug={project_slug}",
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
        f"/api/workflow/projects/{project_slug}/changes/legacy-b",
        json={"reorder": "up"},
    )
    assert moved_up.status_code == 200

    board_after_up = client.get(f"/api/workflow/kanban/changes?project_slug={project_slug}")
    assert [item["id"] for item in board_after_up.json()["items"]] == [
        "legacy-b",
        "legacy-a",
        "legacy-c",
    ]

    _close_client(client)


def test_reorder_does_not_move_between_columns():
    client = _build_client()
    project_slug = _project_slug()
    assert (
        client.post(
            "/api/workflow/projects", json={"slug": project_slug, "name": "Crypto"}
        ).status_code
        == 200
    )

    for title in ["Pending A", "Pending B"]:
        assert (
            client.post(
                f"/api/workflow/kanban/changes?project_slug={project_slug}",
                json={"title": title, "description": "Pending reorder scope"},
            ).status_code
            == 200
        )

    assert (
        client.patch(
            f"/api/workflow/projects/{project_slug}/changes/pending-b",
            json={"status": "PO"},
        ).status_code
        == 200
    )

    reordered = client.patch(
        f"/api/workflow/projects/{project_slug}/changes/pending-a",
        json={"reorder": "down"},
    )
    assert reordered.status_code == 200

    board = client.get(f"/api/workflow/kanban/changes?project_slug={project_slug}")
    items = board.json()["items"]
    pending_ids = [item["id"] for item in items if item["column"] == "Pending"]
    po_ids = [item["id"] for item in items if item["column"] == "PO"]
    assert pending_ids == ["pending-a"]
    assert po_ids == ["pending-b"]

    _close_client(client)
