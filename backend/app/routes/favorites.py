from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models import FavoriteStrategy
from app.schemas.favorite import FavoriteStrategyCreate, FavoriteStrategyResponse, FavoriteStrategyUpdate

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


class ExistsResponse(BaseModel):
    exists: bool


@router.get("/exists", response_model=ExistsResponse)
def favorite_exists(
    strategy_name: str = Query(..., description="Template name"),
    symbol: str = Query(..., description="Symbol (e.g. ETH/USDT)"),
    timeframe: str = Query(..., description="Timeframe (e.g. 1d)"),
    period_type: Optional[str] = Query(None, description="'6m' | '2y' | 'all'"),
    db: Session = Depends(get_db),
):
    """Check if a favorite already exists for (strategy, symbol, timeframe, period_type). Used to skip single optimize."""
    q = db.query(FavoriteStrategy).filter(
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
    return ExistsResponse(exists=q.first() is not None)


@router.get("/", response_model=List[FavoriteStrategyResponse])
def list_favorites(db: Session = Depends(get_db)):
    """List all favorited strategies"""
    return db.query(FavoriteStrategy).all()

@router.post("/", response_model=FavoriteStrategyResponse)
def create_favorite(favorite: FavoriteStrategyCreate, db: Session = Depends(get_db)):
    """Save a new favorite strategy"""
    try:
        db_favorite = FavoriteStrategy(**favorite.model_dump())
        db.add(db_favorite)
        db.commit()
        db.refresh(db_favorite)
        return db_favorite
    except Exception as e:
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating favorite: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.patch("/{favorite_id}", response_model=FavoriteStrategyResponse)
def update_favorite(favorite_id: int, update_data: FavoriteStrategyUpdate, db: Session = Depends(get_db)):
    """Update a favorite strategy (e.g., set tier)"""
    favorite = db.query(FavoriteStrategy).filter(FavoriteStrategy.id == favorite_id).first()
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    # Validate tier value if provided
    if update_data.tier is not None:
        if update_data.tier not in [1, 2, 3]:
            raise HTTPException(status_code=400, detail="Tier must be 1, 2, or 3")
        favorite.tier = update_data.tier
    
    # Update only provided fields
    if update_data.name is not None:
        favorite.name = update_data.name
    if update_data.notes is not None:
        favorite.notes = update_data.notes
    
    db.commit()
    db.refresh(favorite)
    return favorite

@router.delete("/{favorite_id}")
def delete_favorite(favorite_id: int, db: Session = Depends(get_db)):
    """Delete a favorite strategy"""
    favorite = db.query(FavoriteStrategy).filter(FavoriteStrategy.id == favorite_id).first()
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    db.delete(favorite)
    db.commit()
    return {"message": "Favorite deleted"}
