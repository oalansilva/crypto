from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi import Depends
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel
import logging
import threading
import time
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.opportunity_service import OpportunityService
from app.middleware.authMiddleware import get_current_user
from app.services.strategy_secret_visibility import (
    can_view_strategy_secrets,
    redact_opportunity_payload,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/opportunities", tags=["opportunities"])
_CACHE_TTL_SECONDS = 30.0
_CACHE_LOCK = threading.Lock()
_OPPORTUNITIES_CACHE: dict[tuple[str, str | None], dict[str, Any]] = {}
COMMON_USER_TIER_FILTER = "1,2,3"


class OpportunityResponse(BaseModel):
    id: int
    symbol: str
    asset_type: str
    timeframe: str
    template_name: str
    name: str  # user custom name
    notes: Optional[str] = None
    tier: Optional[int] = None  # 1=Core, 2=Complementares, 3=Outros
    parameters: Optional[Dict[str, Any]] = (
        None  # Parâmetros da estratégia (ema_short, sma_long, stop_loss, etc.)
    )
    is_holding: bool
    distance_to_next_status: float | None
    next_status_label: str  # "entry" or "exit"
    indicator_values: Optional[Dict[str, float]] = (
        None  # Valores usados no cálculo da distância (short, medium, long, etc.)
    )
    indicator_values_candle_time: Optional[str] = (
        None  # ISO datetime do candle usado (para conferir com TradingView)
    )
    signal_history: Optional[List[Dict[str, Any]]] = None
    is_strategy_protected: bool = False
    strategy_display_name: Optional[str] = None
    strategy_description: Optional[str] = None

    # Risk / stop-loss (optional)
    entry_price: Optional[float] = None
    stop_price: Optional[float] = None
    distance_to_stop_pct: Optional[float] = None
    # Monitor status is intentionally binary for API consumers: "HOLD" or "EXIT".
    status: Literal["HOLD", "EXIT"]
    badge: str
    message: str
    last_price: float
    timestamp: str
    details: dict


from fastapi import Query


def _read_cached_opportunities(user_id: str, tier: str | None) -> list[dict[str, Any]] | None:
    now = time.time()
    key = (user_id, tier)
    with _CACHE_LOCK:
        cached = _OPPORTUNITIES_CACHE.get(key)
        if not cached:
            return None
        if float(cached.get("expires_at") or 0) <= now:
            _OPPORTUNITIES_CACHE.pop(key, None)
            return None
        return list(cached.get("payload") or [])


def _write_cached_opportunities(
    user_id: str, tier: str | None, payload: list[dict[str, Any]]
) -> None:
    key = (user_id, tier)
    with _CACHE_LOCK:
        _OPPORTUNITIES_CACHE[key] = {
            "payload": list(payload),
            "expires_at": time.time() + _CACHE_TTL_SECONDS,
        }


def _common_user_tier_filter(tier: str | None) -> str:
    normalized = str(tier or "").strip().lower()
    if not normalized or normalized == "all":
        return COMMON_USER_TIER_FILTER
    if normalized == "none":
        return "999"

    allowed = [
        item for item in (part.strip() for part in normalized.split(",")) if item in {"1", "2", "3"}
    ]
    return ",".join(allowed) if allowed else "999"


def _normalize_monitor_status_payload(payload: dict[str, Any]) -> dict[str, Any]:
    raw_status = str(payload.get("status") or "").strip().upper()
    is_holding = bool(payload.get("is_holding"))
    if raw_status in {
        "EXIT",
        "EXIT_SIGNAL",
        "EXIT_NEAR",
        "EXITED",
        "STOPPED_OUT",
        "MISSED_ENTRY",
        "MISSED",
    }:
        status = "EXIT"
    elif raw_status in {"HOLD", "HOLDING", "BUY_SIGNAL"} or is_holding:
        status = "HOLD"
    else:
        status = "EXIT"

    payload["status"] = status
    payload["is_holding"] = status == "HOLD"
    payload["badge"] = "info" if status == "HOLD" else "neutral"
    details = payload.get("details")
    if isinstance(details, dict):
        if "status" in details:
            details["status"] = status
    return payload


@router.get("/", response_model=List[OpportunityResponse])
async def get_opportunities(
    tier: Optional[str] = Query(
        None,
        description="Filter by tier(s). E.g. '1', '1,2', 'none' for null tier, 'all' for no filter",
    ),
    refresh: bool = Query(
        False, description="Bypass short-lived cache and recompute opportunities."
    ),
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get current opportunities (proximity analysis) for favorite strategies.

    Query params:
    - tier: Filter by tier(s). Examples: '1', '1,2', '3', 'none' (null tier), 'all' (no filter)

    Returns opportunities with binary Monitor status: HOLD or EXIT.
    """
    try:
        include_secrets = can_view_strategy_secrets(db, current_user_id)
        effective_tier = tier if include_secrets else _common_user_tier_filter(tier)
        if not refresh:
            cached = _read_cached_opportunities(current_user_id, effective_tier)
            if cached is not None:
                return [
                    redact_opportunity_payload(
                        _normalize_monitor_status_payload(dict(item)),
                        include_secrets=include_secrets,
                    )
                    for item in cached
                ]
        service = OpportunityService()
        payload = service.get_opportunities(user_id=current_user_id, tier_filter=effective_tier)
        _write_cached_opportunities(current_user_id, effective_tier, payload)
        return [
            redact_opportunity_payload(
                _normalize_monitor_status_payload(dict(item)),
                include_secrets=include_secrets,
            )
            for item in payload
        ]
    except Exception as e:
        logger.error(f"Error getting opportunities: {e}")
        raise HTTPException(status_code=500, detail=str(e))
