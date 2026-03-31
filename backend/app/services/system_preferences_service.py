from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import SystemPreference

MINIMAX_API_KEY_KEY = "minimax_api_key"


def get_system_preference(db: Session, key: str) -> SystemPreference | None:
    return db.query(SystemPreference).filter(SystemPreference.key == key).first()


def get_system_preference_value(db: Session, key: str) -> str | None:
    pref = get_system_preference(db, key)
    if not pref or pref.value is None:
        return None
    value = str(pref.value).strip()
    return value or None


def set_system_preference_value(db: Session, *, key: str, value: str, updated_by_user_id: str) -> SystemPreference:
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
