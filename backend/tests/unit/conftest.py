"""Unit-test fixtures and helpers.

Database setup is deliberately opt-in.  Pure unit tests must not pay for a
PostgreSQL connection, schema creation, or table truncation.  Tests that use
application/workflow persistence opt in with ``pytest.mark.postgres`` (or the
``postgres_isolation`` fixture), and receive the same deterministic reset that
the old global fixture provided.
"""

from __future__ import annotations

import os
from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine, text
from app.services import binance_realtime_snapshot_store
from database_guard import assert_safe_test_database_url


def _assert_safe_unit_database(database_url: str) -> None:
    assert_safe_test_database_url(database_url, variable_name="DATABASE_URL")


def _qualified_table_name(table) -> str:
    if table.schema:
        return f'"{table.schema}"."{table.name}"'
    return f'"{table.name}"'


def _database_url_from_environment(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is required for PostgreSQL unit-test persistence")
    _assert_safe_unit_database(value)
    return value


def _reset_postgres_state(database_url: str, workflow_database_url: str) -> None:
    """Create required schemas and truncate every known table once per test."""

    # Importing the application database modules creates their engines.  Keep
    # those imports inside the opt-in path so pure tests do not open a DB at
    # collection or fixture setup time.
    from app.database import Base
    from app.workflow_database import WorkflowBase

    database_urls = tuple(dict.fromkeys((database_url, workflow_database_url)))
    for url in database_urls:
        _assert_safe_unit_database(url)

    snapshot_path = binance_realtime_snapshot_store.get_snapshot_path()
    try:
        snapshot_path.unlink(missing_ok=True)
    except Exception:
        pass

    for url in database_urls:
        engine = create_engine(url, pool_pre_ping=True)
        try:
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
                        text(
                            f"TRUNCATE TABLE {_qualified_table_name(table)} "
                            "RESTART IDENTITY CASCADE"
                        )
                    )
        finally:
            engine.dispose()


def _is_postgres_test_requested(request: pytest.FixtureRequest) -> bool:
    return request.node.get_closest_marker("postgres") is not None


@pytest.fixture
def postgres_isolation() -> Iterator[None]:
    """Opt-in fixture for tests that need a deterministic PostgreSQL reset."""

    database_url = _database_url_from_environment("DATABASE_URL")
    workflow_database_url = _database_url_from_environment("WORKFLOW_DATABASE_URL")
    _reset_postgres_state(database_url, workflow_database_url)
    yield


@pytest.fixture
def unit_database_url() -> str:
    """Return the explicitly configured, safe application test database URL."""

    return _database_url_from_environment("DATABASE_URL")


@pytest.fixture
def unit_workflow_database_url() -> str:
    """Return the explicitly configured, safe workflow test database URL."""

    return _database_url_from_environment("WORKFLOW_DATABASE_URL")


@pytest.fixture(autouse=True)
def _isolate_unit_databases(request: pytest.FixtureRequest) -> Iterator[None]:
    """Reset persistence only for tests explicitly marked ``postgres``."""

    if not _is_postgres_test_requested(request):
        yield
        return

    database_url = _database_url_from_environment("DATABASE_URL")
    workflow_database_url = _database_url_from_environment("WORKFLOW_DATABASE_URL")
    _reset_postgres_state(database_url, workflow_database_url)
    yield
