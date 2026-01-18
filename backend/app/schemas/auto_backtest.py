# file: backend/app/schemas/auto_backtest.py
"""Schemas for Auto Backtest workflow"""
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

class AutoBacktestStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class AutoBacktestRequest(BaseModel):
    symbol: str
    strategy: str

class StageResult(BaseModel):
    stage_number: int
    stage_name: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class AutoBacktestResponse(BaseModel):
    run_id: str
    status: AutoBacktestStatus
    symbol: str
    strategy: str
    stages: List[StageResult] = []
    favorite_id: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

class AutoBacktestHistoryItem(BaseModel):
    run_id: str
    symbol: str
    strategy: str
    status: AutoBacktestStatus
    created_at: datetime
    completed_at: Optional[datetime] = None
    favorite_id: Optional[int] = None
