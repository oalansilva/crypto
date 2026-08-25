from __future__ import annotations

from types import SimpleNamespace

import jwt
import pytest
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.testclient import TestClient

from app.database import get_db
from app.jwt_secret import KNOWN_DEFAULT_JWT_SECRET, resolve_jwt_secret
import app.middleware.authMiddleware as auth_middleware

VALID_SECRET = "a" * 32


def _assert_invalid_secret_error(exc: BaseException, candidate: str | None) -> None:
    message = str(exc)
    assert "JWT_SECRET" in message
    if candidate:
        assert candidate not in message


def test_resolve_jwt_secret_rejects_unset(monkeypatch):
    monkeypatch.delenv("JWT_SECRET", raising=False)
    with pytest.raises(RuntimeError) as exc:
        resolve_jwt_secret()
    _assert_invalid_secret_error(exc.value, None)


@pytest.mark.parametrize("candidate", ["", "   ", "\t\n"])
def test_resolve_jwt_secret_rejects_empty_or_whitespace(monkeypatch, candidate):
    monkeypatch.setenv("JWT_SECRET", candidate)
    with pytest.raises(RuntimeError) as exc:
        resolve_jwt_secret()
    _assert_invalid_secret_error(exc.value, candidate)


def test_resolve_jwt_secret_rejects_known_default(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", KNOWN_DEFAULT_JWT_SECRET)
    with pytest.raises(RuntimeError) as exc:
        resolve_jwt_secret()
    _assert_invalid_secret_error(exc.value, KNOWN_DEFAULT_JWT_SECRET)


def test_resolve_jwt_secret_rejects_short_secret(monkeypatch):
    candidate = "short-secret-value"
    assert len(candidate) < 32
    monkeypatch.setenv("JWT_SECRET", candidate)
    with pytest.raises(RuntimeError) as exc:
        resolve_jwt_secret()
    _assert_invalid_secret_error(exc.value, candidate)


def test_resolve_jwt_secret_accepts_valid_secret(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", f"  {VALID_SECRET}  ")
    assert resolve_jwt_secret() == VALID_SECRET


def test_access_token_signed_with_known_default_is_401():
    app = FastAPI()

    def _dummy_db():
        yield SimpleNamespace()

    app.dependency_overrides[get_db] = _dummy_db

    @app.get("/user")
    async def user_route(user_id: str = Depends(auth_middleware.get_current_user)):
        return {"user_id": user_id}

    @app.get("/admin")
    async def admin_route(user_id: str = Depends(auth_middleware.get_current_admin)):
        return {"user_id": user_id}

    forged = jwt.encode(
        {"sub": "00000000-0000-0000-0000-000000000001", "type": "access"},
        KNOWN_DEFAULT_JWT_SECRET,
        algorithm="HS256",
    )
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {forged}"}
    user_response = client.get("/user", headers=headers)
    admin_response = client.get("/admin", headers=headers)
    assert user_response.status_code == 401
    assert admin_response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_rejects_known_default_token():
    forged = jwt.encode(
        {"sub": "00000000-0000-0000-0000-000000000001", "type": "access"},
        KNOWN_DEFAULT_JWT_SECRET,
        algorithm="HS256",
    )
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=forged)
    request = SimpleNamespace(method="GET", url=SimpleNamespace(path="/api/auth/me"))
    with pytest.raises(HTTPException) as exc:
        await auth_middleware.get_current_user(request, credentials, SimpleNamespace())
    assert exc.value.status_code == 401
