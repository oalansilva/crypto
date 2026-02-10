from __future__ import annotations

import asyncio
import json
import os
import time
import uuid
from typing import Any, Dict, Optional

import websockets


def _get_gateway_url() -> str:
    return os.getenv("OPENCLAW_GATEWAY_URL", "ws://127.0.0.1:18789")


def _get_gateway_token() -> Optional[str]:
    tok = os.getenv("OPENCLAW_GATEWAY_TOKEN")
    if tok:
        return tok

    # Optional: read token from a file path so we don't hardcode secrets in the repo.
    token_file = (os.getenv("OPENCLAW_GATEWAY_TOKEN_FILE") or "").strip()
    if token_file:
        try:
            with open(token_file, "r", encoding="utf-8") as f:
                v = f.read().strip()
            return v or None
        except Exception:
            return None

    return None


def _now_ms() -> int:
    return int(time.time() * 1000)


async def run_agent_via_gateway(*,
                               message: str,
                               session_key: str,
                               agent_id: str = "main",
                               thinking: str = "low",
                               timeout_s: int = 180,
                               extra_system_prompt: Optional[str] = None) -> Dict[str, Any]:
    """Run OpenClaw agent through the Gateway WS protocol.

    Returns the gateway payload from the final `agent` response:
      { runId, status:"ok", result: {...} }

    This avoids spawning `openclaw agent` as a subprocess.
    """

    url = _get_gateway_url()
    token = _get_gateway_token()
    if not token:
        raise RuntimeError("OPENCLAW_GATEWAY_TOKEN is not set")

    connect_req_id = f"conn-{uuid.uuid4().hex[:10]}"
    run_id = uuid.uuid4().hex

    # We use the request id as the idempotencyKey.
    agent_req_id = run_id

    connect_frame = {
        "type": "req",
        "id": connect_req_id,
        "method": "connect",
        "params": {
            "minProtocol": 3,
            "maxProtocol": 3,
            # Use a known client schema identifier so the gateway accepts it.
            "client": {
                "id": "gateway-client",
                "version": "0.1",
                "platform": "linux",
                "mode": "backend",
            },
            "role": "operator",
            "scopes": ["operator.read", "operator.write"],
            "caps": [],
            "commands": [],
            "permissions": {},
            "auth": {"token": token},
            "locale": "pt-BR",
            "userAgent": "crypto-backend/0.1",
            # device is optional when gateway.controlUi.allowInsecureAuth=true
        },
    }

    agent_params: Dict[str, Any] = {
        "idempotencyKey": run_id,
        "agentId": agent_id,
        "sessionKey": session_key,
        "message": message,
        "thinking": thinking,
        "deliver": False,
        "channel": "last",
        "timeout": int(timeout_s),
    }
    if extra_system_prompt:
        agent_params["extraSystemPrompt"] = extra_system_prompt

    agent_frame = {
        "type": "req",
        "id": agent_req_id,
        "method": "agent",
        "params": agent_params,
    }

    deadline = time.time() + timeout_s

    async with websockets.connect(url, ping_interval=20, ping_timeout=20, close_timeout=5) as ws:
        # Expect challenge event first (but be robust)
        await ws.send(json.dumps(connect_frame, ensure_ascii=False))

        accepted = False
        final_payload: Optional[Dict[str, Any]] = None

        while time.time() < deadline:
            remaining = max(1.0, deadline - time.time())
            raw = await asyncio.wait_for(ws.recv(), timeout=remaining)
            frame = json.loads(raw)

            ftype = frame.get("type")
            if ftype == "event" and frame.get("event") == "connect.challenge":
                # We ignore challenge since insecure auth is enabled.
                continue

            if ftype == "res" and frame.get("id") == connect_req_id:
                if not frame.get("ok"):
                    raise RuntimeError(f"gateway connect failed: {frame.get('error')}")
                # once connected, send agent request
                await ws.send(json.dumps(agent_frame, ensure_ascii=False))
                continue

            if ftype == "res" and frame.get("id") == agent_req_id:
                if not frame.get("ok"):
                    raise RuntimeError(f"gateway agent call failed: {frame.get('error')}")

                payload = frame.get("payload") or {}
                status = payload.get("status")
                if status == "accepted":
                    accepted = True
                    continue
                if status == "ok":
                    final_payload = payload
                    break
                if status == "error":
                    raise RuntimeError(payload.get("summary") or "agent error")

        if not accepted:
            raise TimeoutError("agent request was not accepted before timeout")
        if not final_payload:
            raise TimeoutError("agent did not return final response before timeout")

        return final_payload
