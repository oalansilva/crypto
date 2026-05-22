from __future__ import annotations

import logging
import os

from app.services.exchange_service import ExchangeService
from app.symbols_config import is_excluded_symbol

logger = logging.getLogger(__name__)

FALLBACK_BINANCE_USDT_SYMBOLS = [
    "BTC/USDT",
    "ETH/USDT",
    "SOL/USDT",
    "BNB/USDT",
    "XRP/USDT",
]

_ALL_SYMBOL_SENTINELS = {"*", "all", "binance:all", "binance_all"}


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


def _apply_limit(symbols: list[str]) -> list[str]:
    limit = _symbol_limit()
    if limit is None:
        return symbols
    return symbols[:limit]


def resolve_binance_ohlcv_symbols() -> list[str]:
    raw_symbols = os.getenv("MARKET_OHLCV_SYMBOLS", "").strip()
    if raw_symbols and raw_symbols.lower() not in _ALL_SYMBOL_SENTINELS:
        return _apply_limit(_normalize_explicit_symbols(raw_symbols))

    try:
        symbols = ExchangeService().fetch_binance_symbols()
    except Exception as exc:
        logger.warning(
            "Could not resolve Binance symbol universe; using fallback symbols: %s",
            exc,
        )
        return _apply_limit([*FALLBACK_BINANCE_USDT_SYMBOLS])

    filtered = [
        symbol.strip().upper()
        for symbol in symbols
        if str(symbol or "").strip().upper().endswith("/USDT")
        and not is_excluded_symbol(str(symbol or ""))
    ]
    deduped = list(dict.fromkeys(filtered))
    return _apply_limit(deduped or [*FALLBACK_BINANCE_USDT_SYMBOLS])
