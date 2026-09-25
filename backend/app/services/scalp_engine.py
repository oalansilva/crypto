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
HORIZON_S = 900
JEV_LATE_MS = 1500
JEV_FLOOR_MS = 400
# Card #1025: 30 s default, injected by the service (the engine reads no env).
JEV_TARGET_MS = 30000
# Card #1028: the call timeout is decoupled from the late gate. A reply that
# arrives between JEV_LATE_MS and this value is received, mapped and recorded
# and the cycle is still refused as late (same decision, now with data). The
# timeout is a pure contract value; the service may still override it.
JEV_CALL_TIMEOUT_MS = 3000
# Card #1028: toxicity read with two cut-offs and an uncertainty band that only
# labels the record. The decision keeps the single 0.5 cut-off below.
TOXIC_NOUL_DECISION = Decimal("0.5")
TOXIC_NOUL_NOT_TOXIC_BELOW = Decimal("0.4")
TOXIC_NOUL_TOXIC_ABOVE = Decimal("0.6")
ENTRY_REST_TIMEOUT_S = 10
EXIT_TARGET_BP = Decimal("35")
EXIT_STOP_BP = Decimal("-28")
HOLD_AFTER_FILL_S = 900
STUCK_AFTER_FILL_S = 930
CLIENT_ORDER_PREFIX = "cfscalp_"
ORDER_TYPE = "LIMIT"
TIME_IN_FORCE = "GTX"
# Aggressive exit (card #1025): MARKET, no price ceiling and no slippage guard.
AGGRESSIVE_ORDER_TYPE = "MARKET"
CROSS_REJECT_CODES = frozenset({-5022, -2010})

Side = Literal["BUY", "SELL"]
PanelState = Literal["off", "on", "kill", "nokey"]
SkipReason = Optional[str]
# Card #1028: verdict of one reply-fed entry gate. ``not_applicable`` is a gate
# configured off (never a ``fail``).
GateVerdict = Literal["pass", "fail", "not_applicable"]
# Card #1030: market regime of the window volatility (σ, ``vol_bp``) against
# the single configured boundary. ``unknown`` is the fail-closed default (no
# boundary or no finite σ): the regime cannot be named, so neither opens.
MarketRegime = Literal["calm", "active", "unknown"]
REGIME_CALM: MarketRegime = "calm"
REGIME_ACTIVE: MarketRegime = "active"
REGIME_UNKNOWN: MarketRegime = "unknown"
# Card #1030: confidence policy of one market regime. ``numeric`` keeps the
# threshold gate with that regime's value; ``off`` is the removal path of the
# #1025 gate (decision by forecast × cost × regime); ``closed`` does not
# operate.
ConfidencePolicyKind = Literal["numeric", "off", "closed"]
CONFIDENCE_POLICY_NUMERIC: ConfidencePolicyKind = "numeric"
CONFIDENCE_POLICY_OFF: ConfidencePolicyKind = "off"
CONFIDENCE_POLICY_CLOSED: ConfidencePolicyKind = "closed"
# Card #1030: refusal token of a closed regime. It is its own token — never
# ``regime`` (the #1025 cost-with-slack gate) and never ``low_confidence``.
CLOSED_REGIME_SKIP = "regime_closed"
# The reply-fed entry gates, in the order their rules are evaluated below.
GATE_ORDER: tuple[str, ...] = (
    "jev_late",
    "hold",
    "low_confidence",
    "hurdle",
    "regime",
    "toxic_book",
)


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


def unrealized_pnl(
    *, inventory_btc: Decimal, avg_entry: Optional[Decimal], mid: Decimal
) -> Decimal:
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


RestRole = Literal["entry", "exit"]


@dataclass(frozen=True)
class RestingOrder:
    client_order_id: str
    side: Side
    price: Decimal
    role: RestRole = "entry"


@dataclass(frozen=True)
class JevSignal:
    side: Optional[Side]
    confidence: Decimal
    expected_move_bp: Decimal
    book_toxic: bool
    latency_ms: int
    cost_quote: Decimal = Decimal("0")
    # Card #1028: diagnostics carried from the client to the cycle record. The
    # decision never reads them; ``confidence`` above stays the value the gates
    # consume, produced together with ``confidence_origin``.
    model: Optional[str] = None
    confidence_origin: str = "none"
    noul: Optional[Decimal] = None
    noul_label: str = "unknown"
    # Card #1029: the reply read as a position on the ordered scale, plus the
    # band of the level already reached against that cycle's real cost.
    # ``expected_move_bp`` above is already the exact bp of the credited level
    # (never an interpolated value); these two fields only feed the record.
    move_position: Optional[int] = None
    move_band: str = "unknown"


@dataclass(frozen=True)
class GateVerdicts:
    """Verdict of every reply-fed entry gate, computed independently (card #1028)."""

    jev_late: GateVerdict
    hold: GateVerdict
    low_confidence: GateVerdict
    hurdle: GateVerdict
    regime: GateVerdict
    toxic_book: GateVerdict

    def as_items(self) -> tuple[tuple[str, str], ...]:
        """``(gate, verdict)`` pairs in evaluation order (record rendering)."""
        return tuple((name, getattr(self, name)) for name in GATE_ORDER)


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
    # Card #1025: MARKET escape with no price ceiling (exit path only).
    aggressive_exit: bool = False
    # Card #1028: verdict of every reply-fed gate. ``None`` when the cycle has
    # no model reply (pre-call closes and the exit path); a side effect that
    # never enters the decision.
    gate_verdicts: Optional[GateVerdicts] = None
    # Card #1030: market regime the decision used and the kind of the
    # confidence policy applied to it. Record only — the decision already
    # happened when these are read.
    market_regime: MarketRegime = REGIME_UNKNOWN
    confidence_policy_kind: ConfidencePolicyKind = CONFIDENCE_POLICY_NUMERIC


@dataclass(frozen=True)
class ConfidencePolicy:
    """Confidence policy of the market regime a cycle belongs to (card #1030).

    Pure data: the engine receives it by parameter and reads no env.
    ``numeric`` keeps the threshold gate with the regime's value; ``off`` is
    the removal path of the #1025 gate (no ``low_confidence``, decision by
    forecast × cost × regime); ``closed`` does not operate and closes the cycle
    with ``CLOSED_REGIME_SKIP`` without comparing any threshold.

    The default keeps the product threshold for callers of the older entry
    points; the service always passes the policy of the cycle's regime.
    """

    kind: ConfidencePolicyKind = CONFIDENCE_POLICY_NUMERIC
    value: Optional[Decimal] = CONFIDENCE_MIN
    regime: MarketRegime = REGIME_UNKNOWN

    @property
    def closed(self) -> bool:
        return self.kind == CONFIDENCE_POLICY_CLOSED

    @property
    def threshold(self) -> Optional[Decimal]:
        """Numeric threshold in use, or ``None`` when the gate is off/closed."""
        if self.kind != CONFIDENCE_POLICY_NUMERIC:
            return None
        return self.value


def resolve_confidence_policy(
    *,
    confidence_policy: Optional[ConfidencePolicy] = None,
    confidence_min: Optional[Decimal] = CONFIDENCE_MIN,
    market_regime: MarketRegime = REGIME_UNKNOWN,
) -> ConfidencePolicy:
    """Policy the engine reads, with the #1025 ``confidence_min`` as alias.

    Card #1030: the service passes the ``ConfidencePolicy`` of the cycle's
    regime and the market regime itself. Callers of the #1025 contract may
    still pass ``confidence_min`` (``None`` = gate removed); it is read as the
    numeric/off policy of that regime, so the old entry points keep their
    meaning and the engine never reads the env. When a policy is given, the
    regime it carries is the authority.
    """
    if confidence_policy is not None:
        return confidence_policy
    if confidence_min is None:
        return ConfidencePolicy(kind=CONFIDENCE_POLICY_OFF, value=None, regime=market_regime)
    return ConfidencePolicy(
        kind=CONFIDENCE_POLICY_NUMERIC, value=confidence_min, regime=market_regime
    )


from app.services.scalp_window import passes_entry_hurdle, passes_regime_gate  # noqa: E402


def reply_gate_verdicts(
    *,
    jev: JevSignal,
    confidence_min: Optional[Decimal] = CONFIDENCE_MIN,
    confidence_policy: Optional[ConfidencePolicy] = None,
    market_regime: MarketRegime = REGIME_UNKNOWN,
    fee_bp: Decimal = Decimal("10"),
    spread_bp: Decimal = Decimal("0"),
) -> GateVerdicts:
    """Verdict of every entry gate fed by the model reply (card #1028).

    Each verdict is computed independently of the first gate that closes the
    cycle, so a refusal by confidence still carries the cost, regime and
    toxicity verdicts. Pure data: no I/O, no config lookup, no side effect.

    Card #1029: ``jev.expected_move_bp`` is the exact bp of the **level already
    reached** (rounded down), so the two cost verdicts below already read the
    credited level's band; their rules, names and boundaries are untouched.

    Card #1030: the confidence verdict reads the **policy of the regime** the
    cycle belongs to (``numeric`` value, ``off`` or ``closed``), never a single
    global threshold.
    """
    policy = resolve_confidence_policy(
        confidence_policy=confidence_policy,
        confidence_min=confidence_min,
        market_regime=market_regime,
    )
    threshold = policy.threshold
    if threshold is None:
        low_confidence: GateVerdict = "not_applicable"
    elif jev.confidence < threshold:
        low_confidence = "fail"
    else:
        low_confidence = "pass"
    return GateVerdicts(
        jev_late="fail" if jev.latency_ms > JEV_LATE_MS else "pass",
        hold="fail" if jev.side is None else "pass",
        low_confidence=low_confidence,
        hurdle=("pass" if passes_entry_hurdle(jev.expected_move_bp, fee_bp, spread_bp) else "fail"),
        regime=("pass" if passes_regime_gate(jev.expected_move_bp, fee_bp, spread_bp) else "fail"),
        toxic_book="fail" if jev.book_toxic else "pass",
    )


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
    fee_bp: Decimal = Decimal("10"),
    spread_bp: Decimal = Decimal("0"),
    has_open_position: bool = False,
    has_exit_resting: bool = False,
    # ``None`` removes the confidence gate (card #1025 C): no ``low_confidence``
    # refusal is produced and the decision becomes forecast × cost × regime.
    # Card #1030: ``confidence_policy`` (the policy of the cycle's regime) takes
    # precedence; ``confidence_min`` is read only as the #1025 alias.
    confidence_min: Optional[Decimal] = CONFIDENCE_MIN,
    confidence_policy: Optional[ConfidencePolicy] = None,
    market_regime: MarketRegime = REGIME_UNKNOWN,
    jev_target_ms: int = JEV_TARGET_MS,
) -> CycleIntent:
    """Hold is the default. Live send is opt-in after every gate."""
    clipped = clip_inventory(bot_inventory=inventory_btc, free_btc=free_btc, floor_btc=floor_btc)
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

    if has_open_position or has_exit_resting:
        return CycleIntent(
            send=False,
            cancel_resting=cancel_stale,
            fire_kill=False,
            skip_reason="position_open",
            call_jev=False,
            clipped_inventory=clipped if inventory_changed else None,
        )

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
        # Book ticks stay at JEV_FLOOR_MS for stale cancel; the Jev consult
        # cadence is the injected `jev_target_ms` (card #1025: 30 s default).
        if last_jev_elapsed_ms is not None and last_jev_elapsed_ms < jev_target_ms:
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
    # Card #1028: from here on the cycle has a model reply, so the verdict of
    # every reply-fed gate is computed once and attached to whichever return
    # closes the cycle (the decision itself is unchanged).
    # Card #1030: the confidence verdict reads the policy of the cycle's
    # regime; the regime and the policy kind travel in the same intent for the
    # record (never a second decision).
    policy = resolve_confidence_policy(
        confidence_policy=confidence_policy,
        confidence_min=confidence_min,
        market_regime=market_regime,
    )
    verdicts = reply_gate_verdicts(
        jev=jev,
        confidence_policy=policy,
        fee_bp=fee_bp,
        spread_bp=spread_bp,
    )
    reply_meta: dict = {
        "gate_verdicts": verdicts,
        "market_regime": policy.regime,
        "confidence_policy_kind": policy.kind,
    }
    if jev.latency_ms > JEV_LATE_MS:
        return CycleIntent(
            send=False,
            cancel_resting=cancel_stale,
            fire_kill=False,
            skip_reason="jev_late",
            clipped_inventory=clipped if inventory_changed else None,
            **reply_meta,
        )

    side = jev.side
    if side is None:
        return CycleIntent(
            send=False,
            cancel_resting=cancel_stale,
            fire_kill=False,
            skip_reason="hold",
            clipped_inventory=clipped if inventory_changed else None,
            **reply_meta,
        )
    if policy.closed:
        # Card #1030: the regime's policy is closed — the cycle does not
        # operate and closes with its own token, without comparing any
        # threshold. Never `regime` and never `low_confidence`.
        return CycleIntent(
            send=False,
            cancel_resting=cancel_stale,
            fire_kill=False,
            skip_reason=CLOSED_REGIME_SKIP,
            clipped_inventory=clipped if inventory_changed else None,
            **reply_meta,
        )
    threshold = policy.threshold
    if threshold is not None and jev.confidence < threshold:
        return CycleIntent(
            send=False,
            cancel_resting=cancel_stale,
            fire_kill=False,
            skip_reason="low_confidence",
            clipped_inventory=clipped if inventory_changed else None,
            **reply_meta,
        )
    if not passes_entry_hurdle(jev.expected_move_bp, fee_bp, spread_bp):
        return CycleIntent(
            send=False,
            cancel_resting=cancel_stale,
            fire_kill=False,
            skip_reason="hurdle",
            clipped_inventory=clipped if inventory_changed else None,
            **reply_meta,
        )
    # Card #1025: maker cost + 50% slack. Evaluated after the bare hurdle
    # ("below cost") and before `toxic_book`, so the tokens tell the story:
    # `hurdle` = below cost, `regime` = clears cost without the slack.
    # Card #1029: the value compared here is the band of the level already
    # reached (credited, rounded down); one reason only, no new token.
    if not passes_regime_gate(jev.expected_move_bp, fee_bp, spread_bp):
        return CycleIntent(
            send=False,
            cancel_resting=cancel_stale,
            fire_kill=False,
            skip_reason="regime",
            clipped_inventory=clipped if inventory_changed else None,
            **reply_meta,
        )
    if jev.book_toxic:
        return CycleIntent(
            send=False,
            cancel_resting=cancel_stale,
            fire_kill=False,
            skip_reason="toxic_book",
            clipped_inventory=clipped if inventory_changed else None,
            **reply_meta,
        )
    if t <= 0:
        return CycleIntent(
            send=False,
            cancel_resting=cancel_stale,
            fire_kill=False,
            skip_reason="t_zero",
            clipped_inventory=clipped if inventory_changed else None,
            **reply_meta,
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
            **reply_meta,
        )
    if side == "SELL" and clipped <= 0:
        return CycleIntent(
            send=False,
            cancel_resting=cancel_stale,
            fire_kill=False,
            skip_reason="zero_inventory",
            clipped_inventory=clipped if inventory_changed else None,
            **reply_meta,
        )

    price = post_only_price(side, bid=book.bid, ask=book.ask)
    if would_cross(side, price, bid=book.bid, ask=book.ask):
        return CycleIntent(
            send=False,
            cancel_resting=cancel_stale,
            fire_kill=False,
            skip_reason="would_cross",
            clipped_inventory=clipped if inventory_changed else None,
            **reply_meta,
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
                **reply_meta,
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
            **reply_meta,
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
        **reply_meta,
    )


def position_ret_bp(avg_entry: Decimal, mid: Decimal) -> Decimal:
    if avg_entry <= 0 or mid <= 0:
        return Decimal("0")
    return (mid / avg_entry - Decimal("1")) * Decimal("10000")


def should_post_exit(
    *,
    ret_bp: Decimal,
) -> bool:
    """Passive exit inside the waiting window only: target or stop.

    Card #1025: the time branch (``seconds_since_fill >= HOLD_AFTER_FILL_S``)
    is gone — at the end of the window the cycle goes aggressive instead of
    posting one more passive order (the forbidden extra passive attempt).
    """
    if ret_bp >= EXIT_TARGET_BP:
        return True
    if ret_bp <= EXIT_STOP_BP:
        return True
    return False


def should_mark_stuck(seconds_since_fill: float) -> bool:
    return seconds_since_fill >= float(STUCK_AFTER_FILL_S)


def decide_exit_cycle(
    *,
    enabled: bool,
    killed: bool,
    has_spot_key: bool,
    inventory_btc: Decimal,
    free_btc: Decimal,
    floor_btc: Decimal,
    avg_entry: Optional[Decimal],
    book: Book,
    resting: Optional[RestingOrder],
    seconds_since_fill: float,
    stuck: bool,
) -> CycleIntent:
    clipped = clip_inventory(bot_inventory=inventory_btc, free_btc=free_btc, floor_btc=floor_btc)
    inventory_changed = clipped != inventory_btc
    if killed or not enabled or not has_spot_key or clipped <= 0 or avg_entry is None:
        cancel = resting is not None
        return CycleIntent(
            send=False,
            cancel_resting=cancel,
            fire_kill=False,
            skip_reason="halted" if killed else "switch_off",
            clipped_inventory=clipped if inventory_changed else None,
        )
    cancel_stale = False
    if resting is not None:
        touch = post_only_price(resting.side, bid=book.bid, ask=book.ask)
        if resting.price != touch:
            cancel_stale = True
    # Card #1025 (findings F1/F2): the end-of-window escape is evaluated
    # BEFORE the `exit_resting` return below — that return used to come first
    # and made the escape unreachable whenever the bot's passive exit was
    # resting and unfilled. The trigger is the first cycle that reaches
    # HOLD_AFTER_FILL_S with the position open, not the `stuck` mark (930 s).
    # No price ceiling: the aggressive order exits whatever the price.
    if seconds_since_fill >= float(HOLD_AFTER_FILL_S):
        return CycleIntent(
            send=True,
            cancel_resting=resting is not None,
            fire_kill=False,
            skip_reason=None,
            side="SELL",
            price=None,
            quote_qty=None,
            quantity=clipped,
            order_type=AGGRESSIVE_ORDER_TYPE,
            time_in_force="",
            clipped_inventory=clipped if inventory_changed else None,
            aggressive_exit=True,
        )
    if resting is not None:
        return CycleIntent(
            send=False,
            cancel_resting=cancel_stale,
            fire_kill=False,
            skip_reason="exit_resting",
            clipped_inventory=clipped if inventory_changed else None,
        )
    if stuck:
        # Kept for callers that pass the mark directly; the escape above
        # already fires at the window end, so a position is never inert there.
        return CycleIntent(
            send=False,
            cancel_resting=False,
            fire_kill=False,
            skip_reason="stuck",
            clipped_inventory=clipped if inventory_changed else None,
        )
    ret_bp = position_ret_bp(avg_entry, book.mid)
    if not should_post_exit(ret_bp=ret_bp):
        return CycleIntent(
            send=False,
            cancel_resting=False,
            fire_kill=False,
            skip_reason="hold_position",
            clipped_inventory=clipped if inventory_changed else None,
        )
    price = post_only_price("SELL", bid=book.bid, ask=book.ask)
    quantity = clipped
    quote_qty = quantity * price
    if quantity <= 0 or would_cross("SELL", price, bid=book.bid, ask=book.ask):
        return CycleIntent(
            send=False,
            cancel_resting=cancel_stale,
            fire_kill=False,
            skip_reason="would_cross",
            clipped_inventory=clipped if inventory_changed else None,
        )
    return CycleIntent(
        send=True,
        cancel_resting=False,
        fire_kill=False,
        skip_reason=None,
        side="SELL",
        price=price,
        quote_qty=quote_qty,
        quantity=quantity,
        order_type=ORDER_TYPE,
        time_in_force=TIME_IN_FORCE,
        clipped_inventory=clipped if inventory_changed else None,
    )
