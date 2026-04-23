from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pandas as pd
from requests.exceptions import RequestException

from app.services.market_data_providers import CCXT_SOURCE, STOOQ_SOURCE
from app.services.ohlcv_backfill_service import (
    OhlcvBackfillService,
    _coerce_status,
    _estimate_total_for_range,
    _is_retriable_error,
    _normalize_timeframes,
    _parse_int,
    _parse_iso,
)
import app.services.ohlcv_backfill_service as backfill_service_module
from app.services.ohlcv_backfill_store import _default_job_state, _default_timeframe_state


class _FakeRepo:
    def __init__(self, enabled: bool = True, earliest=None):
        self.enabled = enabled
        self.earliest = earliest
        self.write_calls = 0

    def get_earliest_candle_time(self, _symbol: str, _timeframe: str):
        return self.earliest

    def write_candles(self, *_args, **_kwargs):
        self.write_calls += 1
        return (1, 0)


class _FakeThread:
    def __init__(self, *_, **__):
        pass

    def start(self):
        return None


class _FakeStore:
    def __init__(self):
        self.jobs: dict[str, dict] = {}
        self.events: list[tuple[str, dict]] = []

    def get_job(self, job_id):
        job = self.jobs.get(job_id)
        if job is None:
            return None
        return {**job}

    def save_job(self, job: dict):
        payload = {**job}
        self.jobs[payload["job_id"]] = payload
        return payload

    def init_job(self, job):
        if self.jobs.get(job["job_id"]) is not None:
            return {**self.jobs[job["job_id"]]}
        self.jobs[job["job_id"]] = {**job}
        return {**job}

    def update_job(self, job_id: str, **changes):
        job = self.jobs.get(job_id)
        if job is None:
            return None
        payload = {**job}
        payload.update(changes)
        payload.pop("percent", None)
        payload.pop("total_estimate", None)
        payload.pop("eta_seconds", None)
        self.jobs[job_id] = payload
        return {**payload}

    def list_jobs(
        self,
        page: int = 1,
        page_size: int = 50,
        status_filter: str | None = None,
        symbol_filter: str | None = None,
    ):
        filtered = [
            job
            for job in self.jobs.values()
            if (status_filter is None or job.get("status") == status_filter)
            and (symbol_filter is None or job.get("symbol") == symbol_filter)
        ]
        offset = (page - 1) * page_size
        return filtered[offset : offset + page_size], len(filtered)

    def exists_active_for_symbol(self, symbol):
        target = str(symbol).upper()
        for job in self.jobs.values():
            if job.get("symbol") != target:
                continue
            if job.get("status") in {"pending", "running", "retrying"}:
                return True
        return False

    def record_event(self, job_id: str, event: dict, *, max_events: int = 60):
        if job_id == "":
            return
        self.events.append((job_id, event))
        job = self.jobs.get(job_id)
        if job is None:
            return
        events = list(job.get("events", []))
        events.append(event)
        if len(events) > max_events:
            events = events[-max_events:]
        job["events"] = events
        self.jobs[job_id] = job

    @staticmethod
    def calculate_percent(processed: int, estimated_total: int | None) -> float:
        if not estimated_total:
            return 0.0
        return round(min(processed / float(estimated_total), 1.0) * 100, 4)

    @staticmethod
    def estimate_eta_seconds(started_at: str | None, processed: int, estimated_total: int | None):
        if not started_at or not estimated_total or processed <= 0:
            return None
        return 20.0

    @staticmethod
    def build_timeframe_state(timeframe, checkpoint, estimated_total):
        return _default_timeframe_state(timeframe, checkpoint, estimated_total)


def _new_service(monkeypatch) -> OhlcvBackfillService:
    store = _FakeStore()
    monkeypatch.setattr(backfill_service_module, "get_backfill_store", lambda: store)
    backfill_service_module.OhlcvBackfillService._instance = None
    service = OhlcvBackfillService()
    service._store = store
    return service


def test_backfill_service_helpers_and_formatters():
    assert _normalize_timeframes([" 1m ", "1m", "15m", "bad"]) == ["1m", "15m"]
    assert _normalize_timeframes([]) == ["1d"]
    assert _parse_int("12", default=0) == 12
    assert _parse_int("x", default=7) == 7
    assert _coerce_status(None) == "pending"
    assert (
        _estimate_total_for_range(
            datetime(2026, 1, 1, tzinfo=UTC), datetime(2026, 1, 2, tzinfo=UTC), "1d"
        )
        > 0
    )
    assert _is_retriable_error(RequestException("timeout from exchange")) is True
    assert _is_retriable_error(Exception("boom")) is False
    assert _parse_iso("2026-01-01T00:00:00") is not None


def test_fetch_with_retries_supports_retry(monkeypatch):
    service = _new_service(monkeypatch)
    service._store.record_event = lambda *args, **kwargs: None
    monkeypatch.setattr(backfill_service_module.time, "sleep", lambda *_args, **_kwargs: None)

    calls = {"count": 0}

    class _Provider:
        def fetch_ohlcv(self, **_kwargs):
            calls["count"] += 1
            if calls["count"] == 1:
                raise RequestException("timeout from provider")
            return pd.DataFrame({"timestamp_utc": [datetime(2026, 1, 1, tzinfo=UTC)]})

    state: dict[str, int] = {"retries": 0}
    provider = _Provider()
    frame = service._fetch_with_retries(
        provider=provider,
        symbol="BTC/USDT",
        timeframe="1d",
        since=datetime(2026, 1, 1, tzinfo=UTC),
        until=datetime(2026, 1, 2, tzinfo=UTC),
        limit=1000,
        max_requests_per_minute=60,
        max_retries=2,
        job_id="job-1",
        timeframe_state=state,
    )
    assert not frame.empty
    assert state["retries"] == 1
    assert calls["count"] == 2


def test_run_timeframe_backfill_stooq_short_circuit(monkeypatch):
    service = _new_service(monkeypatch)
    service._repo = _FakeRepo()
    now = datetime(2026, 1, 1, tzinfo=UTC)
    service._store.save_job(
        _default_job_state(
            job_id="job-stooq",
            symbol="BTC/USDT",
            timeframes_state={
                "1h": _default_timeframe_state("1h", now.isoformat(), 2),
            },
            requested_window={
                "start": now.isoformat(),
                "end": (now + timedelta(days=1)).isoformat(),
            },
            provider=STOOQ_SOURCE,
        )
    )

    assert service._run_timeframe_backfill("job-stooq", "1h", STOOQ_SOURCE) is True
    updated = service._store.get_job("job-stooq")
    assert updated["timeframe_states"]["1h"]["status"] == "completed"


def test_run_timeframe_backfill_empty_result_becomes_partial(monkeypatch):
    service = _new_service(monkeypatch)
    service._repo = _FakeRepo()
    now = datetime(2026, 1, 1, tzinfo=UTC)
    service._store.save_job(
        _default_job_state(
            job_id="job-empty",
            symbol="ETH/USDT",
            timeframes_state={
                "1h": _default_timeframe_state("1h", now.isoformat(), 2),
            },
            requested_window={
                "start": now.isoformat(),
                "end": (now + timedelta(days=1)).isoformat(),
            },
            provider=CCXT_SOURCE,
        )
    )

    monkeypatch.setattr(
        backfill_service_module,
        "get_market_data_provider",
        lambda *_: type(
            "provider",
            (),
            {"source": CCXT_SOURCE, "fetch_ohlcv": lambda **_: pd.DataFrame()},
        )(),
    )
    assert service._run_timeframe_backfill("job-empty", "1h", CCXT_SOURCE) is False
    updated = service._store.get_job("job-empty")
    assert updated["timeframe_states"]["1h"]["status"] == "partial_complete"


def test_run_timeframe_backfill_completes_with_data(monkeypatch):
    service = _new_service(monkeypatch)
    service._repo = _FakeRepo()
    now = datetime(2026, 1, 1, tzinfo=UTC)
    end = now + timedelta(days=1)
    service._store.save_job(
        _default_job_state(
            job_id="job-data",
            symbol="ETH/USDT",
            timeframes_state={
                "1d": _default_timeframe_state("1d", now.isoformat(), 2),
            },
            requested_window={"start": now.isoformat(), "end": end.isoformat()},
            provider=CCXT_SOURCE,
        )
    )
    service._store.update_job("job-data", page_size=1)

    provider_df = pd.DataFrame(
        {
            "timestamp_utc": [end],
            "open": [1.0],
            "high": [1.1],
            "low": [0.9],
            "close": [1.0],
        }
    )

    class _Provider:
        source = CCXT_SOURCE

        def fetch_ohlcv(self, **_kwargs):
            return provider_df

    monkeypatch.setattr(backfill_service_module, "get_market_data_provider", lambda *_: _Provider())
    assert service._run_timeframe_backfill("job-data", "1d", CCXT_SOURCE) is True
    updated = service._store.get_job("job-data")
    assert updated["timeframe_states"]["1d"]["status"] == "completed"
    assert updated["timeframe_states"]["1d"]["written"] == 1


def test_run_job_completes_and_fails(monkeypatch):
    service = _new_service(monkeypatch)
    now = datetime(2026, 1, 1, tzinfo=UTC)
    service._store.save_job(
        _default_job_state(
            job_id="job-run",
            symbol="BTC/USDT",
            timeframes_state={
                "1d": _default_timeframe_state("1d", now.isoformat(), 2),
                "1h": _default_timeframe_state("1h", now.isoformat(), 2),
            },
            requested_window={
                "start": now.isoformat(),
                "end": (now + timedelta(days=1)).isoformat(),
            },
            provider=CCXT_SOURCE,
        )
    )

    def _complete(job_id, timeframe, source):
        state = service._store.get_job(job_id)["timeframe_states"][timeframe]
        state["status"] = "completed"
        states = service._store.get_job(job_id)["timeframe_states"]
        states[timeframe] = state
        service._store.update_job(job_id, timeframe_states=states)
        return True

    monkeypatch.setattr(service, "_run_timeframe_backfill", _complete)
    monkeypatch.setattr(service, "_resolve_job_source", lambda *_args, **_kwargs: CCXT_SOURCE)
    service._run_job("job-run")
    final = service._store.get_job("job-run")
    assert final["status"] == "completed"

    service._store.update_job("job-run", status="pending")
    service._store.update_job(
        "job-run",
        timeframe_states={
            "1d": {"status": "failed", "checkpoint": now.isoformat()},
            "1h": {"status": "pending", "checkpoint": now.isoformat()},
        },
    )

    def _fail(job_id, timeframe, source):
        states = service._store.get_job(job_id)["timeframe_states"]
        states[timeframe]["status"] = "failed"
        service._store.update_job(job_id, timeframe_states=states)
        return False

    monkeypatch.setattr(service, "_run_timeframe_backfill", _fail)
    service._run_job("job-run")
    final_failed = service._store.get_job("job-run")
    assert final_failed["status"] == "failed"


def test_start_job_controls_and_scheduler(monkeypatch):
    service = _new_service(monkeypatch)
    monkeypatch.setattr(backfill_service_module.threading, "Thread", _FakeThread)
    job_id = service.start_job("btc/usdt", ["1d"], history_window_years=2, page_size=10)

    assert job_id.startswith("backfill-")
    assert service._store.get_job(job_id) is not None

    assert service.request_cancel_job(job_id) is True
    assert service._store.get_job(job_id)["status"] == "cancelled"

    service._store.update_job(job_id, status="pending")
    service._store.update_job(job_id, status="failed")
    assert service.request_retry_job(job_id) is True
    retried = service._store.get_job(job_id)
    assert retried["status"] == "retrying"
    assert retried["attempts"] == 1

    service._repo = _FakeRepo(earliest=None)
    service._store.exists_active_for_symbol = lambda *_: False
    started = []

    def _start_job(**kwargs):
        started.append(kwargs)
        return "scheduler-" + kwargs["symbol"].lower().replace("/", "")

    monkeypatch.setattr(service, "start_job", _start_job)
    monkeypatch.setenv("BACKFILL_SCHEDULER_ENABLED", "1")
    monkeypatch.setenv("BACKFILL_SCHEDULER_SYMBOLS", "BTC/USDT")
    monkeypatch.setenv("BACKFILL_SCHEDULER_TIMEFRAMES", "1d")
    monkeypatch.setenv("BACKFILL_WINDOW_YEARS", "2")
    assert service.run_scheduler_once() == 1
    assert started == [
        {"symbol": "BTC/USDT", "timeframes": ["1d"], "data_source": None, "history_window_years": 2}
    ]

    monkeypatch.setenv("BACKFILL_SCHEDULER_ENABLED", "0")
    assert service.run_scheduler_once() == 0
