"""Tests for multi-project Kanban functionality."""

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


def test_projects_api_list_and_create():
    """Test GET and POST /api/workflow/projects."""
    client = _build_client()

    # List projects (should be empty initially)
    response = client.get("/api/workflow/projects")
    assert response.status_code == 200
    assert response.json() == []

    # Create first project
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
    assert p1["root_directory"] == "/srv/projects/crypto"
    assert p1["frontend_url"] == "https://crypto.example.com"
    assert p1["backend_url"] == "https://api.crypto.example.com"
    assert p1["workflow_database_url"] == "postgresql://wf-crypto"
    assert p1["tech_stack"] == "FastAPI, React"
    assert "id" in p1

    # List projects again (should have one)
    response = client.get("/api/workflow/projects")
    assert response.status_code == 200
    projects = response.json()
    assert len(projects) == 1
    assert projects[0]["slug"] == "crypto"
    assert projects[0]["root_directory"] == "/srv/projects/crypto"

    # Create second project
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
    assert p2["workflow_database_url"] == "postgresql://wf-bot"

    # List projects (should have two)
    response = client.get("/api/workflow/projects")
    assert response.status_code == 200
    projects = response.json()
    assert len(projects) == 2
    slugs = [p["slug"] for p in projects]
    assert "crypto" in slugs
    assert "trading-bot" in slugs

    # Idempotent: creating same slug returns existing
    project1_again = client.post(
        "/api/workflow/projects", json={"slug": "crypto", "name": "Different Name"}
    )
    assert project1_again.status_code == 200
    assert project1_again.json()["id"] == p1["id"]
    assert project1_again.json()["root_directory"] == "/srv/projects/crypto"

    client.app.dependency_overrides.clear()


def test_kanban_filter_by_project():
    """Test that Kanban endpoints respect project_slug parameter."""
    client = _build_client()

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

    client.app.dependency_overrides.clear()


def test_projects_can_store_independent_runtime_metadata():
    client = _build_client()

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

    listed = client.get("/api/workflow/projects")
    assert listed.status_code == 200
    erp = next(project for project in listed.json() if project["slug"] == "erp")
    assert erp["root_directory"] == "/srv/projects/erp"
    assert erp["frontend_url"] == "https://erp.example.com"
    assert erp["backend_url"] == "https://api.erp.example.com"
    assert erp["workflow_database_url"] == "postgresql://wf-erp"
    assert erp["tech_stack"] == "Laravel, Vue, MariaDB"

    client.app.dependency_overrides.clear()


def test_changes_api_per_project():
    """Test that change API endpoints work per project."""
    client = _build_client()

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

    client.app.dependency_overrides.clear()


def test_work_items_per_project():
    """Test that work items are isolated per project."""
    client = _build_client()

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

    client.app.dependency_overrides.clear()
