from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
import uuid
import logging
import os
from typing import Annotated

from app.database import get_db
from app.models import User
from app.middleware.authMiddleware import is_admin_email

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["auth"])

# --- Config ---
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
JWT_ACCESS_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_EXPIRE_MINUTES", "15"))
JWT_REFRESH_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", "7"))


# --- Pydantic Schemas ---
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

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


# --- Helpers ---
def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def _verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


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


# --- Routes ---
@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    # Check duplicate email
    existing = db.query(User).filter(User.email == body.email.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        id=uuid.uuid4(),
        email=body.email.lower(),
        password_hash=_hash_password(body.password),
        name=body.name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return RegisterResponse(id=str(user.id), email=user.email, name=user.name)


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    # DEV BYPASS: alan.silva@gmail.com pode entrar sem senha
    if body.email.lower() == "o.alan.silva@gmail.com":
        user = db.query(User).filter(User.email == body.email.lower()).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        logger.info(f"[AUTH] Login bypass usado para {body.email}")
    else:
        user = db.query(User).filter(User.email == body.email.lower()).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not _verify_password(body.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")

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
        isAdmin=is_admin_email(user.email),
    )


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(body: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email.lower()).first()

    if user:
        # Simulate sending email - log the "email"
        reset_link = f"http://localhost:5173/reset-password?token=simulated-token-{uuid.uuid4()}"
        logger.info(
            f"[AUTH] Password reset email SIMULATED for {user.email}. "
            f"Reset link: {reset_link}"
        )

    # Always return 200 to prevent email enumeration
    return ForgotPasswordResponse(
        message="If the email exists, a reset link was sent"
    )


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

    return MeResponse(id=str(user.id), email=user.email, name=user.name, isAdmin=is_admin_email(user.email))


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
        isAdmin=is_admin_email(user.email),
    )
