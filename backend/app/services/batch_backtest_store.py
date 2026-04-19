from __future__ import annotations

import copy
import json
import logging
import threading
from datetime import UTC, datetime
from functools import lru_cache
from typing import Any

from redis.exceptions import RedisError

from app.config import get_settings
from app.services.redis_store import get_redis_client

logger = logging.getLogger(__name__)

_MEMORY_LOCK = threading.Lock()
_MEMORY_JOBS: dict[str, dict[str, Any]] = {}
_MEMORY_DEAD_LETTERS: list[dict[str, Any]] = []

JOB_KEY_PREFIX = "batch_backtest:job:"
DEAD_LETTER_KEY = "batch_backtest:dead_letters"


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _job_key(job_id: str) -> str:
    return f"{JOB_KEY_PREFIX}{job_id}"


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


class BatchBacktestStore:
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


@lru_cache()
def get_batch_backtest_store() -> BatchBacktestStore:
    return BatchBacktestStore()
