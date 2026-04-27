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
from app.services.onchain_exchange_flow_service import get_exchange_flow_service
from app.services.onchain_mining_metric_service import get_mining_metric_service
from app.services.onchain_supply_distribution_service import get_supply_distribution_service

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


class ExchangeFlowExchangePayload(BaseModel):
    exchange: str
    inflow: float
    outflow: float
    netflow: float


class ExchangeFlowSourcePayload(BaseModel):
    endpoint: str
    points: int
    cached: bool
    fetched_at: datetime
    cached_until: datetime


class ExchangeFlowsResponse(BaseModel):
    asset: str
    window: str
    interval: str
    since: int
    until: int
    cached: bool
    total: dict[str, float]
    exchanges: list[ExchangeFlowExchangePayload]
    sources: dict[str, ExchangeFlowSourcePayload]


class MiningMetricAlertPayload(BaseModel):
    type: str
    threshold_pct: float
    drop_pct_vs_ma_7d: float | None


class MiningMetricPayload(BaseModel):
    metric: str
    asset: str
    interval: str
    endpoint: str
    points: list[dict[str, Any]]
    latest: dict[str, Any] | None
    ath: dict[str, Any] | None
    drop_pct_vs_ma_7d: float | None
    alerts: list[MiningMetricAlertPayload]
    fetched_at: datetime
    cached_until: datetime
    cached: bool


class MiningMetricsResponse(BaseModel):
    asset: str
    interval: str
    since: int | None
    until: int | None
    cached: bool
    metrics: list[MiningMetricPayload]


class SupplyDistributionSourcePayload(BaseModel):
    endpoint: str
    points: int
    cached: bool
    fetched_at: datetime
    cached_until: datetime


class SupplyDistributionBandPayload(BaseModel):
    id: str
    metric: str
    label: str
    min_btc: float | None
    max_btc: float | None
    latest: float | None
    latest_timestamp: int | None
    previous: float | None
    previous_timestamp: int | None
    change_abs: float | None
    change_pct: float | None
    share_pct: float | None


class SupplyDistributionCohortPayload(BaseModel):
    id: str
    label: str
    band_ids: list[str]
    latest: float | None
    latest_timestamp: int | None
    previous: float | None
    previous_timestamp: int | None
    change_abs: float | None
    change_pct: float | None
    share_pct: float | None


class SupplyDistributionWhaleMovementPayload(BaseModel):
    threshold_btc: float
    change_abs: float | None
    direction: str
    alert: bool


class SupplyDistributionAlertPayload(BaseModel):
    type: str
    threshold_btc: float
    change_abs: float | None
    direction: str
    window: str


class SupplyDistributionResponse(BaseModel):
    asset: str
    basis: str
    window: str
    interval: str
    since: int
    until: int
    cached: bool
    bands: list[SupplyDistributionBandPayload]
    cohorts: dict[str, SupplyDistributionCohortPayload]
    whale_movement: SupplyDistributionWhaleMovementPayload
    alerts: list[SupplyDistributionAlertPayload]
    sources: dict[str, SupplyDistributionSourcePayload]


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


@router.get(
    "/glassnode/{asset}/supply-distribution",
    response_model=SupplyDistributionResponse,
)
async def get_glassnode_supply_distribution(
    asset: str,
    basis: str = Query(default="entity", pattern="^entity$"),
    window: str = Query(default="24h", pattern="^(24h|7d|30d)$"),
):
    try:
        payload = await get_supply_distribution_service().fetch_supply_distribution(
            asset,
            basis=basis,
            window=window,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except GlassnodeConfigError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    except GlassnodeRateLimitError as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc))
    return payload


@router.get("/glassnode/{asset}/mining-metrics", response_model=MiningMetricsResponse)
async def get_glassnode_mining_metrics(
    asset: str,
    interval: str = Query(default=DEFAULT_GLASSNODE_INTERVAL, pattern="^24h$"),
    since: int | None = Query(default=None, ge=0),
    until: int | None = Query(default=None, ge=0),
):
    try:
        payload = await get_mining_metric_service().fetch_mining_metrics(
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


@router.get("/glassnode/{asset}/exchange-flows", response_model=ExchangeFlowsResponse)
async def get_glassnode_exchange_flows(
    asset: str,
    window: str = Query(default="24h", pattern="^(24h|7d|30d)$"),
):
    try:
        payload = await get_exchange_flow_service().fetch_exchange_flows(asset, window=window)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except GlassnodeConfigError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))
    except GlassnodeRateLimitError as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc))
    return payload
