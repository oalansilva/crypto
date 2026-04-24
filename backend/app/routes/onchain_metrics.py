from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from app.services.glassnode_service import (
    DEFAULT_GLASSNODE_INTERVAL,
    GlassnodeConfigError,
    GlassnodeRateLimitError,
    get_glassnode_service,
)

router = APIRouter(prefix="/api/onchain", tags=["onchain"])


class GlassnodeMetricPayload(BaseModel):
    metric: str
    asset: str
    interval: str
    endpoint: str
    points: list[dict[str, Any]]
    latest: dict[str, Any] | None
    fetched_at: datetime
    cached_until: datetime
    cached: bool


class GlassnodeMetricsResponse(BaseModel):
    asset: str
    interval: str
    cached: bool
    metrics: list[GlassnodeMetricPayload]


@router.get("/glassnode/{asset}", response_model=GlassnodeMetricsResponse)
async def get_glassnode_onchain_metrics(
    asset: str,
    interval: str = Query(default=DEFAULT_GLASSNODE_INTERVAL, min_length=1),
    since: int | None = Query(default=None, ge=0),
    until: int | None = Query(default=None, ge=0),
):
    try:
        payload = await get_glassnode_service().fetch_metrics(
            asset,
            interval=interval,
            since=since,
            until=until,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except GlassnodeConfigError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    except GlassnodeRateLimitError as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc))
    return payload
