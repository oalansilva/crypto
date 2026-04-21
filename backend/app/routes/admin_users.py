from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import uuid
import bcrypt

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.authMiddleware import get_current_admin
from app.models import AdminActionLog, User

router = APIRouter(prefix="/api/admin", tags=["admin-users"])

ACTION_VIEW = "user_viewed"
ACTION_CREATE = "user_created"
ACTION_UPDATE = "user_updated"
ACTION_SUSPEND = "user_suspended"
ACTION_REACTIVATE = "user_reactivated"
ACTION_BAN = "user_banned"


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def _serialize_datetime(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def _normalize_status(value: str) -> str:
    normalized = value.strip().lower()
    if normalized not in {"active", "suspended", "banned"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status. Use active, suspended or banned.",
        )
    return normalized


def _parse_datetime(value: str | None) -> datetime | None:
    if value is None:
        return None

    normalized = value.strip()
    if not normalized:
        return None

    try:
        dt = datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid datetime format. Use ISO 8601.",
        )

    if dt.tzinfo:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def _require_reason(reason: str | None, action: str) -> str:
    if not reason or not reason.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Reason is required for action '{action}'.",
        )
    return reason.strip()


def _serialize_user(user: User) -> dict[str, Any]:
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "status": user.status,
        "isBanned": bool(user.is_banned),
        "suspendedUntil": _serialize_datetime(user.suspended_until),
        "suspensionReason": user.suspension_reason,
        "notes": user.notes,
        "createdAt": _serialize_datetime(user.created_at),
        "lastLogin": _serialize_datetime(user.last_login),
    }


def _serialize_action_log(
    log: AdminActionLog,
    actor_email_by_id: dict[str, str],
    target_email_by_id: dict[str, str],
) -> dict[str, Any]:
    actor_user_id = str(log.actor_user_id)
    target_user_id = str(log.target_user_id)
    return {
        "id": log.id,
        "actorUserId": actor_user_id,
        "actorEmail": actor_email_by_id.get(actor_user_id),
        "targetUserId": target_user_id,
        "targetEmail": target_email_by_id.get(target_user_id),
        "action": log.action,
        "targetSubject": log.target_subject,
        "reason": log.reason,
        "metadata": log.metadata_json,
        "createdAt": _serialize_datetime(log.created_at),
    }


def _append_admin_action(
    db: Session,
    actor_user_id: str,
    target_user_id: str,
    action: str,
    reason: str,
    target_subject: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    db.add(
        AdminActionLog(
            actor_user_id=str(actor_user_id),
            target_user_id=str(target_user_id),
            action=action,
            target_subject=target_subject,
            reason=reason,
            metadata_json=metadata or {},
        )
    )
    db.commit()


def _load_user(db: Session, user_id: str) -> User:
    try:
        parsed_user_id = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user id format"
        )

    user = db.query(User).filter(User.id == parsed_user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


class AdminUserListItem(BaseModel):
    id: str
    email: str
    name: str
    status: str
    isBanned: bool
    suspendedUntil: str | None
    suspensionReason: str | None
    notes: str | None
    createdAt: str | None
    lastLogin: str | None


class AdminUserListResponse(BaseModel):
    items: list[AdminUserListItem]
    total: int
    page: int
    pageSize: int


class AdminUserDetailResponse(BaseModel):
    id: str
    email: str
    name: str
    status: str
    isBanned: bool
    suspendedUntil: str | None
    suspensionReason: str | None
    notes: str | None
    createdAt: str | None
    lastLogin: str | None


class AdminUserCreateRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=200)
    name: str = Field(min_length=1, max_length=120)
    status: str = "active"
    isBanned: bool = False
    suspendedUntil: str | None = None
    suspensionReason: str | None = Field(default=None, max_length=1024)
    notes: str | None = Field(default=None, max_length=4000)
    reason: str | None = Field(default=None, max_length=2000)


class AdminUserUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    status: str | None = None
    isBanned: bool | None = None
    suspendedUntil: str | None = None
    suspensionReason: str | None = Field(default=None, max_length=1024)
    notes: str | None = Field(default=None, max_length=4000)
    reason: str | None = Field(default=None, max_length=2000)


class AdminUserSuspendRequest(BaseModel):
    reason: str = Field(min_length=4, max_length=2000)
    suspendedUntil: str


class AdminUserBanRequest(BaseModel):
    reason: str = Field(min_length=4, max_length=2000)


class AdminActionLogItem(BaseModel):
    id: int
    actorUserId: str
    actorEmail: str | None
    targetUserId: str
    targetEmail: str | None
    action: str
    targetSubject: str | None
    reason: str
    metadata: dict[str, Any] | None = None
    createdAt: str | None


class AdminActionLogListResponse(BaseModel):
    items: list[AdminActionLogItem]
    total: int
    page: int
    pageSize: int


@router.get("/users", response_model=AdminUserListResponse)
def list_users(
    q: str | None = Query(default=None),
    user_status: str | None = Query(default=None, alias="status"),
    created_from: str | None = Query(default=None, alias="createdFrom"),
    created_to: str | None = Query(default=None, alias="createdTo"),
    last_login_from: str | None = Query(default=None, alias="lastLoginFrom"),
    last_login_to: str | None = Query(default=None, alias="lastLoginTo"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100, alias="pageSize"),
    _admin_user_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    _ = _admin_user_id

    query = db.query(User)

    if q:
        pattern = f"%{q.strip().lower()}%"
        query = query.filter(or_(User.email.ilike(pattern), User.name.ilike(pattern)))

    if user_status:
        query = query.filter(User.status == _normalize_status(user_status))

    created_from_dt = _parse_datetime(created_from)
    created_to_dt = _parse_datetime(created_to)
    last_login_from_dt = _parse_datetime(last_login_from)
    last_login_to_dt = _parse_datetime(last_login_to)

    conditions = []
    if created_from_dt:
        conditions.append(User.created_at >= created_from_dt)
    if created_to_dt:
        conditions.append(User.created_at <= created_to_dt)
    if last_login_from_dt:
        conditions.append(User.last_login >= last_login_from_dt)
    if last_login_to_dt:
        conditions.append(User.last_login <= last_login_to_dt)

    if conditions:
        query = query.filter(and_(*conditions))

    total = query.count()
    rows = (
        query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    )

    return AdminUserListResponse(
        items=[AdminUserListItem(**_serialize_user(row)) for row in rows],
        total=total,
        page=page,
        pageSize=page_size,
    )


@router.get("/users/{user_id}", response_model=AdminUserDetailResponse)
def get_user(
    user_id: str,
    audit: bool = Query(default=False),
    _admin_user_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user = _load_user(db, user_id)
    if audit:
        _append_admin_action(
            db=db,
            actor_user_id=_admin_user_id,
            target_user_id=str(user.id),
            action=ACTION_VIEW,
            reason="viewed user",
            target_subject="user",
            metadata={"source": "detail_view"},
        )
    return AdminUserDetailResponse(**_serialize_user(user))


@router.post("/users", response_model=AdminUserDetailResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: AdminUserCreateRequest,
    _admin_user_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    normalized_email = payload.email.lower()
    existing = db.query(User).filter(User.email == normalized_email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    normalized_status = _normalize_status(payload.status)
    suspended_until = _parse_datetime(payload.suspendedUntil)
    reason = payload.reason.strip() if payload.reason else "Created by admin"
    is_banned = bool(payload.isBanned)
    if normalized_status == "banned" or is_banned:
        normalized_status = "banned"
        is_banned = True

    if normalized_status == "suspended" and not suspended_until:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Suspended users must have suspendedUntil defined",
        )

    user = User(
        id=uuid.uuid4(),
        email=normalized_email,
        password_hash=_hash_password(payload.password),
        name=payload.name,
        status=normalized_status,
        is_banned=is_banned,
        suspended_until=suspended_until,
        suspension_reason=payload.suspensionReason,
        notes=payload.notes,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    _append_admin_action(
        db=db,
        actor_user_id=_admin_user_id,
        target_user_id=str(user.id),
        action=ACTION_CREATE,
        reason=reason,
        target_subject="user",
        metadata={"email": normalized_email},
    )

    return AdminUserDetailResponse(**_serialize_user(user))


@router.put("/users/{user_id}", response_model=AdminUserDetailResponse)
def update_user(
    user_id: str,
    payload: AdminUserUpdateRequest,
    _admin_user_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user = _load_user(db, user_id)
    changed_fields = {}
    reason_required_for = False

    if payload.name is not None and payload.name != user.name:
        user.name = payload.name
        changed_fields["name"] = payload.name

    if payload.notes is not None and payload.notes != user.notes:
        user.notes = payload.notes
        changed_fields["notes"] = payload.notes

    if payload.status is not None:
        new_status = _normalize_status(payload.status)
        if new_status != user.status:
            user.status = new_status
            changed_fields["status"] = new_status
            reason_required_for = True

    if payload.isBanned is not None and bool(payload.isBanned) != bool(user.is_banned):
        user.is_banned = bool(payload.isBanned)
        changed_fields["isBanned"] = bool(payload.isBanned)
        reason_required_for = True

    if payload.suspendedUntil is not None:
        user.suspended_until = _parse_datetime(payload.suspendedUntil)
        changed_fields["suspendedUntil"] = payload.suspendedUntil
        reason_required_for = True

    if payload.suspensionReason is not None:
        if payload.suspensionReason != (user.suspension_reason or ""):
            user.suspension_reason = payload.suspensionReason
            changed_fields["suspensionReason"] = payload.suspensionReason
            reason_required_for = True

    if changed_fields and reason_required_for:
        reason = _require_reason(payload.reason, ACTION_UPDATE)
    elif changed_fields:
        reason = payload.reason.strip() if payload.reason else "Updated by admin"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No changes detected",
        )

    if user.status == "active":
        if user.suspended_until or user.suspension_reason:
            user.suspended_until = None
            user.suspension_reason = None

    if user.status == "banned":
        user.is_banned = True

    db.add(user)
    db.commit()
    db.refresh(user)

    _append_admin_action(
        db=db,
        actor_user_id=_admin_user_id,
        target_user_id=str(user.id),
        action=ACTION_UPDATE,
        reason=reason,
        target_subject="user",
        metadata=changed_fields,
    )

    return AdminUserDetailResponse(**_serialize_user(user))


@router.post("/users/{user_id}/suspend", response_model=AdminUserDetailResponse)
def suspend_user(
    user_id: str,
    payload: AdminUserSuspendRequest,
    _admin_user_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user = _load_user(db, user_id)
    suspended_until = _parse_datetime(payload.suspendedUntil)
    if not suspended_until:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="suspendedUntil is required",
        )
    if suspended_until <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="suspendedUntil must be in the future",
        )

    user.status = "suspended"
    user.suspended_until = suspended_until
    user.suspension_reason = payload.reason
    user.is_banned = False
    db.add(user)
    db.commit()
    db.refresh(user)

    _append_admin_action(
        db=db,
        actor_user_id=_admin_user_id,
        target_user_id=str(user.id),
        action=ACTION_SUSPEND,
        reason=payload.reason,
        target_subject="user",
        metadata={"suspendedUntil": payload.suspendedUntil},
    )

    return AdminUserDetailResponse(**_serialize_user(user))


@router.post("/users/{user_id}/reactivate", response_model=AdminUserDetailResponse)
def reactivate_user(
    user_id: str,
    payload: AdminUserBanRequest,
    _admin_user_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user = _load_user(db, user_id)
    reason = _require_reason(payload.reason, ACTION_REACTIVATE)

    user.status = "active"
    user.is_banned = False
    user.suspended_until = None
    user.suspension_reason = None
    db.add(user)
    db.commit()
    db.refresh(user)

    _append_admin_action(
        db=db,
        actor_user_id=_admin_user_id,
        target_user_id=str(user.id),
        action=ACTION_REACTIVATE,
        reason=reason,
        target_subject="user",
    )

    return AdminUserDetailResponse(**_serialize_user(user))


@router.post("/users/{user_id}/ban", response_model=AdminUserDetailResponse)
def ban_user(
    user_id: str,
    payload: AdminUserBanRequest,
    _admin_user_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    user = _load_user(db, user_id)
    reason = _require_reason(payload.reason, ACTION_BAN)

    user.status = "banned"
    user.is_banned = True
    user.suspended_until = None
    user.suspension_reason = None
    db.add(user)
    db.commit()
    db.refresh(user)

    _append_admin_action(
        db=db,
        actor_user_id=_admin_user_id,
        target_user_id=str(user.id),
        action=ACTION_BAN,
        reason=reason,
        target_subject="user",
    )

    return AdminUserDetailResponse(**_serialize_user(user))


@router.get("/user-actions", response_model=AdminActionLogListResponse)
def list_user_actions(
    action: str | None = Query(default=None),
    actor_user_id: str | None = Query(default=None, alias="actorUserId"),
    target_user_id: str | None = Query(default=None, alias="targetUserId"),
    from_: str | None = Query(default=None, alias="from"),
    to: str | None = Query(default=None, alias="to"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100, alias="pageSize"),
    _admin_user_id: str = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    _ = _admin_user_id

    query = db.query(AdminActionLog)

    if action:
        query = query.filter(AdminActionLog.action == action.strip())
    if actor_user_id:
        query = query.filter(AdminActionLog.actor_user_id == actor_user_id)
    if target_user_id:
        query = query.filter(AdminActionLog.target_user_id == target_user_id)

    from_dt = _parse_datetime(from_)
    to_dt = _parse_datetime(to)

    if from_dt:
        query = query.filter(AdminActionLog.created_at >= from_dt)
    if to_dt:
        query = query.filter(AdminActionLog.created_at <= to_dt)

    total = query.count()
    logs = (
        query.order_by(AdminActionLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    user_ids = {str(log.actor_user_id) for log in logs} | {str(log.target_user_id) for log in logs}
    email_map: dict[str, str] = {}
    if user_ids:
        rows = db.query(User.id, User.email).filter(User.id.in_(user_ids)).all()
        email_map = {str(row[0]): row[1] for row in rows}

    actor_email_by_id = email_map
    target_email_by_id = email_map

    return AdminActionLogListResponse(
        items=[
            AdminActionLogItem(**_serialize_action_log(log, actor_email_by_id, target_email_by_id))
            for log in logs
        ],
        total=total,
        page=page,
        pageSize=page_size,
    )
