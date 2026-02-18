import asyncio
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

try:
    import ccxt.pro as ccxtpro  # type: ignore
except Exception:  # pragma: no cover - handled by runtime checks
    ccxtpro = None

SUPPORTED_EXCHANGES = {"binance", "okx", "bybit"}


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


async def _fetch_top_of_book_ws(exchange_id: str, symbol: str, timeout_sec: int = 10) -> Dict[str, Any]:
    _require_ccxt_pro()

    exchange_class = getattr(ccxtpro, exchange_id, None)
    if exchange_class is None:
        raise ValueError(f"Exchange não suportada: {exchange_id}")

    exchange = exchange_class({"enableRateLimit": True})

    try:
        order_book = await asyncio.wait_for(exchange.watch_order_book(symbol), timeout=timeout_sec)
        best_bid = order_book["bids"][0][0] if order_book.get("bids") else None
        best_ask = order_book["asks"][0][0] if order_book.get("asks") else None
        if best_bid is None or best_ask is None:
            raise RuntimeError(f"Livro de ofertas vazio para {exchange_id}")
        timestamp = order_book.get("timestamp") or exchange.milliseconds()
        return {
            "exchange": exchange_id,
            "best_bid": float(best_bid),
            "best_ask": float(best_ask),
            "timestamp": int(timestamp),
        }
    finally:
        await exchange.close()


def calculate_spreads(quotes: Dict[str, Dict[str, Any]], threshold_pct: float) -> List[Dict[str, Any]]:
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
            if spread_pct < threshold_pct:
                continue
            opportunities.append({
                "buy_exchange": buy_exchange,
                "sell_exchange": sell_exchange,
                "buy_price": buy_ask,
                "sell_price": sell_bid,
                "spread_pct": round(spread_pct, 4),
                "timestamp": max(buy_quote["timestamp"], sell_quote["timestamp"]),
            })

    opportunities.sort(key=lambda item: item["spread_pct"], reverse=True)
    return opportunities


async def get_spread_opportunities(
    symbol: str,
    exchanges: List[str],
    threshold_pct: float,
    timeout_sec: int = 10,
) -> List[Dict[str, Any]]:
    if threshold_pct < 0:
        raise ValueError("Threshold deve ser >= 0")

    normalized = _normalize_exchanges(exchanges)
    tasks = [
        _fetch_top_of_book_ws(exchange_id, symbol, timeout_sec=timeout_sec)
        for exchange_id in normalized
    ]
    results = await asyncio.gather(*tasks)

    quotes = {result["exchange"]: result for result in results}
    return calculate_spreads(quotes, threshold_pct)
