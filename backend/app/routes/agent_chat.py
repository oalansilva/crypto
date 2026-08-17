"""Agent chat endpoints (single-tenant MVP).

LLM calls go to Hermes `POST /v1/responses`. There is no legacy gateway fallback.
The public HTTP contract (`thinking`, `conversation_id`, `detail` on errors) stays stable.

Security notes:
- Single-tenant MVP.
- Disabled unless AGENT_CHAT_ENABLED=1.
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.authMiddleware import get_current_user
from app.models import FavoriteStrategy
from app.services.hermes_responses_client import (
    HermesEmptyReplyError,
    run_agent_via_hermes,
)

router = APIRouter(prefix="/api/agent", tags=["agent"])


def _enabled() -> bool:
    return os.getenv("AGENT_CHAT_ENABLED", "0") in ("1", "true", "yes", "on")


def _debug_enabled() -> bool:
    return os.getenv("AGENT_CHAT_DEBUG", "0") in ("1", "true", "yes", "on")


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


async def _run_hermes_agent(
    session_key: str, message: str, thinking: str, timeout_s: int = 180
) -> Dict[str, Any]:
    start = time.time()
    payload = await run_agent_via_hermes(
        message=message,
        session_key=session_key,
        thinking=thinking,
        timeout_s=timeout_s,
        extra_system_prompt="Responda em português brasileiro. Não revele secrets, tokens ou paths internos.",
    )
    return {
        "reply": payload.get("reply") or "",
        "model": payload.get("model"),
        "usage": payload.get("usage"),
        "meta": {"durationMs": int((time.time() - start) * 1000)},
        "raw": payload.get("raw"),
    }


@router.post("/chat", response_model=AgentChatResponse)
async def agent_chat(
    req: AgentChatRequest,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not _enabled():
        raise HTTPException(status_code=403, detail="Agent chat disabled. Set AGENT_CHAT_ENABLED=1")

    fav = (
        db.query(FavoriteStrategy)
        .filter(
            FavoriteStrategy.id == req.favorite_id,
            FavoriteStrategy.user_id == current_user_id,
        )
        .first()
    )
    if not fav:
        raise HTTPException(status_code=404, detail="Favorite not found")

    conversation_id = (req.conversation_id or f"fav-{fav.id}").strip()
    session_key = f"agent:main:agentchat:{conversation_id}"

    lock = _get_lock(session_key)
    async with lock:
        prompt = _build_prompt(fav, req.message)
        try:
            result = await _run_hermes_agent(
                session_key=session_key, message=prompt, thinking=req.thinking
            )
        except TimeoutError:
            raise HTTPException(status_code=504, detail="Hermes timed out") from None
        except HermesEmptyReplyError:
            raise HTTPException(status_code=502, detail="Agent returned an empty reply") from None
        except RuntimeError as exc:
            raise HTTPException(
                status_code=502, detail=str(exc) or "Hermes request failed"
            ) from None

    reply = str(result.get("reply") or "").strip()
    if not reply:
        raise HTTPException(status_code=502, detail="Agent returned an empty reply")

    debug: Optional[Dict[str, Any]] = None
    if _debug_enabled():
        debug = {
            "topLevelKeys": sorted(list(result.keys())),
            "model": result.get("model"),
        }

    return AgentChatResponse(
        conversation_id=conversation_id,
        reply=reply,
        model=result.get("model"),
        provider="hermes",
        usage=result.get("usage"),
        duration_ms=(result.get("meta") or {}).get("durationMs"),
        debug=debug,
    )
