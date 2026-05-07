from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import asyncio
import json
from datetime import datetime, timezone

from app.database import get_db
from app.models import FavoriteStrategy, MonitorStrategyPreference, User
from app.middleware.authMiddleware import ADMIN_EMAILS, get_current_user, is_admin_email
from app.schemas.favorite import (
    FavoriteStrategyCreate,
    FavoriteStrategyResponse,
    FavoriteStrategyUpdate,
)
from app.services.combo_optimizer import ComboOptimizer
from app.services.market_data_providers import resolve_data_source_for_symbol
from app.services.strategy_secret_visibility import (
    can_view_strategy_secrets,
    redact_favorite_strategy_payload,
)

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


class ExistsResponse(BaseModel):
    exists: bool


class FavoriteTradesResponse(BaseModel):
    favorite_id: int
    trades: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    metrics_match: bool
    metrics_deltas: Dict[str, Dict[str, float]]
    regenerated: bool
    candles: List[Dict[str, Any]] = Field(default_factory=list)
    indicator_data: Dict[str, Any] = Field(default_factory=dict)
    execution_mode: Optional[str] = None


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


_METRICS_TO_COMPARE = (
    "total_trades",
    "win_rate",
    "total_return",
    "total_return_pct",
    "max_drawdown",
    "profit_factor",
)


def _favorite_metric_summary(metrics: Dict[str, Any]) -> Dict[str, Any]:
    return {key: metrics.get(key) for key in _METRICS_TO_COMPARE if key in metrics}


def _numeric_metric(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _compare_favorite_metrics(
    stored_metrics: Dict[str, Any], regenerated_metrics: Dict[str, Any]
) -> tuple[bool, Dict[str, Dict[str, float]]]:
    deltas: Dict[str, Dict[str, float]] = {}
    for key in _METRICS_TO_COMPARE:
        stored = _numeric_metric(stored_metrics.get(key))
        regenerated = _numeric_metric(regenerated_metrics.get(key))
        if stored is None or regenerated is None:
            continue
        delta = abs(stored - regenerated)
        tolerance = max(0.0001, abs(stored) * 0.001)
        if delta > tolerance:
            deltas[key] = {
                "stored": stored,
                "regenerated": regenerated,
                "delta": delta,
            }
    return len(deltas) == 0, deltas


def _analysis_candles_from_metrics(metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
    candles = metrics.get("analysis_candles")
    return candles if isinstance(candles, list) else []


def _analysis_indicators_from_metrics(metrics: Dict[str, Any]) -> Dict[str, Any]:
    indicator_data = metrics.get("analysis_indicator_data")
    return indicator_data if isinstance(indicator_data, dict) else {}


def _analysis_metrics_deltas_from_metrics(metrics: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    deltas = metrics.get("trades_metrics_deltas")
    return deltas if isinstance(deltas, dict) else {}


def _fixed_optimization_ranges(parameters: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    ranges: Dict[str, Dict[str, Any]] = {}
    for key, value in parameters.items():
        if key in {"data_source", "direction"} or isinstance(value, bool):
            continue
        if isinstance(value, int):
            ranges[key] = {"min": value, "max": value, "step": 1}
        elif isinstance(value, float):
            ranges[key] = {"min": value, "max": value, "step": 0.0001}
    return ranges


def _legacy_regeneration_end_date(favorite: FavoriteStrategy) -> str | None:
    if favorite.end_date:
        return favorite.end_date
    if favorite.period_type == "all" and favorite.created_at:
        return favorite.created_at.date().isoformat()
    return None


async def _run_favorite_optimization(favorite: FavoriteStrategy) -> Dict[str, Any]:
    parameters = favorite.parameters if isinstance(favorite.parameters, dict) else {}
    direction = str(parameters.get("direction") or "long").lower()
    if direction not in ("long", "short"):
        direction = "long"
    data_source = parameters.get("data_source") or resolve_data_source_for_symbol(
        favorite.symbol, None
    )
    optimizer = ComboOptimizer()
    return await asyncio.to_thread(
        optimizer.run_optimization,
        template_name=favorite.strategy_name,
        symbol=favorite.symbol,
        timeframe=favorite.timeframe,
        data_source=data_source,
        start_date=favorite.start_date,
        end_date=_legacy_regeneration_end_date(favorite),
        custom_ranges=_fixed_optimization_ranges(parameters),
        deep_backtest=True,
        direction=direction,
    )


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


@router.get("/{favorite_id}/trades", response_model=FavoriteTradesResponse)
async def get_favorite_trades(
    favorite_id: int,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    favorite = db.query(FavoriteStrategy).filter(FavoriteStrategy.id == favorite_id).first()
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")

    include_secrets = can_view_strategy_secrets(db, current_user_id)
    owns_favorite = str(favorite.user_id) == str(current_user_id)
    if not owns_favorite or not include_secrets:
        raise HTTPException(status_code=403, detail="Favorite trades are protected")

    favorite = _normalize_favorite_json_fields(favorite)
    metrics = favorite.metrics if isinstance(favorite.metrics, dict) else {}
    saved_trades = metrics.get("trades")
    saved_trade_count = _numeric_metric(metrics.get("total_trades"))
    history_cached = metrics.get("trades_history_cached") is True
    has_chart_context = len(_analysis_candles_from_metrics(metrics)) > 0
    if isinstance(saved_trades, list) and (
        has_chart_context or history_cached or int(saved_trade_count or 0) <= 0
    ):
        saved_metrics_match = metrics.get("trades_metrics_match")
        return FavoriteTradesResponse(
            favorite_id=favorite_id,
            trades=saved_trades,
            metrics=metrics,
            metrics_match=saved_metrics_match if isinstance(saved_metrics_match, bool) else True,
            metrics_deltas=_analysis_metrics_deltas_from_metrics(metrics),
            regenerated=False,
            candles=_analysis_candles_from_metrics(metrics),
            indicator_data=_analysis_indicators_from_metrics(metrics),
            execution_mode=(
                metrics.get("analysis_execution_mode")
                if isinstance(metrics.get("analysis_execution_mode"), str)
                else None
            ),
        )

    result = await _run_favorite_optimization(favorite)
    regenerated_trades = result.get("trades") or []
    regenerated_metrics = result.get("best_metrics") or result.get("metrics") or {}
    metrics_match, metrics_deltas = _compare_favorite_metrics(metrics, regenerated_metrics)
    analysis_candles = result.get("candles") if isinstance(result.get("candles"), list) else []
    analysis_indicator_data = (
        result.get("indicator_data") if isinstance(result.get("indicator_data"), dict) else {}
    )
    updated_metrics = {
        **metrics,
        **regenerated_metrics,
        "trades": regenerated_trades,
        "trades_history_cached": True,
        "trades_metrics_match": True,
        "trades_metrics_deltas": metrics_deltas,
        "trades_reconciled_from_mismatch": not metrics_match,
        "analysis_candles": analysis_candles,
        "analysis_indicator_data": analysis_indicator_data,
        "analysis_execution_mode": result.get("execution_mode"),
    }
    if not metrics_match:
        updated_metrics["trades_previous_summary"] = _favorite_metric_summary(metrics)
        updated_metrics["trades_reconciled_summary"] = _favorite_metric_summary(regenerated_metrics)
        updated_metrics["trades_reconciled_at"] = datetime.now(timezone.utc).isoformat()
    favorite.metrics = updated_metrics
    db.commit()

    return FavoriteTradesResponse(
        favorite_id=favorite_id,
        trades=regenerated_trades,
        metrics=updated_metrics,
        metrics_match=True,
        metrics_deltas=metrics_deltas,
        regenerated=True,
        candles=analysis_candles,
        indicator_data=analysis_indicator_data,
        execution_mode=result.get("execution_mode"),
    )


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
