"""Background BTCUSDT scalp loop. One Jev request in flight per user."""

from __future__ import annotations

import asyncio
import fcntl
import logging
import os
from pathlib import Path

from app.database import SessionLocal
from app.services.runtime_status import env_flag_enabled
from app.services.scalp_engine import JEV_FLOOR_MS
from app.services.scalp_btcusdt_stream import ensure_scalp_btcusdt_stream, stop_scalp_btcusdt_stream
from app.services.scalp_jev_log import install_diagnostic_log
from app.services.scalp_service import list_enabled_user_ids, tick_user

logger = logging.getLogger(__name__)

_lock_fh = None
_task: asyncio.Task | None = None


def scalp_loop_enabled() -> bool:
    return env_flag_enabled("SCALP_LOOP_ENABLED", "1")


def _lock_path() -> Path:
    return Path(os.getenv("CRYPTO_SCALP_LOOP_LOCK_FILE", "/tmp/crypto-scalp-loop.lock"))


def _acquire_lock() -> bool:
    global _lock_fh
    path = _lock_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = open(path, "a+", encoding="utf-8")
    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        handle.close()
        return False
    _lock_fh = handle
    handle.seek(0)
    handle.write(str(os.getpid()))
    handle.flush()
    return True


def _release_lock() -> None:
    global _lock_fh
    if _lock_fh is None:
        return
    try:
        fcntl.flock(_lock_fh.fileno(), fcntl.LOCK_UN)
    except Exception:
        pass
    try:
        _lock_fh.close()
    except Exception:
        pass
    _lock_fh = None


def _tick_user_blocking(user_id: str) -> None:
    """Run one scalp tick off the asyncio loop so Jev HTTP cannot block the WS stream."""
    db = SessionLocal()
    try:
        tick_user(db, user_id)
    except Exception:
        logger.exception("scalp tick failed user=%s", user_id)
    finally:
        db.close()


async def scalp_loop(stop_event: asyncio.Event | None = None) -> None:
    interval = max(JEV_FLOOR_MS / 1000.0, 0.4)
    # DEV-only diagnostic file (card #1015): installed when this loop runs in
    # the runtime-worker started with RUN_SCALP_LOOP=1. PROD sets no flag.
    # Logging is a side effect: it must never stop the loop.
    try:
        install_diagnostic_log()
    except Exception as exc:  # pragma: no cover - defensive
        logger.warning("Scalp JEV diagnostic log unavailable: %s", exc)
    logger.info("Scalp BTCUSDT loop started (interval=%.2fs)", interval)
    while True:
        if stop_event is not None and stop_event.is_set():
            break
        db = SessionLocal()
        try:
            user_ids = list_enabled_user_ids(db)
            if user_ids:
                await ensure_scalp_btcusdt_stream()
            else:
                await stop_scalp_btcusdt_stream()
            for user_id in user_ids:
                await asyncio.to_thread(_tick_user_blocking, str(user_id))
        except Exception:
            logger.exception("scalp loop listing users failed")
        finally:
            db.close()
        try:
            if stop_event is None:
                await asyncio.sleep(interval)
            else:
                await asyncio.wait_for(stop_event.wait(), timeout=interval)
        except asyncio.TimeoutError:
            continue
        except asyncio.CancelledError:
            break
    logger.info("Scalp BTCUSDT loop stopped")


async def start_scalp_loop() -> None:
    global _task
    if not scalp_loop_enabled():
        logger.info("Scalp loop disabled by SCALP_LOOP_ENABLED")
        return
    if not _acquire_lock():
        logger.info("Scalp loop lock held elsewhere — skipping this process")
        return
    _task = asyncio.create_task(scalp_loop(), name="scalp-btcusdt-loop")


async def stop_scalp_loop() -> None:
    global _task
    if _task is not None:
        _task.cancel()
        try:
            await _task
        except asyncio.CancelledError:
            pass
        _task = None
    _release_lock()
    await stop_scalp_btcusdt_stream()
