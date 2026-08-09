from __future__ import annotations

import hashlib
import hmac
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from decimal import Decimal, ROUND_DOWN
from typing import Any, Dict, Optional, Tuple

from app.config import get_settings

get_settings()

CLIENT_ORDER_PREFIX = "cfstop_"
LIMIT_OFFSET_RATIO = Decimal("0.001")


class BinanceOrderError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        status_code: int = 400,
        code: Optional[int] = None,
        outcome_unknown: bool = False,
        safe_for_user: bool = False,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.outcome_unknown = outcome_unknown
        self.safe_for_user = safe_for_user


def _env_base_url() -> str:
    import os

    return (os.getenv("BINANCE_BASE_URL") or "https://api.binance.com").strip()


def _timeout_s() -> int:
    import os

    raw = (os.getenv("BINANCE_HTTP_TIMEOUT_SECONDS") or "10").strip()
    try:
        return max(1, min(60, int(raw)))
    except Exception:
        return 10


def signed_request(
    *,
    method: str,
    path: str,
    api_key: str,
    api_secret: str,
    params: Optional[Dict[str, Any]] = None,
    base_url: Optional[str] = None,
    timeout_s: Optional[int] = None,
) -> Any:
    base = (base_url or _env_base_url()).rstrip("/")
    payload = dict(params or {})
    payload["timestamp"] = int(time.time() * 1000)
    query = urllib.parse.urlencode(payload, doseq=True)
    signature = hmac.new(api_secret.encode(), query.encode(), hashlib.sha256).hexdigest()
    url = f"{base}{path}?{query}&signature={signature}"
    req = urllib.request.Request(url, method=method.upper())
    req.add_header("X-MBX-APIKEY", api_key)
    try:
        with urllib.request.urlopen(req, timeout=float(timeout_s or _timeout_s())) as resp:
            body = resp.read().decode("utf-8")
            if not body:
                return {}
            return json.loads(body)
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        code = None
        message = "A Binance recusou a solicitação."
        try:
            parsed = json.loads(raw)
            code = parsed.get("code")
            message = str(parsed.get("msg") or message)
        except Exception:
            pass
        is_order_submit = method.upper() == "POST" and path == "/api/v3/order"
        # 429/418 (rate limit) are enforced before order processing by Binance, so a
        # rejected submit here is a definitive non-execution, not an unknown outcome.
        outcome_unknown = is_order_submit and (
            int(exc.code or 0) >= 500 or int(exc.code or 0) == 408 or code in {-1006, -1007}
        )
        status = 403 if code in (-2014, -2015, -1022) else (502 if outcome_unknown else 400)
        if code in (-2014, -2015):
            message = (
                "Chave Binance sem permissão de Spot Trading ou inválida. "
                "Atualize a chave em Meu Perfil com Spot Trading habilitado (sem withdraw)."
            )
        raise BinanceOrderError(
            message,
            status_code=status,
            code=code,
            outcome_unknown=outcome_unknown,
            safe_for_user=code in (-2014, -2015),
        ) from exc
    except Exception as exc:
        is_order_submit = method.upper() == "POST" and path == "/api/v3/order"
        raise BinanceOrderError(
            "Falha ao falar com a Binance.",
            status_code=502,
            outcome_unknown=is_order_submit,
        ) from exc


def public_get(
    path: str, params: Optional[Dict[str, Any]] = None, *, base_url: Optional[str] = None
) -> Any:
    base = (base_url or _env_base_url()).rstrip("/")
    query = urllib.parse.urlencode(params or {}, doseq=True)
    url = f"{base}{path}" + (f"?{query}" if query else "")
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=float(_timeout_s())) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        code = None
        message = "A Binance recusou a consulta pública."
        try:
            parsed = json.loads(raw)
            code = parsed.get("code")
            message = str(parsed.get("msg") or message)
        except Exception:
            pass
        status = 502 if int(exc.code or 0) >= 500 or int(exc.code or 0) == 429 else 400
        raise BinanceOrderError(message, status_code=status, code=code) from exc
    except Exception as exc:
        raise BinanceOrderError(f"Falha ao consultar exchangeInfo: {exc}", status_code=502) from exc


def normalize_symbol(symbol: str) -> str:
    value = re.sub(r"[^A-Za-z0-9]", "", str(symbol or "")).upper()
    if not value:
        raise BinanceOrderError("Símbolo inválido")
    return value


def split_base_quote(symbol: str, exchange_info: Dict[str, Any]) -> Tuple[str, str]:
    sym = normalize_symbol(symbol)
    for item in exchange_info.get("symbols") or []:
        if str(item.get("symbol") or "").upper() == sym:
            base = str(item.get("baseAsset") or "").upper()
            quote = str(item.get("quoteAsset") or "").upper()
            if base and quote:
                return base, quote
    # Fallback common quotes
    for quote in ("USDT", "USDC", "BUSD", "BTC", "ETH"):
        if sym.endswith(quote) and len(sym) > len(quote):
            return sym[: -len(quote)], quote
    raise BinanceOrderError(f"Não foi possível identificar base/quote de {sym}")


def _filter_map(symbol_info: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for item in symbol_info.get("filters") or []:
        ftype = str(item.get("filterType") or "")
        if ftype:
            out[ftype] = item
    return out


def get_symbol_info(symbol: str, *, base_url: Optional[str] = None) -> Dict[str, Any]:
    sym = normalize_symbol(symbol)
    info = public_get("/api/v3/exchangeInfo", {"symbol": sym}, base_url=base_url)
    symbols = info.get("symbols") or []
    if not symbols:
        raise BinanceOrderError(f"Símbolo {sym} não encontrado na Binance Spot")
    return symbols[0]


def decimal_floor(value: Decimal, step: Decimal) -> Decimal:
    if step <= 0:
        return value
    units = (value / step).to_integral_value(rounding=ROUND_DOWN)
    return units * step


def format_decimal(value: Decimal) -> str:
    text = format(value.normalize(), "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def build_client_order_id(*, user_id: str, symbol: str, opportunity_id: str) -> str:
    raw = f"{user_id}:{normalize_symbol(symbol)}:{opportunity_id}"
    digest = hashlib.sha1(raw.encode()).hexdigest()[:16]
    # Binance clientOrderId max length 36
    return f"{CLIENT_ORDER_PREFIX}{digest}"


def fetch_free_balance(
    *,
    api_key: str,
    api_secret: str,
    asset: str,
    base_url: Optional[str] = None,
) -> Decimal:
    account = signed_request(
        method="GET",
        path="/api/v3/account",
        api_key=api_key,
        api_secret=api_secret,
        base_url=base_url,
    )
    target = str(asset or "").upper()
    for row in account.get("balances") or []:
        if str(row.get("asset") or "").upper() == target:
            return Decimal(str(row.get("free") or "0"))
    return Decimal("0")


def list_open_orders(
    *,
    api_key: str,
    api_secret: str,
    symbol: str,
    base_url: Optional[str] = None,
) -> list[Dict[str, Any]]:
    payload = signed_request(
        method="GET",
        path="/api/v3/openOrders",
        api_key=api_key,
        api_secret=api_secret,
        params={"symbol": normalize_symbol(symbol)},
        base_url=base_url,
    )
    if not isinstance(payload, list):
        return []
    return payload


_PROTECTIVE_STOP_TYPES = frozenset({"STOP_LOSS_LIMIT", "STOP_LOSS"})


def _is_protective_stop_order(order: Dict[str, Any]) -> bool:
    side = str(order.get("side") or "").upper()
    order_type = str(order.get("type") or "").upper()
    return side == "SELL" and order_type in _PROTECTIVE_STOP_TYPES


def _is_app_managed_order(order: Dict[str, Any]) -> bool:
    return str(order.get("clientOrderId") or "").startswith(CLIENT_ORDER_PREFIX)


def find_protective_order(
    *,
    api_key: str,
    api_secret: str,
    symbol: str,
    client_order_id: str,
    base_url: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Locate an open protective stop for the symbol.

    Priority:
    1. Exact Cripto Farol ``cfstop_`` clientOrderId for this opportunity
    2. Any other open ``cfstop_`` order on the symbol
    3. Any open Spot SELL stop (``STOP_LOSS`` / ``STOP_LOSS_LIMIT``), including
       orders created on Binance Web/app — so the UI does not offer Proteger
       when a stop already locks the position.
    """
    open_orders = list_open_orders(
        api_key=api_key, api_secret=api_secret, symbol=symbol, base_url=base_url
    )
    exact = None
    app_fallback = None
    external_stop = None
    for order in open_orders:
        cid = str(order.get("clientOrderId") or "")
        if cid == client_order_id:
            exact = order
            break
        if app_fallback is None and cid.startswith(CLIENT_ORDER_PREFIX):
            app_fallback = order
        if external_stop is None and _is_protective_stop_order(order):
            external_stop = order
    return exact or app_fallback or external_stop


def compute_order_prices_and_qty(
    *,
    stop_price: float,
    free_qty: Decimal,
    symbol_info: Dict[str, Any],
) -> Tuple[Decimal, Decimal, Decimal]:
    filters = _filter_map(symbol_info)
    price_filter = filters.get("PRICE_FILTER") or {}
    lot_filter = filters.get("LOT_SIZE") or {}
    notional_filter = filters.get("MIN_NOTIONAL") or filters.get("NOTIONAL") or {}

    tick = Decimal(str(price_filter.get("tickSize") or "0.01"))
    step = Decimal(str(lot_filter.get("stepSize") or "0.0001"))
    min_qty = Decimal(str(lot_filter.get("minQty") or "0"))
    min_notional = Decimal(
        str(notional_filter.get("minNotional") or notional_filter.get("notional") or "0")
    )

    stop = decimal_floor(Decimal(str(stop_price)), tick)
    if stop <= 0:
        raise BinanceOrderError("stop_price inválido")
    limit = decimal_floor(stop * (Decimal("1") - LIMIT_OFFSET_RATIO), tick)
    if limit <= 0:
        raise BinanceOrderError("limitPrice calculado inválido")

    qty = decimal_floor(free_qty, step)
    if qty <= 0 or (min_qty > 0 and qty < min_qty):
        raise BinanceOrderError("Saldo free insuficiente para montar a ordem Spot")
    if min_notional > 0 and (qty * limit) < min_notional:
        raise BinanceOrderError("Notional da ordem abaixo do mínimo da Binance")
    return stop, limit, qty


def get_protective_status(
    *,
    api_key: str,
    api_secret: str,
    user_id: str,
    symbol: str,
    opportunity_id: str,
    base_url: Optional[str] = None,
) -> Dict[str, Any]:
    sym = normalize_symbol(symbol)
    client_order_id = build_client_order_id(
        user_id=user_id, symbol=sym, opportunity_id=str(opportunity_id)
    )
    order = find_protective_order(
        api_key=api_key,
        api_secret=api_secret,
        symbol=sym,
        client_order_id=client_order_id,
        base_url=base_url,
    )
    if not order:
        return {
            "protected": False,
            "symbol": sym,
            "client_order_id": client_order_id,
            "managed_by_app": False,
            "source": None,
            "order": None,
        }
    managed = _is_app_managed_order(order)
    return {
        "protected": True,
        "symbol": sym,
        "client_order_id": str(order.get("clientOrderId") or client_order_id),
        "managed_by_app": managed,
        "source": "app" if managed else "external",
        "order": {
            "order_id": order.get("orderId"),
            "side": order.get("side"),
            "type": order.get("type"),
            "status": order.get("status"),
            "stop_price": float(order.get("stopPrice") or 0) or None,
            "limit_price": float(order.get("price") or 0) or None,
            "quantity": float(order.get("origQty") or 0) or None,
        },
    }


def place_protective_stop(
    *,
    api_key: str,
    api_secret: str,
    user_id: str,
    symbol: str,
    opportunity_id: str,
    stop_price: float,
    direction: str = "long",
    base_url: Optional[str] = None,
) -> Dict[str, Any]:
    if str(direction or "long").strip().lower() == "short":
        raise BinanceOrderError("Proteção Spot stop-limit está disponível apenas para long")

    sym = normalize_symbol(symbol)
    symbol_info = get_symbol_info(sym, base_url=base_url)
    base_asset = str(symbol_info.get("baseAsset") or "").upper()
    if not base_asset:
        raise BinanceOrderError("Base asset não encontrado")

    client_order_id = build_client_order_id(
        user_id=user_id, symbol=sym, opportunity_id=str(opportunity_id)
    )
    existing = find_protective_order(
        api_key=api_key,
        api_secret=api_secret,
        symbol=sym,
        client_order_id=client_order_id,
        base_url=base_url,
    )
    if existing:
        raise BinanceOrderError(
            "Já existe um stop Spot aberto neste símbolo (app ou Binance). Remova antes de criar outro."
        )

    free_qty = fetch_free_balance(
        api_key=api_key, api_secret=api_secret, asset=base_asset, base_url=base_url
    )
    stop, limit, qty = compute_order_prices_and_qty(
        stop_price=stop_price, free_qty=free_qty, symbol_info=symbol_info
    )

    order = signed_request(
        method="POST",
        path="/api/v3/order",
        api_key=api_key,
        api_secret=api_secret,
        params={
            "symbol": sym,
            "side": "SELL",
            "type": "STOP_LOSS_LIMIT",
            "timeInForce": "GTC",
            "quantity": format_decimal(qty),
            "price": format_decimal(limit),
            "stopPrice": format_decimal(stop),
            "newClientOrderId": client_order_id,
        },
        base_url=base_url,
    )
    return {
        "protected": True,
        "symbol": sym,
        "base_asset": base_asset,
        "client_order_id": client_order_id,
        "stop_price": float(stop),
        "limit_price": float(limit),
        "quantity": float(qty),
        "order_id": order.get("orderId"),
        "status": order.get("status"),
    }


def cancel_protective_stop(
    *,
    api_key: str,
    api_secret: str,
    user_id: str,
    symbol: str,
    opportunity_id: str,
    base_url: Optional[str] = None,
) -> Dict[str, Any]:
    sym = normalize_symbol(symbol)
    client_order_id = build_client_order_id(
        user_id=user_id, symbol=sym, opportunity_id=str(opportunity_id)
    )
    order = find_protective_order(
        api_key=api_key,
        api_secret=api_secret,
        symbol=sym,
        client_order_id=client_order_id,
        base_url=base_url,
    )
    if not order:
        raise BinanceOrderError("Nenhuma ordem protetiva Spot encontrada para este símbolo")

    cid = str(order.get("clientOrderId") or "")
    if not (_is_app_managed_order(order) or _is_protective_stop_order(order)):
        raise BinanceOrderError("Ordem encontrada não é um stop protetivo Spot")

    cancel_params: Dict[str, Any] = {"symbol": sym}
    if cid:
        cancel_params["origClientOrderId"] = cid
    else:
        order_id = order.get("orderId")
        if not order_id:
            raise BinanceOrderError("Ordem protetiva sem identificador para cancelar")
        cancel_params["orderId"] = order_id

    canceled = signed_request(
        method="DELETE",
        path="/api/v3/order",
        api_key=api_key,
        api_secret=api_secret,
        params=cancel_params,
        base_url=base_url,
    )
    return {
        "protected": False,
        "symbol": sym,
        "client_order_id": cid,
        "order_id": canceled.get("orderId") or order.get("orderId"),
        "status": canceled.get("status") or "CANCELED",
    }
