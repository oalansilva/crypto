from __future__ import annotations

import io
import json
import logging
import logging.handlers
import os
import urllib.error
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.middleware.authMiddleware import get_current_user
from app.models import ScalpFill, ScalpUserState, UserExchangeCredential
from app.routes import scalp as scalp_route
from app.services.scalp_engine import (
    CLIENT_ORDER_PREFIX,
    CROSS_REJECT_CODES,
    JEV_FLOOR_MS,
    JEV_LATE_MS,
    JEV_TARGET_MS,
    ORDER_TYPE,
    TIME_IN_FORCE,
    Book,
    JevSignal,
    RestingOrder,
    clip_inventory,
    compute_t,
    decide_cycle,
    is_bot_client_order_id,
    panel_state,
    pnl_quote,
    should_kill,
)
from app.services.scalp_jev import (
    _EXPECTED_MOVE_BP_LEVELS_BP,
    _bp_from_score,
    _error_body,
    _expected_move_bp,
    request_jev,
)
from app.services.scalp_jev_log import (
    ERROR_BODY_CHARS,
    ERROR_BODY_READ_BYTES,
    MAX_LOG_BYTES,
    TailTruncatingFileHandler,
    install_diagnostic_log,
    log_call_entry,
    log_call_error,
    log_cycle_refusal,
    logger as diagnostic_logger,
    summarize_account,
)


def _move_bp_to_score(move_bp: float) -> float:
    for index, level_bp in enumerate(_EXPECTED_MOVE_BP_LEVELS_BP):
        if level_bp == move_bp:
            return float(index)
    raise ValueError(f"move_bp {move_bp} not on expected_move_bp score ladder")


from app.services.scalp_service import (
    apply_bot_fill,
    get_or_create_state,
    set_switch,
    status_payload,
    tick_user,
)
from app.services.user_exchange_credentials import BINANCE_PROVIDER


def _buy_signal(**overrides) -> JevSignal:
    values = dict(
        side="BUY",
        confidence=Decimal("0.8"),
        # Card #1025: the signal used as "passes the gates" clears the regime
        # gate too (hurdle + 50% slack) with the conservative 10 bp fee and the
        # seeded ~1,5 bp spread.
        expected_move_bp=Decimal("35"),
        book_toxic=False,
        latency_ms=50,
        cost_quote=Decimal("0"),
    )
    values.update(overrides)
    return JevSignal(**values)


def _seed_stream_for_jev() -> None:
    import time

    from app.services.scalp_btcusdt_stream import get_scalp_btcusdt_memory

    mem = get_scalp_btcusdt_memory()
    mem.reset_for_tests()
    mem.set_ws_connected(True)
    now_ms = int(time.time() * 1000)
    mem.ingest_book_ticker(
        {"s": "BTCUSDT", "b": "65000", "a": "65010", "B": "1.2", "A": "0.8", "E": now_ms}
    )
    mem.ingest_agg_trade({"s": "BTCUSDT", "p": "65000", "q": "0.01", "T": now_ms, "m": False})


def _book() -> Book:
    return Book(bid=Decimal("65000"), ask=Decimal("65010"))


def test_compute_t_caps_and_uses_free_usdt():
    assert compute_t(Decimal("500")) == Decimal("100.00")
    t = compute_t(Decimal("99.63"))
    assert t < Decimal("100")
    assert t >= Decimal("99")
    assert compute_t(Decimal("0")) == Decimal("0")


def test_kill_at_minus_two_percent_of_t():
    assert should_kill(day_pnl=Decimal("-2"), t=Decimal("100")) is True
    assert should_kill(day_pnl=Decimal("-1.99"), t=Decimal("100")) is False


def test_inventory_clip_never_sells_floor():
    assert clip_inventory(
        bot_inventory=Decimal("0.02"),
        free_btc=Decimal("0.011"),
        floor_btc=Decimal("0.01"),
    ) == Decimal("0.001")
    assert clip_inventory(
        bot_inventory=Decimal("0"),
        free_btc=Decimal("0.5"),
        floor_btc=Decimal("0.5"),
    ) == Decimal("0")


def test_hold_is_default_and_post_only_buy_when_gates_pass():
    hold = decide_cycle(
        enabled=True,
        killed=False,
        has_spot_key=True,
        jev_available=True,
        jev_in_flight=False,
        last_jev_elapsed_ms=1000,
        inventory_btc=Decimal("0"),
        floor_btc=Decimal("0.01"),
        free_usdt=Decimal("200"),
        free_btc=Decimal("0.01"),
        day_pnl=Decimal("0"),
        book=_book(),
        resting=None,
        jev=_buy_signal(side=None),
    )
    assert hold.send is False
    assert hold.skip_reason == "hold"

    buy = decide_cycle(
        enabled=True,
        killed=False,
        has_spot_key=True,
        jev_available=True,
        jev_in_flight=False,
        last_jev_elapsed_ms=1000,
        inventory_btc=Decimal("0"),
        floor_btc=Decimal("0.01"),
        free_usdt=Decimal("200"),
        free_btc=Decimal("0.01"),
        day_pnl=Decimal("0"),
        book=_book(),
        resting=None,
        jev=_buy_signal(),
    )
    assert buy.send is True
    assert buy.side == "BUY"
    assert buy.order_type == ORDER_TYPE == "LIMIT"
    assert buy.time_in_force == TIME_IN_FORCE == "GTX"
    assert buy.price == Decimal("65000")
    assert buy.quote_qty <= Decimal("10")
    assert "MARKET" not in (buy.order_type, buy.time_in_force)
    assert "IOC" not in (buy.order_type, buy.time_in_force)


def test_zero_inventory_does_not_sell_floor():
    intent = decide_cycle(
        enabled=True,
        killed=False,
        has_spot_key=True,
        jev_available=True,
        jev_in_flight=False,
        last_jev_elapsed_ms=1000,
        inventory_btc=Decimal("0"),
        floor_btc=Decimal("0.5"),
        free_usdt=Decimal("200"),
        free_btc=Decimal("0.5"),
        day_pnl=Decimal("0"),
        book=_book(),
        resting=None,
        jev=_buy_signal(side="SELL"),
    )
    assert intent.send is False
    assert intent.skip_reason == "zero_inventory"


def test_late_jev_and_in_flight_and_book_move():
    late = decide_cycle(
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
        jev=_buy_signal(latency_ms=1501),
    )
    assert late.send is False
    assert late.skip_reason == "jev_late"

    inflight = decide_cycle(
        enabled=True,
        killed=False,
        has_spot_key=True,
        jev_available=True,
        jev_in_flight=True,
        last_jev_elapsed_ms=1000,
        inventory_btc=Decimal("0"),
        floor_btc=Decimal("0"),
        free_usdt=Decimal("200"),
        free_btc=Decimal("0"),
        day_pnl=Decimal("0"),
        book=_book(),
        resting=RestingOrder("cfscalp_abc", "BUY", Decimal("64900")),
        jev=None,
    )
    assert inflight.call_jev is False
    assert inflight.cancel_resting is True

    stale = decide_cycle(
        enabled=True,
        killed=False,
        has_spot_key=True,
        jev_available=True,
        jev_in_flight=False,
        last_jev_elapsed_ms=50,
        inventory_btc=Decimal("0"),
        floor_btc=Decimal("0"),
        free_usdt=Decimal("200"),
        free_btc=Decimal("0"),
        day_pnl=Decimal("0"),
        book=_book(),
        resting=RestingOrder("cfscalp_abc", "BUY", Decimal("64000")),
        jev=None,
    )
    assert stale.cancel_resting is True
    assert stale.send is False


def test_no_spot_key_and_no_jev_do_not_send():
    no_key = decide_cycle(
        enabled=True,
        killed=False,
        has_spot_key=False,
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
        jev=_buy_signal(),
    )
    assert no_key.send is False
    assert no_key.skip_reason == "no_spot_key"

    no_jev = decide_cycle(
        enabled=True,
        killed=False,
        has_spot_key=True,
        jev_available=False,
        jev_in_flight=False,
        last_jev_elapsed_ms=1000,
        inventory_btc=Decimal("0"),
        floor_btc=Decimal("0"),
        free_usdt=Decimal("200"),
        free_btc=Decimal("0"),
        day_pnl=Decimal("0"),
        book=_book(),
        resting=None,
        jev=None,
    )
    assert no_jev.send is False
    assert no_jev.skip_reason == "jev_unavailable"


def test_switch_off_default_and_pnl_formula():
    assert panel_state(has_spot_key=True, enabled=False, killed=False) == "off"
    assert panel_state(has_spot_key=False, enabled=True, killed=False) == "nokey"
    assert panel_state(has_spot_key=True, enabled=False, killed=True) == "kill"
    total = pnl_quote(
        realized=Decimal("1"),
        unrealized=Decimal("-3"),
        fees=Decimal("0.1"),
        jev_cost=Decimal("0.2"),
    )
    assert total == Decimal("-2.3")
    assert is_bot_client_order_id("cfscalp_deadbeef")
    assert not is_bot_client_order_id("cftrade_abc")
    assert CLIENT_ORDER_PREFIX == "cfscalp_"
    assert -5022 in CROSS_REJECT_CODES


def test_near_ceiling_only_reducing_side():
    intent = decide_cycle(
        enabled=True,
        killed=False,
        has_spot_key=True,
        jev_available=True,
        jev_in_flight=False,
        last_jev_elapsed_ms=1000,
        inventory_btc=Decimal("0.0016"),
        floor_btc=Decimal("0"),
        free_usdt=Decimal("200"),
        free_btc=Decimal("0.0016"),
        day_pnl=Decimal("0"),
        book=_book(),
        resting=None,
        jev=_buy_signal(side="BUY"),
    )
    assert intent.send is False
    assert intent.skip_reason == "ceiling_reduce_only"


class _FakeHttpResponse:
    def __init__(self, payload: dict | bytes):
        self._raw = payload if isinstance(payload, bytes) else json.dumps(payload).encode("utf-8")

    def read(self):
        return self._raw

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def _systemone_response(
    *,
    side: str = "BUY",
    confidence: float | None = 0.75,
    move_bp: float = 25.0,
    toxic: float = 0.1,
    probabilities: dict[str, float] | None = None,
) -> dict:
    side_answer: dict = {
        "type": "choice",
        "choice": side,
        "probabilities": probabilities or {"BUY": 0.82, "SELL": 0.10, "HOLD": 0.08},
    }
    if confidence is not None:
        side_answer["confidence"] = confidence
    return {
        "model": "jev-1.13.0",
        "answers": {
            "side": side_answer,
            "expected_move_bp": {"type": "score", "score": _move_bp_to_score(move_bp)},
            "book_toxic": {"type": "noul", "noul": toxic},
        },
        "usage": {"input_tokens": 296, "output_tokens": 20},
    }


def _capture_urlopen(monkeypatch, responder):
    captured: dict = {}

    def fake_urlopen(req, timeout=None):
        captured["url"] = req.get_full_url()
        captured["method"] = req.get_method()
        captured["timeout"] = timeout
        captured["body"] = json.loads(req.data.decode("utf-8"))
        captured["headers"] = {key.lower(): value for key, value in req.header_items()}
        return responder(req, timeout, captured)

    monkeypatch.setattr("app.services.scalp_jev.urllib.request.urlopen", fake_urlopen)
    return captured


def test_jev_secret_never_appears_in_logs(monkeypatch):
    monkeypatch.setenv("JEV_API_KEY", "super-secret-jev-token")
    monkeypatch.setenv("JEV_BASE_URL", "http://127.0.0.1:1")
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    logger = logging.getLogger("app.services.scalp_jev")
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)
    try:
        signal = request_jev({"bid": "1"}, timeout_s=0.05)
    finally:
        logger.removeHandler(handler)
    text = stream.getvalue()
    assert "super-secret-jev-token" not in text
    assert "Bearer" not in text
    assert signal.side is None

    stream.truncate(0)
    stream.seek(0)
    logger.addHandler(handler)
    try:

        def boom(_req, _timeout, _captured):
            raise urllib.error.HTTPError(
                "https://api.typesafe.ai/v1/systemone",
                404,
                "Not Found",
                hdrs=None,
                fp=io.BytesIO(b"{}"),
            )

        _capture_urlopen(monkeypatch, boom)
        four_oh_four = request_jev({"bid": "1"})
    finally:
        logger.removeHandler(handler)
    logged = stream.getvalue()
    assert "Jev HTTP error status=404" in logged
    assert "super-secret-jev-token" not in logged
    assert "Bearer" not in logged
    assert four_oh_four.side is None
    assert four_oh_four.confidence == Decimal("0")


def test_request_jev_posts_systemone_not_signal(monkeypatch):
    monkeypatch.setenv("JEV_API_KEY", "super-secret-jev-token")
    monkeypatch.delenv("JEV_BASE_URL", raising=False)

    def ok(_req, _timeout, _captured):
        return _FakeHttpResponse(_systemone_response())

    captured = _capture_urlopen(monkeypatch, ok)
    payload = {
        "state": {
            "symbol": "BTCUSDT",
            "horizon_s": 900,
            "touch": {"bid": "65000", "ask": "65010", "spread_bp": "1.5"},
            "window": {"horizon_s": 900, "trade_count": 1},
            "account": {"inventory_btc": "0", "t": "80", "fee_bp": "10"},
            "resting": None,
        }
    }
    signal = request_jev(payload)
    assert captured["url"] == "https://api.typesafe.ai/v1/systemone"
    assert "/v1/signal" not in captured["url"]
    assert captured["method"] == "POST"
    assert captured["timeout"] == JEV_LATE_MS / 1000.0
    body = captured["body"]
    assert body["model"] == "jev-latest"
    assert set(body["questions"]) == {"side", "expected_move_bp", "book_toxic"}
    assert body["questions"]["side"]["type"] == "choice"
    move_q = body["questions"]["expected_move_bp"]
    assert move_q["type"] == "score"
    assert isinstance(move_q["criteria"], list)
    assert 2 <= len(move_q["criteria"]) <= 10
    assert "35 bp" in move_q["criteria"][7]
    assert "20 bp" in move_q["criteria"][4]
    assert body["questions"]["book_toxic"]["type"] == "noul"
    assert body["state"]["symbol"] == "BTCUSDT"
    assert "edge_after_fees" not in body["questions"]
    assert captured["headers"]["authorization"] == "Bearer super-secret-jev-token"
    assert signal.side == "BUY"


def test_expected_move_bp_score_interpolation_and_legacy_number():
    assert _bp_from_score(5.0) == Decimal("25")
    assert _bp_from_score(4.5) == Decimal("22.5")
    assert _expected_move_bp({"expected_move_bp": {"type": "score", "score": 5.0}}) == Decimal("25")
    assert _expected_move_bp({"expected_move_bp": {"type": "number", "number": 18}}) == Decimal(
        "18"
    )
    assert _expected_move_bp({"expected_move_bp": {"type": "score"}}) == Decimal("0")


def test_request_jev_maps_systemone_buy(monkeypatch):
    monkeypatch.setenv("JEV_API_KEY", "k")
    monkeypatch.setenv("JEV_BASE_URL", "https://api.typesafe.ai/")

    def ok(_req, _timeout, _captured):
        return _FakeHttpResponse(
            _systemone_response(side="BUY", confidence=0.75, move_bp=25.0, toxic=0.1)
        )

    captured = _capture_urlopen(monkeypatch, ok)
    signal = request_jev({"state": {"symbol": "BTCUSDT"}})
    assert captured["url"] == "https://api.typesafe.ai/v1/systemone"
    assert signal.side == "BUY"
    assert signal.confidence == Decimal("0.75")
    assert signal.confidence >= Decimal("0.7")
    assert signal.expected_move_bp == Decimal("25")
    assert signal.book_toxic is False
    assert signal.cost_quote == Decimal("0")


def test_request_jev_hold_and_http_404_are_none(monkeypatch):
    monkeypatch.setenv("JEV_API_KEY", "k")

    def hold(_req, _timeout, _captured):
        return _FakeHttpResponse(
            _systemone_response(side="HOLD", confidence=0.91, move_bp=5.0, toxic=0.1)
        )

    _capture_urlopen(monkeypatch, hold)
    held = request_jev({"bid": "1"})
    assert held.side is None
    assert held.cost_quote == Decimal("0")

    def missing_confidence(_req, _timeout, _captured):
        return _FakeHttpResponse(
            _systemone_response(
                side="BUY",
                confidence=None,
                probabilities={"BUY": 0.71, "SELL": 0.2, "HOLD": 0.09},
            )
        )

    _capture_urlopen(monkeypatch, missing_confidence)
    fallback = request_jev({"bid": "1"})
    assert fallback.side == "BUY"
    assert fallback.confidence == Decimal("0.71")

    def not_found(_req, _timeout, _captured):
        raise urllib.error.HTTPError(
            "https://api.typesafe.ai/v1/systemone",
            404,
            "Not Found",
            hdrs=None,
            fp=io.BytesIO(b"{}"),
        )

    _capture_urlopen(monkeypatch, not_found)
    missing = request_jev({"bid": "1"})
    assert missing.side is None
    assert missing.confidence == Decimal("0")
    assert missing.expected_move_bp == Decimal("0")
    assert missing.book_toxic is False


class FakeExchange:
    def __init__(self):
        self.bid = Decimal("65000")
        self.ask = Decimal("65010")
        self.free_usdt = Decimal("80")
        self.free_btc = Decimal("0.01")
        self.placed: list[dict] = []
        self.aggressive: list[dict] = []
        self.cancelled: list[str] = []
        self.queried: list[str] = []
        self.orders: dict[str, dict] = {}
        self.reject_code = None
        self.aggressive_reject_code = None

    def book(self) -> Book:
        return Book(self.bid, self.ask)

    def free_balances(self, api_key: str, api_secret: str):
        assert api_key != "house"
        return self.free_usdt, self.free_btc

    def place_post_only(self, **kwargs):
        from app.services.binance_spot_orders import BinanceOrderError

        assert kwargs["side"] in {"BUY", "SELL"}
        assert str(kwargs["client_order_id"]).startswith("cfscalp_")
        if self.reject_code is not None:
            raise BinanceOrderError("would cross", code=self.reject_code)
        self.placed.append(kwargs)
        cid = str(kwargs["client_order_id"])
        result = {
            "status": "NEW",
            "executedQty": "0",
            "orderId": 1,
            "side": kwargs["side"],
            "price": str(kwargs["price"]),
            "origQty": str(kwargs["quantity"]),
            "cummulativeQuoteQty": "0",
            "clientOrderId": cid,
        }
        self.orders[cid] = dict(result)
        return result

    def place_aggressive_exit(self, **kwargs):
        """Card #1025: MARKET escape, no price and no time-in-force."""
        from app.services.binance_spot_orders import BinanceOrderError

        assert "price" not in kwargs
        assert "time_in_force" not in kwargs
        assert str(kwargs["client_order_id"]).startswith("cfscalp_")
        if self.aggressive_reject_code is not None:
            raise BinanceOrderError("market refused", code=self.aggressive_reject_code)
        self.aggressive.append(kwargs)
        cid = str(kwargs["client_order_id"])
        quantity = Decimal(str(kwargs["quantity"]))
        result = {
            "status": "FILLED",
            "executedQty": str(quantity),
            "orderId": 7,
            "side": "SELL",
            "price": "0",
            "origQty": str(quantity),
            "cummulativeQuoteQty": str(quantity * self.bid),
            "clientOrderId": cid,
        }
        self.orders[cid] = dict(result)
        return result

    def cancel_bot_orders(self, **kwargs):
        self.cancelled.append("all")
        return 1

    def cancel_bot_order(self, **kwargs):
        self.cancelled.append(kwargs["client_order_id"])

    def query_order(self, **kwargs):
        cid = str(kwargs["client_order_id"])
        self.queried.append(cid)
        if cid in self.orders:
            return dict(self.orders[cid])
        return {
            "status": "NEW",
            "executedQty": "0",
            "side": "BUY",
            "price": "0",
            "origQty": "0",
            "cummulativeQuoteQty": "0",
            "clientOrderId": cid,
        }


@pytest.fixture(autouse=True)
def _scalp_stream_memory():
    _seed_stream_for_jev()
    yield
    from app.services.scalp_btcusdt_stream import get_scalp_btcusdt_memory

    get_scalp_btcusdt_memory().reset_for_tests()


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


def _add_key(db, user_id: str, api_key: str = "user-spot-key") -> None:
    db.add(
        UserExchangeCredential(
            user_id=str(user_id),
            provider=BINANCE_PROVIDER,
            api_key=api_key,
            api_secret="user-spot-secret",
        )
    )
    db.commit()


def test_switch_defaults_off_and_is_per_user(scalp_db):
    user_a = str(uuid.uuid4())
    user_b = str(uuid.uuid4())
    _add_key(scalp_db, user_a, "key-a")
    _add_key(scalp_db, user_b, "key-b")
    status_a = status_payload(scalp_db, user_a, free_usdt=Decimal("50"), mid=Decimal("65000"))
    status_b = status_payload(scalp_db, user_b, free_usdt=Decimal("50"), mid=Decimal("65000"))
    assert status_a["state"] == "off"
    assert status_b["state"] == "off"
    fx = FakeExchange()
    set_switch(scalp_db, user_a, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    assert status_payload(scalp_db, user_a)["state"] == "on"
    assert status_payload(scalp_db, user_b)["state"] == "off"


def test_missing_spot_key_cannot_enable(scalp_db):
    user_id = str(uuid.uuid4())
    with pytest.raises(PermissionError):
        set_switch(scalp_db, user_id, enabled=True, exchange=FakeExchange())
    payload = status_payload(scalp_db, user_id)
    assert payload["state"] == "nokey"
    assert payload["has_spot_key"] is False


def test_orders_use_user_spot_key_not_house(scalp_db):
    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id, "key-of-user")
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    result = tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        jev_fn=lambda _payload: _buy_signal(),
        free_usdt=Decimal("80"),
        free_btc=Decimal("0.01"),
        book=_book(),
    )
    assert result.sent is True
    assert fx.placed[0]["api_key"] == "key-of-user"
    assert fx.placed[0]["api_secret"] == "user-spot-secret"


def test_live_without_jev_key_does_not_send(scalp_db, monkeypatch):
    monkeypatch.delenv("JEV_API_KEY", raising=False)
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    monkeypatch.delenv("JEV_STAND_IN", raising=False)
    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    result = tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        free_usdt=Decimal("80"),
        free_btc=Decimal("0.01"),
        book=_book(),
    )
    assert result.sent is False
    assert result.skipped == "jev_unavailable"
    assert fx.placed == []


def test_cross_reject_waits_next_cycle(scalp_db):
    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    fx.reject_code = -5022
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    result = tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        jev_fn=lambda _payload: _buy_signal(),
        free_usdt=Decimal("80"),
        free_btc=Decimal("0.01"),
        book=_book(),
    )
    assert result.sent is False
    assert fx.placed == []


def test_kill_stops_sending_and_does_not_flatten(scalp_db):
    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    state = get_or_create_state(scalp_db, user_id)
    state.realized_pnl_quote = Decimal("-3")
    state.inventory_btc = Decimal("0.001")
    scalp_db.commit()
    result = tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        jev_fn=lambda _payload: _buy_signal(),
        free_usdt=Decimal("80"),
        free_btc=Decimal("0.011"),
        book=_book(),
    )
    assert result.killed is True
    payload = status_payload(
        scalp_db, user_id, free_usdt=Decimal("80"), free_btc=Decimal("0.011"), mid=Decimal("65000")
    )
    assert payload["state"] == "kill"
    state = get_or_create_state(scalp_db, user_id)
    assert Decimal(str(state.inventory_btc)) == Decimal("0.001")
    assert "all" in fx.cancelled


def test_outside_fill_clips_inventory_not_pnl(scalp_db):
    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    apply_bot_fill(
        scalp_db,
        user_id,
        client_order_id="cfscalp_fill1",
        side="BUY",
        quantity=Decimal("0.002"),
        price=Decimal("65000"),
    )
    apply_bot_fill(
        scalp_db,
        user_id,
        client_order_id="cftrade_operar",
        side="SELL",
        quantity=Decimal("0.002"),
        price=Decimal("66000"),
    )
    state = get_or_create_state(scalp_db, user_id)
    assert Decimal(str(state.inventory_btc)) == Decimal("0.002")
    tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        jev_fn=lambda _payload: _buy_signal(side=None),
        free_usdt=Decimal("50"),
        free_btc=Decimal("0.0105"),
        book=_book(),
    )
    state = get_or_create_state(scalp_db, user_id)
    assert Decimal(str(state.inventory_btc)) == Decimal("0.0005")
    assert state.inventory_clipped is True
    assert Decimal(str(state.realized_pnl_quote)) == Decimal("0")


def test_restart_keeps_switch_off(scalp_db):
    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    row = get_or_create_state(scalp_db, user_id)
    assert row.enabled is False
    scalp_db.commit()
    again = get_or_create_state(scalp_db, user_id)
    assert again.enabled is False
    assert status_payload(scalp_db, user_id)["state"] == "off"


def test_status_payload_never_includes_typesafe(scalp_db, monkeypatch):
    monkeypatch.setenv("JEV_API_KEY", "super-secret-jev-token")
    user_id = str(uuid.uuid4())
    payload = status_payload(scalp_db, user_id)
    blob = str(payload).lower()
    assert "super-secret-jev-token" not in blob
    assert "jev_api_key" not in blob
    assert "typesafe" not in blob


def test_api_switch_and_isolation(scalp_db, monkeypatch):
    monkeypatch.setattr("app.services.scalp_service.LiveExchange", FakeExchange)
    user_a = str(uuid.uuid4())
    user_b = str(uuid.uuid4())
    _add_key(scalp_db, user_a, "key-a")
    _add_key(scalp_db, user_b, "key-b")

    app = FastAPI()
    app.include_router(scalp_route.router)

    def override_db():
        yield scalp_db

    current = {"id": user_a}
    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = lambda: current["id"]

    client = TestClient(app)
    off = client.get("/api/scalp/status")
    assert off.status_code == 200
    assert off.json()["state"] == "off"
    assert "super-secret" not in str(off.json())

    on = client.post("/api/scalp/switch", json={"enabled": True})
    assert on.status_code == 200
    assert on.json()["state"] == "on"

    current["id"] = user_b
    other = client.get("/api/scalp/status")
    assert other.json()["state"] == "off"

    current["id"] = str(uuid.uuid4())
    nokey = client.post("/api/scalp/switch", json={"enabled": True})
    assert nokey.status_code == 400


def test_open_gtx_rest_is_queried_not_overwritten(scalp_db):
    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    t0 = datetime(2026, 9, 21, 12, 0, 0)
    first = tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        jev_fn=lambda _payload: _buy_signal(),
        free_usdt=Decimal("80"),
        free_btc=Decimal("0.01"),
        book=_book(),
        now=t0,
    )
    assert first.sent is True
    assert len(fx.placed) == 1
    state = get_or_create_state(scalp_db, user_id)
    rest_id = str(state.rest_client_order_id)
    assert rest_id.startswith("cfscalp_")
    assert Decimal(str(state.inventory_btc)) == Decimal("0")

    later = t0 + timedelta(milliseconds=JEV_TARGET_MS + 50)
    # Card #1025: the consult cadence (30 s) is longer than the entry post-only
    # timeout (10 s), so the fixture keeps the resting entry fresh to test the
    # sync/query behaviour itself instead of the timeout that would cancel it.
    state = get_or_create_state(scalp_db, user_id)
    state.rest_opened_at = later
    scalp_db.commit()
    second = tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        jev_fn=lambda _payload: _buy_signal(),
        free_usdt=Decimal("80"),
        free_btc=Decimal("0.01"),
        book=_book(),
        now=later,
    )
    assert second.sent is False
    assert len(fx.placed) == 1
    assert rest_id in fx.queried
    state = get_or_create_state(scalp_db, user_id)
    assert str(state.rest_client_order_id) == rest_id

    qty = fx.placed[0]["quantity"]
    price = fx.placed[0]["price"]
    fx.orders[rest_id] = {
        "status": "FILLED",
        "executedQty": str(qty),
        "origQty": str(qty),
        "side": "BUY",
        "price": str(price),
        "cummulativeQuoteQty": str(qty * price),
        "clientOrderId": rest_id,
    }
    filled_at = later + timedelta(milliseconds=JEV_TARGET_MS + 50)
    tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        jev_fn=lambda _payload: _buy_signal(side=None),
        free_usdt=Decimal("80"),
        free_btc=Decimal("0.011"),
        book=_book(),
        now=filled_at,
    )
    state = get_or_create_state(scalp_db, user_id)
    assert state.rest_client_order_id is None
    booked = Decimal(str(state.inventory_btc))
    assert booked > 0
    assert abs(booked - qty) < Decimal("1e-12")
    assert len(fx.placed) == 1


def test_religar_after_kill_starts_new_day_pnl(scalp_db):
    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    state = get_or_create_state(scalp_db, user_id)
    state.realized_pnl_quote = Decimal("-3")
    state.fees_quote = Decimal("0.4")
    state.jev_cost_quote = Decimal("0.1")
    state.day_pnl_quote = Decimal("-3.5")
    state.inventory_btc = Decimal("0.001")
    scalp_db.commit()
    killed = tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        jev_fn=lambda _payload: _buy_signal(),
        free_usdt=Decimal("80"),
        free_btc=Decimal("0.011"),
        book=_book(),
    )
    assert killed.killed is True
    state = get_or_create_state(scalp_db, user_id)
    assert state.day_started_at is not None
    assert Decimal(str(state.realized_pnl_quote)) == Decimal("-3")

    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    state = get_or_create_state(scalp_db, user_id)
    assert state.killed is False
    assert Decimal(str(state.realized_pnl_quote)) == Decimal("0")
    assert Decimal(str(state.fees_quote)) == Decimal("0")
    assert Decimal(str(state.jev_cost_quote)) == Decimal("0")
    assert Decimal(str(state.day_pnl_quote)) == Decimal("0")
    assert state.day_started_at is not None

    revived = tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        jev_fn=lambda _payload: _buy_signal(),
        free_usdt=Decimal("80"),
        free_btc=Decimal("0.01"),
        book=_book(),
    )
    assert revived.killed is False
    assert revived.skipped != "kill"
    assert revived.sent is True


def test_switch_off_during_jev_does_not_place(scalp_db):
    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    engine = scalp_db.get_bind()
    LoopSession = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)
    OtherSession = sessionmaker(bind=engine, autoflush=False)
    loop_db = LoopSession()
    try:

        def jev_fn(_payload):
            other = OtherSession()
            try:
                set_switch(other, user_id, enabled=False, exchange=fx)
            finally:
                other.close()
            return _buy_signal()

        result = tick_user(
            loop_db,
            user_id,
            exchange=fx,
            jev_fn=jev_fn,
            free_usdt=Decimal("80"),
            free_btc=Decimal("0.01"),
            book=_book(),
        )
        assert result.sent is False
        assert fx.placed == []
        assert result.skipped == "switch_off"
    finally:
        loop_db.close()


def test_stand_in_without_jev_key_does_not_place(scalp_db, monkeypatch):
    monkeypatch.delenv("JEV_API_KEY", raising=False)
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    monkeypatch.setenv("JEV_STAND_IN", "1")
    monkeypatch.setenv("JEV_STAND_IN_SIDE", "BUY")
    monkeypatch.setenv("JEV_STAND_IN_CONFIDENCE", "0.9")
    monkeypatch.setenv("JEV_STAND_IN_EDGE", "1")
    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    result = tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        free_usdt=Decimal("80"),
        free_btc=Decimal("0.01"),
        book=_book(),
    )
    assert result.sent is False
    assert fx.placed == []


def test_jev_requests_wait_target_ms_stale_cancel_does_not():
    assert JEV_FLOOR_MS == 400
    assert JEV_TARGET_MS == 30000
    too_soon = decide_cycle(
        enabled=True,
        killed=False,
        has_spot_key=True,
        jev_available=True,
        jev_in_flight=False,
        last_jev_elapsed_ms=500,
        inventory_btc=Decimal("0"),
        floor_btc=Decimal("0"),
        free_usdt=Decimal("200"),
        free_btc=Decimal("0"),
        day_pnl=Decimal("0"),
        book=_book(),
        resting=RestingOrder("cfscalp_abc", "BUY", Decimal("64000")),
        jev=None,
    )
    assert too_soon.call_jev is False
    assert too_soon.send is False
    assert too_soon.cancel_resting is True
    assert too_soon.skip_reason == "jev_target"

    ready = decide_cycle(
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
        jev=None,
    )
    assert ready.call_jev is True
    assert ready.skip_reason == "need_jev"

    with_signal = decide_cycle(
        enabled=True,
        killed=False,
        has_spot_key=True,
        jev_available=True,
        jev_in_flight=False,
        last_jev_elapsed_ms=500,
        inventory_btc=Decimal("0"),
        floor_btc=Decimal("0"),
        free_usdt=Decimal("200"),
        free_btc=Decimal("0"),
        day_pnl=Decimal("0"),
        book=_book(),
        resting=None,
        jev=_buy_signal(),
    )
    assert with_signal.send is True


# --- card #1015: scalp Jev diagnostic log ---------------------------------


def _diagnostic_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _diagnostic_lines(path: Path) -> list[str]:
    return [line for line in _diagnostic_text(path).splitlines() if line.strip()]


def _call_id(line: str) -> str:
    return line.split("id=", 1)[1].split(" ", 1)[0]


def _diagnostic_call_payload(
    *,
    inventory_btc: str = "0.0005",
    t: str = "80",
    remaining_to_t: str = "47.5",
    resting: dict | None = None,
) -> dict:
    return {
        "state": {
            "symbol": "BTCUSDT",
            "horizon_s": 900,
            "touch": {
                "bid": "65000",
                "ask": "65010",
                "mid": "65005",
                "spread_bp": "1.5",
                "age_ms": 10,
            },
            "window": {"horizon_s": 900, "trade_count": 3, "ret_bp": "1.0", "vol_bp": "2.0"},
            "account": {
                "inventory_btc": inventory_btc,
                "t": t,
                "remaining_to_t": remaining_to_t,
                "fee_bp": "10",
                "bnb_fee_active": False,
            },
            "resting": resting,
        }
    }


@pytest.fixture
def diagnostic_log(tmp_path):
    """Dedicated file handler on the diagnostic logger (always one file)."""
    path = tmp_path / "scalp_jev_diagnostic.log"
    handler = TailTruncatingFileHandler(path)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    previous_level = diagnostic_logger.level
    diagnostic_logger.addHandler(handler)
    diagnostic_logger.setLevel(logging.INFO)
    try:
        yield path
    finally:
        diagnostic_logger.removeHandler(handler)
        diagnostic_logger.setLevel(previous_level)
        handler.close()


def test_diagnostic_log_records_entry_and_return_of_one_call(monkeypatch, diagnostic_log):
    monkeypatch.setenv("JEV_API_KEY", "super-secret-jev-token")

    def ok(_req, _timeout, _captured):
        response = _FakeHttpResponse(
            _systemone_response(side="BUY", confidence=0.75, move_bp=25.0, toxic=0.1)
        )
        response.status = 200
        return response

    captured = _capture_urlopen(monkeypatch, ok)
    signal = request_jev(_diagnostic_call_payload(resting=None))
    assert signal.side == "BUY"

    # The wire body is the criterion: summarization happens only when the log
    # record is formatted, so the exact account sent to Jev survives untouched
    # (an in-place summary would replace it in ``captured["body"]`` too).
    assert captured["body"]["state"]["account"] == {
        "inventory_btc": "0.0005",
        "t": "80",
        "remaining_to_t": "47.5",
        "fee_bp": "10",
        "bnb_fee_active": False,
    }

    lines = _diagnostic_lines(diagnostic_log)
    entries = [line for line in lines if "call entry" in line]
    returns = [line for line in lines if "call return" in line]
    assert len(entries) == 1, "propagate=False: exactly one entry per call"
    assert len(returns) == 1, "propagate=False: exactly one return per call"
    entry = entries[0]
    returned = returns[0]
    assert _call_id(entry) == _call_id(returned)

    assert '"symbol":"BTCUSDT"' in entry
    assert '"touch":{"bid":"65000"' in entry
    assert '"window":{"horizon_s":900' in entry
    assert '"resting":null' in entry
    assert '"account":{"has_position":true,"has_balance":true}' in entry
    assert 'questions={"side":"choice","expected_move_bp":"score","book_toxic":"noul"}' in entry

    assert "status=200" in returned
    assert "side=BUY" in returned
    assert "expected_move_bp=25" in returned
    assert f"score={_move_bp_to_score(25.0)}" in returned
    assert "book_toxic=False" in returned
    assert "confidence=0.75" in returned
    assert "latency_ms=" in returned


def test_diagnostic_log_account_summary_is_booleans_only():
    assert summarize_account({"inventory_btc": "0", "t": "0"}) == {
        "has_position": False,
        "has_balance": False,
    }
    assert summarize_account({"inventory_btc": "0.00000001", "t": "0.01"}) == {
        "has_position": True,
        "has_balance": True,
    }
    assert summarize_account({}) == {"has_position": False, "has_balance": False}
    assert summarize_account({"inventory_btc": "n/a", "t": None}) == {
        "has_position": False,
        "has_balance": False,
    }


def test_diagnostic_log_return_carries_the_http_status(monkeypatch, diagnostic_log):
    monkeypatch.setenv("JEV_API_KEY", "secret-status-token")

    def ok(_req, _timeout, _captured):
        response = _FakeHttpResponse(_systemone_response())
        response.status = 207
        return response

    _capture_urlopen(monkeypatch, ok)
    request_jev(_diagnostic_call_payload())
    returned = next(line for line in _diagnostic_lines(diagnostic_log) if "call return" in line)
    assert "status=207" in returned


def test_diagnostic_log_never_carries_secrets_or_exact_account_values(monkeypatch, diagnostic_log):
    monkeypatch.setenv("JEV_API_KEY", "super-secret-jev-token")
    monkeypatch.setenv("TYPESAFE_API_KEY", "second-secret-token")

    def ok(_req, _timeout, _captured):
        response = _FakeHttpResponse(_systemone_response())
        response.status = 200
        return response

    captured = _capture_urlopen(monkeypatch, ok)
    request_jev(
        _diagnostic_call_payload(inventory_btc="0.12345678", t="77.5", remaining_to_t="69.473")
    )
    assert captured["body"]["state"]["account"]["inventory_btc"] == "0.12345678"
    assert captured["body"]["state"]["account"]["t"] == "77.5"
    assert captured["body"]["state"]["account"]["remaining_to_t"] == "69.473"

    def boom(_req, _timeout, _captured):
        raise urllib.error.HTTPError(
            "https://api.typesafe.ai/v1/systemone",
            500,
            "Server Error",
            hdrs=None,
            fp=io.BytesIO(b'{"error":"invalid key super-secret-jev-token second-secret-token"}'),
        )

    _capture_urlopen(monkeypatch, boom)
    assert request_jev(_diagnostic_call_payload()).side is None

    text = _diagnostic_text(diagnostic_log)
    assert text.strip()
    for forbidden in (
        "super-secret-jev-token",
        "second-secret-token",
        "Bearer",
        "0.12345678",
        "77.5",
        "69.473",
        "Authorization",
    ):
        assert forbidden not in text
    assert "<redacted>" in text


def test_diagnostic_log_error_body_is_summarized_redacted_and_compact(monkeypatch, diagnostic_log):
    monkeypatch.setenv("JEV_API_KEY", "super-secret-jev-token")
    body = b'{"error":"bad key super-secret-jev-token",\n "trace":"' + b"z" * 600 + b'"}'

    def boom(_req, _timeout, _captured):
        raise urllib.error.HTTPError(
            "https://api.typesafe.ai/v1/systemone",
            500,
            "Server Error",
            hdrs=None,
            fp=io.BytesIO(body),
        )

    _capture_urlopen(monkeypatch, boom)
    hold = request_jev(_diagnostic_call_payload())
    assert hold.side is None

    line = next(line for line in _diagnostic_lines(diagnostic_log) if "call error" in line)
    assert "WARNING" in line
    assert "status=500" in line
    assert "latency_ms=" in line
    assert "super-secret-jev-token" not in line
    assert "<redacted>" in line
    summarized = line.split("body=", 1)[1]
    assert len(summarized) <= ERROR_BODY_CHARS + 1
    assert summarized.endswith("…")
    assert "\n" not in summarized


def test_diagnostic_log_transport_error_is_recorded(monkeypatch, diagnostic_log):
    monkeypatch.setenv("JEV_API_KEY", "super-secret-jev-token")

    def boom(_req, _timeout, _captured):
        raise urllib.error.URLError("connection refused super-secret-jev-token")

    _capture_urlopen(monkeypatch, boom)
    hold = request_jev(_diagnostic_call_payload())
    assert hold.side is None
    line = next(line for line in _diagnostic_lines(diagnostic_log) if "call error" in line)
    assert "status=transport_error" in line
    assert "super-secret-jev-token" not in line


def test_diagnostic_log_bad_reply_keeps_the_http_status(monkeypatch, diagnostic_log):
    monkeypatch.setenv("JEV_API_KEY", "secret-bad-reply")

    def bad_json(_req, _timeout, _captured):
        response = _FakeHttpResponse(b"{not json")
        response.status = 200
        return response

    _capture_urlopen(monkeypatch, bad_json)
    assert request_jev(_diagnostic_call_payload()).side is None

    def bad_encoding(_req, _timeout, _captured):
        response = _FakeHttpResponse(b"\xff\xfe\xfa")
        response.status = 206
        return response

    _capture_urlopen(monkeypatch, bad_encoding)
    assert request_jev(_diagnostic_call_payload()).side is None

    errors = [line for line in _diagnostic_lines(diagnostic_log) if "call error" in line]
    assert len(errors) == 2
    # The request left and a status came back: it is a bad reply, not a lost
    # transport, so the real HTTP status is kept in the record.
    assert "status=200" in errors[0]
    assert "status=206" in errors[1]
    assert all("bad_reply" in line for line in errors)
    assert all("transport_error" not in line for line in errors)


def test_error_body_read_fallback_is_bounded(monkeypatch):
    from app.services import scalp_jev

    seen: dict = {}

    def spy(body, *, limit=ERROR_BODY_CHARS):
        seen["length"] = len(str(body))
        return "summarized"

    monkeypatch.setattr(scalp_jev, "summarize_body", spy)

    class _NoSizeBody:
        def read(self):  # no size argument: the bounded read raises TypeError
            return b"y" * (ERROR_BODY_READ_BYTES * 4)

        def close(self):
            return None

    exc = urllib.error.HTTPError(
        "https://api.typesafe.ai/v1/systemone", 500, "Server Error", hdrs=None, fp=_NoSizeBody()
    )
    assert _error_body(exc) == "summarized"
    assert seen["length"] <= ERROR_BODY_READ_BYTES


def test_diagnostic_log_no_call_is_recorded_for_the_keyless_stand_in(monkeypatch, diagnostic_log):
    monkeypatch.delenv("JEV_API_KEY", raising=False)
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    monkeypatch.setenv("JEV_STAND_IN", "1")
    monkeypatch.setenv("JEV_STAND_IN_SIDE", "BUY")
    request_jev(_diagnostic_call_payload())
    text = _diagnostic_text(diagnostic_log)
    assert "call entry" not in text
    assert "call return" not in text


def test_diagnostic_log_level_is_configurable(monkeypatch, tmp_path):
    path = tmp_path / "level.log"
    monkeypatch.setenv("RUN_SCALP_LOOP", "1")
    monkeypatch.delenv("SCALP_JEV_LOG_ENABLED", raising=False)
    monkeypatch.setenv("SCALP_JEV_LOG_LEVEL", "WARNING")
    monkeypatch.setenv("SCALP_JEV_LOG_FILE", str(path))
    handler = install_diagnostic_log()
    try:
        assert isinstance(handler, TailTruncatingFileHandler)
        log_call_entry(call_id="deadbeef", systemone=_diagnostic_call_payload())
        assert _diagnostic_text(path) == ""
        log_call_error(call_id="deadbeef", status=500, latency_ms=7, body="boom")
        text = _diagnostic_text(path)
        assert "call error" in text
        assert "call entry" not in text
        assert "WARNING" in text
    finally:
        if handler is not None:
            diagnostic_logger.removeHandler(handler)
            handler.close()
        diagnostic_logger.setLevel(logging.NOTSET)

    monkeypatch.setenv("SCALP_JEV_LOG_LEVEL", "INFO")
    assert install_diagnostic_log(path=path) is not None
    handler = diagnostic_logger.handlers[-1]
    try:
        log_call_entry(call_id="deadbeef", systemone=_diagnostic_call_payload())
        assert "call entry" in _diagnostic_text(path)
    finally:
        diagnostic_logger.removeHandler(handler)
        handler.close()
        diagnostic_logger.setLevel(logging.NOTSET)


def test_diagnostic_log_installs_one_handler_and_defaults(monkeypatch, tmp_path):
    from app.services import scalp_jev_log

    monkeypatch.setenv("RUN_SCALP_LOOP", "1")
    monkeypatch.delenv("SCALP_JEV_LOG_ENABLED", raising=False)
    monkeypatch.delenv("SCALP_JEV_LOG_FILE", raising=False)
    monkeypatch.delenv("SCALP_JEV_LOG_LEVEL", raising=False)
    default_path = scalp_jev_log.log_file_path()
    assert default_path.name == "scalp_jev_diagnostic.log"
    assert default_path.parent.name == "backend"
    assert scalp_jev_log.log_level() == logging.INFO
    monkeypatch.setenv("SCALP_JEV_LOG_LEVEL", "not-a-level")
    assert scalp_jev_log.log_level() == logging.INFO

    installed = install_diagnostic_log(path=tmp_path / "one.log")
    try:
        assert isinstance(installed, TailTruncatingFileHandler)
        assert scalp_jev_log.installed_handler() is installed
        assert install_diagnostic_log(path=tmp_path / "two.log") is installed
        assert (
            sum(isinstance(h, TailTruncatingFileHandler) for h in diagnostic_logger.handlers) == 1
        )
        assert not (tmp_path / "two.log").exists()
    finally:
        if installed is not None:
            diagnostic_logger.removeHandler(installed)
            installed.close()
        diagnostic_logger.setLevel(logging.NOTSET)


def test_diagnostic_log_is_single_file_with_a_200mb_ceiling(tmp_path):
    assert MAX_LOG_BYTES == 209_715_200
    assert not issubclass(TailTruncatingFileHandler, logging.handlers.RotatingFileHandler)
    assert not issubclass(TailTruncatingFileHandler, logging.handlers.TimedRotatingFileHandler)

    path = tmp_path / "ceiling.log"
    handler = TailTruncatingFileHandler(path, max_bytes=600)
    handler.setFormatter(logging.Formatter("%(message)s"))
    previous_level = diagnostic_logger.level
    diagnostic_logger.addHandler(handler)
    diagnostic_logger.setLevel(logging.INFO)
    try:
        for index in range(40):
            diagnostic_logger.info("record %03d %s", index, "x" * 40)
        handler.flush()
    finally:
        diagnostic_logger.removeHandler(handler)
        diagnostic_logger.setLevel(previous_level)
        handler.close()

    lines = _diagnostic_lines(path)
    assert path.stat().st_size <= 600
    assert lines, "the newest records stay in the file"
    assert all(line.startswith("record ") for line in lines), "cut on a line boundary"
    assert "record 039" in lines[-1]
    assert not any("record 000" in line for line in lines), "the oldest records fall"
    assert sorted(p.name for p in tmp_path.iterdir()) == ["ceiling.log"]


def test_diagnostic_log_keeps_an_oversized_record_whole(tmp_path):
    path = tmp_path / "oversize.log"
    handler = TailTruncatingFileHandler(path, max_bytes=64)
    handler.setFormatter(logging.Formatter("%(message)s"))
    previous_level = diagnostic_logger.level
    diagnostic_logger.addHandler(handler)
    diagnostic_logger.setLevel(logging.INFO)
    oversized = "record-over-ceiling " + "y" * 200
    try:
        diagnostic_logger.info(oversized)
        handler.flush()
    finally:
        diagnostic_logger.removeHandler(handler)
        diagnostic_logger.setLevel(previous_level)
        handler.close()

    assert _diagnostic_text(path).strip() == oversized, "the newest record stays whole"
    size = path.stat().st_size
    # ceiling promise: size <= max(ceiling, largest single record)
    assert size == len(oversized) + 1
    assert size > 64


def test_diagnostic_log_rejects_a_non_positive_ceiling(tmp_path):
    for bad in (0, -1):
        with pytest.raises(ValueError):
            TailTruncatingFileHandler(tmp_path / f"bad-{bad}.log", max_bytes=bad)
    assert list(tmp_path.iterdir()) == []


def test_diagnostic_log_ignores_an_empty_refusal_token(diagnostic_log):
    log_cycle_refusal(user_id="u-1", skip_reason="")
    log_cycle_refusal(user_id="u-1", skip_reason=None)
    log_cycle_refusal(user_id="u-1", skip_reason="   ")
    assert _diagnostic_text(diagnostic_log) == ""


def test_diagnostic_log_shift_retries_partial_writes(monkeypatch, tmp_path):
    real_pwrite = os.pwrite
    calls = {"count": 0}

    def partial_pwrite(fd, data, offset):
        calls["count"] += 1
        return real_pwrite(fd, data[:7], offset)

    monkeypatch.setattr(os, "pwrite", partial_pwrite)
    path = tmp_path / "partial.log"
    handler = TailTruncatingFileHandler(path, max_bytes=600)
    handler.setFormatter(logging.Formatter("%(message)s"))
    previous_level = diagnostic_logger.level
    diagnostic_logger.addHandler(handler)
    diagnostic_logger.setLevel(logging.INFO)
    try:
        for index in range(40):
            diagnostic_logger.info("record %03d %s", index, "x" * 40)
        handler.flush()
    finally:
        diagnostic_logger.removeHandler(handler)
        diagnostic_logger.setLevel(previous_level)
        handler.close()

    lines = _diagnostic_lines(path)
    assert calls["count"] > 1, "the shift retried the bytes left by the partial write"
    assert path.stat().st_size <= 600
    assert lines and all(line.startswith("record ") for line in lines)
    assert "record 039" in lines[-1]


def test_diagnostic_log_records_pre_call_refusal(scalp_db, diagnostic_log):
    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    result = tick_user(
        scalp_db,
        user_id,
        exchange=FakeExchange(),
        free_usdt=Decimal("80"),
        free_btc=Decimal("0.01"),
        book=_book(),
    )
    assert result.sent is False
    assert result.skipped == "switch_off"
    assert f"scalp cycle refused user={user_id} skip_reason=switch_off" in _diagnostic_text(
        diagnostic_log
    )


def test_diagnostic_log_records_post_call_refusal(scalp_db, diagnostic_log):
    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    result = tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        jev_fn=lambda _payload: _buy_signal(expected_move_bp=Decimal("15")),
        free_usdt=Decimal("80"),
        free_btc=Decimal("0.01"),
        book=_book(),
    )
    assert result.sent is False
    assert result.skipped == "hurdle"
    assert f"scalp cycle refused user={user_id} skip_reason=hurdle" in _diagnostic_text(
        diagnostic_log
    )
    # the panel stays untouched: the reason lives only in the diagnostic file
    panel = status_payload(scalp_db, user_id, free_usdt=Decimal("80"), mid=Decimal("65005"))
    assert "skip_reason" not in panel
    assert not any("skip" in str(key) for key in panel)


def test_diagnostic_log_ignores_closes_without_a_gate_token(scalp_db, diagnostic_log):
    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    fx.reject_code = -1013
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    result = tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        jev_fn=lambda _payload: _buy_signal(),
        free_usdt=Decimal("80"),
        free_btc=Decimal("0.01"),
        book=_book(),
    )
    assert result.sent is False
    assert result.skipped is None
    assert "skip_reason" not in _diagnostic_text(diagnostic_log)


def test_diagnostic_log_ignores_rest_open_blocking_the_send(scalp_db, diagnostic_log):
    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    t0 = datetime(2026, 9, 21, 12, 0, 0)
    first = tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        jev_fn=lambda _payload: _buy_signal(),
        free_usdt=Decimal("80"),
        free_btc=Decimal("0.01"),
        book=_book(),
        now=t0,
    )
    assert first.sent is True
    assert get_or_create_state(scalp_db, user_id).rest_client_order_id is not None

    # second cycle: the decided send is blocked by the resting order (no gate token)
    second_at = t0 + timedelta(milliseconds=JEV_TARGET_MS + 50)
    # Keep the resting entry fresh: the 10 s entry timeout is shorter than the
    # 30 s consult cadence (card #1025).
    state = get_or_create_state(scalp_db, user_id)
    state.rest_opened_at = second_at
    scalp_db.commit()
    second = tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        jev_fn=lambda _payload: _buy_signal(),
        free_usdt=Decimal("80"),
        free_btc=Decimal("0.01"),
        book=_book(),
        now=second_at,
    )
    assert second.sent is False
    assert second.skipped is None
    assert len(fx.placed) == 1, "no second order: the send was blocked, not decided away"
    assert "skip_reason" not in _diagnostic_text(diagnostic_log)


def test_diagnostic_log_ignores_keyless_stand_in_send(scalp_db, diagnostic_log, monkeypatch):
    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    monkeypatch.delenv("JEV_API_KEY", raising=False)
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    monkeypatch.setenv("JEV_STAND_IN", "1")
    monkeypatch.setenv("JEV_STAND_IN_SIDE", "BUY")
    monkeypatch.setenv("JEV_STAND_IN_CONFIDENCE", "0.9")
    monkeypatch.setenv("JEV_STAND_IN_MOVE_BP", "35")
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))

    # live_jev is true (stand-in) but live_send is false (no key): decided send, no order
    result = tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        free_usdt=Decimal("80"),
        free_btc=Decimal("0.01"),
        book=_book(),
    )
    assert result.sent is False
    assert result.skipped is None
    assert fx.placed == []
    text = _diagnostic_text(diagnostic_log)
    assert "skip_reason" not in text
    assert "call entry" not in text


def test_diagnostic_log_ships_dev_only(monkeypatch):
    from app.services import scalp_jev_log

    root = Path(__file__).resolve().parents[3]
    dev_unit = (root / "ops/systemd/criptofarol-dev-runtime-worker.service").read_text(
        encoding="utf-8"
    )
    prod_unit = (root / "ops/systemd/criptofarol-prod-runtime-worker.service").read_text(
        encoding="utf-8"
    )
    assert "RUN_SCALP_LOOP=1" in dev_unit
    assert "RUN_SCALP_LOOP" not in prod_unit
    assert "SCALP_JEV_LOG" not in prod_unit

    monkeypatch.delenv("RUN_SCALP_LOOP", raising=False)
    monkeypatch.delenv("SCALP_JEV_LOG_ENABLED", raising=False)
    assert scalp_jev_log.diagnostic_enabled() is False
    monkeypatch.setenv("RUN_SCALP_LOOP", "1")
    assert scalp_jev_log.diagnostic_enabled() is True
    monkeypatch.setenv("SCALP_JEV_LOG_ENABLED", "0")
    assert scalp_jev_log.diagnostic_enabled() is False
