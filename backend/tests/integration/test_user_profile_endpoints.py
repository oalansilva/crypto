from __future__ import annotations

import httpx
import pytest
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import database as database_module
from app.database import Base, get_db
from app.main import app
from app.routes import auth as auth_routes
from app.routes import user_profile as user_profile_routes


def _build_session_local():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _override_db(SessionLocal):
    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db


def _install_fast_password_helpers():
    def _hash_password(password: str) -> str:
        return f"test-hash::{password}"

    def _verify_password(password: str, hashed: str) -> bool:
        return hashed == f"test-hash::{password}"

    auth_routes._hash_password = _hash_password
    auth_routes._verify_password = _verify_password
    user_profile_routes._hash_password = _hash_password
    user_profile_routes._verify_password = _verify_password


async def _register_and_login(client: httpx.AsyncClient) -> dict[str, str]:
    register = await client.post(
        "/api/auth/register",
        json={
            "email": "profile@example.com",
            "password": "supersecret123",
            "name": "Profile Tester",
        },
    )
    assert register.status_code == 201

    login = await client.post(
        "/api/auth/login",
        json={
            "email": "profile@example.com",
            "password": "supersecret123",
        },
    )
    assert login.status_code == 200
    return login.json()


@pytest.mark.asyncio
async def test_get_me_returns_authenticated_profile():
    SessionLocal = _build_session_local()
    _override_db(SessionLocal)
    _install_fast_password_helpers()
    transport = httpx.ASGITransport(app=app)

    try:
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            auth = await _register_and_login(client)

            response = await client.get(
                "/api/users/me",
                headers={"Authorization": f"Bearer {auth['accessToken']}"},
            )

        assert response.status_code == 200
        body = response.json()
        assert body["email"] == "profile@example.com"
        assert body["name"] == "Profile Tester"
        assert body["createdAt"] is not None
        assert body["lastLogin"] is not None
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_me_requires_authentication():
    SessionLocal = _build_session_local()
    _override_db(SessionLocal)
    _install_fast_password_helpers()
    transport = httpx.ASGITransport(app=app)

    try:
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get("/api/users/me")

        assert response.status_code == 401
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_put_me_updates_name():
    SessionLocal = _build_session_local()
    _override_db(SessionLocal)
    _install_fast_password_helpers()
    transport = httpx.ASGITransport(app=app)

    try:
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            auth = await _register_and_login(client)

            response = await client.put(
                "/api/users/me",
                headers={"Authorization": f"Bearer {auth['accessToken']}"},
                json={"name": "Updated Tester"},
            )

        assert response.status_code == 200
        assert response.json()["name"] == "Updated Tester"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_put_password_changes_password_when_current_matches():
    SessionLocal = _build_session_local()
    _override_db(SessionLocal)
    _install_fast_password_helpers()
    transport = httpx.ASGITransport(app=app)

    try:
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            auth = await _register_and_login(client)

            response = await client.put(
                "/api/users/password",
                headers={"Authorization": f"Bearer {auth['accessToken']}"},
                json={
                    "currentPassword": "supersecret123",
                    "newPassword": "newsupersecret456",
                },
            )
            relogin = await client.post(
                "/api/auth/login",
                json={"email": "profile@example.com", "password": "newsupersecret456"},
            )

        assert response.status_code == 200
        assert response.json()["message"] == "Password updated successfully"
        assert relogin.status_code == 200
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_put_password_rejects_incorrect_current_password():
    SessionLocal = _build_session_local()
    _override_db(SessionLocal)
    _install_fast_password_helpers()
    transport = httpx.ASGITransport(app=app)

    try:
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            auth = await _register_and_login(client)

            response = await client.put(
                "/api/users/password",
                headers={"Authorization": f"Bearer {auth['accessToken']}"},
                json={
                    "currentPassword": "wrong-password",
                    "newPassword": "newsupersecret456",
                },
            )

        assert response.status_code == 400
        assert response.json()["detail"] == "Current password is incorrect"
    finally:
        app.dependency_overrides.clear()


def test_login_works_after_runtime_sqlite_adds_missing_last_login(tmp_path, monkeypatch):
    db_file = tmp_path / "legacy_auth.db"
    conn = sqlite3.connect(db_file)
    try:
        conn.execute("""
            CREATE TABLE users (
                id TEXT PRIMARY KEY,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                created_at DATETIME
            )
            """)
        conn.execute(
            """
            INSERT INTO users (id, email, password_hash, name, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                "11111111-1111-1111-1111-111111111111",
                "profile@example.com",
                "test-hash::supersecret123",
                "Profile Tester",
                "2026-04-03T00:00:00",
            ),
        )
        conn.commit()
    finally:
        conn.close()

    engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False},
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    monkeypatch.setattr(database_module, "DB_URL", f"sqlite:///{db_file}")
    monkeypatch.setattr(database_module, "DB_PATH", db_file)

    database_module.ensure_runtime_schema_migrations()
    _install_fast_password_helpers()

    with SessionLocal() as db:
        response = auth_routes.login(
            auth_routes.LoginRequest(
                email="profile@example.com",
                password="supersecret123",
            ),
            db=db,
        )

    assert response.email == "profile@example.com"
    assert response.accessToken
    assert response.refreshToken

    with sqlite3.connect(db_file) as check_conn:
        columns = {row[1] for row in check_conn.execute("PRAGMA table_info(users)").fetchall()}
        assert "last_login" in columns

        stored_last_login = check_conn.execute(
            "SELECT last_login FROM users WHERE email = ?",
            ("profile@example.com",),
        ).fetchone()
        assert stored_last_login is not None
        assert stored_last_login[0] is not None
