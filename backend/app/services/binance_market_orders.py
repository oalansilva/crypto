from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, Iterable, Optional

from app.services.binance_spot_orders import (
    BinanceOrderError,
    _filter_map,
    decimal_floor,
    format_decimal,
    get_symbol_info,
    normalize_symbol,
    public_get,
    signed_request,
)

TERMINAL_BINANCE_STATUSES = frozenset(
    {"FILLED", "CANCELED", "REJECTED", "EXPIRED", "EXPIRED_IN_MATCH"}
)


def _validation_error(message: str, *, status_code: int = 400) -> BinanceOrderError:
    return BinanceOrderError(message, status_code=status_code, safe_for_user=True)


@dataclass(frozen=True)
class MarketOrderPlan:
    symbol: str
    side: str
    base_asset: str
    quote_asset: str
    account_identity_hash: str
    indicative_price: Decimal
    quote_balance: Decimal
    base_balance: Decimal
    quote_amount: Optional[Decimal]
    base_quantity: Optional[Decimal]
    estimated_base_quantity: Optional[Decimal]
    estimated_quote_amount: Optional[Decimal]
    residual_quantity: Decimal


def _account_identity_hash(account: Dict[str, Any], *, api_key: str) -> str:
    account_uid = str(account.get("uid") or "").strip()
    identity = f"uid:{account_uid}" if account_uid else f"api-key:{api_key}"
    return hashlib.sha256(f"binance-account:{identity}".encode()).hexdigest()


def get_binance_account_identity_hash(*, api_key: str, api_secret: str) -> str:
    account = signed_request(
        method="GET",
        path="/api/v3/account",
        api_key=api_key,
        api_secret=api_secret,
    )
    return _account_identity_hash(account, api_key=api_key)


def _positive_decimal(value: Any, label: str) -> Decimal:
    try:
        parsed = Decimal(str(value))
    except Exception as exc:
        raise _validation_error(f"{label} inválido") from exc
    if not parsed.is_finite() or parsed <= 0:
        raise _validation_error(f"{label} deve ser maior que zero")
    return parsed


def _balance_map(account: Dict[str, Any]) -> Dict[str, Decimal]:
    balances: Dict[str, Decimal] = {}
    for row in account.get("balances") or []:
        asset = str(row.get("asset") or "").upper()
        if not asset:
            continue
        try:
            value = Decimal(str(row.get("free") or "0"))
        except Exception:
            value = Decimal("0")
        balances[asset] = value if value.is_finite() and value > 0 else Decimal("0")
    return balances


def _filter_decimal(filter_row: Dict[str, Any], key: str) -> Decimal:
    try:
        value = Decimal(str(filter_row.get(key) or "0"))
    except Exception as exc:
        raise _validation_error("Filtros de quantidade inválidos na Binance") from exc
    return value if value.is_finite() and value > 0 else Decimal("0")


def _market_quantity_limits(
    filters: Dict[str, Dict[str, Any]],
) -> tuple[Decimal, Decimal, Decimal]:
    market = filters.get("MARKET_LOT_SIZE") or {}
    lot = filters.get("LOT_SIZE") or {}

    def active_value(key: str) -> Decimal:
        market_value = _filter_decimal(market, key)
        return market_value if market_value > 0 else _filter_decimal(lot, key)

    return active_value("stepSize"), active_value("minQty"), active_value("maxQty")


def _validate_market_quantity(
    quantity: Decimal,
    *,
    min_qty: Decimal,
    max_qty: Decimal,
) -> None:
    if quantity <= 0 or (min_qty > 0 and quantity < min_qty):
        raise _validation_error("Quantidade abaixo do mínimo permitido pela Binance")
    if max_qty > 0 and quantity > max_qty:
        raise _validation_error("Quantidade acima do máximo permitido pela Binance")


def _validate_notional(
    *,
    notional: Decimal,
    filters: Dict[str, Dict[str, Any]],
) -> None:
    minimum = filters.get("MIN_NOTIONAL") or {}
    if bool(minimum.get("applyToMarket")):
        min_value = Decimal(str(minimum.get("minNotional") or "0"))
        if min_value > 0 and notional < min_value:
            raise _validation_error("Valor abaixo do mínimo permitido pela Binance")

    bounded = filters.get("NOTIONAL") or {}
    min_value = Decimal(str(bounded.get("minNotional") or "0"))
    max_value = Decimal(str(bounded.get("maxNotional") or "0"))
    if bool(bounded.get("applyMinToMarket")) and min_value > 0 and notional < min_value:
        raise _validation_error("Valor abaixo do mínimo permitido pela Binance")
    if bool(bounded.get("applyMaxToMarket")) and max_value > 0 and notional > max_value:
        raise _validation_error("Valor acima do máximo permitido pela Binance")


def _requires_average_notional_price(filters: Dict[str, Dict[str, Any]]) -> bool:
    minimum = filters.get("MIN_NOTIONAL") or {}
    bounded = filters.get("NOTIONAL") or {}
    candidates = (
        (bool(minimum.get("applyToMarket")), minimum.get("avgPriceMins")),
        (
            bool(bounded.get("applyMinToMarket")) or bool(bounded.get("applyMaxToMarket")),
            bounded.get("avgPriceMins"),
        ),
    )
    for applies_to_market, raw_minutes in candidates:
        try:
            if applies_to_market and int(raw_minutes or 0) > 0:
                return True
        except (TypeError, ValueError):
            raise _validation_error("Filtro de notional inválido na Binance")
    return False


def _market_notional_reference_price(
    *,
    symbol: str,
    filters: Dict[str, Dict[str, Any]],
    indicative_price: Decimal,
    base_url: Optional[str],
) -> Decimal:
    if not _requires_average_notional_price(filters):
        return indicative_price
    payload = public_get("/api/v3/avgPrice", {"symbol": symbol}, base_url=base_url)
    return _positive_decimal(payload.get("price"), "Preço médio para validação")


def _validate_symbol_info(symbol_info: Dict[str, Any], *, side: str) -> tuple[str, str]:
    if str(symbol_info.get("status") or "").upper() != "TRADING":
        raise _validation_error("Ativo indisponível para negociação Spot")
    if symbol_info.get("isSpotTradingAllowed") is not True:
        raise _validation_error("Ativo sem negociação Spot habilitada")
    order_types = {str(value).upper() for value in symbol_info.get("orderTypes") or []}
    if "MARKET" not in order_types:
        raise _validation_error("Ativo não aceita ordem MARKET")
    base = str(symbol_info.get("baseAsset") or "").upper()
    quote = str(symbol_info.get("quoteAsset") or "").upper()
    if not base or quote != "USDT":
        raise _validation_error("Operação direta disponível apenas para pares cotados em USDT")
    if side == "BUY" and symbol_info.get("quoteOrderQtyMarketAllowed") is not True:
        raise _validation_error("Ativo não aceita compra MARKET por valor em USDT")
    return base, quote


def build_market_order_plan(
    *,
    api_key: str,
    api_secret: str,
    symbol: str,
    side: str,
    quote_amount: Optional[Decimal] = None,
    base_url: Optional[str] = None,
) -> MarketOrderPlan:
    sym = normalize_symbol(symbol)
    normalized_side = str(side or "").upper()
    if normalized_side not in {"BUY", "SELL"}:
        raise _validation_error("Lado da ordem inválido")

    symbol_info = get_symbol_info(sym, base_url=base_url)
    base_asset, quote_asset = _validate_symbol_info(symbol_info, side=normalized_side)
    price_payload = public_get("/api/v3/ticker/price", {"symbol": sym}, base_url=base_url)
    price = _positive_decimal(price_payload.get("price"), "Preço indicativo")
    account = signed_request(
        method="GET",
        path="/api/v3/account",
        api_key=api_key,
        api_secret=api_secret,
        base_url=base_url,
    )
    if account.get("canTrade") is not True:
        raise _validation_error(
            "Chave Binance sem permissão de Spot Trading. Revise a conexão em Meu Perfil.",
            status_code=403,
        )
    balances = _balance_map(account)
    quote_balance = balances.get(quote_asset, Decimal("0"))
    base_balance = balances.get(base_asset, Decimal("0"))
    filters = _filter_map(symbol_info)
    step, min_qty, max_qty = _market_quantity_limits(filters)

    if normalized_side == "BUY":
        requested_quote = _positive_decimal(quote_amount, "Valor em USDT")
        if requested_quote > quote_balance:
            raise _validation_error("Saldo livre em USDT insuficiente")
        _validate_notional(notional=requested_quote, filters=filters)
        estimated_base_quantity = requested_quote / price
        _validate_market_quantity(
            estimated_base_quantity,
            min_qty=min_qty,
            max_qty=max_qty,
        )
        return MarketOrderPlan(
            symbol=sym,
            side=normalized_side,
            base_asset=base_asset,
            quote_asset=quote_asset,
            account_identity_hash=_account_identity_hash(account, api_key=api_key),
            indicative_price=price,
            quote_balance=quote_balance,
            base_balance=base_balance,
            quote_amount=requested_quote,
            base_quantity=None,
            estimated_base_quantity=estimated_base_quantity,
            estimated_quote_amount=None,
            residual_quantity=Decimal("0"),
        )

    quantity = decimal_floor(base_balance, step)
    _validate_market_quantity(quantity, min_qty=min_qty, max_qty=max_qty)
    notional_reference_price = _market_notional_reference_price(
        symbol=sym,
        filters=filters,
        indicative_price=price,
        base_url=base_url,
    )
    _validate_notional(notional=quantity * notional_reference_price, filters=filters)
    estimated_quote_amount = quantity * price
    return MarketOrderPlan(
        symbol=sym,
        side=normalized_side,
        base_asset=base_asset,
        quote_asset=quote_asset,
        account_identity_hash=_account_identity_hash(account, api_key=api_key),
        indicative_price=price,
        quote_balance=quote_balance,
        base_balance=base_balance,
        quote_amount=None,
        base_quantity=quantity,
        estimated_base_quantity=None,
        estimated_quote_amount=estimated_quote_amount,
        residual_quantity=max(Decimal("0"), base_balance - quantity),
    )


def _exchange_info_by_symbol(symbols: list[str]) -> Dict[str, Dict[str, Any]]:
    if not symbols:
        return {}
    try:
        exchange_info = public_get(
            "/api/v3/exchangeInfo",
            {"symbols": json.dumps(symbols, separators=(",", ":"))},
        )
    except BinanceOrderError as exc:
        if exc.code != -1121:
            raise
        if len(symbols) == 1:
            return {}
        midpoint = len(symbols) // 2
        return {
            **_exchange_info_by_symbol(symbols[:midpoint]),
            **_exchange_info_by_symbol(symbols[midpoint:]),
        }
    return {
        str(item.get("symbol") or "").upper(): item
        for item in exchange_info.get("symbols") or []
    }


def get_market_order_eligibility(symbols: Iterable[str]) -> list[Dict[str, Any]]:
    normalized_symbols: list[str] = []
    for symbol in symbols:
        normalized = normalize_symbol(symbol)
        if normalized not in normalized_symbols:
            normalized_symbols.append(normalized)

    available = _exchange_info_by_symbol(normalized_symbols)
    results: list[Dict[str, Any]] = []
    for symbol in normalized_symbols:
        symbol_info = available.get(symbol)
        if symbol_info is None:
            results.append(
                {
                    "symbol": symbol,
                    "eligible": False,
                    "reason": "Par não encontrado na Binance Spot.",
                }
            )
            continue
        try:
            _validate_symbol_info(symbol_info, side="BUY")
        except BinanceOrderError:
            try:
                _validate_symbol_info(symbol_info, side="SELL")
            except BinanceOrderError as exc:
                results.append({"symbol": symbol, "eligible": False, "reason": str(exc)})
            else:
                results.append({"symbol": symbol, "eligible": True, "reason": None})
        else:
            results.append({"symbol": symbol, "eligible": True, "reason": None})
    return results


def submit_market_order(
    *,
    api_key: str,
    api_secret: str,
    plan: MarketOrderPlan,
    client_order_id: str,
    base_url: Optional[str] = None,
) -> Dict[str, Any]:
    params: Dict[str, Any] = {
        "symbol": plan.symbol,
        "side": plan.side,
        "type": "MARKET",
        "newClientOrderId": client_order_id,
        "newOrderRespType": "FULL",
    }
    if plan.side == "BUY":
        if plan.quote_amount is None:
            raise _validation_error("Preview de compra sem valor em USDT")
        params["quoteOrderQty"] = format_decimal(plan.quote_amount)
    else:
        if plan.base_quantity is None:
            raise _validation_error("Preview de venda sem quantidade válida")
        params["quantity"] = format_decimal(plan.base_quantity)
    return signed_request(
        method="POST",
        path="/api/v3/order",
        api_key=api_key,
        api_secret=api_secret,
        params=params,
        base_url=base_url,
    )


def query_market_order(
    *,
    api_key: str,
    api_secret: str,
    symbol: str,
    client_order_id: str,
    base_url: Optional[str] = None,
) -> Dict[str, Any]:
    return signed_request(
        method="GET",
        path="/api/v3/order",
        api_key=api_key,
        api_secret=api_secret,
        params={
            "symbol": normalize_symbol(symbol),
            "origClientOrderId": client_order_id,
        },
        base_url=base_url,
    )


def _aggregate_fees(fills: Iterable[Dict[str, Any]]) -> list[Dict[str, str]]:
    fees: Dict[str, Decimal] = {}
    for fill in fills:
        asset = str(fill.get("commissionAsset") or "").upper()
        if not asset:
            continue
        try:
            commission = Decimal(str(fill.get("commission") or "0"))
        except Exception:
            continue
        if commission > 0:
            fees[asset] = fees.get(asset, Decimal("0")) + commission
    return [
        {"asset": asset, "amount": format_decimal(amount)} for asset, amount in sorted(fees.items())
    ]


def normalize_market_order_result(payload: Dict[str, Any]) -> Dict[str, Any]:
    status = str(payload.get("status") or "").upper()
    base_qty = Decimal(str(payload.get("executedQty") or "0"))
    quote_qty = Decimal(str(payload.get("cummulativeQuoteQty") or "0"))
    average_price = quote_qty / base_qty if base_qty > 0 else Decimal("0")
    if status == "FILLED":
        state = "filled"
    elif base_qty > 0 and status in TERMINAL_BINANCE_STATUSES:
        state = "partial"
    elif status in TERMINAL_BINANCE_STATUSES:
        state = "rejected"
    else:
        state = "reconciling"
    return {
        "state": state,
        "external_order_id": str(payload.get("orderId") or "") or None,
        "executed_base_quantity": format_decimal(base_qty),
        "executed_quote_amount": format_decimal(quote_qty),
        "average_price": format_decimal(average_price),
        "fees": _aggregate_fees(payload.get("fills") or []),
        "binance_status": status or "UNKNOWN",
    }
