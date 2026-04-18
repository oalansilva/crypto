from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import Column, DateTime, Float, Index, Integer, String, Text

from app.database import Base

SAO_PAULO_TZ = ZoneInfo("America/Sao_Paulo")


def sao_paulo_now() -> datetime:
    return datetime.now(timezone.utc).astimezone(SAO_PAULO_TZ)


class SignalHistory(Base):
    __tablename__ = "signal_history"

    id = Column(String, primary_key=True)
    asset = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False)  # BUY, SELL, HOLD
    confidence = Column(Integer, nullable=False)
    target_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    indicators = Column(Text, nullable=True)  # JSON string
    created_at = Column(
        DateTime(timezone=True), nullable=False, index=True, default=lambda: sao_paulo_now()
    )
    risk_profile = Column(String, nullable=False)
    status = Column(
        String, nullable=False, default="ativo", index=True
    )  # ativo, disparado, expirado, cancelado

    # PnL fields
    entry_price = Column(Float, nullable=True)
    exit_price = Column(Float, nullable=True)
    quantity = Column(Float, nullable=True)
    pnl = Column(Float, nullable=True)  # (exit_price - entry_price) * quantity

    # Metadata
    trigger_price = Column(Float, nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)
    archived = Column(String, default="no", index=True)  # yes/no

    # Multi-tenant isolation
    user_id = Column(String, nullable=True)  # UUID do usuário, NULL para dados legados

    __table_args__ = (
        Index("ix_signal_history_asset_created", "asset", "created_at"),
        Index("ix_signal_history_status_created", "status", "created_at"),
    )
