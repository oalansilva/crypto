from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import json

from app.database import get_db
from app.models import FavoriteStrategy, MonitorStrategyPreference, User
from app.middleware.authMiddleware import ADMIN_EMAILS, get_current_user, is_admin_email
from app.schemas.favorite import (
    FavoriteStrategyCreate,
    FavoriteStrategyResponse,
    FavoriteStrategyUpdate,
)
from app.services.strategy_secret_visibility import (
    can_view_strategy_secrets,
    redact_favorite_strategy_payload,
)

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


_TIER_UNSET = object()


def _favorite_response(
    row: FavoriteStrategy,
    *,
    include_secrets: bool,
    tier_override: int | None | object = _TIER_UNSET,
) -> FavoriteStrategyResponse:
    normalized = _normalize_favorite_json_fields(row)
    payload = FavoriteStrategyResponse.model_validate(normalized).model_dump()
    if tier_override is not _TIER_UNSET:
        payload["tier"] = tier_override
    return FavoriteStrategyResponse(
        **redact_favorite_strategy_payload(payload, include_secrets=include_secrets)
    )


def _configured_admin_emails() -> list[str]:
    return sorted(email for email in ADMIN_EMAILS if email)


def _current_user(db: Session, user_id: str) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def _admin_catalog_user_ids(db: Session, *, exclude_user_id: str | None = None) -> list[str]:
    admin_emails = _configured_admin_emails()
    if not admin_emails:
        return []

    rows = (
        db.query(User)
        .filter(func.lower(User.email).in_(admin_emails))
        .order_by(User.email.asc())
        .all()
    )
    return [
        str(row.id)
        for row in rows
        if str(row.id) != str(exclude_user_id or "") and is_admin_email(row.email)
    ]


def _strategy_tier_preferences(db: Session, user_id: str) -> dict[int, int | None]:
    rows = (
        db.query(MonitorStrategyPreference)
        .filter(MonitorStrategyPreference.user_id == user_id)
        .all()
    )
    return {int(row.favorite_id): getattr(row, "tier", None) for row in rows}


def _upsert_strategy_tier_preference(
    db: Session,
    *,
    user_id: str,
    favorite_id: int,
    tier: int | None,
) -> MonitorStrategyPreference:
    existing = (
        db.query(MonitorStrategyPreference)
        .filter(
            MonitorStrategyPreference.user_id == user_id,
            MonitorStrategyPreference.favorite_id == favorite_id,
        )
        .first()
    )
    if not existing:
        existing = MonitorStrategyPreference(
            user_id=user_id,
            favorite_id=favorite_id,
            liked=tier is not None,
            tier=tier,
        )
        db.add(existing)
    else:
        existing.liked = tier is not None
        existing.tier = tier
    return existing


@router.get("/exists", response_model=ExistsResponse)
def favorite_exists(
    strategy_name: str = Query(..., description="Template name"),
    symbol: str = Query(..., description="Symbol (e.g. ETH/USDT)"),
    timeframe: str = Query(..., description="Timeframe (e.g. 1d)"),
    period_type: Optional[str] = Query(None, description="'6m' | '2y' | 'all'"),
    direction: Optional[str] = Query(
        None, description="'long' | 'short'; if omitted, any direction matches"
    ),
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
            r for r in rows if ((r.parameters or {}).get("direction") or "long").lower() == want
        ]
    return ExistsResponse(exists=len(rows) > 0)


@router.get("/", response_model=List[FavoriteStrategyResponse])
def list_favorites(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all favorited strategies"""
    include_secrets = can_view_strategy_secrets(db, current_user_id)
    current_user = _current_user(db, current_user_id)

    if include_secrets or (current_user and is_admin_email(current_user.email)):
        rows = db.query(FavoriteStrategy).filter(FavoriteStrategy.user_id == current_user_id).all()
        return [_favorite_response(row, include_secrets=include_secrets) for row in rows]

    if not current_user:
        rows = db.query(FavoriteStrategy).filter(FavoriteStrategy.user_id == current_user_id).all()
        return [_favorite_response(row, include_secrets=include_secrets) for row in rows]

    admin_user_ids = _admin_catalog_user_ids(db, exclude_user_id=current_user_id)
    if not admin_user_ids:
        rows = db.query(FavoriteStrategy).filter(FavoriteStrategy.user_id == current_user_id).all()
        return [_favorite_response(row, include_secrets=include_secrets) for row in rows]

    tier_by_favorite_id = _strategy_tier_preferences(db, current_user_id)
    rows = (
        db.query(FavoriteStrategy)
        .filter(FavoriteStrategy.user_id.in_(admin_user_ids))
        .order_by(
            FavoriteStrategy.symbol.asc(),
            FavoriteStrategy.timeframe.asc(),
            FavoriteStrategy.id.asc(),
        )
        .all()
    )
    return [
        _favorite_response(
            row,
            include_secrets=False,
            tier_override=tier_by_favorite_id.get(int(row.id)),
        )
        for row in rows
    ]


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
        include_secrets = can_view_strategy_secrets(db, current_user_id)
        return _favorite_response(db_favorite, include_secrets=include_secrets)
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
    favorite = db.query(FavoriteStrategy).filter(FavoriteStrategy.id == favorite_id).first()
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")

    # Update only fields that were explicitly sent (exclude_unset so we can set tier to null)
    updates = update_data.model_dump(exclude_unset=True)
    tier_override = _TIER_UNSET
    include_secrets = can_view_strategy_secrets(db, current_user_id)
    owns_favorite = str(favorite.user_id) == str(current_user_id)
    admin_catalog_ids = set(_admin_catalog_user_ids(db, exclude_user_id=current_user_id))

    if not owns_favorite:
        if str(favorite.user_id) not in admin_catalog_ids or include_secrets:
            raise HTTPException(status_code=404, detail="Favorite not found")
        if set(updates.keys()) - {"tier"}:
            raise HTTPException(
                status_code=403,
                detail="Common users can update only their own star tier for admin favorites",
            )

    if "tier" in updates:
        tier_val = updates["tier"]
        if tier_val is not None and tier_val not in (1, 2, 3):
            raise HTTPException(status_code=400, detail="Tier must be 1, 2, 3 or null (Sem tier)")
        if owns_favorite:
            favorite.tier = tier_val
        else:
            _upsert_strategy_tier_preference(
                db,
                user_id=current_user_id,
                favorite_id=favorite_id,
                tier=tier_val,
            )
            tier_override = tier_val
    if update_data.name is not None:
        favorite.name = update_data.name
    if update_data.notes is not None:
        favorite.notes = update_data.notes

    db.commit()
    db.refresh(favorite)
    return _favorite_response(
        favorite,
        include_secrets=include_secrets,
        tier_override=tier_override,
    )


@router.delete("/{favorite_id}")
def delete_favorite(
    favorite_id: int,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a favorite strategy"""
    favorite = (
        db.query(FavoriteStrategy)
        .filter(
            FavoriteStrategy.id == favorite_id,
            FavoriteStrategy.user_id == current_user_id,
        )
        .first()
    )
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")
    db.delete(favorite)
    db.commit()
    return {"message": "Favorite deleted"}
