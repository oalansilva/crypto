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



def test_workflow_kanban_tasks_adapter_returns_checklist_shape_from_work_items():
    client = _build_client()

    try:
        project = client.post("/api/workflow/projects", json={"slug": "crypto", "name": "Crypto"})
        assert project.status_code == 200

        change = client.post(
            "/api/workflow/projects/crypto/changes",
            json={"change_id": "centralize-workflow-state-db", "title": "Workflow DB", "status": "in_progress"},
        )
        assert change.status_code == 200

        story = client.post(
            "/api/workflow/projects/crypto/changes/centralize-workflow-state-db/tasks",
            json={"type": "story", "title": "Move Kanban tasks to workflow DB", "priority": 10, "state": "active"},
        )
        assert story.status_code == 200
        story_id = story.json()["id"]

        child_bug = client.post(
            "/api/workflow/projects/crypto/changes/centralize-workflow-state-db/tasks",
            json={"type": "bug", "title": "Preserve legacy checklist response shape", "parent_id": story_id, "state": "done"},
        )
        assert child_bug.status_code == 200
        child_bug_id = child_bug.json()["id"]

        root_bug = client.post(
            "/api/workflow/projects/crypto/changes/centralize-workflow-state-db/tasks",
            json={"type": "bug", "title": "Handle orphan bug card", "priority": 1, "state": "queued"},
        )
        assert root_bug.status_code == 200
        root_bug_id = root_bug.json()["id"]

        res = client.get(
            "/api/workflow/kanban/changes/centralize-workflow-state-db/tasks?project_slug=crypto"
        )
        assert res.status_code == 200, res.text
        payload = res.json()

        assert payload["change_id"] == "centralize-workflow-state-db"
        assert payload["path"] == "openspec/changes/centralize-workflow-state-db/tasks.md"
        assert [section["title"] for section in payload["sections"]] == ["Tasks"]

        items = payload["sections"][0]["items"]
        assert [item["title"] for item in items] == ["Story", "Bug"]
        assert [item["text"] for item in items] == [
            "Move Kanban tasks to workflow DB",
            "Handle orphan bug card",
        ]

        assert items[0]["checked"] is False
        assert items[0]["code"] == story_id
        assert items[0]["children"] == [
            {
                "text": "Preserve legacy checklist response shape",
                "checked": True,
                "code": child_bug_id,
                "title": "Bug",
                "children": [],
            }
        ]

        assert items[1]["checked"] is False
        assert items[1]["code"] == root_bug_id
        assert items[1]["children"] == []
    finally:
        client.app.dependency_overrides.clear()
