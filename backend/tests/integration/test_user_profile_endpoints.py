from __future__ import annotations

from uuid import uuid4

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import database as database_module
from app.database import Base, get_db
from app.main import app
from app.routes import auth as auth_routes
from app.routes import user_profile as user_profile_routes


def _build_session_local():
    engine = create_engine(
        "postgresql://postgres:postgres@127.0.0.1:5432/postgres",
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


async def _register_and_login(
    client: httpx.AsyncClient, email: str | None = None
) -> tuple[dict[str, str], str]:
    email = email or f"profile-{uuid4().hex}@example.com"
    register = await client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "supersecret123",
            "name": "Profile Tester",
        },
    )
    assert register.status_code == 201

    login = await client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": "supersecret123",
        },
    )
    assert login.status_code == 200
    return login.json(), email


@pytest.mark.asyncio
async def test_get_me_returns_authenticated_profile():
    SessionLocal = _build_session_local()
    _override_db(SessionLocal)
    _install_fast_password_helpers()
    transport = httpx.ASGITransport(app=app)

    try:
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            auth, email = await _register_and_login(client)

            response = await client.get(
                "/api/users/me",
                headers={"Authorization": f"Bearer {auth['accessToken']}"},
            )

        assert response.status_code == 200
        body = response.json()
        assert body["email"] == email
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
            auth, _ = await _register_and_login(client)

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
            auth, email = await _register_and_login(client)

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
                json={"email": email, "password": "newsupersecret456"},
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
            auth, _ = await _register_and_login(client)

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


def test_runtime_db_url_is_postgresql_for_profile_module(monkeypatch):
    monkeypatch.setattr(
        database_module,
        "DB_URL",
        "postgresql://postgres:postgres@127.0.0.1:5432/postgres",
    )
    assert database_module._is_postgres_url(database_module.DB_URL)
