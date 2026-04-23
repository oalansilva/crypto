"""Unit-test fixtures and helpers.

Keep a clean PostgreSQL state between unit tests to avoid flaky
``UniqueViolation`` failures across fixtures that use shared default DB URLs.
"""

from __future__ import annotations

import os

import pytest
from sqlalchemy import create_engine, text
from app.services import binance_realtime_snapshot_store

from app.database import Base
from app.workflow_database import WorkflowBase

_TEST_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@127.0.0.1:5432/postgres",
)


def _qualified_table_name(table) -> str:
    if table.schema:
        return f'"{table.schema}"."{table.name}"'
    return f'"{table.name}"'


@pytest.fixture(autouse=True)
def _isolate_unit_databases():
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
