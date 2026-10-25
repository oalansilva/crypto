"""Estado durável do lote de backtests: lotes e itens por ativo (#1120)."""

from alembic import op
import sqlalchemy as sa

revision = "20261024_0001"
down_revision = "20261023_0001"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(name)


def upgrade():
    # O app também cria as tabelas na subida (create_all); a migração é idempotente.
    if not _has_table("batch_backtest_jobs"):
        op.create_table(
            "batch_backtest_jobs",
            sa.Column("job_id", sa.String(64), primary_key=True),
            sa.Column("user_id", sa.String()),
            sa.Column("task_id", sa.String(128)),
            sa.Column("status", sa.String(16), nullable=False),
            sa.Column("payload", sa.JSON()),
            sa.Column("plan", sa.JSON()),
            sa.Column("total", sa.Integer(), nullable=False),
            sa.Column("processed", sa.Integer(), nullable=False),
            sa.Column("succeeded", sa.Integer(), nullable=False),
            sa.Column("failed", sa.Integer(), nullable=False),
            sa.Column("skipped", sa.Integer(), nullable=False),
            sa.Column("errors", sa.JSON()),
            sa.Column("skipped_reasons", sa.JSON()),
            sa.Column("pause_requested", sa.Boolean(), nullable=False),
            sa.Column("cancel_requested", sa.Boolean(), nullable=False),
            sa.Column("retry_count", sa.Integer(), nullable=False),
            sa.Column("last_error", sa.Text()),
            sa.Column("dead_lettered", sa.Boolean(), nullable=False),
            sa.Column("current_symbol", sa.String(64)),
            sa.Column("current_stage", sa.String(120)),
            sa.Column("elapsed_sec", sa.Float(), nullable=False),
            sa.Column("estimated_remaining_sec", sa.Float()),
            sa.Column("started_at", sa.DateTime()),
            sa.Column("finished_at", sa.DateTime()),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
        )
        op.create_index(
            "ix_batch_backtest_jobs_user_status", "batch_backtest_jobs", ["user_id", "status"]
        )
    if not _has_table("batch_backtest_items"):
        op.create_table(
            "batch_backtest_items",
            sa.Column(
                "id",
                sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
                primary_key=True,
                autoincrement=True,
            ),
            sa.Column("job_id", sa.String(64), nullable=False),
            sa.Column("position", sa.Integer(), nullable=False),
            sa.Column("symbol", sa.String(64), nullable=False),
            sa.Column("asset_class", sa.String(16)),
            sa.Column("currency", sa.String(16)),
            sa.Column("state", sa.String(16), nullable=False),
            sa.Column("reason", sa.Text()),
            sa.Column("progress", sa.String(160)),
            sa.Column("favorite_id", sa.Integer()),
            sa.Column("execution", sa.JSON()),
            sa.Column("snapshot_id", sa.String(64)),
            sa.Column("extra", sa.JSON()),
            sa.Column("started_at", sa.DateTime()),
            sa.Column("finished_at", sa.DateTime()),
            sa.UniqueConstraint("job_id", "position", name="uq_batch_backtest_items_job_position"),
        )
        op.create_index("ix_batch_backtest_items_job", "batch_backtest_items", ["job_id"])


def downgrade():
    # O lote pausado é estado do usuário: o rollback deixa as tabelas sem uso, sem apagá-las.
    raise RuntimeError("Conservative rollback retains the durable batch backtest state")
