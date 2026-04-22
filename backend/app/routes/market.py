from __future__ import annotations

import logging
import threading
import time
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi import APIRouter, Query

from app.services.binance_realtime_connector import (
    get_connector_status,
    get_market_latest_prices,
    get_top_pairs,
    is_running,
)

router = APIRouter(prefix="/api/market", tags=["market"])
logger = logging.getLogger(__name__)

_DEFAULT_SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
_CACHE_TTL_SECONDS = 30.0
_TIMEOUT_SECONDS = 5.0
_CACHE_LOCK = threading.Lock()
_PRICE_CACHE: dict[tuple[str, ...], dict[str, Any]] = {}


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _normalize_symbols(raw: str | None) -> tuple[str, ...]:
    items = []
    for piece in str(raw or "").split(","):
        symbol = piece.strip().upper()
        if not symbol or symbol in items:
            continue
        items.append(symbol)
    return tuple(items or _DEFAULT_SYMBOLS)


def _coerce_float(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed == parsed else None


def _to_fallback_payload(raw_prices: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "symbol": item["symbol"],
            "price": item["price"],
            "change_24h_pct": item["change_24h_pct"],
        }
        for item in raw_prices
        if item.get("symbol") is not None and item.get("price") is not None
    ]


def _fallback_price_payload(item: dict[str, Any]) -> dict[str, Any] | None:
    symbol = str(item.get("symbol") or "").strip().upper()
    if not symbol:
        return None
    price = _coerce_float(item.get("price"))
    change_24h_pct = _coerce_float(item.get("change_24h_pct"))
    if price is None:
        return None
    return {"symbol": symbol, "price": price, "change_24h_pct": change_24h_pct}


async def _fetch_binance_prices(symbols: tuple[str, ...]) -> dict[str, Any]:
    # Build symbols param: [\"BTCUSDT\",\"ETHUSDT\"] (no spaces)
    symbols_param = "[" + ",".join(f'\"{s}\"' for s in symbols) + "]"
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

    prices = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        symbol = str(item.get("symbol") or "").strip().upper()
        price = _coerce_float(item.get("lastPrice"))
        change_24h_pct = _coerce_float(item.get("priceChangePercent"))
        normalized = _fallback_price_payload(
            {
                "symbol": symbol,
                "price": price,
                "change_24h_pct": change_24h_pct,
            }
        )
        if normalized is None:
            continue
        prices.append(normalized)

    ordered = []
    for symbol in symbols:
        for item in prices:
            if item["symbol"] == symbol:
                ordered.append(item)
                break
    if not ordered:
        ordered = prices

    return {"prices": ordered, "fetched_at": _utc_now_iso()}


def _read_cache(symbols: tuple[str, ...]) -> dict[str, Any] | None:
    now = time.time()
    with _CACHE_LOCK:
        cached = _PRICE_CACHE.get(symbols)
        if not cached:
            return None
        if float(cached.get("expires_at") or 0) <= now:
            _PRICE_CACHE.pop(symbols, None)
            return None
        return {
            "prices": list(cached.get("prices") or []),
            "fetched_at": cached.get("fetched_at"),
        }


def _write_cache(symbols: tuple[str, ...], payload: dict[str, Any]) -> None:
    with _CACHE_LOCK:
        _PRICE_CACHE[symbols] = {
            "prices": list(payload.get("prices") or []),
            "fetched_at": payload.get("fetched_at"),
            "expires_at": time.time() + _CACHE_TTL_SECONDS,
        }


@router.get("/prices")
async def get_market_prices(
    symbols: str = Query(
        ",".join(_DEFAULT_SYMBOLS),
        description="Comma-separated Binance symbols, e.g. BTCUSDT,ETHUSDT",
    ),
) -> dict[str, Any]:
    normalized_symbols = _normalize_symbols(symbols)
    cached = _read_cache(normalized_symbols)
    if cached is not None:
        return cached

    if is_running():
        try:
            latest, fetched_at, _ = await get_market_latest_prices(list(normalized_symbols))
            if latest:
                fallback_payload = _to_fallback_payload(latest)
                if fallback_payload:
                    _write_cache(normalized_symbols, {"prices": fallback_payload, "fetched_at": fetched_at})
                    return {"prices": fallback_payload, "fetched_at": fetched_at}
        except Exception as exc:
            logger.warning("Failed to read Binance realtime connector prices: %s", exc)

    try:
        payload = await _fetch_binance_prices(normalized_symbols)
    except Exception as exc:
        logger.warning("Failed to fetch Binance prices for %s: %s", normalized_symbols, exc)
        return {"prices": [], "fetched_at": None}

    _write_cache(normalized_symbols, payload)
    return payload


@router.get("/binance/top-pairs")
async def get_binance_top_pairs() -> dict[str, Any]:
    if not is_running():
        return {
            "running": False,
            "pairs": [],
            "count": 0,
            "cached_at": None,
            "is_stale": False,
            "ttl_seconds": 0,
        }
    return await get_top_pairs()


@router.get("/binance/prices/latest")
async def get_binance_realtime_prices(
    symbols: str | None = Query(None, description="Comma-separated Binance symbols"),
) -> dict[str, Any]:
    if not is_running():
        return {"running": False, "prices": [], "fetched_at": None, "is_stale": True}

    requested = None if symbols is None else _normalize_symbols(symbols)
    try:
        prices, fetched_at, is_stale = await get_market_latest_prices(
            list(requested) if requested is not None else None
        )
        return {
            "running": True,
            "prices": _to_fallback_payload(prices),
            "fetched_at": fetched_at,
            "is_stale": is_stale,
        }
    except Exception as exc:
        logger.warning("Failed to get binance realtime prices: %s", exc)
        return {"running": False, "prices": [], "fetched_at": None, "is_stale": True}


@router.get("/binance/status")
async def get_binance_status() -> dict[str, Any]:
    if not is_running():
        return {
            "running": False,
            "service": "binance-realtime-connector",
            "pair_limit": 0,
            "pair_refresh_seconds": 0,
            "price_ttl_seconds": 0,
        }
    return await get_connector_status()
