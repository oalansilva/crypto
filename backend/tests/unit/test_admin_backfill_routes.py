from __future__ import annotations

from fastapi import HTTPException
import pytest

from app.routes import admin_backfill
from app.schemas.backfill import OhlcvBackfillStartRequest


class _FakeBackfillService:
    def __init__(self, *, start_job_returns_job_id: bool = True):
        self.start_job_returns_job_id = start_job_returns_job_id
        self.jobs = {
            "job-1": {
                "job_id": "job-1",
                "symbol": "BTC/USDT",
                "timeframes": ["1d"],
                "status": "running",
                "processed": 10,
                "written": 4,
                "duplicates": 1,
                "attempts": 0,
                "estimated_total": 10,
                "total_estimate": 10,
                "percent": 40.0,
                "eta_seconds": 120.0,
                "requested_window": {
                    "start": "2026-01-01T00:00:00+00:00",
                    "end": "2026-01-02T00:00:00+00:00",
                },
                "provider": "ccxt",
                "requested_source": None,
                "page_size": 1000,
                "max_requests_per_minute": 60,
                "last_error": None,
                "created_at": "2026-01-01T00:00:00+00:00",
                "started_at": "2026-01-01T01:00:00+00:00",
                "updated_at": "2026-01-01T01:00:00+00:00",
                "finished_at": None,
                "current_timeframe": "1d",
                "current_lookback_to": None,
                "timeframe_states": {"1d": {"status": "running"}},
                "events": [],
            }
        }
        self.last_status = None
        self.start_count = 0

    def list_jobs(self, page=1, page_size=20, status=None, symbol=None):
        filtered = [
            job
            for job in self.jobs.values()
            if (status is None or job["status"] == status)
            and (symbol is None or job["symbol"] == symbol)
        ]
        return filtered[(page - 1) * page_size : page * page_size], len(filtered)

    def get_job(self, job_id):
        if job_id == "missing":
            return None
        return self.jobs.get(job_id)

    def start_job(self, *, symbol: str, timeframes: list[str], **kwargs):
        self.start_count += 1
        job_id = "job-1" if self.start_job_returns_job_id else "job-missing"
        self.last_status = {"symbol": symbol, "timeframes": timeframes, **kwargs}
        if self.start_job_returns_job_id:
            return job_id
        return "job-error"

    def request_cancel_job(self, job_id):
        if job_id != "job-1":
            return False
        self.last_status = {"action": "cancel", "job_id": job_id}
        return True

    def request_retry_job(self, job_id):
        if job_id != "job-1":
            return False
        self.last_status = {"action": "retry", "job_id": job_id}
        return True

    def run_scheduler_once(self):
        return 2


def test_admin_backfill_list_and_detail_routes(monkeypatch):
    service = _FakeBackfillService()
    monkeypatch.setattr(admin_backfill, "get_backfill_service", lambda: service)

    listed = admin_backfill.list_backfill_jobs(
        status="running", symbol="BTC/USDT", _admin_user_id="admin"
    )
    assert listed["total"] == 1
    assert listed["items"][0]["job_id"] == "job-1"

    details = admin_backfill.get_backfill_job("job-1", _admin_user_id="admin")
    assert details["symbol"] == "BTC/USDT"
    assert details["status"] == "running"

    with pytest.raises(HTTPException) as exc:
        admin_backfill.get_backfill_job("missing", _admin_user_id="admin")
    assert exc.value.status_code == 404


def test_admin_backfill_create_and_action_routes(monkeypatch):
    service = _FakeBackfillService()
    monkeypatch.setattr(admin_backfill, "get_backfill_service", lambda: service)

    payload = OhlcvBackfillStartRequest(
        symbol="btc/usdt",
        timeframes=["1d", "1h", "1h"],
        history_window_years=2,
        page_size=500,
        max_requests_per_minute=120,
    )
    created = admin_backfill.start_backfill_job(payload, _admin_user_id="admin")
    assert created["job_id"] == "job-1"
    assert service.start_count == 1
    assert service.last_status["symbol"] == "BTC/USDT"
    assert service.last_status["timeframes"] == ["1d", "1h"]
    assert service.last_status["max_requests_per_minute"] == 120

    cancelled = admin_backfill.cancel_backfill_job("job-1", _admin_user_id="admin")
    assert cancelled == {"success": True, "job_id": "job-1"}

    retried = admin_backfill.retry_backfill_job("job-1", _admin_user_id="admin")
    assert retried == {"success": True, "job_id": "job-1"}

    assert admin_backfill.run_backfill_scheduler_now(_admin_user_id="admin") == {"started": 2}


def test_admin_backfill_create_returns_500_when_job_not_found(monkeypatch):
    service = _FakeBackfillService(start_job_returns_job_id=False)
    monkeypatch.setattr(admin_backfill, "get_backfill_service", lambda: service)
    payload = OhlcvBackfillStartRequest(symbol="BTC/USDT")
    with pytest.raises(HTTPException) as exc:
        admin_backfill.start_backfill_job(payload, _admin_user_id="admin")
    assert exc.value.status_code == 500
