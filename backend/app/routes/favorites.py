from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import json

from app.database import get_db
from app.models import FavoriteStrategy
from app.middleware.authMiddleware import get_current_user
from app.schemas.favorite import FavoriteStrategyCreate, FavoriteStrategyResponse, FavoriteStrategyUpdate

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


class ExistsResponse(BaseModel):
    exists: bool


def _decode_jsonish(value):
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return value
        if isinstance(parsed, str):
            try:
                parsed_again = json.loads(parsed)
                return parsed_again
            except json.JSONDecodeError:
                return parsed
        return parsed
    return value


def _normalize_favorite_json_fields(row: FavoriteStrategy) -> FavoriteStrategy:
    row.parameters = _decode_jsonish(row.parameters)
    row.metrics = _decode_jsonish(row.metrics)
    return row


@router.get("/exists", response_model=ExistsResponse)
def favorite_exists(
    strategy_name: str = Query(..., description="Template name"),
    symbol: str = Query(..., description="Symbol (e.g. ETH/USDT)"),
    timeframe: str = Query(..., description="Timeframe (e.g. 1d)"),
    period_type: Optional[str] = Query(None, description="'6m' | '2y' | 'all'"),
    direction: Optional[str] = Query(None, description="'long' | 'short'; if omitted, any direction matches"),
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Check if a favorite already exists for (strategy, symbol, timeframe, period_type, direction). Used to skip single optimize."""
    q = db.query(FavoriteStrategy).filter(
        FavoriteStrategy.user_id == current_user_id,
        FavoriteStrategy.strategy_name == strategy_name,
        FavoriteStrategy.symbol == symbol,
        FavoriteStrategy.timeframe == timeframe,
    )
    if period_type is not None:
        q = q.filter(FavoriteStrategy.period_type == period_type)
    else:
        q = q.filter(
            FavoriteStrategy.start_date.is_(None),
            FavoriteStrategy.end_date.is_(None),
        )
    rows = q.all()
    rows = [_normalize_favorite_json_fields(r) for r in rows]
    if direction is not None:
        want = (direction or "long").lower()
        if want not in ("long", "short"):
            want = "long"
        rows = [
            r for r in rows
            if ((r.parameters or {}).get("direction") or "long").lower() == want
        ]
    return ExistsResponse(exists=len(rows) > 0)


@router.get("/", response_model=List[FavoriteStrategyResponse])
def list_favorites(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all favorited strategies"""
    rows = db.query(FavoriteStrategy).filter(FavoriteStrategy.user_id == current_user_id).all()
    return [_normalize_favorite_json_fields(row) for row in rows]

@router.post("/", response_model=FavoriteStrategyResponse)
def create_favorite(
    favorite: FavoriteStrategyCreate,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Save a new favorite strategy"""
    try:
        db_favorite = FavoriteStrategy(user_id=current_user_id, **favorite.model_dump())
        db.add(db_favorite)
        db.commit()
        db.refresh(db_favorite)
        return _normalize_favorite_json_fields(db_favorite)
    except Exception as e:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating favorite: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.patch("/{favorite_id}", response_model=FavoriteStrategyResponse)
def update_favorite(
    favorite_id: int,
    update_data: FavoriteStrategyUpdate,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a favorite strategy (e.g., set tier)"""
    favorite = db.query(FavoriteStrategy).filter(
        FavoriteStrategy.id == favorite_id,
        FavoriteStrategy.user_id == current_user_id,
    ).first()
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    # Update only fields that were explicitly sent (exclude_unset so we can set tier to null)
    updates = update_data.model_dump(exclude_unset=True)
    if "tier" in updates:
        tier_val = updates["tier"]
        if tier_val is not None and tier_val not in (1, 2, 3):
            raise HTTPException(status_code=400, detail="Tier must be 1, 2, 3 or null (Sem tier)")
        favorite.tier = tier_val
    if update_data.name is not None:
        favorite.name = update_data.name
    if update_data.notes is not None:
        favorite.notes = update_data.notes
    
    db.commit()
    db.refresh(favorite)
    return _normalize_favorite_json_fields(favorite)

@router.delete("/{favorite_id}")
def delete_favorite(
    favorite_id: int,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a favorite strategy"""
    favorite = db.query(FavoriteStrategy).filter(
        FavoriteStrategy.id == favorite_id,
        FavoriteStrategy.user_id == current_user_id,
    ).first()
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    db.delete(favorite)
    db.commit()
    return {"message": "Favorite deleted"}
