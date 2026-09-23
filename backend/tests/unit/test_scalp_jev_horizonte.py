from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import ScalpFill, ScalpUserState, UserExchangeCredential

from app.services.scalp_engine import (
    ENTRY_REST_TIMEOUT_S,
    EXIT_TARGET_BP,
    HORIZON_S,
    JEV_LATE_MS,
    Book,
    decide_cycle,
    decide_exit_cycle,
    should_mark_stuck,
    should_post_exit,
)
from app.services.scalp_jev_payload import build_jev_payload
from app.services.scalp_window import passes_entry_hurdle
from app.services.scalp_btcusdt_stream import get_scalp_btcusdt_memory
from app.services.scalp_service import (
    _maybe_cancel_entry_timeout,
    get_or_create_state,
    set_switch,
    tick_user,
)
from test_scalp_direcional_jev import FakeExchange, _add_key, _book


@pytest.fixture
def scalp_db(postgres_isolation, unit_database_url):
    from app.database import ensure_runtime_schema_migrations

    ensure_runtime_schema_migrations()
    engine = create_engine(unit_database_url)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    db.query(ScalpFill).delete()
    db.query(ScalpUserState).delete()
    db.query(UserExchangeCredential).delete()
    db.commit()
    try:
        yield db
    finally:
        db.query(ScalpFill).delete()
        db.query(ScalpUserState).delete()
        db.query(UserExchangeCredential).delete()
        db.commit()
        db.close()
        engine.dispose()


def test_horizon_constant_900():
    assert HORIZON_S == 900
    assert JEV_LATE_MS == 1500


def test_hurdle_10_bp_move_does_not_pass():
    assert passes_entry_hurdle(Decimal("10"), Decimal("10"), Decimal("0.1")) is False


def test_empty_window_skips_jev_payload():
    import time

    mem = get_scalp_btcusdt_memory()
    mem.reset_for_tests()
    mem.set_ws_connected(True)
    now_ms = int(time.time() * 1000)
    mem.ingest_book_ticker(
        {
            "s": "BTCUSDT",
            "b": "65000",
            "a": "65010",
            "B": "1.2",
            "A": "0.8",
            "E": now_ms,
        }
    )
    body, skip = build_jev_payload(
        inventory_btc=Decimal("0"),
        free_usdt=Decimal("100"),
        fee_bp=Decimal("10"),
        bnb_fee_active=False,
        resting=None,
        rest_opened_at=None,
        now=__import__("datetime").datetime.utcnow(),
        memory=mem,
    )
    assert body is None
    assert skip == "window_empty"


def test_stuck_after_15m30s():
    assert should_mark_stuck(929) is False
    assert should_mark_stuck(930) is True


def test_exit_triggers_on_target():
    assert should_post_exit(ret_bp=Decimal("35")) is True
    assert should_post_exit(ret_bp=Decimal("-28")) is True
    # Card #1025: the waiting-window end no longer posts a passive exit —
    # that cycle goes aggressive (see test_scalp_aggressive_exit.py).
    assert should_post_exit(ret_bp=Decimal("10")) is False


def test_decide_cycle_rejects_low_hurdle():
    from app.services.scalp_engine import Book, JevSignal

    book = Book(bid=Decimal("65000"), ask=Decimal("65010"))
    jev = JevSignal(
        side="BUY",
        confidence=Decimal("0.8"),
        expected_move_bp=Decimal("10"),
        book_toxic=False,
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
        book=book,
        resting=None,
        jev=jev,
        fee_bp=Decimal("10"),
        spread_bp=Decimal("0.1"),
    )
    assert intent.send is False
    assert intent.skip_reason == "hurdle"


def test_decide_exit_cycle_holds_until_target_or_time():
    book = Book(bid=Decimal("65000"), ask=Decimal("65010"))
    intent = decide_exit_cycle(
        enabled=True,
        killed=False,
        has_spot_key=True,
        inventory_btc=Decimal("0.001"),
        free_btc=Decimal("0.01"),
        floor_btc=Decimal("0"),
        avg_entry=Decimal("65000"),
        book=book,
        resting=None,
        seconds_since_fill=60.0,
        stuck=False,
    )
    assert intent.send is False
    assert intent.skip_reason == "hold_position"


def test_decide_exit_cycle_posts_sell_on_target_bp():
    book = Book(bid=Decimal("65230"), ask=Decimal("65240"))
    intent = decide_exit_cycle(
        enabled=True,
        killed=False,
        has_spot_key=True,
        inventory_btc=Decimal("0.001"),
        free_btc=Decimal("0.01"),
        floor_btc=Decimal("0"),
        avg_entry=Decimal("65000"),
        book=book,
        resting=None,
        seconds_since_fill=10.0,
        stuck=False,
    )
    assert intent.send is True
    assert intent.side == "SELL"
    ret_bp = (book.mid / Decimal("65000") - Decimal("1")) * Decimal("10000")
    assert ret_bp >= EXIT_TARGET_BP


def test_maybe_cancel_entry_timeout_clears_stale_rest(scalp_db):
    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    state = get_or_create_state(scalp_db, user_id)
    cred = (
        scalp_db.query(UserExchangeCredential)
        .filter(UserExchangeCredential.user_id == user_id)
        .one()
    )
    now = datetime.utcnow()
    state.rest_client_order_id = "cfscalp_entry_timeout"
    state.rest_side = "BUY"
    state.rest_price = Decimal("65000")
    state.rest_role = "entry"
    state.rest_opened_at = now - timedelta(seconds=ENTRY_REST_TIMEOUT_S + 1)
    scalp_db.commit()
    fx = FakeExchange()
    _maybe_cancel_entry_timeout(state, cred=cred, exchange=fx, now=now)
    assert state.rest_client_order_id is None
    assert state.rest_role is None
    assert "cfscalp_entry_timeout" in fx.cancelled


class _CancelFailingExchange(FakeExchange):
    def cancel_bot_order(self, **kwargs):
        from app.services.binance_spot_orders import BinanceOrderError

        raise BinanceOrderError("cancel refused", code=-2011)


def test_maybe_cancel_entry_timeout_keeps_state_when_cancel_fails(scalp_db):
    """E3 fail-soft: cancelamento falhado mantém o estado resting e o timeout.

    A ordem pode continuar viva; limpar ``rest_opened_at``/``rest_role`` aqui
    deixaria o id vivo com o timeout silenciado (nunca voltaria a disparar).
    """
    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    state = get_or_create_state(scalp_db, user_id)
    cred = (
        scalp_db.query(UserExchangeCredential)
        .filter(UserExchangeCredential.user_id == user_id)
        .one()
    )
    now = datetime.utcnow()
    state.rest_client_order_id = "cfscalp_entry_timeout"
    state.rest_side = "BUY"
    state.rest_price = Decimal("65000")
    state.rest_role = "entry"
    state.rest_opened_at = now - timedelta(seconds=ENTRY_REST_TIMEOUT_S + 1)
    scalp_db.commit()

    _maybe_cancel_entry_timeout(state, cred=cred, exchange=_CancelFailingExchange(), now=now)
    assert state.rest_client_order_id == "cfscalp_entry_timeout"
    assert state.rest_role == "entry"
    assert state.rest_opened_at is not None, "o timeout volta a disparar no ciclo seguinte"

    # O ciclo seguinte re-tenta; com o cancelamento aceite o estado é limpo.
    fx = FakeExchange()
    _maybe_cancel_entry_timeout(state, cred=cred, exchange=fx, now=now)
    assert state.rest_client_order_id is None
    assert state.rest_role is None
    assert state.rest_opened_at is None
    assert "cfscalp_entry_timeout" in fx.cancelled


def test_tick_user_with_open_position_holds_without_jev(scalp_db, monkeypatch):
    monkeypatch.setattr(
        "app.services.scalp_btcusdt_snapshot_store.publish_scalp_btcusdt_snapshot",
        lambda **_kwargs: None,
    )
    get_scalp_btcusdt_memory().reset_for_tests()
    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    state = get_or_create_state(scalp_db, user_id)
    state.floor_btc = Decimal("0")
    state.inventory_btc = Decimal("0.001")
    state.avg_entry_quote = Decimal("65000")
    state.position_opened_at = datetime.utcnow() - timedelta(seconds=120)
    scalp_db.commit()
    result = tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        free_usdt=Decimal("200"),
        free_btc=Decimal("0.01"),
        book=_book(),
    )
    assert result.sent is False
    assert result.skipped == "hold_position"
    assert fx.placed == []
