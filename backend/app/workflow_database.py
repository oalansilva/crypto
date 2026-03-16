# file: backend/app/workflow_database.py
"""Workflow state database (Postgres-first).

This module is intentionally separate from `app.database` because the legacy app
DB currently defaults to SQLite and stores backtesting / UI data.

For this change (centralize-workflow-state-db), we introduce a dedicated
*workflow* database that will eventually become the operational source of truth
for changes/stories/bugs/locks/comments.

Enable with:
- WORKFLOW_DB_ENABLED=1
- WORKFLOW_DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/workflow

Local/dev fallback (when enabled but URL not provided): a SQLite file
`backend/workflow.db`.
"""

from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import get_settings


WorkflowBase = declarative_base()


def _enabled() -> bool:
    # Prefer Settings() because backend/.env is loaded by pydantic-settings,
    # but those values are not automatically exported into os.environ.
    settings = get_settings()
    raw = getattr(settings, "workflow_db_enabled", None)
    if raw is None:
        raw = os.getenv("WORKFLOW_DB_ENABLED", "0")
    return str(raw).strip().lower() in {"1", "true", "yes", "on"}


def _default_sqlite_url() -> str:
    base_dir = Path(__file__).resolve().parent.parent  # backend/
    db_path = base_dir / "workflow.db"
    return f"sqlite:///{db_path}"


def get_workflow_db_url() -> str | None:
    if not _enabled():
        return None

    settings = get_settings()
    url = getattr(settings, "workflow_database_url", None) or os.getenv("WORKFLOW_DATABASE_URL")
    return url or _default_sqlite_url()


def get_workflow_engine():
    url = get_workflow_db_url()
    if not url:
        return None

    if url.startswith("sqlite:"):
        return create_engine(url, connect_args={"check_same_thread": False})

    # Postgres / others
    return create_engine(url, pool_pre_ping=True)


workflow_engine = get_workflow_engine()

WorkflowSessionLocal = None
if workflow_engine is not None:
    WorkflowSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=workflow_engine)


def init_workflow_schema() -> None:
    """Create workflow tables (idempotent)."""

    if workflow_engine is None:
        return

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
                cols = {row[1] for row in conn.execute(text("PRAGMA table_info(wf_changes)"))}
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
                conn.execute(text("ALTER TABLE wf_changes ADD COLUMN description TEXT NOT NULL DEFAULT ''"))
            if "sort_order" not in cols:
                conn.execute(text("ALTER TABLE wf_changes ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 0"))
            if "card_number" not in cols:
                conn.execute(text("ALTER TABLE wf_changes ADD COLUMN card_number INTEGER"))
            if "image_data" not in cols:
                conn.execute(text("ALTER TABLE wf_changes ADD COLUMN image_data TEXT NOT NULL DEFAULT '[]'"))
        except Exception:
            # Best-effort lightweight compatibility shim.
            pass


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
