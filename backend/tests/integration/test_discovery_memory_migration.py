"""Actual additive Alembic operations over a private legacy PostgreSQL schema."""

import importlib.util
import os
from pathlib import Path
import uuid

from alembic.migration import MigrationContext
from alembic.operations import Operations
import pytest
from sqlalchemy import create_engine, text


def test_additive_migration_conservative_backfill_and_rollback_retains_evidence():
    url = os.environ["DATABASE_URL"]
    assert "card-1093-integration" in url or os.getenv("GITHUB_ACTIONS") == "true"
    engine = create_engine(url)
    schema = "migration_1093_" + uuid.uuid4().hex[:12]
    path = Path(__file__).parents[2] / "alembic/versions/20261013_0001_discovery_attempt_ledger.py"
    spec = importlib.util.spec_from_file_location("migration_1093", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA {schema}"))
        conn.execute(text(f"SET LOCAL search_path TO {schema}"))
        conn.execute(
            text(
                "CREATE TABLE discovery_sweeps (id varchar PRIMARY KEY, state varchar, terminal_reason varchar, terminal_code varchar, completed_at timestamp)"
            )
        )
        conn.execute(
            text(
                "CREATE TABLE discovery_combinations (id bigint PRIMARY KEY, sweep_id varchar, state varchar, attempts int, lease_expires_at timestamp)"
            )
        )
        conn.execute(text("CREATE TABLE discovery_results (candle_version varchar(32))"))
        conn.execute(
            text(
                "INSERT INTO discovery_sweeps (id,state) VALUES ('active','running'),('exhausted','running'),('paused','paused')"
            )
        )
        conn.execute(
            text(
                "INSERT INTO discovery_combinations (id,sweep_id,state,attempts,lease_expires_at) VALUES (1,'active','running',2,CURRENT_TIMESTAMP+INTERVAL '5 minutes'),(2,'exhausted','pending',7,NULL),(3,'exhausted','pending',0,NULL),(4,'paused','pending',3,NULL)"
            )
        )
        context = MigrationContext.configure(conn)
        with Operations.context(context):
            module.upgrade()
            with pytest.raises(RuntimeError, match="retains"):
                module.downgrade()
        rows = conn.execute(
            text(
                "SELECT id,state,attempts,last_failure_code,lease_generation FROM discovery_combinations ORDER BY id"
            )
        ).all()
        assert rows == [
            (1, "running", 2, "legacy_interruption", 0),
            (2, "failed", 7, "legacy_budget_exhausted", 0),
            (3, "skipped", 0, None, 0),
            (4, "failed", 3, "legacy_budget_exhausted", 0),
        ]
        assert conn.execute(
            text(
                "SELECT lease_expires_at <= CURRENT_TIMESTAMP FROM discovery_combinations WHERE id=1"
            )
        ).scalar()
        assert (
            conn.execute(text("SELECT state FROM discovery_sweeps WHERE id='paused'")).scalar()
            == "paused"
        )
        assert (
            conn.execute(
                text("SELECT terminal_code FROM discovery_sweeps WHERE id='exhausted'")
            ).scalar()
            == "resource_recovery_exhausted"
        )
        assert conn.execute(text("SELECT count(*) FROM discovery_attempts")).scalar() == 0
        # Test-only schema cleanup; never the shared DEV/PROD schema.
        conn.execute(text(f"DROP SCHEMA {schema} CASCADE"))
    engine.dispose()
