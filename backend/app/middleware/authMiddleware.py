"""Middleware de autenticação multi-tenant.

Extrai user_id do JWT e adiciona ao contexto da requisição.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Optional
import uuid
import jwt
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
JWT_ACCESS_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_EXPIRE_MINUTES", "15"))
ADMIN_EMAILS = {
    email.strip().lower()
    for email in os.getenv("ADMIN_EMAILS", "o.alan.silva@gmail.com").split(",")
    if email.strip()
}

security = HTTPBearer(auto_error=False)


def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user_optional(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)] = None,
    db: Session = Depends(get_db),
) -> Optional[str]:
    """
    Dependency que extrai user_id do JWT (se disponível).
    Retorna None para rotas públicas sem autenticação.
    """
    if not credentials:
        return None

    try:
        payload = _decode_token(credentials.credentials)
        if payload.get("type") != "access":
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        # Verifica se usuário existe
        user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
        if not user:
            return None

        return user_id
    except Exception:
        return None


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Session = Depends(get_db),
) -> str:
    """
    Dependency que exige autenticação válida.
    Retorna user_id (string UUID) do usuário autenticado.
    Lança 401 se não houver token válido.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication",
        )

    payload = _decode_token(credentials.credentials)

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    now = datetime.utcnow()
    if _ensure_user_accessible(user, now):
        db.add(user)
        db.commit()

    return user_id


def is_admin_email(email: str | None) -> bool:
    return str(email or "").strip().lower() in ADMIN_EMAILS


async def get_current_admin(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> str:
    user = db.query(User).filter(User.id == uuid.UUID(current_user_id)).first()
    if not user or not is_admin_email(user.email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user_id


def _is_user_temporarily_suspended(user: User, now: datetime) -> bool:
    if user.status != "suspended":
        return False

    if not user.suspended_until:
        return True

    return now < user.suspended_until.replace(tzinfo=None)


def _ensure_user_accessible(user: User, now: datetime) -> bool:
    if user.status == "banned" or user.is_banned:
        raise HTTPException(
            status_code=403,
            detail="User account is banned",
        )

    if _is_user_temporarily_suspended(user, now):
        raise HTTPException(
            status_code=403,
            detail="User account is suspended",
        )

    if user.status == "suspended" and not _is_user_temporarily_suspended(user, now):
        user.status = "active"
        user.suspended_until = None
        user.suspension_reason = None
        return True

    return False


# Type alias para uso nas rotas
CurrentUser = Annotated[Optional[str], Depends(get_current_user_optional)]
AuthenticatedUser = Annotated[str, Depends(get_current_user)]
AdminUser = Annotated[str, Depends(get_current_admin)]
