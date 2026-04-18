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
from app.middleware.authMiddleware import get_current_user, get_current_user_optional
from app.services import binance_service, sentiment_service
from app.services.system_preferences_service import (
    SIGNAL_HISTORY_ALLOW_AGGRESSIVE_KEY,
    SIGNAL_HISTORY_ALLOW_BUY_KEY,
    SIGNAL_HISTORY_ALLOW_CONSERVATIVE_KEY,
    SIGNAL_HISTORY_ALLOW_MODERATE_KEY,
    SIGNAL_HISTORY_ALLOW_NEUTRAL_MACD_KEY,
    SIGNAL_HISTORY_ALLOW_SELL_KEY,
    SIGNAL_HISTORY_MAX_REWARD_RISK_KEY,
    SIGNAL_HISTORY_MAX_RSI_KEY,
    SIGNAL_HISTORY_MIN_CONFIDENCE_KEY,
    SIGNAL_HISTORY_MIN_REWARD_RISK_KEY,
    SIGNAL_HISTORY_MIN_RSI_KEY,
    get_system_preference_bool,
    get_system_preference_float,
    get_system_preference_int,
)

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


class OpenSignalPositionItem(BaseModel):
    id: str
    asset: str
    confidence: int
    target_price: float
    stop_loss: float
    created_at: datetime
    risk_profile: str
    status: str
    entry_price: float
    current_price: float | None = None
    pnl_percent: float | None = None
    updated_at: datetime | None = None


class OpenSignalPositionsResponse(BaseModel):
    positions: list[OpenSignalPositionItem]
    total: int
    cached_at: datetime | None = None
    is_stale: bool = False


class UpdateStatusRequest(BaseModel):
    status: str
    exit_price: float | None = None
    quantity: float | None = None


@dataclass(frozen=True)
class HistoryQualityGateSettings:
    min_confidence: int
    min_reward_risk: float
    max_reward_risk: float
    min_rsi: float
    max_rsi: float
    allow_neutral_macd: bool
    allow_buy: bool
    allow_sell: bool
    allow_conservative: bool
    allow_moderate: bool
    allow_aggressive: bool


QUALITY_GATE_MIN_CONFIDENCE = 55
QUALITY_GATE_MIN_REWARD_RISK = 1.2
QUALITY_GATE_MAX_REWARD_RISK = 5.0
QUALITY_GATE_MIN_RSI = 30.0
QUALITY_GATE_MAX_RSI = 34.0
QUALITY_GATE_ALLOW_NEUTRAL_MACD = True
QUALITY_GATE_ALLOW_BUY = True
QUALITY_GATE_ALLOW_SELL = False
QUALITY_GATE_ALLOW_CONSERVATIVE = False
QUALITY_GATE_ALLOW_MODERATE = True
QUALITY_GATE_ALLOW_AGGRESSIVE = True


def _get_history_quality_gate_settings(db: Session) -> HistoryQualityGateSettings:
    return HistoryQualityGateSettings(
        min_confidence=get_system_preference_int(
            db, SIGNAL_HISTORY_MIN_CONFIDENCE_KEY, QUALITY_GATE_MIN_CONFIDENCE
        ),
        min_reward_risk=get_system_preference_float(
            db, SIGNAL_HISTORY_MIN_REWARD_RISK_KEY, QUALITY_GATE_MIN_REWARD_RISK
        ),
        max_reward_risk=get_system_preference_float(
            db, SIGNAL_HISTORY_MAX_REWARD_RISK_KEY, QUALITY_GATE_MAX_REWARD_RISK
        ),
        min_rsi=get_system_preference_float(db, SIGNAL_HISTORY_MIN_RSI_KEY, QUALITY_GATE_MIN_RSI),
        max_rsi=get_system_preference_float(db, SIGNAL_HISTORY_MAX_RSI_KEY, QUALITY_GATE_MAX_RSI),
        allow_neutral_macd=get_system_preference_bool(
            db,
            SIGNAL_HISTORY_ALLOW_NEUTRAL_MACD_KEY,
            QUALITY_GATE_ALLOW_NEUTRAL_MACD,
        ),
        allow_buy=get_system_preference_bool(
            db, SIGNAL_HISTORY_ALLOW_BUY_KEY, QUALITY_GATE_ALLOW_BUY
        ),
        allow_sell=get_system_preference_bool(
            db, SIGNAL_HISTORY_ALLOW_SELL_KEY, QUALITY_GATE_ALLOW_SELL
        ),
        allow_conservative=get_system_preference_bool(
            db,
            SIGNAL_HISTORY_ALLOW_CONSERVATIVE_KEY,
            QUALITY_GATE_ALLOW_CONSERVATIVE,
        ),
        allow_moderate=get_system_preference_bool(
            db, SIGNAL_HISTORY_ALLOW_MODERATE_KEY, QUALITY_GATE_ALLOW_MODERATE
        ),
        allow_aggressive=get_system_preference_bool(
            db,
            SIGNAL_HISTORY_ALLOW_AGGRESSIVE_KEY,
            QUALITY_GATE_ALLOW_AGGRESSIVE,
        ),
    )


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


def _calculate_reward_risk(signal: Signal) -> float | None:
    if signal.entry_price is None:
        return None

    entry_price = float(signal.entry_price)
    if entry_price <= 0:
        return None

    if signal.type == SignalType.BUY:
        reward = signal.target_price - entry_price
        risk = entry_price - signal.stop_loss
    elif signal.type == SignalType.SELL:
        reward = entry_price - signal.target_price
        risk = signal.stop_loss - entry_price
    else:
        return None

    if risk <= 0 or reward <= 0:
        return None
    return reward / risk


def _passes_history_quality_gate(signal: Signal, db: Session) -> bool:
    settings = _get_history_quality_gate_settings(db)
    return _signal_passes_quality_gate(signal, settings)


def _signal_passes_quality_gate(signal: Signal, settings: HistoryQualityGateSettings) -> bool:
    if signal.type == SignalType.HOLD:
        return False
    if signal.type == SignalType.BUY and not settings.allow_buy:
        return False
    if signal.type == SignalType.SELL and not settings.allow_sell:
        return False
    if signal.risk_profile == RiskProfile.conservative and not settings.allow_conservative:
        return False
    if signal.risk_profile == RiskProfile.moderate and not settings.allow_moderate:
        return False
    if signal.risk_profile == RiskProfile.aggressive and not settings.allow_aggressive:
        return False
    if signal.confidence < settings.min_confidence:
        return False
    if not settings.allow_neutral_macd and str(signal.indicators.macd).lower() == "neutral":
        return False
    rsi = float(signal.indicators.rsi)
    if rsi < settings.min_rsi or rsi > settings.max_rsi:
        return False
    reward_risk = _calculate_reward_risk(signal)
    if (
        reward_risk is None
        or reward_risk < settings.min_reward_risk
        or reward_risk > settings.max_reward_risk
    ):
        return False
    return True


def _history_row_to_signal(row: SignalHistory) -> Signal | None:
    indicators_raw: dict[str, Any] | None = None
    if row.indicators:
        try:
            indicators_raw = json.loads(row.indicators)
        except Exception:
            indicators_raw = None
    if not indicators_raw:
        return None

    try:
        return Signal(
            id=row.id,
            asset=row.asset,
            type=SignalType(str(row.type).upper()),
            confidence=int(row.confidence),
            target_price=float(row.target_price),
            stop_loss=float(row.stop_loss),
            indicators=indicators_raw,
            created_at=_ensure_sao_paulo(row.created_at) or datetime.now(SAO_PAULO_TZ),
            risk_profile=RiskProfile(str(row.risk_profile).lower()),
            entry_price=row.entry_price,
        )
    except Exception:
        return None


def _history_row_passes_quality_gate(
    row: SignalHistory, settings: HistoryQualityGateSettings
) -> bool:
    signal = _history_row_to_signal(row)
    if signal is None:
        return False
    return _signal_passes_quality_gate(signal, settings)


def _apply_history_status_filter(query, status: str):
    normalized = status.strip().lower()
    if normalized in {"open", "aberto"}:
        return query.filter(SignalHistory.status == "ativo")
    if normalized in {"closed", "fechado"}:
        return query.filter(SignalHistory.status.in_(["disparado", "expirado", "cancelado"]))
    return query.filter(SignalHistory.status == status)


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
    description="Returns actionable BUY/SELL signals generated from Binance OHLCV data and temporary heuristics until Card #55 ships the final ML ensemble.",
)
async def get_signals(
    current_user_id: str | None = Depends(get_current_user_optional),
    type: SignalType | None = Query(default=None, description="Filter by BUY or SELL"),
    confidence_min: int | None = Query(
        default=None, ge=0, le=100, description="Minimum confidence threshold"
    ),
    asset: str | None = Query(default=None, description="Binance symbol, e.g. BTCUSDT"),
    risk_profile: RiskProfile = Query(
        default=RiskProfile.moderate, description="Signal risk profile"
    ),
    limit: int = Query(default=20, ge=1, le=50, description="Maximum number of signals to return"),
):
    return await binance_service.build_signal_feed(
        signal_type=type,
        confidence_min=confidence_min,
        asset=asset,
        risk_profile=risk_profile,
        limit=limit,
        user_id=current_user_id,
    )


@router.get(
    "/latest",
    response_model=SignalListResponse,
    summary="Latest high-confidence signals",
    description="Returns the latest five signals with confidence >= 70 across default assets and all supported risk profiles.",
)
async def get_latest_signals(current_user_id: str | None = Depends(get_current_user_optional)):
    return await binance_service.get_latest_high_confidence_signals(user_id=current_user_id)


@router.get(
    "/open-positions",
    response_model=OpenSignalPositionsResponse,
    summary="Open BUY positions for the authenticated user",
)
async def get_open_signal_positions(current_user_id: str = Depends(get_current_user)):
    db: Session = SessionLocal()
    try:
        rows = (
            db.query(SignalHistory)
            .filter(
                SignalHistory.archived == "no",
                SignalHistory.user_id == current_user_id,
                SignalHistory.type == "BUY",
                SignalHistory.status == "ativo",
            )
            .order_by(SignalHistory.created_at.desc())
            .all()
        )
    finally:
        db.close()

    asset_list = sorted({str(row.asset) for row in rows if row.asset})
    current_prices, cached_at, is_stale = await binance_service.get_latest_prices(asset_list)

    positions: list[OpenSignalPositionItem] = []
    for row in rows:
        if row.entry_price is None:
            continue

        current_price = current_prices.get(str(row.asset))
        pnl_percent = None
        if current_price is not None and row.entry_price > 0:
            pnl_percent = round(((current_price - row.entry_price) / row.entry_price) * 100, 4)

        positions.append(
            OpenSignalPositionItem(
                id=row.id,
                asset=row.asset,
                confidence=row.confidence,
                target_price=row.target_price,
                stop_loss=row.stop_loss,
                created_at=_ensure_sao_paulo(row.created_at),
                risk_profile=row.risk_profile,
                status=row.status,
                entry_price=row.entry_price,
                current_price=current_price,
                pnl_percent=pnl_percent,
                updated_at=_ensure_sao_paulo(row.updated_at),
            )
        )

    return OpenSignalPositionsResponse(
        positions=positions,
        total=len(positions),
        cached_at=cached_at,
        is_stale=is_stale,
    )


# IMPORTANT: /history routes must come BEFORE /{signal_id} to avoid FastAPI matching "history" as a signal_id
@router.get(
    "/history",
    response_model=SignalHistoryResponse,
    summary="Signal history with filters and pagination",
)
async def get_signal_history(
    current_user_id: str = Depends(get_current_user),
    asset: str | None = Query(default=None, description="Filter by asset, e.g. BTCUSDT"),
    type: str | None = Query(default=None, description="Filter by BUY or SELL"),
    status: str | None = Query(
        default=None, description="Filter by status: open/closed or raw values"
    ),
    risk_profile: str | None = Query(
        default=None, description="Filter by risk profile: conservative, moderate, aggressive"
    ),
    data_inicio: str | None = Query(default=None, description="Start date ISO, e.g. 2026-01-01"),
    data_fim: str | None = Query(default=None, description="End date ISO, e.g. 2026-03-28"),
    confidence_min: int | None = Query(default=None, ge=0, le=100),
    pnl_filter: str | None = Query(
        default=None, description="Filter by pnl quality: positive, negative, realized"
    ),
    sort_by: str = Query(default="created_at", description="Sort by created_at, confidence, pnl"),
    sort_order: str = Query(default="desc", description="Sort direction: asc or desc"),
    apply_quality_gate: bool = Query(
        default=True, description="Apply current history gate to legacy records"
    ),
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
            query = _apply_history_status_filter(query, status)
        if risk_profile:
            query = query.filter(SignalHistory.risk_profile == risk_profile)
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
        if pnl_filter == "positive":
            query = query.filter(SignalHistory.pnl.isnot(None), SignalHistory.pnl > 0)
        elif pnl_filter == "negative":
            query = query.filter(SignalHistory.pnl.isnot(None), SignalHistory.pnl < 0)
        elif pnl_filter == "realized":
            query = query.filter(SignalHistory.pnl.isnot(None))

        rows = query.all()

        if apply_quality_gate:
            settings = _get_history_quality_gate_settings(db)
            rows = [row for row in rows if _history_row_passes_quality_gate(row, settings)]

        reverse = sort_order != "asc"
        if sort_by == "confidence":
            rows.sort(key=lambda row: (row.confidence, row.created_at), reverse=reverse)
        elif sort_by == "pnl":
            rows.sort(
                key=lambda row: (
                    (row.pnl if row.pnl is not None else float("-inf")),
                    row.created_at,
                ),
                reverse=reverse,
            )
        else:
            rows.sort(key=lambda row: row.created_at, reverse=reverse)

        total = len(rows)
        rows = rows[offset : offset + limit]

        signals = [_build_history_item(row) for row in rows]
        return SignalHistoryResponse(signals=signals, total=total, limit=limit, offset=offset)
    finally:
        db.close()


@router.get(
    "/history/{signal_id}",
    response_model=SignalHistoryItem,
    summary="Get a single signal from history",
)
async def get_signal_history_detail(
    signal_id: str,
    current_user_id: str = Depends(get_current_user),
):
    db: Session = SessionLocal()
    try:
        row = db.query(SignalHistory).filter(SignalHistory.id == signal_id).first()
        if not row:
            raise HTTPException(status_code=404, detail="Signal not found")
        # Multi-tenant: usuário só pode ver seu próprio signal
        if row.user_id != current_user_id:
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
    current_user_id: str = Depends(get_current_user),
):
    db: Session = SessionLocal()
    try:
        row = db.query(SignalHistory).filter(SignalHistory.id == signal_id).first()
        if not row:
            raise HTTPException(status_code=404, detail="Signal not found")
        # Multi-tenant: usuário só pode alterar seu próprio signal
        if row.user_id != current_user_id:
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
    asset: str | None = Query(default=None),
    type: str | None = Query(default=None),
    status: str | None = Query(default=None),
    risk_profile: str | None = Query(default=None),
    data_inicio: str | None = Query(default=None),
    data_fim: str | None = Query(default=None),
    confidence_min: int | None = Query(default=None, ge=0, le=100),
    pnl_filter: str | None = Query(default=None),
    apply_quality_gate: bool = Query(
        default=True, description="Apply current history gate to legacy records"
    ),
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
            query = _apply_history_status_filter(query, status)
        if risk_profile:
            query = query.filter(SignalHistory.risk_profile == risk_profile)

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
        if pnl_filter == "positive":
            query = query.filter(SignalHistory.pnl.isnot(None), SignalHistory.pnl > 0)
        elif pnl_filter == "negative":
            query = query.filter(SignalHistory.pnl.isnot(None), SignalHistory.pnl < 0)
        elif pnl_filter == "realized":
            query = query.filter(SignalHistory.pnl.isnot(None))

        rows = query.all()
        if apply_quality_gate:
            settings = _get_history_quality_gate_settings(db)
            rows = [row for row in rows if _history_row_passes_quality_gate(row, settings)]
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
            return

        if not _passes_history_quality_gate(signal, db):
            return

        if signal.type.value == "SELL":
            if not user_id:
                return

            open_buy = (
                db.query(SignalHistory)
                .filter(
                    SignalHistory.user_id == user_id,
                    SignalHistory.archived == "no",
                    SignalHistory.asset == signal.asset,
                    SignalHistory.risk_profile == signal.risk_profile.value,
                    SignalHistory.type == "BUY",
                    SignalHistory.status == "ativo",
                )
                .order_by(SignalHistory.created_at.desc())
                .first()
            )
            if open_buy is None or open_buy.entry_price is None:
                return

            exit_price = signal.entry_price or signal.target_price
            pnl_pct = ((exit_price - open_buy.entry_price) / open_buy.entry_price) * 100
            open_buy.status = "disparado"
            open_buy.exit_price = exit_price
            open_buy.pnl = round(pnl_pct, 4)
            open_buy.updated_at = sao_paulo_now()
            db.commit()
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
