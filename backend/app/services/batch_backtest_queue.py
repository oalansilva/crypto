from __future__ import annotations

import logging
from typing import Any

from app.services.batch_backtest_store import get_batch_backtest_store
from app.tasks.batch_backtest_tasks import run_batch_backtest_task

logger = logging.getLogger(__name__)


def enqueue_batch_backtest(job_id: str, payload: dict[str, Any]) -> str:
    store = get_batch_backtest_store()
    try:
        result = run_batch_backtest_task.delay(job_id, payload)
    except Exception as exc:
        logger.exception("Failed to enqueue batch backtest job %s: %s", job_id, exc)
        store.update_job(job_id, status="failed", last_error=f"queue dispatch failed: {exc}")
        raise

    task_id = getattr(result, "id", None) or job_id
    store.update_job(job_id, task_id=task_id)
    return task_id
