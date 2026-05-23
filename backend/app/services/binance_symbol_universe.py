from __future__ import annotations

import logging
import os

import httpx

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


def _apply_limit(symbols: list[str]) -> list[str]:
    limit = _symbol_limit()
    if limit is None:
        return symbols
    return symbols[:limit]


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
    raw_symbols = os.getenv("MARKET_OHLCV_SYMBOLS", "").strip()
    if raw_symbols and raw_symbols.lower() not in _ALL_SYMBOL_SENTINELS:
        return _apply_limit(_normalize_explicit_symbols(raw_symbols))

    try:
        symbols = _fetch_trading_spot_usdt_symbols()
    except Exception as exchange_info_exc:
        try:
            symbols = ExchangeService().fetch_binance_symbols()
        except Exception as exc:
            logger.warning(
                "Could not resolve Binance symbol universe; using fallback symbols: %s",
                exc,
            )
            return _apply_limit([*FALLBACK_BINANCE_USDT_SYMBOLS])
        logger.warning(
            "Could not resolve Binance exchangeInfo symbol universe; using cached exchange service symbols: %s",
            exchange_info_exc,
        )

    filtered = [
        symbol.strip().upper()
        for symbol in symbols
        if str(symbol or "").strip().upper().endswith("/USDT")
        and not is_excluded_symbol(str(symbol or ""))
    ]
    deduped = list(dict.fromkeys(filtered))
    return _apply_limit(deduped or [*FALLBACK_BINANCE_USDT_SYMBOLS])
