from __future__ import annotations

import asyncio
import logging
import os
import signal
from collections.abc import Iterable

from sqlalchemy import text

from app.database import Base, engine, ensure_runtime_schema_migrations, sync_postgres_identity_sequences
from app.services.binance_service import (
    start_signal_feed_snapshot_worker,
    stop_signal_feed_snapshot_worker,
)
from app.services.signal_monitor import signal_monitor
import app.models  # noqa: F401
import app.models_signal_history  # noqa: F401

LOG_LEVEL = os.getenv("WORKER_LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger("runtime_worker")


def _env_enabled(name: str, default: str = "1") -> bool:
    value = os.getenv(name, default).strip().lower()
    return value not in {"", "0", "false", "no", "off"}


def _wait_for_database(*, max_attempts: int = 20, delay_seconds: float = 3.0) -> None:
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("Database is reachable.")
            return
        except Exception as exc:  # pragma: no cover - defensive runtime path
            last_error = exc
            logger.warning(
                "Database connection attempt %s/%s failed: %s",
                attempt,
                max_attempts,
                exc,
            )
            if attempt < max_attempts:
                import time

                time.sleep(delay_seconds)
    raise RuntimeError("Unable to connect to the database for worker startup") from last_error


def _initialize_runtime_state() -> None:
    _wait_for_database()
    Base.metadata.create_all(bind=engine)
    sync_postgres_identity_sequences()
    ensure_runtime_schema_migrations()
    logger.info("Worker runtime state initialized.")


def _install_signal_handlers(stop_event: asyncio.Event, signals: Iterable[signal.Signals]) -> None:
    loop = asyncio.get_running_loop()
    for signum in signals:
        try:
            loop.add_signal_handler(signum, stop_event.set)
        except NotImplementedError:  # pragma: no cover - Windows fallback
            signal.signal(signum, lambda *_args: stop_event.set())


async def _run(stop_event: asyncio.Event) -> None:
    run_signal_monitor = _env_enabled("RUN_SIGNAL_MONITOR")
    run_signal_feed = _env_enabled("RUN_SIGNAL_FEED_SNAPSHOT_WORKER")

    if not run_signal_monitor and not run_signal_feed:
        logger.warning(
            "No worker routines enabled. Set RUN_SIGNAL_MONITOR and/or "
            "RUN_SIGNAL_FEED_SNAPSHOT_WORKER to 1."
        )
        return

    _initialize_runtime_state()

    if run_signal_monitor:
        signal_monitor.start()
        logger.info("Signal monitor started.")

    if run_signal_feed:
        await start_signal_feed_snapshot_worker()
        logger.info("Signal feed snapshot worker started.")

    try:
        await stop_event.wait()
    finally:
        if run_signal_feed:
            await stop_signal_feed_snapshot_worker()
            logger.info("Signal feed snapshot worker stopped.")
        if run_signal_monitor:
            signal_monitor.stop()
            logger.info("Signal monitor stopped.")


async def main() -> None:
    stop_event = asyncio.Event()
    _install_signal_handlers(stop_event, (signal.SIGINT, signal.SIGTERM))
    await _run(stop_event)


if __name__ == "__main__":
    asyncio.run(main())
