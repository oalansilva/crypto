from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
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
    name: str # user custom name
    is_holding: bool
    distance_to_next_status: float | None
    next_status_label: str  # "entry" or "exit"
    # Legacy fields (kept for backward compatibility)
    status: str
    badge: str
    message: str
    last_price: float
    timestamp: str
    details: dict

@router.get("/", response_model=List[OpportunityResponse])
async def get_opportunities():
    """
    Get current opportunities (proximity analysis) for all favorite strategies.
    sorted by Signal Priority (SIGNAL > NEAR > NEUTRAL).
    """
    try:
        service = OpportunityService()
        return service.get_opportunities()
    except Exception as e:
        logger.error(f"Error getting opportunities: {e}")
        raise HTTPException(status_code=500, detail=str(e))
