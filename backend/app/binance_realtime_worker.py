from __future__ import annotations

import asyncio
import logging
import re
import signal
import time
from contextlib import suppress
from datetime import datetime, timezone
from typing import Any

import httpx

from app.config import get_settings
from app.services.binance_realtime_snapshot_store import write_snapshot

logger = logging.getLogger(__name__)
_BINANCE_SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{4,32}$")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _timestamp_to_iso(value: float | None) -> str | None:
    if not value:
        return None
    return datetime.fromtimestamp(value, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def _to_float(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed == parsed else None


def _setting(settings: Any, name: str, default: Any) -> Any:
    value = getattr(settings, name, default)
    return default if value is None else value


def _is_supported_binance_symbol(symbol: str) -> bool:
    normalized = str(symbol or "").strip().upper()
    if not normalized.endswith("USDT"):
        return False
    return bool(_BINANCE_SYMBOL_PATTERN.fullmatch(normalized))


async def _fetch_top_pairs(
    client: httpx.AsyncClient,
    *,
    base_url: str,
    pair_limit: int,
) -> list[str]:
    response = await client.get(f"{base_url}/api/v3/ticker/24hr")
    response.raise_for_status()
    payload = response.json()

    if not isinstance(payload, list):
        raise ValueError("Unexpected top-pairs response format")

    candidates: list[tuple[str, float]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        symbol = str(item.get("symbol") or "").strip().upper()
        if not _is_supported_binance_symbol(symbol):
            continue
        quote_volume = _to_float(item.get("quoteVolume"))
        if quote_volume is None:
            continue
        candidates.append((symbol, quote_volume))

    candidates.sort(key=lambda item: item[1], reverse=True)
    return [symbol for symbol, _ in candidates[:pair_limit]]


async def _fetch_price_snapshot(
    client: httpx.AsyncClient,
    *,
    base_url: str,
    symbols: list[str],
) -> list[dict[str, Any]]:
    prices: list[dict[str, Any]] = []
    updated_at = _utc_now_iso()

    for symbol in symbols:
        try:
            response = await client.get(
                f"{base_url}/api/v3/ticker/24hr",
                params={"symbol": symbol},
            )
            response.raise_for_status()
        except Exception as exc:
            logger.warning("[binance-worker] price fetch failed for %s: %s", symbol, exc)
            continue

        payload = response.json()
        if not isinstance(payload, dict):
            continue

        price = _to_float(payload.get("lastPrice"))
        change_24h_pct = _to_float(payload.get("priceChangePercent"))
        bid = _to_float(payload.get("bidPrice"))
        ask = _to_float(payload.get("askPrice"))
        if price is None:
            continue

        prices.append(
            {
                "symbol": symbol,
                "price": price,
                "change_24h_pct": change_24h_pct,
                "bid": bid if bid is not None else price,
                "ask": ask if ask is not None else price,
                "updated_at": updated_at,
                "source": "worker-rest",
            }
        )

    return prices


def _build_snapshot_payload(
    *,
    running: bool,
    pair_limit: int,
    pair_refresh_seconds: int,
    price_ttl_seconds: float,
    ws_stream_limit: int,
    pairs: list[str],
    prices: list[dict[str, Any]],
    top_pairs_cached_at_ts: float | None,
    last_pair_refresh_at_ts: float | None,
    pair_refresh_errors: int,
    rest_sync_errors: int,
) -> dict[str, Any]:
    now_ts = time.time()
    fetched_at = None
    if prices:
        fetched_at = max(
            (item.get("updated_at") for item in prices if isinstance(item.get("updated_at"), str)),
            default=None,
        )

    top_pairs = {
        "pairs": list(pairs),
        "count": len(pairs),
        "is_stale": bool(
            top_pairs_cached_at_ts is not None
            and (now_ts - top_pairs_cached_at_ts) > pair_refresh_seconds
        ),
        "cached_at": _timestamp_to_iso(top_pairs_cached_at_ts),
        "ttl_seconds": pair_refresh_seconds,
    }
    status = {
        "running": running,
        "service": "binance-realtime-connector",
        "pair_limit": pair_limit,
        "pair_refresh_seconds": pair_refresh_seconds,
        "price_ttl_seconds": price_ttl_seconds,
        "ws_stream_limit": ws_stream_limit,
        "top_pairs_count": len(pairs),
        "top_pairs_cached_at": _timestamp_to_iso(top_pairs_cached_at_ts),
        "last_pair_refresh_at": _timestamp_to_iso(last_pair_refresh_at_ts),
        "last_ws_connect_at": None,
        "last_ws_disconnect_at": None,
        "last_ws_message_age_seconds": None,
        "reconnect_count": 0,
        "disconnect_count": 0,
        "pair_refresh_errors": pair_refresh_errors,
        "rest_sync_errors": rest_sync_errors,
        "rest_weight_used": None,
        "rest_weight_limit": None,
        "latency_p95_ms": None,
        "latency_p99_ms": None,
        "event_to_cache_last_ms": None,
    }

    return {
        "service": "binance-realtime-connector",
        "running": running,
        "heartbeat_at": _utc_now_iso(),
        "heartbeat_ts": now_ts,
        "now_ts": now_ts,
        "fetched_at": fetched_at,
        "status": status,
        "top_pairs": top_pairs,
        "prices": prices,
    }


async def _run_worker() -> None:
    settings = get_settings()
    base_url = str(settings.binance_base_url).rstrip("/")
    pair_limit = max(1, min(250, int(settings.binance_top_pairs_limit)))
    ws_stream_limit = max(
        1,
        min(pair_limit, int(_setting(settings, "binance_ws_stream_limit", 10))),
    )
    pair_refresh_seconds = max(5, int(settings.binance_top_pairs_refresh_seconds))
    price_ttl_seconds = max(1.0, float(settings.binance_price_ttl_seconds))
    request_timeout_seconds = max(2.0, float(settings.binance_request_timeout_seconds))
    poll_seconds = max(2.0, min(float(pair_refresh_seconds), float(price_ttl_seconds)))

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    def _request_stop() -> None:
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        with suppress(NotImplementedError):
            loop.add_signal_handler(sig, _request_stop)

    pairs: list[str] = []
    prices: list[dict[str, Any]] = []
    top_pairs_cached_at_ts: float | None = None
    last_pair_refresh_at_ts: float | None = None
    pair_refresh_errors = 0
    rest_sync_errors = 0

    timeout = httpx.Timeout(request_timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout) as client:
        while not stop_event.is_set():
            try:
                pairs = await _fetch_top_pairs(client, base_url=base_url, pair_limit=pair_limit)
                now_ts = time.time()
                top_pairs_cached_at_ts = now_ts
                last_pair_refresh_at_ts = now_ts
            except Exception as exc:
                pair_refresh_errors += 1
                logger.warning("[binance-worker] top pair refresh failed: %s", exc)

            if pairs:
                next_prices = await _fetch_price_snapshot(
                    client,
                    base_url=base_url,
                    symbols=pairs[:ws_stream_limit],
                )
                if next_prices:
                    prices = next_prices
                else:
                    rest_sync_errors += 1

            payload = _build_snapshot_payload(
                running=True,
                pair_limit=pair_limit,
                pair_refresh_seconds=pair_refresh_seconds,
                price_ttl_seconds=price_ttl_seconds,
                ws_stream_limit=ws_stream_limit,
                pairs=pairs,
                prices=prices,
                top_pairs_cached_at_ts=top_pairs_cached_at_ts,
                last_pair_refresh_at_ts=last_pair_refresh_at_ts,
                pair_refresh_errors=pair_refresh_errors,
                rest_sync_errors=rest_sync_errors,
            )
            await asyncio.to_thread(write_snapshot, payload)

            try:
                await asyncio.wait_for(stop_event.wait(), timeout=poll_seconds)
            except TimeoutError:
                continue

    payload = _build_snapshot_payload(
        running=False,
        pair_limit=pair_limit,
        pair_refresh_seconds=pair_refresh_seconds,
        price_ttl_seconds=price_ttl_seconds,
        ws_stream_limit=ws_stream_limit,
        pairs=pairs,
        prices=prices,
        top_pairs_cached_at_ts=top_pairs_cached_at_ts,
        last_pair_refresh_at_ts=last_pair_refresh_at_ts,
        pair_refresh_errors=pair_refresh_errors,
        rest_sync_errors=rest_sync_errors,
    )
    await asyncio.to_thread(write_snapshot, payload)


def main() -> None:
    asyncio.run(_run_worker())


if __name__ == "__main__":
    main()
