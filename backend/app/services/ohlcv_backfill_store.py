from __future__ import annotations

import copy
import json
import logging
import threading
from datetime import UTC, datetime
from functools import lru_cache
from typing import Any, Iterable

from redis.exceptions import RedisError

from app.config import get_settings
from app.services.redis_store import get_redis_client

logger = logging.getLogger(__name__)

_MEMORY_LOCK = threading.Lock()
_MEMORY_JOBS: dict[str, dict[str, Any]] = {}
_MEMORY_JOBS_LIST: list[str] = []

JOB_KEY_PREFIX = "ohlcv_backfill:job:"
JOB_LIST_KEY = "ohlcv_backfill:jobs"
_MAX_JOBS = 1000


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _job_key(job_id: str) -> str:
    return f"{JOB_KEY_PREFIX}{job_id}"


def _to_int(value: Any, *, default: int | None = None) -> int | None:
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_float(value: Any, *, default: float | None = None) -> float | None:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _estimate_eta_seconds(
    started_at: str | None, processed: int, estimated_total: int | None
) -> float | None:
    if not processed or processed <= 0:
        return None
    if not estimated_total or estimated_total <= 0:
        return None
    if not started_at:
        return None

    try:
        started = datetime.fromisoformat(started_at)
    except Exception:
        return None

    if started.tzinfo is None:
        started = started.replace(tzinfo=UTC)
    elapsed = (datetime.now(UTC) - started).total_seconds()
    if elapsed <= 0:
        return None

    rate = processed / elapsed
    if rate <= 0:
        return None

    return round((estimated_total - processed) / rate, 3)


def _calculate_percent(processed: int, estimated_total: int | None) -> float:
    if not estimated_total or estimated_total <= 0:
        return 0.0
    ratio = max(0.0, min(processed / float(estimated_total), 1.0))
    return round(ratio * 100.0, 4)


def _coerce_job_for_response(job: dict[str, Any] | None) -> dict[str, Any] | None:
    if job is None:
        return None

    response = copy.deepcopy(job)
    estimated_total = _to_int(response.get("estimated_total"))
    processed = _to_int(response.get("processed"), default=0) or 0
    percent = _calculate_percent(processed, estimated_total)
    eta_seconds = response.get("eta_seconds")
    if eta_seconds is None:
        eta_seconds = _estimate_eta_seconds(response.get("started_at"), processed, estimated_total)

    response.update(
        {
            "estimated_total": estimated_total,
            "total_estimate": estimated_total,
            "percent": percent,
            "eta_seconds": eta_seconds,
        }
    )
    response.setdefault("events", [])
    response.setdefault("timeframe_states", {})
    response.setdefault("attempts", 0)
    response.setdefault("cancel_requested", False)
    return response


def _deepcopy(value: dict[str, Any] | None) -> dict[str, Any] | None:
    if value is None:
        return None
    return copy.deepcopy(value)


def _default_timeframe_state(
    timeframe: str,
    checkpoint: str,
    estimated_total: int | None,
) -> dict[str, Any]:
    return {
        "timeframe": timeframe,
        "status": "pending",
        "checkpoint": checkpoint,
        "processed": 0,
        "written": 0,
        "duplicates": 0,
        "requests": 0,
        "errors": 0,
        "retries": 0,
        "estimated_total": estimated_total,
        "latest_ingested": None,
    }


def _default_job_state(
    job_id: str,
    symbol: str,
    timeframes_state: dict[str, dict[str, Any]],
    requested_window: dict[str, Any],
    provider: str,
) -> dict[str, Any]:
    estimated_total = (
        sum(int(state.get("estimated_total") or 0) for state in timeframes_state.values()) or None
    )

    return {
        "job_id": job_id,
        "symbol": symbol,
        "timeframes": list(timeframes_state.keys()),
        "provider": provider,
        "status": "pending",
        "processed": 0,
        "written": 0,
        "duplicates": 0,
        "attempts": 0,
        "estimated_total": estimated_total,
        "total_estimate": estimated_total,
        "requested_window": requested_window,
        "timeframe_states": timeframes_state,
        "events": [],
        "current_timeframe": None,
        "current_lookback_to": None,
        "last_error": None,
        "created_at": _now_iso(),
        "started_at": None,
        "updated_at": _now_iso(),
        "finished_at": None,
        "cancel_requested": False,
        "dead_lettered": False,
        "percent": 0.0,
        "eta_seconds": None,
    }


def _coerce_jobs_response(jobs: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [job for job in (_coerce_job_for_response(job) or {} for job in jobs) if job]


class OhlcvBackfillStore:
    def __init__(self) -> None:
        settings = get_settings()
        self._ttl_seconds = settings.async_job_ttl_seconds
        self._redis = get_redis_client()

    def _load_list(self) -> list[str]:
        if self._redis is not None:
            try:
                raw = self._redis.lrange(JOB_LIST_KEY, 0, -1)
                return [str(value) for value in (raw or []) if str(value)]
            except RedisError as exc:
                logger.warning("Failed to load backfill job list from Redis: %s", exc)
                self._redis = None

        with _MEMORY_LOCK:
            return list(_MEMORY_JOBS_LIST)

    def _save_list(self, job_ids: list[str]) -> None:
        normalized = [job_id for job_id in job_ids if job_id]
        if self._redis is not None:
            try:
                pipe = self._redis.pipeline()
                pipe.delete(JOB_LIST_KEY)
                if normalized:
                    pipe.lpush(JOB_LIST_KEY, *normalized)
                    pipe.ltrim(JOB_LIST_KEY, 0, _MAX_JOBS - 1)
                pipe.expire(JOB_LIST_KEY, self._ttl_seconds)
                pipe.execute()
                return
            except RedisError as exc:
                logger.warning("Failed to persist backfill job list in Redis: %s", exc)
                self._redis = None

        with _MEMORY_LOCK:
            global _MEMORY_JOBS_LIST
            _MEMORY_JOBS_LIST = normalized[:_MAX_JOBS]

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        if self._redis is not None:
            try:
                raw = self._redis.get(_job_key(job_id))
                if raw is None:
                    return None
                return _coerce_job_for_response(
                    json.loads(raw) if isinstance(raw, str) else json.loads(str(raw))
                )
            except (RedisError, json.JSONDecodeError) as exc:
                logger.warning("Failed to get backfill job %s from Redis: %s", job_id, exc)
                self._redis = None

        with _MEMORY_LOCK:
            return _coerce_job_for_response(_MEMORY_JOBS.get(job_id))

    def save_job(self, job: dict[str, Any]) -> dict[str, Any]:
        global _MEMORY_JOBS_LIST
        payload = copy.deepcopy(job)
        payload["updated_at"] = _now_iso()
        payload["attempts"] = _to_int(payload.get("attempts"), default=0) or 0

        if self._redis is not None:
            try:
                serialized = json.dumps(payload)
                self._redis.setex(_job_key(payload["job_id"]), self._ttl_seconds, serialized)

                try:
                    self._redis.lrem(JOB_LIST_KEY, 0, payload["job_id"])
                    self._redis.lpush(JOB_LIST_KEY, payload["job_id"])
                    self._redis.ltrim(JOB_LIST_KEY, 0, _MAX_JOBS - 1)
                    self._redis.expire(JOB_LIST_KEY, self._ttl_seconds)
                except RedisError as exc:
                    logger.warning("Failed to update backfill job list in Redis: %s", exc)
                    self._redis = None
                if self._redis is None:
                    with _MEMORY_LOCK:
                        _MEMORY_JOBS[payload["job_id"]] = payload
                        _MEMORY_JOBS_LIST = [payload["job_id"]] + [
                            job_id for job_id in _MEMORY_JOBS_LIST if job_id != payload["job_id"]
                        ]
                        self._save_list(_MEMORY_JOBS_LIST)
                return _coerce_job_for_response(payload) or payload
            except (RedisError, TypeError) as exc:
                logger.warning(
                    "Failed to persist backfill job %s to Redis: %s", payload.get("job_id"), exc
                )
                self._redis = None

        with _MEMORY_LOCK:
            _MEMORY_JOBS[payload["job_id"]] = copy.deepcopy(payload)
            _MEMORY_JOBS_LIST = [
                payload["job_id"],
                *(item for item in _MEMORY_JOBS_LIST if item != payload["job_id"]),
            ]
            _MEMORY_JOBS_LIST = _MEMORY_JOBS_LIST[:_MAX_JOBS]
            return _coerce_job_for_response(payload) or payload

    def init_job(self, job: dict[str, Any]) -> dict[str, Any]:
        existing = self.get_job(job["job_id"])
        if existing is not None:
            return existing
        return self.save_job(job)

    def update_job(self, job_id: str, **changes: Any) -> dict[str, Any] | None:
        job = self.get_job(job_id)
        if job is None:
            return None
        payload = copy.deepcopy(job)
        payload.update(changes)
        payload.pop("percent", None)
        payload.pop("total_estimate", None)
        payload.pop("eta_seconds", None)
        return self.save_job(payload)

    def list_jobs(
        self,
        *,
        status_filter: str | None = None,
        symbol_filter: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[dict[str, Any]], int]:
        job_ids = self._load_list()
        seen: set[str] = set()
        jobs: list[dict[str, Any]] = []

        for job_id in job_ids:
            if not job_id or job_id in seen:
                continue
            seen.add(job_id)
            job = self.get_job(job_id)
            if not job:
                continue

            if status_filter and str(job.get("status")).strip().lower() != status_filter.lower():
                continue
            if symbol_filter and str(job.get("symbol", "")).upper() != str(symbol_filter).upper():
                continue
            jobs.append(job)

        total = len(jobs)
        offset = max(1, page) - 1
        size = max(1, min(100, page_size))
        start = offset * size
        end = start + size
        return jobs[start:end], total

    def exists_active_for_symbol(self, symbol: str) -> bool:
        target = str(symbol).upper()
        for job in self._iterate_jobs():
            if str(job.get("symbol", "")).upper() != target:
                continue
            if job.get("status") in {"pending", "running", "retrying"}:
                return True
        return False

    def _iterate_jobs(self) -> list[dict[str, Any]]:
        jobs: list[dict[str, Any]] = []
        for job_id in self._load_list():
            job = self.get_job(job_id)
            if job:
                jobs.append(job)
        return jobs

    def record_event(self, job_id: str, event: dict[str, Any], *, max_events: int = 60) -> None:
        job = self.get_job(job_id)
        if job is None:
            return

        events = list(job.get("events") or [])
        events.append(event)
        if len(events) > max_events:
            events = events[-max_events:]
        self.update_job(job_id, events=events)

    @staticmethod
    def calculate_percent(processed: int, estimated_total: int | None) -> float:
        return _calculate_percent(processed, estimated_total)

    @staticmethod
    def estimate_eta_seconds(
        started_at: str | None,
        processed: int,
        estimated_total: int | None,
    ) -> float | None:
        return _estimate_eta_seconds(started_at, processed, estimated_total)

    @staticmethod
    def normalize_status(status: str) -> str:
        return str(status or "pending").strip().lower()

    @staticmethod
    def build_timeframe_state(
        timeframe: str,
        checkpoint: str,
        estimated_total: int | None,
    ) -> dict[str, Any]:
        return _default_timeframe_state(timeframe, checkpoint, estimated_total)


@lru_cache()
def get_backfill_store() -> OhlcvBackfillStore:
    return OhlcvBackfillStore()
