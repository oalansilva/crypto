from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.middleware.authMiddleware import get_current_admin
from app.services.market_indicator_service import get_market_indicator_service

router = APIRouter(prefix="/api/admin/indicators", tags=["admin-indicators"])


class IndicatorRecomputeRequest(BaseModel):
    symbol: str
    timeframes: list[str] | None = None
    force_full: bool = Field(default=False, alias="forceFull")


class IndicatorRecomputeResponse(BaseModel):
    status: str
    job_id: str
    symbol: str
    timeframes: list[str]
    estimated_bars: int


class IndicatorRecomputeJobResponse(BaseModel):
    status: str
    job_id: str
    symbol: str
    timeframes: list[str]
    force_full: bool
    estimated_bars: int
    estimated_bars_remaining: int
    processed_timeframes: int
    created_at: str | None
    started_at: str | None
    finished_at: str | None
    current_timeframe: str | None
    error: str | None = None


def _serialize_job(job: dict[str, Any]) -> IndicatorRecomputeJobResponse:
    return IndicatorRecomputeJobResponse(
        status=job.get("status", "pending"),
        job_id=job.get("job_id"),
        symbol=job.get("symbol"),
        timeframes=job.get("timeframes") or [],
        force_full=bool(job.get("force_full") or False),
        estimated_bars=int(job.get("estimated_bars") or 0),
        estimated_bars_remaining=int(job.get("estimated_bars_remaining") or 0),
        processed_timeframes=int(job.get("processed_timeframes") or 0),
        created_at=job.get("created_at"),
        started_at=job.get("started_at"),
        finished_at=job.get("finished_at"),
        current_timeframe=job.get("current_timeframe"),
        error=job.get("error"),
    )


@router.post("/recompute", response_model=IndicatorRecomputeResponse, status_code=status.HTTP_202_ACCEPTED)
def start_recompute_indicators(
    payload: IndicatorRecomputeRequest,
    _admin_user_id: str = Depends(get_current_admin),
):
    _ = _admin_user_id
    try:
        job = get_market_indicator_service().start_recompute(
            symbol=payload.symbol,
            timeframes=payload.timeframes,
            force_full=payload.force_full,
        )
    except RuntimeError as exc:
        if "already running" in str(exc):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(exc),
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    if not job or not isinstance(job.get("job_id"), str):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to start indicator recompute job",
        )

    return IndicatorRecomputeResponse(
        status=job.get("status", "accepted"),
        job_id=job.get("job_id"),
        symbol=job.get("symbol"),
        timeframes=job.get("timeframes") or [],
        estimated_bars=int(job.get("estimated_bars") or 0),
    )


@router.get("/jobs/{job_id}", response_model=IndicatorRecomputeJobResponse)
def get_recompute_job(
    job_id: str,
    _admin_user_id: str = Depends(get_current_admin),
):
    _ = _admin_user_id
    job = get_market_indicator_service().get_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indicator job not found")
    return _serialize_job(job)


@router.get("/latest")
def get_latest_indicators(
    symbol: str = Query(..., min_length=1),
    timeframe: str = Query(..., min_length=1),
    limit: int = Query(default=1, ge=1, le=200),
    _admin_user_id: str = Depends(get_current_admin),
):
    _ = _admin_user_id
    rows = get_market_indicator_service().get_latest(symbol=symbol, timeframe=timeframe, limit=limit)
    if not rows:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No indicators found for symbol/timeframe",
        )
    return {"items": rows}
