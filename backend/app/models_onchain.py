# file: backend/app/models_onchain.py
"""SQLAlchemy models for onchain signal tables."""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
)

from app.database import Base


SAO_PAULO_TZ = ZoneInfo("America/Sao_Paulo")


def sao_paulo_now() -> datetime:
    return datetime.now(timezone.utc).astimezone(SAO_PAULO_TZ)


class OnchainSignal(Base):
    """Latest onchain metrics snapshot per token+chain."""

    __tablename__ = "onchain_signals"

    id = Column(String, primary_key=True)  # "{token}_{chain}_{timestamp}"
    token = Column(String, nullable=False, index=True)
    chain = Column(String, nullable=False, index=True)
    tvl = Column(Float, nullable=True)
    active_addresses = Column(Float, nullable=True)
    exchange_flow = Column(Float, nullable=True)  # positive = inflow to exchange (sell pressure), negative = outflow
    github_commits = Column(Integer, nullable=True)
    github_stars = Column(Integer, nullable=True)
    github_prs = Column(Integer, nullable=True)
    github_issues = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=sao_paulo_now)
    updated_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_onchain_signals_token_chain", "token", "chain"),
        Index("ix_onchain_signals_created_at", "created_at"),
    )


class OnchainSignalHistory(Base):
    """Historical record of generated onchain signals with signal type and confidence."""

    __tablename__ = "onchain_signals_history"

    id = Column(String, primary_key=True)
    token = Column(String, nullable=False, index=True)
    chain = Column(String, nullable=False, index=True)
    signal_type = Column(String, nullable=False)  # BUY, SELL, HOLD
    confidence = Column(Integer, nullable=False)
    breakdown = Column(Text, nullable=True)  # JSON string with metric contributions
    status = Column(String, nullable=False, default="ativo", index=True)  # ativo, disparado, expirado, cancelado

    # Raw metrics at signal time
    tvl = Column(Float, nullable=True)
    active_addresses = Column(Float, nullable=True)
    exchange_flow = Column(Float, nullable=True)
    github_commits = Column(Integer, nullable=True)
    github_stars = Column(Integer, nullable=True)
    github_prs = Column(Integer, nullable=True)
    github_issues = Column(Integer, nullable=True)

    # Outcome tracking
    price_at_signal = Column(Float, nullable=True)
    price_after_1h = Column(Float, nullable=True)
    price_after_4h = Column(Float, nullable=True)
    price_after_24h = Column(Float, nullable=True)
    outcome_1h = Column(String, nullable=True)  # win, loss, neutral
    outcome_4h = Column(String, nullable=True)
    outcome_24h = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, default=sao_paulo_now, index=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)
    archived = Column(String, default="no", index=True)

    __table_args__ = (
        Index("ix_onchain_signals_history_token_chain", "token", "chain"),
        Index("ix_onchain_signals_history_signal_type", "signal_type"),
        Index("ix_onchain_signals_history_status_created", "status", "created_at"),
    )
