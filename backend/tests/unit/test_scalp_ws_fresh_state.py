"""Scalp WS fresh-state; scalp_db via postgres_isolation and unit_database_url (test_scalp_direcional_jev)."""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from decimal import Decimal
import pytest
import websockets

from app.services.scalp_btcusdt_snapshot_store import publish_scalp_btcusdt_snapshot
from app.services.scalp_btcusdt_stream import (
    FRESH_AGE_MS,
    TRADE_WINDOW_SECONDS,
    _consume_stream,
    _handle_message,
    _stream_url,
    _to_decimal,
    ensure_scalp_btcusdt_stream,
    get_scalp_btcusdt_memory,
    scalp_stream_task_running,
    stop_scalp_btcusdt_stream,
)
from app.services.binance_spot_orders import BinanceOrderError
from app.services.scalp_engine import Book
from app.services.scalp_loop import scalp_loop, _tick_user_blocking
from app.services.scalp_service import (
    BOOK_UNAVAILABLE_COPY,
    get_or_create_state,
    list_enabled_user_ids,
    status_payload,
    tick_user,
)
from tests.unit.test_scalp_direcional_jev import (
    FakeExchange,
    _add_key,
    _buy_signal,
    scalp_db,
    set_switch,
)


@pytest.fixture(autouse=True)
def _isolated_scalp_btcusdt_snapshot(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "CRYPTO_SCALP_BTCUSDT_SNAPSHOT_PATH", str(tmp_path / "scalp-btcusdt-snapshot.json")
    )


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
    assert (
        result.skipped in {None, "hold", "jev_floor", "jev_target", "jev_in_flight"} or result.sent
    )


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
    monkeypatch.setattr("app.services.scalp_loop._tick_user_blocking", lambda _uid: None)

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


def test_to_decimal_invalid_returns_zero():
    assert _to_decimal("not-a-number") == Decimal("0")
    assert _to_decimal(object()) == Decimal("0")


def test_memory_ingest_book_ticker_rejects_bad_symbol_and_prices():
    memory = get_scalp_btcusdt_memory()
    memory.reset_for_tests()
    memory.ingest_book_ticker({"s": "ETHUSDT", "b": "1", "a": "2"})
    assert memory.read_book() is None
    memory.ingest_book_ticker({"s": "BTCUSDT", "b": "0", "a": "65010"})
    assert memory.read_book() is None
    memory.ingest_book_ticker({"s": "BTCUSDT", "b": "65000", "a": "-1"})
    assert memory.read_book() is None


def test_memory_ingest_agg_trade_rejects_bad_rows_and_prunes_window():
    memory = get_scalp_btcusdt_memory()
    memory.reset_for_tests()
    memory.ingest_agg_trade({"s": "ETHUSDT", "p": "1", "q": "1", "T": 1000})
    assert memory.recent_trades() == []
    memory.ingest_agg_trade({"s": "BTCUSDT", "p": "65000", "q": "0", "T": 1000})
    assert memory.recent_trades() == []

    now_ms = int(time.time() * 1000)
    old_ms = now_ms - int((TRADE_WINDOW_SECONDS + 2) * 1000)
    memory.ingest_agg_trade({"s": "BTCUSDT", "p": "64000", "q": "0.01", "T": old_ms})
    memory.ingest_agg_trade({"s": "BTCUSDT", "p": "65000", "q": "0.02", "T": now_ms})
    trades = memory.recent_trades()
    assert len(trades) == 1
    assert trades[0].price == Decimal("65000")


def test_read_touch_empty_and_disconnect_clears_touch():
    memory = get_scalp_btcusdt_memory()
    memory.reset_for_tests()
    assert memory.read_touch() is None
    _seed_fresh_touch(memory)
    assert memory.read_touch() is not None
    memory.set_ws_connected(False)
    assert memory.read_touch() is None


def test_handle_message_json_agg_trade_and_book_ticker():
    memory = get_scalp_btcusdt_memory()
    memory.reset_for_tests()
    _handle_message(memory, "not-json")
    _handle_message(memory, "[]")
    _handle_message(
        memory,
        json.dumps(
            {
                "data": {
                    "e": "aggTrade",
                    "s": "BTCUSDT",
                    "p": "65000",
                    "q": "0.01",
                    "T": int(time.time() * 1000),
                    "m": True,
                }
            }
        ),
    )
    assert len(memory.recent_trades()) == 1
    _handle_message(
        memory,
        json.dumps(
            {
                "s": "BTCUSDT",
                "b": "64990",
                "a": "65010",
                "B": "1",
                "A": "2",
                "E": int(time.time() * 1000),
            }
        ),
    )
    book = memory.read_book()
    assert book is not None
    assert book.bid == Decimal("64990")
    _handle_message(memory, json.dumps({"data": "nope"}))
    _handle_message(memory, json.dumps({"data": 123}))
    _handle_message(
        memory,
        json.dumps({"s": "ETHUSDT", "b": "1", "a": "2", "E": 1}),
    )


def test_stream_url_from_settings(monkeypatch):
    class _Settings:
        binance_ws_base_url = "wss://example.test/"

    monkeypatch.setattr(
        "app.services.scalp_btcusdt_stream.get_settings",
        lambda: _Settings(),
    )
    url = _stream_url()
    assert url.startswith("wss://example.test/stream?streams=")
    assert "btcusdt@bookTicker" in url
    assert "btcusdt@aggTrade" in url


@pytest.mark.asyncio
async def test_consume_stream_ws_paths(monkeypatch):
    import app.services.scalp_btcusdt_stream as stream_mod

    memory = get_scalp_btcusdt_memory()
    memory.reset_for_tests()
    stop = asyncio.Event()

    class _Settings:
        binance_ws_base_url = "wss://stream.test"
        binance_ws_reconnect_base_seconds = 0.5
        binance_ws_reconnect_max_seconds = 1.0
        binance_ws_heartbeat_timeout_seconds = 8.0

    monkeypatch.setattr(stream_mod, "get_settings", lambda: _Settings())
    monkeypatch.setattr(stream_mod.random, "uniform", lambda _a, _b: 0.0)

    attempts = 0

    class _HeartbeatSocket:
        def __init__(self) -> None:
            self._recv_count = 0

        async def recv(self) -> str:
            self._recv_count += 1
            if self._recv_count == 1:
                return json.dumps(
                    {
                        "data": {
                            "e": "aggTrade",
                            "s": "BTCUSDT",
                            "p": "65001",
                            "q": "0.001",
                            "T": int(time.time() * 1000),
                            "m": False,
                        }
                    }
                )
            raise asyncio.TimeoutError

    class _ClosedSocket:
        async def recv(self) -> str:
            raise websockets.ConnectionClosed(None, None)

    class _FakeConnect:
        def __init__(self, socket) -> None:
            self._socket = socket

        async def __aenter__(self):
            return self._socket

        async def __aexit__(self, exc_type, exc, tb) -> bool:
            return False

    def _fake_connect(*_args, **_kwargs):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return _FakeConnect(_HeartbeatSocket())
        if attempts == 2:
            return _FakeConnect(_ClosedSocket())
        stop.set()
        raise RuntimeError("ws connect failed")

    monkeypatch.setattr(stream_mod.websockets, "connect", _fake_connect)

    await asyncio.wait_for(_consume_stream(stop), timeout=3.0)

    assert attempts >= 1
    assert memory.connection_count() >= 1
    assert memory.stream_connected() is False


@pytest.mark.asyncio
async def test_consume_stream_connect_failure_before_stop(monkeypatch):
    import app.services.scalp_btcusdt_stream as stream_mod

    memory = get_scalp_btcusdt_memory()
    memory.reset_for_tests()
    stop = asyncio.Event()

    class _Settings:
        binance_ws_base_url = "wss://stream.test"
        binance_ws_reconnect_base_seconds = 0.5
        binance_ws_reconnect_max_seconds = 1.0
        binance_ws_heartbeat_timeout_seconds = 8.0

    monkeypatch.setattr(stream_mod, "get_settings", lambda: _Settings())
    monkeypatch.setattr(stream_mod.random, "uniform", lambda _a, _b: 0.0)

    def _failing_connect(*_args, **_kwargs):
        raise OSError("ws down")

    monkeypatch.setattr(stream_mod.websockets, "connect", _failing_connect)

    runner = asyncio.create_task(_consume_stream(stop))
    await asyncio.sleep(0.05)
    stop.set()
    await asyncio.wait_for(runner, timeout=3.0)
    assert memory.stream_connected() is False


@pytest.mark.asyncio
async def test_consume_stream_propagates_cancellation(monkeypatch):
    import app.services.scalp_btcusdt_stream as stream_mod

    memory = get_scalp_btcusdt_memory()
    memory.reset_for_tests()
    stop = asyncio.Event()

    class _Settings:
        binance_ws_base_url = "wss://stream.test"
        binance_ws_reconnect_base_seconds = 0.5
        binance_ws_reconnect_max_seconds = 1.0
        binance_ws_heartbeat_timeout_seconds = 8.0

    class _HangSocket:
        async def recv(self) -> str:
            await asyncio.sleep(3600)
            return "{}"

    class _FakeConnect:
        async def __aenter__(self):
            return _HangSocket()

        async def __aexit__(self, exc_type, exc, tb) -> bool:
            return False

    monkeypatch.setattr(stream_mod, "get_settings", lambda: _Settings())
    monkeypatch.setattr(stream_mod.websockets, "connect", lambda *_a, **_k: _FakeConnect())

    runner = asyncio.create_task(_consume_stream(stop))
    await asyncio.sleep(0.05)
    runner.cancel()
    with pytest.raises(asyncio.CancelledError):
        await runner
    assert memory.stream_connected() is False


@pytest.mark.asyncio
async def test_consume_stream_exits_immediately_when_stopped(monkeypatch):
    import app.services.scalp_btcusdt_stream as stream_mod

    memory = get_scalp_btcusdt_memory()
    memory.reset_for_tests()
    stop = asyncio.Event()
    stop.set()

    def _should_not_connect(*_args, **_kwargs):
        raise AssertionError("connect must not run when stop is already set")

    monkeypatch.setattr(stream_mod.websockets, "connect", _should_not_connect)
    await _consume_stream(stop)
    assert memory.stream_connected() is False


def test_tick_user_cached_balance_binance_error(scalp_db, monkeypatch):
    memory = get_scalp_btcusdt_memory()
    _seed_fresh_touch(memory)

    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))

    def _raise_balance(*_args, **_kwargs):
        raise BinanceOrderError("balance unavailable")

    monkeypatch.setattr("app.services.scalp_service._cached_balances", _raise_balance)

    result = tick_user(
        scalp_db,
        user_id,
        exchange=fx,
        jev_fn=lambda _payload: _buy_signal(),
    )
    assert result.skipped == "t_zero"


def test_tick_user_memory_book_missing_after_available(scalp_db, monkeypatch):
    memory = get_scalp_btcusdt_memory()
    _seed_fresh_touch(memory)

    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))

    monkeypatch.setattr(memory, "read_book", lambda: None)

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


def test_tick_user_fresh_book_gone_before_send(scalp_db, monkeypatch):
    memory = get_scalp_btcusdt_memory()
    _seed_fresh_touch(memory)

    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))

    calls = {"n": 0}
    real_read_book = memory.read_book

    def _read_book_twice():
        calls["n"] += 1
        if calls["n"] <= 1:
            return real_read_book()
        return None

    monkeypatch.setattr(memory, "read_book", _read_book_twice)

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


def test_status_payload_uses_live_book_for_mid(scalp_db, monkeypatch):
    memory = get_scalp_btcusdt_memory()
    _seed_fresh_touch(memory, bid="64000", ask="64020")

    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))

    monkeypatch.setattr(
        "app.services.scalp_service._cached_balances",
        lambda *_a, **_k: (Decimal("120"), Decimal("0.02")),
    )
    monkeypatch.setattr(
        "app.services.scalp_service.LiveExchange",
        lambda: fx,
    )

    payload = status_payload(scalp_db, user_id)
    assert payload["state"] == "on"
    assert payload["book_available"] is True
    assert payload["t_quote"] != "0"


def test_status_payload_mark_from_memory_when_mid_zero(scalp_db):
    memory = get_scalp_btcusdt_memory()
    _seed_fresh_touch(memory, bid="64000", ask="64020")

    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))

    payload = status_payload(scalp_db, user_id, free_usdt=Decimal("80"))
    assert payload["state"] == "on"
    assert payload["pnl_quote"] is not None


def test_status_payload_swallows_balance_errors(scalp_db, monkeypatch):
    memory = get_scalp_btcusdt_memory()
    _seed_fresh_touch(memory)

    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))

    def _balance_error(*_args, **_kwargs):
        raise RuntimeError("balance down")

    monkeypatch.setattr("app.services.scalp_service._cached_balances", _balance_error)
    monkeypatch.setattr("app.services.scalp_service.LiveExchange", lambda: fx)

    payload = status_payload(scalp_db, user_id)
    assert payload["state"] == "on"


@pytest.mark.asyncio
async def test_scalp_loop_stops_stream_without_enabled_users(scalp_db, monkeypatch):
    await stop_scalp_btcusdt_stream()
    stop_calls = 0

    async def _record_stop() -> None:
        nonlocal stop_calls
        stop_calls += 1

    monkeypatch.setattr("app.services.scalp_loop.stop_scalp_btcusdt_stream", _record_stop)

    async def _blocked_ensure() -> None:
        raise AssertionError("ensure must not run without enabled users")

    monkeypatch.setattr("app.services.scalp_loop.ensure_scalp_btcusdt_stream", _blocked_ensure)

    class _DbSession:
        def __init__(self, db):
            self._db = db

        def close(self) -> None:
            pass

        def __getattr__(self, name):
            return getattr(self._db, name)

    monkeypatch.setattr("app.services.scalp_loop.SessionLocal", lambda: _DbSession(scalp_db))
    stop = asyncio.Event()
    loop_task = asyncio.create_task(scalp_loop(stop_event=stop))
    await asyncio.sleep(0.12)
    assert stop_calls >= 1
    stop.set()
    await loop_task


def test_status_reads_cross_process_snapshot_when_api_memory_empty(scalp_db):
    """Split-brain: loop lock elsewhere but worker snapshot is fresh → panel must not lie."""
    memory = get_scalp_btcusdt_memory()
    memory.reset_for_tests()

    now = time.time()
    publish_scalp_btcusdt_snapshot(
        ws_connected=True,
        received_at=now,
        bid="65000",
        ask="65010",
    )

    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    set_switch(scalp_db, user_id, enabled=True, exchange=FakeExchange(), free_btc=Decimal("0.01"))

    payload = status_payload(scalp_db, user_id, free_usdt=Decimal("80"), mid=Decimal("0"))
    assert payload["state"] == "on"
    assert payload["book_available"] is True
    assert payload["book_age_ms"] is not None
    assert payload["book_age_ms"] <= FRESH_AGE_MS
    assert payload["status_text"] != BOOK_UNAVAILABLE_COPY


def test_status_fail_closed_when_snapshot_stale_and_no_local_stream(scalp_db):
    memory = get_scalp_btcusdt_memory()
    memory.reset_for_tests()

    publish_scalp_btcusdt_snapshot(
        ws_connected=True,
        received_at=time.time() - 2.0,
        bid="65000",
        ask="65010",
    )

    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    set_switch(scalp_db, user_id, enabled=True, exchange=FakeExchange(), free_btc=Decimal("0.01"))

    payload = status_payload(scalp_db, user_id, free_usdt=Decimal("80"), mid=Decimal("65005"))
    assert payload["book_available"] is False
    assert payload["status_text"] == BOOK_UNAVAILABLE_COPY


def test_status_fail_closed_when_snapshot_ws_down(scalp_db):
    memory = get_scalp_btcusdt_memory()
    memory.reset_for_tests()

    publish_scalp_btcusdt_snapshot(
        ws_connected=False,
        received_at=None,
        bid=None,
        ask=None,
    )

    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    set_switch(scalp_db, user_id, enabled=True, exchange=FakeExchange(), free_btc=Decimal("0.01"))

    payload = status_payload(scalp_db, user_id, free_usdt=Decimal("80"), mid=Decimal("65005"))
    assert payload["book_available"] is False
    assert payload["status_text"] == BOOK_UNAVAILABLE_COPY


def test_local_stale_stream_wins_over_fresh_snapshot(scalp_db):
    memory = get_scalp_btcusdt_memory()
    _seed_fresh_touch(memory)
    _age_touch(memory, 900)

    publish_scalp_btcusdt_snapshot(
        ws_connected=True,
        received_at=time.time(),
        bid="65000",
        ask="65010",
    )

    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    set_switch(scalp_db, user_id, enabled=True, exchange=FakeExchange(), free_btc=Decimal("0.01"))

    payload = status_payload(scalp_db, user_id, free_usdt=Decimal("80"), mid=Decimal("65005"))
    assert payload["book_available"] is False
    assert payload["status_text"] == BOOK_UNAVAILABLE_COPY


def _loop_db_session(scalp_db):
    class _DbSession:
        def __init__(self, db):
            self._db = db

        def close(self) -> None:
            pass

        def __getattr__(self, name):
            return getattr(self._db, name)

    return _DbSession(scalp_db)


@pytest.mark.asyncio
async def test_scalp_loop_slow_jev_keeps_book_fresh(scalp_db, monkeypatch):
    """Slow Jev HTTP must not block the shared WS task from refreshing book age."""
    await stop_scalp_btcusdt_stream()
    memory = get_scalp_btcusdt_memory()
    _seed_fresh_touch(memory)
    peak_ages: list[int] = []

    async def fake_consume_with_ticks(stop_event: asyncio.Event) -> None:
        memory.set_ws_connected(True)
        memory.record_connect()
        try:
            while not stop_event.is_set():
                memory.ingest_book_ticker(
                    {
                        "s": "BTCUSDT",
                        "b": "65000",
                        "a": "65010",
                        "B": "1",
                        "A": "1",
                        "E": int(time.time() * 1000),
                    }
                )
                age = memory.age_ms()
                if age is not None:
                    peak_ages.append(age)
                await asyncio.sleep(0.05)
        finally:
            memory.set_ws_connected(False)

    monkeypatch.setattr(
        "app.services.scalp_btcusdt_stream._consume_stream",
        fake_consume_with_ticks,
    )

    def slow_jev(_payload):
        time.sleep(1.0)
        return _buy_signal()

    monkeypatch.setattr("app.services.scalp_service.request_jev", slow_jev)
    monkeypatch.setattr("app.services.scalp_service.jev_api_key", lambda: "test-key")

    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    monkeypatch.setattr("app.services.scalp_loop.SessionLocal", lambda: _loop_db_session(scalp_db))

    stop = asyncio.Event()
    loop_task = asyncio.create_task(scalp_loop(stop_event=stop))
    await asyncio.sleep(1.4)
    payload = status_payload(scalp_db, user_id, free_usdt=Decimal("80"), mid=Decimal("65005"))
    stop.set()
    await loop_task
    await stop_scalp_btcusdt_stream()

    assert peak_ages, "shared stream should keep ingesting bookTicker while Jev runs"
    assert max(peak_ages) <= FRESH_AGE_MS
    assert payload["book_available"] is True
    assert payload["status_text"] != BOOK_UNAVAILABLE_COPY


@pytest.mark.asyncio
async def test_tick_user_blocking_matches_to_thread_contract(scalp_db, monkeypatch):
    memory = get_scalp_btcusdt_memory()
    _seed_fresh_touch(memory)
    stop_ingest = asyncio.Event()
    peak_ages: list[int] = []

    async def ingest_loop() -> None:
        while not stop_ingest.is_set():
            memory.ingest_book_ticker(
                {
                    "s": "BTCUSDT",
                    "b": "65001",
                    "a": "65011",
                    "B": "1",
                    "A": "1",
                    "E": int(time.time() * 1000),
                }
            )
            age = memory.age_ms()
            if age is not None:
                peak_ages.append(age)
            await asyncio.sleep(0.05)

    ingest_task = asyncio.create_task(ingest_loop())

    def slow_jev(_payload):
        time.sleep(1.0)
        return _buy_signal()

    user_id = str(uuid.uuid4())
    _add_key(scalp_db, user_id)
    fx = FakeExchange()
    set_switch(scalp_db, user_id, enabled=True, exchange=fx, free_btc=Decimal("0.01"))
    monkeypatch.setattr("app.services.scalp_loop.SessionLocal", lambda: _loop_db_session(scalp_db))
    monkeypatch.setattr("app.services.scalp_service.request_jev", slow_jev)
    monkeypatch.setattr("app.services.scalp_service.jev_api_key", lambda: "test-key")

    await asyncio.to_thread(_tick_user_blocking, user_id)
    stop_ingest.set()
    await ingest_task

    assert peak_ages
    assert max(peak_ages) <= FRESH_AGE_MS
