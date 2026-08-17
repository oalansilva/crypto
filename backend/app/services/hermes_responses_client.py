from __future__ import annotations

import os
import re
import uuid
from typing import Any, Dict, Optional

import httpx

DEFAULT_HERMES_API_BASE_URL = "http://127.0.0.1:8642"
DEFAULT_TIMEOUT_S = 180
THINKING_LEVELS = {"off", "minimal", "low", "medium", "high"}
SECRETISH = re.compile(r"(?i)(bearer\s+\S+|sk-[A-Za-z0-9_-]{8,}|gh[pousr]_[A-Za-z0-9]{8,})")


class HermesEmptyReplyError(RuntimeError):
    pass


def _base_url() -> str:
    raw = (os.getenv("HERMES_API_BASE_URL") or DEFAULT_HERMES_API_BASE_URL).strip().rstrip("/")
    return raw or DEFAULT_HERMES_API_BASE_URL


def _responses_url() -> str:
    base = _base_url()
    root = base if base.endswith("/v1") else f"{base}/v1"
    return f"{root}/responses"


def _optional_token() -> Optional[str]:
    tok = (os.getenv("HERMES_API_TOKEN") or os.getenv("HERMES_API_KEY") or "").strip()
    if tok:
        return tok
    token_file = (os.getenv("HERMES_API_TOKEN_FILE") or "").strip()
    if not token_file:
        return None
    try:
        with open(token_file, "r", encoding="utf-8") as handle:
            value = handle.read().strip()
        return value or None
    except OSError:
        return None


def _sanitize_text(value: str) -> str:
    cleaned = SECRETISH.sub("[redacted]", value or "")
    return cleaned.strip()


def extract_response_text(payload: Any) -> str:
    if not isinstance(payload, dict):
        return ""
    for key in ("output_text", "text", "content"):
        direct = payload.get(key)
        if isinstance(direct, str) and direct.strip():
            return _sanitize_text(direct)
    output = payload.get("output")
    if not isinstance(output, list):
        return ""
    texts: list[str] = []
    for item in output:
        if not isinstance(item, dict):
            continue
        content = item.get("content")
        if isinstance(content, str) and content.strip():
            texts.append(content.strip())
            continue
        if isinstance(content, list):
            for part in content:
                if isinstance(part, dict):
                    text = part.get("text") or part.get("output_text")
                    if isinstance(text, str) and text.strip():
                        texts.append(text.strip())
                elif isinstance(part, str) and part.strip():
                    texts.append(part.strip())
    return _sanitize_text("\n\n".join(texts))


def _thinking_options(thinking: str) -> Dict[str, Any]:
    level = thinking if thinking in THINKING_LEVELS else "low"
    effort = "none" if level == "off" else level
    return {"model_options": {"reasoning_effort": effort}}


async def run_agent_via_hermes(
    *,
    message: str,
    session_key: str,
    thinking: str = "low",
    timeout_s: int = DEFAULT_TIMEOUT_S,
    extra_system_prompt: Optional[str] = None,
    idempotency_key: Optional[str] = None,
) -> Dict[str, Any]:
    """Call Hermes POST /v1/responses. No legacy gateway fallback."""
    headers = {
        "Content-Type": "application/json",
        "X-Hermes-Session-Key": session_key,
        "Idempotency-Key": idempotency_key or uuid.uuid4().hex,
    }
    token = _optional_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    body: Dict[str, Any] = {
        "input": message,
        "store": True,
        "conversation": session_key,
    }
    model = (os.getenv("HERMES_MODEL") or "").strip()
    if model:
        body["model"] = model
    if extra_system_prompt:
        body["instructions"] = extra_system_prompt
    body.update(_thinking_options(thinking))

    timeout = httpx.Timeout(timeout_s, connect=min(10.0, float(timeout_s)))
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(_responses_url(), headers=headers, json=body)
    except httpx.TimeoutException as exc:
        raise TimeoutError("Hermes API Server timed out") from exc
    except httpx.HTTPError as exc:
        raise RuntimeError("Hermes API Server unavailable") from exc

    payload: Any
    try:
        payload = response.json()
    except ValueError:
        payload = {"raw": _sanitize_text(response.text[:500])}

    if response.status_code >= 400:
        detail = ""
        if isinstance(payload, dict):
            err = payload.get("error")
            if isinstance(err, dict):
                detail = str(err.get("message") or "")
            elif isinstance(err, str):
                detail = err
            else:
                detail = str(payload.get("detail") or "")
        raise RuntimeError(
            _sanitize_text(detail) or f"Hermes API Server returned {response.status_code}"
        )

    reply = extract_response_text(payload)
    if not reply:
        raise HermesEmptyReplyError("Hermes API Server returned no usable text")

    usage = payload.get("usage") if isinstance(payload, dict) else None
    return {
        "reply": reply,
        "model": payload.get("model") if isinstance(payload, dict) else None,
        "usage": usage if isinstance(usage, dict) else None,
        "raw": payload,
    }
