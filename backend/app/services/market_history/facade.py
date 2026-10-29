"""Pontos de entrada usados pelos consumidores (card #1118).

* ``get_history_service()``: instância compartilhada do processo.
* ``spec_for_request``: identidade de série a partir de ``asset_id`` ou símbolo.
* ``loader_frame``: leitura no formato do ``IncrementalLoader`` (substitui o
  download direto da CCXT quando ``MARKET_HISTORY_UNIFIED=1``).
"""

from __future__ import annotations

import logging
import threading
from typing import Any

import pandas as pd

from app.services.market_history.cache import ParquetReadCache
from app.services.market_history.model import (
    ADJ_ADJUSTED,
    ADJ_RAW,
    CLASS_ETF,
    CLASS_STOCK,
    HistoryError,
    SeriesSpec,
    crypto_spec,
    equity_spec,
    to_utc,
)
from app.services.market_history.service import HistoryService

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_service: HistoryService | None = None
_cache: ParquetReadCache | None = None


def get_history_service() -> HistoryService:
    global _service
    with _lock:
        if _service is None:
            _service = HistoryService()
        return _service


def get_read_cache() -> ParquetReadCache:
    global _cache
    with _lock:
        if _cache is None:
            _cache = ParquetReadCache()
        return _cache


def set_history_service(
    service: HistoryService | None, cache: ParquetReadCache | None = None
) -> None:
    """Troca as instâncias compartilhadas (testes e workers com engine própria)."""

    global _service, _cache
    with _lock:
        _service = service
        _cache = cache


def is_crypto_symbol(symbol: str) -> bool:
    return "/" in str(symbol or "")


def spec_for_request(
    *,
    timeframe: str,
    asset_id: str | None = None,
    symbol: str | None = None,
    adjustment: str = ADJ_ADJUSTED,
    db: Any = None,
) -> SeriesSpec:
    """Resolve o pedido do cliente numa série.

    Cripto não precisa do catálogo (mantém o contrato do gráfico). Ação e ETF
    exigem o ativo no catálogo do #1117: o ticker da Binance vem de lá.
    """

    adj = ADJ_RAW if str(adjustment).lower() in {"raw", "unadjusted"} else ADJ_ADJUSTED
    asset = str(asset_id or "").strip()
    sym = str(symbol or "").strip()
    if asset.startswith("binance:spot:"):
        return crypto_spec(asset.split(":", 2)[2], timeframe)
    if not asset and is_crypto_symbol(sym):
        return crypto_spec(sym, timeframe)
    if not asset and not sym:
        raise HistoryError("Informe asset_id ou symbol.", code="asset_required")

    from app.models_asset_catalog import AssetCatalog

    own = db is None
    if own:
        from app.database import SessionLocal

        db = SessionLocal()
    try:
        query = db.query(AssetCatalog)
        if asset:
            row = query.filter(AssetCatalog.asset_id == asset).first()
        else:
            row = (
                query.filter(
                    AssetCatalog.symbol == sym.upper(),
                    AssetCatalog.asset_class.in_([CLASS_STOCK, CLASS_ETF]),
                )
                .order_by(AssetCatalog.removed_at.isnot(None), AssetCatalog.asset_id)
                .first()
            )
        if row is None:
            raise HistoryError(
                f"{asset or sym} não está no catálogo da Binance.", code="asset_not_in_catalog"
            )
        if row.asset_class == "crypto":
            return crypto_spec(row.symbol, timeframe)
        return equity_spec(row.asset_id, row.symbol, row.asset_class, timeframe, adj)
    finally:
        if own:
            db.close()


def to_loader_frame(candles: pd.DataFrame) -> pd.DataFrame:
    """Formato do ``IncrementalLoader.fetch_data``: índice ``timestamp_utc``,
    colunas ``timestamp`` (ms), open, high, low, close, volume."""

    if candles is None or candles.empty:
        return pd.DataFrame()
    out = candles[["open", "high", "low", "close", "volume"]].copy()
    index = pd.DatetimeIndex(out.index)
    out.insert(0, "timestamp", index.as_unit("ms").asi8)
    out.index = pd.DatetimeIndex(index.as_unit("us"), name="timestamp_utc")
    return out


def loader_frame(
    symbol: str,
    timeframe: str,
    since: Any = None,
    until: Any = None,
    *,
    read_only: bool = False,
    full_history_if_empty: bool = True,
    allow_large_backfill: bool = False,
) -> pd.DataFrame:
    """Cripto via autoridade: completa o trecho que falta (se não for só leitura) e lê o cache."""

    service = get_history_service()
    cache = get_read_cache()
    series = service.resolve(crypto_spec(symbol, timeframe))
    if not read_only:
        outcome = service.ensure(
            series,
            since,
            until,
            allow_large_backfill=allow_large_backfill,
            full_history_if_empty=full_history_if_empty,
        )
        if outcome.status == "failed":
            logger.warning(
                "Coleta de %s %s falhou (%s); seguindo com o histórico guardado.",
                symbol,
                timeframe,
                outcome.error_code,
            )
    lo = to_utc(since) if since is not None else None
    hi = to_utc(until) if until is not None else None
    return to_loader_frame(cache.read(service, series, lo, hi))
