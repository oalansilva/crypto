from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.schemas.signal import RiskProfile, Signal, SignalListResponse, SignalType
from app.services import binance_service

router = APIRouter(prefix="/api/signals", tags=["signals"])


@router.get(
    "",
    response_model=SignalListResponse,
    summary="List trading signals",
    description="Returns BUY/SELL/HOLD signals generated from Binance OHLCV data and temporary heuristics until Card #55 ships the final ML ensemble.",
)
async def get_signals(
    type: SignalType | None = Query(default=None, description="Filter by BUY, SELL or HOLD"),
    confidence_min: int | None = Query(default=None, ge=0, le=100, description="Minimum confidence threshold"),
    asset: str | None = Query(default=None, description="Binance symbol, e.g. BTCUSDT"),
    risk_profile: RiskProfile = Query(default=RiskProfile.moderate, description="Signal risk profile"),
    limit: int = Query(default=20, ge=1, le=50, description="Maximum number of signals to return"),
):
    return await binance_service.build_signal_feed(
        signal_type=type,
        confidence_min=confidence_min,
        asset=asset,
        risk_profile=risk_profile,
        limit=limit,
    )


@router.get(
    "/latest",
    response_model=SignalListResponse,
    summary="Latest high-confidence signals",
    description="Returns the latest five signals with confidence >= 70 across default assets and all supported risk profiles.",
)
async def get_latest_signals():
    return await binance_service.get_latest_high_confidence_signals()


@router.get(
    "/{signal_id}",
    response_model=Signal,
    summary="Get a signal by id",
)
async def get_signal_by_id(signal_id: str):
    try:
        return await binance_service.get_signal_detail(signal_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Signal not found") from exc
