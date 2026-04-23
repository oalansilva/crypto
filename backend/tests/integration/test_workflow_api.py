from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.workflow_database import WorkflowBase, get_workflow_db


def _build_client():
    workflow_database_url = "postgresql://postgres:postgres@127.0.0.1:5432/postgres"
    engine = create_engine(
        workflow_database_url,
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
    return client, workflow_database_url


def _close_client(client: TestClient) -> None:
    client.close()
    client.app.dependency_overrides.clear()
    client.engine.dispose()  # type: ignore[attr-defined]


def test_workflow_api_supports_changes_tasks_comments_approvals_and_handoffs():
    client, workflow_database_url = _build_client()
    project_slug = f"crypto-{uuid4().hex[:8]}"
    change_id = f"centralize-workflow-state-db-{uuid4().hex[:8]}"

    project = client.post(
        "/api/workflow/projects",
        json={
            "slug": project_slug,
            "name": "Crypto",
            "workflow_database_url": workflow_database_url,
        },
    )
    assert project.status_code == 200

    change = client.post(
        f"/api/workflow/projects/{project_slug}/changes",
        json={
            "change_id": change_id,
            "title": "Workflow DB",
            "description": "Initial workflow runtime cutover",
            "status": "in_progress",
        },
    )
    assert change.status_code == 200
    change_body = change.json()
    assert change_body["change_id"] == change_id
    assert change_body["description"] == "Initial workflow runtime cutover"

    updated = client.patch(
        f"/api/workflow/projects/{project_slug}/changes/{change_id}",
        json={
            "status": "DEV",
            "title": "Workflow DB APIs",
            "description": "APIs and Kanban compat",
        },
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "DEV"
    assert updated.json()["description"] == "APIs and Kanban compat"

    story = client.post(
        f"/api/workflow/projects/{project_slug}/changes/{change_id}/tasks",
        json={
            "type": "story",
            "title": "Add workflow APIs",
            "description": "Expose DB-backed runtime state",
        },
    )
    assert story.status_code == 200
    story_id = story.json()["id"]

    bug = client.post(
        f"/api/workflow/projects/{project_slug}/changes/{change_id}/tasks",
        json={"type": "bug", "title": "Fix approval filter", "parent_id": story_id},
    )
    assert bug.status_code == 200
    assert bug.json()["parent_id"] == story_id

    invalid_story_parent = client.post(
        f"/api/workflow/projects/{project_slug}/changes/{change_id}/tasks",
        json={"type": "story", "title": "Nested story", "parent_id": story_id},
    )
    assert invalid_story_parent.status_code == 400

    task_list = client.get(f"/api/workflow/projects/{project_slug}/changes/{change_id}/tasks")
    assert task_list.status_code == 200
    assert [item["type"] for item in task_list.json()] == ["story", "bug"]

    change_comment = client.post(
        f"/api/workflow/projects/{project_slug}/changes/{change_id}/comments",
        json={"scope": "change", "author": "DEV", "body": "API base pronta"},
    )
    assert change_comment.status_code == 200
    assert change_comment.json()["scope"] == "change"

    task_comment = client.post(
        f"/api/workflow/projects/{project_slug}/changes/{change_id}/comments",
        json={
            "scope": "work_item",
            "work_item_id": story_id,
            "author": "DEV",
            "body": "Story em progresso",
        },
    )
    assert task_comment.status_code == 200
    assert task_comment.json()["work_item_id"] == story_id

    comment_list = client.get(f"/api/workflow/projects/{project_slug}/changes/{change_id}/comments")
    assert comment_list.status_code == 200
    assert len(comment_list.json()) == 1

    task_comment_list = client.get(
        f"/api/workflow/projects/{project_slug}/changes/{change_id}/comments?work_item_id={story_id}"
    )
    assert task_comment_list.status_code == 200
    assert len(task_comment_list.json()) == 1

    approval = client.post(
        f"/api/workflow/projects/{project_slug}/changes/{change_id}/approvals",
        json={
            "scope": "change",
            "gate": "Approval",
            "state": "approved",
            "actor": "Alan",
            "note": "ok",
        },
    )
    assert approval.status_code == 200
    assert approval.json()["gate"] == "Approval"

    handoff = client.post(
        f"/api/workflow/projects/{project_slug}/changes/{change_id}/handoffs",
        json={
            "scope": "work_item",
            "work_item_id": story_id,
            "from_role": "DEV",
            "to_role": "QA",
            "summary": "Backend API pronta para validar",
        },
    )
    assert handoff.status_code == 200
    assert handoff.json()["to_role"] == "QA"

    approvals = client.get(f"/api/workflow/projects/{project_slug}/changes/{change_id}/approvals")
    assert approvals.status_code == 200
    approval_items = approvals.json()
    assert len(approval_items) >= 1
    assert approval_items[-1]["gate"] == "Approval"

    handoffs = client.get(
        f"/api/workflow/projects/{project_slug}/changes/{change_id}/handoffs?work_item_id={story_id}"
    )
    assert handoffs.status_code == 200
    assert len(handoffs.json()) == 1

    _close_client(client)
