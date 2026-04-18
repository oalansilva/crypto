from __future__ import annotations

from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import Session

from app.models import SystemPreference

MINIMAX_API_KEY_KEY = "minimax_api_key"
SIGNAL_HISTORY_MIN_CONFIDENCE_KEY = "signal_history_min_confidence"
SIGNAL_HISTORY_MIN_REWARD_RISK_KEY = "signal_history_min_reward_risk"
SIGNAL_HISTORY_MAX_REWARD_RISK_KEY = "signal_history_max_reward_risk"
SIGNAL_HISTORY_MIN_RSI_KEY = "signal_history_min_rsi"
SIGNAL_HISTORY_MAX_RSI_KEY = "signal_history_max_rsi"
SIGNAL_HISTORY_ALLOW_NEUTRAL_MACD_KEY = "signal_history_allow_neutral_macd"
SIGNAL_HISTORY_ALLOW_BUY_KEY = "signal_history_allow_buy"
SIGNAL_HISTORY_ALLOW_SELL_KEY = "signal_history_allow_sell"
SIGNAL_HISTORY_ALLOW_CONSERVATIVE_KEY = "signal_history_allow_conservative"
SIGNAL_HISTORY_ALLOW_MODERATE_KEY = "signal_history_allow_moderate"
SIGNAL_HISTORY_ALLOW_AGGRESSIVE_KEY = "signal_history_allow_aggressive"


def get_system_preference(db: Session, key: str) -> SystemPreference | None:
    try:
        return db.query(SystemPreference).filter(SystemPreference.key == key).first()
    except (OperationalError, ProgrammingError):
        return None


def get_system_preference_value(db: Session, key: str) -> str | None:
    pref = get_system_preference(db, key)
    if not pref or pref.value is None:
        return None
    value = str(pref.value).strip()
    return value or None


def set_system_preference_value(
    db: Session, *, key: str, value: str, updated_by_user_id: str
) -> SystemPreference:
    pref = get_system_preference(db, key)
    if pref is None:
        pref = SystemPreference(key=key, value=value.strip(), updated_by_user_id=updated_by_user_id)
        db.add(pref)
    else:
        pref.value = value.strip()
        pref.updated_by_user_id = updated_by_user_id
    db.commit()
    db.refresh(pref)
    return pref


def set_optional_system_preference_value(
    db: Session,
    *,
    key: str,
    value: str | None,
    updated_by_user_id: str,
) -> SystemPreference | None:
    if value is None:
        delete_system_preference_value(db, key=key)
        return None
    return set_system_preference_value(
        db, key=key, value=str(value), updated_by_user_id=updated_by_user_id
    )


def delete_system_preference_value(db: Session, *, key: str) -> bool:
    pref = get_system_preference(db, key)
    if pref is None:
        return False
    db.delete(pref)
    db.commit()
    return True


def mask_secret(value: str | None) -> str | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    if len(raw) <= 8:
        return "*" * len(raw)
    return f"{raw[:4]}{'*' * max(4, len(raw) - 8)}{raw[-4:]}"


def get_system_preference_int(db: Session, key: str, default: int) -> int:
    value = get_system_preference_value(db, key)
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def get_system_preference_float(db: Session, key: str, default: float) -> float:
    value = get_system_preference_value(db, key)
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def get_system_preference_bool(db: Session, key: str, default: bool) -> bool:
    value = get_system_preference_value(db, key)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return default
