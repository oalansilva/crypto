from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models_signal_history import SAO_PAULO_TZ, SignalHistory, sao_paulo_now
from app.schemas.signal import RiskProfile, Signal, SignalListResponse, SignalType
from app.middleware.authMiddleware import get_current_user
from app.services import binance_service, sentiment_service

router = APIRouter(prefix="/api/signals", tags=["signals"])


# --- Pydantic schemas for history ---


class SignalHistoryItem(BaseModel):
    id: str
    asset: str
    type: str
    confidence: int
    target_price: float
    stop_loss: float
    indicators: dict[str, Any] | None = None
    created_at: datetime
    risk_profile: str
    status: str
    entry_price: float | None = None
    exit_price: float | None = None
    quantity: float | None = None
    pnl: float | None = None
    trigger_price: float | None = None
    updated_at: datetime | None = None
    user_id: str | None = None


class SignalHistoryResponse(BaseModel):
    signals: list[SignalHistoryItem]
    total: int
    limit: int
    offset: int


class SignalStatsResponse(BaseModel):
    total_signals: int
    win_rate: float
    avg_confidence: float
    expired_rate: float
    total_pnl: float


class UpdateStatusRequest(BaseModel):
    status: str
    exit_price: float | None = None
    quantity: float | None = None


def _ensure_sao_paulo(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=SAO_PAULO_TZ)
    return dt.astimezone(SAO_PAULO_TZ)


def _convert_utc_to_sao_paulo(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(SAO_PAULO_TZ)


def _parse_history_datetime(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=SAO_PAULO_TZ)
    return parsed.astimezone(SAO_PAULO_TZ)


def _build_history_item(row: SignalHistory) -> SignalHistoryItem:
    indicators = None
    if row.indicators:
        try:
            indicators = json.loads(row.indicators)
        except Exception:
            indicators = None

    return SignalHistoryItem(
        id=row.id,
        asset=row.asset,
        type=row.type,
        confidence=row.confidence,
        target_price=row.target_price,
        stop_loss=row.stop_loss,
        indicators=indicators,
        created_at=_ensure_sao_paulo(row.created_at),
        risk_profile=row.risk_profile,
        status=row.status,
        entry_price=row.entry_price,
        exit_price=row.exit_price,
        quantity=row.quantity,
        pnl=row.pnl,
        trigger_price=row.trigger_price,
        updated_at=_ensure_sao_paulo(row.updated_at),
        user_id=row.user_id,
    )


def _get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@dataclass
class SentimentResponse:
    score: int
    components: dict[str, int]
    signal: str


@router.get(
    "/sentiment",
    response_model=SentimentResponse,
    summary="Market sentiment score",
    description="Returns a 0-100 sentiment score combining Fear & Greed Index (30%), CoinGecko news (40%) and Reddit-style analysis (30%).",
)
async def get_sentiment():
    result = await sentiment_service.get_market_sentiment()
    return SentimentResponse(
        score=result.score,
        components=result.components,
        signal=result.signal,
    )


@router.get(
    "",
    response_model=SignalListResponse,
    summary="List trading signals",
    description="Returns BUY/SELL/HOLD signals generated from Binance OHLCV data and temporary heuristics until Card #55 ships the final ML ensemble.",
)
async def get_signals(
    type: SignalType | None = Query(default=None, description="Filter by BUY, SELL or HOLD"),
    confidence_min: int | None = Query(default=None, ge=0, le=100, description="Minimum confidence threshold"),
    asset: str | None = Query(default=None, description="Binance symbol, e.g. BTCUSDT"),
    risk_profile: RiskProfile = Query(default=RiskProfile.moderate, description="Signal risk profile"),
    limit: int = Query(default=20, ge=1, le=50, description="Maximum number of signals to return"),
):
    sentiment = await sentiment_service.get_market_sentiment()
    return await binance_service.build_signal_feed(
        signal_type=type,
        confidence_min=confidence_min,
        asset=asset,
        risk_profile=risk_profile,
        limit=limit,
        sentiment_score=sentiment.score,
    )


@router.get(
    "/latest",
    response_model=SignalListResponse,
    summary="Latest high-confidence signals",
    description="Returns the latest five signals with confidence >= 70 across default assets and all supported risk profiles.",
)
async def get_latest_signals():
    return await binance_service.get_latest_high_confidence_signals()


# IMPORTANT: /history routes must come BEFORE /{signal_id} to avoid FastAPI matching "history" as a signal_id
@router.get(
    "/history",
    response_model=SignalHistoryResponse,
    summary="Signal history with filters and pagination",
)
async def get_signal_history(
    current_user_id: str = Depends(get_current_user),
    asset: str | None = Query(default=None, description="Filter by asset, e.g. BTCUSDT"),
    type: str | None = Query(default=None, description="Filter by BUY, SELL or HOLD"),
    status: str | None = Query(default=None, description="Filter by status: ativo, disparado, expirado, cancelado"),
    data_inicio: str | None = Query(default=None, description="Start date ISO, e.g. 2026-01-01"),
    data_fim: str | None = Query(default=None, description="End date ISO, e.g. 2026-03-28"),
    confidence_min: int | None = Query(default=None, ge=0, le=100),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    db: Session = SessionLocal()
    try:
        query = db.query(SignalHistory).filter(SignalHistory.archived == "no")

        # Multi-tenant: filtrar por user_id do JWT
        query = query.filter(SignalHistory.user_id == current_user_id)

        if asset:
            query = query.filter(SignalHistory.asset == asset.upper())
        if type:
            query = query.filter(SignalHistory.type == type.upper())
        if status:
            query = query.filter(SignalHistory.status == status)
        if data_inicio:
            try:
                dt_inicio = _parse_history_datetime(data_inicio)
                query = query.filter(SignalHistory.created_at >= dt_inicio)
            except ValueError:
                pass
        if data_fim:
            try:
                dt_fim = _parse_history_datetime(data_fim)
                query = query.filter(SignalHistory.created_at <= dt_fim)
            except ValueError:
                pass
        if confidence_min is not None:
            query = query.filter(SignalHistory.confidence >= confidence_min)

        total = query.count()
        rows = query.order_by(SignalHistory.created_at.desc()).offset(offset).limit(limit).all()

        signals = [_build_history_item(row) for row in rows]
        return SignalHistoryResponse(signals=signals, total=total, limit=limit, offset=offset)
    finally:
        db.close()


@router.get(
    "/history/{signal_id}",
    response_model=SignalHistoryItem,
    summary="Get a single signal from history",
)
async def get_signal_history_detail(signal_id: str):
    db: Session = SessionLocal()
    try:
        row = db.query(SignalHistory).filter(SignalHistory.id == signal_id).first()
        if not row:
            raise HTTPException(status_code=404, detail="Signal not found")
        return _build_history_item(row)
    finally:
        db.close()


@router.put(
    "/history/{signal_id}/status",
    response_model=SignalHistoryItem,
    summary="Update signal status and optionally set PnL",
)
async def update_signal_status(
    signal_id: str,
    req: UpdateStatusRequest,
):
    db: Session = SessionLocal()
    try:
        row = db.query(SignalHistory).filter(SignalHistory.id == signal_id).first()
        if not row:
            raise HTTPException(status_code=404, detail="Signal not found")

        row.status = req.status
        row.updated_at = sao_paulo_now()

        if req.exit_price is not None:
            row.exit_price = req.exit_price
        if req.quantity is not None:
            row.quantity = req.quantity

        # Calculate PnL
        if row.entry_price is not None and req.exit_price is not None and req.quantity is not None:
            row.pnl = (req.exit_price - row.entry_price) * req.quantity

        db.commit()
        db.refresh(row)

        return _build_history_item(row)
    finally:
        db.close()


@router.get(
    "/stats",
    response_model=SignalStatsResponse,
    summary="Signal history statistics",
)
async def get_signal_stats(
    current_user_id: str = Depends(get_current_user),
    data_inicio: str | None = Query(default=None),
    data_fim: str | None = Query(default=None),
):
    db: Session = SessionLocal()
    try:
        query = db.query(SignalHistory).filter(SignalHistory.archived == "no")

        # Multi-tenant: filtrar por user_id do JWT
        query = query.filter(SignalHistory.user_id == current_user_id)

        if data_inicio:
            try:
                dt_inicio = _parse_history_datetime(data_inicio)
                query = query.filter(SignalHistory.created_at >= dt_inicio)
            except ValueError:
                pass
        if data_fim:
            try:
                dt_fim = _parse_history_datetime(data_fim)
                query = query.filter(SignalHistory.created_at <= dt_fim)
            except ValueError:
                pass

        rows = query.all()
        total = len(rows)

        if total == 0:
            return SignalStatsResponse(
                total_signals=0,
                win_rate=0.0,
                avg_confidence=0.0,
                expired_rate=0.0,
                total_pnl=0.0,
            )

        # Win rate: disparado signals with positive pnl
        disparados = [r for r in rows if r.status == "disparado"]
        winners = [r for r in disparados if r.pnl is not None and r.pnl > 0]
        win_rate = (len(winners) / len(disparados) * 100) if disparados else 0.0

        # Avg confidence
        avg_confidence = sum(r.confidence for r in rows) / total

        # Expired rate
        expirados = [r for r in rows if r.status == "expirado"]
        expired_rate = (len(expirados) / total * 100) if total > 0 else 0.0

        # Total PnL
        total_pnl = sum(r.pnl for r in rows if r.pnl is not None)

        return SignalStatsResponse(
            total_signals=total,
            win_rate=round(win_rate, 2),
            avg_confidence=round(avg_confidence, 2),
            expired_rate=round(expired_rate, 2),
            total_pnl=round(total_pnl, 6),
        )
    finally:
        db.close()


# NOTE: This route must come AFTER /history routes
@router.get(
    "/{signal_id}",
    response_model=Signal,
    summary="Get a signal by id (live, not from history)",
)
async def get_signal_by_id(signal_id: str):
    try:
        return await binance_service.get_signal_detail(signal_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Signal not found") from exc


def _save_signal_to_history(signal: Signal, user_id: str | None = None) -> None:
    """Save a generated signal to the history table (sync, called from async context)."""
    import json
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        existing = db.query(SignalHistory).filter(SignalHistory.id == signal.id).first()
        if existing:
            db.close()
            return

        # Skip SELL signals - they are not actual trades, just market timing indicators
        if signal.type.value == "SELL":
            db.close()
            return

        entry_price = signal.entry_price

        record = SignalHistory(
            id=signal.id,
            asset=signal.asset,
            type=signal.type.value,
            confidence=signal.confidence,
            target_price=signal.target_price,
            stop_loss=signal.stop_loss,
            indicators=json.dumps(signal.indicators.model_dump(by_alias=True), default=str),
            created_at=_convert_utc_to_sao_paulo(signal.created_at),
            risk_profile=signal.risk_profile.value,
            status="ativo",
            entry_price=entry_price,
            user_id=user_id,
        )
        db.add(record)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[signal_history] Failed to save signal {signal.id}: {e}")
    finally:
        db.close()
