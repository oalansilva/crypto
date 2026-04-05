# file: backend/app/routes/onchain_signals.py
"""Onchain signal API routes."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.services.onchain_service import (
    TOP_CHAINS,
    OnchainSignalHistory,
    compose_onchain_signal,
    get_onchain_history,
    get_onchain_performance,
    save_onchain_signal,
)


router = APIRouter(prefix="/api/signals/onchain", tags=["onchain-signals"])


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------


class OnchainMetricsSchema(BaseModel):
    token: str
    chain: str
    tvl: float | None = None
    active_addresses: float | None = None
    exchange_flow: float | None = None
    github_commits: int | None = None
    github_stars: int | None = None
    github_prs: int | None = None
    github_issues: int | None = None
    fetched_at: datetime


class BreakdownSchema(BaseModel):
    tvl: float = Field(description="TVL contribution to confidence (%)")
    active_addresses: float = Field(description="Active addresses contribution (%)")
    exchange_flow: float = Field(description="Exchange flow contribution (%)")
    github_commits: float = Field(description="GitHub commits contribution (%)")
    github_stars: float = Field(description="GitHub stars contribution (%)")
    github_issues: float = Field(description="GitHub issues contribution (%)")


class OnchainSignalResponse(BaseModel):
    signal: str = Field(description="BUY, SELL, or HOLD")
    confidence: int = Field(ge=0, le=100, description="Confidence score 0-100")
    breakdown: dict[str, float]
    metrics: OnchainMetricsSchema
    timestamp: datetime


class OnchainHistoryItem(BaseModel):
    id: str
    token: str
    chain: str
    signal_type: str
    confidence: int
    breakdown: dict[str, Any]
    status: str
    tvl: float | None
    active_addresses: float | None
    exchange_flow: float | None
    github_commits: int | None
    github_stars: int | None
    github_prs: int | None
    github_issues: int | None
    price_at_signal: float | None
    price_after_1h: float | None
    price_after_4h: float | None
    price_after_24h: float | None
    created_at: datetime


class OnchainHistoryResponse(BaseModel):
    signals: list[OnchainHistoryItem]
    total: int
    limit: int
    offset: int


class PerformanceByType(BaseModel):
    count: int
    avg_confidence: float


class OnchainPerformanceResponse(BaseModel):
    total_signals: int
    win_rate: float
    avg_confidence: float
    expired_rate: float
    by_signal_type: dict[str, PerformanceByType]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_history_item(row: OnchainSignalHistory) -> OnchainHistoryItem:
    breakdown: dict[str, Any] = {}
    if row.breakdown:
        try:
            breakdown = json.loads(row.breakdown)
        except Exception:
            breakdown = {}

    return OnchainHistoryItem(
        id=row.id,
        token=row.token,
        chain=row.chain,
        signal_type=row.signal_type,
        confidence=row.confidence,
        breakdown=breakdown,
        status=row.status,
        tvl=row.tvl,
        active_addresses=row.active_addresses,
        exchange_flow=row.exchange_flow,
        github_commits=row.github_commits,
        github_stars=row.github_stars,
        github_prs=row.github_prs,
        github_issues=row.github_issues,
        price_at_signal=row.price_at_signal,
        price_after_1h=row.price_after_1h,
        price_after_4h=row.price_after_4h,
        price_after_24h=row.price_after_24h,
        created_at=row.created_at,
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get(
    "",
    response_model=OnchainSignalResponse,
    summary="Onchain signal for token + chain",
    description="Fetches latest DeFiLlama + GitHub data and returns BUY/SELL/HOLD signal with confidence breakdown.",
)
async def get_onchain_signal(
    token: str = Query(..., description="Token symbol, e.g. ETH, SOL", min_length=1),
    chain: str = Query(..., description="Chain slug: ethereum, solana, arbitrum, base, matic"),
):
    if chain.lower() not in TOP_CHAINS:
        chain = TOP_CHAINS[0]  # fallback to ethereum

    result = compose_onchain_signal(token.upper(), chain.lower())
    save_onchain_signal(token.upper(), chain.lower(), result)

    return OnchainSignalResponse(
        signal=result.signal,
        confidence=result.confidence,
        breakdown=result.breakdown,
        metrics=OnchainMetricsSchema(
            token=result.metrics.token,
            chain=result.metrics.chain,
            tvl=result.metrics.tvl,
            active_addresses=result.metrics.active_addresses,
            exchange_flow=result.metrics.exchange_flow,
            github_commits=result.metrics.github_commits,
            github_stars=result.metrics.github_stars,
            github_prs=result.metrics.github_prs,
            github_issues=result.metrics.github_issues,
            fetched_at=result.timestamp,
        ),
        timestamp=result.timestamp,
    )


@router.get(
    "/history",
    response_model=OnchainHistoryResponse,
    summary="Onchain signal history",
)
async def list_onchain_history(
    token: str | None = Query(default=None, description="Filter by token, e.g. ETH"),
    chain: str | None = Query(default=None, description="Filter by chain slug"),
    signal_type: str | None = Query(default=None, description="Filter by signal type: BUY, SELL, HOLD"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    rows, total = get_onchain_history(
        token=token,
        chain=chain,
        signal_type=signal_type,
        limit=limit,
        offset=offset,
    )
    return OnchainHistoryResponse(
        signals=[_build_history_item(r) for r in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/performance",
    response_model=OnchainPerformanceResponse,
    summary="Onchain signal performance statistics",
)
async def get_performance():
    stats = get_onchain_performance()
    by_type = {}
    for st, data in stats.get("by_signal_type", {}).items():
        by_type[st] = PerformanceByType(
            count=data["count"],
            avg_confidence=data["avg_confidence"],
        )
    return OnchainPerformanceResponse(
        total_signals=stats["total_signals"],
        win_rate=stats["win_rate"],
        avg_confidence=stats["avg_confidence"],
        expired_rate=stats["expired_rate"],
        by_signal_type=by_type,
    )
