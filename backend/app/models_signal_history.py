from sqlalchemy import Column, String, Float, Integer, DateTime, Text, Index
from app.database import Base
from datetime import datetime


class SignalHistory(Base):
    __tablename__ = "signal_history"

    id = Column(String, primary_key=True)
    asset = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False)  # BUY, SELL, HOLD
    confidence = Column(Integer, nullable=False)
    target_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    indicators = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, nullable=False, index=True, default=datetime.utcnow)
    risk_profile = Column(String, nullable=False)
    status = Column(String, nullable=False, default="ativo", index=True)  # ativo, disparado, expirado, cancelado

    # PnL fields
    entry_price = Column(Float, nullable=True)
    exit_price = Column(Float, nullable=True)
    quantity = Column(Float, nullable=True)
    pnl = Column(Float, nullable=True)  # (exit_price - entry_price) * quantity

    # Metadata
    trigger_price = Column(Float, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    archived = Column(String, default="no", index=True)  # yes/no

    __table_args__ = (
        Index("ix_signal_history_asset_created", "asset", "created_at"),
        Index("ix_signal_history_status_created", "status", "created_at"),
    )
