"""
Batch backtest orchestration.

Runs optimization per symbol using the same config, saves each best result
as a new favorite with notes "gerado em lote" and tier=3. Never overwrites
existing favorites.
"""

import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

from app.services.combo_optimizer import ComboOptimizer
from app.database import SessionLocal
from app.models import FavoriteStrategy

logger = logging.getLogger(__name__)

# In-memory progress store keyed by job_id
_batch_jobs: Dict[str, Dict[str, Any]] = {}


def _get_or_init_job(job_id: str, total: int) -> Dict[str, Any]:
    if job_id not in _batch_jobs:
        _batch_jobs[job_id] = {
            "job_id": job_id,
            "status": "running",
            "processed": 0,
            "total": total,
            "succeeded": 0,
            "failed": 0,
            "skipped": 0,
            "errors": [],
            "started_at": datetime.utcnow().isoformat(),
            "elapsed_sec": 0.0,
            "estimated_remaining_sec": None,
            "cancel_requested": False,
            "pause_requested": False,
        }
    return _batch_jobs[job_id]


def get_batch_progress(job_id: str) -> Optional[Dict[str, Any]]:
    """Return current progress for a batch job, or None if not found."""
    return _batch_jobs.get(job_id)


def init_batch_job(job_id: str, total: int) -> None:
    """Create job entry before background task runs so GET /batch/{id} returns immediately."""
    _get_or_init_job(job_id, total)


def request_pause_batch(job_id: str) -> bool:
    """Signal the batch job to pause after the current symbol. Returns True if job exists."""
    job = _batch_jobs.get(job_id)
    if not job or job["status"] != "running":
        return False
    job["pause_requested"] = True
    return True


def request_cancel_batch(job_id: str) -> bool:
    """Signal the batch job to cancel after the current symbol. Returns True if job exists."""
    job = _batch_jobs.get(job_id)
    if not job or job["status"] != "running":
        return False
    job["cancel_requested"] = True
    return True


def run_batch_backtest(job_id: str, payload: Dict[str, Any]) -> None:
    """
    Run optimization for each symbol, save best result as new favorite.
    Updates _batch_jobs[job_id] with progress. Never overwrites favorites.
    """
    template_name = payload["template_name"]
    symbols = payload["symbols"]
    timeframe = payload.get("timeframe", "1d")
    start_date = payload.get("start_date")
    end_date = payload.get("end_date")
    period_type = payload.get("period_type")  # '6m' | '2y' | 'all'
    deep_backtest = payload.get("deep_backtest", True)
    custom_ranges = payload.get("custom_ranges")
    initial_capital = payload.get("initial_capital", 100)

    total = len(symbols)
    job = _get_or_init_job(job_id, total)
    started = time.time()
    batch_note = f'gerado em lote ({job_id[:8]})'

    optimizer = ComboOptimizer()

    for i, symbol in enumerate(symbols):
        job["elapsed_sec"] = time.time() - started
        if job.get("cancel_requested"):
            job["status"] = "cancelled"
            job["estimated_remaining_sec"] = None
            logger.info("Batch %s cancelled by user", job_id[:8])
            return
        if job.get("pause_requested"):
            job["status"] = "paused"
            job["estimated_remaining_sec"] = None
            logger.info("Batch %s paused by user", job_id[:8])
            return

        db_check = SessionLocal()
        try:
            q = db_check.query(FavoriteStrategy).filter(
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
            existing = q.first()
            if existing:
                logger.info("Batch: skip %s (already in favorites, same period)", symbol)
                job["skipped"] = job.get("skipped", 0) + 1
                job["processed"] = job["succeeded"] + job["failed"] + job["skipped"]
                if job["processed"] > 0 and job["processed"] < total:
                    job["estimated_remaining_sec"] = (job["elapsed_sec"] / job["processed"]) * (total - job["processed"])
                continue
        finally:
            db_check.close()

        try:
            result = optimizer.run_optimization(
                template_name=template_name,
                symbol=symbol,
                timeframe=timeframe,
                start_date=start_date,
                end_date=end_date,
                custom_ranges=custom_ranges,
                deep_backtest=deep_backtest,
                job_id=job_id,
            )
        except Exception as e:
            logger.exception("Batch backtest failed for %s: %s", symbol, e)
            job["failed"] = job.get("failed", 0) + 1
            job["errors"].append({"symbol": symbol, "error": str(e)})
            job["processed"] = job["succeeded"] + job["failed"] + job.get("skipped", 0)
            if job["processed"] > 0 and job["processed"] < total:
                job["estimated_remaining_sec"] = (job["elapsed_sec"] / job["processed"]) * (total - job["processed"])
            continue

        best_params = result.get("best_parameters") or result.get("parameters") or {}
        best_metrics = result.get("best_metrics") or {}

        name = f"{template_name} - {symbol} {timeframe} (batch)"
        notes = batch_note

        db = SessionLocal()
        try:
            fav = FavoriteStrategy(
                name=name,
                symbol=symbol,
                timeframe=timeframe,
                strategy_name=template_name,
                parameters=best_params,
                metrics=best_metrics,
                notes=notes,
                tier=3,
                start_date=start_date,
                end_date=end_date,
                period_type=period_type,
            )
            db.add(fav)
            db.commit()
            db.refresh(fav)
            job["succeeded"] = job.get("succeeded", 0) + 1
            logger.info("Batch: saved favorite for %s (id=%s)", symbol, fav.id)
        except Exception as e:
            logger.exception("Batch: failed to save favorite for %s: %s", symbol, e)
            job["failed"] = job.get("failed", 0) + 1
            job["errors"].append({"symbol": symbol, "error": f"save favorite: {e}"})
        finally:
            db.close()

        job["processed"] = job["succeeded"] + job["failed"] + job.get("skipped", 0)
        if job["processed"] > 0 and job["processed"] < total:
            job["estimated_remaining_sec"] = (job["elapsed_sec"] / job["processed"]) * (total - job["processed"])

    job["processed"] = total
    job["elapsed_sec"] = time.time() - started
    job["status"] = "completed"
    job["estimated_remaining_sec"] = None
    logger.info("Batch %s completed: %d succeeded, %d failed, %d skipped", job_id[:8],
                job.get("succeeded", 0), job.get("failed", 0), job.get("skipped", 0))
