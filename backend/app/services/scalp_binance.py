"""Binance Spot helpers for the directional scalp. Post-only LIMIT/GTX only."""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional

from app.services.binance_spot_orders import (
    BinanceOrderError,
    decimal_floor,
    fetch_free_balance,
    format_decimal,
    get_symbol_info,
    list_open_orders,
    public_get,
    signed_request,
)
from app.services.scalp_engine import (
    AGGRESSIVE_ORDER_TYPE,
    CLIENT_ORDER_PREFIX,
    ORDER_TYPE,
    SYMBOL,
    TIME_IN_FORCE,
    Book,
    Side,
    is_bot_client_order_id,
)

ACCOUNT_PATH = "/api/v3/account"
BNB_BURN_PATH = "/sapi/v1/bnbBurn"
_BP_PER_RATE = Decimal("10000")


def fetch_maker_fee_bp(
    *,
    api_key: str,
    api_secret: str,
    base_url: Optional[str] = None,
) -> Decimal:
    """Real maker commission of the account, in basis points **per leg**.

    ``commissionRates.maker`` already reflects the account's effective rate
    (VIP tier and BNB discount when active).
    """
    payload = signed_request(
        method="GET",
        path=ACCOUNT_PATH,
        api_key=api_key,
        api_secret=api_secret,
        base_url=base_url,
    )
    rates = payload.get("commissionRates") if isinstance(payload, dict) else None
    maker = (rates or {}).get("maker") if isinstance(rates, dict) else None
    if maker is None:
        raise BinanceOrderError("commissionRates.maker ausente")
    fee_bp = Decimal(str(maker)) * _BP_PER_RATE
    if fee_bp <= 0:
        raise BinanceOrderError("commissionRates.maker inválido")
    return fee_bp


def fetch_spot_bnb_burn(
    *,
    api_key: str,
    api_secret: str,
    base_url: Optional[str] = None,
) -> bool:
    """Whether the account pays Spot fees with BNB (``spotBNBBurn``)."""
    payload = signed_request(
        method="GET",
        path=BNB_BURN_PATH,
        api_key=api_key,
        api_secret=api_secret,
        base_url=base_url,
    )
    return bool((payload or {}).get("spotBNBBurn")) if isinstance(payload, dict) else False


def fetch_book(*, base_url: Optional[str] = None) -> Book:
    payload = public_get("/api/v3/ticker/bookTicker", {"symbol": SYMBOL}, base_url=base_url)
    bid = Decimal(str(payload.get("bidPrice") or "0"))
    ask = Decimal(str(payload.get("askPrice") or "0"))
    if bid <= 0 or ask <= 0:
        raise BinanceOrderError("Livro BTCUSDT indisponível")
    return Book(bid=bid, ask=ask)


def fetch_free_usdt_btc(
    *,
    api_key: str,
    api_secret: str,
    base_url: Optional[str] = None,
) -> tuple[Decimal, Decimal]:
    usdt = fetch_free_balance(
        api_key=api_key, api_secret=api_secret, asset="USDT", base_url=base_url
    )
    btc = fetch_free_balance(api_key=api_key, api_secret=api_secret, asset="BTC", base_url=base_url)
    return usdt, btc


def list_bot_open_orders(
    *,
    api_key: str,
    api_secret: str,
    base_url: Optional[str] = None,
) -> list[dict[str, Any]]:
    orders = list_open_orders(
        api_key=api_key, api_secret=api_secret, symbol=SYMBOL, base_url=base_url
    )
    return [row for row in orders if is_bot_client_order_id(str(row.get("clientOrderId") or ""))]


def cancel_bot_order(
    *,
    api_key: str,
    api_secret: str,
    client_order_id: str,
    base_url: Optional[str] = None,
) -> None:
    if not is_bot_client_order_id(client_order_id):
        return
    signed_request(
        method="DELETE",
        path="/api/v3/order",
        api_key=api_key,
        api_secret=api_secret,
        params={"symbol": SYMBOL, "origClientOrderId": client_order_id},
        base_url=base_url,
    )


def cancel_all_bot_orders(
    *,
    api_key: str,
    api_secret: str,
    base_url: Optional[str] = None,
) -> int:
    cancelled = 0
    for row in list_bot_open_orders(api_key=api_key, api_secret=api_secret, base_url=base_url):
        cid = str(row.get("clientOrderId") or "")
        if not cid:
            continue
        try:
            cancel_bot_order(
                api_key=api_key,
                api_secret=api_secret,
                client_order_id=cid,
                base_url=base_url,
            )
            cancelled += 1
        except BinanceOrderError:
            continue
    return cancelled


def place_post_only(
    *,
    api_key: str,
    api_secret: str,
    side: Side,
    price: Decimal,
    quantity: Decimal,
    client_order_id: str,
    base_url: Optional[str] = None,
) -> dict[str, Any]:
    if not is_bot_client_order_id(client_order_id):
        raise BinanceOrderError("clientOrderId deste scalp inválido")
    info = get_symbol_info(SYMBOL, base_url=base_url)
    filters = {str(item.get("filterType") or ""): item for item in (info.get("filters") or [])}
    tick = Decimal(str((filters.get("PRICE_FILTER") or {}).get("tickSize") or "0.01"))
    step = Decimal(str((filters.get("LOT_SIZE") or {}).get("stepSize") or "0.00001"))
    min_qty = Decimal(str((filters.get("LOT_SIZE") or {}).get("minQty") or "0"))
    min_notional = Decimal(
        str(
            (filters.get("MIN_NOTIONAL") or {}).get("minNotional")
            or (filters.get("NOTIONAL") or {}).get("minNotional")
            or "0"
        )
    )
    px = decimal_floor(price, tick)
    qty = decimal_floor(quantity, step)
    if qty < min_qty or qty <= 0 or px <= 0:
        raise BinanceOrderError("Quantidade abaixo do filtro da Binance")
    if min_notional > 0 and (qty * px) < min_notional:
        raise BinanceOrderError("Notional abaixo do filtro da Binance")
    return signed_request(
        method="POST",
        path="/api/v3/order",
        api_key=api_key,
        api_secret=api_secret,
        params={
            "symbol": SYMBOL,
            "side": side,
            "type": ORDER_TYPE,
            "timeInForce": TIME_IN_FORCE,
            "quantity": format_decimal(qty),
            "price": format_decimal(px),
            "newClientOrderId": client_order_id,
        },
        base_url=base_url,
    )


def place_aggressive_exit(
    *,
    api_key: str,
    api_secret: str,
    quantity: Decimal,
    client_order_id: str,
    reference_price: Decimal,
    side: Side = "SELL",
    base_url: Optional[str] = None,
) -> dict[str, Any]:
    """Aggressive exit: MARKET with **no price ceiling** and no slippage guard.

    The escape exists to close a position the passive target/stop did not
    close; a price cap or guard would leave the position stuck again. MARKET
    carries no price and no ``timeInForce`` on Spot.

    ``reference_price`` is **only** the reference for the symbol's
    NOTIONAL/MIN_NOTIONAL filter — the same one ``place_post_only`` validates.
    A MARKET order carries no price of its own, so without a reference the
    notional filter cannot be checked and Binance would reject the escape
    exactly when it is needed. It never enters the order.
    """
    if not is_bot_client_order_id(client_order_id):
        raise BinanceOrderError("clientOrderId deste scalp inválido")
    info = get_symbol_info(SYMBOL, base_url=base_url)
    filters = {str(item.get("filterType") or ""): item for item in (info.get("filters") or [])}
    step = Decimal(str((filters.get("LOT_SIZE") or {}).get("stepSize") or "0.00001"))
    min_qty = Decimal(str((filters.get("LOT_SIZE") or {}).get("minQty") or "0"))
    min_notional = Decimal(
        str(
            (filters.get("MIN_NOTIONAL") or {}).get("minNotional")
            or (filters.get("NOTIONAL") or {}).get("minNotional")
            or "0"
        )
    )
    qty = decimal_floor(quantity, step)
    if qty < min_qty or qty <= 0:
        raise BinanceOrderError("Quantidade abaixo do filtro da Binance")
    if min_notional > 0 and (qty * reference_price) < min_notional:
        raise BinanceOrderError("Notional abaixo do filtro da Binance")
    return signed_request(
        method="POST",
        path="/api/v3/order",
        api_key=api_key,
        api_secret=api_secret,
        params={
            "symbol": SYMBOL,
            "side": side,
            "type": AGGRESSIVE_ORDER_TYPE,
            "quantity": format_decimal(qty),
            "newClientOrderId": client_order_id,
        },
        base_url=base_url,
    )


def query_order(
    *,
    api_key: str,
    api_secret: str,
    client_order_id: str,
    base_url: Optional[str] = None,
) -> dict[str, Any]:
    payload = signed_request(
        method="GET",
        path="/api/v3/order",
        api_key=api_key,
        api_secret=api_secret,
        params={"symbol": SYMBOL, "origClientOrderId": client_order_id},
        base_url=base_url,
    )
    return payload if isinstance(payload, dict) else {}


# Prefix is part of the public contract so tests can assert we never cancel Operar ids.
assert CLIENT_ORDER_PREFIX == "cfscalp_"
