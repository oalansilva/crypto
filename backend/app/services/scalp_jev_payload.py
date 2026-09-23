"""Assemble enriched Jev state from stream memory and account snapshot."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import ROUND_DOWN, Decimal
from typing import Any, Optional, Sequence

from app.services.scalp_btcusdt_stream import (
    AggTradeTick,
    ScalpBtcusdtMemory,
    get_scalp_btcusdt_memory,
)
from app.services.scalp_engine import HORIZON_S, RestingOrder, compute_t
from app.services.scalp_window import TouchMetrics, WindowMetrics, touch_metrics, window_metrics

# Card #1025 (P3): the window summary carries the horizon aggregates plus at
# most these last trades — never the full tick dump.
RECENT_TRADES_N = 5


def _dec(value: Any) -> Decimal:
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def _dec_str(value: Any, places: str) -> str:
    """Rounded decimal string: the summary keeps bp-level resolution only."""
    try:
        return str(_dec(value).quantize(Decimal(places), rounding=ROUND_DOWN))
    except Exception:
        return str(value)


def _recent_trades(
    trades: Sequence[AggTradeTick], *, now: datetime, limit: int = RECENT_TRADES_N
) -> list[list[Any]]:
    """Last N trades as [age_s, price, qty, aggressor] (1 buy, −1 sell)."""
    now_epoch = (
        now.replace(tzinfo=timezone.utc).timestamp() if now.tzinfo is None else now.timestamp()
    )
    sample: list[list[Any]] = []
    for tick in list(trades)[-limit:]:
        age_s = max(0, int(now_epoch - (tick.trade_time_ms / 1000.0)))
        sample.append(
            [
                age_s,
                _dec_str(tick.price, "0.01"),
                _dec_str(tick.quantity, "0.00001"),
                -1 if tick.is_buyer_maker else 1,
            ]
        )
    return sample


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
    if touch is None:
        return None, "no_book"
    window = build_window(mem)
    if window is None or window.trade_count <= 0:
        return None, "window_empty"
    t = compute_t(free_usdt)
    inv_quote = inventory_btc * touch.mid
    remaining = t - inv_quote
    trades = mem.recent_trades()
    state: dict[str, Any] = {
        "symbol": "BTCUSDT",
        "horizon_s": HORIZON_S,
        "touch": {
            "bid": _dec_str(touch.bid, "0.01"),
            "ask": _dec_str(touch.ask, "0.01"),
            "bid_qty": _dec_str(touch.bid_qty, "0.00001"),
            "ask_qty": _dec_str(touch.ask_qty, "0.00001"),
            "mid": _dec_str(touch.mid, "0.01"),
            "spread_bp": _dec_str(touch.spread_bp, "0.001"),
            "microprice": _dec_str(touch.microprice, "0.01"),
            "imbalance": _dec_str(touch.imbalance, "0.0001"),
            "age_ms": touch.age_ms,
        },
        "window": {
            "horizon_s": window.horizon_s,
            "trade_count": window.trade_count,
            "ret_bp": _dec_str(window.ret_bp, "0.01"),
            "vol_bp": _dec_str(window.vol_bp, "0.01"),
            "aggressor_flow": _dec_str(window.aggressor_flow, "0.00001"),
            "volume": _dec_str(window.volume, "0.00001"),
            "spread_bp_mean": _dec_str(window.spread_bp_mean, "0.001"),
            "recent_trades": _recent_trades(trades, now=now),
        },
        "account": {
            "inventory_btc": _dec_str(inventory_btc, "0.00000001"),
            "t": _dec_str(t, "0.01"),
            "remaining_to_t": _dec_str(remaining, "0.01"),
            "fee_bp": _dec_str(fee_bp, "0.01"),
            "bnb_fee_active": bnb_fee_active,
        },
        "resting": resting_payload(resting, rest_opened_at=rest_opened_at, now=now),
    }
    return {"state": state}, None
