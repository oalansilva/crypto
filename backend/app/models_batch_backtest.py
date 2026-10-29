"""Estado durável do lote de backtests (card #1120, decisão 10).

``batch_backtest_jobs`` guarda uma linha por lote (corpo do pedido, plano, estado, pedidos de
pausa e de encerramento, totais e tempos) e ``batch_backtest_items`` uma linha por ativo, na
ordem da seleção. Sem prazo: o lote pausado espera enquanto o usuário não retomar ou encerrar.
O Redis fica só como fila do Celery.
"""

from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)

from app.database import Base

JOB_ACTIVE_STATUSES = ("queued", "running", "retrying", "paused")
JOB_FINAL_STATUSES = ("completed", "cancelled", "failed")

ITEM_FINAL_STATES = (
    "success",
    "success_daily",
    "insufficient",
    "rejected",
    "failed",
    "skipped",
    "out",
    "not_run",
)


class BatchBacktestJob(Base):
    __tablename__ = "batch_backtest_jobs"

    job_id = Column(String(64), primary_key=True)
    user_id = Column(String, nullable=True)
    task_id = Column(String(128), nullable=True)
    # queued | running | retrying | paused | cancelled | completed | failed
    status = Column(String(16), nullable=False, default="queued")
    payload = Column(JSON, nullable=True)
    plan = Column(JSON, nullable=True)
    total = Column(Integer, nullable=False, default=0)
    processed = Column(Integer, nullable=False, default=0)
    succeeded = Column(Integer, nullable=False, default=0)
    failed = Column(Integer, nullable=False, default=0)
    skipped = Column(Integer, nullable=False, default=0)
    errors = Column(JSON, nullable=True)
    skipped_reasons = Column(JSON, nullable=True)
    pause_requested = Column(Boolean, nullable=False, default=False)
    cancel_requested = Column(Boolean, nullable=False, default=False)
    retry_count = Column(Integer, nullable=False, default=0)
    last_error = Column(Text, nullable=True)
    dead_lettered = Column(Boolean, nullable=False, default=False)
    current_symbol = Column(String(64), nullable=True)
    current_stage = Column(String(120), nullable=True)
    elapsed_sec = Column(Float, nullable=False, default=0.0)
    estimated_remaining_sec = Column(Float, nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    __table_args__ = (Index("ix_batch_backtest_jobs_user_status", "user_id", "status"),)


class BatchBacktestItem(Base):
    __tablename__ = "batch_backtest_items"

    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True)
    job_id = Column(String(64), nullable=False)
    position = Column(Integer, nullable=False)
    symbol = Column(String(64), nullable=False)
    asset_class = Column(String(16), nullable=True)
    currency = Column(String(16), nullable=True)
    # queued | collecting | optimizing | success | success_daily | insufficient | rejected |
    # failed | skipped | out | not_run
    state = Column(String(16), nullable=False, default="queued")
    reason = Column(Text, nullable=True)
    progress = Column(String(160), nullable=True)
    favorite_id = Column(Integer, nullable=True)
    execution = Column(JSON, nullable=True)
    snapshot_id = Column(String(64), nullable=True)
    extra = Column(JSON, nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint("job_id", "position", name="uq_batch_backtest_items_job_position"),
        Index("ix_batch_backtest_items_job", "job_id"),
    )
