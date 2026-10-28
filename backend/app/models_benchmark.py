"""Comparação com referência e coluna extra do Decidir (card #1123, decisões 4, 5 e 10).

``benchmark_comparisons`` guarda cada comparação uma vez (números, período comum, o que ficou de
fora, moedas e amostra congelada da referência). O dono é um resultado de rodada (``result``), um
favorito (``favorite``) ou um candidato da Descoberta (``discovery_result``, célula da coluna extra).
Abrir ou exportar lê daqui; nada recalcula na leitura.

``discovery_reference_columns`` guarda a escolha da coluna extra por varredura e por usuário: uma
linha por referência escolhida, no máximo uma ativa por ``(sweep_id, actor)``.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, Column, DateTime, Index, Integer, String, Text, text

from app.database import Base

OWNER_KINDS = ("result", "favorite", "discovery_result")
COMPARISON_STATUSES = ("valid", "insufficient")
COLUMN_STATUSES = ("collecting", "computing", "done", "failed")
COLUMN_RUNNING = ("collecting", "computing")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class BenchmarkComparison(Base):
    __tablename__ = "benchmark_comparisons"

    id = Column(String(36), primary_key=True)
    user_id = Column(String, nullable=True)
    favorite_id = Column(Integer, nullable=True)
    owner_kind = Column(String(24), nullable=False)
    result_id = Column(String(64), nullable=True)
    column_id = Column(String(36), nullable=True)
    created_at = Column(DateTime, nullable=False, default=_utcnow)
    status = Column(String(16), nullable=False)
    payload = Column(JSON, nullable=False)

    __table_args__ = (
        Index("ix_benchmark_comparisons_user", "user_id"),
        Index("ix_benchmark_comparisons_favorite", "favorite_id"),
        Index("ix_benchmark_comparisons_column", "column_id", "result_id"),
        Index("ix_benchmark_comparisons_created", "created_at"),
    )


class DiscoveryReferenceColumn(Base):
    __tablename__ = "discovery_reference_columns"

    id = Column(String(36), primary_key=True)
    sweep_id = Column(String(64), nullable=False)
    actor = Column(String(128), nullable=False)
    reference = Column(JSON, nullable=False)
    reference_snapshot_id = Column(String(40), nullable=True)
    status = Column(String(16), nullable=False, default="collecting")
    done = Column(Integer, nullable=False, default=0)
    total = Column(Integer, nullable=False, default=0)
    error = Column(Text, nullable=True)
    active = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=_utcnow)
    completed_at = Column(DateTime, nullable=True)
    deactivated_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_discovery_reference_columns_sweep_actor", "sweep_id", "actor"),
        Index(
            "uq_discovery_reference_columns_active",
            "sweep_id",
            "actor",
            unique=True,
            postgresql_where=text("active"),
        ),
    )
