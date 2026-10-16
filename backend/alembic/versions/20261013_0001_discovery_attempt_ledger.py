"""Add durable Discovery attempts and environment resource circuit (#1093)."""

from alembic import op
import sqlalchemy as sa

revision = "20261013_0001"
down_revision = "20261002_0001"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "discovery_results",
        "candle_version",
        existing_type=sa.String(32),
        type_=sa.String(64),
        existing_nullable=True,
    )
    for name, type_, default in (
        ("lease_generation", sa.Integer(), "0"),
        ("heartbeat_at", sa.DateTime(), None),
        ("progress_at", sa.DateTime(), None),
        ("next_attempt_at", sa.DateTime(), None),
        ("last_failure_code", sa.String(64), None),
        ("input_snapshot", sa.JSON(), None),
    ):
        op.add_column(
            "discovery_combinations",
            sa.Column(name, type_, nullable=default is None, server_default=default),
        )
    op.create_table(
        "discovery_attempts",
        sa.Column("combination_id", sa.BigInteger(), primary_key=True),
        sa.Column("attempt_seq", sa.Integer(), primary_key=True),
        sa.Column("owner", sa.String(128), nullable=False),
        sa.Column("generation", sa.Integer(), nullable=False),
        sa.Column("state", sa.String(24), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("heartbeat_at", sa.DateTime(), nullable=False),
        sa.Column("progress_at", sa.DateTime(), nullable=False),
        sa.Column("finished_at", sa.DateTime()),
        sa.Column("failure_code", sa.String(64)),
        sa.Column("profile", sa.JSON(), nullable=False),
        sa.Column("counters", sa.JSON(), nullable=False),
        sa.Column("supervisor_pid", sa.Integer()),
        sa.Column("supervisor_start", sa.String(64)),
    )
    op.create_table(
        "discovery_resource_circuits",
        sa.Column("environment", sa.String(32), primary_key=True),
        sa.Column("failures", sa.JSON(), nullable=False),
        sa.Column("opened_at", sa.DateTime()),
        sa.Column("acknowledged_at", sa.DateTime()),
        sa.Column("acknowledgements", sa.JSON(), nullable=False),
    )
    # Active legacy attempts have consumed a slot, but cannot have a trusted owner.
    # Do not manufacture successful history or reset their existing attempts.
    op.execute(
        "UPDATE discovery_combinations SET lease_expires_at = CURRENT_TIMESTAMP, "
        "last_failure_code = 'legacy_interruption' WHERE state = 'running'"
    )
    op.execute(
        "UPDATE discovery_combinations SET state = 'failed', "
        "last_failure_code = 'legacy_budget_exhausted' "
        "WHERE state = 'pending' AND attempts >= 3"
    )
    op.execute(
        "UPDATE discovery_sweeps SET state = 'failed', terminal_reason = 'operational_failure', "
        "terminal_code = 'resource_recovery_exhausted', completed_at = CURRENT_TIMESTAMP "
        "WHERE state = 'running' AND id IN (SELECT sweep_id FROM discovery_combinations "
        "WHERE last_failure_code = 'legacy_budget_exhausted')"
    )
    op.execute(
        "UPDATE discovery_combinations SET state = 'skipped' WHERE state = 'pending' "
        "AND sweep_id IN (SELECT id FROM discovery_sweeps WHERE terminal_code = 'resource_recovery_exhausted')"
    )
    op.create_index(
        "ix_discovery_combinations_retry", "discovery_combinations", ["state", "next_attempt_at"]
    )


def downgrade():
    # Durable evidence must survive rollback of the application.
    raise RuntimeError("Conservative rollback retains the Discovery attempt ledger")
