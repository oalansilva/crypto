from __future__ import annotations

import asyncio
import time
import uuid
from decimal import Decimal
import pytest

from app.services.scalp_btcusdt_stream import (
    FRESH_AGE_MS,
    ensure_scalp_btcusdt_stream,
    get_scalp_btcusdt_memory,
    scalp_stream_task_running,
    stop_scalp_btcusdt_stream,
)
from app.services.scalp_engine import Book
from app.services.scalp_loop import scalp_loop
from app.services.scalp_service import (
    BOOK_UNAVAILABLE_COPY,
    get_or_create_state,
    list_enabled_user_ids,
    status_payload,
    tick_user,
)
from tests.unit.test_scalp_direcional_jev import FakeExchange, _add_key, _buy_signal, scalp_db, set_switch


def _seed_fresh_touch(memory, *, bid: str = "65000", ask: str = "65010") -> None:
    memory.reset_for_tests()
    memory.set_ws_connected(True)
    memory.ingest_book_ticker(
        {
            "s": "BTCUSDT",
            "b": bid,
            "a": ask,
            "B": "1.2",
            "A": "0.8",
            "E": int(time.time() * 1000),
        }
    )


def _age_touch(memory, age_ms: int) -> None:
    with memory._lock:  # noqa: SLF001 — test helper
        assert memory._touch is not None
        memory._touch.received_at = time.time() - (age_ms / 1000.0)


def test_cycle_uses_memory_not_rest_book(scalp_db, monkeypatch):
    memory = get_scalp_btcusdt_memory()
    _seed_fresh_touch(memory)
    fetch_calls: list[int] = []

    def _blocked_fetch(*_args, **_kwargs):
        fetch_calls.append(1)
        raise AssertionError("REST bookTicker must not run with scalp ligado")

    monkeypatch.setattr("app.services.scalp_binance.fetch_book", _blocked_fetch)

    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    result = tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        jev_fn=lambda _payload: _buy_signal(),
        free_usdt=Decimal("80"),
        free_btc=Decimal("0.01"),
    )
    assert fetch_calls == []
    assert result.skipped in {None, "hold", "jev_floor", "jev_target", "jev_in_flight"} or result.sent


def test_stale_book_after_jev_skips_send(scalp_db):
    memory = get_scalp_btcusdt_memory()
    _seed_fresh_touch(memory)

    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))

    def _jev_then_stale(_payload):
        _age_touch(memory, FRESH_AGE_MS + 50)
        return _buy_signal()

    result = tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        jev_fn=_jev_then_stale,
        free_usdt=Decimal("80"),
        free_btc=Decimal("0.01"),
    )
    assert result.sent is False
    assert result.skipped == "no_book"
    assert fx.placed == []


def test_stale_age_ms_blocks_send_and_cancels_resting(scalp_db):
    memory = get_scalp_btcusdt_memory()
    _seed_fresh_touch(memory)
    _age_touch(memory, FRESH_AGE_MS + 50)

    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    state = get_or_create_state(scalp_db, user_id)
    state.rest_client_order_id = "cfscalp_resting01"
    state.rest_side = "BUY"
    state.rest_price = Decimal("64000")
    scalp_db.commit()

    result = tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        jev_fn=lambda _payload: _buy_signal(),
        free_usdt=Decimal("80"),
        free_btc=Decimal("0.01"),
    )
    assert result.sent is False
    assert result.skipped == "no_book"
    assert "all" in fx.cancelled or "cfscalp_resting01" in fx.cancelled


def test_ws_disconnect_fails_closed(scalp_db):
    memory = get_scalp_btcusdt_memory()
    _seed_fresh_touch(memory)
    memory.set_ws_connected(False)

    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))

    result = tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        jev_fn=lambda _payload: _buy_signal(),
        free_usdt=Decimal("80"),
        free_btc=Decimal("0.01"),
    )
    assert result.sent is False
    assert result.skipped == "no_book"


def test_fresh_touch_allows_cycle_with_injected_book_path(scalp_db):
    memory = get_scalp_btcusdt_memory()
    _seed_fresh_touch(memory)

    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    result = tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        jev_fn=lambda _payload: _buy_signal(),
        free_usdt=Decimal("80"),
        free_btc=Decimal("0.01"),
    )
    assert memory.age_ms() is not None
    assert memory.age_ms() <= FRESH_AGE_MS
    assert result.sent is True


def test_status_shows_livro_indisponivel_when_on_and_stale(scalp_db):
    memory = get_scalp_btcusdt_memory()
    _seed_fresh_touch(memory)
    _age_touch(memory, 900)

    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))

    payload = status_payload(scalp_db, user_id, free_usdt=Decimal("80"), mid=Decimal("65005"))
    assert payload["state"] == "on"
    assert payload["status_text"] == BOOK_UNAVAILABLE_COPY
    assert payload["book_available"] is False


@pytest.mark.asyncio
async def test_scalp_loop_two_enabled_users_share_one_stream(scalp_db, monkeypatch):
    await stop_scalp_btcusdt_stream()
    memory = get_scalp_btcusdt_memory()
    memory.reset_for_tests()
    _seed_fresh_touch(memory)

    async def fake_consume(stop_event: asyncio.Event) -> None:
        memory.set_ws_connected(True)
        memory.record_connect()
        try:
            await stop_event.wait()
        finally:
            memory.set_ws_connected(False)

    monkeypatch.setattr(
        "app.services.scalp_btcusdt_stream._consume_stream",
        fake_consume,
    )

    user_a = str(uuid.uuid4())
    user_b = str(uuid.uuid4())
    _add_key(scalp_db, user_a)
    _add_key(scalp_db, user_b)
    fx = FakeExchange()
    set_switch(scalp_db, user_a, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    set_switch(scalp_db, user_b, enabled=True, exchange=fx, free_btc=Decimal("0.01"))

    class _DbSession:
        def __init__(self, db):
            self._db = db

        def close(self) -> None:
            pass

        def __getattr__(self, name):
            return getattr(self._db, name)

    monkeypatch.setattr("app.services.scalp_loop.SessionLocal", lambda: _DbSession(scalp_db))
    monkeypatch.setattr("app.services.scalp_loop.tick_user", lambda _db, _uid: None)

    stop = asyncio.Event()

    loop_task = asyncio.create_task(scalp_loop(stop_event=stop))
    await asyncio.sleep(0.1)
    assert scalp_stream_task_running() is True
    assert memory.connection_count() == 1
    assert len(list_enabled_user_ids(scalp_db)) == 2
    stop.set()
    await loop_task
    await stop_scalp_btcusdt_stream()

    assert scalp_stream_task_running() is False


@pytest.mark.asyncio
async def test_single_shared_stream_task_per_process(monkeypatch):
    memory = get_scalp_btcusdt_memory()
    memory.reset_for_tests()

    async def fake_consume(stop_event: asyncio.Event) -> None:
        memory.set_ws_connected(True)
        memory.record_connect()
        try:
            await stop_event.wait()
        finally:
            memory.set_ws_connected(False)

    monkeypatch.setattr(
        "app.services.scalp_btcusdt_stream._consume_stream",
        fake_consume,
    )
    await ensure_scalp_btcusdt_stream()
    task_a = scalp_stream_task_running()
    await ensure_scalp_btcusdt_stream()
    task_b = scalp_stream_task_running()
    assert task_a and task_b
    await stop_scalp_btcusdt_stream()
    assert not scalp_stream_task_running()


def test_explicit_book_param_bypasses_memory_for_tests(scalp_db):
    memory = get_scalp_btcusdt_memory()
    memory.reset_for_tests()
    memory.set_ws_connected(False)

    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    result = tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        jev_fn=lambda _payload: _buy_signal(),
        free_usdt=Decimal("80"),
        free_btc=Decimal("0.01"),
        book=Book(bid=Decimal("65000"), ask=Decimal("65010")),
    )
    assert result.sent is True
