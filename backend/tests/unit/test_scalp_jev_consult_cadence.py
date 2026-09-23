"""Card #1025 — F: Jev consult cadence, payload budget and measured latency."""

from __future__ import annotations

import time
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import ScalpFill, ScalpUserState, UserExchangeCredential
from app.services import scalp_jev
from app.services.scalp_engine import (
    JEV_FLOOR_MS,
    JEV_LATE_MS,
    JEV_TARGET_MS,
    Book,
    JevSignal,
    decide_cycle,
)
from app.services.scalp_jev import (
    _EXPECTED_MOVE_BP_LEVELS_BP,
    _systemone_payload,
    request_jev,
    systemone_input_tokens,
)
from app.services.scalp_jev_payload import RECENT_TRADES_N, build_jev_payload
from app.services.scalp_service import _jev_target_ms, get_or_create_state, set_switch, tick_user
from test_scalp_direcional_jev import (
    FakeExchange,
    _FakeHttpResponse,
    _add_key,
    _buy_signal,
    _capture_urlopen,
    _diagnostic_call_payload,
    _systemone_response,
)


@pytest.fixture(autouse=True)
def _scalp_stream_memory():
    import random

    from app.services.scalp_btcusdt_stream import get_scalp_btcusdt_memory

    mem = get_scalp_btcusdt_memory()
    mem.reset_for_tests()
    mem.set_ws_connected(True)
    now_ms = int(time.time() * 1000)
    mem.ingest_book_ticker(
        {
            "s": "BTCUSDT",
            "b": "85529.85",
            "a": "85529.86",
            "B": "3.65146",
            "A": "2.70834",
            "E": now_ms,
        }
    )
    price = Decimal("85529.86")
    for index in range(300):
        price = price * (Decimal("1") + Decimal(str(random.uniform(-0.00005, 0.00005))))
        mem.ingest_agg_trade(
            {
                "s": "BTCUSDT",
                "p": str(price),
                "q": str(round(random.uniform(0.0001, 0.5), 5)),
                "T": now_ms - (300 - index) * 1000,
                "m": random.random() < 0.5,
            }
        )
    yield
    mem.reset_for_tests()


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


def _book() -> Book:
    return Book(bid=Decimal("65000"), ask=Decimal("65010"))


def test_cadence_defaults_to_thirty_seconds_and_cuts_requests_per_hour():
    assert JEV_TARGET_MS == 30000
    requests_at_one_hz = 3600
    requests_now = 3_600_000 / JEV_TARGET_MS
    assert requests_at_one_hz >= 15 * requests_now
    assert requests_now == 120


def test_loop_interval_and_fail_closed_are_untouched():
    assert JEV_FLOOR_MS == 400
    assert max(JEV_FLOOR_MS / 1000.0, 0.4) == 0.4
    assert JEV_LATE_MS == 1500


def test_cadence_is_configurable_by_env(monkeypatch):
    monkeypatch.delenv("SCALP_JEV_TARGET_MS", raising=False)
    assert _jev_target_ms() == JEV_TARGET_MS
    monkeypatch.setenv("SCALP_JEV_TARGET_MS", "5000")
    assert _jev_target_ms() == 5000
    for bad in ("", "abc", "0", "-1"):
        monkeypatch.setenv("SCALP_JEV_TARGET_MS", bad)
        assert _jev_target_ms() == JEV_TARGET_MS


def test_engine_receives_the_cadence_and_never_reads_the_environment():
    source = Path(scalp_jev.__file__).resolve().parents[0] / "scalp_engine.py"
    assert "getenv" not in source.read_text(encoding="utf-8")
    assert "environ" not in source.read_text(encoding="utf-8")

    too_soon = decide_cycle(
        enabled=True,
        killed=False,
        has_spot_key=True,
        jev_available=True,
        jev_in_flight=False,
        last_jev_elapsed_ms=20000,
        inventory_btc=Decimal("0"),
        floor_btc=Decimal("0"),
        free_usdt=Decimal("200"),
        free_btc=Decimal("0"),
        day_pnl=Decimal("0"),
        book=_book(),
        resting=None,
        jev=None,
        jev_target_ms=30000,
    )
    assert too_soon.skip_reason == "jev_target"
    assert too_soon.call_jev is False

    ready = decide_cycle(
        enabled=True,
        killed=False,
        has_spot_key=True,
        jev_available=True,
        jev_in_flight=False,
        last_jev_elapsed_ms=20000,
        inventory_btc=Decimal("0"),
        floor_btc=Decimal("0"),
        free_usdt=Decimal("200"),
        free_btc=Decimal("0"),
        day_pnl=Decimal("0"),
        book=_book(),
        resting=None,
        jev=None,
        jev_target_ms=10000,
    )
    assert ready.skip_reason == "need_jev"
    assert ready.call_jev is True


def test_tick_uses_the_env_cadence(scalp_db, monkeypatch):
    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    state = get_or_create_state(scalp_db, user_id)
    stale = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(seconds=20)
    state.last_jev_at = stale
    scalp_db.commit()

    calls = {"n": 0}

    def jev_fn(_payload):
        calls["n"] += 1
        return _buy_signal()

    result = tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        jev_fn=jev_fn,
        free_usdt=Decimal("80"),
        free_btc=Decimal("0.01"),
        book=_book(),
    )
    assert result.skipped == "jev_target", "default 30 s cadence holds"
    assert calls["n"] == 0

    monkeypatch.setenv("SCALP_JEV_TARGET_MS", "5000")
    state = get_or_create_state(scalp_db, user_id)
    state.last_jev_at = stale
    scalp_db.commit()
    tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        jev_fn=jev_fn,
        free_usdt=Decimal("80"),
        free_btc=Decimal("0.01"),
        book=_book(),
    )
    assert calls["n"] == 1, "the env cadence drives the jev_target gate"


def test_payload_stays_within_the_token_budget_with_the_ladder_intact():
    from datetime import timezone as _tz

    from app.services.scalp_btcusdt_stream import get_scalp_btcusdt_memory

    body, skip = build_jev_payload(
        inventory_btc=Decimal("0.0005"),
        free_usdt=Decimal("80"),
        fee_bp=Decimal("7.5"),
        bnb_fee_active=True,
        resting=None,
        rest_opened_at=None,
        now=datetime.now(_tz.utc).replace(tzinfo=None),
        memory=get_scalp_btcusdt_memory(),
    )
    assert skip is None
    assert systemone_input_tokens(body) <= 500

    systemone = _systemone_payload(body)
    criteria = systemone["questions"]["expected_move_bp"]["criteria"]
    assert criteria == [f"{bp} bp" for bp in _EXPECTED_MOVE_BP_LEVELS_BP]
    assert _EXPECTED_MOVE_BP_LEVELS_BP == (0, 5, 10, 15, 20, 25, 30, 35, 50, 80)
    assert systemone["questions"]["expected_move_bp"]["type"] == "score"

    window = body["state"]["window"]
    assert 0 < len(window["recent_trades"]) <= RECENT_TRADES_N
    assert "trades" not in window, "no full tick dump"
    assert window["horizon_s"] == 900
    for field in ("ret_bp", "vol_bp", "aggressor_flow", "spread_bp_mean", "trade_count"):
        assert field in window


def test_latency_measures_the_call_and_not_the_entry_registration(monkeypatch):
    monkeypatch.setenv("JEV_API_KEY", "super-secret-jev-token")
    written: list[str] = []

    def slow_entry(*, call_id, systemone):
        time.sleep(0.2)
        written.append(call_id)

    monkeypatch.setattr(scalp_jev, "log_call_entry", slow_entry)

    def ok(_req, _timeout, _captured):
        response = _FakeHttpResponse(_systemone_response())
        response.status = 200
        return response

    _capture_urlopen(monkeypatch, ok)
    signal = request_jev(_diagnostic_call_payload())
    assert written, "the #1015 entry record is still written"
    assert signal.latency_ms < 200, "the entry registration is outside the clock"
    assert signal.side == "BUY"


def test_a_prompt_reply_is_not_refused_as_late():
    signal = JevSignal(
        side="BUY",
        confidence=Decimal("0.9"),
        expected_move_bp=Decimal("35"),
        book_toxic=False,
        latency_ms=200,
    )
    intent = decide_cycle(
        enabled=True,
        killed=False,
        has_spot_key=True,
        jev_available=True,
        jev_in_flight=False,
        last_jev_elapsed_ms=JEV_TARGET_MS,
        inventory_btc=Decimal("0"),
        floor_btc=Decimal("0"),
        free_usdt=Decimal("200"),
        free_btc=Decimal("0"),
        day_pnl=Decimal("0"),
        book=_book(),
        resting=None,
        jev=signal,
    )
    assert intent.skip_reason != "jev_late"
    assert intent.send is True
