"""Card #1025 — D: regime gate (maker cost + 50% slack) and fixed geometry."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.services.scalp_engine import (
    EXIT_STOP_BP,
    EXIT_TARGET_BP,
    HOLD_AFTER_FILL_S,
    Book,
    JevSignal,
    decide_cycle,
)
from app.services.scalp_window import (
    entry_hurdle_bp,
    entry_hurdle_bp_with_slack,
    passes_entry_hurdle,
    passes_regime_gate,
)


def _book() -> Book:
    return Book(bid=Decimal("65000"), ask=Decimal("65010"))


def _cycle(
    *,
    expected_move_bp: Decimal,
    fee_bp: Decimal = Decimal("10"),
    spread_bp: Decimal = Decimal("0"),
    confidence: Decimal = Decimal("0.9"),
):
    jev = JevSignal(
        side="BUY",
        confidence=confidence,
        expected_move_bp=expected_move_bp,
        book_toxic=False,
        latency_ms=50,
    )
    return decide_cycle(
        enabled=True,
        killed=False,
        has_spot_key=True,
        jev_available=True,
        jev_in_flight=False,
        last_jev_elapsed_ms=1000,
        inventory_btc=Decimal("0"),
        floor_btc=Decimal("0"),
        free_usdt=Decimal("200"),
        free_btc=Decimal("0"),
        day_pnl=Decimal("0"),
        book=_book(),
        resting=None,
        jev=jev,
        fee_bp=fee_bp,
        spread_bp=spread_bp,
    )


def test_regime_threshold_is_the_hurdle_with_fifty_percent_slack():
    assert entry_hurdle_bp(Decimal("10"), Decimal("2")) == Decimal("22")
    assert entry_hurdle_bp_with_slack(Decimal("10"), Decimal("2")) == Decimal("33")
    assert passes_regime_gate(Decimal("33"), Decimal("10"), Decimal("2")) is True
    assert passes_regime_gate(Decimal("32.9"), Decimal("10"), Decimal("2")) is False
    # The bare hurdle keeps its own (strict) meaning: below cost.
    assert passes_entry_hurdle(Decimal("22"), Decimal("10"), Decimal("2")) is False
    assert passes_entry_hurdle(Decimal("22.1"), Decimal("10"), Decimal("2")) is True


def test_calm_regime_refuses_with_the_regime_token_and_no_order():
    intent = _cycle(expected_move_bp=Decimal("25"))
    assert intent.send is False
    assert intent.skip_reason == "regime"
    assert intent.price is None and intent.quantity is None


def test_active_regime_is_allowed():
    intent = _cycle(expected_move_bp=Decimal("31"))
    assert intent.send is True
    assert intent.skip_reason is None
    assert intent.side == "BUY"


def test_below_cost_is_hurdle_and_above_cost_without_slack_is_regime():
    below = _cycle(expected_move_bp=Decimal("19"))
    assert below.skip_reason == "hurdle"

    without_slack = _cycle(expected_move_bp=Decimal("25"))
    assert without_slack.skip_reason == "regime"

    with_slack = _cycle(expected_move_bp=Decimal("30"))
    assert with_slack.send is True


def test_regime_gate_uses_the_real_maker_cost():
    # Maker real 7,5 bp + spread 0,5 → hurdle 15,5 → gate exige 23,25.
    assert (
        _cycle(
            expected_move_bp=Decimal("23"), fee_bp=Decimal("7.5"), spread_bp=Decimal("0.5")
        ).skip_reason
        == "regime"
    )
    assert (
        _cycle(expected_move_bp=Decimal("24"), fee_bp=Decimal("7.5"), spread_bp=Decimal("0.5")).send
        is True
    )


def test_regime_token_comes_before_toxic_book():
    jev = JevSignal(
        side="BUY",
        confidence=Decimal("0.9"),
        expected_move_bp=Decimal("25"),
        book_toxic=True,
        latency_ms=50,
    )
    intent = decide_cycle(
        enabled=True,
        killed=False,
        has_spot_key=True,
        jev_available=True,
        jev_in_flight=False,
        last_jev_elapsed_ms=1000,
        inventory_btc=Decimal("0"),
        floor_btc=Decimal("0"),
        free_usdt=Decimal("200"),
        free_btc=Decimal("0"),
        day_pnl=Decimal("0"),
        book=_book(),
        resting=None,
        jev=jev,
        fee_bp=Decimal("10"),
        spread_bp=Decimal("0"),
    )
    assert intent.skip_reason == "regime"


def test_no_environment_switch_disables_the_regime_gate(monkeypatch):
    for name in (
        "SCALP_REGIME_GATE",
        "SCALP_REGIME_GATE_ENABLED",
        "SCALP_DISABLE_REGIME",
        "REGIME_GATE",
    ):
        monkeypatch.setenv(name, "0")
    monkeypatch.setenv("RUN_SCALP_LOOP", "1")
    intent = _cycle(expected_move_bp=Decimal("25"))
    assert intent.skip_reason == "regime"
    assert intent.send is False


def test_geometry_and_waiting_window_are_unchanged_without_the_ruler():
    """Card A declared an insufficient sample: geometry and window stay put."""
    assert EXIT_TARGET_BP == Decimal("35")
    assert EXIT_STOP_BP == Decimal("-28")
    assert HOLD_AFTER_FILL_S == 900
