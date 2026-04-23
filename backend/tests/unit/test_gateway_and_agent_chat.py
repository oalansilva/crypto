from __future__ import annotations

import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import FavoriteStrategy
import app.routes.agent_chat as agent_chat_route
import app.services.openclaw_gateway_client as gateway_client


@pytest.fixture
def app_db_session():
    engine = create_engine("postgresql://postgres:postgres@127.0.0.1:5432/postgres")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


class _FakeWebSocketConnection:
    def __init__(self, mode: str = "success"):
        self.mode = mode
        self.sent: list[dict] = []
        self.recv_index = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def send(self, raw: str):
        self.sent.append(json.loads(raw))

    async def recv(self) -> str:
        self.recv_index += 1
        if self.recv_index == 1:
            return json.dumps({"type": "event", "event": "connect.challenge"})

        if self.recv_index == 2:
            connect_id = self.sent[0]["id"]
            if self.mode == "connect-error":
                return json.dumps({"type": "res", "id": connect_id, "ok": False, "error": "denied"})
            return json.dumps(
                {"type": "res", "id": connect_id, "ok": True, "payload": {"status": "ok"}}
            )

        agent_id = self.sent[1]["id"]
        if self.recv_index == 3:
            if self.mode == "agent-call-error":
                return json.dumps(
                    {"type": "res", "id": agent_id, "ok": False, "error": "agent failed"}
                )
            if self.mode == "not-accepted":
                return json.dumps(
                    {"type": "res", "id": agent_id, "ok": True, "payload": {"status": "queued"}}
                )
            return json.dumps(
                {"type": "res", "id": agent_id, "ok": True, "payload": {"status": "accepted"}}
            )

        if self.mode == "agent-status-error":
            return json.dumps(
                {
                    "type": "res",
                    "id": agent_id,
                    "ok": True,
                    "payload": {"status": "error", "summary": "upstream failure"},
                }
            )

        if self.mode == "no-final":
            raise TimeoutError("socket stalled")

        return json.dumps(
            {
                "type": "res",
                "id": agent_id,
                "ok": True,
                "payload": {
                    "status": "ok",
                    "result": {
                        "payloads": [{"text": "Resposta final"}],
                        "meta": {
                            "agentMeta": {
                                "model": "gpt",
                                "provider": "openai",
                                "usage": {"tokens": 1},
                            }
                        },
                    },
                },
            }
        )


def test_gateway_token_helpers_and_now_ms(monkeypatch, tmp_path):
    monkeypatch.setenv("OPENCLAW_GATEWAY_URL", "ws://gateway.example")
    assert gateway_client._get_gateway_url() == "ws://gateway.example"

    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "secret-token")
    assert gateway_client._get_gateway_token() == "secret-token"

    monkeypatch.delenv("OPENCLAW_GATEWAY_TOKEN", raising=False)
    token_file = tmp_path / "gateway.token"
    token_file.write_text("file-token\n", encoding="utf-8")
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN_FILE", str(token_file))
    assert gateway_client._get_gateway_token() == "file-token"

    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN_FILE", str(tmp_path / "missing.token"))
    assert gateway_client._get_gateway_token() is None

    monkeypatch.setattr(gateway_client.time, "time", lambda: 123.456)
    assert gateway_client._now_ms() == 123456


@pytest.mark.asyncio
async def test_run_agent_via_gateway_covers_success_and_error_paths(monkeypatch):
    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "token")

    connection = _FakeWebSocketConnection(mode="success")
    monkeypatch.setattr(gateway_client.websockets, "connect", lambda *args, **kwargs: connection)
    payload = await gateway_client.run_agent_via_gateway(
        message="hello",
        session_key="session-1",
        extra_system_prompt="extra",
        timeout_s=5,
    )
    assert payload["status"] == "ok"
    assert payload["result"]["payloads"][0]["text"] == "Resposta final"
    assert connection.sent[0]["method"] == "connect"
    assert connection.sent[1]["method"] == "agent"
    assert connection.sent[1]["params"]["extraSystemPrompt"] == "extra"

    monkeypatch.delenv("OPENCLAW_GATEWAY_TOKEN", raising=False)
    monkeypatch.delenv("OPENCLAW_GATEWAY_TOKEN_FILE", raising=False)
    with pytest.raises(RuntimeError, match="OPENCLAW_GATEWAY_TOKEN is not set"):
        await gateway_client.run_agent_via_gateway(message="hello", session_key="session-2")

    monkeypatch.setenv("OPENCLAW_GATEWAY_TOKEN", "token")
    monkeypatch.setattr(
        gateway_client.websockets,
        "connect",
        lambda *args, **kwargs: _FakeWebSocketConnection(mode="connect-error"),
    )
    with pytest.raises(RuntimeError, match="gateway connect failed"):
        await gateway_client.run_agent_via_gateway(
            message="hello", session_key="session-3", timeout_s=5
        )

    monkeypatch.setattr(
        gateway_client.websockets,
        "connect",
        lambda *args, **kwargs: _FakeWebSocketConnection(mode="agent-call-error"),
    )
    with pytest.raises(RuntimeError, match="gateway agent call failed"):
        await gateway_client.run_agent_via_gateway(
            message="hello", session_key="session-4", timeout_s=5
        )

    monkeypatch.setattr(
        gateway_client.websockets,
        "connect",
        lambda *args, **kwargs: _FakeWebSocketConnection(mode="agent-status-error"),
    )
    with pytest.raises(RuntimeError, match="upstream failure"):
        await gateway_client.run_agent_via_gateway(
            message="hello", session_key="session-5", timeout_s=5
        )

    monkeypatch.setattr(
        gateway_client.websockets,
        "connect",
        lambda *args, **kwargs: _FakeWebSocketConnection(mode="not-accepted"),
    )
    with pytest.raises(TimeoutError, match="accepted"):
        await gateway_client.run_agent_via_gateway(
            message="hello", session_key="session-6", timeout_s=5
        )


@pytest.mark.asyncio
async def test_agent_chat_route_and_helpers_cover_success_debug_and_fallbacks(
    monkeypatch, app_db_session
):
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
    monkeypatch.setenv("AGENT_CHAT_DEBUG", "0")
    agent_chat_route._LOCKS.clear()

    assert agent_chat_route._enabled() is True
    assert agent_chat_route._debug_enabled() is False
    assert agent_chat_route._get_lock("same-key") is agent_chat_route._get_lock("same-key")

    prompt = agent_chat_route._build_prompt(fav, "What should I test next?")
    assert "Momentum" in prompt
    assert "What should I test next?" in prompt
    assert '"strategy_name": "ema_rsi"' in prompt

    async def fake_gateway_run(**kwargs):
        return {
            "status": "ok",
            "result": {
                "payloads": [
                    {"text": "Primeira resposta"},
                    {"nested": [{"text": "Primeira resposta"}, {"content": "Detalhe extra"}]},
                ],
                "meta": {
                    "agentMeta": {"model": "gpt", "provider": "openai", "usage": {"tokens": 9}}
                },
            },
        }

    monkeypatch.setattr(agent_chat_route, "run_agent_via_gateway", fake_gateway_run)
    normalized = await agent_chat_route._run_openclaw_agent(
        session_key="session-1",
        message="prompt",
        thinking="low",
        timeout_s=5,
    )
    assert normalized["meta"]["agentMeta"]["model"] == "gpt"
    assert len(normalized["payloads"]) == 2

    request = agent_chat_route.AgentChatRequest(favorite_id=1, message="Analyze this setup")
    response = await agent_chat_route.agent_chat(request, "user-1", app_db_session)
    assert response.conversation_id == "fav-1"
    assert response.reply == "Primeira resposta\n\nDetalhe extra"
    assert response.model == "gpt"
    assert response.provider == "openai"
    assert response.usage == {"tokens": 9}
    assert response.debug is None

    monkeypatch.setenv("AGENT_CHAT_DEBUG", "1")
    assert agent_chat_route._debug_enabled() is True

    async def fake_route_run(**kwargs):
        return {
            "payloads": [],
            "reply": "Fallback reply",
            "meta": {"durationMs": 12, "agentMeta": {"model": "mini", "provider": "openai"}},
        }

    monkeypatch.setattr(agent_chat_route, "_run_openclaw_agent", fake_route_run)
    fallback = await agent_chat_route.agent_chat(
        agent_chat_route.AgentChatRequest(
            favorite_id=1,
            message="Use fallback",
            conversation_id="custom-conv",
        ),
        "user-1",
        app_db_session,
    )
    assert fallback.conversation_id == "custom-conv"
    assert fallback.reply == "Fallback reply"
    assert fallback.debug is not None
    assert fallback.debug["payloadsCount"] == 0

    monkeypatch.setenv("AGENT_CHAT_ENABLED", "0")
    with pytest.raises(HTTPException) as disabled_exc:
        await agent_chat_route.agent_chat(request, "user-1", app_db_session)
    assert disabled_exc.value.status_code == 403

    monkeypatch.setenv("AGENT_CHAT_ENABLED", "1")
    with pytest.raises(HTTPException) as missing_exc:
        await agent_chat_route.agent_chat(
            agent_chat_route.AgentChatRequest(favorite_id=999, message="missing"),
            "user-1",
            app_db_session,
        )
    assert missing_exc.value.status_code == 404
