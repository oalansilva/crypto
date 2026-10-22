from __future__ import annotations

import logging
import os

import httpx

from app.symbols_config import is_excluded_symbol

logger = logging.getLogger(__name__)

# Só ordenação: a janela de ingestão por rodada fixa estes pares na frente quando
# existem. Nunca é universo: sem catálogo e sem exchangeInfo a rodada não roda.
INGESTION_PRIORITY_SYMBOLS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "BNB/USDT",
    "XRP/USDT",
]

_ALL_SYMBOL_SENTINELS = {"*", "all", "binance:all", "binance_all"}
BINANCE_EXCHANGE_INFO_URL = "https://api.binance.com/api/v3/exchangeInfo"


def _normalize_explicit_symbols(raw_symbols: str) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for raw in raw_symbols.split(","):
        symbol = str(raw or "").strip().upper()
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        normalized.append(symbol)
    return normalized


def _symbol_limit() -> int | None:
    raw = os.getenv("MARKET_OHLCV_SYMBOL_LIMIT", "").strip()
    if not raw:
        return None
    try:
        parsed = int(float(raw))
    except ValueError:
        return None
    return parsed if parsed > 0 else None


def _catalog_tradable_symbols() -> list[str] | None:
    """Cripto negociáveis do catálogo persistido (#1117), ou None se indisponível."""
    try:
        from app.services.asset_catalog_service import list_tradable_crypto_symbols

        return list_tradable_crypto_symbols()
    except Exception as exc:
        logger.warning("Catálogo de ativos indisponível para a ingestão: %s", exc)
        return None


def resolve_binance_ohlcv_symbol_universe() -> list[str]:
    """Universo spot USDT negociável (sem limite por rodada).

    Lê o catálogo persistido; sem catálogo, tenta ``exchangeInfo``. Sem os dois,
    registra a falha e devolve lista vazia: a rodada não roda e nenhuma lista
    fixa de poucos pares a substitui.
    """
    raw_symbols = os.getenv("MARKET_OHLCV_SYMBOLS", "").strip()
    if raw_symbols and raw_symbols.lower() not in _ALL_SYMBOL_SENTINELS:
        return _normalize_explicit_symbols(raw_symbols)

    symbols = _catalog_tradable_symbols()
    if not symbols:
        try:
            symbols = _fetch_trading_spot_usdt_symbols()
        except Exception as exc:
            logger.error(
                "Universo de ingestão indisponível: catálogo sem lista de cripto e "
                "exchangeInfo falhou (%s). A rodada não roda.",
                exc,
            )
            return []

    filtered = [
        symbol.strip().upper()
        for symbol in symbols
        if str(symbol or "").strip().upper().endswith("/USDT")
        and not is_excluded_symbol(str(symbol or ""))
    ]
    deduped = list(dict.fromkeys(filtered))
    if not deduped:
        logger.error("Universo de ingestão vazio depois dos filtros. A rodada não roda.")
    return deduped


def slice_symbol_universe_for_ingestion_run(
    universe: list[str],
    *,
    priority_symbols: list[str] | None = None,
    limit: int | None,
    offset: int,
) -> tuple[list[str], int]:
    """Rotate through the full universe when a per-run cap is configured."""
    if not universe:
        return [], 0

    ordered = list(universe)
    if priority_symbols:
        priority_set = {symbol.strip().upper() for symbol in priority_symbols if symbol}
        front = [symbol for symbol in ordered if symbol in priority_set]
        tail = [symbol for symbol in ordered if symbol not in priority_set]
        ordered = front + tail

    if limit is None or limit <= 0 or limit >= len(ordered):
        return ordered, 0

    batch: list[str] = []
    index = offset % len(ordered)
    while len(batch) < limit:
        batch.append(ordered[index])
        index = (index + 1) % len(ordered)
    next_offset = (offset + limit) % len(ordered)
    return batch, next_offset


def _apply_limit(symbols: list[str]) -> list[str]:
    """Cap the universe size while keeping major pairs in the window.

    Binance spot USDT lists are alphabetical, so a naive ``symbols[:limit]``
    drops BTC/ETH/etc. when the limit is small. Majors from
    ``INGESTION_PRIORITY_SYMBOLS`` are pinned first when present (ordering only).
    """
    limit = _symbol_limit()
    if limit is None:
        return symbols
    present = set(symbols)
    priority = [symbol for symbol in INGESTION_PRIORITY_SYMBOLS if symbol in present]
    priority_set = set(priority)
    remainder = [symbol for symbol in symbols if symbol not in priority_set]
    return (priority + remainder)[:limit]


def _fetch_trading_spot_usdt_symbols() -> list[str]:
    timeout = httpx.Timeout(20.0)
    with httpx.Client(timeout=timeout) as client:
        response = client.get(BINANCE_EXCHANGE_INFO_URL)
        response.raise_for_status()
        payload = response.json()

    resolved: list[str] = []
    for item in payload.get("symbols", []):
        if item.get("status") != "TRADING":
            continue
        if item.get("quoteAsset") != "USDT":
            continue
        if item.get("isSpotTradingAllowed") is not True:
            continue
        base = str(item.get("baseAsset") or "").strip().upper()
        if not base:
            continue
        resolved.append(f"{base}/USDT")
    return sorted(dict.fromkeys(resolved))


def resolve_binance_ohlcv_symbols() -> list[str]:
    return _apply_limit(resolve_binance_ohlcv_symbol_universe())
