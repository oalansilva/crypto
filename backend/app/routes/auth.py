from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime, timedelta, timezone
import jwt
import uuid
import logging
import os
from typing import Annotated

from app.database import get_db
from app.jwt_secret import resolve_jwt_secret
from app.models import User
from app.middleware.authMiddleware import ADMIN_EMAILS, is_admin_email
from app.services.beta_access import temporary_password_expired
from app.services.beta_access import verify_password as _verify_password
from app.services.beta_invites import (
    SOURCE_REGISTER_INVITE,
    InviteConsumptionError,
    consume_invite,
    record_invite_refusal,
    validate_invite,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

# --- Config ---
JWT_SECRET = resolve_jwt_secret()
JWT_ACCESS_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_EXPIRE_MINUTES", "15"))
JWT_REFRESH_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", "7"))
# Legacy configuration.  ``BETA_PUBLIC_REGISTRATION_ENABLED`` no longer restores
# account creation without a single-use invite, and neither the beta invited
# e-mail allowlist nor ``ADMIN_EMAILS`` is an entrance door any more (D5).
BETA_PUBLIC_REGISTRATION_ENABLED = os.getenv(
    "BETA_PUBLIC_REGISTRATION_ENABLED",
    "0",
).strip().lower() in {"1", "true", "yes", "on"}
BETA_INVITED_EMAILS = {
    email.strip().lower()
    for email in os.getenv("BETA_INVITED_EMAILS", "").split(",")
    if email.strip()
}


# --- Pydantic Schemas ---
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    inviteToken: str | None = None

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()


class RegisterResponse(BaseModel):
    id: str
    email: str
    name: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    accessToken: str
    refreshToken: str
    expiresIn: int
    id: str
    userId: str
    email: str
    name: str
    isAdmin: bool
    mustChangePassword: bool


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    message: str


class RefreshRequest(BaseModel):
    refreshToken: str


class MeResponse(BaseModel):
    id: str
    email: str
    name: str
    isAdmin: bool
    mustChangePassword: bool


def _generate_access_token(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "user_id": str(user.id),
        "email": user.email,
        "type": "access",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def _generate_refresh_token(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "type": "refresh",
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(days=JWT_REFRESH_EXPIRE_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def _decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def _invitation_required() -> HTTPException:
    """Neutral refusal: never reveals privilege or allowlist membership."""

    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Closed beta access requires invitation",
    )


# --- Routes ---
@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    normalized_email = body.email.lower()

    # (1) The single-use invite for this address is checked FIRST -- before any
    # duplicate lookup -- so a refusal without a valid invite reveals neither
    # privilege (ADMIN_EMAILS / beta allowlist) nor account existence.
    invite_token = str(body.inviteToken or "").strip()
    decision = validate_invite(db, token=invite_token, email=normalized_email)
    if not invite_token or not decision.is_valid:
        if invite_token:
            record_invite_refusal(
                db,
                invite=decision.invite,
                email=normalized_email,
                state=decision.state,
                source=SOURCE_REGISTER_INVITE,
            )
            db.commit()
        raise _invitation_required()

    # (2) Only after a valid invite: the existing duplicate behavior stays
    # explicit (C2).  It does NOT consume the invite nor touch the account, so
    # the owner can still define a new password through the invite flow (D8).
    existing = db.query(User).filter(User.email == normalized_email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # (3) Consume the invite and create the account in the same transaction.
    # No register path can grant administrator role.
    try:
        consumption = consume_invite(
            db,
            token=invite_token,
            email=normalized_email,
            password=body.password,
            name=body.name,
            source=SOURCE_REGISTER_INVITE,
        )
    except InviteConsumptionError:
        db.rollback()
        raise _invitation_required()

    db.commit()
    db.refresh(consumption.user)
    user = consumption.user

    return RegisterResponse(id=str(user.id), email=user.email, name=user.name)


def _raise_if_blocked_by_status(user: User, now: datetime) -> None:
    if user.is_banned or user.status == "banned":
        raise HTTPException(status_code=403, detail="User account is banned")

    if user.status == "suspended":
        if user.suspended_until and user.suspended_until > now:
            raise HTTPException(status_code=403, detail="User account is suspended")
        if not user.suspended_until or user.suspended_until <= now:
            user.status = "active"
            user.suspended_until = None
            user.suspension_reason = None


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    normalized_email = body.email.lower()

    user = db.query(User).filter(User.email == normalized_email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not _verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    now = datetime.utcnow()
    _raise_if_blocked_by_status(user, now)
    if temporary_password_expired(user, now):
        raise HTTPException(status_code=403, detail="Temporary password expired")

    user.last_login = datetime.utcnow()
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = _generate_access_token(user)
    refresh_token = _generate_refresh_token(user)

    return TokenResponse(
        accessToken=access_token,
        refreshToken=refresh_token,
        expiresIn=JWT_ACCESS_EXPIRE_MINUTES * 60,
        id=str(user.id),
        userId=str(user.id),
        email=user.email,
        name=user.name,
        isAdmin=is_admin_email(db, user.email),
        mustChangePassword=bool(user.must_change_password),
    )


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(body: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email.lower()).first()

    if user:
        # Simulate sending email without logging email, token, or reset link.
        logger.info("[AUTH] Password reset requested")

    # Always return 200 to prevent email enumeration
    return ForgotPasswordResponse(message="If the email exists, a reset link was sent")


@router.get("/me", response_model=MeResponse)
def me(
    authorization: Annotated[str | None, Header()] = None,
    db: Session = Depends(get_db),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = authorization[7:]
    payload = _decode_token(token)

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    _raise_if_blocked_by_status(user, datetime.utcnow())
    if temporary_password_expired(user):
        raise HTTPException(status_code=403, detail="Temporary password expired")

    return MeResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
        isAdmin=is_admin_email(db, user.email),
        mustChangePassword=bool(user.must_change_password),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)):
    payload = _decode_token(body.refreshToken)

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(User).filter(User.id == uuid.UUID(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    now = datetime.utcnow()
    _raise_if_blocked_by_status(user, now)
    if temporary_password_expired(user, now):
        raise HTTPException(status_code=403, detail="Temporary password expired")
    user.last_login = datetime.utcnow()
    db.add(user)
    db.commit()

    access_token = _generate_access_token(user)
    refresh_token = _generate_refresh_token(user)

    return TokenResponse(
        accessToken=access_token,
        refreshToken=refresh_token,
        expiresIn=JWT_ACCESS_EXPIRE_MINUTES * 60,
        id=str(user.id),
        userId=str(user.id),
        email=user.email,
        name=user.name,
        isAdmin=is_admin_email(db, user.email),
        mustChangePassword=bool(user.must_change_password),
    )
