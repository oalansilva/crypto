"""Catálogo persistido de ativos Binance (card #1117).

``asset_catalog`` guarda uma linha por ativo (cripto spot USDT, ações e ETFs),
com identidade estável, estado de negociação e resumo de histórico.
``asset_catalog_refresh`` guarda uma linha por tentativa de atualização de cada
grupo de origem (``crypto`` e ``equity``) com contagens verificáveis.
"""

from __future__ import annotations

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    Index,
    JSON,
    String,
    Text,
)

from app.database import Base


class AssetCatalog(Base):
    __tablename__ = "asset_catalog"

    # binance:spot:<BASE>/USDT  |  binance:equity:<ac>
    asset_id = Column(String(96), primary_key=True)
    asset_class = Column(String(16), nullable=False)  # crypto | stock | etf
    symbol = Column(String(64), nullable=False)
    name = Column(String(300), nullable=False, default="")
    binance_id = Column(String(96), nullable=False, default="")
    state = Column(String(24), nullable=False)
    state_reason = Column(String(300), nullable=True)
    info_note = Column(String(300), nullable=True)
    search_key = Column(Text, nullable=False, default="")
    first_seen_at = Column(DateTime(timezone=True), nullable=False)
    last_seen_at = Column(DateTime(timezone=True), nullable=False)
    removed_at = Column(DateTime(timezone=True), nullable=True)
    history_from = Column(DateTime(timezone=True), nullable=True)
    history_to = Column(DateTime(timezone=True), nullable=True)
    history_checked_at = Column(DateTime(timezone=True), nullable=True)
    extra = Column(JSON, nullable=True)

    __table_args__ = (
        Index("ix_asset_catalog_class_symbol", "asset_class", "symbol"),
        Index("ix_asset_catalog_symbol", "symbol"),
        Index("ix_asset_catalog_class_state", "asset_class", "state"),
    )


class AssetCatalogRefresh(Base):
    __tablename__ = "asset_catalog_refresh"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    catalog_group = Column(String(16), nullable=False)  # crypto | equity
    trigger = Column(String(16), nullable=False, default="scheduled")
    started_at = Column(DateTime(timezone=True), nullable=False)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(16), nullable=False)  # ok | error
    error_code = Column(String(64), nullable=True)
    error_message = Column(Text, nullable=True)
    counts = Column(JSON, nullable=True)

    __table_args__ = (
        Index("ix_asset_catalog_refresh_group_started", "catalog_group", "started_at"),
    )
