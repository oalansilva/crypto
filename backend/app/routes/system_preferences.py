from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.authMiddleware import get_current_admin
from app.services.system_preferences_service import (
    MINIMAX_API_KEY_KEY,
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
    delete_system_preference_value,
    get_system_preference_bool,
    get_system_preference_float,
    get_system_preference_int,
    get_system_preference_value,
    mask_secret,
    set_optional_system_preference_value,
    set_system_preference_value,
)

router = APIRouter(prefix="/api/system/preferences", tags=["system-preferences"])

DEFAULT_SIGNAL_HISTORY_MIN_CONFIDENCE = 55
DEFAULT_SIGNAL_HISTORY_MIN_REWARD_RISK = 1.2
DEFAULT_SIGNAL_HISTORY_MAX_REWARD_RISK = 5.0
DEFAULT_SIGNAL_HISTORY_MIN_RSI = 30
DEFAULT_SIGNAL_HISTORY_MAX_RSI = 34
DEFAULT_SIGNAL_HISTORY_ALLOW_NEUTRAL_MACD = True
DEFAULT_SIGNAL_HISTORY_ALLOW_BUY = True
DEFAULT_SIGNAL_HISTORY_ALLOW_SELL = False
DEFAULT_SIGNAL_HISTORY_ALLOW_CONSERVATIVE = False
DEFAULT_SIGNAL_HISTORY_ALLOW_MODERATE = True
DEFAULT_SIGNAL_HISTORY_ALLOW_AGGRESSIVE = True


class SystemPreferencesResponse(BaseModel):
    minimax_api_key_configured: bool
    minimax_api_key_masked: str | None = None
    signal_history_min_confidence: int
    signal_history_min_reward_risk: float
    signal_history_max_reward_risk: float
    signal_history_min_rsi: float
    signal_history_max_rsi: float
    signal_history_allow_neutral_macd: bool
    signal_history_allow_buy: bool
    signal_history_allow_sell: bool
    signal_history_allow_conservative: bool
    signal_history_allow_moderate: bool
    signal_history_allow_aggressive: bool


class SystemPreferencesPayload(BaseModel):
    minimax_api_key: str | None = Field(default=None, min_length=10, max_length=512)
    signal_history_min_confidence: int = Field(default=DEFAULT_SIGNAL_HISTORY_MIN_CONFIDENCE, ge=0, le=100)
    signal_history_min_reward_risk: float = Field(default=DEFAULT_SIGNAL_HISTORY_MIN_REWARD_RISK, ge=0.1, le=20)
    signal_history_max_reward_risk: float = Field(default=DEFAULT_SIGNAL_HISTORY_MAX_REWARD_RISK, ge=0.1, le=20)
    signal_history_min_rsi: float = Field(default=DEFAULT_SIGNAL_HISTORY_MIN_RSI, ge=0, le=100)
    signal_history_max_rsi: float = Field(default=DEFAULT_SIGNAL_HISTORY_MAX_RSI, ge=0, le=100)
    signal_history_allow_neutral_macd: bool = Field(default=DEFAULT_SIGNAL_HISTORY_ALLOW_NEUTRAL_MACD)
    signal_history_allow_buy: bool = Field(default=DEFAULT_SIGNAL_HISTORY_ALLOW_BUY)
    signal_history_allow_sell: bool = Field(default=DEFAULT_SIGNAL_HISTORY_ALLOW_SELL)
    signal_history_allow_conservative: bool = Field(default=DEFAULT_SIGNAL_HISTORY_ALLOW_CONSERVATIVE)
    signal_history_allow_moderate: bool = Field(default=DEFAULT_SIGNAL_HISTORY_ALLOW_MODERATE)
    signal_history_allow_aggressive: bool = Field(default=DEFAULT_SIGNAL_HISTORY_ALLOW_AGGRESSIVE)


def _build_response(db: Session) -> SystemPreferencesResponse:
    value = get_system_preference_value(db, MINIMAX_API_KEY_KEY)
    return SystemPreferencesResponse(
        minimax_api_key_configured=bool(value),
        minimax_api_key_masked=mask_secret(value),
        signal_history_min_confidence=get_system_preference_int(
            db,
            SIGNAL_HISTORY_MIN_CONFIDENCE_KEY,
            DEFAULT_SIGNAL_HISTORY_MIN_CONFIDENCE,
        ),
        signal_history_min_reward_risk=get_system_preference_float(
            db,
            SIGNAL_HISTORY_MIN_REWARD_RISK_KEY,
            DEFAULT_SIGNAL_HISTORY_MIN_REWARD_RISK,
        ),
        signal_history_max_reward_risk=get_system_preference_float(
            db,
            SIGNAL_HISTORY_MAX_REWARD_RISK_KEY,
            DEFAULT_SIGNAL_HISTORY_MAX_REWARD_RISK,
        ),
        signal_history_min_rsi=get_system_preference_float(
            db,
            SIGNAL_HISTORY_MIN_RSI_KEY,
            DEFAULT_SIGNAL_HISTORY_MIN_RSI,
        ),
        signal_history_max_rsi=get_system_preference_float(
            db,
            SIGNAL_HISTORY_MAX_RSI_KEY,
            DEFAULT_SIGNAL_HISTORY_MAX_RSI,
        ),
        signal_history_allow_neutral_macd=get_system_preference_bool(
            db,
            SIGNAL_HISTORY_ALLOW_NEUTRAL_MACD_KEY,
            DEFAULT_SIGNAL_HISTORY_ALLOW_NEUTRAL_MACD,
        ),
        signal_history_allow_buy=get_system_preference_bool(
            db,
            SIGNAL_HISTORY_ALLOW_BUY_KEY,
            DEFAULT_SIGNAL_HISTORY_ALLOW_BUY,
        ),
        signal_history_allow_sell=get_system_preference_bool(
            db,
            SIGNAL_HISTORY_ALLOW_SELL_KEY,
            DEFAULT_SIGNAL_HISTORY_ALLOW_SELL,
        ),
        signal_history_allow_conservative=get_system_preference_bool(
            db,
            SIGNAL_HISTORY_ALLOW_CONSERVATIVE_KEY,
            DEFAULT_SIGNAL_HISTORY_ALLOW_CONSERVATIVE,
        ),
        signal_history_allow_moderate=get_system_preference_bool(
            db,
            SIGNAL_HISTORY_ALLOW_MODERATE_KEY,
            DEFAULT_SIGNAL_HISTORY_ALLOW_MODERATE,
        ),
        signal_history_allow_aggressive=get_system_preference_bool(
            db,
            SIGNAL_HISTORY_ALLOW_AGGRESSIVE_KEY,
            DEFAULT_SIGNAL_HISTORY_ALLOW_AGGRESSIVE,
        ),
    )


@router.get("", response_model=SystemPreferencesResponse)
def get_system_preferences(
    _admin_user_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return _build_response(db)


@router.put("", response_model=SystemPreferencesResponse)
def put_system_preferences(
    payload: SystemPreferencesPayload,
    admin_user_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if payload.minimax_api_key is not None:
        set_system_preference_value(
            db,
            key=MINIMAX_API_KEY_KEY,
            value=payload.minimax_api_key,
            updated_by_user_id=admin_user_id,
        )
    set_optional_system_preference_value(
        db,
        key=SIGNAL_HISTORY_MIN_CONFIDENCE_KEY,
        value=str(payload.signal_history_min_confidence),
        updated_by_user_id=admin_user_id,
    )
    set_optional_system_preference_value(
        db,
        key=SIGNAL_HISTORY_MIN_REWARD_RISK_KEY,
        value=str(payload.signal_history_min_reward_risk),
        updated_by_user_id=admin_user_id,
    )
    set_optional_system_preference_value(
        db,
        key=SIGNAL_HISTORY_MAX_REWARD_RISK_KEY,
        value=str(payload.signal_history_max_reward_risk),
        updated_by_user_id=admin_user_id,
    )
    set_optional_system_preference_value(
        db,
        key=SIGNAL_HISTORY_MIN_RSI_KEY,
        value=str(payload.signal_history_min_rsi),
        updated_by_user_id=admin_user_id,
    )
    set_optional_system_preference_value(
        db,
        key=SIGNAL_HISTORY_MAX_RSI_KEY,
        value=str(payload.signal_history_max_rsi),
        updated_by_user_id=admin_user_id,
    )
    set_optional_system_preference_value(
        db,
        key=SIGNAL_HISTORY_ALLOW_NEUTRAL_MACD_KEY,
        value="true" if payload.signal_history_allow_neutral_macd else "false",
        updated_by_user_id=admin_user_id,
    )
    set_optional_system_preference_value(
        db,
        key=SIGNAL_HISTORY_ALLOW_BUY_KEY,
        value="true" if payload.signal_history_allow_buy else "false",
        updated_by_user_id=admin_user_id,
    )
    set_optional_system_preference_value(
        db,
        key=SIGNAL_HISTORY_ALLOW_SELL_KEY,
        value="true" if payload.signal_history_allow_sell else "false",
        updated_by_user_id=admin_user_id,
    )
    set_optional_system_preference_value(
        db,
        key=SIGNAL_HISTORY_ALLOW_CONSERVATIVE_KEY,
        value="true" if payload.signal_history_allow_conservative else "false",
        updated_by_user_id=admin_user_id,
    )
    set_optional_system_preference_value(
        db,
        key=SIGNAL_HISTORY_ALLOW_MODERATE_KEY,
        value="true" if payload.signal_history_allow_moderate else "false",
        updated_by_user_id=admin_user_id,
    )
    set_optional_system_preference_value(
        db,
        key=SIGNAL_HISTORY_ALLOW_AGGRESSIVE_KEY,
        value="true" if payload.signal_history_allow_aggressive else "false",
        updated_by_user_id=admin_user_id,
    )
    return _build_response(db)


@router.delete("")
def delete_system_preferences(
    _admin_user_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    delete_system_preference_value(db, key=MINIMAX_API_KEY_KEY)
    return {"message": "System preferences cleared"}
