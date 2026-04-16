from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi import Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import logging
import threading
import time

from app.services.opportunity_service import OpportunityService
from app.middleware.authMiddleware import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/opportunities", tags=["opportunities"])
_CACHE_TTL_SECONDS = 30.0
_CACHE_LOCK = threading.Lock()
_OPPORTUNITIES_CACHE: dict[tuple[str, str | None], dict[str, Any]] = {}

class OpportunityResponse(BaseModel):
    id: int
    symbol: str
    timeframe: str
    template_name: str
    name: str  # user custom name
    notes: Optional[str] = None
    tier: Optional[int] = None  # 1=Core, 2=Complementares, 3=Outros
    parameters: Optional[Dict[str, Any]] = None  # Parâmetros da estratégia (ema_short, sma_long, stop_loss, etc.)
    is_holding: bool
    distance_to_next_status: float | None
    next_status_label: str  # "entry" or "exit"
    indicator_values: Optional[Dict[str, float]] = None  # Valores usados no cálculo da distância (short, medium, long, etc.)
    indicator_values_candle_time: Optional[str] = None  # ISO datetime do candle usado (para conferir com TradingView)
    signal_history: Optional[List[Dict[str, Any]]] = None

    # Risk / stop-loss (optional)
    entry_price: Optional[float] = None
    stop_price: Optional[float] = None
    distance_to_stop_pct: Optional[float] = None
    # Legacy fields (kept for backward compatibility)
    status: str
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


def _write_cached_opportunities(user_id: str, tier: str | None, payload: list[dict[str, Any]]) -> None:
    key = (user_id, tier)
    with _CACHE_LOCK:
        _OPPORTUNITIES_CACHE[key] = {
            "payload": list(payload),
            "expires_at": time.time() + _CACHE_TTL_SECONDS,
        }


@router.get("/", response_model=List[OpportunityResponse])
async def get_opportunities(
    tier: Optional[str] = Query(None, description="Filter by tier(s). E.g. '1', '1,2', 'none' for null tier, 'all' for no filter"),
    refresh: bool = Query(False, description="Bypass short-lived cache and recompute opportunities."),
    current_user_id: str = Depends(get_current_user),
):
    """
    Get current opportunities (proximity analysis) for favorite strategies.
    
    Query params:
    - tier: Filter by tier(s). Examples: '1', '1,2', '3', 'none' (null tier), 'all' (no filter)
    
    Returns opportunities sorted by Signal Priority (SIGNAL > NEAR > NEUTRAL).
    """
    try:
        if not refresh:
            cached = _read_cached_opportunities(current_user_id, tier)
            if cached is not None:
                return cached
        service = OpportunityService()
        payload = service.get_opportunities(user_id=current_user_id, tier_filter=tier)
        _write_cached_opportunities(current_user_id, tier, payload)
        return payload
    except Exception as e:
        logger.error(f"Error getting opportunities: {e}")
        raise HTTPException(status_code=500, detail=str(e))
