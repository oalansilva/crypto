"""Unit-test fixtures and helpers.

Keep a clean PostgreSQL state between unit tests to avoid flaky
``UniqueViolation`` failures across fixtures that use shared default DB URLs.
"""

from __future__ import annotations

import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from app.services import binance_realtime_snapshot_store

from app.database import Base
from app.workflow_database import WorkflowBase

_TEST_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@127.0.0.1:5432/postgres",
)

_FORBIDDEN_DATABASE_NAMES = {
    "crypto_app",
    "crypto_workflow",
    "workflow",
    "workflow_registry",
    "kanban_app",
    "kanban_registry",
    "kanban_workflow",
}


def _assert_safe_unit_database(database_url: str) -> None:
    url = make_url(database_url)
    backend = url.get_backend_name()
    if backend == "sqlite":
        return

    database_name = (url.database or "").lower()
    explicitly_test_db = (
        database_name == "postgres"
        or database_name.startswith("test_")
        or database_name.endswith("_test")
        or database_name.endswith("_tests")
        or database_name.endswith("_testing")
    )

    if database_name in _FORBIDDEN_DATABASE_NAMES or not explicitly_test_db:
        raise RuntimeError(
            "Refusing to isolate unit tests against a non-test database "
            f"({database_name or '<empty>'}). Set DATABASE_URL to a dedicated test database."
        )


def _qualified_table_name(table) -> str:
    if table.schema:
        return f'"{table.schema}"."{table.name}"'
    return f'"{table.name}"'


@pytest.fixture(autouse=True)
def _isolate_unit_databases():
    _assert_safe_unit_database(_TEST_DATABASE_URL)
    engine = create_engine(_TEST_DATABASE_URL, pool_pre_ping=True)
    try:
        snapshot_path = binance_realtime_snapshot_store.get_snapshot_path()
        try:
            snapshot_path.unlink(missing_ok=True)
        except Exception:
            pass

        Base.metadata.create_all(bind=engine)
        WorkflowBase.metadata.create_all(bind=engine)

        seen: set[tuple[str | None, str]] = set()
        with engine.begin() as connection:
            for table in (
                *Base.metadata.sorted_tables,
                *WorkflowBase.metadata.sorted_tables,
            ):
                key = (table.schema, table.name)
                if key in seen:
                    continue
                seen.add(key)
                connection.execute(
                    text(f"TRUNCATE TABLE {_qualified_table_name(table)} RESTART IDENTITY CASCADE")
                )
    finally:
        engine.dispose()
