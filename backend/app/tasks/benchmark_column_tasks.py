"""Job da coluna extra do Decidir na fila de lotes (card #1123, decisão 10; fila do #1120)."""

from __future__ import annotations

import logging

from app.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.benchmark_column_tasks.run_reference_column_task", acks_late=True)
def run_reference_column_task(column_id: str) -> None:
    from app.services.discovery_reference_column import run_column

    logger.info("Coluna extra %s: início", column_id)
    run_column(column_id)
