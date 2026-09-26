"""Card #1025 — E: aggressive exit (MARKET, no price cap) at the window end."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import ScalpFill, ScalpUserState, UserExchangeCredential
from app.services.scalp_engine import (
    AGGRESSIVE_ORDER_TYPE,
    HOLD_AFTER_FILL_S,
    STUCK_AFTER_FILL_S,
    Book,
    RestingOrder,
    decide_exit_cycle,
    should_mark_stuck,
    should_post_exit,
)
from app.services.scalp_jev_log import (
    TailTruncatingFileHandler,
    logger as diagnostic_logger,
)
from app.services.scalp_service import get_or_create_state, set_switch, status_payload, tick_user
from test_scalp_direcional_jev import FakeExchange, _add_key, _book, _seed_stream_for_jev


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


@pytest.fixture
def diagnostic_log(tmp_path):
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


def _exit_cycle(
    *,
    seconds_since_fill: float,
    resting=None,
    stuck: bool = False,
    avg_entry: Decimal = Decimal("65000"),
    book: Book | None = None,
):
    return decide_exit_cycle(
        enabled=True,
        killed=False,
        has_spot_key=True,
        inventory_btc=Decimal("0.001"),
        free_btc=Decimal("0.01"),
        floor_btc=Decimal("0"),
        avg_entry=avg_entry,
        book=book or _book(),
        resting=resting,
        seconds_since_fill=seconds_since_fill,
        stuck=stuck,
    )


def test_escape_is_reached_with_an_unfilled_passive_exit_resting():
    resting = RestingOrder("cfscalp_passive", "SELL", Decimal("65230"), role="exit")
    intent = _exit_cycle(seconds_since_fill=float(HOLD_AFTER_FILL_S), resting=resting)
    assert intent.send is True
    assert intent.aggressive_exit is True
    assert intent.skip_reason is None
    assert intent.cancel_resting is True, "the unfilled passive exit is cancelled"
    assert intent.side == "SELL"
    assert intent.order_type == AGGRESSIVE_ORDER_TYPE == "MARKET"
    assert intent.price is None, "no price ceiling on the escape"
    assert intent.quantity == Decimal("0.001")


def test_escape_does_not_preempt_on_a_stale_resting_price():
    resting = RestingOrder("cfscalp_stale", "SELL", Decimal("60000"), role="exit")
    intent = _exit_cycle(seconds_since_fill=float(HOLD_AFTER_FILL_S) + 5, resting=resting)
    assert intent.aggressive_exit is True
    assert intent.cancel_resting is True


def test_escape_fires_at_the_window_end_not_at_the_stuck_mark():
    assert STUCK_AFTER_FILL_S > HOLD_AFTER_FILL_S
    assert should_mark_stuck(HOLD_AFTER_FILL_S) is False
    at_window_end = _exit_cycle(seconds_since_fill=float(HOLD_AFTER_FILL_S), stuck=False)
    assert at_window_end.aggressive_exit is True
    assert at_window_end.send is True


def test_position_past_the_window_without_resting_is_never_inert():
    intent = _exit_cycle(seconds_since_fill=float(HOLD_AFTER_FILL_S) + 60, stuck=True)
    assert intent.send is True
    assert intent.aggressive_exit is True
    assert intent.skip_reason != "stuck"


def test_no_passive_post_at_or_after_the_window_end():
    # Inside the window the passive target/stop still posts.
    assert should_post_exit(ret_bp=Decimal("35")) is True
    assert should_post_exit(ret_bp=Decimal("-28")) is True
    assert should_post_exit(ret_bp=Decimal("0")) is False
    # The time branch is gone: the window end never posts a passive order.
    intent = _exit_cycle(seconds_since_fill=float(HOLD_AFTER_FILL_S) + 1)
    assert intent.order_type == "MARKET"
    assert intent.aggressive_exit is True


def test_passive_exit_inside_the_window_is_untouched():
    # At the current ask the resting exit is not stale: nothing is cancelled.
    resting = RestingOrder("cfscalp_passive", "SELL", Decimal("65010"), role="exit")
    intent = _exit_cycle(seconds_since_fill=60.0, resting=resting)
    assert intent.send is False
    assert intent.skip_reason == "exit_resting"
    assert intent.cancel_resting is False
    assert intent.aggressive_exit is False


def _open_position(scalp_db, user_id: str, *, seconds: float) -> None:
    state = get_or_create_state(scalp_db, user_id)
    state.floor_btc = Decimal("0")
    state.inventory_btc = Decimal("0.001")
    state.avg_entry_quote = Decimal("65000")
    state.position_opened_at = datetime.utcnow() - timedelta(seconds=seconds)
    scalp_db.commit()


def test_tick_cancels_the_unfilled_passive_exit_and_sends_the_aggressive_one(
    scalp_db, diagnostic_log
):
    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    _open_position(scalp_db, user_id, seconds=HOLD_AFTER_FILL_S + 1)
    state = get_or_create_state(scalp_db, user_id)
    state.rest_client_order_id = "cfscalp_passive_exit"
    state.rest_side = "SELL"
    state.rest_price = Decimal("65300")
    state.rest_role = "exit"
    state.rest_opened_at = datetime.utcnow() - timedelta(seconds=HOLD_AFTER_FILL_S)
    scalp_db.commit()

    result = tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        free_usdt=Decimal("80"),
        free_btc=Decimal("0.011"),
        book=_book(),
    )

    assert result.sent is True
    assert result.skipped is None
    assert "cfscalp_passive_exit" in fx.cancelled, "the passive exit was cancelled"
    assert len(fx.aggressive) == 1, "one aggressive order, no extra passive attempt"
    assert fx.placed == []
    order = fx.aggressive[0]
    assert "price" not in order and "time_in_force" not in order
    assert order["quantity"] == Decimal("0.001")
    state = get_or_create_state(scalp_db, user_id)
    assert Decimal(str(state.inventory_btc)) == Decimal("0")
    assert state.rest_client_order_id is None

    line = next(
        line
        for line in diagnostic_log.read_text(encoding="utf-8").splitlines()
        if "aggressive exit" in line
    )
    assert "WARNING" in line
    assert "reason=hold_window_end" in line
    assert "order_type=MARKET" in line
    assert "price_cap=none" in line
    assert "status=FILLED" in line
    assert f"user={user_id}" in line
    assert "skip_reason=stuck" not in line


def test_tick_sends_the_escape_with_no_passive_exit_resting(scalp_db, diagnostic_log):
    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    _open_position(scalp_db, user_id, seconds=HOLD_AFTER_FILL_S + 30)

    result = tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        free_usdt=Decimal("80"),
        free_btc=Decimal("0.011"),
        book=_book(),
    )
    assert result.sent is True
    assert len(fx.aggressive) == 1
    assert fx.placed == []
    assert "scalp aggressive exit" in diagnostic_log.read_text(encoding="utf-8")


def test_tick_escape_is_not_blocked_by_a_leftover_entry_resting(scalp_db, diagnostic_log):
    """A partially filled entry can leave a bot order resting with the position open."""
    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    _open_position(scalp_db, user_id, seconds=HOLD_AFTER_FILL_S + 5)
    state = get_or_create_state(scalp_db, user_id)
    state.rest_client_order_id = "cfscalp_entry_remainder"
    state.rest_side = "BUY"
    state.rest_price = Decimal("64000")
    state.rest_role = "entry"
    state.rest_opened_at = datetime.utcnow()
    scalp_db.commit()

    result = tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        free_usdt=Decimal("80"),
        free_btc=Decimal("0.011"),
        book=_book(),
    )
    assert result.sent is True, "the escape is never blocked by a resting order"
    assert "cfscalp_entry_remainder" in fx.cancelled
    assert len(fx.aggressive) == 1


def test_panel_and_status_gain_no_escape_field(scalp_db):
    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    payload = status_payload(scalp_db, user_id, free_usdt=Decimal("80"), mid=Decimal("65005"))
    assert not any("aggressive" in str(key) or "escape" in str(key) for key in payload)
    assert "aggressive" not in str(payload["status_text"]).lower()


def test_binance_place_aggressive_exit_sends_market_without_a_price(monkeypatch):
    from app.services import scalp_binance
    from app.services.binance_spot_orders import BinanceOrderError

    captured: dict = {}

    def fake_signed_request(*, method, path, api_key, api_secret, params=None, base_url=None):
        captured.update({"method": method, "path": path, "params": dict(params or {})})
        return {"orderId": 1, "status": "FILLED"}

    monkeypatch.setattr(scalp_binance, "signed_request", fake_signed_request)
    monkeypatch.setattr(
        scalp_binance,
        "get_symbol_info",
        lambda symbol, base_url=None: {
            "filters": [{"filterType": "LOT_SIZE", "stepSize": "0.00001", "minQty": "0.00001"}]
        },
    )
    scalp_binance.place_aggressive_exit(
        api_key="k",
        api_secret="s",
        quantity=Decimal("0.00123"),
        client_order_id="cfscalp_escape",
        reference_price=Decimal("65000"),
    )
    assert captured["method"] == "POST"
    assert captured["path"] == "/api/v3/order"
    assert captured["params"]["type"] == "MARKET"
    assert captured["params"]["side"] == "SELL"
    assert captured["params"]["quantity"] == "0.00123"
    assert "price" not in captured["params"], "the escape carries no price ceiling"
    assert "timeInForce" not in captured["params"]

    with pytest.raises(BinanceOrderError):
        scalp_binance.place_aggressive_exit(
            api_key="k",
            api_secret="s",
            quantity=Decimal("0.001"),
            client_order_id="cftrade_x",
            reference_price=Decimal("65000"),
        )


def _symbol_info_with_notional(filter_type: str) -> dict:
    return {
        "filters": [
            {"filterType": "LOT_SIZE", "stepSize": "0.00001", "minQty": "0.00001"},
            {"filterType": filter_type, "minNotional": "5"},
        ]
    }


@pytest.mark.parametrize("filter_type", ["MIN_NOTIONAL", "NOTIONAL"])
def test_binance_place_aggressive_exit_validates_the_notional_filter(monkeypatch, filter_type):
    """Correção pós-CR (item 3): a agressiva espelha a validação de MIN_NOTIONAL."""
    from app.services import scalp_binance
    from app.services.binance_spot_orders import BinanceOrderError

    captured: dict = {}

    def fake_signed_request(*, method, path, api_key, api_secret, params=None, base_url=None):
        captured.update({"method": method, "path": path, "params": dict(params or {})})
        return {"orderId": 9, "status": "FILLED"}

    monkeypatch.setattr(scalp_binance, "signed_request", fake_signed_request)
    monkeypatch.setattr(
        scalp_binance,
        "get_symbol_info",
        lambda symbol, base_url=None: _symbol_info_with_notional(filter_type),
    )
    # 0.00001 BTC × 65000 = 0.65 USDT < 5: rejeitada antes de sair para a Binance.
    with pytest.raises(BinanceOrderError) as low:
        scalp_binance.place_aggressive_exit(
            api_key="k",
            api_secret="s",
            quantity=Decimal("0.00001"),
            client_order_id="cfscalp_small",
            reference_price=Decimal("65000"),
        )
    assert "Notional" in str(low.value)
    assert captured == {}, "a ordem abaixo do filtro não chega à Binance"
    # 0.001 BTC × 65000 = 65 USDT >= 5: a MARKET sai sem preço nenhum.
    result = scalp_binance.place_aggressive_exit(
        api_key="k",
        api_secret="s",
        quantity=Decimal("0.001"),
        client_order_id="cfscalp_ok",
        reference_price=Decimal("65000"),
    )
    assert result["orderId"] == 9
    assert captured["params"]["type"] == "MARKET"
    assert "price" not in captured["params"]
    assert "timeInForce" not in captured["params"]


def test_binance_place_post_only_validates_the_notional_filter(monkeypatch):
    """Confirmação pedida no item 3: o post-only valida MIN_NOTIONAL antes de sair."""
    from app.services import scalp_binance
    from app.services.binance_spot_orders import BinanceOrderError

    captured: dict = {}

    def fake_signed_request(*, method, path, api_key, api_secret, params=None, base_url=None):
        captured.update({"method": method, "path": path, "params": dict(params or {})})
        return {"orderId": 11, "status": "NEW"}

    monkeypatch.setattr(scalp_binance, "signed_request", fake_signed_request)
    monkeypatch.setattr(
        scalp_binance,
        "get_symbol_info",
        lambda symbol, base_url=None: _symbol_info_with_notional("MIN_NOTIONAL"),
    )
    with pytest.raises(BinanceOrderError) as low:
        scalp_binance.place_post_only(
            api_key="k",
            api_secret="s",
            side="SELL",
            price=Decimal("65000"),
            quantity=Decimal("0.00001"),
            client_order_id="cfscalp_small",
        )
    assert "Notional" in str(low.value)
    assert captured == {}
    scalp_binance.place_post_only(
        api_key="k",
        api_secret="s",
        side="SELL",
        price=Decimal("65000"),
        quantity=Decimal("0.001"),
        client_order_id="cfscalp_ok",
    )
    assert captured["params"]["type"] == scalp_binance.ORDER_TYPE


class _RecordingEscape(FakeExchange):
    """Escape port that records every attempt, accepted or rejected."""

    def __init__(self, *, reject_code: str | None = None):
        super().__init__()
        self.aggressive_reject_code = reject_code
        self.escape_attempts: list[str] = []

    def place_aggressive_exit(self, **kwargs):
        self.escape_attempts.append(str(kwargs["client_order_id"]))
        assert "reference_price" in kwargs, "a agressiva valida o notional com preço de referência"
        return super().place_aggressive_exit(**kwargs)


def _escape_cycle(scalp_db, fx, user_id: str):
    return tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        free_usdt=Decimal("80"),
        free_btc=Decimal("0.011"),
        book=_book(),
    )


def test_a_rejected_escape_is_not_resent_on_the_next_cycle(scalp_db, caplog):
    """Correção pós-CR (item 3): sem tempestade de MARKET rejeitadas a cada ciclo."""
    caplog.set_level(logging.DEBUG)
    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = _RecordingEscape(reject_code="MARKET_REJECT")
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    _open_position(scalp_db, user_id, seconds=HOLD_AFTER_FILL_S + 1)

    first = _escape_cycle(scalp_db, fx, user_id)
    second = _escape_cycle(scalp_db, fx, user_id)

    assert first.sent is False
    assert second.sent is False
    assert len(fx.escape_attempts) == 1, "o ciclo seguinte não reenvia a agressiva rejeitada"
    assert fx.aggressive == []
    messages = [record.getMessage() for record in caplog.records]
    assert sum("scalp aggressive exit failed" in message for message in messages) == 1
    assert any("scalp aggressive exit backoff" in message for message in messages)


def test_the_retried_escape_keeps_one_client_order_id(monkeypatch, scalp_db, diagnostic_log):
    """O mesmo id fica como chave de reconciliação entre tentativas."""
    monkeypatch.setattr("app.services.scalp_service.AGGRESSIVE_RETRY_SECONDS", 0.0)
    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = _RecordingEscape(reject_code="MARKET_REJECT")
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    _open_position(scalp_db, user_id, seconds=HOLD_AFTER_FILL_S + 1)

    for _ in range(3):
        _escape_cycle(scalp_db, fx, user_id)

    assert len(fx.escape_attempts) == 3
    assert len(set(fx.escape_attempts)) == 1, "o id não é renovado a cada tentativa"
    assert fx.escape_attempts[0].startswith("cfscalp_")


def _resting_exit(scalp_db, user_id: str) -> None:
    state = get_or_create_state(scalp_db, user_id)
    state.rest_client_order_id = "cfscalp_passive_exit"
    state.rest_side = "SELL"
    state.rest_price = Decimal("65300")
    state.rest_role = "exit"
    state.rest_opened_at = datetime.utcnow() - timedelta(seconds=HOLD_AFTER_FILL_S)
    scalp_db.commit()


class _CancelFailingExchange(FakeExchange):
    """Passive cancel rejected until ``fail_cancel`` is turned off."""

    def __init__(self, *, fail_cancel: bool = True):
        super().__init__()
        self.fail_cancel = fail_cancel

    def cancel_bot_order(self, **kwargs):
        if self.fail_cancel:
            from app.services.binance_spot_orders import BinanceOrderError

            raise BinanceOrderError("cancel refused", code=-2011)
        return super().cancel_bot_order(**kwargs)


def test_escape_is_deferred_when_the_passive_cancel_fails(monkeypatch, scalp_db, caplog):
    """E3: cancelar a passiva que falha não envia a agressiva no mesmo ciclo.

    A ordem passiva pode continuar viva e preencher; uma MARKET enviada na
    mesma podia vender duas vezes (oversell). O escape é adiado (mesma chave de
    reconciliação e backoff) e o estado resting é mantido para reconciliação.
    """
    caplog.set_level(logging.WARNING)
    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = _CancelFailingExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    _open_position(scalp_db, user_id, seconds=HOLD_AFTER_FILL_S + 1)
    _resting_exit(scalp_db, user_id)

    first = _escape_cycle(scalp_db, fx, user_id)
    assert first.sent is False
    assert fx.aggressive == [], "sem agressiva enquanto a passiva pode estar viva"
    state = get_or_create_state(scalp_db, user_id)
    assert state.rest_client_order_id == "cfscalp_passive_exit"
    messages = [record.getMessage() for record in caplog.records]
    assert any("scalp aggressive exit deferred" in message for message in messages)

    # Cancel ack + backoff elapsed -> the escape goes out in the next cycle.
    monkeypatch.setattr("app.services.scalp_service.AGGRESSIVE_RETRY_SECONDS", 0.0)
    fx.fail_cancel = False
    second = _escape_cycle(scalp_db, fx, user_id)
    assert second.sent is True
    assert "cfscalp_passive_exit" in fx.cancelled
    assert len(fx.aggressive) == 1
    state = get_or_create_state(scalp_db, user_id)
    assert Decimal(str(state.inventory_btc)) == Decimal("0")


class _DustExchange(FakeExchange):
    """Escape always rejected by the symbol filter: the remainder is dust."""

    def __init__(self):
        super().__init__()
        self.escape_attempts: list[str] = []

    def place_aggressive_exit(self, **kwargs):
        from app.services.binance_spot_orders import (
            ORDER_FILTER_REJECTED_CODE,
            BinanceOrderError,
        )

        self.escape_attempts.append(str(kwargs["client_order_id"]))
        raise BinanceOrderError(
            "Notional abaixo do filtro da Binance", code=ORDER_FILTER_REJECTED_CODE
        )


def test_dust_remainder_closes_the_position_instead_of_retrying_forever(scalp_db, caplog):
    """N3: resto abaixo do MIN_NOTIONAL é dust — não fica a re-tentar para sempre."""
    caplog.set_level(logging.WARNING)
    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = _DustExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    state = get_or_create_state(scalp_db, user_id)
    state.floor_btc = Decimal("0")
    # 0.00001 BTC × ~65000 = 0.65 USDT < MIN_NOTIONAL (5): não é executável.
    state.inventory_btc = Decimal("0.00001")
    # Entrada acima do realizável (bid 65000): a perda do dust tem de ser
    # lançada, não evaporar com o `unrealized`.
    state.avg_entry_quote = Decimal("66000")
    state.position_opened_at = datetime.utcnow() - timedelta(seconds=HOLD_AFTER_FILL_S + 1)
    scalp_db.commit()

    result = _escape_cycle(scalp_db, fx, user_id)
    assert result.sent is False
    assert len(fx.escape_attempts) == 1
    state = get_or_create_state(scalp_db, user_id)
    assert Decimal(str(state.inventory_btc)) == Decimal("0"), "posição encerrada como dust"
    assert state.avg_entry_quote is None
    assert state.position_opened_at is None
    expected_loss = (Decimal("65000") - Decimal("66000")) * Decimal("0.00001")
    assert Decimal(str(state.realized_pnl_quote)) == expected_loss, "perda do dust lançada"
    messages = [record.getMessage() for record in caplog.records]
    assert any("scalp aggressive exit dust" in message for message in messages)

    # No next attempt and the bot is no longer holding an open position.
    _escape_cycle(scalp_db, fx, user_id)
    assert len(fx.escape_attempts) == 1
    state = get_or_create_state(scalp_db, user_id)
    assert state.position_opened_at is None
