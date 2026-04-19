from __future__ import annotations

from celery import Celery

from app.config import get_settings


def _env_enabled(value: str) -> bool:
    return str(value).strip().lower() not in {"", "0", "false", "no", "off"}


settings = get_settings()

celery_app = Celery(
    "crypto",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_default_queue="default",
    task_routes={
        "app.tasks.batch_backtest_tasks.run_batch_backtest_task": {"queue": "batch_backtest"},
    },
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    result_expires=settings.async_job_ttl_seconds,
    task_track_started=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=settings.celery_worker_prefetch_multiplier,
    broker_connection_retry_on_startup=True,
    task_always_eager=_env_enabled(settings.celery_task_always_eager),
)

celery_app.autodiscover_tasks(["app.tasks"])
