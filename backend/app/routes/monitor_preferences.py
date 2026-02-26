from datetime import datetime
from typing import Dict, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import MonitorPreference

router = APIRouter(prefix="/api/monitor", tags=["monitor"])

CardMode = Literal["price", "strategy"]
PriceTimeframe = Literal["15m", "1h", "4h", "1d"]
ThemeName = Literal["dark-green", "black"]
PRICE_TIMEFRAMES = {"15m", "1h", "4h", "1d"}
THEMES = {"dark-green", "black"}


class MonitorPreferencePayload(BaseModel):
    in_portfolio: bool
    card_mode: CardMode
    price_timeframe: PriceTimeframe
    theme: ThemeName


class MonitorPreferenceUpdate(BaseModel):
    in_portfolio: Optional[bool] = None
    card_mode: Optional[CardMode] = None
    price_timeframe: Optional[PriceTimeframe] = None
    theme: Optional[ThemeName] = None


def _normalize_symbol(symbol: str) -> str:
    normalized = str(symbol or "").strip()
    if not normalized:
        raise HTTPException(status_code=400, detail="Symbol must not be empty")
    return normalized


def _is_stock_symbol(symbol: str) -> bool:
    return "/" not in symbol


def _normalize_price_timeframe(symbol: str, timeframe: Optional[str]) -> str:
    normalized = str(timeframe or "").strip().lower()
    if normalized not in PRICE_TIMEFRAMES:
        normalized = "1d"
    if _is_stock_symbol(symbol):
        return "1d"
    return normalized


@router.get("/preferences", response_model=Dict[str, MonitorPreferencePayload])
def list_monitor_preferences(db: Session = Depends(get_db)):
    rows = db.query(MonitorPreference).all()
    return {
        row.symbol: {
            "in_portfolio": bool(row.in_portfolio),
            "card_mode": row.card_mode if row.card_mode in {"price", "strategy"} else "price",
            "price_timeframe": _normalize_price_timeframe(row.symbol, getattr(row, "price_timeframe", None)),
            "theme": row.theme if getattr(row, "theme", None) in THEMES else "dark-green",
        }
        for row in rows
    }


@router.put("/preferences/{symbol:path}", response_model=MonitorPreferencePayload)
def update_monitor_preferences(
    payload: MonitorPreferenceUpdate,
    symbol: str = Path(..., description="Symbol (e.g. BTC/USDT or NVDA)"),
    db: Session = Depends(get_db),
):
    if (
        payload.in_portfolio is None
        and payload.card_mode is None
        and payload.price_timeframe is None
        and payload.theme is None
    ):
        raise HTTPException(status_code=400, detail="At least one field must be provided")

    normalized_symbol = _normalize_symbol(symbol)
    is_stock = _is_stock_symbol(normalized_symbol)
    if is_stock and payload.price_timeframe is not None and payload.price_timeframe != "1d":
        raise HTTPException(
            status_code=400,
            detail="Stocks currently support only timeframe='1d'",
        )

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
    if payload.price_timeframe is not None:
        existing.price_timeframe = payload.price_timeframe
    elif not getattr(existing, "price_timeframe", None):
        existing.price_timeframe = "1d"

    if payload.theme is not None:
        existing.theme = payload.theme
    elif not getattr(existing, "theme", None):
        existing.theme = "dark-green"

    existing.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(existing)

    return {
        "in_portfolio": bool(existing.in_portfolio),
        "card_mode": existing.card_mode if existing.card_mode in {"price", "strategy"} else "price",
        "price_timeframe": _normalize_price_timeframe(normalized_symbol, getattr(existing, "price_timeframe", None)),
        "theme": existing.theme if getattr(existing, "theme", None) in THEMES else "dark-green",
    }
