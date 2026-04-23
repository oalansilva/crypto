from __future__ import annotations

import uuid
from datetime import datetime, timedelta

import bcrypt
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import AdminActionLog, User
from app.routes import admin_users


@pytest.fixture
def admin_db_session():
    engine = create_engine("postgresql://postgres:postgres@127.0.0.1:5432/postgres")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


def _seed_user(
    db,
    *,
    email: str,
    name: str,
    status: str = "active",
    is_banned: bool = False,
    suspended_until: datetime | None = None,
    suspension_reason: str | None = None,
    notes: str | None = None,
    created_at: datetime | None = None,
    last_login: datetime | None = None,
):
    user = User(
        id=uuid.uuid4(),
        email=email,
        password_hash="secret",
        name=name,
        status=status,
        is_banned=is_banned,
        suspended_until=suspended_until,
        suspension_reason=suspension_reason,
        notes=notes,
        created_at=created_at or datetime.utcnow(),
        last_login=last_login,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_admin_user_helpers_cover_serialization_and_validation(admin_db_session):
    hashed = admin_users._hash_password("supersecret123")
    assert hashed != "supersecret123"
    assert bcrypt.checkpw("supersecret123".encode("utf-8"), hashed.encode("utf-8"))

    now = datetime(2026, 4, 21, 3, 0, 0)
    assert admin_users._serialize_datetime(now) == now.isoformat()
    assert admin_users._serialize_datetime(None) is None
    assert admin_users._normalize_status(" Suspended ") == "suspended"
    assert admin_users._parse_datetime(None) is None
    assert admin_users._parse_datetime("   ") is None
    assert admin_users._parse_datetime("2026-04-21T03:00:00Z") == now
    assert admin_users._require_reason("  ok  ", "action") == "ok"

    with pytest.raises(Exception, match="Invalid status"):
        admin_users._normalize_status("paused")

    with pytest.raises(Exception, match="Invalid datetime format"):
        admin_users._parse_datetime("not-a-date")

    with pytest.raises(Exception, match="Reason is required"):
        admin_users._require_reason("   ", "ban")

    user = _seed_user(
        admin_db_session,
        email="helper@example.com",
        name="Helper",
        notes="note",
        last_login=now,
    )
    serialized_user = admin_users._serialize_user(user)
    assert serialized_user["email"] == "helper@example.com"
    assert serialized_user["notes"] == "note"

    log = AdminActionLog(
        actor_user_id=str(user.id),
        target_user_id=str(user.id),
        action=admin_users.ACTION_VIEW,
        target_subject="user",
        reason="viewed",
        metadata_json={"k": "v"},
        created_at=now,
    )
    serialized_log = admin_users._serialize_action_log(
        log,
        {str(user.id): user.email},
        {str(user.id): user.email},
    )
    assert serialized_log["actorEmail"] == "helper@example.com"
    assert serialized_log["metadata"] == {"k": "v"}

    with pytest.raises(Exception, match="Invalid user id format"):
        admin_users._load_user(admin_db_session, "not-a-uuid")

    with pytest.raises(Exception, match="User not found"):
        admin_users._load_user(admin_db_session, str(uuid.uuid4()))


def test_admin_user_routes_cover_crud_filters_and_action_logs(admin_db_session, monkeypatch):
    monkeypatch.setattr(admin_users, "_hash_password", lambda password: f"hash::{password}")
    admin_id = str(uuid.uuid4())
    now = datetime.utcnow()

    active_user = _seed_user(
        admin_db_session,
        email="alpha@example.com",
        name="Alpha",
        created_at=now - timedelta(days=2),
        last_login=now - timedelta(hours=2),
    )
    suspended_user = _seed_user(
        admin_db_session,
        email="suspended@example.com",
        name="Suspended",
        status="suspended",
        suspended_until=now + timedelta(days=1),
        suspension_reason="manual",
        created_at=now - timedelta(days=1),
        last_login=now - timedelta(hours=1),
    )

    listed = admin_users.list_users(
        q="alpha",
        user_status="active",
        created_from=(now - timedelta(days=3)).isoformat(),
        created_to=(now - timedelta(days=1)).isoformat(),
        last_login_from=(now - timedelta(days=1)).isoformat(),
        last_login_to=now.isoformat(),
        page=1,
        page_size=20,
        _admin_user_id=admin_id,
        db=admin_db_session,
    )
    assert listed.total == 1
    assert listed.items[0].email == "alpha@example.com"

    detail = admin_users.get_user(
        str(active_user.id),
        audit=True,
        _admin_user_id=admin_id,
        db=admin_db_session,
    )
    assert detail.email == "alpha@example.com"

    with pytest.raises(Exception, match="Email already registered"):
        admin_users.create_user(
            admin_users.AdminUserCreateRequest(
                email="alpha@example.com",
                password="supersecret123",
                name="Duplicate",
            ),
            _admin_user_id=admin_id,
            db=admin_db_session,
        )

    with pytest.raises(Exception, match="Suspended users must have suspendedUntil defined"):
        admin_users.create_user(
            admin_users.AdminUserCreateRequest(
                email="new-suspended@example.com",
                password="supersecret123",
                name="Need Date",
                status="suspended",
            ),
            _admin_user_id=admin_id,
            db=admin_db_session,
        )

    created = admin_users.create_user(
        admin_users.AdminUserCreateRequest(
            email="created@example.com",
            password="supersecret123",
            name="Created User",
            status="banned",
            isBanned=True,
            notes="created by test",
            reason="support request",
        ),
        _admin_user_id=admin_id,
        db=admin_db_session,
    )
    assert created.status == "banned"
    assert created.isBanned is True

    with pytest.raises(Exception, match="No changes detected"):
        admin_users.update_user(
            str(active_user.id),
            admin_users.AdminUserUpdateRequest(),
            _admin_user_id=admin_id,
            db=admin_db_session,
        )

    updated = admin_users.update_user(
        str(suspended_user.id),
        admin_users.AdminUserUpdateRequest(
            name="Suspended Updated",
            status="active",
            notes="released",
            suspendedUntil="",
            suspensionReason="released by admin",
            reason="manual review",
        ),
        _admin_user_id=admin_id,
        db=admin_db_session,
    )
    assert updated.name == "Suspended Updated"
    assert updated.status == "active"
    assert updated.suspendedUntil is None

    with pytest.raises(Exception, match="suspendedUntil must be in the future"):
        admin_users.suspend_user(
            str(active_user.id),
            admin_users.AdminUserSuspendRequest(
                reason="temp block",
                suspendedUntil=(now - timedelta(minutes=1)).isoformat(),
            ),
            _admin_user_id=admin_id,
            db=admin_db_session,
        )

    suspended_result = admin_users.suspend_user(
        str(active_user.id),
        admin_users.AdminUserSuspendRequest(
            reason="temp block",
            suspendedUntil=(now + timedelta(hours=1)).isoformat(),
        ),
        _admin_user_id=admin_id,
        db=admin_db_session,
    )
    assert suspended_result.status == "suspended"

    reactivated = admin_users.reactivate_user(
        str(active_user.id),
        admin_users.AdminUserBanRequest(reason="appeal accepted"),
        _admin_user_id=admin_id,
        db=admin_db_session,
    )
    assert reactivated.status == "active"
    assert reactivated.isBanned is False

    banned = admin_users.ban_user(
        str(active_user.id),
        admin_users.AdminUserBanRequest(reason="fraud"),
        _admin_user_id=admin_id,
        db=admin_db_session,
    )
    assert banned.status == "banned"
    assert banned.isBanned is True

    actions = admin_users.list_user_actions(
        action=admin_users.ACTION_BAN,
        actor_user_id=admin_id,
        target_user_id=str(active_user.id),
        from_=(now - timedelta(days=1)).isoformat(),
        to=(now + timedelta(days=1)).isoformat(),
        page=1,
        page_size=20,
        _admin_user_id=admin_id,
        db=admin_db_session,
    )
    assert actions.total >= 1
    assert any(item.action == admin_users.ACTION_BAN for item in actions.items)
