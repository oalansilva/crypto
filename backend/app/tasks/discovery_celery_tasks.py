"""Celery task for the discovery sweep orchestrator (card #469)."""

from __future__ import annotations

import logging
from typing import Any

from celery import Task

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models_discovery import DiscoverySweep
from app.services.discovery_service import DiscoveryService

logger = logging.getLogger(__name__)


class DiscoveryOrchestratorTask(Task):
    autoretry_for = (Exception,)
    retry_backoff = True
    retry_jitter = True
    acks_late = True
    reject_on_worker_lost = True


def run_sweep_orchestrator(sweep_id: str, generation: int) -> dict[str, Any]:
    """Orquestrador de um sweep: reclama combinações em lote, executa e
    reconcilia. Idempotente: combinações já com resultado não reexecutam.

    Caminho do intent com sweep `cancelling` (card #853, P1): claim vazio →
    lock + refresh → release escopado ao sweep (flush-only) → `reconcile_sweep`
    sob lock (flush) → ack flush-only como última mutação — tudo no mesmo
    commit único do sweep. SOMENTE o helper escopado é usado aqui; o
    `release_expired_leases` global com commit próprio foi removido deste
    caminho (ressuscitaria `running` expirado em `pending` de `cancelled` de
    OUTRO sweep sem reconcile acoplado).
    """
    from app.tasks.discovery_tasks import _reconcile_locked, reconcile_sweep, run_combination

    service = DiscoveryService()
    db = SessionLocal()
    try:
        probe = db.query(DiscoverySweep).filter(DiscoverySweep.id == sweep_id).first()
        if probe is not None and probe.state == "cancelling":
            locked = service._lock_sweep(db, sweep_id)
            if locked is not None:
                db.refresh(locked)
                if locked.state == "cancelling":
                    service._release_expired_leases_for_sweep(db, sweep_id)
                    summary = _reconcile_locked(locked, db)
                    service._ack_locked(sweep_id, generation, db=db)
                    db.commit()
                    logger.info(
                        "Discovery cancel finalizer ack recorded: sweep=%s generation=%s state=%s running=%s pending=%s",
                        sweep_id,
                        generation,
                        summary.get("state"),
                        summary.get("running"),
                        summary.get("pending"),
                    )
                    return summary
            # Caiu para terminal entre probe e lock: rollback e segue o caminho
            # normal, que re-finaliza resíduo sem sobrescrever o terminal.
            db.rollback()
        claimed = service.claim_combinations(sweep_id, owner=f"orchestrator-{generation}", db=db)
        logger.info(
            "Discovery orchestrator started: sweep=%s generation=%s claimed=%s",
            sweep_id,
            generation,
            len(claimed),
        )
        for combination in claimed:
            run_combination(db, combination, owner=f"orchestrator-{generation}")
            # Persist progress after each potentially long optimization so the
            # polling UI does not remain at 0 until the whole claim finishes.
            reconcile_sweep(sweep_id, db)
        service.release_expired_leases(db=db)
        summary = reconcile_sweep(sweep_id, db)
        if summary.get("state") == "running":
            claimable = service.count_claimable(sweep_id, db=db)
            if claimable > 0:
                service.ensure_sweep_wakeup(db, sweep_id, rotate_from=generation)
        service.ack_outbox(sweep_id, generation, db=db)
        logger.info("Discovery orchestrator finished: sweep=%s summary=%s", sweep_id, summary)
        return summary
    finally:
        db.close()


@celery_app.task(
    bind=True,
    base=DiscoveryOrchestratorTask,
    name="app.tasks.discovery_celery_tasks.run_sweep_orchestrator_task",
    max_retries=3,
)
def run_sweep_orchestrator_task(
    self: DiscoveryOrchestratorTask, sweep_id: str, generation: int
) -> dict[str, Any]:
    return run_sweep_orchestrator(sweep_id, generation)
