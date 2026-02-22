from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import logging

from app.services.opportunity_service import OpportunityService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/opportunities", tags=["opportunities"])

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

@router.get("/", response_model=List[OpportunityResponse])
async def get_opportunities(
    tier: Optional[str] = Query(None, description="Filter by tier(s). E.g. '1', '1,2', 'none' for null tier, 'all' for no filter")
):
    """
    Get current opportunities (proximity analysis) for favorite strategies.
    
    Query params:
    - tier: Filter by tier(s). Examples: '1', '1,2', '3', 'none' (null tier), 'all' (no filter)
    
    Returns opportunities sorted by Signal Priority (SIGNAL > NEAR > NEUTRAL).
    """
    try:
        service = OpportunityService()
        return service.get_opportunities(tier_filter=tier)
    except Exception as e:
        logger.error(f"Error getting opportunities: {e}")
        raise HTTPException(status_code=500, detail=str(e))
