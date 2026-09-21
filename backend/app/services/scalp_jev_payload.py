"""Assemble enriched Jev state from stream memory and account snapshot."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from app.services.scalp_btcusdt_stream import ScalpBtcusdtMemory, get_scalp_btcusdt_memory
from app.services.scalp_engine import HORIZON_S, RestingOrder, compute_t
from app.services.scalp_window import TouchMetrics, WindowMetrics, touch_metrics, window_metrics


def _dec(value: Any) -> Decimal:
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def build_touch(memory: ScalpBtcusdtMemory) -> Optional[TouchMetrics]:
    touch = memory.read_touch()
    age = memory.age_ms()
    if touch is None or age is None:
        return None
    bid, ask, bid_qty, ask_qty = touch
    return touch_metrics(bid=bid, ask=ask, bid_qty=bid_qty, ask_qty=ask_qty, age_ms=age)


def build_window(memory: ScalpBtcusdtMemory) -> Optional[WindowMetrics]:
    trades = memory.recent_trades()
    spreads = memory.spread_samples_bp()
    return window_metrics(trades, spread_samples_bp=spreads, horizon_s=HORIZON_S)


def resting_payload(
    resting: Optional[RestingOrder],
    *,
    rest_opened_at: Optional[datetime],
    now: datetime,
) -> Optional[dict[str, Any]]:
    if resting is None:
        return None
    age_ms = 0
    if rest_opened_at is not None:
        age_ms = int((now - rest_opened_at).total_seconds() * 1000)
    return {
        "side": resting.side,
        "price": str(resting.price),
        "age_ms": age_ms,
        "role": resting.role,
    }


def build_jev_payload(
    *,
    inventory_btc: Decimal,
    free_usdt: Decimal,
    fee_bp: Decimal,
    bnb_fee_active: bool,
    resting: Optional[RestingOrder],
    rest_opened_at: Optional[datetime],
    now: datetime,
    memory: Optional[ScalpBtcusdtMemory] = None,
) -> tuple[Optional[dict[str, Any]], Optional[str]]:
    mem = memory or get_scalp_btcusdt_memory()
    touch = build_touch(mem)
    window = build_window(mem)
    if window is None or window.trade_count <= 0:
        return None, "window_empty"
    if touch is None:
        return None, "no_book"
    t = compute_t(free_usdt)
    inv_quote = inventory_btc * touch.mid
    remaining = t - inv_quote
    state: dict[str, Any] = {
        "symbol": "BTCUSDT",
        "horizon_s": HORIZON_S,
        "touch": {
            "bid": str(touch.bid),
            "ask": str(touch.ask),
            "bid_qty": str(touch.bid_qty),
            "ask_qty": str(touch.ask_qty),
            "mid": str(touch.mid),
            "spread_bp": str(touch.spread_bp),
            "microprice": str(touch.microprice),
            "imbalance": str(touch.imbalance),
            "age_ms": touch.age_ms,
        },
        "window": {
            "horizon_s": window.horizon_s,
            "trade_count": window.trade_count,
            "ret_bp": str(window.ret_bp),
            "vol_bp": str(window.vol_bp),
            "aggressor_flow": str(window.aggressor_flow),
            "volume": str(window.volume),
            "spread_bp_mean": str(window.spread_bp_mean),
        },
        "account": {
            "inventory_btc": str(inventory_btc),
            "t": str(t),
            "remaining_to_t": str(remaining),
            "fee_bp": str(fee_bp),
            "bnb_fee_active": bnb_fee_active,
        },
        "resting": resting_payload(resting, rest_opened_at=rest_opened_at, now=now),
    }
    return {"state": state}, None
