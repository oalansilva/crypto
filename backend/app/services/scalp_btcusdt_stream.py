"""Shared in-process BTCUSDT bookTicker + aggTrade stream for the scalp loop."""

from __future__ import annotations

import asyncio
import json
import logging
import random
import threading
import time
from collections import deque
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Optional

import websockets

from app.config import get_settings
from app.services.scalp_engine import SYMBOL, Book

logger = logging.getLogger(__name__)

FRESH_AGE_MS = 500
TRADE_WINDOW_SECONDS = 5.0
_SYMBOL = SYMBOL.lower()


def _to_decimal(value: Any) -> Decimal:
    try:
        return Decimal(str(value))
    except Exception:
        return Decimal("0")


@dataclass(frozen=True)
class AggTradeTick:
    price: Decimal
    quantity: Decimal
    trade_time_ms: int
    is_buyer_maker: bool


@dataclass
class _TouchState:
    bid: Decimal
    ask: Decimal
    bid_qty: Decimal
    ask_qty: Decimal
    event_time_ms: int
    received_at: float


class ScalpBtcusdtMemory:
    """Thread-safe in-process cache fed by a single WS per process."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._touch: _TouchState | None = None
        self._trades: deque[AggTradeTick] = deque()
        self._ws_connected = False
        self._connect_count = 0

    def reset_for_tests(self) -> None:
        with self._lock:
            self._touch = None
            self._trades.clear()
            self._ws_connected = False

    def set_ws_connected(self, connected: bool) -> None:
        with self._lock:
            self._ws_connected = connected
            if not connected:
                self._touch = None
        self._publish_cross_process_snapshot()

    def ingest_book_ticker(self, payload: dict[str, Any]) -> None:
        symbol = str(payload.get("s") or "").strip().upper()
        if symbol != SYMBOL:
            return
        bid = _to_decimal(payload.get("b"))
        ask = _to_decimal(payload.get("a"))
        if bid <= 0 or ask <= 0:
            return
        bid_qty = _to_decimal(payload.get("B"))
        ask_qty = _to_decimal(payload.get("A"))
        event_time_ms = int(payload.get("E") or payload.get("u") or 0)
        now = time.time()
        with self._lock:
            self._touch = _TouchState(
                bid=bid,
                ask=ask,
                bid_qty=bid_qty,
                ask_qty=ask_qty,
                event_time_ms=event_time_ms,
                received_at=now,
            )
        self._publish_cross_process_snapshot()

    def ingest_agg_trade(self, payload: dict[str, Any]) -> None:
        symbol = str(payload.get("s") or "").strip().upper()
        if symbol != SYMBOL:
            return
        price = _to_decimal(payload.get("p"))
        qty = _to_decimal(payload.get("q"))
        if price <= 0 or qty <= 0:
            return
        trade_time_ms = int(payload.get("T") or payload.get("E") or 0)
        is_buyer_maker = bool(payload.get("m"))
        tick = AggTradeTick(
            price=price,
            quantity=qty,
            trade_time_ms=trade_time_ms,
            is_buyer_maker=is_buyer_maker,
        )
        cutoff_ms = int((time.time() - TRADE_WINDOW_SECONDS) * 1000)
        with self._lock:
            self._trades.append(tick)
            while self._trades and self._trades[0].trade_time_ms < cutoff_ms:
                self._trades.popleft()

    def age_ms(self) -> int | None:
        with self._lock:
            if self._touch is None:
                return None
            return int((time.time() - self._touch.received_at) * 1000)

    def stream_connected(self) -> bool:
        with self._lock:
            return self._ws_connected

    def book_available(self) -> bool:
        age = self.age_ms()
        if age is None:
            return False
        return self.stream_connected() and age <= FRESH_AGE_MS

    def read_book(self) -> Book | None:
        with self._lock:
            if self._touch is None:
                return None
            touch = self._touch
        return Book(bid=touch.bid, ask=touch.ask)

    def read_touch(self) -> tuple[Decimal, Decimal, Decimal, Decimal] | None:
        with self._lock:
            if self._touch is None:
                return None
            t = self._touch
            return t.bid, t.ask, t.bid_qty, t.ask_qty

    def recent_trades(self) -> list[AggTradeTick]:
        cutoff_ms = int((time.time() - TRADE_WINDOW_SECONDS) * 1000)
        with self._lock:
            return [t for t in self._trades if t.trade_time_ms >= cutoff_ms]

    def connection_count(self) -> int:
        with self._lock:
            return self._connect_count

    def record_connect(self) -> None:
        with self._lock:
            self._connect_count += 1

    def _publish_cross_process_snapshot(self) -> None:
        from app.services.scalp_btcusdt_snapshot_store import publish_scalp_btcusdt_snapshot

        with self._lock:
            touch = self._touch
            ws_connected = self._ws_connected
        received_at = touch.received_at if touch is not None else None
        bid = str(touch.bid) if touch is not None else None
        ask = str(touch.ask) if touch is not None else None
        publish_scalp_btcusdt_snapshot(
            ws_connected=ws_connected,
            received_at=received_at,
            bid=bid,
            ask=ask,
        )


_memory = ScalpBtcusdtMemory()
_stream_task: asyncio.Task[None] | None = None
_stream_stop = asyncio.Event()
_stream_lock = asyncio.Lock()


def get_scalp_btcusdt_memory() -> ScalpBtcusdtMemory:
    return _memory


def _stream_url() -> str:
    settings = get_settings()
    base = str(settings.binance_ws_base_url).rstrip("/")
    return f"{base}/stream?streams={_SYMBOL}@bookTicker/{_SYMBOL}@aggTrade"


async def _consume_stream(stop_event: asyncio.Event) -> None:
    settings = get_settings()
    reconnect_base = max(0.5, float(settings.binance_ws_reconnect_base_seconds))
    reconnect_max = max(1.0, float(settings.binance_ws_reconnect_max_seconds))
    heartbeat_timeout = max(8.0, float(settings.binance_ws_heartbeat_timeout_seconds))
    backoff = reconnect_base
    memory = get_scalp_btcusdt_memory()

    while not stop_event.is_set():
        url = _stream_url()
        try:
            async with websockets.connect(
                url,
                ping_interval=15,
                ping_timeout=20,
                close_timeout=5,
            ) as websocket:
                memory.set_ws_connected(True)
                memory.record_connect()
                backoff = reconnect_base
                logger.info("[scalp-btcusdt] ws connected")
                while not stop_event.is_set():
                    try:
                        message_text = await asyncio.wait_for(
                            websocket.recv(),
                            timeout=heartbeat_timeout,
                        )
                    except asyncio.TimeoutError:
                        logger.warning("[scalp-btcusdt] ws heartbeat timeout, reconnecting")
                        break
                    except websockets.ConnectionClosed:
                        break
                    _handle_message(memory, message_text)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            if stop_event.is_set():
                break
            logger.warning("[scalp-btcusdt] ws error: %s; retrying in %.2fs", exc, backoff)
        finally:
            memory.set_ws_connected(False)

        if stop_event.is_set():
            break
        delay = min(backoff, reconnect_max) + random.uniform(0.0, 0.4)
        backoff = min(backoff * 2, reconnect_max)
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=delay)
        except asyncio.TimeoutError:
            continue

    memory.set_ws_connected(False)
    logger.info("[scalp-btcusdt] ws loop stopped")


def _handle_message(memory: ScalpBtcusdtMemory, message_text: str) -> None:
    try:
        envelope = json.loads(message_text)
    except json.JSONDecodeError:
        return
    if not isinstance(envelope, dict):
        return
    payload = envelope.get("data") if isinstance(envelope.get("data"), dict) else envelope
    if not isinstance(payload, dict):
        return
    event = str(payload.get("e") or "").strip()
    if event == "aggTrade":
        memory.ingest_agg_trade(payload)
        return
    if "b" in payload and "a" in payload and str(payload.get("s") or "").upper() == SYMBOL:
        memory.ingest_book_ticker(payload)


async def ensure_scalp_btcusdt_stream() -> None:
    """Start the shared stream task if not already running (one per process)."""
    global _stream_task
    async with _stream_lock:
        if _stream_task is not None and not _stream_task.done():
            return
        _stream_stop.clear()
        _stream_task = asyncio.create_task(_consume_stream(_stream_stop), name="scalp-btcusdt-ws")


async def stop_scalp_btcusdt_stream() -> None:
    global _stream_task
    async with _stream_lock:
        if _stream_task is None:
            return
        _stream_stop.set()
        _stream_task.cancel()
        try:
            await _stream_task
        except asyncio.CancelledError:
            pass
        _stream_task = None


def scalp_stream_task_running() -> bool:
    return _stream_task is not None and not _stream_task.done()
