"""Pure directional scalp rules (BTCUSDT post-only). No I/O, no secrets."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN
from typing import Literal, Optional

SYMBOL = "BTCUSDT"
T_CAP = Decimal("100")
CLIP_CAP = Decimal("10")
KILL_RATIO = Decimal("0.02")
CONFIDENCE_MIN = Decimal("0.7")
FEE_HEADROOM = Decimal("0.001")
JEV_LATE_MS = 800
JEV_FLOOR_MS = 400
JEV_TARGET_MS = 1000
CLIENT_ORDER_PREFIX = "cfscalp_"
ORDER_TYPE = "LIMIT"
TIME_IN_FORCE = "GTX"
CROSS_REJECT_CODES = frozenset({-5022, -2010})

Side = Literal["BUY", "SELL"]
PanelState = Literal["off", "on", "kill", "nokey"]
SkipReason = Optional[str]


def _q(value: Decimal, places: str = "0.01") -> Decimal:
    return value.quantize(Decimal(places), rounding=ROUND_DOWN)


def compute_t(free_usdt: Decimal) -> Decimal:
    """T = min(100, free USDT with fee headroom). Does not require 100.00."""
    if free_usdt <= 0:
        return Decimal("0")
    usable = _q(free_usdt / (Decimal("1") + FEE_HEADROOM))
    if usable <= 0:
        return Decimal("0")
    return min(T_CAP, usable)


def clip_quote(*, remaining_to_t: Decimal) -> Decimal:
    room = remaining_to_t if remaining_to_t > 0 else Decimal("0")
    return min(CLIP_CAP, room)


def should_kill(*, day_pnl: Decimal, t: Decimal) -> bool:
    if t <= 0:
        return False
    return day_pnl <= -(KILL_RATIO * t)


def clip_inventory(*, bot_inventory: Decimal, free_btc: Decimal, floor_btc: Decimal) -> Decimal:
    available = max(Decimal("0"), free_btc - floor_btc)
    inventory = max(Decimal("0"), bot_inventory)
    return min(inventory, available)


def post_only_price(side: Side, *, bid: Decimal, ask: Decimal) -> Decimal:
    return bid if side == "BUY" else ask


def would_cross(side: Side, price: Decimal, *, bid: Decimal, ask: Decimal) -> bool:
    if side == "BUY":
        return price >= ask
    return price <= bid


def pnl_quote(
    *,
    realized: Decimal,
    unrealized: Decimal,
    fees: Decimal,
    jev_cost: Decimal,
) -> Decimal:
    return realized + unrealized - fees - jev_cost


def unrealized_pnl(*, inventory_btc: Decimal, avg_entry: Optional[Decimal], mid: Decimal) -> Decimal:
    if inventory_btc <= 0 or avg_entry is None:
        return Decimal("0")
    return (mid - avg_entry) * inventory_btc


def panel_state(*, has_spot_key: bool, enabled: bool, killed: bool) -> PanelState:
    if not has_spot_key:
        return "nokey"
    if killed:
        return "kill"
    if enabled:
        return "on"
    return "off"


def is_bot_client_order_id(client_order_id: str | None) -> bool:
    return str(client_order_id or "").startswith(CLIENT_ORDER_PREFIX)


def build_client_order_id(user_id: str, nonce: str) -> str:
    digest = "".join(ch for ch in f"{user_id}{nonce}" if ch.isalnum())[-16:]
    if len(digest) < 16:
        digest = (digest + "0" * 16)[:16]
    return f"{CLIENT_ORDER_PREFIX}{digest[:16]}"


@dataclass(frozen=True)
class Book:
    bid: Decimal
    ask: Decimal

    @property
    def mid(self) -> Decimal:
        return (self.bid + self.ask) / Decimal("2")


@dataclass(frozen=True)
class RestingOrder:
    client_order_id: str
    side: Side
    price: Decimal


@dataclass(frozen=True)
class JevSignal:
    side: Optional[Side]
    confidence: Decimal
    edge_after_fees: bool
    book_toxic: bool
    latency_ms: int
    cost_quote: Decimal = Decimal("0")


@dataclass(frozen=True)
class CycleIntent:
    send: bool
    cancel_resting: bool
    fire_kill: bool
    skip_reason: SkipReason
    side: Optional[Side] = None
    price: Optional[Decimal] = None
    quote_qty: Optional[Decimal] = None
    quantity: Optional[Decimal] = None
    order_type: str = ORDER_TYPE
    time_in_force: str = TIME_IN_FORCE
    clipped_inventory: Optional[Decimal] = None
    call_jev: bool = False


def decide_cycle(
    *,
    enabled: bool,
    killed: bool,
    has_spot_key: bool,
    jev_available: bool,
    jev_in_flight: bool,
    last_jev_elapsed_ms: Optional[int],
    inventory_btc: Decimal,
    floor_btc: Decimal,
    free_usdt: Decimal,
    free_btc: Decimal,
    day_pnl: Decimal,
    book: Book,
    resting: Optional[RestingOrder],
    jev: Optional[JevSignal] = None,
) -> CycleIntent:
    """Hold is the default. Live send is opt-in after every gate."""
    clipped = clip_inventory(
        bot_inventory=inventory_btc, free_btc=free_btc, floor_btc=floor_btc
    )
    inventory_changed = clipped != inventory_btc
    t = compute_t(free_usdt)
    if killed or not enabled:
        cancel = resting is not None
        return CycleIntent(
            send=False,
            cancel_resting=cancel,
            fire_kill=False,
            skip_reason="halted" if killed else "switch_off",
            clipped_inventory=clipped if inventory_changed else None,
        )
    if not has_spot_key:
        return CycleIntent(
            send=False,
            cancel_resting=resting is not None,
            fire_kill=False,
            skip_reason="no_spot_key",
            clipped_inventory=clipped if inventory_changed else None,
        )
    if should_kill(day_pnl=day_pnl, t=t):
        return CycleIntent(
            send=False,
            cancel_resting=resting is not None,
            fire_kill=True,
            skip_reason="kill",
            clipped_inventory=clipped if inventory_changed else None,
        )

    cancel_stale = False
    if resting is not None:
        touch = post_only_price(resting.side, bid=book.bid, ask=book.ask)
        if resting.price != touch:
            cancel_stale = True

    if jev_in_flight:
        return CycleIntent(
            send=False,
            cancel_resting=cancel_stale,
            fire_kill=False,
            skip_reason="jev_in_flight",
            clipped_inventory=clipped if inventory_changed else None,
        )
    if not jev_available:
        return CycleIntent(
            send=False,
            cancel_resting=cancel_stale,
            fire_kill=False,
            skip_reason="jev_unavailable",
            call_jev=False,
            clipped_inventory=clipped if inventory_changed else None,
        )
    if jev is None:
        # Book ticks stay at JEV_FLOOR_MS for stale cancel; Jev itself is ~1 s.
        if last_jev_elapsed_ms is not None and last_jev_elapsed_ms < JEV_TARGET_MS:
            return CycleIntent(
                send=False,
                cancel_resting=cancel_stale,
                fire_kill=False,
                skip_reason="jev_target",
                call_jev=False,
                clipped_inventory=clipped if inventory_changed else None,
            )
        return CycleIntent(
            send=False,
            cancel_resting=cancel_stale,
            fire_kill=False,
            skip_reason="need_jev",
            call_jev=True,
            clipped_inventory=clipped if inventory_changed else None,
        )
    if jev.latency_ms > JEV_LATE_MS:
        return CycleIntent(
            send=False,
            cancel_resting=cancel_stale,
            fire_kill=False,
            skip_reason="jev_late",
            clipped_inventory=clipped if inventory_changed else None,
        )

    side = jev.side
    if side is None:
        return CycleIntent(
            send=False,
            cancel_resting=cancel_stale,
            fire_kill=False,
            skip_reason="hold",
            clipped_inventory=clipped if inventory_changed else None,
        )
    if jev.confidence < CONFIDENCE_MIN:
        return CycleIntent(
            send=False,
            cancel_resting=cancel_stale,
            fire_kill=False,
            skip_reason="low_confidence",
            clipped_inventory=clipped if inventory_changed else None,
        )
    if not jev.edge_after_fees:
        return CycleIntent(
            send=False,
            cancel_resting=cancel_stale,
            fire_kill=False,
            skip_reason="no_edge",
            clipped_inventory=clipped if inventory_changed else None,
        )
    if jev.book_toxic:
        return CycleIntent(
            send=False,
            cancel_resting=cancel_stale,
            fire_kill=False,
            skip_reason="toxic_book",
            clipped_inventory=clipped if inventory_changed else None,
        )
    if t <= 0:
        return CycleIntent(
            send=False,
            cancel_resting=cancel_stale,
            fire_kill=False,
            skip_reason="t_zero",
            clipped_inventory=clipped if inventory_changed else None,
        )

    inventory_quote = clipped * book.mid
    remaining_to_t = t - inventory_quote
    near_ceiling = remaining_to_t <= CLIP_CAP
    if near_ceiling and side == "BUY":
        return CycleIntent(
            send=False,
            cancel_resting=cancel_stale,
            fire_kill=False,
            skip_reason="ceiling_reduce_only",
            clipped_inventory=clipped if inventory_changed else None,
        )
    if side == "SELL" and clipped <= 0:
        return CycleIntent(
            send=False,
            cancel_resting=cancel_stale,
            fire_kill=False,
            skip_reason="zero_inventory",
            clipped_inventory=clipped if inventory_changed else None,
        )

    price = post_only_price(side, bid=book.bid, ask=book.ask)
    if would_cross(side, price, bid=book.bid, ask=book.ask):
        return CycleIntent(
            send=False,
            cancel_resting=cancel_stale,
            fire_kill=False,
            skip_reason="would_cross",
            clipped_inventory=clipped if inventory_changed else None,
        )
    if side == "BUY":
        quote_qty = min(CLIP_CAP, max(Decimal("0"), remaining_to_t), compute_t(free_usdt))
        quote_qty = min(quote_qty, _q(free_usdt / (Decimal("1") + FEE_HEADROOM)))
        if quote_qty <= 0:
            return CycleIntent(
                send=False,
                cancel_resting=cancel_stale,
                fire_kill=False,
                skip_reason="t_zero",
                clipped_inventory=clipped if inventory_changed else None,
            )
        quantity = (quote_qty / price) if price > 0 else Decimal("0")
    else:
        sell_quote_cap = min(CLIP_CAP, clipped * price)
        quote_qty = sell_quote_cap
        quantity = (quote_qty / price) if price > 0 else Decimal("0")
        quantity = min(quantity, clipped)
        quote_qty = quantity * price

    if quantity <= 0 or quote_qty <= 0:
        return CycleIntent(
            send=False,
            cancel_resting=cancel_stale,
            fire_kill=False,
            skip_reason="dust",
            clipped_inventory=clipped if inventory_changed else None,
        )
    if quote_qty > CLIP_CAP:
        quote_qty = CLIP_CAP
        quantity = quote_qty / price

    return CycleIntent(
        send=True,
        cancel_resting=cancel_stale,
        fire_kill=False,
        skip_reason=None,
        side=side,
        price=price,
        quote_qty=quote_qty,
        quantity=quantity,
        order_type=ORDER_TYPE,
        time_in_force=TIME_IN_FORCE,
        clipped_inventory=clipped if inventory_changed else None,
    )
