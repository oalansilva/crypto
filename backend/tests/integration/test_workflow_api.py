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


def test_workflow_api_supports_changes_tasks_comments_approvals_and_handoffs():
    client = _build_client()

    project = client.post("/api/workflow/projects", json={"slug": "crypto", "name": "Crypto"})
    assert project.status_code == 200

    change = client.post(
        "/api/workflow/projects/crypto/changes",
        json={
            "change_id": "centralize-workflow-state-db",
            "title": "Workflow DB",
            "description": "Initial workflow runtime cutover",
            "status": "in_progress",
        },
    )
    assert change.status_code == 200
    change_body = change.json()
    assert change_body["change_id"] == "centralize-workflow-state-db"
    assert change_body["description"] == "Initial workflow runtime cutover"

    updated = client.patch(
        "/api/workflow/projects/crypto/changes/centralize-workflow-state-db",
        json={"status": "DEV", "title": "Workflow DB APIs", "description": "APIs and Kanban compat"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "DEV"
    assert updated.json()["description"] == "APIs and Kanban compat"

    story = client.post(
        "/api/workflow/projects/crypto/changes/centralize-workflow-state-db/tasks",
        json={"type": "story", "title": "Add workflow APIs", "description": "Expose DB-backed runtime state"},
    )
    assert story.status_code == 200
    story_id = story.json()["id"]

    bug = client.post(
        "/api/workflow/projects/crypto/changes/centralize-workflow-state-db/tasks",
        json={"type": "bug", "title": "Fix approval filter", "parent_id": story_id},
    )
    assert bug.status_code == 200
    assert bug.json()["parent_id"] == story_id

    invalid_story_parent = client.post(
        "/api/workflow/projects/crypto/changes/centralize-workflow-state-db/tasks",
        json={"type": "story", "title": "Nested story", "parent_id": story_id},
    )
    assert invalid_story_parent.status_code == 400

    task_list = client.get("/api/workflow/projects/crypto/changes/centralize-workflow-state-db/tasks")
    assert task_list.status_code == 200
    assert [item["type"] for item in task_list.json()] == ["story", "bug"]

    change_comment = client.post(
        "/api/workflow/projects/crypto/changes/centralize-workflow-state-db/comments",
        json={"scope": "change", "author": "DEV", "body": "API base pronta"},
    )
    assert change_comment.status_code == 200
    assert change_comment.json()["scope"] == "change"

    task_comment = client.post(
        "/api/workflow/projects/crypto/changes/centralize-workflow-state-db/comments",
        json={"scope": "work_item", "work_item_id": story_id, "author": "DEV", "body": "Story em progresso"},
    )
    assert task_comment.status_code == 200
    assert task_comment.json()["work_item_id"] == story_id

    comment_list = client.get("/api/workflow/projects/crypto/changes/centralize-workflow-state-db/comments")
    assert comment_list.status_code == 200
    assert len(comment_list.json()) == 1

    task_comment_list = client.get(
        f"/api/workflow/projects/crypto/changes/centralize-workflow-state-db/comments?work_item_id={story_id}"
    )
    assert task_comment_list.status_code == 200
    assert len(task_comment_list.json()) == 1

    approval = client.post(
        "/api/workflow/projects/crypto/changes/centralize-workflow-state-db/approvals",
        json={"scope": "change", "gate": "Approval", "state": "approved", "actor": "Alan", "note": "ok"},
    )
    assert approval.status_code == 200
    assert approval.json()["gate"] == "Approval"

    handoff = client.post(
        "/api/workflow/projects/crypto/changes/centralize-workflow-state-db/handoffs",
        json={"scope": "work_item", "work_item_id": story_id, "from_role": "DEV", "to_role": "QA", "summary": "Backend API pronta para validar"},
    )
    assert handoff.status_code == 200
    assert handoff.json()["to_role"] == "QA"

    approvals = client.get("/api/workflow/projects/crypto/changes/centralize-workflow-state-db/approvals")
    assert approvals.status_code == 200
    approval_items = approvals.json()
    assert len(approval_items) >= 1
    assert approval_items[-1]["gate"] == "Approval"

    handoffs = client.get(
        f"/api/workflow/projects/crypto/changes/centralize-workflow-state-db/handoffs?work_item_id={story_id}"
    )
    assert handoffs.status_code == 200
    assert len(handoffs.json()) == 1

    client.app.dependency_overrides.clear()
