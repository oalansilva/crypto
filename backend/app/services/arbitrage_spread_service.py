import asyncio
import logging
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)

try:
    import ccxt.pro as ccxtpro  # type: ignore
except Exception:  # pragma: no cover - handled by runtime checks
    ccxtpro = None

SUPPORTED_EXCHANGES = {"binance", "okx", "bybit"}

_quote_cache: Dict[Tuple[str, str], Dict[str, Any]] = {}
_quote_events: Dict[Tuple[str, str], asyncio.Event] = {}
_ws_tasks: Dict[Tuple[str, str], asyncio.Task] = {}
_exchange_clients: Dict[str, Any] = {}
_exchange_lock = asyncio.Lock()
_symbol_meta: Dict[Tuple[str, str], Tuple[str, bool]] = {}


def _resolve_symbol(exchange, symbol: str) -> tuple[str, bool]:
    if symbol in exchange.symbols:
        return symbol, False

    base, quote = symbol.split("/")
    for market_symbol, market in exchange.markets.items():
        if market.get("base") == base and market.get("quote") == quote:
            return market_symbol, False

    for market_symbol, market in exchange.markets.items():
        if market.get("base") == quote and market.get("quote") == base:
            return market_symbol, True

    raise ValueError(f"{exchange.id} não possui símbolo {symbol}")


def _require_ccxt_pro() -> None:
    if ccxtpro is None:
        raise RuntimeError("ccxt.pro não está instalado. Instale ccxt.pro para uso via WebSocket.")


def _normalize_exchanges(exchanges: List[str]) -> List[str]:
    normalized = [e.strip().lower() for e in exchanges if e and e.strip()]
    if not normalized:
        raise ValueError("Nenhuma exchange informada.")
    unsupported = [e for e in normalized if e not in SUPPORTED_EXCHANGES]
    if unsupported:
        raise ValueError(f"Exchanges não suportadas: {', '.join(unsupported)}")
    return normalized


async def _get_exchange(exchange_id: str):
    _require_ccxt_pro()
    async with _exchange_lock:
        if exchange_id in _exchange_clients:
            return _exchange_clients[exchange_id]
        exchange_class = getattr(ccxtpro, exchange_id, None)
        if exchange_class is None:
            raise ValueError(f"Exchange não suportada: {exchange_id}")
        exchange = exchange_class({"enableRateLimit": True})
        await exchange.load_markets()
        _exchange_clients[exchange_id] = exchange
        return exchange


def _get_event(key: Tuple[str, str]) -> asyncio.Event:
    if key not in _quote_events:
        _quote_events[key] = asyncio.Event()
    return _quote_events[key]


def _ensure_stream(exchange_id: str, symbol: str) -> None:
    key = (exchange_id, symbol)
    if key in _ws_tasks and not _ws_tasks[key].done():
        return

    async def _stream() -> None:
        try:
            exchange = await _get_exchange(exchange_id)
            resolved_symbol, inverted = _resolve_symbol(exchange, symbol)
            _symbol_meta[key] = (resolved_symbol, inverted)
        except Exception as exc:  # noqa: BLE001
            logger.error("Falha ao preparar stream %s %s: %s", exchange_id, symbol, exc)
            _quote_cache[key] = {
                "exchange": exchange_id,
                "symbol": symbol,
                "error": str(exc),
                "timestamp": 0,
            }
            _get_event(key).set()
            return

        while True:
            try:
                exchange = _exchange_clients.get(exchange_id) or await _get_exchange(exchange_id)
                resolved_symbol, inverted = _symbol_meta[key]
                order_book = await exchange.watch_order_book(resolved_symbol)
                best_bid = order_book["bids"][0][0] if order_book.get("bids") else None
                best_ask = order_book["asks"][0][0] if order_book.get("asks") else None
                if best_bid is None or best_ask is None:
                    raise RuntimeError(f"Livro de ofertas vazio para {exchange_id}")
                if inverted:
                    best_bid, best_ask = (1 / best_ask), (1 / best_bid)
                timestamp = order_book.get("timestamp") or exchange.milliseconds()
                _quote_cache[key] = {
                    "exchange": exchange_id,
                    "symbol": resolved_symbol,
                    "inverted": inverted,
                    "best_bid": float(best_bid),
                    "best_ask": float(best_ask),
                    "timestamp": int(timestamp),
                }
                _get_event(key).set()
            except Exception as exc:  # noqa: BLE001
                logger.warning("Erro stream %s %s: %s", exchange_id, symbol, exc)
                await asyncio.sleep(2)

    _ws_tasks[key] = asyncio.create_task(_stream())


def calculate_spreads(quotes: Dict[str, Dict[str, Any]], threshold_pct: float) -> Dict[str, List[Dict[str, Any]]]:
    spreads: List[Dict[str, Any]] = []
    opportunities: List[Dict[str, Any]] = []
    exchanges = list(quotes.keys())

    for buy_exchange in exchanges:
        buy_quote = quotes[buy_exchange]
        buy_ask = buy_quote["best_ask"]
        for sell_exchange in exchanges:
            if sell_exchange == buy_exchange:
                continue
            sell_quote = quotes[sell_exchange]
            sell_bid = sell_quote["best_bid"]
            spread_pct = (sell_bid - buy_ask) / buy_ask * 100
            item = {
                "buy_exchange": buy_exchange,
                "sell_exchange": sell_exchange,
                "buy_price": buy_ask,
                "sell_price": sell_bid,
                "spread_pct": round(spread_pct, 4),
                "timestamp": max(buy_quote["timestamp"], sell_quote["timestamp"]),
                "meets_threshold": spread_pct >= threshold_pct,
            }
            spreads.append(item)
            if spread_pct >= threshold_pct:
                opportunities.append(item)

    spreads.sort(key=lambda item: item["spread_pct"], reverse=True)
    opportunities.sort(key=lambda item: item["spread_pct"], reverse=True)
    return {"spreads": spreads, "opportunities": opportunities}


async def _await_quote(key: Tuple[str, str], timeout_sec: int) -> Dict[str, Any]:
    event = _get_event(key)
    try:
        await asyncio.wait_for(event.wait(), timeout=timeout_sec)
    except asyncio.TimeoutError as exc:
        raise RuntimeError(f"Timeout aguardando {key[0]} {key[1]}") from exc
    quote = _quote_cache.get(key)
    if not quote or quote.get("error"):
        raise RuntimeError(quote.get("error") if quote else "Sem cotação disponível")
    return quote


async def get_spread_opportunities(
    symbol: str,
    exchanges: List[str],
    threshold_pct: float,
    timeout_sec: int = 10,
) -> Dict[str, List[Dict[str, Any]]]:
    if threshold_pct < 0:
        raise ValueError("Threshold deve ser >= 0")

    normalized = _normalize_exchanges(exchanges)
    for exchange_id in normalized:
        _ensure_stream(exchange_id, symbol)

    quotes = {}
    for exchange_id in normalized:
        key = (exchange_id, symbol)
        quotes[exchange_id] = await _await_quote(key, timeout_sec)

    return calculate_spreads(quotes, threshold_pct)


async def get_spreads_for_symbols(
    symbols: List[str],
    exchanges: List[str],
    threshold_pct: float,
    timeout_sec: int = 10,
) -> Dict[str, Dict[str, Any]]:
    async def _fetch(symbol: str) -> tuple[str, Dict[str, Any]]:
        try:
            result = await get_spread_opportunities(
                symbol=symbol,
                exchanges=exchanges,
                threshold_pct=threshold_pct,
                timeout_sec=timeout_sec,
            )
            return symbol, result
        except (ValueError, RuntimeError) as exc:
            return symbol, {
                "spreads": [],
                "opportunities": [],
                "error": str(exc),
            }

    results = await asyncio.gather(*[_fetch(symbol) for symbol in symbols])
    return {symbol: payload for symbol, payload in results}
