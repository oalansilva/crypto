"""Real price path for scalp Jev barrier resolution (card #1070)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Optional, Protocol, Sequence


@dataclass(frozen=True)
class TradeTick:
    at: datetime
    price: Decimal


@dataclass(frozen=True)
class OneSecondBar:
    open_time: datetime
    high: Decimal
    low: Decimal
    close: Decimal


class PricePathStore(Protocol):
    def trades_between(self, start: datetime, end: datetime) -> list[TradeTick]:
        ...

    def one_second_bars_between(self, start: datetime, end: datetime) -> list[OneSecondBar]:
        ...


@dataclass
class MemoryPricePathStore:
    trades: tuple[TradeTick, ...] = ()
    one_second: tuple[OneSecondBar, ...] = ()

    def trades_between(self, start: datetime, end: datetime) -> list[TradeTick]:
        return [t for t in self.trades if start <= t.at <= end]

    def one_second_bars_between(self, start: datetime, end: datetime) -> list[OneSecondBar]:
        return [
            b
            for b in self.one_second
            if start <= b.open_time and b.open_time + timedelta(seconds=1) <= end
        ]


def load_agg_trades_jsonl(path: Path) -> MemoryPricePathStore:
    trades: list[TradeTick] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        ts_ms = int(row.get("T") or row.get("time") or 0)
        price = Decimal(str(row.get("p") or row.get("price") or "0"))
        if price <= 0:
            continue
        at = datetime.utcfromtimestamp(ts_ms / 1000.0)
        trades.append(TradeTick(at=at, price=price))
    trades.sort(key=lambda item: item.at)
    return MemoryPricePathStore(trades=tuple(trades))


def _barrier_from_path(
    *,
    side: str,
    entry: Decimal,
    path: Sequence[tuple[Decimal, Decimal]],
    target_bp: Decimal,
    stop_bp: Decimal,
) -> str:
    if side not in {"BUY", "SELL"} or entry <= 0 or not path:
        return "unknown"
    if side == "BUY":
        target = entry * (Decimal("1") + target_bp / Decimal("10000"))
        stop = entry * (Decimal("1") + stop_bp / Decimal("10000"))
    else:
        target = entry * (Decimal("1") - target_bp / Decimal("10000"))
        stop = entry * (Decimal("1") - stop_bp / Decimal("10000"))
    for high, low in path:
        if side == "BUY":
            if low <= stop:
                return "stop"
            if high >= target:
                return "target"
        else:
            if high >= stop:
                return "stop"
            if low <= target:
                return "target"
    return "none"


def _complete_one_second_bars(start: datetime, end: datetime, bars: Sequence[OneSecondBar]) -> bool:
    if end <= start:
        return False
    expected = int((end - start).total_seconds())
    if expected <= 0:
        return False
    stamps = {
        b.open_time
        for b in bars
        if start <= b.open_time and b.open_time + timedelta(seconds=1) <= end
    }
    for i in range(expected):
        if start + timedelta(seconds=i) not in stamps:
            return False
    return True


def barrier_for_window(
    store: Optional[PricePathStore],
    *,
    side: Optional[str],
    entry: Decimal,
    start: datetime,
    end: datetime,
    target_bp: Decimal,
    stop_bp: Decimal,
) -> tuple[str, Optional[Decimal]]:
    if side not in {"BUY", "SELL"} or entry <= 0:
        return "unknown", None
    if store is None:
        return "indeterminate", None
    trades = store.trades_between(start, end)
    if trades:
        path = [(t.price, t.price) for t in trades]
        barrier = _barrier_from_path(
            side=side, entry=entry, path=path, target_bp=target_bp, stop_bp=stop_bp
        )
        return barrier, trades[-1].price
    bars = store.one_second_bars_between(start, end)
    if bars and _complete_one_second_bars(start, end, bars):
        path = [(b.high, b.low) for b in bars]
        barrier = _barrier_from_path(
            side=side, entry=entry, path=path, target_bp=target_bp, stop_bp=stop_bp
        )
        return barrier, bars[-1].close
    return "indeterminate", None


def realized_signed_bp(
    *, side: Optional[str], entry: Decimal, exit_price: Optional[Decimal]
) -> Optional[Decimal]:
    if exit_price is None or exit_price <= 0 or entry <= 0:
        return None
    move_bp = (exit_price / entry - Decimal("1")) * Decimal("10000")
    if side == "SELL":
        return -move_bp
    if side == "BUY":
        return move_bp
    return None
