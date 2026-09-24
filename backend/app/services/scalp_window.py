"""Rolling 15 min window aggregates from scalp BTCUSDT stream memory."""

from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Sequence

from app.services.scalp_btcusdt_stream import AggTradeTick

HORIZON_S = 900


@dataclass(frozen=True)
class TouchMetrics:
    bid: Decimal
    ask: Decimal
    bid_qty: Decimal
    ask_qty: Decimal
    mid: Decimal
    spread_bp: Decimal
    microprice: Decimal
    imbalance: Decimal
    age_ms: int


@dataclass(frozen=True)
class WindowMetrics:
    horizon_s: int
    trade_count: int
    ret_bp: Decimal
    vol_bp: Decimal
    aggressor_flow: Decimal
    volume: Decimal
    spread_bp_mean: Decimal


def touch_metrics(
    *,
    bid: Decimal,
    ask: Decimal,
    bid_qty: Decimal,
    ask_qty: Decimal,
    age_ms: int,
) -> TouchMetrics:
    mid = (bid + ask) / Decimal("2") if bid > 0 and ask > 0 else Decimal("0")
    spread_bp = Decimal("0")
    if mid > 0:
        spread_bp = (ask - bid) / mid * Decimal("10000")
    denom = bid_qty + ask_qty
    if denom > 0:
        microprice = (bid * ask_qty + ask * bid_qty) / denom
        imbalance = (bid_qty - ask_qty) / denom
    else:
        microprice = mid
        imbalance = Decimal("0")
    return TouchMetrics(
        bid=bid,
        ask=ask,
        bid_qty=bid_qty,
        ask_qty=ask_qty,
        mid=mid,
        spread_bp=spread_bp,
        microprice=microprice,
        imbalance=imbalance,
        age_ms=age_ms,
    )


def window_metrics(
    trades: Sequence[AggTradeTick],
    *,
    spread_samples_bp: Sequence[Decimal],
    horizon_s: int = HORIZON_S,
) -> Optional[WindowMetrics]:
    if not trades:
        return None
    prices = [t.price for t in trades if t.price > 0]
    if not prices:
        return None
    first = prices[0]
    last = prices[-1]
    ret_bp = Decimal("0")
    if first > 0:
        ret_bp = (last / first - Decimal("1")) * Decimal("10000")
    log_returns: list[float] = []
    for i in range(1, len(prices)):
        p0 = float(prices[i - 1])
        p1 = float(prices[i])
        if p0 > 0 and p1 > 0:
            log_returns.append(math.log(p1 / p0))
    vol_bp = Decimal("0")
    if len(log_returns) >= 2:
        mean = sum(log_returns) / len(log_returns)
        var = sum((x - mean) ** 2 for x in log_returns) / len(log_returns)
        vol_bp = Decimal(str(math.sqrt(var) * 10000))
    aggressor = Decimal("0")
    volume = Decimal("0")
    for t in trades:
        volume += t.quantity
        sign = Decimal("-1") if t.is_buyer_maker else Decimal("1")
        aggressor += sign * t.quantity
    spread_mean = Decimal("0")
    if spread_samples_bp:
        spread_mean = sum(spread_samples_bp, Decimal("0")) / Decimal(len(spread_samples_bp))
    return WindowMetrics(
        horizon_s=horizon_s,
        trade_count=len(trades),
        ret_bp=ret_bp,
        vol_bp=vol_bp,
        aggressor_flow=aggressor,
        volume=volume,
        spread_bp_mean=spread_mean,
    )


def entry_hurdle_bp(fee_bp: Decimal, spread_bp: Decimal) -> Decimal:
    return Decimal("2") * fee_bp + spread_bp


def passes_entry_hurdle(expected_move_bp: Decimal, fee_bp: Decimal, spread_bp: Decimal) -> bool:
    return expected_move_bp > entry_hurdle_bp(fee_bp, spread_bp)


# Card #1025, regime gate: maker cost plus 50% of slack (P3 placement).
REGIME_SLACK = Decimal("1.5")


def entry_hurdle_bp_with_slack(fee_bp: Decimal, spread_bp: Decimal) -> Decimal:
    """The entry hurdle the regime gate demands: maker cost + 50% slack."""
    return entry_hurdle_bp(fee_bp, spread_bp) * REGIME_SLACK


def passes_regime_gate(expected_move_bp: Decimal, fee_bp: Decimal, spread_bp: Decimal) -> bool:
    """The forecast covers the maker cost with 50% slack.

    The forecast (``expected_move_bp``) is the **primary and only** input:
    σ of the window (``vol_bp``) is not read here (the Card A ruler did not
    justify it as a secondary condition).
    """
    return expected_move_bp >= entry_hurdle_bp_with_slack(fee_bp, spread_bp)


# Card #1029: names of the three bands of a level's **exact** bp against the
# **real cost of that cycle**. They are labels of the two comparisons above,
# read in this order: covers with slack (>= hurdle × 1.5) implies covers the
# cost (strict > hurdle), which implies not below it. No boundary is added to
# the scale and no new threshold or constant is introduced.
MOVE_BAND_BELOW_COST = "below_cost"
MOVE_BAND_COVERS_COST = "covers_cost"
MOVE_BAND_COVERS_WITH_SLACK = "covers_with_slack"


def move_band(expected_move_bp: Decimal, fee_bp: Decimal, spread_bp: Decimal) -> str:
    """Band of a level's exact bp against the cycle's real cost (card #1029).

    Deliberately a thin reading over ``passes_regime_gate`` / ``passes_entry_hurdle``
    with their current boundaries (``>=`` and strict ``>``), so the band the
    model sees and the band the entry decision reads come from the same rules.
    """
    if passes_regime_gate(expected_move_bp, fee_bp, spread_bp):
        return MOVE_BAND_COVERS_WITH_SLACK
    if passes_entry_hurdle(expected_move_bp, fee_bp, spread_bp):
        return MOVE_BAND_COVERS_COST
    return MOVE_BAND_BELOW_COST
