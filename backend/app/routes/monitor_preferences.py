from datetime import datetime
from typing import Dict, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import MonitorPreference

router = APIRouter(prefix="/api/monitor", tags=["monitor"])

CardMode = Literal["price", "strategy"]


class MonitorPreferencePayload(BaseModel):
    in_portfolio: bool
    card_mode: CardMode


class MonitorPreferenceUpdate(BaseModel):
    in_portfolio: Optional[bool] = None
    card_mode: Optional[CardMode] = None


def _normalize_symbol(symbol: str) -> str:
    normalized = str(symbol or "").strip()
    if not normalized:
        raise HTTPException(status_code=400, detail="Symbol must not be empty")
    return normalized


@router.get("/preferences", response_model=Dict[str, MonitorPreferencePayload])
def list_monitor_preferences(db: Session = Depends(get_db)):
    rows = db.query(MonitorPreference).all()
    return {
        row.symbol: {
            "in_portfolio": bool(row.in_portfolio),
            "card_mode": row.card_mode if row.card_mode in {"price", "strategy"} else "price",
        }
        for row in rows
    }


@router.put("/preferences/{symbol:path}", response_model=MonitorPreferencePayload)
def update_monitor_preferences(
    payload: MonitorPreferenceUpdate,
    symbol: str = Path(..., description="Symbol (e.g. BTC/USDT or NVDA)"),
    db: Session = Depends(get_db),
):
    if payload.in_portfolio is None and payload.card_mode is None:
        raise HTTPException(status_code=400, detail="At least one field must be provided")

    normalized_symbol = _normalize_symbol(symbol)

    existing = (
        db.query(MonitorPreference)
        .filter(MonitorPreference.symbol == normalized_symbol)
        .first()
    )
    if not existing:
        existing = MonitorPreference(symbol=normalized_symbol)
        db.add(existing)

    if payload.in_portfolio is not None:
        existing.in_portfolio = payload.in_portfolio
    if payload.card_mode is not None:
        existing.card_mode = payload.card_mode

    existing.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(existing)

    return {
        "in_portfolio": bool(existing.in_portfolio),
        "card_mode": existing.card_mode if existing.card_mode in {"price", "strategy"} else "price",
    }
