"""TypeSafe/Jev client. Key lives only in server env. Never log the secret."""

from __future__ import annotations

import json
import logging
import os
import time
import urllib.error
import urllib.request
from decimal import Decimal
from typing import Any, Optional

from app.services.scalp_engine import JEV_LATE_MS, JevSignal, Side, SYMBOL

logger = logging.getLogger(__name__)

_SECRET_ENV_NAMES = ("JEV_API_KEY", "TYPESAFE_API_KEY")


def jev_api_key() -> Optional[str]:
    for name in _SECRET_ENV_NAMES:
        value = (os.getenv(name) or "").strip()
        if value:
            return value
    return None


def jev_available() -> bool:
    if jev_api_key():
        return True
    return _stand_in_enabled()


def _stand_in_enabled() -> bool:
    return (os.getenv("JEV_STAND_IN") or "").strip().lower() in {"1", "true", "yes", "on"}


def _base_url() -> str:
    return (os.getenv("JEV_BASE_URL") or "").strip().rstrip("/")


def _redact(message: str) -> str:
    text = str(message or "")
    key = jev_api_key()
    if key:
        text = text.replace(key, "<redacted>")
    for name in _SECRET_ENV_NAMES:
        raw = (os.getenv(name) or "").strip()
        if raw:
            text = text.replace(raw, "<redacted>")
    return text


def _parse_side(value: Any) -> Optional[Side]:
    token = str(value or "").strip().upper()
    if token in {"BUY", "SELL"}:
        return token  # type: ignore[return-value]
    return None


def stand_in_signal(*, latency_ms: int = 1) -> JevSignal:
    """Test/dev stand-in. Live without a key MUST NOT send (caller checks jev_api_key)."""
    side = _parse_side(os.getenv("JEV_STAND_IN_SIDE"))
    confidence_raw = (os.getenv("JEV_STAND_IN_CONFIDENCE") or "0").strip()
    try:
        confidence = Decimal(confidence_raw)
    except Exception:
        confidence = Decimal("0")
    edge = (os.getenv("JEV_STAND_IN_EDGE") or "").strip().lower() in {"1", "true", "yes", "on"}
    toxic = (os.getenv("JEV_STAND_IN_TOXIC") or "").strip().lower() in {"1", "true", "yes", "on"}
    return JevSignal(
        side=side,
        confidence=confidence,
        edge_after_fees=edge,
        book_toxic=toxic,
        latency_ms=latency_ms,
        cost_quote=Decimal("0"),
    )


def request_jev(payload: dict[str, Any], *, timeout_s: Optional[float] = None) -> JevSignal:
    """One HTTP call. Timeout defaults to the 800 ms late gate."""
    started = time.perf_counter()
    timeout = float(timeout_s if timeout_s is not None else (JEV_LATE_MS / 1000.0))
    key = jev_api_key()
    if not key:
        if _stand_in_enabled():
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            return stand_in_signal(latency_ms=max(1, elapsed_ms))
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        return JevSignal(
            side=None,
            confidence=Decimal("0"),
            edge_after_fees=False,
            book_toxic=False,
            latency_ms=elapsed_ms,
        )

    url = f"{_base_url() or 'https://api.typesafe.invalid'}/v1/signal"
    body = json.dumps({"symbol": SYMBOL, **payload}, separators=(",", ":")).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {key}")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
        parsed = json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        logger.warning("Jev HTTP error status=%s latency_ms=%s", int(exc.code or 0), elapsed_ms)
        return JevSignal(
            side=None,
            confidence=Decimal("0"),
            edge_after_fees=False,
            book_toxic=False,
            latency_ms=elapsed_ms,
        )
    except Exception as exc:
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        logger.warning("Jev request failed latency_ms=%s err=%s", elapsed_ms, _redact(str(exc)))
        return JevSignal(
            side=None,
            confidence=Decimal("0"),
            edge_after_fees=False,
            book_toxic=False,
            latency_ms=max(
                elapsed_ms, JEV_LATE_MS + 1 if elapsed_ms >= JEV_LATE_MS else elapsed_ms
            ),
        )

    elapsed_ms = int((time.perf_counter() - started) * 1000)
    data = parsed if isinstance(parsed, dict) else {}
    try:
        confidence = Decimal(str(data.get("confidence") or "0"))
    except Exception:
        confidence = Decimal("0")
    try:
        cost = Decimal(str(data.get("cost") or data.get("cost_quote") or "0"))
    except Exception:
        cost = Decimal("0")
    toxic = bool(data.get("toxic") or data.get("book_toxic"))
    edge = bool(data.get("edge_after_fees") if "edge_after_fees" in data else data.get("edge"))
    return JevSignal(
        side=_parse_side(data.get("side")),
        confidence=confidence,
        edge_after_fees=edge,
        book_toxic=toxic,
        latency_ms=elapsed_ms,
        cost_quote=cost,
    )
