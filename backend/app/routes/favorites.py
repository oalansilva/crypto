from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import FavoriteStrategy
from app.schemas.favorite import FavoriteStrategyCreate, FavoriteStrategyResponse

router = APIRouter(prefix="/api/favorites", tags=["favorites"])

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

@router.delete("/{favorite_id}")
def delete_favorite(favorite_id: int, db: Session = Depends(get_db)):
    """Delete a favorite strategy"""
    favorite = db.query(FavoriteStrategy).filter(FavoriteStrategy.id == favorite_id).first()
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    db.delete(favorite)
    db.commit()
    return {"message": "Favorite deleted"}
