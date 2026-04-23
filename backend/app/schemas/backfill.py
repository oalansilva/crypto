"""
Pydantic schemas for manual/scheduled OHLCV backfill job management.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class OhlcvBackfillStartRequest(BaseModel):
    """Request to start a historical backfill job."""

    symbol: str = Field(
        ..., min_length=1, max_length=40, description="Trading symbol, e.g. BTC/USDT"
    )
    timeframes: List[str] = Field(
        default_factory=lambda: ["1d"], description="Timeframes to backfill"
    )
    data_source: Optional[str] = Field(
        None, description="Optional data source override (ccxt/stooq/yahoo)"
    )
    history_window_years: int = Field(
        default=2, ge=1, le=10, description="How many years of history to backfill"
    )
    page_size: int = Field(
        default=1000, ge=100, le=5000, description="Batch size per provider request"
    )
    max_requests_per_minute: int = Field(
        default=60, ge=10, le=6000, description="Max API calls per minute"
    )

    @field_validator("timeframes")
    @classmethod
    def normalize_timeframes(cls, value: List[str]) -> List[str]:
        normalized = [str(item).strip().lower() for item in (value or []) if str(item).strip()]
        if not normalized:
            return ["1d"]
        # Preserve user order, remove duplicates
        seen: set[str] = set()
        output: list[str] = []
        for item in normalized:
            if item in seen:
                continue
            seen.add(item)
            output.append(item)
        return output

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        return str(value or "").strip().upper()


class OhlcvBackfillJobResponse(BaseModel):
    """Backfill job summary."""

    job_id: str
    symbol: str
    timeframes: list[str]
    status: str
    processed: int
    written: int
    duplicates: int
    attempts: int
    estimated_total: Optional[int] = None
    total_estimate: Optional[int] = None
    percent: float
    eta_seconds: Optional[float] = None
    requested_window: Dict[str, Any]
    provider: Optional[str] = None
    requested_source: Optional[str] = None
    page_size: int = 1000
    max_requests_per_minute: int = 60
    last_error: Optional[str] = None
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    updated_at: Optional[str] = None
    finished_at: Optional[str] = None
    current_timeframe: Optional[str] = None
    current_lookback_to: Optional[str] = None
    timeframe_states: Optional[Dict[str, Dict[str, Any]]] = None
    events: list[Dict[str, Any]] = Field(default_factory=list)


class OhlcvBackfillListResponse(BaseModel):
    """Paged list of backfill jobs."""

    items: list[OhlcvBackfillJobResponse]
    total: int
    page: int = 1
    page_size: int = 50
