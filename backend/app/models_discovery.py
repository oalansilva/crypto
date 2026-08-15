"""Discovery sweep persistence models (card #469).

Descoberta sistemática de estratégias swing: varredura template × símbolo ×
timeframe com leaderboard. A spec vive em
openspec/changes/card-469-varredura-backtest/specs/.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

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


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def strategy_identity_key(*, structure_version: str, canonical: str) -> str:
    """Hash canônico da identidade de estratégia (estrutura + params efetivos
    quantizados + símbolo + timeframe + direção; janela NÃO participa)."""
    payload = json.dumps(
        {"structure_version": structure_version, "canonical": canonical},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode()).hexdigest()


class DiscoverySweep(Base):
    __tablename__ = "discovery_sweeps"

    id = Column(String(64), primary_key=True)
    actor = Column(String(128), nullable=False)
    state = Column(String(24), nullable=False, default="pending")
    idempotency_key = Column(String(64), nullable=False)
    payload_hash = Column(String(64), nullable=False)
    snapshot_token = Column(String(64), nullable=False)
    snapshot_hash = Column(String(64), nullable=False)
    snapshot = Column(JSON, nullable=False)
    total = Column(Integer, nullable=False)
    succeeded = Column(Integer, nullable=False, default=0)
    failed = Column(Integer, nullable=False, default=0)
    skipped = Column(Integer, nullable=False, default=0)
    processed = Column(Integer, nullable=False, default=0)
    terminal_reason = Column(String(64), nullable=True)
    terminal_code = Column(String(64), nullable=True)
    cancellation_requested = Column(Boolean, nullable=False, default=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=_utcnow)
    updated_at = Column(DateTime, nullable=False, default=_utcnow)

    __table_args__ = (
        UniqueConstraint("actor", "idempotency_key", name="uq_discovery_sweeps_actor_key"),
        Index("ix_discovery_sweeps_state", "state"),
        Index("ix_discovery_sweeps_actor", "actor"),
    )


class DiscoveryCombination(Base):
    __tablename__ = "discovery_combinations"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    sweep_id = Column(String(64), nullable=False)
    template_id = Column(String(64), nullable=False)
    symbol = Column(String(32), nullable=False)
    timeframe = Column(String(8), nullable=False)
    direction = Column(String(8), nullable=False)
    state = Column(String(24), nullable=False, default="pending")
    attempts = Column(Integer, nullable=False, default=0)
    lease_owner = Column(String(128), nullable=True)
    lease_expires_at = Column(DateTime, nullable=True)
    result_id = Column(String(64), nullable=True)
    created_at = Column(DateTime, nullable=False, default=_utcnow)
    updated_at = Column(DateTime, nullable=False, default=_utcnow)

    __table_args__ = (
        UniqueConstraint(
            "sweep_id",
            "template_id",
            "symbol",
            "timeframe",
            "direction",
            name="uq_discovery_combinations_key",
        ),
        Index("ix_discovery_combinations_sweep_state", "sweep_id", "state"),
        Index("ix_discovery_combinations_lease", "lease_owner", "lease_expires_at"),
    )


class DiscoveryResult(Base):
    __tablename__ = "discovery_results"

    id = Column(String(64), primary_key=True)
    sweep_id = Column(String(64), nullable=False)
    combination_id = Column(BigInteger, nullable=False)
    template_id = Column(String(64), nullable=False)
    template_version = Column(String(32), nullable=True)
    symbol = Column(String(32), nullable=False)
    timeframe = Column(String(8), nullable=False)
    direction = Column(String(8), nullable=False)
    parameters = Column(JSON, nullable=False)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    candle_source = Column(String(32), nullable=True)
    candle_version = Column(String(32), nullable=True)
    expected_candles = Column(Integer, nullable=True)
    observed_valid_candles = Column(Integer, nullable=True)
    coverage = Column(Float, nullable=True)
    fees_slippage = Column(JSON, nullable=True)
    metrics = Column(JSON, nullable=False)
    trades_count = Column(Integer, nullable=True)
    win_rate = Column(Float, nullable=True)
    sharpe_ratio = Column(Float, nullable=True)
    profit_factor = Column(Float, nullable=True)
    max_drawdown = Column(Float, nullable=True)
    calmar_ratio = Column(Float, nullable=True)
    cagr = Column(Float, nullable=True)
    benchmark_cagr = Column(Float, nullable=True)
    delta_cagr_vs_bh = Column(Float, nullable=True)
    strategy_identity_key = Column(String(64), nullable=False)
    evidence_fingerprint = Column(String(64), nullable=False)
    eligibility = Column(String(16), nullable=False, default="eligible")
    eligibility_reason = Column(String(128), nullable=True)
    dedup_state = Column(String(32), nullable=False, default="unique")
    dedup_reference = Column(String(64), nullable=True)
    created_at = Column(DateTime, nullable=False, default=_utcnow)
    updated_at = Column(DateTime, nullable=False, default=_utcnow)

    __table_args__ = (
        UniqueConstraint("combination_id", name="uq_discovery_results_combination"),
        UniqueConstraint(
            "strategy_identity_key",
            "sweep_id",
            name="uq_discovery_results_identity_sweep",
        ),
        Index("ix_discovery_results_sweep", "sweep_id"),
        Index("ix_discovery_results_identity", "strategy_identity_key"),
        Index("ix_discovery_results_rank", "sweep_id", "calmar_ratio", "trades_count"),
    )


class DiscoveryDedupEvidence(Base):
    __tablename__ = "discovery_dedup_evidence"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    result_id = Column(String(64), nullable=False)
    classification = Column(String(32), nullable=False)
    matched_reference = Column(String(64), nullable=True)
    structure_version = Column(String(32), nullable=True)
    quantum_version = Column(String(32), nullable=True)
    compared_dimensions = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=_utcnow)

    __table_args__ = (Index("ix_discovery_dedup_evidence_result", "result_id"),)


class DiscoveryOutbox(Base):
    __tablename__ = "discovery_outbox"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    sweep_id = Column(String(64), nullable=False)
    generation = Column(Integer, nullable=False, default=1)
    state = Column(String(24), nullable=False, default="pending")
    attempts = Column(Integer, nullable=False, default=0)
    acked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=_utcnow)
    updated_at = Column(DateTime, nullable=False, default=_utcnow)

    __table_args__ = (
        Index("ix_discovery_outbox_state", "state", "created_at"),
        Index("ix_discovery_outbox_sweep", "sweep_id"),
    )


class DiscoveryIdempotency(Base):
    """Registro de idempotência de promoções (actor, idempotency_key) com
    payload_hash e identidade da resposta (favorite id)."""

    __tablename__ = "discovery_idempotency"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    actor = Column(String(128), nullable=False)
    idempotency_key = Column(String(64), nullable=False)
    payload_hash = Column(String(64), nullable=False)
    resource_type = Column(String(32), nullable=False, default="promotion")
    resource_id = Column(String(128), nullable=False)
    created_at = Column(DateTime, nullable=False, default=_utcnow)

    __table_args__ = (
        UniqueConstraint("actor", "idempotency_key", name="uq_discovery_idempotency_actor_key"),
        Index("ix_discovery_idempotency_actor", "actor"),
    )
