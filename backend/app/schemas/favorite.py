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
    tier: Optional[int] = None  # 1=Core obrigatório, 2=Bons complementares, 3=Outros
    notify_telegram: bool = True
    start_date: Optional[str] = None  # Período do backtest (6m/2y/todo)
    end_date: Optional[str] = None
    period_type: Optional[str] = None  # '6m' | '2y' | 'all'; chave para skip


class FavoriteStrategyCreate(FavoriteStrategyBase):
    pass


class FavoriteStrategyResponse(FavoriteStrategyBase):
    id: int
    created_at: datetime
    is_strategy_protected: bool = False
    strategy_display_name: Optional[str] = None

    class Config:
        from_attributes = True


class FavoriteStrategyUpdate(BaseModel):
    tier: Optional[int] = None  # 1, 2, 3 ou None
    notify_telegram: Optional[bool] = None
    name: Optional[str] = None
    notes: Optional[str] = None
