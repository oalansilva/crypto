from __future__ import annotations

import json
import logging
import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

import httpx
from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/market", tags=["market"])
logger = logging.getLogger(__name__)

_DEFAULT_SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
_CACHE_TTL_SECONDS = 30.0
_TIMEOUT_SECONDS = 5.0
_CACHE_LOCK = threading.Lock()
_PRICE_CACHE: Dict[Tuple[str, ...], Dict[str, Any]] = {}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _normalize_symbols(raw: str | None) -> Tuple[str, ...]:
    items = []
    for piece in str(raw or "").split(","):
        symbol = piece.strip().upper()
        if not symbol:
            continue
        if symbol not in items:
            items.append(symbol)
    return tuple(items or _DEFAULT_SYMBOLS)


def _coerce_float(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed == parsed else None


async def _fetch_binance_prices(symbols: Tuple[str, ...]) -> Dict[str, Any]:
    # Build symbols param: ["BTCUSDT","ETHUSDT"] without spaces (Binance is strict about spaces)
    symbols_param = "[" + ",".join(f'"{s}"' for s in symbols) + "]"
    params = {"symbols": symbols_param}
    timeout = httpx.Timeout(_TIMEOUT_SECONDS)

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.get("https://api.binance.com/api/v3/ticker/24hr", params=params)
        response.raise_for_status()
        payload = response.json()

    if isinstance(payload, dict):
        payload = [payload]
    if not isinstance(payload, list):
        raise ValueError("Unexpected Binance payload format")

    prices: List[Dict[str, Any]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        symbol = str(item.get("symbol") or "").strip().upper()
        if not symbol:
            continue
        price = _coerce_float(item.get("lastPrice"))
        change_24h_pct = _coerce_float(item.get("priceChangePercent"))
        if price is None or change_24h_pct is None:
            continue
        prices.append(
            {
                "symbol": symbol,
                "price": price,
                "change_24h_pct": change_24h_pct,
            }
        )

    prices.sort(key=lambda item: symbols.index(item["symbol"]) if item["symbol"] in symbols else len(symbols))
    return {"prices": prices, "fetched_at": _utc_now_iso()}


def _read_cache(symbols: Tuple[str, ...]) -> Dict[str, Any] | None:
    now = time.time()
    with _CACHE_LOCK:
        cached = _PRICE_CACHE.get(symbols)
        if not cached:
            return None
        if float(cached.get("expires_at") or 0) <= now:
            _PRICE_CACHE.pop(symbols, None)
            return None
        return {"prices": list(cached.get("prices") or []), "fetched_at": cached.get("fetched_at")}


def _write_cache(symbols: Tuple[str, ...], payload: Dict[str, Any]) -> None:
    with _CACHE_LOCK:
        _PRICE_CACHE[symbols] = {
            "prices": list(payload.get("prices") or []),
            "fetched_at": payload.get("fetched_at"),
            "expires_at": time.time() + _CACHE_TTL_SECONDS,
        }


@router.get("/prices")
async def get_market_prices(
    symbols: str = Query(",".join(_DEFAULT_SYMBOLS), description="Comma-separated Binance symbols, e.g. BTCUSDT,ETHUSDT"),
) -> Dict[str, Any]:
    normalized_symbols = _normalize_symbols(symbols)
    cached = _read_cache(normalized_symbols)
    if cached is not None:
        return cached

    try:
        payload = await _fetch_binance_prices(normalized_symbols)
    except Exception as exc:
        logger.warning("Failed to fetch Binance prices for %s: %s", normalized_symbols, exc)
        return {"prices": [], "fetched_at": None}

    _write_cache(normalized_symbols, payload)
    return payload
