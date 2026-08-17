from __future__ import annotations

import json

import httpx
import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import FavoriteStrategy
import app.routes.agent_chat as agent_chat_route
import app.services.hermes_responses_client as hermes_client


@pytest.fixture
def app_db_session(postgres_isolation, unit_database_url):
    engine = create_engine(unit_database_url)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


class _FakeAsyncClient:
    def __init__(self, handler):
        self.handler = handler

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post(self, url, headers=None, json=None):
        return self.handler(url, headers or {}, json or {})


def _json_response(status: int, payload: dict):
    request = httpx.Request("POST", "http://127.0.0.1:8642/v1/responses")
    return httpx.Response(status, json=payload, request=request)


def test_hermes_url_and_optional_token(monkeypatch, tmp_path):
    monkeypatch.delenv("HERMES_API_BASE_URL", raising=False)
    assert hermes_client._responses_url() == "http://127.0.0.1:8642/v1/responses"
    monkeypatch.setenv("HERMES_API_BASE_URL", "http://127.0.0.1:8642/v1")
    assert hermes_client._responses_url() == "http://127.0.0.1:8642/v1/responses"

    monkeypatch.delenv("HERMES_API_TOKEN", raising=False)
    monkeypatch.delenv("HERMES_API_KEY", raising=False)
    monkeypatch.delenv("HERMES_API_TOKEN_FILE", raising=False)
    assert hermes_client._optional_token() is None

    monkeypatch.setenv("HERMES_API_TOKEN", "secret-token")
    assert hermes_client._optional_token() == "secret-token"

    monkeypatch.delenv("HERMES_API_TOKEN", raising=False)
    token_file = tmp_path / "hermes.token"
    token_file.write_text("file-token\n", encoding="utf-8")
    monkeypatch.setenv("HERMES_API_TOKEN_FILE", str(token_file))
    assert hermes_client._optional_token() == "file-token"


def test_extract_response_text_sanitizes_secrets():
    payload = {
        "output": [
            {
                "type": "message",
                "content": [
                    {
                        "type": "output_text",
                        "text": "Use Bearer abcdefghijklmnop and continue",
                    }
                ],
            }
        ]
    }
    text = hermes_client.extract_response_text(payload)
    assert "abcdefghijklmnop" not in text
    assert "[redacted]" in text


@pytest.mark.asyncio
async def test_run_agent_via_hermes_success_maps_thinking(monkeypatch):
    captured = {}

    def handler(url, headers, body):
        captured["url"] = url
        captured["headers"] = headers
        captured["body"] = body
        return _json_response(
            200,
            {
                "id": "resp_1",
                "model": "hermes-agent",
                "output": [
                    {
                        "type": "message",
                        "content": [{"type": "output_text", "text": "Resposta final"}],
                    }
                ],
                "usage": {"input_tokens": 3, "output_tokens": 2},
            },
        )

    monkeypatch.setattr(
        hermes_client.httpx,
        "AsyncClient",
        lambda timeout=None: _FakeAsyncClient(handler),
    )
    payload = await hermes_client.run_agent_via_hermes(
        message="hello",
        session_key="session-1",
        thinking="high",
        extra_system_prompt="extra",
        timeout_s=5,
    )
    assert payload["reply"] == "Resposta final"
    assert captured["url"] == "http://127.0.0.1:8642/v1/responses"
    assert captured["body"]["model_options"]["reasoning_effort"] == "high"
    assert captured["body"]["conversation"] == "session-1"
    assert captured["headers"]["X-Hermes-Session-Key"] == "session-1"
    assert captured["headers"]["Idempotency-Key"]
    assert captured["body"]["instructions"] == "extra"
    assert "18789" not in captured["url"]
    assert "OPENCLAW" not in json.dumps(captured)

    payload_off = await hermes_client.run_agent_via_hermes(
        message="hello",
        session_key="session-1",
        thinking="off",
        timeout_s=5,
    )
    assert payload_off["reply"] == "Resposta final"
    assert captured["body"]["model_options"]["reasoning_effort"] == "none"


@pytest.mark.asyncio
async def test_run_agent_via_hermes_timeout_and_empty(monkeypatch):
    def timeout_handler(url, headers, body):
        raise httpx.TimeoutException("slow")

    monkeypatch.setattr(
        hermes_client.httpx,
        "AsyncClient",
        lambda timeout=None: _FakeAsyncClient(timeout_handler),
    )
    with pytest.raises(TimeoutError, match="timed out"):
        await hermes_client.run_agent_via_hermes(
            message="hello", session_key="session-2", timeout_s=1
        )

    def empty_handler(url, headers, body):
        return _json_response(200, {"output": []})

    monkeypatch.setattr(
        hermes_client.httpx,
        "AsyncClient",
        lambda timeout=None: _FakeAsyncClient(empty_handler),
    )
    with pytest.raises(hermes_client.HermesEmptyReplyError):
        await hermes_client.run_agent_via_hermes(
            message="hello", session_key="session-3", timeout_s=1
        )


@pytest.mark.asyncio
async def test_agent_chat_route_success_timeout_empty_and_no_openclaw(monkeypatch, app_db_session):
    fav = FavoriteStrategy(
        id=1,
        user_id="user-1",
        name="Momentum",
        symbol="BTC/USDT",
        timeframe="1h",
        strategy_name="ema_rsi",
        parameters={"ema": 21},
        metrics={"sharpe": 1.5},
        notes="Watch volatility",
        tier=1,
        start_date="2025-01-01",
        end_date="2025-12-31",
        period_type="1y",
    )
    app_db_session.add(fav)
    app_db_session.commit()

    monkeypatch.setenv("AGENT_CHAT_ENABLED", "1")
    agent_chat_route._LOCKS.clear()

    async def fake_hermes(**kwargs):
        assert kwargs["thinking"] == "low"
        return {
            "reply": "Primeira resposta",
            "model": "hermes-agent",
            "usage": {"tokens": 9},
        }

    monkeypatch.setattr(agent_chat_route, "run_agent_via_hermes", fake_hermes)
    response = await agent_chat_route.agent_chat(
        agent_chat_route.AgentChatRequest(favorite_id=1, message="Analyze this setup"),
        "user-1",
        app_db_session,
    )
    assert response.conversation_id == "fav-1"
    assert response.reply == "Primeira resposta"
    assert response.provider == "hermes"
    assert response.model == "hermes-agent"

    async def fake_timeout(**kwargs):
        raise TimeoutError("Hermes API Server timed out")

    monkeypatch.setattr(agent_chat_route, "run_agent_via_hermes", fake_timeout)
    with pytest.raises(HTTPException) as timeout_exc:
        await agent_chat_route.agent_chat(
            agent_chat_route.AgentChatRequest(favorite_id=1, message="timeout"),
            "user-1",
            app_db_session,
        )
    assert timeout_exc.value.status_code == 504
    assert timeout_exc.value.detail == "Hermes timed out"

    async def fake_empty(**kwargs):
        raise agent_chat_route.HermesEmptyReplyError("empty")

    monkeypatch.setattr(agent_chat_route, "run_agent_via_hermes", fake_empty)
    with pytest.raises(HTTPException) as empty_exc:
        await agent_chat_route.agent_chat(
            agent_chat_route.AgentChatRequest(favorite_id=1, message="empty"),
            "user-1",
            app_db_session,
        )
    assert empty_exc.value.status_code == 502
    assert "empty" in str(empty_exc.value.detail).lower()

    for path in (agent_chat_route.__file__, hermes_client.__file__):
        text = open(path, encoding="utf-8").read()
        assert "OPENCLAW_GATEWAY" not in text
        assert "18789" not in text
        assert "openclaw" not in text.lower()
