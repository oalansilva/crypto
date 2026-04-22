from __future__ import annotations

import asyncio
import json
import logging
import random
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import httpx
import websockets

from app.config import get_settings

logger = logging.getLogger(__name__)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _to_float(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed == parsed else None


def _to_int(value: Any) -> int | None:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed


def _normalize_symbols(raw_symbols: list[str] | None) -> list[str] | None:
    if not raw_symbols:
        return None
    normalized: list[str] = []
    seen: set[str] = set()
    for symbol in raw_symbols:
        normalized_symbol = str(symbol or "").strip().upper().replace("/", "")
        if not normalized_symbol or normalized_symbol in seen:
            continue
        seen.add(normalized_symbol)
        normalized.append(normalized_symbol)
    return normalized


def _percentile(values: deque[float], percent: int) -> float | None:
    if not values:
        return None
    sorted_values = sorted(values)
    if not sorted_values:
        return None
    index = max(0, min(len(sorted_values) - 1, int(len(sorted_values) * percent / 100)))
    return sorted_values[index]


@dataclass
class _PriceRecord:
    symbol: str
    price: float | None
    change_24h_pct: float | None
    bid: float | None
    ask: float | None
    event_time_ms: int
    event_to_cache_ms: float | None
    updated_at_iso: str
    updated_at_ts: float
    source: str


class _TokenBucket:
    def __init__(self, max_tokens: int, refill_per_second: float):
        self._max_tokens = max(1, int(max_tokens))
        self._tokens = float(self._max_tokens)
        self._refill_per_second = max(0.01, float(refill_per_second))
        self._lock = asyncio.Lock()
        self._last_refill = time.monotonic()

    async def take(self, cost: float = 1.0) -> None:
        required = max(0.0, float(cost))
        if required <= 0:
            return

        while True:
            async with self._lock:
                now = time.monotonic()
                elapsed = max(0.0, now - self._last_refill)
                self._tokens = min(
                    self._max_tokens, self._tokens + elapsed * self._refill_per_second
                )
                self._last_refill = now

                if self._tokens >= required:
                    self._tokens -= required
                    return

                missing = required - self._tokens
                wait_seconds = missing / self._refill_per_second
                self._tokens = 0.0

            await asyncio.sleep(wait_seconds + random.uniform(0.0, 0.2))


class BinanceRealtimeConnector:
    def __init__(self) -> None:
        settings = get_settings()

        self._rest_base_url = str(settings.binance_base_url).rstrip("/")
        self._ws_base_url = str(settings.binance_ws_base_url).rstrip("/")
        self._pair_limit = max(1, min(250, int(settings.binance_top_pairs_limit)))
        self._pair_refresh_seconds = max(5, int(settings.binance_top_pairs_refresh_seconds))
        self._pair_ttl_seconds = max(5, int(settings.binance_top_pairs_ttl_seconds))
        self._price_ttl_seconds = max(1, float(settings.binance_price_ttl_seconds))
        self._heartbeat_timeout_seconds = max(
            8.0, float(settings.binance_ws_heartbeat_timeout_seconds)
        )
        self._reconnect_base_seconds = max(0.5, float(settings.binance_ws_reconnect_base_seconds))
        self._reconnect_max_seconds = max(1.0, float(settings.binance_ws_reconnect_max_seconds))
        rate_limit_per_minute = max(1, int(settings.binance_rate_limit_per_minute))
        self._request_timeout_seconds = max(1.0, float(settings.binance_request_timeout_seconds))
        self._max_rest_retries = max(1, int(settings.binance_rest_max_retries))

        self._rate_limiter = _TokenBucket(rate_limit_per_minute, rate_limit_per_minute / 60.0)
        self._lock = asyncio.Lock()
        self._prices: dict[str, _PriceRecord] = {}
        self._pairs: list[str] = []
        self._pair_cache_updated_at: float | None = None
        self._tasks: set[asyncio.Task[Any]] = set()
        self._shutdown = asyncio.Event()
        self._pairs_changed = asyncio.Event()
        self._pair_snapshot_error_count = 0
        self._rest_sync_error_count = 0
        self._ws_reconnect_count = 0
        self._ws_disconnect_count = 0
        self._running = False
        self._latency_ms = deque[float](maxlen=1000)
        self._last_pair_refresh_at: float | None = None
        self._last_ws_connect_at: float | None = None
        self._last_ws_disconnect_at: float | None = None
        self._last_ws_message_at: float | None = None
        self._last_ws_event_loop_ms: float | None = None
        self._last_rest_weight_used: int | None = None
        self._last_rest_weight_limit: int | None = None

    async def start(self) -> None:
        if self._running:
            return

        self._running = True
        self._shutdown.clear()
        self._pairs_changed.clear()

        pair_task = asyncio.create_task(self._pair_refresh_loop(), name="binance-top-pairs-refresh")
        ws_task = asyncio.create_task(self._ws_loop(), name="binance-ws-loop")
        self._tasks.update({pair_task, ws_task})
        pair_task.add_done_callback(self._tasks.discard)
        ws_task.add_done_callback(self._tasks.discard)
        logger.info("[binance-realtime] connector started")

    async def stop(self) -> None:
        if not self._running:
            return

        self._running = False
        self._shutdown.set()
        self._pairs_changed.set()

        tasks = [task for task in list(self._tasks) if not task.done()]
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        self._tasks.clear()

        logger.info("[binance-realtime] connector stopped")

    async def _safe_request(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        *,
        weight: float = 1.0,
    ) -> Any:
        url = f"{self._rest_base_url}{endpoint}"

        for attempt in range(1, self._max_rest_retries + 1):
            if self._shutdown.is_set():
                raise RuntimeError("Binance connector is stopping")

            await self._rate_limiter.take(weight)
            timeout = httpx.Timeout(self._request_timeout_seconds)
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    response = await client.get(url, params=params)

                if response.status_code == 429:
                    retry_after = response.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after else min(30.0, 2.0**attempt)
                    logger.warning(
                        "[binance-realtime] rate-limited on %s, retrying in %.2fs (attempt=%s)",
                        endpoint,
                        delay,
                        attempt,
                    )
                    await asyncio.sleep(delay)
                    continue

                response.raise_for_status()
                self._capture_rate_headers(response.headers)
                return response.json()
            except (httpx.HTTPError, ValueError) as exc:
                if attempt >= self._max_rest_retries:
                    raise
                delay = min(2.0 + (2.0 ** (attempt - 1)), 8.0)
                logger.warning(
                    "[binance-realtime] REST request failed on %s (attempt=%s): %s; retrying in %.2fs",
                    endpoint,
                    attempt,
                    exc,
                    delay,
                )
                await asyncio.sleep(delay)

        raise RuntimeError(f"REST request failed for endpoint {endpoint}")

    def _capture_rate_headers(self, headers: httpx.Headers) -> None:
        try:
            used = _to_int(headers.get("X-MBX-USED-WEIGHT-1m"))
            limit = _to_int(headers.get("X-MBX-WEIGHT-1M"))
            if used is not None:
                self._last_rest_weight_used = used
            if limit is not None:
                self._last_rest_weight_limit = limit
        except Exception:
            pass

    async def _pair_refresh_loop(self) -> None:
        while not self._shutdown.is_set():
            try:
                await self._refresh_top_pairs()
            except Exception as exc:
                self._pair_snapshot_error_count += 1
                logger.warning("[binance-realtime] top pair refresh failed: %s", exc)

            try:
                await asyncio.wait_for(self._shutdown.wait(), timeout=self._pair_refresh_seconds)
            except TimeoutError:
                continue

    async def _refresh_top_pairs(self) -> None:
        payload = await self._safe_request("/api/v3/ticker/24hr", weight=40.0)

        if not isinstance(payload, list):
            raise ValueError("Unexpected top-pairs response format")

        candidates: list[tuple[str, float]] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            symbol = str(item.get("symbol") or "").strip().upper()
            if not symbol.endswith("USDT"):
                continue
            quote_volume = _to_float(item.get("quoteVolume"))
            if quote_volume is None:
                continue
            candidates.append((symbol, quote_volume))

        candidates.sort(key=lambda item: item[1], reverse=True)
        next_pairs = [symbol for symbol, _ in candidates[: self._pair_limit]]

        changed = False
        async with self._lock:
            if next_pairs != self._pairs:
                self._pairs = next_pairs
                changed = True
            self._pair_cache_updated_at = time.time()

        self._last_pair_refresh_at = time.time()
        if changed:
            self._pairs_changed.set()
            await self._sync_prices_from_rest(next_pairs)
        elif not self._prices:
            await self._sync_prices_from_rest(next_pairs)

    async def _sync_prices_from_rest(self, symbols: list[str]) -> None:
        if not symbols:
            return

        chunks: list[list[str]] = [symbols[i : i + 100] for i in range(0, len(symbols), 100)]
        now = time.time()

        received_iso = _utc_now_iso()
        records = {}
        for chunk in chunks:
            payload = await self._safe_request(
                "/api/v3/ticker/price",
                params={"symbols": json.dumps(chunk)},
                weight=2.0,
            )
            if isinstance(payload, dict):
                payload = [payload]
            if not isinstance(payload, list):
                continue

            for item in payload:
                if not isinstance(item, dict):
                    continue
                symbol = str(item.get("symbol") or "").strip().upper()
                if not symbol:
                    continue
                price = _to_float(item.get("price"))
                if price is None:
                    continue
                records[symbol] = _PriceRecord(
                    symbol=symbol,
                    price=price,
                    change_24h_pct=None,
                    bid=price,
                    ask=price,
                    event_time_ms=int(now * 1000.0),
                    event_to_cache_ms=0.0,
                    updated_at_iso=received_iso,
                    updated_at_ts=now,
                    source="rest-sync",
                )

        async with self._lock:
            for symbol, record in records.items():
                self._prices[symbol] = record
            active = set(self._pairs)
            prune_before = now - self._pair_ttl_seconds
            for symbol in list(self._prices.keys()):
                if symbol not in active and self._prices[symbol].updated_at_ts < prune_before:
                    self._prices.pop(symbol, None)

    async def _ws_loop(self) -> None:
        while not self._shutdown.is_set():
            pairs = await self._current_pairs()
            if not pairs:
                await asyncio.sleep(min(self._reconnect_base_seconds * 2, 5.0))
                continue

            stream_url = f"{self._ws_base_url}/stream?streams={'/'.join(pair.lower() + '@ticker' for pair in pairs)}"
            backoff = self._reconnect_base_seconds

            while not self._shutdown.is_set() and not self._pairs_changed.is_set():
                try:
                    async with websockets.connect(
                        stream_url,
                        ping_interval=15,
                        ping_timeout=20,
                        close_timeout=5,
                    ) as websocket:
                        self._last_ws_connect_at = time.time()
                        self._last_ws_event_loop_ms = None
                        self._pairs_changed.clear()
                        await self._consume_ws_stream(websocket)
                except asyncio.CancelledError:
                    raise
                except Exception as exc:
                    self._ws_disconnect_count += 1
                    if self._shutdown.is_set():
                        break
                    self._last_ws_disconnect_at = time.time()
                    await self._sync_prices_from_rest(pairs)
                    self._ws_reconnect_count += 1
                    delay = min(backoff, self._reconnect_max_seconds)
                    backoff = min(backoff * 2, self._reconnect_max_seconds)
                    logger.warning(
                        "[binance-realtime] ws disconnected: %s; retrying in %.2fs",
                        exc,
                        delay,
                    )
                    await asyncio.sleep(delay + random.uniform(0.0, 0.4))

                if self._pairs_changed.is_set():
                    break

    async def _consume_ws_stream(self, websocket: websockets.WebSocketClientProtocol) -> None:
        await self._sync_prices_from_rest(await self._current_pairs())

        while not self._shutdown.is_set() and not self._pairs_changed.is_set():
            try:
                message_text = await asyncio.wait_for(
                    websocket.recv(),
                    timeout=self._heartbeat_timeout_seconds,
                )
            except asyncio.TimeoutError:
                self._ws_disconnect_count += 1
                self._last_ws_disconnect_at = time.time()
                logger.warning("[binance-realtime] ws heartbeat timeout, reconnecting")
                return
            except websockets.ConnectionClosed:
                self._ws_disconnect_count += 1
                self._last_ws_disconnect_at = time.time()
                return

            self._last_ws_message_at = time.time()
            await self._handle_ws_message(message_text)

    async def _handle_ws_message(self, message_text: str) -> None:
        try:
            payload = json.loads(message_text)
        except json.JSONDecodeError:
            return

        if not isinstance(payload, dict):
            return
        if isinstance(payload.get("data"), dict):
            payload = payload["data"]
            if not isinstance(payload, dict):
                return

        symbol = str(payload.get("s") or "").strip().upper()
        if not symbol:
            return

        async with self._lock:
            if self._pairs and symbol not in self._pairs:
                return

        last_price = _to_float(payload.get("c"))
        bid = _to_float(payload.get("b"))
        ask = _to_float(payload.get("a"))
        change_24h_pct = _to_float(payload.get("P"))
        event_time_ms = _to_int(payload.get("E"))
        if event_time_ms is None:
            return

        now_ms = int(time.time() * 1000)
        event_to_cache_ms = max(0.0, float(now_ms - event_time_ms))
        self._latency_ms.append(event_to_cache_ms)
        self._last_ws_event_loop_ms = event_to_cache_ms

        now = time.time()
        record = _PriceRecord(
            symbol=symbol,
            price=last_price,
            change_24h_pct=change_24h_pct,
            bid=bid,
            ask=ask,
            event_time_ms=event_time_ms,
            event_to_cache_ms=event_to_cache_ms,
            updated_at_iso=_utc_now_iso(),
            updated_at_ts=now,
            source="websocket",
        )
        async with self._lock:
            self._prices[symbol] = record

    async def _current_pairs(self) -> list[str]:
        async with self._lock:
            if not self._pairs:
                return []
            return list(self._pairs)

    async def get_top_pairs(self) -> dict[str, Any]:
        async with self._lock:
            cached_at = self._pair_cache_updated_at
            is_stale = cached_at is not None and (time.time() - cached_at) > self._pair_ttl_seconds
            return {
                "pairs": list(self._pairs),
                "count": len(self._pairs),
                "is_stale": bool(is_stale),
                "cached_at": (
                    datetime.fromtimestamp(cached_at, tz=timezone.utc)
                    .isoformat()
                    .replace("+00:00", "Z")
                    if cached_at
                    else None
                ),
                "ttl_seconds": self._pair_ttl_seconds,
            }

    async def get_status(self) -> dict[str, Any]:
        async with self._lock:
            status = {
                "running": self._running and not self._shutdown.is_set(),
                "service": "binance-realtime-connector",
                "pair_limit": self._pair_limit,
                "pair_refresh_seconds": self._pair_refresh_seconds,
                "price_ttl_seconds": self._price_ttl_seconds,
                "top_pairs_count": len(self._pairs),
                "top_pairs_cached_at": (
                    datetime.fromtimestamp(self._pair_cache_updated_at, tz=timezone.utc)
                    .isoformat()
                    .replace("+00:00", "Z")
                    if self._pair_cache_updated_at
                    else None
                ),
                "last_pair_refresh_at": (
                    datetime.fromtimestamp(self._last_pair_refresh_at, tz=timezone.utc)
                    .isoformat()
                    .replace("+00:00", "Z")
                    if self._last_pair_refresh_at
                    else None
                ),
                "last_ws_connect_at": (
                    datetime.fromtimestamp(self._last_ws_connect_at, tz=timezone.utc)
                    .isoformat()
                    .replace("+00:00", "Z")
                    if self._last_ws_connect_at
                    else None
                ),
                "last_ws_disconnect_at": (
                    datetime.fromtimestamp(self._last_ws_disconnect_at, tz=timezone.utc)
                    .isoformat()
                    .replace("+00:00", "Z")
                    if self._last_ws_disconnect_at
                    else None
                ),
                "last_ws_message_age_seconds": (
                    time.time() - self._last_ws_message_at if self._last_ws_message_at else None
                ),
                "reconnect_count": self._ws_reconnect_count,
                "disconnect_count": self._ws_disconnect_count,
                "pair_refresh_errors": self._pair_snapshot_error_count,
                "rest_sync_errors": self._rest_sync_error_count,
                "rest_weight_used": self._last_rest_weight_used,
                "rest_weight_limit": self._last_rest_weight_limit,
                "latency_p95_ms": _percentile(self._latency_ms, 95),
                "latency_p99_ms": _percentile(self._latency_ms, 99),
                "event_to_cache_last_ms": self._last_ws_event_loop_ms,
            }
            return status

    async def get_latest_prices(
        self,
        symbols: list[str] | None = None,
    ) -> tuple[list[dict[str, Any]], str | None, bool]:
        requested = _normalize_symbols(symbols) or await self._all_symbols()
        now = time.time()

        prices: list[dict[str, Any]] = []
        stale = False
        missing: list[str] = []
        snapshots: dict[str, _PriceRecord] = {}

        async with self._lock:
            for symbol in requested:
                record = self._prices.get(symbol)
                if record is None:
                    missing.append(symbol)
                    continue
                snapshots[symbol] = record

        for symbol, record in snapshots.items():
            stale = stale or (now - record.updated_at_ts) > self._price_ttl_seconds
            prices.append(
                {
                    "symbol": symbol,
                    "price": record.price,
                    "change_24h_pct": record.change_24h_pct,
                    "bid": record.bid,
                    "ask": record.ask,
                    "updated_at": record.updated_at_iso,
                    "source": record.source,
                }
            )

        if missing:
            fallback = await self._fetch_fallback_prices(missing)
            prices.extend(fallback)
            if fallback:
                stale = stale or True

        records_by_symbol = {item["symbol"]: item for item in prices}
        ordered = []
        for symbol in requested:
            item = records_by_symbol.get(symbol)
            if item is None:
                continue
            ordered.append(item)

        cached_at = None
        timestamps: list[float] = []
        for item in ordered:
            value = item.get("updated_at")
            if not isinstance(value, str):
                continue
            try:
                timestamps.append(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())
            except Exception:
                continue

        if timestamps:
            cached_at = (
                datetime.fromtimestamp(max(timestamps), tz=timezone.utc)
                .isoformat()
                .replace(
                    "+00:00",
                    "Z",
                )
            )

        return ordered, cached_at, stale

    async def _all_symbols(self) -> list[str]:
        async with self._lock:
            if self._pairs:
                return list(self._pairs)
            return list(self._prices.keys())

    async def _fetch_fallback_prices(self, symbols: list[str]) -> list[dict[str, Any]]:
        if not symbols:
            return []

        now = _utc_now_iso()
        now_ts = time.time()
        result: list[dict[str, Any]] = []
        chunks = [symbols[i : i + 100] for i in range(0, len(symbols), 100)]

        for chunk in chunks:
            try:
                payload = await self._safe_request(
                    "/api/v3/ticker/24hr",
                    params={"symbols": json.dumps(chunk)},
                    weight=4.0,
                )
            except Exception as exc:
                self._rest_sync_error_count += 1
                logger.warning("[binance-realtime] fallback prices fetch failed: %s", exc)
                continue

            if isinstance(payload, dict):
                payload = [payload]
            if not isinstance(payload, list):
                continue

            for item in payload:
                if not isinstance(item, dict):
                    continue
                symbol = str(item.get("symbol") or "").strip().upper()
                if not symbol:
                    continue
                price = _to_float(item.get("lastPrice"))
                if price is None:
                    continue
                change_24h_pct = _to_float(item.get("priceChangePercent"))
                if change_24h_pct is None:
                    continue
                result.append(
                    {
                        "symbol": symbol,
                        "price": price,
                        "change_24h_pct": change_24h_pct,
                        "bid": price,
                        "ask": price,
                        "updated_at": now,
                        "source": "rest-fallback",
                    }
                )
                async with self._lock:
                    self._prices[symbol] = _PriceRecord(
                        symbol=symbol,
                        price=price,
                        change_24h_pct=change_24h_pct,
                        bid=price,
                        ask=price,
                        event_time_ms=int(now_ts * 1000.0),
                        event_to_cache_ms=max(0.0, time.time() * 1000.0 - now_ts * 1000.0),
                        updated_at_iso=now,
                        updated_at_ts=now_ts,
                        source="rest-fallback",
                    )

        return result


_connector = BinanceRealtimeConnector()


async def start_binance_realtime_connector() -> None:
    await _connector.start()


async def stop_binance_realtime_connector() -> None:
    await _connector.stop()


def is_running() -> bool:
    return _connector._running


async def get_top_pairs() -> dict[str, Any]:
    return await _connector.get_top_pairs()


async def get_connector_status() -> dict[str, Any]:
    return await _connector.get_status()


async def get_market_latest_prices(
    symbols: list[str] | None = None,
) -> tuple[list[dict[str, Any]], str | None, bool]:
    return await _connector.get_latest_prices(symbols)
