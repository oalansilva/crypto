"""Auth e contrato sem path para GET /api/logs/tail (card #686)."""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest
from fastapi import FastAPI, HTTPException

import app.routes.logs as logs_route
from app.middleware.authMiddleware import get_current_admin


def _build_app() -> FastAPI:
    app = FastAPI()
    app.include_router(logs_route.router)
    return app


@pytest.fixture
def log_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "full_execution_log.txt"
    path.write_text("line-a\nline-b\n", encoding="utf-8")
    monkeypatch.setitem(logs_route.LOG_MAP, "full_execution_log", path)
    return path


@pytest.mark.asyncio
async def test_tail_anonymous_returns_401(log_file: Path):
    app = _build_app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/api/logs/tail", params={"name": "full_execution_log"})

    assert response.status_code == 401
    body = response.json()
    assert "path" not in body
    assert log_file.read_text(encoding="utf-8") not in response.text


@pytest.mark.asyncio
async def test_tail_non_admin_returns_403(log_file: Path):
    app = _build_app()

    async def _deny_admin():
        raise HTTPException(status_code=403, detail="Admin access required")

    app.dependency_overrides[get_current_admin] = _deny_admin
    transport = httpx.ASGITransport(app=app)
    try:
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get(
                "/api/logs/tail",
                params={"name": "full_execution_log"},
                headers={"Authorization": "Bearer user-token"},
            )
    finally:
        app.dependency_overrides.pop(get_current_admin, None)

    assert response.status_code == 403
    body = response.json()
    assert "path" not in body
    assert "line-a" not in response.text


@pytest.mark.asyncio
async def test_tail_admin_200_omits_path(log_file: Path):
    app = _build_app()
    app.dependency_overrides[get_current_admin] = lambda: "admin-user"
    transport = httpx.ASGITransport(app=app)
    try:
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get(
                "/api/logs/tail",
                params={"name": "full_execution_log", "lines": 10},
                headers={"Authorization": "Bearer admin-token"},
            )
    finally:
        app.dependency_overrides.pop(get_current_admin, None)

    assert response.status_code == 200
    payload = response.json()
    assert "path" not in payload
    assert "/srv/" not in response.text
    assert "full_execution_log.txt" not in response.text
    assert payload["name"] == "full_execution_log"
    assert "line-a" in payload["content"]
    assert payload["file_id"]
