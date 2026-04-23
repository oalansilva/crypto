from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.middleware.authMiddleware import get_current_admin
from app.schemas.backfill import (
    OhlcvBackfillJobResponse,
    OhlcvBackfillListResponse,
    OhlcvBackfillStartRequest,
)
from app.services.ohlcv_backfill_service import get_backfill_service

router = APIRouter(prefix="/api/admin/backfill", tags=["admin-backfill"])


def _serialize_job(job: dict[str, Any]) -> OhlcvBackfillJobResponse:
    return OhlcvBackfillJobResponse(
        job_id=job.get("job_id"),
        symbol=job.get("symbol"),
        timeframes=job.get("timeframes") or [],
        status=job.get("status", "pending"),
        processed=int(job.get("processed") or 0),
        written=int(job.get("written") or 0),
        duplicates=int(job.get("duplicates") or 0),
        attempts=int(job.get("attempts") or 0),
        estimated_total=job.get("estimated_total"),
        total_estimate=job.get("total_estimate"),
        percent=float(job.get("percent") or 0.0),
        eta_seconds=job.get("eta_seconds"),
        requested_window=job.get("requested_window", {}),
        provider=job.get("provider"),
        requested_source=job.get("requested_source"),
        page_size=int(job.get("page_size") or 0),
        max_requests_per_minute=int(job.get("max_requests_per_minute") or 0),
        last_error=job.get("last_error"),
        created_at=job.get("created_at"),
        started_at=job.get("started_at"),
        updated_at=job.get("updated_at"),
        finished_at=job.get("finished_at"),
        current_timeframe=job.get("current_timeframe"),
        current_lookback_to=job.get("current_lookback_to"),
        timeframe_states=job.get("timeframe_states") or {},
        events=job.get("events") or [],
    )


@router.get("/jobs", response_model=OhlcvBackfillListResponse)
def list_backfill_jobs(
    status: str | None = Query(default=None),
    symbol: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100, alias="pageSize"),
    _admin_user_id: str = Depends(get_current_admin),
):
    _ = _admin_user_id
    items, total = get_backfill_service().list_jobs(
        status=_normalize_status_filter(status),
        symbol=symbol,
        page=page,
        page_size=page_size,
    )
    return {
        "items": [_serialize_job(item) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/jobs/{job_id}", response_model=OhlcvBackfillJobResponse)
def get_backfill_job(job_id: str, _admin_user_id: str = Depends(get_current_admin)):
    _ = _admin_user_id
    job = get_backfill_service().get_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Backfill job not found")
    return _serialize_job(job)


@router.post("/jobs", response_model=OhlcvBackfillJobResponse, status_code=status.HTTP_201_CREATED)
def start_backfill_job(
    payload: OhlcvBackfillStartRequest,
    _admin_user_id: str = Depends(get_current_admin),
):
    _ = _admin_user_id
    service = get_backfill_service()
    job_id = service.start_job(
        symbol=payload.symbol,
        timeframes=payload.timeframes,
        data_source=payload.data_source,
        history_window_years=payload.history_window_years,
        page_size=payload.page_size,
        max_requests_per_minute=payload.max_requests_per_minute,
    )

    job = service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create backfill job")
    return _serialize_job(job)


@router.post("/jobs/{job_id}/cancel")
def cancel_backfill_job(
    job_id: str,
    _admin_user_id: str = Depends(get_current_admin),
):
    _ = _admin_user_id
    ok = get_backfill_service().request_cancel_job(job_id)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backfill job not found or cannot be cancelled in current state",
        )
    return {"success": True, "job_id": job_id}


@router.post("/jobs/{job_id}/retry")
def retry_backfill_job(
    job_id: str,
    _admin_user_id: str = Depends(get_current_admin),
):
    _ = _admin_user_id
    ok = get_backfill_service().request_retry_job(job_id)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backfill job not found or cannot be retried in current state",
        )
    return {"success": True, "job_id": job_id}


@router.post("/scheduler/run-now")
def run_backfill_scheduler_now(_admin_user_id: str = Depends(get_current_admin)):
    _ = _admin_user_id
    count = get_backfill_service().run_scheduler_once()
    return {"started": count}


def _normalize_status_filter(status: str | None) -> str | None:
    if not status:
        return None
    return status.strip().lower()

