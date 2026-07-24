from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models_signal_history import SAO_PAULO_TZ, SignalHistory, sao_paulo_now
from app.schemas.signal import RiskProfile, Signal, SignalType
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


def _convert_utc_to_sao_paulo(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(SAO_PAULO_TZ)


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


def save_signal_to_history(signal: Signal, user_id: str | None = None) -> None:
    """Save a generated signal to the history table (sync, called from async context)."""
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


# Backward-compatible private alias used by existing call sites.
_save_signal_to_history = save_signal_to_history
