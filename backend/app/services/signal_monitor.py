"""Background price monitor that closes BUY signals when target/stop is hit."""

import asyncio
import logging
import threading
import time
from typing import Any

import httpx

from app.database import SessionLocal
from app.models_signal_history import SignalHistory, sao_paulo_now

logger = logging.getLogger(__name__)

BINANCE_TICKER_URL = "https://api.binance.com/api/v3/ticker/price"
REQUEST_TIMEOUT = 8.0
CHECK_INTERVAL_SECONDS = 60.0
_MAX_CONCURRENT_PRICEFETCH = 15


async def _fetch_price(asset: str) -> float | None:
    """Fetch current price for an asset from Binance."""
    params = {"symbol": asset}
    timeout = httpx.Timeout(REQUEST_TIMEOUT)
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(BINANCE_TICKER_URL, params=params)
            if response.status_code == 429:
                return None
            response.raise_for_status()
            data = response.json()
            return float(data.get("price"))
    except Exception:
        return None


def _check_and_update_signals() -> None:
    """Check all ativo BUY signals and close those whose target/stop was hit."""
    db = SessionLocal()
    try:
        signals = (
            db.query(SignalHistory)
            .filter(
                SignalHistory.type == "BUY",
                SignalHistory.status == "ativo",
                SignalHistory.entry_price is not None,
            )
            .all()
        )
        if not signals:
            db.close()
            return

        assets = list({s.asset for s in signals})

        async def _fetch_all_prices():
            semaphore = asyncio.Semaphore(_MAX_CONCURRENT_PRICEFETCH)

            async def _sem_fetch(asset: str) -> tuple[str, float | None]:
                async with semaphore:
                    price = await _fetch_price(asset)
                    return asset, price

            results = await asyncio.gather(*[_sem_fetch(a) for a in assets])
            return dict(results)

        price_map: dict[str, float | None] = {}
        try:
            price_map = asyncio.run(_fetch_all_prices())
        except Exception as e:
            logger.warning("[signal_monitor] Failed to fetch prices: %s", e)
            db.close()
            return

        updated_count = 0
        for signal in signals:
            current_price = price_map.get(signal.asset)
            if current_price is None:
                continue

            exit_price: float | None = None
            triggered = False

            if current_price >= signal.target_price:
                exit_price = signal.target_price
                triggered = True
            elif current_price <= signal.stop_loss:
                exit_price = signal.stop_loss
                triggered = True

            if triggered and exit_price is not None:
                pnl_pct = ((exit_price - signal.entry_price) / signal.entry_price) * 100
                signal.status = "disparado"
                signal.exit_price = exit_price
                signal.pnl = round(pnl_pct, 4)
                signal.updated_at = sao_paulo_now()
                updated_count += 1
                logger.info(
                    "[signal_monitor] Signal %s triggered: entry=%.4f exit=%.4f pnl=%.4f%%",
                    signal.asset,
                    signal.entry_price,
                    exit_price,
                    pnl_pct,
                )

        if updated_count > 0:
            db.commit()
            logger.info("[signal_monitor] Updated %d signals", updated_count)
        db.close()
    except Exception as e:
        db.rollback()
        try:
            db.close()
        except Exception:
            pass
        logger.error("[signal_monitor] Error checking signals: %s", e)


class SignalMonitor:
    """Background service that monitors BUY signals and closes them when target/stop is hit."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def _run_loop(self) -> None:
        logger.info("[signal_monitor] Started background loop")
        while not self._stop_event.is_set():
            try:
                _check_and_update_signals()
            except Exception as e:
                logger.error("[signal_monitor] Unexpected error: %s", e)
            self._stop_event.wait(CHECK_INTERVAL_SECONDS)
        logger.info("[signal_monitor] Stopped background loop")

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("[signal_monitor] Started")

    def stop(self) -> None:
        if self._thread is None:
            return
        self._stop_event.set()
        self._thread.join(timeout=5.0)
        self._thread = None
        logger.info("[signal_monitor] Stopped")


signal_monitor = SignalMonitor()
