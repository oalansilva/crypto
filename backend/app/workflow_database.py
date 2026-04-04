# file: backend/app/workflow_database.py
"""Workflow state database (Postgres-first).

This module is intentionally separate from `app.database` because the legacy app
DB currently defaults to SQLite and stores backtesting / UI data.

For this change (centralize-workflow-state-db), we introduce a dedicated
*workflow* database that will eventually become the operational source of truth
for changes/stories/bugs/locks/comments.

Enable with:
- WORKFLOW_DB_ENABLED=1
- WORKFLOW_DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/workflow_registry

Runtime now requires PostgreSQL. SQLite is allowed only in explicit test mode.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict

from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import get_settings


WorkflowBase = declarative_base()
_workflow_engines: Dict[str, object] = {}
_workflow_sessionmakers: Dict[str, sessionmaker] = {}


def _enabled() -> bool:
    # Prefer Settings() because backend/.env is loaded by pydantic-settings,
    # but those values are not automatically exported into os.environ.
    settings = get_settings()
    raw = getattr(settings, "workflow_db_enabled", None)
    if raw is None:
        raw = os.getenv("WORKFLOW_DB_ENABLED", "0")
    return str(raw).strip().lower() in {"1", "true", "yes", "on"}


def _allow_sqlite_for_tests() -> bool:
    raw = os.getenv("ALLOW_SQLITE_FOR_TESTS", "").strip().lower()
    if raw in {"1", "true", "yes", "on"}:
        return True
    return any("pytest" in arg for arg in sys.argv)


def _default_sqlite_url() -> str:
    base_dir = Path(__file__).resolve().parent.parent  # backend/
    db_path = base_dir / "workflow.db"
    return f"sqlite:///{db_path}"


def _is_postgres_url(url: str) -> bool:
    normalized = (url or "").strip().lower()
    return normalized.startswith("postgresql://") or normalized.startswith(
        "postgresql+psycopg2://"
    )


def get_workflow_db_url() -> str | None:
    if not _enabled():
        return None

    settings = get_settings()
    url = getattr(settings, "workflow_database_url", None) or os.getenv(
        "WORKFLOW_DATABASE_URL"
    )
    if url:
        if not _is_postgres_url(url) and not _allow_sqlite_for_tests():
            raise RuntimeError(
                "WORKFLOW_DATABASE_URL must point to PostgreSQL. SQLite is no longer supported in runtime."
            )
        return url

    if _allow_sqlite_for_tests():
        return _default_sqlite_url()

    raise RuntimeError(
        "WORKFLOW_DATABASE_URL is required and must point to PostgreSQL. SQLite fallback was removed."
    )


def get_workflow_engine():
    url = get_workflow_db_url()
    if not url:
        return None

    cached = _workflow_engines.get(url)
    if cached is not None:
        return cached

    if url.startswith("sqlite:"):
        engine = create_engine(url, connect_args={"check_same_thread": False})
    else:
        # Postgres / others
        engine = create_engine(url, pool_pre_ping=True)

    _workflow_engines[url] = engine
    return engine


def get_workflow_sessionmaker_for_url(url: str):
    existing = _workflow_sessionmakers.get(url)
    if existing is not None:
        return existing

    engine = get_workflow_engine_for_url(url)
    maker = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    _workflow_sessionmakers[url] = maker
    return maker


def get_workflow_engine_for_url(url: str):
    cached = _workflow_engines.get(url)
    if cached is not None:
        return cached

    if url.startswith("sqlite:"):
        engine = create_engine(url, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(url, pool_pre_ping=True)

    _workflow_engines[url] = engine
    return engine


workflow_engine = get_workflow_engine()

WorkflowSessionLocal = None
if workflow_engine is not None:
    WorkflowSessionLocal = get_workflow_sessionmaker_for_url(str(workflow_engine.url))


def init_workflow_schema_for_url(url: str) -> None:
    """Create workflow tables (idempotent)."""
    workflow_engine = get_workflow_engine_for_url(url)

    # Import models so metadata is populated.
    from app.workflow_models import (  # noqa: F401
        Project,
        Change,
        WorkItem,
        WorkItemDependency,
        AgentRun,
        WorkItemLock,
        WorkflowComment,
        WorkflowApproval,
        WorkflowHandoff,
    )

    WorkflowBase.metadata.create_all(bind=workflow_engine)

    # Lightweight forward-only migration for older workflow DBs.
    with workflow_engine.begin() as conn:
        try:
            is_sqlite = str(workflow_engine.url).startswith("sqlite:")
            if is_sqlite:
                cols = {
                    row[1]
                    for row in conn.execute(text("PRAGMA table_info(wf_changes)"))
                }
            else:
                rows = conn.execute(
                    text(
                        """
                        SELECT column_name
                        FROM information_schema.columns
                        WHERE table_schema = current_schema()
                          AND table_name = 'wf_changes'
                        """
                    )
                )
                cols = {str(row[0]) for row in rows}
            if "description" not in cols:
                conn.execute(
                    text(
                        "ALTER TABLE wf_changes ADD COLUMN description TEXT NOT NULL DEFAULT ''"
                    )
                )
            if "sort_order" not in cols:
                conn.execute(
                    text(
                        "ALTER TABLE wf_changes ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 0"
                    )
                )
            if "card_number" not in cols:
                conn.execute(
                    text("ALTER TABLE wf_changes ADD COLUMN card_number INTEGER")
                )
            if "image_data" not in cols:
                conn.execute(
                    text(
                        "ALTER TABLE wf_changes ADD COLUMN image_data TEXT NOT NULL DEFAULT '[]'"
                    )
                )

            project_cols = None
            try:
                if is_sqlite:
                    project_cols = {
                        row[1]
                        for row in conn.execute(text("PRAGMA table_info(wf_projects)"))
                    }
                else:
                    rows = conn.execute(
                        text(
                            """
                            SELECT column_name
                            FROM information_schema.columns
                            WHERE table_schema = current_schema()
                              AND table_name = 'wf_projects'
                            """
                        )
                    )
                    project_cols = {str(row[0]) for row in rows}
            except Exception:
                pass

            if project_cols is not None:
                if "root_directory" not in project_cols:
                    conn.execute(
                        text(
                            "ALTER TABLE wf_projects ADD COLUMN root_directory VARCHAR(512)"
                        )
                    )
                if "database_url" not in project_cols:
                    conn.execute(
                        text(
                            "ALTER TABLE wf_projects ADD COLUMN database_url VARCHAR(1024)"
                        )
                    )
                if "frontend_url" not in project_cols:
                    conn.execute(
                        text(
                            "ALTER TABLE wf_projects ADD COLUMN frontend_url VARCHAR(512)"
                        )
                    )
                if "backend_url" not in project_cols:
                    conn.execute(
                        text(
                            "ALTER TABLE wf_projects ADD COLUMN backend_url VARCHAR(512)"
                        )
                    )
                if "workflow_database_url" not in project_cols:
                    conn.execute(
                        text(
                            "ALTER TABLE wf_projects ADD COLUMN workflow_database_url VARCHAR(1024)"
                        )
                    )
                if "tech_stack" not in project_cols:
                    conn.execute(
                        text(
                            "ALTER TABLE wf_projects ADD COLUMN tech_stack VARCHAR(512)"
                        )
                    )

            # Lightweight forward-only migration for work_items table
            work_items_cols = None
            try:
                if is_sqlite:
                    work_items_cols = {
                        row[1]
                        for row in conn.execute(
                            text("PRAGMA table_info(wf_work_items)")
                        )
                    }
                else:
                    rows = conn.execute(
                        text(
                            """
                            SELECT column_name
                            FROM information_schema.columns
                            WHERE table_schema = current_schema()
                              AND table_name = 'wf_work_items'
                            """
                        )
                    )
                    work_items_cols = {str(row[0]) for row in rows}
            except Exception:
                pass

            if work_items_cols is not None:
                if "stage_started_at" not in work_items_cols:
                    conn.execute(
                        text(
                            "ALTER TABLE wf_work_items ADD COLUMN stage_started_at TIMESTAMP WITH TIME ZONE"
                        )
                    )
                if "stage_completed_at" not in work_items_cols:
                    conn.execute(
                        text(
                            "ALTER TABLE wf_work_items ADD COLUMN stage_completed_at TIMESTAMP WITH TIME ZONE"
                        )
                    )
                if "last_agent_acted" not in work_items_cols:
                    conn.execute(
                        text(
                            "ALTER TABLE wf_work_items ADD COLUMN last_agent_acted VARCHAR(64)"
                        )
                    )
        except Exception:
            # Best-effort lightweight compatibility shim.
            pass


def init_workflow_schema() -> None:
    url = get_workflow_db_url()
    if not url:
        return
    init_workflow_schema_for_url(url)


def get_project_workflow_db_url(project) -> str:
    url = getattr(project, "workflow_database_url", None)
    if url:
        if not _is_postgres_url(url) and not _allow_sqlite_for_tests():
            raise RuntimeError(
                f"Project '{project.slug}' must use a PostgreSQL workflow database."
            )
        return url

    registry_url = get_workflow_db_url()
    if registry_url and (
        registry_url.startswith("sqlite:")
        or os.getenv("WORKFLOW_ALLOW_SHARED_PROJECT_DB", "").strip().lower()
        in {"1", "true", "yes", "on"}
    ):
        return registry_url

    raise RuntimeError(
        f"Project '{project.slug}' has no workflow_database_url configured."
    )


def get_project_workflow_sessionmaker(project):
    return get_workflow_sessionmaker_for_url(get_project_workflow_db_url(project))


def sync_project_to_workflow_db(project, db_session) -> None:
    from app.workflow_models import Project

    existing = db_session.query(Project).filter(Project.slug == project.slug).first()
    if existing:
        existing.name = project.name
        existing.root_directory = project.root_directory
        existing.database_url = project.database_url
        existing.frontend_url = project.frontend_url
        existing.backend_url = project.backend_url
        existing.workflow_database_url = project.workflow_database_url
        existing.tech_stack = project.tech_stack
        db_session.flush()
        return

    db_session.add(
        Project(
            id=project.id,
            slug=project.slug,
            name=project.name,
            root_directory=project.root_directory,
            database_url=project.database_url,
            frontend_url=project.frontend_url,
            backend_url=project.backend_url,
            workflow_database_url=project.workflow_database_url,
            tech_stack=project.tech_stack,
            created_at=project.created_at,
        )
    )
    db_session.flush()


def bootstrap_project_workflow_db(project) -> None:
    url = get_project_workflow_db_url(project)
    init_workflow_schema_for_url(url)
    SessionLocal = get_project_workflow_sessionmaker(project)
    db = SessionLocal()
    try:
        sync_project_to_workflow_db(project, db)
        db.commit()
    finally:
        db.close()


def get_workflow_db():
    """FastAPI dependency. Raises if workflow DB is disabled."""

    if WorkflowSessionLocal is None:
        raise RuntimeError(
            "Workflow DB is disabled. Set WORKFLOW_DB_ENABLED=1 and configure WORKFLOW_DATABASE_URL."
        )

    db = WorkflowSessionLocal()
    try:
        yield db
    finally:
        db.close()
