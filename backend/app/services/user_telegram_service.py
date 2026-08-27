from __future__ import annotations

import os
import re
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.models import User

TELEGRAM_LINK_TTL_MINUTES = 15
_USERNAME_RE = re.compile(r"^[a-zA-Z0-9_]{5,32}$")


def normalize_telegram_username(value: str | None) -> str:
    normalized = str(value or "").strip().lstrip("@").lower()
    if not normalized or not _USERNAME_RE.match(normalized):
        raise ValueError("Informe um @username Telegram válido (5-32 caracteres, a-z, 0-9, _)")
    return normalized


def serialize_telegram_settings(user: User) -> dict[str, Any]:
    linked = bool(user.telegram_chat_id)
    return {
        "telegramUsername": user.telegram_username,
        "telegramAlertsEnabled": bool(user.telegram_alerts_enabled),
        "linked": linked,
        "linkedAt": user.telegram_linked_at.isoformat() if user.telegram_linked_at else None,
        "usernameMismatch": bool(user.telegram_username_mismatch),
        "botUsername": (os.getenv("MONITOR_TELEGRAM_BOT_USERNAME") or "").strip() or None,
        "hasPendingLinkToken": bool(
            user.telegram_link_token
            and user.telegram_link_expires_at
            and user.telegram_link_expires_at > datetime.utcnow()
        ),
    }


def update_telegram_settings(
    db: Session,
    user: User,
    *,
    telegram_username: str | None = None,
    telegram_alerts_enabled: bool | None = None,
) -> User:
    if telegram_username is not None:
        user.telegram_username = normalize_telegram_username(telegram_username)
    if telegram_alerts_enabled is not None:
        user.telegram_alerts_enabled = bool(telegram_alerts_enabled)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_link_token(db: Session, user: User) -> dict[str, str]:
    if not user.telegram_username:
        raise ValueError("Informe seu @username Telegram antes de vincular")
    token = secrets.token_urlsafe(24)
    user.telegram_link_token = token
    user.telegram_link_expires_at = datetime.utcnow() + timedelta(minutes=TELEGRAM_LINK_TTL_MINUTES)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
        "token": token,
        "command": f"/link {token}",
        "expiresAt": user.telegram_link_expires_at.isoformat() if user.telegram_link_expires_at else None,
    }


def list_eligible_alert_users(db: Session) -> list[User]:
    return (
        db.query(User)
        .filter(
            User.status == "active",
            User.telegram_alerts_enabled.is_(True),
            User.telegram_chat_id.isnot(None),
        )
        .all()
    )


def process_link_command(
    db: Session,
    *,
    token: str,
    chat_id: str,
    from_username: str | None,
) -> tuple[bool, str]:
    cleaned = str(token or "").strip()
    if not cleaned:
        return False, "Token inválido. Gere um novo código no Perfil do Cripto Farol."

    user = (
        db.query(User)
        .filter(User.telegram_link_token == cleaned)
        .first()
    )
    if user is None:
        return False, "Token inválido ou expirado. Gere um novo código no Perfil."

    if user.telegram_link_expires_at is None or user.telegram_link_expires_at < datetime.utcnow():
        user.telegram_link_token = None
        user.telegram_link_expires_at = None
        db.add(user)
        db.commit()
        return False, "Token expirado. Gere um novo código no Perfil."

    declared = str(user.telegram_username or "").strip().lower()
    linked_username = str(from_username or "").strip().lstrip("@").lower()
    mismatch = bool(declared and linked_username and declared != linked_username)

    user.telegram_chat_id = str(chat_id)
    user.telegram_linked_at = datetime.utcnow()
    user.telegram_link_token = None
    user.telegram_link_expires_at = None
    user.telegram_username_mismatch = mismatch
    if linked_username and not declared:
        user.telegram_username = linked_username
    db.add(user)
    db.commit()

    if mismatch:
        return True, (
            "Conta vinculada com aviso: o @username do Telegram difere do informado no Perfil. "
            "Revise em Meu Perfil se necessário."
        )
    return True, "Conta vinculada. Alertas position-aware serão enviados neste chat quando habilitados."


def load_user_by_id(db: Session, user_id: str) -> User | None:
    try:
        parsed = uuid.UUID(str(user_id))
    except (TypeError, ValueError):
        return None
    return db.query(User).filter(User.id == parsed).first()
