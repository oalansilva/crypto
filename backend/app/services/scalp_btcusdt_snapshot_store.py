"""Cross-process freshness snapshot for the BTCUSDT scalp stream (loop holder → API)."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from decimal import Decimal

from app.services.scalp_engine import Book, SYMBOL

FRESH_AGE_MS = 500


def _snapshot_path() -> Path:
    configured = os.getenv("CRYPTO_SCALP_BTCUSDT_SNAPSHOT_PATH")
    if configured:
        return Path(configured)
    return Path("/tmp/crypto-scalp-btcusdt-snapshot.json")


def publish_scalp_btcusdt_snapshot(
    *,
    ws_connected: bool,
    received_at: float | None,
    bid: str | None = None,
    ask: str | None = None,
) -> None:
    payload: dict[str, Any] = {
        "symbol": SYMBOL,
        "ws_connected": bool(ws_connected),
        "received_at": received_at,
        "bid": bid,
        "ask": ask,
        "pid": os.getpid(),
        "written_at": time.time(),
    }
    path = _snapshot_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    temp_path.write_text(
        json.dumps(payload, ensure_ascii=True, separators=(",", ":")),
        encoding="utf-8",
    )
    temp_path.replace(path)


def read_scalp_btcusdt_snapshot() -> dict[str, Any] | None:
    path = _snapshot_path()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except Exception:
        return None
    if not isinstance(raw, dict):
        return None
    return raw


def _freshness_from_snapshot(snapshot: dict[str, Any]) -> tuple[bool, int | None]:
    if not snapshot.get("ws_connected"):
        return False, None
    received_at = snapshot.get("received_at")
    if not isinstance(received_at, (int, float)) or received_at <= 0:
        return False, None
    age_ms = int((time.time() - float(received_at)) * 1000)
    if age_ms > FRESH_AGE_MS:
        return False, age_ms
    return True, age_ms


def book_from_snapshot(snapshot: dict[str, Any] | None) -> Book | None:
    if snapshot is None:
        return None
    avail, _ = _freshness_from_snapshot(snapshot)
    if not avail:
        return None
    bid_raw = snapshot.get("bid")
    ask_raw = snapshot.get("ask")
    if bid_raw is None or ask_raw is None:
        return None
    try:
        bid = Decimal(str(bid_raw))
        ask = Decimal(str(ask_raw))
    except Exception:
        return None
    if bid <= 0 or ask <= 0:
        return None
    return Book(bid=bid, ask=ask)


def resolve_scalp_btcusdt_freshness(
    local_connected: bool,
    local_age_ms: int | None,
    local_book_available: bool,
) -> tuple[bool, int | None]:
    """Same freshness the cycle uses in the loop holder; API reads cross-process snapshot."""
    if local_connected or local_age_ms is not None:
        return local_book_available, local_age_ms
    snapshot = read_scalp_btcusdt_snapshot()
    if snapshot is None:
        return False, None
    return _freshness_from_snapshot(snapshot)


def resolve_scalp_btcusdt_book(
    local_connected: bool,
    local_age_ms: int | None,
    local_book: Book | None,
) -> Book | None:
    if local_connected or local_age_ms is not None:
        return local_book
    return book_from_snapshot(read_scalp_btcusdt_snapshot())
