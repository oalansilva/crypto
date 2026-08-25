"""Tests for multi-project Kanban functionality."""

from __future__ import annotations

from contextlib import contextmanager

import app.workflow_database as workflow_database
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import get_db
from app.main import app
from app.middleware.authMiddleware import get_current_admin, get_current_user
from app.services.workflow_auth import WorkflowActor, get_workflow_actor
from app.workflow_database import WorkflowBase, get_workflow_db
from app.workflow_models import Project

TEST_ACTOR = WorkflowActor(
    user_id="11111111-1111-1111-1111-111111111111", email="tester@example.com"
)
REDACTED_KEYS = ("database_url", "workflow_database_url", "root_directory")
ADMIN_USER_ID = "22222222-2222-2222-2222-222222222222"


def _reset_workflow_engine_cache():
    for cached_engine in workflow_database._workflow_engines.values():
        try:
            cached_engine.dispose()
        except Exception:
            pass
    workflow_database._workflow_engines.clear()
    workflow_database._workflow_sessionmakers.clear()
    workflow_database.WorkflowSessionLocal = None


def _assert_redacted_project(payload: dict) -> None:
    for key in REDACTED_KEYS:
        assert key not in payload
    assert "id" in payload
    assert "slug" in payload
    assert "name" in payload


def _assert_body_without_secrets(response) -> None:
    body = response.text.lower()
    assert "database_url" not in body
    assert "workflow_database_url" not in body
    assert "root_directory" not in body
    assert "postgresql://" not in body


@contextmanager
def _build_client(*, as_admin: bool = False):
    _reset_workflow_engine_cache()
    engine = create_engine(
        "postgresql://postgres:postgres@127.0.0.1:5432/postgres",
    )
    WorkflowBase.metadata.drop_all(bind=engine)
    WorkflowBase.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_workflow_db] = override_get_db
    app.dependency_overrides[get_workflow_actor] = lambda: TEST_ACTOR
    if as_admin:
        app.dependency_overrides[get_current_admin] = lambda: ADMIN_USER_ID
    client = TestClient(app)
    try:
        yield client, SessionLocal
    finally:
        client.close()
        app.dependency_overrides.clear()
        engine.dispose()
        _reset_workflow_engine_cache()


def test_anonymous_get_projects_is_401_without_secrets():
    with _build_client() as (client, _):
        response = client.get("/api/workflow/projects")
        assert response.status_code == 401
        _assert_body_without_secrets(response)


def test_authenticated_non_admin_get_projects_is_403_without_secrets():
    class _NonAdmin:
        email = "user@example.com"

    class _FakeDb:
        def query(self, *_args, **_kwargs):
            return self

        def filter(self, *_args, **_kwargs):
            return self

        def first(self):
            return _NonAdmin()

    with _build_client() as (client, _):
        assert get_current_admin not in app.dependency_overrides
        app.dependency_overrides[get_current_user] = lambda: TEST_ACTOR.user_id
        app.dependency_overrides[get_db] = lambda: _FakeDb()
        response = client.get("/api/workflow/projects")
        assert response.status_code == 403
        _assert_body_without_secrets(response)


def test_projects_api_list_and_create():
    """Test GET and POST /api/workflow/projects."""
    with _build_client(as_admin=True) as (client, SessionLocal):
        response = client.get("/api/workflow/projects")
        assert response.status_code == 200
        assert response.json() == []

        project1 = client.post(
            "/api/workflow/projects",
            json={
                "slug": "crypto",
                "name": "Crypto Project",
                "root_directory": "/srv/projects/crypto",
                "frontend_url": "https://crypto.example.com",
                "backend_url": "https://api.crypto.example.com",
                "workflow_database_url": "postgresql://wf-crypto",
                "tech_stack": "FastAPI, React",
            },
        )
        assert project1.status_code == 200
        p1 = project1.json()
        assert p1["slug"] == "crypto"
        assert p1["name"] == "Crypto Project"
        assert p1["frontend_url"] == "https://crypto.example.com"
        assert p1["backend_url"] == "https://api.crypto.example.com"
        assert p1["tech_stack"] == "FastAPI, React"
        _assert_redacted_project(p1)

        db = SessionLocal()
        try:
            stored = db.query(Project).filter(Project.slug == "crypto").one()
            assert stored.root_directory == "/srv/projects/crypto"
            assert stored.workflow_database_url == "postgresql://wf-crypto"
        finally:
            db.close()

        response = client.get("/api/workflow/projects")
        assert response.status_code == 200
        projects = response.json()
        assert len(projects) == 1
        assert projects[0]["slug"] == "crypto"
        _assert_redacted_project(projects[0])

        project2 = client.post(
            "/api/workflow/projects",
            json={
                "slug": "trading-bot",
                "name": "Trading Bot",
                "root_directory": "/srv/projects/trading-bot",
                "frontend_url": "https://bot.example.com",
                "backend_url": "https://api.bot.example.com",
                "workflow_database_url": "postgresql://wf-bot",
                "tech_stack": "Node.js, Next.js, PostgreSQL",
            },
        )
        assert project2.status_code == 200
        p2 = project2.json()
        assert p2["slug"] == "trading-bot"
        assert p2["name"] == "Trading Bot"
        _assert_redacted_project(p2)

        response = client.get("/api/workflow/projects")
        assert response.status_code == 200
        projects = response.json()
        assert len(projects) == 2
        slugs = [p["slug"] for p in projects]
        assert "crypto" in slugs
        assert "trading-bot" in slugs

        project1_again = client.post(
            "/api/workflow/projects", json={"slug": "crypto", "name": "Different Name"}
        )
        assert project1_again.status_code == 200
        assert project1_again.json()["id"] == p1["id"]
        _assert_redacted_project(project1_again.json())


def test_kanban_filter_by_project():
    """Test that Kanban endpoints respect project_slug parameter."""
    with _build_client() as (client, _):
        # Create projects
        client.post("/api/workflow/projects", json={"slug": "crypto", "name": "Crypto"})
        client.post("/api/workflow/projects", json={"slug": "trading-bot", "name": "Trading Bot"})

        # Create changes in different projects
        client.post(
            "/api/workflow/projects/crypto/changes",
            json={"change_id": "change-crypto-1", "title": "Crypto Change 1"},
        )
        client.post(
            "/api/workflow/projects/crypto/changes",
            json={"change_id": "change-crypto-2", "title": "Crypto Change 2"},
        )
        client.post(
            "/api/workflow/projects/trading-bot/changes",
            json={"change_id": "change-bot-1", "title": "Bot Change 1"},
        )

        # List kanban changes filtered by project
        crypto_kanban = client.get("/api/workflow/kanban/changes?project_slug=crypto")
        assert crypto_kanban.status_code == 200
        crypto_items = crypto_kanban.json()["items"]
        crypto_change_ids = [item["id"] for item in crypto_items]
        assert "change-crypto-1" in crypto_change_ids
        assert "change-crypto-2" in crypto_change_ids
        assert "change-bot-1" not in crypto_change_ids

        trading_bot_kanban = client.get("/api/workflow/kanban/changes?project_slug=trading-bot")
        assert trading_bot_kanban.status_code == 200
        bot_items = trading_bot_kanban.json()["items"]
        bot_change_ids = [item["id"] for item in bot_items]
        assert "change-bot-1" in bot_change_ids
        assert "change-crypto-1" not in bot_change_ids

        # Default project (first created)
        default_kanban = client.get("/api/workflow/kanban/changes")
        assert default_kanban.status_code == 200
        default_items = default_kanban.json()["items"]
        default_change_ids = [item["id"] for item in default_items]
        # Default should be the first project (crypto)
        assert "change-crypto-1" in default_change_ids


def test_projects_can_store_independent_runtime_metadata():
    with _build_client(as_admin=True) as (client, SessionLocal):
        created = client.post(
            "/api/workflow/projects",
            json={
                "slug": "erp",
                "name": "ERP",
                "root_directory": "/srv/projects/erp",
                "frontend_url": "https://erp.example.com",
                "backend_url": "https://api.erp.example.com",
                "workflow_database_url": "postgresql://wf-erp",
                "tech_stack": "Laravel, Vue, MariaDB",
            },
        )
        assert created.status_code == 200
        _assert_redacted_project(created.json())

        listed = client.get("/api/workflow/projects")
        assert listed.status_code == 200
        erp = next(project for project in listed.json() if project["slug"] == "erp")
        assert erp["frontend_url"] == "https://erp.example.com"
        assert erp["backend_url"] == "https://api.erp.example.com"
        assert erp["tech_stack"] == "Laravel, Vue, MariaDB"
        _assert_redacted_project(erp)

        db = SessionLocal()
        try:
            stored = db.query(Project).filter(Project.slug == "erp").one()
            assert stored.root_directory == "/srv/projects/erp"
            assert stored.workflow_database_url == "postgresql://wf-erp"
        finally:
            db.close()


def test_changes_api_per_project():
    """Test that change API endpoints work per project."""
    with _build_client() as (client, _):
        # Create projects
        client.post("/api/workflow/projects", json={"slug": "project-a", "name": "Project A"})
        client.post("/api/workflow/projects", json={"slug": "project-b", "name": "Project B"})

        # Create change in project-a
        change_a = client.post(
            "/api/workflow/projects/project-a/changes",
            json={"change_id": "change-in-a", "title": "Change in A"},
        )
        assert change_a.status_code == 200

        # Try to get same change_id from project-b (should not exist)
        change_b = client.get("/api/workflow/projects/project-b/changes/change-in-a")
        assert change_b.status_code == 404

        # Get from correct project
        change_a_get = client.get("/api/workflow/projects/project-a/changes/change-in-a")
        assert change_a_get.status_code == 200
        assert change_a_get.json()["change_id"] == "change-in-a"

        # Create change in project-b with same change_id (should work - different project)
        change_b_create = client.post(
            "/api/workflow/projects/project-b/changes",
            json={"change_id": "change-in-a", "title": "Change in B with same ID"},
        )
        assert change_b_create.status_code == 200
        assert change_b_create.json()["project_id"] != change_a.json()["project_id"]


def test_work_items_per_project():
    """Test that work items are isolated per project."""
    with _build_client() as (client, _):
        # Create projects
        client.post("/api/workflow/projects", json={"slug": "proj-1", "name": "Project 1"})
        client.post("/api/workflow/projects", json={"slug": "proj-2", "name": "Project 2"})

        # Create changes in both projects
        client.post(
            "/api/workflow/projects/proj-1/changes",
            json={"change_id": "change-1", "title": "Change 1"},
        )
        client.post(
            "/api/workflow/projects/proj-2/changes",
            json={"change_id": "change-2", "title": "Change 2"},
        )

        # Add task to change-1
        task = client.post(
            "/api/workflow/projects/proj-1/changes/change-1/tasks",
            json={"type": "story", "title": "Story in Project 1"},
        )
        assert task.status_code == 200

        # Get tasks for change-1 (should have the story)
        tasks_1 = client.get("/api/workflow/projects/proj-1/changes/change-1/tasks")
        assert tasks_1.status_code == 200
        assert len(tasks_1.json()) == 1
        assert tasks_1.json()[0]["title"] == "Story in Project 1"

        # Get tasks for change-2 (should be empty - no tasks created)
        tasks_2 = client.get("/api/workflow/projects/proj-2/changes/change-2/tasks")
        assert tasks_2.status_code == 200
        assert len(tasks_2.json()) == 0
