from __future__ import annotations

import logging
from typing import Any

from celery import Task

from app.celery_app import celery_app
from app.config import get_settings
from app.services.batch_backtest_service import run_batch_backtest
from app.services.batch_backtest_store import get_batch_backtest_store

logger = logging.getLogger(__name__)


class BatchBacktestTask(Task):
    autoretry_for = (Exception,)
    retry_backoff = True
    retry_jitter = True
    acks_late = True
    reject_on_worker_lost = True

    def on_retry(
        self,
        exc: BaseException,
        task_id: str,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        einfo: Any,
    ) -> None:
        job_id = str(args[0])
        store = get_batch_backtest_store()
        retry_count = int(self.request.retries or 0)
        store.update_job(
            job_id,
            status="retrying",
            retry_count=retry_count,
            last_error=str(exc),
            task_id=task_id,
        )
        logger.warning("Retrying batch backtest job %s (retry=%s): %s", job_id, retry_count, exc)

    def on_failure(
        self,
        exc: BaseException,
        task_id: str,
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
        einfo: Any,
    ) -> None:
        job_id = str(args[0])
        payload = dict(args[1]) if len(args) > 1 and isinstance(args[1], dict) else {}
        store = get_batch_backtest_store()
        current = store.get_job(job_id) or {}
        if current.get("status") not in {"completed", "cancelled", "paused"}:
            retry_count = int(self.request.retries or 0)
            store.update_job(
                job_id,
                status="failed",
                retry_count=retry_count,
                last_error=str(exc),
                dead_lettered=True,
                task_id=task_id,
            )
            store.record_dead_letter(
                job_id=job_id,
                task_id=task_id,
                payload=payload,
                reason=str(exc),
                retry_count=retry_count,
            )
        logger.error("Batch backtest job %s failed permanently: %s", job_id, exc)


@celery_app.task(
    bind=True,
    base=BatchBacktestTask,
    name="app.tasks.batch_backtest_tasks.run_batch_backtest_task",
    max_retries=get_settings().celery_batch_max_retries,
    retry_backoff_max=get_settings().celery_retry_backoff_max,
)
def run_batch_backtest_task(
    self: BatchBacktestTask, job_id: str, payload: dict[str, Any]
) -> dict[str, Any]:
    store = get_batch_backtest_store()
    store.update_job(job_id, status="running", task_id=self.request.id)
    run_batch_backtest(job_id, payload)
    return {"job_id": job_id, "task_id": self.request.id}
