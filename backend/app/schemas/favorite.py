from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class FavoriteStrategyBase(BaseModel):
    name: str
    symbol: str
    timeframe: str
    strategy_name: str
    parameters: Dict[str, Any]
    metrics: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

class FavoriteStrategyCreate(FavoriteStrategyBase):
    pass

class FavoriteStrategyResponse(FavoriteStrategyBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
