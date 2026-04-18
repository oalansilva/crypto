from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models import UserExchangeCredential

BINANCE_PROVIDER = "binance"


def get_user_exchange_credential(
    db: Session, user_id: str, provider: str
) -> Optional[UserExchangeCredential]:
    return (
        db.query(UserExchangeCredential)
        .filter(
            UserExchangeCredential.user_id == user_id,
            UserExchangeCredential.provider == provider,
        )
        .first()
    )


def upsert_user_exchange_credential(
    db: Session,
    *,
    user_id: str,
    provider: str,
    api_key: str,
    api_secret: str,
) -> UserExchangeCredential:
    existing = get_user_exchange_credential(db, user_id, provider)
    if existing is None:
        existing = UserExchangeCredential(
            user_id=user_id,
            provider=provider,
            api_key=api_key,
            api_secret=api_secret,
        )
        db.add(existing)
    else:
        existing.api_key = api_key
        existing.api_secret = api_secret

    db.commit()
    db.refresh(existing)
    return existing


def delete_user_exchange_credential(db: Session, *, user_id: str, provider: str) -> bool:
    existing = get_user_exchange_credential(db, user_id, provider)
    if existing is None:
        return False
    db.delete(existing)
    db.commit()
    return True
