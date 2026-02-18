import asyncio
import logging
from pathlib import Path
from typing import List

from app.services.arbitrage_spread_service import get_spreads_for_symbols

LOG_PATH = Path(__file__).resolve().parents[2] / "logs" / "arbitrage_opportunities.log"
DEFAULT_SYMBOLS = ["USDT/USDC", "USDT/DAI", "USDC/DAI"]
DEFAULT_EXCHANGES = ["binance", "okx", "bybit"]
DEFAULT_THRESHOLD = 0.30
DEFAULT_INTERVAL_SECONDS = 3


def _get_logger() -> logging.Logger:
    logger = logging.getLogger("arbitrage-monitor")
    if any(isinstance(h, logging.FileHandler) and h.baseFilename == str(LOG_PATH) for h in logger.handlers):
        return logger

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(LOG_PATH, mode="a", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger


async def monitor_arbitrage_opportunities(
    *,
    symbols: List[str] = None,
    exchanges: List[str] = None,
    threshold: float = DEFAULT_THRESHOLD,
    interval_seconds: int = DEFAULT_INTERVAL_SECONDS,
    stop_event: asyncio.Event | None = None,
) -> None:
    logger = _get_logger()
    symbols = symbols or DEFAULT_SYMBOLS
    exchanges = exchanges or DEFAULT_EXCHANGES

    logger.info("Arbitrage monitor iniciado (threshold=%.2f%%, interval=%ss)", threshold, interval_seconds)
    while True:
        if stop_event and stop_event.is_set():
            logger.info("Arbitrage monitor encerrado")
            return

        try:
            results = await get_spreads_for_symbols(
                symbols=symbols,
                exchanges=exchanges,
                threshold_pct=threshold,
            )

            for symbol, payload in results.items():
                opportunities = payload.get("opportunities", [])
                if not opportunities:
                    logger.info("NO_OPPORTUNITY %s", symbol)
                    continue
                for opp in opportunities:
                    logger.info(
                        "OPPORTUNITY %s | %s -> %s | spread=%.4f%% | buy=%.6f sell=%.6f",
                        symbol,
                        opp.get("buy_exchange"),
                        opp.get("sell_exchange"),
                        opp.get("spread_pct", 0.0),
                        opp.get("buy_price", 0.0),
                        opp.get("sell_price", 0.0),
                    )
        except Exception as exc:  # noqa: BLE001
            logger.error("Erro no monitor de arbitragem: %s", exc)

        try:
            await asyncio.sleep(interval_seconds)
        except asyncio.CancelledError:
            logger.info("Arbitrage monitor cancelado")
            return
