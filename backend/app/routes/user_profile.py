from __future__ import annotations

from datetime import datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.authMiddleware import get_current_user
from app.models import User
from app.services.beta_access import hash_password as _hash_password
from app.services.beta_access import temporary_password_expired
from app.services.beta_access import verify_password as _verify_password

router = APIRouter(prefix="/api/users", tags=["user-profile"])


def _serialize_profile(user: User) -> dict[str, str | None]:
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "createdAt": user.created_at.isoformat() if user.created_at else None,
        "lastLogin": user.last_login.isoformat() if user.last_login else None,
    }


class UserProfileResponse(BaseModel):
    id: str
    email: str
    name: str
    createdAt: str | None
    lastLogin: str | None = None


class UpdateProfileRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Name cannot be empty")
        return normalized


class ChangePasswordRequest(BaseModel):
    currentPassword: str = Field(..., min_length=1)
    newPassword: str = Field(..., min_length=8, max_length=256)

    @field_validator("newPassword")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        return value


class MessageResponse(BaseModel):
    message: str
    updatedAt: str


def _load_user(db: Session, current_user_id: str) -> User:
    user = db.query(User).filter(User.id == uuid.UUID(current_user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/me", response_model=UserProfileResponse)
def get_me(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = _load_user(db, current_user_id)
    return UserProfileResponse(**_serialize_profile(user))


@router.put("/me", response_model=UserProfileResponse)
def update_me(
    payload: UpdateProfileRequest,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = _load_user(db, current_user_id)
    user.name = payload.name
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserProfileResponse(**_serialize_profile(user))


@router.put("/password", response_model=MessageResponse)
def update_password(
    payload: ChangePasswordRequest,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = _load_user(db, current_user_id)
    now = datetime.utcnow()
    if temporary_password_expired(user, now):
        raise HTTPException(status_code=403, detail="Temporary password expired")
    if not _verify_password(payload.currentPassword, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    if payload.currentPassword == payload.newPassword:
        raise HTTPException(
            status_code=400, detail="New password must be different from current password"
        )

    user.password_hash = _hash_password(payload.newPassword)
    if user.must_change_password:
        user.temporary_password_used_at = now
    user.must_change_password = False
    user.temporary_password_expires_at = None
    user.password_changed_at = now
    db.add(user)
    db.commit()

    return MessageResponse(
        message="Password updated successfully",
        updatedAt=now.isoformat(),
    )
