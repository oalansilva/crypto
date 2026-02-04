"""Agent chat endpoints (single-tenant MVP).

This route allows the frontend to "chat about" a saved FavoriteStrategy.

LLM calls are delegated to OpenClaw via the local `openclaw agent` CLI.
This reuses OpenClaw's existing provider auth (oauth) and returns token usage
from the CLI JSON output.

Security notes (important):
- This is intended for single-tenant setups.
- By default it is DISABLED unless AGENT_CHAT_ENABLED=1.
- Add your own auth (session cookie, API key) before exposing publicly.
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.database import get_db
from sqlalchemy.orm import Session

from app.models import FavoriteStrategy

router = APIRouter(prefix="/api/agent", tags=["agent"])


def _enabled() -> bool:
    return os.getenv("AGENT_CHAT_ENABLED", "0") in ("1", "true", "yes", "on")


def _debug_enabled() -> bool:
    return os.getenv("AGENT_CHAT_DEBUG", "0") in ("1", "true", "yes", "on")


# Per-conversation lock to avoid OpenClaw session file lock issues.
_LOCKS: Dict[str, asyncio.Lock] = {}


def _get_lock(key: str) -> asyncio.Lock:
    if key not in _LOCKS:
        _LOCKS[key] = asyncio.Lock()
    return _LOCKS[key]


class AgentChatRequest(BaseModel):
    favorite_id: int
    message: str = Field(..., min_length=1, max_length=8000)
    conversation_id: Optional[str] = None
    thinking: str = "low"  # off|minimal|low|medium|high


class AgentChatResponse(BaseModel):
    conversation_id: str
    reply: str
    model: Optional[str] = None
    provider: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    duration_ms: Optional[int] = None
    debug: Optional[Dict[str, Any]] = None


def _build_prompt(fav: FavoriteStrategy, user_msg: str) -> str:
    """Build a compact context prompt."""
    context = {
        "favorite": {
            "id": fav.id,
            "name": fav.name,
            "symbol": fav.symbol,
            "timeframe": fav.timeframe,
            "strategy_name": fav.strategy_name,
            "parameters": fav.parameters,
            "metrics": fav.metrics,
            "notes": fav.notes,
            "tier": fav.tier,
            "start_date": fav.start_date,
            "end_date": fav.end_date,
            "period_type": fav.period_type,
            "created_at": str(fav.created_at),
        }
    }

    return (
        "Você é um analista de estratégias de trading. "
        "Analise a estratégia FAVORITA abaixo e responda de forma direta, com hipóteses e próximos testes. "
        "Se precisar, faça perguntas objetivas.\n\n"
        f"DADOS (JSON):\n{json.dumps(context, ensure_ascii=False)}\n\n"
        f"MENSAGEM DO USUÁRIO:\n{user_msg}\n"
    )


from app.services.openclaw_gateway_client import run_agent_via_gateway


async def _run_openclaw_agent(session_key: str, message: str, thinking: str, timeout_s: int = 180) -> Dict[str, Any]:
    """Call OpenClaw via Gateway WS API and return a result shape similar to the CLI.

    We return a dict with a `payloads` list when possible, plus `meta.agentMeta` when present.
    """

    start = time.time()
    payload = await run_agent_via_gateway(
        message=message,
        session_key=session_key,
        agent_id="main",
        thinking=thinking,
        timeout_s=timeout_s,
    )
    dur_ms = int((time.time() - start) * 1000)

    # Gateway returns: { runId, status, summary, result }
    result = payload.get("result") if isinstance(payload, dict) else None

    # Normalize to the previous expectations of this route
    data: Dict[str, Any] = {
        "payloads": None,
        "meta": {
            "durationMs": dur_ms,
            "agentMeta": None,
        },
        "raw": payload,
    }

    if isinstance(result, dict):
        # Some versions return { payloads, meta: { agentMeta } }
        if isinstance(result.get("payloads"), list):
            data["payloads"] = result.get("payloads")
        if isinstance((result.get("meta") or {}).get("agentMeta"), dict):
            data["meta"]["agentMeta"] = (result.get("meta") or {}).get("agentMeta")

    return data


@router.post("/chat", response_model=AgentChatResponse)
async def agent_chat(req: AgentChatRequest, db: Session = Depends(get_db)):
    if not _enabled():
        raise HTTPException(status_code=403, detail="Agent chat disabled. Set AGENT_CHAT_ENABLED=1")

    fav = db.query(FavoriteStrategy).filter(FavoriteStrategy.id == req.favorite_id).first()
    if not fav:
        raise HTTPException(status_code=404, detail="Favorite not found")

    # stable conversation_id per favorite unless provided
    conversation_id = (req.conversation_id or f"fav-{fav.id}").strip()
    # Use an agent-scoped gateway session key for stability
    session_key = f"agent:main:agentchat:{conversation_id}"

    lock = _get_lock(session_key)
    async with lock:
        prompt = _build_prompt(fav, req.message)
        result = await _run_openclaw_agent(session_key=session_key, message=prompt, thinking=req.thinking)

    payloads = result.get("payloads") or []

    # Robustly extract assistant text from OpenClaw CLI JSON.
    # Different OpenClaw versions/providers may shape payloads differently.
    def _collect_text(x: Any, out: list[str]) -> None:
        if x is None:
            return
        if isinstance(x, str):
            if x.strip():
                out.append(x.strip())
            return
        if isinstance(x, dict):
            # Prefer explicit common keys first
            for k in ("text", "content", "message", "output_text"):
                if k in x and isinstance(x[k], str) and x[k].strip():
                    out.append(x[k].strip())
                    # don't early-return; there may be more text nested
            # Traverse other fields
            for v in x.values():
                _collect_text(v, out)
            return
        if isinstance(x, (list, tuple)):
            for it in x:
                _collect_text(it, out)
            return

    reply_parts: list[str] = []
    if isinstance(payloads, list):
        for p in payloads:
            _collect_text(p, reply_parts)

    # De-dup while preserving order
    seen: set[str] = set()
    deduped: list[str] = []
    for t in reply_parts:
        if t in seen:
            continue
        seen.add(t)
        deduped.append(t)

    reply = "\n\n".join(deduped).strip()

    # final fallbacks
    if not reply:
        for k in ("reply", "text", "output"):
            v = result.get(k)
            if isinstance(v, str) and v.strip():
                reply = v.strip()
                break

    agent_meta = (((result.get("meta") or {}).get("agentMeta")) or {})
    usage = agent_meta.get("usage")

    debug: Optional[Dict[str, Any]] = None
    if _debug_enabled():
        # keep small + safe
        debug = {
            "topLevelKeys": sorted(list(result.keys())),
            "metaKeys": sorted(list((result.get("meta") or {}).keys())),
            "payloadsCount": len(payloads) if isinstance(payloads, list) else None,
            "agentMeta": agent_meta or None,
            # include a compact preview to figure out where the text lives
            "payloadsPreview": payloads[:2] if isinstance(payloads, list) else payloads,
        }

    return AgentChatResponse(
        conversation_id=conversation_id,
        reply=reply,
        model=agent_meta.get("model"),
        provider=agent_meta.get("provider"),
        usage=usage,
        duration_ms=(result.get("meta") or {}).get("durationMs"),
        debug=debug,
    )
