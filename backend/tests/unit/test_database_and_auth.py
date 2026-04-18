from __future__ import annotations

import builtins
import io
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import User
import app.database as database_module
import app.middleware.authMiddleware as auth_middleware


@pytest.fixture
def auth_db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


def test_database_url_resolution_helpers_and_dependency(monkeypatch, tmp_path):
    monkeypatch.delenv("ALLOW_SQLITE_FOR_TESTS", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr(database_module.sys, "argv", ["uvicorn"])

    assert database_module._allow_sqlite_for_tests() is False
    monkeypatch.setenv("ALLOW_SQLITE_FOR_TESTS", "yes")
    assert database_module._allow_sqlite_for_tests() is True
    monkeypatch.delenv("ALLOW_SQLITE_FOR_TESTS", raising=False)
    monkeypatch.setattr(database_module.sys, "argv", ["pytest", "-q"])
    assert database_module._allow_sqlite_for_tests() is True

    assert database_module._is_postgres_url("postgresql://db")
    assert database_module._is_postgres_url("postgresql+psycopg2://db")
    assert database_module._is_postgres_url(" sqlite:///db ") is False

    monkeypatch.setattr(
        database_module,
        "get_settings",
        lambda: SimpleNamespace(database_url="postgresql://settings"),
    )
    monkeypatch.setenv("DATABASE_URL", "postgresql://env")
    assert database_module.resolve_db_url() == "postgresql://settings"

    monkeypatch.setattr(database_module, "get_settings", lambda: SimpleNamespace(database_url=None))
    assert database_module.resolve_db_url() == "postgresql://env"

    monkeypatch.setenv("DATABASE_URL", "sqlite:///runtime.db")
    monkeypatch.setattr(database_module.sys, "argv", ["uvicorn"])
    with pytest.raises(RuntimeError, match="must point to PostgreSQL"):
        database_module.resolve_db_url()

    sqlite_path = tmp_path / "test.db"
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("ALLOW_SQLITE_FOR_TESTS", "1")
    monkeypatch.setattr(database_module, "DB_PATH", sqlite_path)
    assert database_module.resolve_db_url() == f"sqlite:///{sqlite_path}"

    monkeypatch.delenv("ALLOW_SQLITE_FOR_TESTS", raising=False)
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


def test_sqlite_runtime_migrations_and_postgres_sequence_sync(monkeypatch, tmp_path):
    db_file = tmp_path / "legacy.db"
    conn = sqlite3.connect(db_file)
    try:
        cur = conn.cursor()
        cur.execute("CREATE TABLE users (id TEXT PRIMARY KEY, email TEXT NOT NULL)")
        cur.execute(
            "INSERT INTO users (id, email) VALUES (?, ?)",
            ("user-1", "o.alan.silva@gmail.com"),
        )
        cur.execute("CREATE TABLE favorite_strategies (id INTEGER PRIMARY KEY, name TEXT NOT NULL)")
        cur.execute("INSERT INTO favorite_strategies (id, name) VALUES (1, 'Legacy favorite')")
        cur.execute("""
            CREATE TABLE monitor_preferences (
                symbol TEXT PRIMARY KEY,
                in_portfolio BOOLEAN NOT NULL DEFAULT 0,
                card_mode TEXT NOT NULL DEFAULT 'price',
                updated_at DATETIME
            )
            """)
        cur.execute("""
            INSERT INTO monitor_preferences (symbol, in_portfolio, card_mode, updated_at)
            VALUES ('BTC/USDT', 1, 'price', '2026-04-18T00:00:00Z')
            """)
        conn.commit()
    finally:
        conn.close()

    monkeypatch.setattr(database_module, "DB_URL", f"sqlite:///{db_file}")
    monkeypatch.setattr(database_module, "DB_PATH", db_file)
    database_module.ensure_runtime_schema_migrations()

    conn = sqlite3.connect(db_file)
    try:
        cur = conn.cursor()

        cur.execute("PRAGMA table_info(users)")
        assert "last_login" in {row[1] for row in cur.fetchall()}

        cur.execute("PRAGMA table_info(favorite_strategies)")
        assert "user_id" in {row[1] for row in cur.fetchall()}
        cur.execute("SELECT user_id FROM favorite_strategies WHERE id = 1")
        assert cur.fetchone()[0] == "user-1"

        cur.execute("PRAGMA table_info(monitor_preferences)")
        monitor_cols = {row[1] for row in cur.fetchall()}
        assert {"user_id", "price_timeframe", "theme"}.issubset(monitor_cols)
        cur.execute("""
            SELECT user_id, symbol, in_portfolio, card_mode, price_timeframe, theme
            FROM monitor_preferences
            """)
        assert cur.fetchone() == ("user-1", "BTC/USDT", 1, "price", "1d", "dark-green")
    finally:
        conn.close()

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
        await auth_middleware.get_current_user(None, auth_db_session)
    assert missing_auth_exc.value.detail == "Missing authentication"

    with pytest.raises(HTTPException) as wrong_type_exc:
        await auth_middleware.get_current_user(
            _credentials({"type": "refresh", "sub": str(user_id)}),
            auth_db_session,
        )
    assert wrong_type_exc.value.detail == "Invalid token type"

    with pytest.raises(HTTPException) as bad_payload_exc:
        await auth_middleware.get_current_user(
            _credentials({"type": "access"}),
            auth_db_session,
        )
    assert bad_payload_exc.value.detail == "Invalid token payload"

    with pytest.raises(HTTPException) as missing_user_exc:
        await auth_middleware.get_current_user(
            _credentials({"type": "access", "sub": str(uuid.uuid4())}),
            auth_db_session,
        )
    assert missing_user_exc.value.detail == "User not found"

    assert await auth_middleware.get_current_user(
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
