from __future__ import annotations

import builtins
import io
import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import BetaAccessAuditLog, User
import app.database as database_module
import app.middleware.authMiddleware as auth_middleware
import app.routes.auth as auth_routes
import app.routes.leads as leads_routes
import app.routes.user_profile as user_profile_routes
from app.services.beta_access import create_beta_access_for_lead, send_welcome_email_gog
from app.services.beta_access import verify_password, WelcomeEmail


@pytest.fixture
def auth_db_session():
    engine = create_engine("postgresql://postgres:postgres@127.0.0.1:5432/postgres")
    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        conn.execute(
            text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS "
                "must_change_password BOOLEAN NOT NULL DEFAULT FALSE"
            )
        )
        conn.execute(
            text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS temporary_password_expires_at TIMESTAMP NULL"
            )
        )
        conn.execute(
            text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS temporary_password_used_at TIMESTAMP NULL"
            )
        )
        conn.execute(
            text("ALTER TABLE users ADD COLUMN IF NOT EXISTS password_changed_at TIMESTAMP NULL")
        )
        conn.execute(
            text("ALTER TABLE users ADD COLUMN IF NOT EXISTS access_invitation_source VARCHAR NULL")
        )
        conn.execute(
            text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS access_invitation_created_at TIMESTAMP NULL"
            )
        )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


def test_database_url_resolution_helpers_and_dependency(monkeypatch, tmp_path):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr(database_module.sys, "argv", ["uvicorn"])

    assert database_module._is_postgres_url("postgresql://db")
    assert database_module._is_postgres_url("postgresql+psycopg2://db")
    assert database_module._is_postgres_url("mysql://db") is False

    monkeypatch.setattr(
        database_module,
        "get_settings",
        lambda: SimpleNamespace(database_url="postgresql://settings"),
    )
    monkeypatch.setenv("DATABASE_URL", "postgresql://env")
    assert database_module.resolve_db_url() == "postgresql://settings"

    monkeypatch.setattr(database_module, "get_settings", lambda: SimpleNamespace(database_url=None))
    assert database_module.resolve_db_url() == "postgresql://env"

    monkeypatch.setenv("DATABASE_URL", "mysql://runtime.db")
    monkeypatch.setattr(database_module.sys, "argv", ["uvicorn"])
    with pytest.raises(RuntimeError, match="must point to PostgreSQL"):
        database_module.resolve_db_url()

    monkeypatch.setenv("DATABASE_URL", "postgresql://env")
    assert database_module.resolve_db_url() == "postgresql://env"

    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr(database_module.sys, "argv", ["uvicorn"])
    with pytest.raises(RuntimeError, match="DATABASE_URL is required"):
        database_module.resolve_db_url()

    class FakeSession:
        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

    fake_session = FakeSession()
    monkeypatch.setattr(database_module, "SessionLocal", lambda: fake_session)
    dependency = database_module.get_db()
    assert next(dependency) is fake_session
    with pytest.raises(StopIteration):
        next(dependency)
    assert fake_session.closed is True


def test_postgres_identity_sequence_sync(monkeypatch):

    executed: list[tuple[str, dict | None]] = []

    class FakeScalarResult:
        def __init__(self, value):
            self._value = value

        def scalar(self):
            return self._value

    class FakeConn:
        def execute(self, statement, params=None):
            sql = str(statement)
            executed.append((sql, params))
            if "pg_get_serial_sequence" in sql:
                if params and params["table_name"] == "favorite_strategies":
                    return FakeScalarResult("favorite_strategies_id_seq")
                return FakeScalarResult(None)
            return FakeScalarResult(None)

    class FakeBegin:
        def __enter__(self):
            return FakeConn()

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(database_module, "DB_URL", "postgresql://crypto")
    monkeypatch.setattr(database_module, "engine", SimpleNamespace(begin=lambda: FakeBegin()))
    database_module.sync_postgres_identity_sequences()

    assert any("pg_get_serial_sequence" in sql for sql, _params in executed)
    assert any("setval" in sql for sql, _params in executed)


def test_market_ohlcv_timescale_policy_check_controls(monkeypatch):
    monkeypatch.delenv("MARKET_OHLCV_VERIFY_POLICIES", raising=False)
    monkeypatch.setenv("APP_ENV", "development")
    assert not database_module._policy_checks_enabled()

    monkeypatch.setenv("APP_ENV", "production")
    assert database_module._policy_checks_enabled()

    monkeypatch.setenv("MARKET_OHLCV_VERIFY_POLICIES", "0")
    assert not database_module._policy_checks_enabled()

    monkeypatch.setenv("MARKET_OHLCV_VERIFY_POLICIES", "1")
    assert database_module._policy_checks_enabled()


def test_postgres_runtime_schema_migrations_execute_admin_user_statements(monkeypatch):
    executed: list[str] = []

    class FakeConn:
        def execute(self, statement, params=None):
            executed.append(str(statement))
            return None

    class FakeBegin:
        def __enter__(self):
            return FakeConn()

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(database_module, "DB_URL", "postgresql://crypto")
    monkeypatch.setattr(database_module, "engine", SimpleNamespace(begin=lambda: FakeBegin()))

    database_module.ensure_runtime_schema_migrations()

    joined = "\n".join(executed)
    assert "ADD COLUMN IF NOT EXISTS status" in joined
    assert "ADD COLUMN IF NOT EXISTS suspended_until" in joined
    assert "ADD COLUMN IF NOT EXISTS suspension_reason" in joined
    assert "ADD COLUMN IF NOT EXISTS is_banned" in joined
    assert "ADD COLUMN IF NOT EXISTS notes" in joined
    assert "ADD COLUMN IF NOT EXISTS must_change_password" in joined
    assert "ADD COLUMN IF NOT EXISTS temporary_password_expires_at" in joined
    assert "CREATE TABLE IF NOT EXISTS beta_access_audit_logs" in joined
    assert "CREATE INDEX IF NOT EXISTS ix_beta_access_audit_logs_email_created" in joined
    assert "CREATE TABLE IF NOT EXISTS admin_action_logs" in joined
    assert "CREATE INDEX IF NOT EXISTS ix_admin_action_logs_created_at" in joined


def test_decode_token_handles_valid_expired_and_invalid_tokens(monkeypatch):
    monkeypatch.setattr(auth_middleware, "JWT_SECRET", "unit-test-secret")

    valid_token = jwt.encode(
        {"sub": "123", "type": "access"},
        "unit-test-secret",
        algorithm="HS256",
    )
    assert auth_middleware._decode_token(valid_token)["sub"] == "123"

    expired_token = jwt.encode(
        {
            "sub": "123",
            "type": "access",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        "unit-test-secret",
        algorithm="HS256",
    )
    with pytest.raises(HTTPException) as expired_exc:
        auth_middleware._decode_token(expired_token)
    assert expired_exc.value.detail == "Token expired"

    with pytest.raises(HTTPException) as invalid_exc:
        auth_middleware._decode_token("not-a-jwt")
    assert invalid_exc.value.detail == "Invalid token"


@pytest.mark.asyncio
async def test_auth_dependencies_cover_optional_required_and_admin_paths(
    monkeypatch, auth_db_session
):
    monkeypatch.setattr(auth_middleware, "JWT_SECRET", "unit-test-secret")
    monkeypatch.setattr(auth_middleware, "ADMIN_EMAILS", {"admin@example.com"})

    admin_id = uuid.uuid4()
    user_id = uuid.uuid4()
    auth_db_session.add_all(
        [
            User(
                id=admin_id,
                email="Admin@Example.com",
                password_hash="secret",
                name="Admin",
            ),
            User(
                id=user_id,
                email="user@example.com",
                password_hash="secret",
                name="User",
            ),
        ]
    )
    auth_db_session.commit()

    def _credentials(payload: dict) -> HTTPAuthorizationCredentials:
        token = jwt.encode(payload, "unit-test-secret", algorithm="HS256")
        return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

    request = SimpleNamespace(method="GET", url=SimpleNamespace(path="/api/favorites/"))

    assert await auth_middleware.get_current_user_optional(None, auth_db_session) is None
    assert (
        await auth_middleware.get_current_user_optional(
            _credentials({"type": "refresh", "sub": str(user_id)}),
            auth_db_session,
        )
        is None
    )
    assert (
        await auth_middleware.get_current_user_optional(
            _credentials({"type": "access"}),
            auth_db_session,
        )
        is None
    )
    assert (
        await auth_middleware.get_current_user_optional(
            _credentials({"type": "access", "sub": "not-a-uuid"}),
            auth_db_session,
        )
        is None
    )
    assert (
        await auth_middleware.get_current_user_optional(
            _credentials({"type": "access", "sub": str(uuid.uuid4())}),
            auth_db_session,
        )
        is None
    )
    assert await auth_middleware.get_current_user_optional(
        _credentials({"type": "access", "sub": str(user_id)}),
        auth_db_session,
    ) == str(user_id)

    with pytest.raises(HTTPException) as missing_auth_exc:
        await auth_middleware.get_current_user(request, None, auth_db_session)
    assert missing_auth_exc.value.detail == "Missing authentication"

    with pytest.raises(HTTPException) as wrong_type_exc:
        await auth_middleware.get_current_user(
            request,
            _credentials({"type": "refresh", "sub": str(user_id)}),
            auth_db_session,
        )
    assert wrong_type_exc.value.detail == "Invalid token type"

    with pytest.raises(HTTPException) as bad_payload_exc:
        await auth_middleware.get_current_user(
            request,
            _credentials({"type": "access"}),
            auth_db_session,
        )
    assert bad_payload_exc.value.detail == "Invalid token payload"

    with pytest.raises(HTTPException) as missing_user_exc:
        await auth_middleware.get_current_user(
            request,
            _credentials({"type": "access", "sub": str(uuid.uuid4())}),
            auth_db_session,
        )
    assert missing_user_exc.value.detail == "User not found"

    assert await auth_middleware.get_current_user(
        request,
        _credentials({"type": "access", "sub": str(user_id)}),
        auth_db_session,
    ) == str(user_id)

    assert auth_middleware.is_admin_email("ADMIN@example.com") is True
    assert auth_middleware.is_admin_email("user@example.com") is False
    assert auth_middleware.is_admin_email(None) is False

    with pytest.raises(HTTPException) as admin_exc:
        await auth_middleware.get_current_admin(str(user_id), auth_db_session)
    assert admin_exc.value.detail == "Admin access required"

    assert await auth_middleware.get_current_admin(str(admin_id), auth_db_session) == str(admin_id)


@pytest.mark.asyncio
async def test_auth_middleware_handles_banned_suspended_and_expired_users(
    monkeypatch, auth_db_session
):
    monkeypatch.setattr(auth_middleware, "JWT_SECRET", "unit-test-secret")

    banned_user = User(
        id=uuid.uuid4(),
        email="banned@example.com",
        password_hash="secret",
        name="Banned",
        status="banned",
        is_banned=True,
    )
    suspended_user = User(
        id=uuid.uuid4(),
        email="suspended@example.com",
        password_hash="secret",
        name="Suspended",
        status="suspended",
        suspended_until=datetime.utcnow() + timedelta(minutes=10),
    )
    expired_user = User(
        id=uuid.uuid4(),
        email="expired@example.com",
        password_hash="secret",
        name="Expired",
        status="suspended",
        suspended_until=datetime.utcnow() - timedelta(minutes=5),
        suspension_reason="timeout",
    )
    auth_db_session.add_all([banned_user, suspended_user, expired_user])
    auth_db_session.commit()

    with pytest.raises(HTTPException, match="banned"):
        auth_middleware._ensure_user_accessible(banned_user, datetime.utcnow())

    with pytest.raises(HTTPException, match="suspended"):
        auth_middleware._ensure_user_accessible(suspended_user, datetime.utcnow())

    assert auth_middleware._is_user_temporarily_suspended(suspended_user, datetime.utcnow()) is True
    assert auth_middleware._ensure_user_accessible(expired_user, datetime.utcnow()) is True
    assert expired_user.status == "active"
    assert expired_user.suspended_until is None
    assert expired_user.suspension_reason is None

    token = jwt.encode(
        {"type": "access", "sub": str(expired_user.id)},
        "unit-test-secret",
        algorithm="HS256",
    )
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    request = SimpleNamespace(method="GET", url=SimpleNamespace(path="/api/favorites/"))
    assert await auth_middleware.get_current_user(request, credentials, auth_db_session) == str(
        expired_user.id
    )


def test_auth_route_status_helpers_login_me_and_refresh(monkeypatch, auth_db_session):
    monkeypatch.setattr(auth_routes, "JWT_SECRET", "unit-test-secret")
    monkeypatch.setattr(auth_routes, "JWT_ACCESS_EXPIRE_MINUTES", 15)
    monkeypatch.setattr(auth_routes, "JWT_REFRESH_EXPIRE_DAYS", 7)
    monkeypatch.setattr(
        auth_routes, "_verify_password", lambda password, hashed: password == hashed
    )

    active_user = User(
        id=uuid.uuid4(),
        email="user@example.com",
        password_hash="valid-pass",
        name="User",
        status="active",
    )
    banned_user = User(
        id=uuid.uuid4(),
        email="blocked@example.com",
        password_hash="valid-pass",
        name="Blocked",
        status="banned",
        is_banned=True,
    )
    expired_user = User(
        id=uuid.uuid4(),
        email="expired-login@example.com",
        password_hash="valid-pass",
        name="Expired Login",
        status="suspended",
        suspended_until=datetime.utcnow() - timedelta(minutes=1),
        suspension_reason="expired",
    )
    suspended_user = User(
        id=uuid.uuid4(),
        email="suspended-login@example.com",
        password_hash="valid-pass",
        name="Suspended Login",
        status="suspended",
        suspended_until=datetime.utcnow() + timedelta(minutes=5),
    )
    auth_db_session.add_all([active_user, banned_user, expired_user, suspended_user])
    auth_db_session.commit()

    with pytest.raises(HTTPException, match="banned"):
        auth_routes._raise_if_blocked_by_status(banned_user, datetime.utcnow())

    with pytest.raises(HTTPException, match="suspended"):
        auth_routes._raise_if_blocked_by_status(suspended_user, datetime.utcnow())

    auth_routes._raise_if_blocked_by_status(expired_user, datetime.utcnow())
    assert expired_user.status == "active"
    assert expired_user.suspended_until is None
    assert expired_user.suspension_reason is None

    with pytest.raises(HTTPException, match="Invalid credentials"):
        auth_routes.login(
            auth_routes.LoginRequest(email="missing@example.com", password="x"), auth_db_session
        )

    with pytest.raises(HTTPException, match="Invalid credentials"):
        auth_routes.login(
            auth_routes.LoginRequest(email="user@example.com", password="wrong-pass"),
            auth_db_session,
        )

    login_response = auth_routes.login(
        auth_routes.LoginRequest(email="user@example.com", password="valid-pass"),
        auth_db_session,
    )
    assert login_response.email == "user@example.com"
    assert login_response.accessToken
    assert login_response.refreshToken

    with pytest.raises(HTTPException, match="Invalid credentials"):
        auth_routes.login(
            auth_routes.LoginRequest(email="user@example.com", password=""),
            auth_db_session,
        )

    access_token = auth_routes._generate_access_token(active_user)
    me_response = auth_routes.me(authorization=f"Bearer {access_token}", db=auth_db_session)
    assert me_response.email == "user@example.com"

    refresh_token = auth_routes._generate_refresh_token(active_user)
    refresh_response = auth_routes.refresh(
        auth_routes.RefreshRequest(refreshToken=refresh_token),
        auth_db_session,
    )
    assert refresh_response.email == "user@example.com"

    with pytest.raises(HTTPException, match="User not found"):
        ghost_refresh = jwt.encode(
            {"sub": str(uuid.uuid4()), "type": "refresh"},
            "unit-test-secret",
            algorithm="HS256",
        )
        auth_routes.refresh(auth_routes.RefreshRequest(refreshToken=ghost_refresh), auth_db_session)


def test_closed_beta_registration_blocks_public_and_allows_invited_or_explicit_public(
    monkeypatch, auth_db_session
):
    invited_email = f"invited-{uuid.uuid4().hex}@example.com"
    admin_email = f"admin-{uuid.uuid4().hex}@example.com"
    visitor_email = f"visitor-{uuid.uuid4().hex}@example.com"
    public_email = f"public-enabled-{uuid.uuid4().hex}@example.com"

    monkeypatch.setattr(auth_routes, "_hash_password", lambda password: f"hash::{password}")
    monkeypatch.setattr(auth_routes, "BETA_PUBLIC_REGISTRATION_ENABLED", False)
    monkeypatch.setattr(auth_routes, "BETA_INVITED_EMAILS", {invited_email})
    monkeypatch.setattr(auth_routes, "ADMIN_EMAILS", {admin_email})

    with pytest.raises(HTTPException) as blocked_exc:
        auth_routes.register(
            auth_routes.RegisterRequest(
                email=visitor_email,
                password="valid-pass",
                name="Visitor",
            ),
            auth_db_session,
        )
    assert blocked_exc.value.status_code == 403
    assert blocked_exc.value.detail == "Closed beta access requires invitation"
    assert auth_db_session.query(User).filter(User.email == visitor_email).first() is None

    invited = auth_routes.register(
        auth_routes.RegisterRequest(
            email=invited_email.upper(),
            password="valid-pass",
            name="Invited",
        ),
        auth_db_session,
    )
    assert invited.email == invited_email

    admin_bootstrap = auth_routes.register(
        auth_routes.RegisterRequest(
            email=admin_email,
            password="valid-pass",
            name="Admin",
        ),
        auth_db_session,
    )
    assert admin_bootstrap.email == admin_email

    monkeypatch.setattr(auth_routes, "BETA_PUBLIC_REGISTRATION_ENABLED", True)
    public = auth_routes.register(
        auth_routes.RegisterRequest(
            email=public_email,
            password="valid-pass",
            name="Public Enabled",
        ),
        auth_db_session,
    )
    assert public.email == public_email


def test_beta_lead_access_creates_temp_user_and_audit_without_exposing_password(
    auth_db_session,
):
    email = f"lead-{uuid.uuid4().hex}@example.com"
    sent_messages = []

    result = create_beta_access_for_lead(
        auth_db_session,
        name="Lead User",
        email=email.upper(),
        whatsapp="51999999999",
        profile="iniciante",
        pain="muito ruido",
        temporary_password="TemporaryPass123!",
        email_sender=lambda message: sent_messages.append(message) or True,
    )

    user = auth_db_session.query(User).filter(User.email == email).one()
    assert result.email == email
    assert result.user_created is True
    assert result.must_change_password is True
    assert result.welcome_email_sent is True
    assert result.temporary_password_expires_at is not None
    assert user.must_change_password is True
    assert user.temporary_password_expires_at is not None
    assert user.access_invitation_source == "landing"
    assert user.password_hash != "TemporaryPass123!"
    assert verify_password("TemporaryPass123!", user.password_hash)
    assert sent_messages[0].login_url == "https://criptofarol.com.br/login"
    assert sent_messages[0].temporary_password == "TemporaryPass123!"

    audit = auth_db_session.query(BetaAccessAuditLog).filter_by(email=email).one()
    assert audit.user_id == str(user.id)
    assert audit.action == "lead_access_created"
    assert audit.result == "created_email_sent"
    assert "TemporaryPass123!" not in str(audit.metadata_json)


def test_beta_lead_existing_user_preserves_password_and_records_audit(auth_db_session):
    user = User(
        id=uuid.uuid4(),
        email=f"existing-lead-{uuid.uuid4().hex}@example.com",
        password_hash="original-hash",
        name="Existing",
        status="active",
        must_change_password=False,
    )
    auth_db_session.add(user)
    auth_db_session.commit()

    result = create_beta_access_for_lead(
        auth_db_session,
        name="Existing Lead",
        email=user.email,
        temporary_password="ShouldNotBeUsed123!",
        email_sender=lambda _message: True,
    )

    auth_db_session.refresh(user)
    assert result.user_created is False
    assert result.result == "existing_user_preserved"
    assert user.password_hash == "original-hash"
    assert user.must_change_password is False

    audit = auth_db_session.query(BetaAccessAuditLog).filter_by(email=user.email).one()
    assert audit.action == "lead_access_requested"
    assert audit.result == "existing_user_preserved"
    assert "ShouldNotBeUsed123!" not in str(audit.metadata_json)


def test_leads_route_returns_safe_response_without_temporary_password(auth_db_session):
    email = f"route-lead-{uuid.uuid4().hex}@example.com"

    response = leads_routes.create_lead_access(
        leads_routes.LeadAccessRequest(
            name="Route Lead",
            email=email,
            whatsapp="51999999999",
            profile="intermediario",
            pain="timing",
            origin="landing-v4",
        ),
        auth_db_session,
    )

    payload = response.model_dump()
    assert payload["status"] == "accepted"
    assert payload["message"]
    assert "userCreated" not in payload
    assert "mustChangePassword" not in payload
    assert "temporaryPasswordExpiresAt" not in payload
    assert "TemporaryPass" not in str(payload)
    assert "token_urlsafe" not in str(payload)


def test_leads_stats_counts_landing_users_and_remaining_spots(auth_db_session):
    initial = leads_routes.get_lead_stats(auth_db_session)
    base_registered = initial.registered
    base_spots_left = initial.spotsLeft

    landing_user = User(
        id=uuid.uuid4(),
        email=f"landing-stats-{uuid.uuid4().hex}@example.com",
        password_hash="hash",
        name="Landing Stats",
        status="active",
        is_banned=False,
        access_invitation_source="landing",
    )
    manual_user = User(
        id=uuid.uuid4(),
        email=f"manual-stats-{uuid.uuid4().hex}@example.com",
        password_hash="hash",
        name="Manual Stats",
        status="active",
        is_banned=False,
        access_invitation_source="admin",
    )
    banned_landing_user = User(
        id=uuid.uuid4(),
        email=f"banned-landing-stats-{uuid.uuid4().hex}@example.com",
        password_hash="hash",
        name="Banned Landing Stats",
        status="banned",
        is_banned=True,
        access_invitation_source="landing",
    )
    auth_db_session.add_all([landing_user, manual_user, banned_landing_user])
    auth_db_session.commit()

    stats = leads_routes.get_lead_stats(auth_db_session)

    assert stats.totalSpots == 50
    assert stats.registered == min(50, base_registered + 1)
    assert stats.spotsLeft == max(0, base_spots_left - 1)


def test_beta_lead_does_not_commit_unknown_password_when_email_not_sent(auth_db_session):
    email = f"no-email-{uuid.uuid4().hex}@example.com"

    result = create_beta_access_for_lead(
        auth_db_session,
        name="No Email",
        email=email,
        temporary_password="TemporaryPass123!",
        email_sender=lambda _message: False,
    )

    assert result.user_created is False
    assert result.result == "created_email_not_configured"
    assert auth_db_session.query(User).filter(User.email == email).first() is None

    audit = auth_db_session.query(BetaAccessAuditLog).filter_by(email=email).one()
    assert audit.user_id is None
    assert audit.result == "created_email_not_configured"
    assert "TemporaryPass123!" not in str(audit.metadata_json)


def test_gog_welcome_email_uses_existing_clara_gmail_channel(monkeypatch, tmp_path):
    env_file = tmp_path / ".env.leads"
    env_file.write_text("GOG_KEYRING_PASSWORD=secret-value\n", encoding="utf-8")
    calls = []

    def fake_run(args, **kwargs):
        calls.append((args, kwargs))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr("app.services.beta_access.BETA_ACCESS_GOG_ENV_FILE", str(env_file))
    monkeypatch.setenv("BETA_ACCESS_WELCOME_EMAIL_CC", "alan@example.com")
    monkeypatch.setattr("app.services.beta_access.subprocess.run", fake_run)

    sent = send_welcome_email_gog(
        WelcomeEmail(
            to_email="lead@example.com",
            name="Lead",
            login_url="https://criptofarol.com.br/login",
            temporary_password="TemporaryPass123!",
            expires_at=datetime(2026, 5, 11, 12, 0, 0),
        )
    )

    assert sent is True
    args, kwargs = calls[0]
    assert args[:3] == ["gog", "gmail", "send"]
    assert "--to" in args and "lead@example.com" in args
    assert "--cc" in args and "alan@example.com" in args
    assert kwargs["env"]["GOG_KEYRING_PASSWORD"] == "secret-value"
    assert kwargs["capture_output"] is True


def test_temporary_password_login_requires_change_and_expires(monkeypatch, auth_db_session):
    now = datetime.utcnow()
    email = f"temp-login-{uuid.uuid4().hex}@example.com"
    result = create_beta_access_for_lead(
        auth_db_session,
        name="Temp Login",
        email=email,
        now=now,
        temporary_password="TemporaryPass123!",
        email_sender=lambda _message: True,
    )
    assert result.user_created is True

    login_response = auth_routes.login(
        auth_routes.LoginRequest(email=email, password="TemporaryPass123!"),
        auth_db_session,
    )
    assert login_response.email == email
    assert login_response.mustChangePassword is True
    assert login_response.accessToken

    user = auth_db_session.query(User).filter(User.email == email).one()
    user.temporary_password_expires_at = now - timedelta(minutes=1)
    auth_db_session.add(user)
    auth_db_session.commit()

    with pytest.raises(HTTPException) as expired_exc:
        auth_routes.login(
            auth_routes.LoginRequest(email=email, password="TemporaryPass123!"),
            auth_db_session,
        )
    assert expired_exc.value.status_code == 403
    assert expired_exc.value.detail == "Temporary password expired"


def test_temporary_password_token_is_blocked_from_regular_protected_apis(auth_db_session):
    email = f"temp-gate-{uuid.uuid4().hex}@example.com"
    create_beta_access_for_lead(
        auth_db_session,
        name="Temp Gate",
        email=email,
        temporary_password="TemporaryPass123!",
        email_sender=lambda _message: True,
    )
    login_response = auth_routes.login(
        auth_routes.LoginRequest(email=email, password="TemporaryPass123!"),
        auth_db_session,
    )
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=login_response.accessToken,
    )

    blocked_request = SimpleNamespace(
        method="GET",
        url=SimpleNamespace(path="/api/favorites/"),
    )
    with pytest.raises(HTTPException) as blocked_exc:
        asyncio.run(
            auth_middleware.get_current_user(
                request=blocked_request,
                credentials=credentials,
                db=auth_db_session,
            )
        )
    assert blocked_exc.value.status_code == 403
    assert blocked_exc.value.detail == "Password change required"
    assert (
        asyncio.run(
            auth_middleware.get_current_user_optional(
                credentials,
                db=auth_db_session,
            )
        )
        is None
    )

    allowed_request = SimpleNamespace(
        method="PUT",
        url=SimpleNamespace(path="/api/users/password"),
    )
    assert (
        asyncio.run(
            auth_middleware.get_current_user(
                request=allowed_request,
                credentials=credentials,
                db=auth_db_session,
            )
        )
        == login_response.userId
    )


def test_password_change_clears_temporary_access_state(monkeypatch, auth_db_session):
    email = f"temp-change-{uuid.uuid4().hex}@example.com"
    create_beta_access_for_lead(
        auth_db_session,
        name="Temp Change",
        email=email,
        temporary_password="TemporaryPass123!",
        email_sender=lambda _message: True,
    )
    user = auth_db_session.query(User).filter(User.email == email).one()

    response = user_profile_routes.update_password(
        user_profile_routes.ChangePasswordRequest(
            currentPassword="TemporaryPass123!",
            newPassword="OwnPassword456!",
        ),
        current_user_id=str(user.id),
        db=auth_db_session,
    )

    auth_db_session.refresh(user)
    assert response.message == "Password updated successfully"
    assert user.must_change_password is False
    assert user.temporary_password_expires_at is None
    assert user.temporary_password_used_at is not None
    assert user.password_changed_at is not None
    assert verify_password("OwnPassword456!", user.password_hash)


def test_database_timescale_policy_verification_reports_missing_and_exception_paths(monkeypatch):
    class _Scalar:
        def __init__(self, value):
            self.value = value

        def scalar(self):
            return self.value

    class _Conn:
        def __init__(self, values):
            self.values = values
            self.executed = []
            self.should_raise = None

        def execute(self, statement, params=None):
            sql = str(statement)
            self.executed.append((sql, params))

            if self.should_raise is not None:
                raise self.should_raise

            if "timescaledb_information.hypertables" in sql:
                return _Scalar(self.values.get("hypertable", False))
            if "FROM timescaledb_information.jobs" in sql:
                proc_name = (params or {}).get("proc_name") if params else None
                if proc_name == "policy_retention":
                    return _Scalar(self.values.get("retention", False))
                if proc_name == "policy_compression":
                    return _Scalar(self.values.get("compression", False))
            if "UNNEST(C.RELOPTIONS" in sql.upper():
                return _Scalar(self.values.get("compression_setting", False))
            return _Scalar(False)

    warnings = []
    infos = []

    def _warn(msg, *_, **__):
        warnings.append(msg)

    def _info(msg, *_, **__):
        infos.append(msg)

    monkeypatch.setattr(database_module.logger, "warning", _warn)
    monkeypatch.setattr(database_module.logger, "info", _info)

    conn = _Conn(
        {"hypertable": True, "retention": False, "compression": False, "compression_setting": False}
    )
    database_module._verify_market_ohlcv_timescale_policies(conn)
    assert any("incomplete" in str(item) for item in warnings)

    warnings.clear()
    complete_conn = _Conn(
        {
            "hypertable": True,
            "retention": True,
            "compression": True,
            "compression_setting": True,
        }
    )
    database_module._verify_market_ohlcv_timescale_policies(complete_conn)
    assert any("verified as active" in str(item) for item in infos)

    warnings.clear()
    error_conn = _Conn({})
    error_conn.should_raise = RuntimeError("boom")
    database_module._verify_market_ohlcv_timescale_policies(error_conn)
    assert any("Could not complete timescale policy verification" in str(item) for item in warnings)


def test_database_runtime_schema_migrations_timescale_setup_exception_keeps_running(monkeypatch):
    class _Scalar:
        def scalar(self):
            return None

    class _FailingConn:
        def __init__(self):
            self.executed = []

        def execute(self, statement, params=None):
            sql = str(statement)
            self.executed.append((sql, params))
            if "create extension if not exists timescaledb" in sql.lower():
                raise RuntimeError("timescaledb unavailable")
            return _Scalar()

    conn = _FailingConn()

    class _Begin:
        def __init__(self, c):
            self._c = c

        def __enter__(self):
            return self._c

        def __exit__(self, exc_type, exc, tb):
            return False

    warnings = []
    called = []

    monkeypatch.setattr(database_module, "DB_URL", "postgresql://unit-tests")
    monkeypatch.setattr(database_module, "engine", SimpleNamespace(begin=lambda: _Begin(conn)))
    monkeypatch.setattr(
        database_module,
        "_verify_market_ohlcv_timescale_policies",
        lambda *_: called.append("called"),
    )
    monkeypatch.setattr(
        database_module.logger, "warning", lambda msg, *a, **k: warnings.append(msg)
    )
    monkeypatch.setattr(database_module, "_policy_checks_enabled", lambda: True)

    database_module.ensure_runtime_schema_migrations()

    assert called == []
    assert any("Timescale configuration for market_ohlcv failed" in str(item) for item in warnings)
