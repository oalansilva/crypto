"""
Batch backtest orchestration.

Runs optimization per symbol using the same config, saves each best result
as a new favorite with notes "gerado em lote" and tier=3. Never overwrites
existing favorites.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Any

from app.database import SessionLocal
from app.models import FavoriteStrategy
from app.services.batch_backtest_store import get_batch_backtest_store
from app.services.combo_optimizer import ComboOptimizer
from app.services.market_data_providers import resolve_data_source_for_symbol
from app.services.opportunity_service import _is_unsupported_symbol

logger = logging.getLogger(__name__)


def _persist_progress(job: dict[str, Any]) -> dict[str, Any]:
    return get_batch_backtest_store().save_job(job)


def _load_job(job_id: str) -> dict[str, Any] | None:
    return get_batch_backtest_store().get_job(job_id)


def get_batch_progress(job_id: str) -> dict[str, Any] | None:
    """Return current progress for a batch job, or None if not found."""
    return _load_job(job_id)


def init_batch_job(job_id: str, total: int) -> None:
    """Create job entry before task dispatch so GET /batch/{id} returns immediately."""
    get_batch_backtest_store().init_job(job_id, total)


def request_pause_batch(job_id: str) -> bool:
    """Signal the batch job to pause after the current symbol. Returns True if job exists."""
    store = get_batch_backtest_store()
    job = store.get_job(job_id)
    if not job or job["status"] not in {"queued", "running", "retrying"}:
        return False
    if job["status"] == "queued":
        job["status"] = "paused"
    job["pause_requested"] = True
    _persist_progress(job)
    return True


def request_cancel_batch(job_id: str) -> bool:
    """Signal the batch job to cancel after the current symbol. Returns True if job exists."""
    store = get_batch_backtest_store()
    job = store.get_job(job_id)
    if not job or job["status"] not in {"queued", "running", "retrying"}:
        return False
    if job["status"] == "queued":
        job["status"] = "cancelled"
        job["estimated_remaining_sec"] = None
        job["current_symbol"] = None
    job["cancel_requested"] = True
    _persist_progress(job)
    return True


def _should_stop(job_id: str, job: dict[str, Any]) -> tuple[bool, dict[str, Any]]:
    latest = _load_job(job_id)
    if latest is None:
        return False, job
    job["cancel_requested"] = latest.get("cancel_requested", False)
    job["pause_requested"] = latest.get("pause_requested", False)
    job["retry_count"] = latest.get("retry_count", job.get("retry_count", 0))
    job["task_id"] = latest.get("task_id", job.get("task_id"))
    if job.get("cancel_requested"):
        job["status"] = "cancelled"
        job["estimated_remaining_sec"] = None
        job["current_symbol"] = None
        _persist_progress(job)
        logger.info("Batch %s cancelled by user", job_id[:8])
        return True, job
    if job.get("pause_requested"):
        job["status"] = "paused"
        job["estimated_remaining_sec"] = None
        job["current_symbol"] = None
        _persist_progress(job)
        logger.info("Batch %s paused by user", job_id[:8])
        return True, job
    return False, job


def run_batch_backtest(job_id: str, payload: dict[str, Any]) -> None:
    """
    Run optimization for each symbol, save best result as new favorite.
    Updates the shared store with progress. Never overwrites favorites.
    """
    template_name = payload["template_name"]
    symbols = payload["symbols"]
    timeframe = payload.get("timeframe", "1d")
    data_source = payload.get("data_source")
    start_date = payload.get("start_date")
    end_date = payload.get("end_date")
    period_type = payload.get("period_type")  # '6m' | '2y' | 'all'
    deep_backtest = payload.get("deep_backtest", True)
    custom_ranges = payload.get("custom_ranges")
    direction = payload.get("direction", "long")
    user_id = payload.get("user_id")
    if direction not in ("long", "short"):
        direction = "long"

    total = len(symbols)
    job = _load_job(job_id) or get_batch_backtest_store().init_job(job_id, total)
    job["status"] = "running"
    job["started_at"] = job.get("started_at") or datetime.utcnow().isoformat()
    job["total"] = total
    job["last_error"] = None
    _persist_progress(job)

    should_stop, job = _should_stop(job_id, job)
    if should_stop:
        return

    started = time.time()
    batch_note = f"gerado em lote ({job_id[:8]})"
    optimizer = ComboOptimizer()

    for symbol in symbols:
        job["elapsed_sec"] = time.time() - started
        job["current_symbol"] = symbol
        _persist_progress(job)

        should_stop, job = _should_stop(job_id, job)
        if should_stop:
            return

        if _is_unsupported_symbol(symbol):
            logger.info("Batch: skip %s (unsupported / excluded)", symbol)
            job["skipped"] = job.get("skipped", 0) + 1
            job["processed"] = job["succeeded"] + job["failed"] + job["skipped"]
            if 0 < job["processed"] < total:
                job["estimated_remaining_sec"] = (job["elapsed_sec"] / job["processed"]) * (
                    total - job["processed"]
                )
            _persist_progress(job)
            continue

        db_check = SessionLocal()
        try:
            q = db_check.query(FavoriteStrategy).filter(
                FavoriteStrategy.user_id == user_id,
                FavoriteStrategy.strategy_name == template_name,
                FavoriteStrategy.symbol == symbol,
                FavoriteStrategy.timeframe == timeframe,
            )
            if period_type is not None:
                q = q.filter(FavoriteStrategy.period_type == period_type)
            else:
                if start_date is None:
                    q = q.filter(FavoriteStrategy.start_date.is_(None))
                else:
                    q = q.filter(FavoriteStrategy.start_date == start_date)
                if end_date is None:
                    q = q.filter(FavoriteStrategy.end_date.is_(None))
                else:
                    q = q.filter(FavoriteStrategy.end_date == end_date)
            rows = q.all()
            if direction is not None:
                want = (direction or "long").lower()
                if want not in ("long", "short"):
                    want = "long"
                rows = [
                    row
                    for row in rows
                    if ((row.parameters or {}).get("direction") or "long").lower() == want
                ]
            if rows:
                logger.info(
                    "Batch: skip %s (already in favorites, same period and direction)", symbol
                )
                job["skipped"] = job.get("skipped", 0) + 1
                job["processed"] = job["succeeded"] + job["failed"] + job["skipped"]
                if 0 < job["processed"] < total:
                    job["estimated_remaining_sec"] = (job["elapsed_sec"] / job["processed"]) * (
                        total - job["processed"]
                    )
                _persist_progress(job)
                continue
        finally:
            db_check.close()

        effective_data_source = data_source
        if not effective_data_source:
            effective_data_source = resolve_data_source_for_symbol(symbol, None)

        try:
            result = optimizer.run_optimization(
                template_name=template_name,
                symbol=symbol,
                timeframe=timeframe,
                data_source=effective_data_source,
                start_date=start_date,
                end_date=end_date,
                custom_ranges=custom_ranges,
                deep_backtest=deep_backtest,
                job_id=job_id,
                direction=direction,
            )
        except KeyboardInterrupt:
            job["status"] = "cancelled"
            job["estimated_remaining_sec"] = None
            job["current_symbol"] = None
            _persist_progress(job)
            logger.info("Batch %s cancelled (CTRL+C)", job_id[:8])
            return
        except Exception as exc:
            logger.exception("Batch backtest failed for %s: %s", symbol, exc)
            job["failed"] = job.get("failed", 0) + 1
            job["errors"].append({"symbol": symbol, "error": str(exc)})
            job["processed"] = job["succeeded"] + job["failed"] + job.get("skipped", 0)
            if 0 < job["processed"] < total:
                job["estimated_remaining_sec"] = (job["elapsed_sec"] / job["processed"]) * (
                    total - job["processed"]
                )
            _persist_progress(job)
            continue

        best_params = result.get("best_parameters") or result.get("parameters") or {}
        best_metrics = result.get("best_metrics") or {}
        params_with_direction = dict(best_params)
        params_with_direction["direction"] = direction
        if effective_data_source:
            params_with_direction["data_source"] = effective_data_source

        name = f"{template_name} - {symbol} {timeframe} (batch)"
        notes = batch_note

        db = SessionLocal()
        try:
            favorite = FavoriteStrategy(
                user_id=user_id,
                name=name,
                symbol=symbol,
                timeframe=timeframe,
                strategy_name=template_name,
                parameters=params_with_direction,
                metrics=best_metrics,
                notes=notes,
                tier=3,
                start_date=start_date,
                end_date=end_date,
                period_type=period_type,
            )
            db.add(favorite)
            db.commit()
            db.refresh(favorite)
            job["succeeded"] = job.get("succeeded", 0) + 1
            logger.info("Batch: saved favorite for %s (id=%s)", symbol, favorite.id)
        except Exception as exc:
            logger.exception("Batch: failed to save favorite for %s: %s", symbol, exc)
            job["failed"] = job.get("failed", 0) + 1
            job["errors"].append({"symbol": symbol, "error": f"save favorite: {exc}"})
        finally:
            db.close()

        job["processed"] = job["succeeded"] + job["failed"] + job.get("skipped", 0)
        if 0 < job["processed"] < total:
            job["estimated_remaining_sec"] = (job["elapsed_sec"] / job["processed"]) * (
                total - job["processed"]
            )
        _persist_progress(job)

    job["processed"] = total
    job["elapsed_sec"] = time.time() - started
    job["status"] = "completed"
    job["estimated_remaining_sec"] = None
    job["current_symbol"] = None
    _persist_progress(job)
    logger.info(
        "Batch %s completed: %d succeeded, %d failed, %d skipped",
        job_id[:8],
        job.get("succeeded", 0),
        job.get("failed", 0),
        job.get("skipped", 0),
    )
