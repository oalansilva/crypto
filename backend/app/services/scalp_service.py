"""Per-user scalp persistence, switch, and one cycle of the BTCUSDT loop."""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Callable, Optional, Protocol

from sqlalchemy.orm import Session

from app.models import ScalpFill, ScalpUserState, UserExchangeCredential
from app.services.binance_spot_orders import BinanceOrderError
from app.services.scalp_engine import (
    CROSS_REJECT_CODES,
    JEV_FLOOR_MS,
    JEV_TARGET_MS,
    SYMBOL,
    Book,
    CycleIntent,
    JevSignal,
    RestingOrder,
    Side,
    clip_inventory,
    compute_t,
    decide_cycle,
    is_bot_client_order_id,
    panel_state,
    pnl_quote,
    unrealized_pnl,
)
from app.services.scalp_btcusdt_snapshot_store import (
    resolve_scalp_btcusdt_book,
    resolve_scalp_btcusdt_freshness,
)
from app.services.scalp_btcusdt_stream import get_scalp_btcusdt_memory
from app.services.scalp_jev import jev_api_key, jev_available, request_jev
from app.services.user_exchange_credentials import BINANCE_PROVIDER, get_user_exchange_credential

logger = logging.getLogger(__name__)

BOOK_UNAVAILABLE_COPY = "livro indisponível"
BALANCE_CACHE_SECONDS = 5.0

STATUS_COPY = {
    "off": "Desligado — não envia ordem deste scalp. Inventário e P&L ficam visíveis.",
    "on": (
        "Ligado — o primeiro ciclo (livro + Jev a tempo) pode enviar post-only "
        "sem confirmar cada ordem. Operar continua ao lado."
    ),
    "kill": "Parado por kill — sem envio. Inventário e P&L ficam visíveis. Religar é o interruptor.",
    "nokey": "Sem chave Spot em Meu Perfil — não envia. Configure a chave Spot (a mesma do Operar).",
}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _dec(value: Any) -> Decimal:
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def has_spot_key(db: Session, user_id: str) -> bool:
    cred = get_user_exchange_credential(db, user_id, BINANCE_PROVIDER)
    return bool(cred and str(cred.api_key or "").strip() and str(cred.api_secret or "").strip())


def get_or_create_state(db: Session, user_id: str) -> ScalpUserState:
    row = db.query(ScalpUserState).filter(ScalpUserState.user_id == str(user_id)).first()
    if row is not None:
        return row
    row = ScalpUserState(
        user_id=str(user_id),
        enabled=False,
        killed=False,
        inventory_btc=Decimal("0"),
        floor_btc=Decimal("0"),
        realized_pnl_quote=Decimal("0"),
        fees_quote=Decimal("0"),
        jev_cost_quote=Decimal("0"),
        day_pnl_quote=Decimal("0"),
        calibration_hits=0,
        calibration_signals=0,
        jev_in_flight=False,
        inventory_clipped=False,
        created_at=_utcnow(),
        updated_at=_utcnow(),
    )
    db.add(row)
    db.flush()
    return row


class ExchangePort(Protocol):
    def book(self) -> Book: ...

    def free_balances(self, api_key: str, api_secret: str) -> tuple[Decimal, Decimal]: ...

    def place_post_only(
        self,
        *,
        api_key: str,
        api_secret: str,
        side: Side,
        price: Decimal,
        quantity: Decimal,
        client_order_id: str,
    ) -> dict[str, Any]: ...

    def cancel_bot_orders(self, *, api_key: str, api_secret: str) -> int: ...

    def cancel_bot_order(self, *, api_key: str, api_secret: str, client_order_id: str) -> None: ...

    def query_order(
        self, *, api_key: str, api_secret: str, client_order_id: str
    ) -> dict[str, Any]: ...


@dataclass
class _BalanceCacheEntry:
    usdt: Decimal
    btc: Decimal
    fetched_at: float


_balance_cache: dict[str, _BalanceCacheEntry] = {}


def invalidate_balance_cache(user_id: str) -> None:
    _balance_cache.pop(str(user_id), None)


def _cached_balances(
    user_id: str, port: ExchangePort, cred: UserExchangeCredential
) -> tuple[Decimal, Decimal]:
    key = str(user_id)
    now = time.time()
    hit = _balance_cache.get(key)
    if hit is not None and (now - hit.fetched_at) < BALANCE_CACHE_SECONDS:
        return hit.usdt, hit.btc
    live_usdt, live_btc = port.free_balances(cred.api_key, cred.api_secret)
    _balance_cache[key] = _BalanceCacheEntry(usdt=live_usdt, btc=live_btc, fetched_at=now)
    return live_usdt, live_btc


class LiveExchange:
    def book(self) -> Book:
        from app.services.scalp_binance import fetch_book

        return fetch_book()

    def free_balances(self, api_key: str, api_secret: str) -> tuple[Decimal, Decimal]:
        from app.services.scalp_binance import fetch_free_usdt_btc

        return fetch_free_usdt_btc(api_key=api_key, api_secret=api_secret)

    def place_post_only(
        self,
        *,
        api_key: str,
        api_secret: str,
        side: Side,
        price: Decimal,
        quantity: Decimal,
        client_order_id: str,
    ) -> dict[str, Any]:
        from app.services.scalp_binance import place_post_only

        return place_post_only(
            api_key=api_key,
            api_secret=api_secret,
            side=side,
            price=price,
            quantity=quantity,
            client_order_id=client_order_id,
        )

    def cancel_bot_orders(self, *, api_key: str, api_secret: str) -> int:
        from app.services.scalp_binance import cancel_all_bot_orders

        return cancel_all_bot_orders(api_key=api_key, api_secret=api_secret)

    def cancel_bot_order(self, *, api_key: str, api_secret: str, client_order_id: str) -> None:
        from app.services.scalp_binance import cancel_bot_order

        cancel_bot_order(api_key=api_key, api_secret=api_secret, client_order_id=client_order_id)

    def query_order(self, *, api_key: str, api_secret: str, client_order_id: str) -> dict[str, Any]:
        from app.services.scalp_binance import query_order

        return query_order(api_key=api_key, api_secret=api_secret, client_order_id=client_order_id)


JevFn = Callable[[dict[str, Any]], JevSignal]


@dataclass
class CycleResult:
    user_id: str
    intent: CycleIntent
    sent: bool
    killed: bool
    skipped: Optional[str]


def _credential(db: Session, user_id: str) -> Optional[UserExchangeCredential]:
    cred = get_user_exchange_credential(db, user_id, BINANCE_PROVIDER)
    if cred is None:
        return None
    if not str(cred.api_key or "").strip() or not str(cred.api_secret or "").strip():
        return None
    return cred


def _resting(state: ScalpUserState) -> Optional[RestingOrder]:
    cid = str(state.rest_client_order_id or "")
    side = str(state.rest_side or "").upper()
    if not cid or side not in {"BUY", "SELL"} or state.rest_price is None:
        return None
    return RestingOrder(client_order_id=cid, side=side, price=_dec(state.rest_price))  # type: ignore[arg-type]


def _elapsed_ms(state: ScalpUserState, now: datetime) -> Optional[int]:
    if state.last_jev_at is None:
        return None
    delta = now - state.last_jev_at
    return int(delta.total_seconds() * 1000)


def _apply_fill(
    state: ScalpUserState, *, side: Side, quantity: Decimal, price: Decimal, fee: Decimal
) -> None:
    qty = max(Decimal("0"), quantity)
    if qty <= 0:
        return
    if side == "BUY":
        prev = _dec(state.inventory_btc)
        avg = _dec(state.avg_entry_quote) if state.avg_entry_quote is not None else price
        new_inv = prev + qty
        if new_inv > 0:
            state.avg_entry_quote = ((avg * prev) + (price * qty)) / new_inv
        state.inventory_btc = new_inv
    else:
        prev = _dec(state.inventory_btc)
        sell_qty = min(qty, prev)
        avg = _dec(state.avg_entry_quote) if state.avg_entry_quote is not None else price
        realized = (price - avg) * sell_qty
        state.realized_pnl_quote = _dec(state.realized_pnl_quote) + realized
        remaining = prev - sell_qty
        state.inventory_btc = remaining
        if remaining <= 0:
            state.avg_entry_quote = None
    state.fees_quote = _dec(state.fees_quote) + max(Decimal("0"), fee)


def _refresh_day_pnl(state: ScalpUserState, *, mid: Decimal) -> Decimal:
    unrealized = unrealized_pnl(
        inventory_btc=_dec(state.inventory_btc),
        avg_entry=_dec(state.avg_entry_quote) if state.avg_entry_quote is not None else None,
        mid=mid,
    )
    total = pnl_quote(
        realized=_dec(state.realized_pnl_quote),
        unrealized=unrealized,
        fees=_dec(state.fees_quote),
        jev_cost=_dec(state.jev_cost_quote),
    )
    state.day_pnl_quote = total
    return total


def _cancel_resting(
    state: ScalpUserState,
    *,
    cred: Optional[UserExchangeCredential],
    exchange: ExchangePort,
    all_bot: bool = False,
) -> None:
    if cred is None:
        state.rest_client_order_id = None
        state.rest_side = None
        state.rest_price = None
        return
    try:
        if all_bot:
            exchange.cancel_bot_orders(api_key=cred.api_key, api_secret=cred.api_secret)
        elif state.rest_client_order_id:
            exchange.cancel_bot_order(
                api_key=cred.api_key,
                api_secret=cred.api_secret,
                client_order_id=str(state.rest_client_order_id),
            )
    except BinanceOrderError as exc:
        logger.warning("scalp cancel failed user=%s code=%s", state.user_id, exc.code)
    state.rest_client_order_id = None
    state.rest_side = None
    state.rest_price = None


_OPEN_ORDER_STATUSES = frozenset({"NEW", "PARTIALLY_FILLED", "PENDING_CANCEL"})
_MISSING_ORDER_CODES = frozenset({-2013})


def _booked_qty(db: Session, user_id: str, client_order_id: str) -> Decimal:
    rows = (
        db.query(ScalpFill.quantity)
        .filter(
            ScalpFill.user_id == str(user_id),
            ScalpFill.client_order_id == client_order_id,
        )
        .all()
    )
    total = Decimal("0")
    for (qty,) in rows:
        total += _dec(qty)
    return total


def _live_switch_flags(db: Session, user_id: str) -> tuple[bool, bool]:
    row = (
        db.query(ScalpUserState.enabled, ScalpUserState.killed)
        .filter(ScalpUserState.user_id == str(user_id))
        .first()
    )
    if row is None:
        return False, False
    return bool(row.enabled), bool(row.killed)


def _sync_resting_order(
    db: Session,
    state: ScalpUserState,
    *,
    cred: Optional[UserExchangeCredential],
    exchange: ExchangePort,
) -> ScalpUserState:
    cid = str(state.rest_client_order_id or "")
    if not cid or cred is None:
        return state
    try:
        payload = exchange.query_order(
            api_key=cred.api_key,
            api_secret=cred.api_secret,
            client_order_id=cid,
        )
    except BinanceOrderError as exc:
        logger.warning("scalp query_order failed user=%s code=%s", state.user_id, exc.code)
        if exc.code in _MISSING_ORDER_CODES:
            state.rest_client_order_id = None
            state.rest_side = None
            state.rest_price = None
        return state
    if not payload:
        return state
    status = str(payload.get("status") or "").upper()
    executed = _dec(payload.get("executedQty"))
    side_raw = str(payload.get("side") or state.rest_side or "").upper()
    if executed > 0 and side_raw in {"BUY", "SELL"}:
        booked = _booked_qty(db, str(state.user_id), cid)
        delta = executed - booked
        if delta > 0:
            quote = _dec(payload.get("cummulativeQuoteQty"))
            avg = (
                (quote / executed)
                if executed > 0 and quote > 0
                else _dec(payload.get("price") or state.rest_price)
            )
            apply_bot_fill(
                db,
                str(state.user_id),
                client_order_id=cid,
                side=side_raw,  # type: ignore[arg-type]
                quantity=delta,
                price=avg,
            )
            state = get_or_create_state(db, str(state.user_id))
    orig = _dec(payload.get("origQty"))
    still_open = status in _OPEN_ORDER_STATUSES
    if orig > 0 and executed >= orig:
        still_open = False
    if not still_open:
        state.rest_client_order_id = None
        state.rest_side = None
        state.rest_price = None
    return state


def set_switch(
    db: Session,
    user_id: str,
    *,
    enabled: bool,
    exchange: Optional[ExchangePort] = None,
    now: Optional[datetime] = None,
    free_btc: Optional[Decimal] = None,
) -> ScalpUserState:
    """User interruptor. Kill religar is this same switch. Missing Spot key cannot enable."""
    stamp = now or _utcnow()
    port = exchange or LiveExchange()
    state = get_or_create_state(db, user_id)
    cred = _credential(db, user_id)
    if enabled and cred is None:
        raise PermissionError("no_spot_key")
    if enabled:
        btc = free_btc
        if btc is None and cred is not None:
            try:
                _usdt, btc = port.free_balances(cred.api_key, cred.api_secret)
            except BinanceOrderError:
                btc = Decimal("0")
        state.enabled = True
        state.killed = False
        state.inventory_btc = Decimal("0")
        state.floor_btc = _dec(btc)
        state.avg_entry_quote = None
        state.inventory_clipped = False
        state.jev_in_flight = False
        state.day_started_at = stamp
        state.realized_pnl_quote = Decimal("0")
        state.fees_quote = Decimal("0")
        state.jev_cost_quote = Decimal("0")
        state.day_pnl_quote = Decimal("0")
        _cancel_resting(state, cred=cred, exchange=port, all_bot=True)
    else:
        state.enabled = False
        _cancel_resting(state, cred=cred, exchange=port, all_bot=True)
        state.jev_in_flight = False
    state.updated_at = stamp
    db.add(state)
    db.commit()
    db.refresh(state)
    return state


def apply_bot_fill(
    db: Session,
    user_id: str,
    *,
    client_order_id: str,
    side: Side,
    quantity: Decimal,
    price: Decimal,
    fee_quote: Decimal = Decimal("0"),
) -> None:
    """Book only this loop's fills. Operar / outside fills MUST NOT call this."""
    if not is_bot_client_order_id(client_order_id):
        return
    state = get_or_create_state(db, user_id)
    existing = (
        db.query(ScalpFill)
        .filter(
            ScalpFill.user_id == str(user_id),
            ScalpFill.client_order_id == client_order_id,
            ScalpFill.side == side,
            ScalpFill.quantity == quantity,
            ScalpFill.price == price,
        )
        .first()
    )
    if existing is not None:
        return
    _apply_fill(state, side=side, quantity=quantity, price=price, fee=fee_quote)
    db.add(
        ScalpFill(
            id=uuid.uuid4(),
            user_id=str(user_id),
            client_order_id=client_order_id,
            side=side,
            quantity=quantity,
            price=price,
            fee_quote=fee_quote,
            created_at=_utcnow(),
        )
    )
    state.updated_at = _utcnow()
    db.add(state)
    db.commit()
    invalidate_balance_cache(str(user_id))


def tick_user(
    db: Session,
    user_id: str,
    *,
    exchange: Optional[ExchangePort] = None,
    jev_fn: Optional[JevFn] = None,
    now: Optional[datetime] = None,
    book: Optional[Book] = None,
    free_usdt: Optional[Decimal] = None,
    free_btc: Optional[Decimal] = None,
) -> CycleResult:
    stamp = now or _utcnow()
    port = exchange or LiveExchange()
    state = get_or_create_state(db, user_id)
    cred = _credential(db, user_id)
    key_ok = cred is not None

    if free_usdt is None or free_btc is None:
        if cred is not None:
            try:
                live_usdt, live_btc = _cached_balances(str(user_id), port, cred)
            except BinanceOrderError:
                live_usdt, live_btc = Decimal("0"), Decimal("0")
        else:
            live_usdt, live_btc = Decimal("0"), Decimal("0")
        if free_usdt is None:
            free_usdt = live_usdt
        if free_btc is None:
            free_btc = live_btc

    memory = get_scalp_btcusdt_memory()
    book_from_memory = False
    if book is None:
        if not memory.book_available():
            _cancel_resting(state, cred=cred, exchange=port, all_bot=True)
            intent = CycleIntent(
                send=False, cancel_resting=True, fire_kill=False, skip_reason="no_book"
            )
            state.updated_at = stamp
            db.add(state)
            db.commit()
            return CycleResult(
                user_id=str(user_id), intent=intent, sent=False, killed=False, skipped="no_book"
            )
        memory.read_touch()
        memory.recent_trades()
        book = memory.read_book()
        book_from_memory = True
        if book is None:
            _cancel_resting(state, cred=cred, exchange=port, all_bot=True)
            intent = CycleIntent(
                send=False, cancel_resting=True, fire_kill=False, skip_reason="no_book"
            )
            state.updated_at = stamp
            db.add(state)
            db.commit()
            return CycleResult(
                user_id=str(user_id), intent=intent, sent=False, killed=False, skipped="no_book"
            )

    clipped = clip_inventory(
        bot_inventory=_dec(state.inventory_btc),
        free_btc=_dec(free_btc),
        floor_btc=_dec(state.floor_btc),
    )
    if clipped != _dec(state.inventory_btc):
        state.inventory_btc = clipped
        state.inventory_clipped = True
        if clipped <= 0:
            state.avg_entry_quote = None

    state = _sync_resting_order(db, state, cred=cred, exchange=port)

    day_pnl = _refresh_day_pnl(state, mid=book.mid)
    live_jev = bool(jev_api_key()) or jev_fn is not None or jev_available()
    # Stand-in MAY run (signal only). Live send requires TypeSafe key or injected jev_fn.
    live_send = bool(jev_api_key()) or jev_fn is not None
    if jev_fn is None and not jev_api_key() and not jev_available():
        live_jev = False

    elapsed = _elapsed_ms(state, stamp)
    if state.jev_in_flight and elapsed is not None and elapsed > max(JEV_FLOOR_MS * 5, 2000):
        state.jev_in_flight = False

    intent = decide_cycle(
        enabled=bool(state.enabled),
        killed=bool(state.killed),
        has_spot_key=key_ok,
        jev_available=live_jev,
        jev_in_flight=bool(state.jev_in_flight),
        last_jev_elapsed_ms=elapsed,
        inventory_btc=_dec(state.inventory_btc),
        floor_btc=_dec(state.floor_btc),
        free_usdt=_dec(free_usdt),
        free_btc=_dec(free_btc),
        day_pnl=day_pnl,
        book=book,
        resting=_resting(state),
        jev=None,
    )

    if intent.fire_kill:
        state.killed = True
        state.enabled = False
        _cancel_resting(state, cred=cred, exchange=port, all_bot=True)
        state.updated_at = stamp
        db.add(state)
        db.commit()
        return CycleResult(
            user_id=str(user_id), intent=intent, sent=False, killed=True, skipped="kill"
        )

    if intent.cancel_resting:
        _cancel_resting(state, cred=cred, exchange=port, all_bot=False)

    if not state.enabled or state.killed or not key_ok:
        if intent.skip_reason in {"switch_off", "halted"}:
            _cancel_resting(state, cred=cred, exchange=port, all_bot=True)
        state.updated_at = stamp
        db.add(state)
        db.commit()
        return CycleResult(
            user_id=str(user_id),
            intent=intent,
            sent=False,
            killed=bool(state.killed),
            skipped=intent.skip_reason,
        )

    if intent.skip_reason == "jev_unavailable" or not live_jev:
        state.updated_at = stamp
        db.add(state)
        db.commit()
        return CycleResult(
            user_id=str(user_id), intent=intent, sent=False, killed=False, skipped="jev_unavailable"
        )

    if intent.skip_reason in {"jev_in_flight", "jev_floor", "jev_target"}:
        state.updated_at = stamp
        db.add(state)
        db.commit()
        return CycleResult(
            user_id=str(user_id),
            intent=intent,
            sent=False,
            killed=False,
            skipped=intent.skip_reason,
        )

    caller = jev_fn or request_jev
    state.jev_in_flight = True
    db.add(state)
    db.commit()
    try:
        signal = caller(
            {
                "bid": str(book.bid),
                "ask": str(book.ask),
                "inventory_btc": str(state.inventory_btc),
                "t": str(compute_t(_dec(free_usdt))),
            }
        )
    finally:
        state.jev_in_flight = False
        state.last_jev_at = stamp
        state.last_jev_latency_ms = None

    state.last_jev_latency_ms = int(signal.latency_ms)
    state.jev_cost_quote = _dec(state.jev_cost_quote) + _dec(signal.cost_quote)
    state.calibration_signals = int(state.calibration_signals or 0) + 1

    enabled_now, killed_now = _live_switch_flags(db, str(user_id))
    state.enabled = enabled_now
    state.killed = killed_now
    if not enabled_now or killed_now:
        skip = "halted" if killed_now else "switch_off"
        _cancel_resting(state, cred=cred, exchange=port, all_bot=True)
        state.updated_at = stamp
        db.add(state)
        db.commit()
        return CycleResult(
            user_id=str(user_id),
            intent=intent,
            sent=False,
            killed=killed_now,
            skipped=skip,
        )

    intent = decide_cycle(
        enabled=enabled_now,
        killed=killed_now,
        has_spot_key=key_ok,
        jev_available=True,
        jev_in_flight=False,
        last_jev_elapsed_ms=max(JEV_TARGET_MS, int(signal.latency_ms)),
        inventory_btc=_dec(state.inventory_btc),
        floor_btc=_dec(state.floor_btc),
        free_usdt=_dec(free_usdt),
        free_btc=_dec(free_btc),
        day_pnl=_refresh_day_pnl(state, mid=book.mid),
        book=book,
        resting=_resting(state),
        jev=signal,
    )
    sent = False
    rest_open = bool(state.rest_client_order_id)
    if (
        intent.send
        and intent.side
        and intent.price is not None
        and intent.quantity is not None
        and cred is not None
        and live_send
        and not rest_open
    ):
        if book_from_memory:
            if not memory.book_available():
                _cancel_resting(state, cred=cred, exchange=port, all_bot=True)
                state.updated_at = stamp
                db.add(state)
                db.commit()
                return CycleResult(
                    user_id=str(user_id),
                    intent=intent,
                    sent=False,
                    killed=False,
                    skipped="no_book",
                )
            fresh_book = memory.read_book()
            if fresh_book is None:
                _cancel_resting(state, cred=cred, exchange=port, all_bot=True)
                state.updated_at = stamp
                db.add(state)
                db.commit()
                return CycleResult(
                    user_id=str(user_id),
                    intent=intent,
                    sent=False,
                    killed=False,
                    skipped="no_book",
                )
            book = fresh_book
        client_order_id = f"cfscalp_{uuid.uuid4().hex[:16]}"
        try:
            result = port.place_post_only(
                api_key=cred.api_key,
                api_secret=cred.api_secret,
                side=intent.side,
                price=intent.price,
                quantity=intent.quantity,
                client_order_id=client_order_id,
            )
        except BinanceOrderError as exc:
            if exc.code in CROSS_REJECT_CODES:
                logger.info(
                    "scalp cross-reject user=%s code=%s — wait next cycle", state.user_id, exc.code
                )
            else:
                logger.warning("scalp post failed user=%s code=%s", state.user_id, exc.code)
            result = None
        if result is not None:
            sent = True
            state.calibration_hits = int(state.calibration_hits or 0) + 1
            status = str(result.get("status") or "").upper()
            executed = _dec(result.get("executedQty"))
            if executed > 0:
                avg = (
                    _dec(result.get("cummulativeQuoteQty")) / executed if executed else intent.price
                )
                fee = Decimal("0")
                apply_side: Side = intent.side
                _apply_fill(
                    state, side=apply_side, quantity=executed, price=avg or intent.price, fee=fee
                )
                db.add(
                    ScalpFill(
                        id=uuid.uuid4(),
                        user_id=str(user_id),
                        client_order_id=client_order_id,
                        side=apply_side,
                        quantity=executed,
                        price=avg or intent.price,
                        fee_quote=fee,
                        created_at=stamp,
                    )
                )
            if status in {"NEW", "PARTIALLY_FILLED"} and executed < _dec(intent.quantity):
                state.rest_client_order_id = client_order_id
                state.rest_side = intent.side
                state.rest_price = intent.price
            else:
                state.rest_client_order_id = None
                state.rest_side = None
                state.rest_price = None
    elif intent.cancel_resting:
        _cancel_resting(state, cred=cred, exchange=port, all_bot=False)

    _refresh_day_pnl(state, mid=book.mid)
    if intent.fire_kill:
        state.killed = True
        state.enabled = False
        _cancel_resting(state, cred=cred, exchange=port, all_bot=True)

    state.updated_at = stamp
    db.add(state)
    db.commit()
    if sent:
        invalidate_balance_cache(str(user_id))
    return CycleResult(
        user_id=str(user_id),
        intent=intent,
        sent=sent,
        killed=bool(state.killed),
        skipped=None if sent else intent.skip_reason,
    )


def list_enabled_user_ids(db: Session) -> list[str]:
    rows = (
        db.query(ScalpUserState.user_id)
        .filter(ScalpUserState.enabled.is_(True), ScalpUserState.killed.is_(False))
        .all()
    )
    return [str(row[0]) for row in rows]


def status_payload(
    db: Session,
    user_id: str,
    *,
    free_usdt: Optional[Decimal] = None,
    free_btc: Optional[Decimal] = None,
    mid: Optional[Decimal] = None,
) -> dict[str, Any]:
    state = db.query(ScalpUserState).filter(ScalpUserState.user_id == str(user_id)).first()
    key_ok = has_spot_key(db, user_id)
    enabled = bool(state.enabled) if state is not None else False
    killed = bool(state.killed) if state is not None else False
    visual = panel_state(has_spot_key=key_ok, enabled=enabled, killed=killed)
    inventory = _dec(state.inventory_btc) if state is not None else Decimal("0")
    t = compute_t(
        _dec(free_usdt) if free_usdt is not None else Decimal("100") if key_ok else Decimal("0")
    )
    if free_usdt is not None:
        t = compute_t(_dec(free_usdt))
    elif not key_ok:
        t = Decimal("0")
    else:
        t = compute_t(Decimal("100"))
        cred = _credential(db, user_id)
        if cred is not None:
            try:
                port = LiveExchange()
                live_usdt, live_btc = _cached_balances(str(user_id), port, cred)
                t = compute_t(live_usdt)
                if free_btc is None:
                    free_btc = live_btc
                if enabled and not killed:
                    live_book = get_scalp_btcusdt_memory().read_book()
                    if live_book is not None:
                        mid = mid or live_book.mid
            except Exception:
                pass
    mark = mid or Decimal("0")
    unrealized = Decimal("0")
    fees = _dec(state.fees_quote) if state is not None else Decimal("0")
    jev_cost = _dec(state.jev_cost_quote) if state is not None else Decimal("0")
    realized = _dec(state.realized_pnl_quote) if state is not None else Decimal("0")
    if state is not None:
        if free_btc is not None:
            clipped = clip_inventory(
                bot_inventory=inventory,
                free_btc=_dec(free_btc),
                floor_btc=_dec(state.floor_btc),
            )
            if clipped != inventory:
                inventory = clipped
        unrealized = unrealized_pnl(
            inventory_btc=inventory,
            avg_entry=_dec(state.avg_entry_quote) if state.avg_entry_quote is not None else None,
            mid=mark,
        )
    pnl = pnl_quote(realized=realized, unrealized=unrealized, fees=fees, jev_cost=jev_cost)
    cal = None
    if state is not None and int(state.calibration_signals or 0) > 0:
        latency_s = None
        if state.last_jev_latency_ms is not None:
            latency_s = max(1, int(round(int(state.last_jev_latency_ms) / 1000))) or 1
        cal = {
            "hits": int(state.calibration_hits or 0),
            "signals": int(state.calibration_signals or 0),
            "last_latency_s": latency_s,
        }
    jev_live = bool(jev_api_key())
    memory = get_scalp_btcusdt_memory()
    local_age = memory.age_ms()
    book_available = True
    book_age_ms: int | None = None
    if visual == "on":
        book_available, book_age_ms = resolve_scalp_btcusdt_freshness(
            local_connected=memory.stream_connected(),
            local_age_ms=local_age,
            local_book_available=memory.book_available(),
        )
    status_text = STATUS_COPY[visual]
    if visual == "on" and not book_available:
        status_text = BOOK_UNAVAILABLE_COPY
    elif visual == "on" and not jev_live:
        status_text = "Jev indisponível — sem envio live"
    if visual == "on" and mark <= 0:
        live_book = resolve_scalp_btcusdt_book(
            local_connected=memory.stream_connected(),
            local_age_ms=local_age,
            local_book=memory.read_book(),
        )
        if live_book is not None:
            mark = live_book.mid
    return {
        "symbol": SYMBOL,
        "state": visual,
        "has_spot_key": key_ok,
        "jev_available": jev_live,
        "jev_unavailable": visual == "on" and not jev_live,
        "book_available": book_available,
        "book_age_ms": book_age_ms if visual == "on" else memory.age_ms(),
        "t_quote": str(t),
        "clip_quote": "10",
        "inventory_btc": str(inventory),
        "calibration": cal,
        "pnl_quote": str(pnl),
        "status_text": status_text,
        "kill_banner": visual == "kill",
        "inventory_clipped": bool(state.inventory_clipped) if state is not None else False,
        "enabled": enabled and not killed and key_ok,
    }
