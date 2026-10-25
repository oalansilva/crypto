"""Estado do lote de backtests (cards #1120 e anteriores).

O estado dos lotes novos vive no PostgreSQL (``batch_backtest_jobs`` e ``batch_backtest_items``,
decisão 10 do #1120): sem prazo enquanto o lote está pausado, por ativo, e lido pela API e pelo
worker do Celery. O Redis fica só como fila do Celery.

Lotes que já estavam no Redis (ou na memória, sem Redis) na hora do deploy terminam no caminho
antigo: ``get_job`` e ``update_job`` caem no armazém antigo quando o lote não está no PostgreSQL, e
o painel lê os dois formatos (``items`` ausente = painel antigo).
"""

from __future__ import annotations

import copy
import json
import logging
import threading
from datetime import UTC, datetime
from functools import lru_cache
from typing import Any, Iterable

from redis.exceptions import RedisError
from sqlalchemy import and_, or_

from app.config import get_settings
from app.models_batch_backtest import (
    ITEM_FINAL_STATES,
    JOB_ACTIVE_STATUSES,
    BatchBacktestItem,
    BatchBacktestJob,
)
from app.services.redis_store import get_redis_client

logger = logging.getLogger(__name__)

_MEMORY_LOCK = threading.Lock()
_MEMORY_JOBS: dict[str, dict[str, Any]] = {}
_MEMORY_DEAD_LETTERS: list[dict[str, Any]] = []

JOB_KEY_PREFIX = "batch_backtest:job:"
DEAD_LETTER_KEY = "batch_backtest:dead_letters"

ITEM_STATES = (
    "queued",
    "collecting",
    "optimizing",
    "success",
    "success_daily",
    "insufficient",
    "rejected",
    "failed",
    "skipped",
    "out",
    "not_run",
)

_JOB_COLUMNS = {c.name for c in BatchBacktestJob.__table__.columns}
_ITEM_COLUMNS = {c.name for c in BatchBacktestItem.__table__.columns}
_DATETIME_FIELDS = {"started_at", "finished_at"}


def utcnow_naive() -> datetime:
    return _utcnow()


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _utcnow() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def _job_key(job_id: str) -> str:
    return f"{JOB_KEY_PREFIX}{job_id}"


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _parse_dt(value: Any) -> datetime | None:
    if value is None or isinstance(value, datetime):
        return value
    text = str(value)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed.astimezone(UTC).replace(tzinfo=None) if parsed.tzinfo else parsed


def _deepcopy(data: dict[str, Any] | None) -> dict[str, Any] | None:
    if data is None:
        return None
    return copy.deepcopy(data)


def _default_job_state(job_id: str, total: int) -> dict[str, Any]:
    return {
        "job_id": job_id,
        "task_id": None,
        "status": "queued",
        "processed": 0,
        "total": total,
        "succeeded": 0,
        "failed": 0,
        "skipped": 0,
        "errors": [],
        "started_at": None,
        "elapsed_sec": 0.0,
        "estimated_remaining_sec": None,
        "current_symbol": None,
        "cancel_requested": False,
        "pause_requested": False,
        "retry_count": 0,
        "last_error": None,
        "dead_lettered": False,
        "updated_at": _now_iso(),
    }


class LegacyBatchStore:
    """Armazém antigo (Redis com prazo, ou memória): só lotes anteriores ao #1120."""

    def __init__(self) -> None:
        settings = get_settings()
        self._ttl_seconds = settings.async_job_ttl_seconds
        self._dead_letter_max_items = settings.async_dead_letter_max_items
        self._redis = get_redis_client()

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        if self._redis is not None:
            try:
                payload = self._redis.get(_job_key(job_id))
                if payload is None:
                    return None
                return json.loads(payload)
            except (RedisError, json.JSONDecodeError) as exc:
                logger.warning("Failed to load batch job %s from Redis: %s", job_id, exc)
                self._redis = None

        with _MEMORY_LOCK:
            return _deepcopy(_MEMORY_JOBS.get(job_id))

    def save_job(self, job: dict[str, Any]) -> dict[str, Any]:
        stored = copy.deepcopy(job)
        stored["updated_at"] = _now_iso()

        if self._redis is not None:
            try:
                self._redis.setex(_job_key(stored["job_id"]), self._ttl_seconds, json.dumps(stored))
                return stored
            except (RedisError, TypeError) as exc:
                logger.warning("Failed to persist batch job %s to Redis: %s", stored["job_id"], exc)
                self._redis = None

        with _MEMORY_LOCK:
            _MEMORY_JOBS[stored["job_id"]] = stored
        return copy.deepcopy(stored)

    def init_job(self, job_id: str, total: int) -> dict[str, Any]:
        existing = self.get_job(job_id)
        if existing is not None:
            return existing
        return self.save_job(_default_job_state(job_id, total))

    def update_job(self, job_id: str, **changes: Any) -> dict[str, Any] | None:
        job = self.get_job(job_id)
        if job is None:
            return None
        job.update(changes)
        return self.save_job(job)

    def record_dead_letter(
        self,
        *,
        job_id: str,
        task_id: str | None,
        payload: dict[str, Any],
        reason: str,
        retry_count: int,
    ) -> None:
        entry = {
            "job_id": job_id,
            "task_id": task_id,
            "reason": reason,
            "retry_count": retry_count,
            "payload": payload,
            "recorded_at": _now_iso(),
        }

        if self._redis is not None:
            try:
                pipe = self._redis.pipeline()
                pipe.lpush(DEAD_LETTER_KEY, json.dumps(entry))
                pipe.ltrim(DEAD_LETTER_KEY, 0, self._dead_letter_max_items - 1)
                pipe.expire(DEAD_LETTER_KEY, self._ttl_seconds)
                pipe.execute()
                return
            except (RedisError, TypeError) as exc:
                logger.warning("Failed to persist dead letter for job %s: %s", job_id, exc)
                self._redis = None

        with _MEMORY_LOCK:
            _MEMORY_DEAD_LETTERS.insert(0, entry)
            del _MEMORY_DEAD_LETTERS[self._dead_letter_max_items :]


def _job_to_dict(row: BatchBacktestJob) -> dict[str, Any]:
    return {
        "job_id": row.job_id,
        "user_id": row.user_id,
        "task_id": row.task_id,
        "status": row.status,
        "payload": row.payload,
        "plan": row.plan,
        "total": row.total or 0,
        "processed": row.processed or 0,
        "succeeded": row.succeeded or 0,
        "failed": row.failed or 0,
        "skipped": row.skipped or 0,
        "errors": list(row.errors or []),
        "skipped_reasons": list(row.skipped_reasons or []),
        "started_at": _iso(row.started_at),
        "finished_at": _iso(row.finished_at),
        "elapsed_sec": float(row.elapsed_sec or 0.0),
        "estimated_remaining_sec": row.estimated_remaining_sec,
        "current_symbol": row.current_symbol,
        "current_stage": row.current_stage,
        "cancel_requested": bool(row.cancel_requested),
        "pause_requested": bool(row.pause_requested),
        "retry_count": row.retry_count or 0,
        "last_error": row.last_error,
        "dead_lettered": bool(row.dead_lettered),
        "created_at": _iso(row.created_at),
        "updated_at": _iso(row.updated_at),
    }


def _item_to_dict(row: BatchBacktestItem) -> dict[str, Any]:
    return {
        "position": row.position,
        "symbol": row.symbol,
        "asset_class": row.asset_class,
        "currency": row.currency,
        "state": row.state,
        "reason": row.reason,
        "progress": row.progress,
        "favorite_id": row.favorite_id,
        "execution": row.execution,
        "snapshot_id": row.snapshot_id,
        "extra": row.extra or {},
        "started_at": _iso(row.started_at),
        "finished_at": _iso(row.finished_at),
    }


def totals_by_state(items: Iterable[dict[str, Any]]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for item in items:
        totals[item["state"]] = totals.get(item["state"], 0) + 1
    return totals


def _coerce(changes: dict[str, Any], allowed: set[str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in changes.items():
        if key not in allowed:
            continue
        out[key] = _parse_dt(value) if key in _DATETIME_FIELDS else value
    return out


class BatchBacktestStore:
    """PostgreSQL: um lote por linha, um ativo por linha; pedidos de pausa e encerramento atômicos."""

    def __init__(self, session_factory: Any = None) -> None:
        self._session_factory = session_factory
        self._legacy_store: LegacyBatchStore | None = None

    # -- infraestrutura ------------------------------------------------------------------

    def _session(self):
        if self._session_factory is not None:
            return self._session_factory()
        from app.database import SessionLocal

        return SessionLocal()

    @property
    def _legacy(self) -> LegacyBatchStore:
        if self._legacy_store is None:
            self._legacy_store = LegacyBatchStore()
        return self._legacy_store

    def is_durable(self, job_id: str) -> bool:
        with self._session() as db:
            return db.get(BatchBacktestJob, job_id) is not None

    # -- criação -------------------------------------------------------------------------

    def create_job(
        self,
        job_id: str,
        *,
        user_id: str | None,
        payload: dict[str, Any] | None,
        plan: dict[str, Any] | None,
        items: list[dict[str, Any]],
        total: int | None = None,
    ) -> dict[str, Any]:
        now = _utcnow()
        with self._session() as db:
            job = BatchBacktestJob(
                job_id=job_id,
                user_id=user_id,
                status="queued",
                payload=payload,
                plan=plan,
                total=(
                    sum(1 for i in items if (i.get("state") or "queued") != "out")
                    if total is None
                    else total
                ),
                processed=0,
                succeeded=0,
                failed=0,
                skipped=0,
                errors=[],
                skipped_reasons=[],
                pause_requested=False,
                cancel_requested=False,
                retry_count=0,
                dead_lettered=False,
                elapsed_sec=0.0,
                created_at=now,
                updated_at=now,
            )
            db.add(job)
            for position, spec in enumerate(items):
                state = spec.get("state") or "queued"
                db.add(
                    BatchBacktestItem(
                        job_id=job_id,
                        position=position,
                        symbol=spec["symbol"],
                        asset_class=spec.get("asset_class"),
                        currency=spec.get("currency"),
                        state=state,
                        reason=spec.get("reason"),
                        progress=spec.get("progress"),
                        extra=spec.get("extra") or {},
                        finished_at=now if state in ITEM_FINAL_STATES else None,
                    )
                )
            db.commit()
        return self.get_job(job_id, include_items=True) or {}

    def init_job(
        self,
        job_id: str,
        total: int,
        *,
        user_id: str | None = None,
        payload: dict[str, Any] | None = None,
        plan: dict[str, Any] | None = None,
        items: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Cria o lote (idempotente). Sem ``items``, o lote nasce só com o total."""

        existing = self.get_job(job_id)
        if existing is not None:
            return existing
        return self.create_job(
            job_id,
            user_id=user_id,
            payload=payload,
            plan=plan,
            items=items or [],
            total=total if not items else None,
        )

    # -- leitura -------------------------------------------------------------------------

    def get_job(self, job_id: str, *, include_items: bool = False) -> dict[str, Any] | None:
        with self._session() as db:
            row = db.get(BatchBacktestJob, job_id)
            if row is None:
                return self._legacy.get_job(job_id)
            job = _job_to_dict(row)
            if include_items:
                items = [
                    _item_to_dict(i)
                    for i in db.query(BatchBacktestItem)
                    .filter(BatchBacktestItem.job_id == job_id)
                    .order_by(BatchBacktestItem.position)
                    .all()
                ]
                job["items"] = items
                job["totals"] = totals_by_state(items)
            return job

    def list_items(self, job_id: str) -> list[dict[str, Any]]:
        with self._session() as db:
            return [
                _item_to_dict(i)
                for i in db.query(BatchBacktestItem)
                .filter(BatchBacktestItem.job_id == job_id)
                .order_by(BatchBacktestItem.position)
                .all()
            ]

    def active_job(
        self, user_id: str | None, *, include_items: bool = True
    ) -> dict[str, Any] | None:
        """O lote não final mais recente do usuário (rodando, na fila, em nova tentativa ou pausado)."""

        with self._session() as db:
            row = (
                db.query(BatchBacktestJob)
                .filter(
                    BatchBacktestJob.user_id == user_id,
                    BatchBacktestJob.status.in_(JOB_ACTIVE_STATUSES),
                )
                .order_by(BatchBacktestJob.created_at.desc(), BatchBacktestJob.job_id)
                .first()
            )
            job_id = row.job_id if row is not None else None
        return self.get_job(job_id, include_items=include_items) if job_id else None

    def paused_job(self, user_id: str | None) -> dict[str, Any] | None:
        with self._session() as db:
            row = (
                db.query(BatchBacktestJob)
                .filter(BatchBacktestJob.user_id == user_id, BatchBacktestJob.status == "paused")
                .order_by(BatchBacktestJob.created_at.desc())
                .first()
            )
            return _job_to_dict(row) if row is not None else None

    # -- escrita -------------------------------------------------------------------------

    def update_job(self, job_id: str, **changes: Any) -> dict[str, Any] | None:
        """Atualiza só as colunas informadas (sem reescrever os pedidos de pausa/encerramento)."""

        values = _coerce(changes, _JOB_COLUMNS - {"job_id", "created_at"})
        with self._session() as db:
            row = db.get(BatchBacktestJob, job_id)
            if row is None:
                legacy = self._legacy.get_job(job_id)
                if legacy is None:
                    return None
                return self._legacy.update_job(job_id, **changes)
            values["updated_at"] = _utcnow()
            db.query(BatchBacktestJob).filter(BatchBacktestJob.job_id == job_id).update(
                values, synchronize_session=False
            )
            db.commit()
        return self.get_job(job_id)

    def save_job(self, job: dict[str, Any]) -> dict[str, Any]:
        """Grava o andamento do lote; os pedidos de pausa e de encerramento nunca são regravados."""

        job_id = job["job_id"]
        if not self.is_durable(job_id):
            return self._legacy.save_job(job)
        # status, pedidos e dono só mudam por transição atômica ou por ``update_job`` explícito
        skip = {
            "job_id",
            "status",
            "pause_requested",
            "cancel_requested",
            "task_id",
            "user_id",
            "payload",
            "plan",
        }
        self.update_job(job_id, **{k: v for k, v in job.items() if k not in skip})
        return self.get_job(job_id) or job

    def update_item(self, job_id: str, position: int, **changes: Any) -> None:
        values = _coerce(changes, _ITEM_COLUMNS - {"id", "job_id", "position"})
        if not values:
            return
        with self._session() as db:
            db.query(BatchBacktestItem).filter(
                BatchBacktestItem.job_id == job_id, BatchBacktestItem.position == position
            ).update(values, synchronize_session=False)
            db.commit()

    # -- transições atômicas ---------------------------------------------------------------

    def claim(self, job_id: str, task_id: str | None) -> bool:
        """O worker assume o lote: só um por vez, e nunca um lote pausado ou final.

        Vale para ``queued`` e ``retrying`` e para a reentrega da mesma tarefa (worker perdido).
        """

        now = _utcnow()
        with self._session() as db:
            claimed = (
                db.query(BatchBacktestJob)
                .filter(
                    BatchBacktestJob.job_id == job_id,
                    or_(
                        BatchBacktestJob.status.in_(("queued", "retrying")),
                        and_(
                            BatchBacktestJob.status == "running",
                            BatchBacktestJob.task_id == task_id,
                        ),
                    ),
                )
                .update(
                    {"status": "running", "task_id": task_id, "updated_at": now},
                    synchronize_session=False,
                )
            )
            if claimed:
                # etapa interrompida por queda do worker volta à fila (o que já foi guardado fica)
                db.query(BatchBacktestItem).filter(
                    BatchBacktestItem.job_id == job_id,
                    BatchBacktestItem.state.in_(("collecting", "optimizing")),
                ).update({"state": "queued"}, synchronize_session=False)
            db.commit()
            return bool(claimed)

    def request_pause(self, job_id: str) -> bool:
        with self._session() as db:
            row = db.get(BatchBacktestJob, job_id)
            if row is None or row.status not in ("queued", "running", "retrying"):
                return False
            values: dict[str, Any] = {"pause_requested": True, "updated_at": _utcnow()}
            if row.status == "queued":
                values["status"] = "paused"
            db.query(BatchBacktestJob).filter(BatchBacktestJob.job_id == job_id).update(
                values, synchronize_session=False
            )
            db.commit()
            return True

    def request_cancel(self, job_id: str) -> bool:
        """Encerrar. Parado (na fila ou pausado) encerra na hora; rodando espera o fim da etapa."""

        now = _utcnow()
        with self._session() as db:
            row = db.get(BatchBacktestJob, job_id)
            if row is None or row.status not in ("queued", "running", "retrying", "paused"):
                return False
            if row.status in ("queued", "paused"):
                self._close_unfinished(db, job_id)
                db.query(BatchBacktestJob).filter(BatchBacktestJob.job_id == job_id).update(
                    {
                        "status": "cancelled",
                        "cancel_requested": True,
                        "pause_requested": False,
                        "estimated_remaining_sec": None,
                        "current_symbol": None,
                        "current_stage": None,
                        "finished_at": now,
                        "updated_at": now,
                    },
                    synchronize_session=False,
                )
                self._refresh_counters(db, job_id)
            else:
                db.query(BatchBacktestJob).filter(BatchBacktestJob.job_id == job_id).update(
                    {"cancel_requested": True, "updated_at": now}, synchronize_session=False
                )
            db.commit()
            return True

    def request_resume(self, job_id: str) -> bool:
        """Pausado volta à fila no mesmo lote; o pedido de pausa é desfeito."""

        with self._session() as db:
            changed = (
                db.query(BatchBacktestJob)
                .filter(BatchBacktestJob.job_id == job_id, BatchBacktestJob.status == "paused")
                .update(
                    {
                        "status": "queued",
                        "pause_requested": False,
                        "updated_at": _utcnow(),
                        "current_stage": None,
                    },
                    synchronize_session=False,
                )
            )
            db.commit()
            return bool(changed)

    def finish_stop(self, job_id: str, *, cancelled: bool) -> None:
        """O worker chegou ao fim da etapa e para: pausa ou encerra o lote."""

        now = _utcnow()
        with self._session() as db:
            if cancelled:
                self._close_unfinished(db, job_id)
                values: dict[str, Any] = {
                    "status": "cancelled",
                    "finished_at": now,
                }
            else:
                values = {"status": "paused", "pause_requested": False}
            values.update(
                {
                    "estimated_remaining_sec": None,
                    "current_symbol": None,
                    "current_stage": None,
                    "updated_at": now,
                }
            )
            db.query(BatchBacktestJob).filter(BatchBacktestJob.job_id == job_id).update(
                values, synchronize_session=False
            )
            self._refresh_counters(db, job_id)
            db.commit()

    @staticmethod
    def _close_unfinished(db: Any, job_id: str) -> None:
        """Encerrar marca o resto "Não rodou"; o que já terminou e os favoritos ficam."""

        db.query(BatchBacktestItem).filter(
            BatchBacktestItem.job_id == job_id,
            BatchBacktestItem.state.in_(("queued", "collecting", "optimizing")),
        ).update(
            {
                "state": "not_run",
                "reason": "lote encerrado antes",
                "progress": None,
                "finished_at": _utcnow(),
            },
            synchronize_session=False,
        )

    @staticmethod
    def _refresh_counters(db: Any, job_id: str) -> None:
        states = [
            s
            for (s,) in db.query(BatchBacktestItem.state)
            .filter(BatchBacktestItem.job_id == job_id)
            .all()
        ]
        processed = sum(1 for s in states if s in ITEM_FINAL_STATES and s != "out")
        db.query(BatchBacktestJob).filter(BatchBacktestJob.job_id == job_id).update(
            {
                "processed": processed,
                "succeeded": sum(1 for s in states if s in ("success", "success_daily")),
                "failed": sum(1 for s in states if s == "failed"),
                "skipped": sum(1 for s in states if s in ("skipped", "rejected")),
            },
            synchronize_session=False,
        )

    def refresh_counters(self, job_id: str) -> None:
        with self._session() as db:
            self._refresh_counters(db, job_id)
            db.commit()

    # -- fila morta ----------------------------------------------------------------------

    def record_dead_letter(self, **kwargs: Any) -> None:
        """Lote durável: a linha do lote já guarda corpo, erro e ``dead_lettered`` (Redis só é fila)."""

        if self.is_durable(str(kwargs.get("job_id"))):
            return
        self._legacy.record_dead_letter(**kwargs)


@lru_cache()
def get_batch_backtest_store() -> BatchBacktestStore:
    return BatchBacktestStore()
