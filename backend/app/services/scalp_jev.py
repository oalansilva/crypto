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
_DEFAULT_BASE_URL = "https://api.typesafe.ai"
_SYSTEMONE_PATH = "/v1/systemone"
_JEV_MODEL = "jev-latest"


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


def _endpoint_url() -> str:
    return f"{_base_url() or _DEFAULT_BASE_URL}{_SYSTEMONE_PATH}"


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


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _decimal(value: Any, default: str = "0") -> Decimal:
    try:
        return Decimal(str(value if value is not None else default))
    except Exception:
        return Decimal(default)


def _hold_signal(latency_ms: int) -> JevSignal:
    return JevSignal(
        side=None,
        confidence=Decimal("0"),
        expected_move_bp=Decimal("0"),
        book_toxic=False,
        latency_ms=latency_ms,
        cost_quote=Decimal("0"),
    )


def stand_in_signal(*, latency_ms: int = 1) -> JevSignal:
    """Test/dev stand-in. Live without a key MUST NOT send (caller checks jev_api_key)."""
    side = _parse_side(os.getenv("JEV_STAND_IN_SIDE"))
    confidence_raw = (os.getenv("JEV_STAND_IN_CONFIDENCE") or "0").strip()
    try:
        confidence = Decimal(confidence_raw)
    except Exception:
        confidence = Decimal("0")
    move_raw = (os.getenv("JEV_STAND_IN_MOVE_BP") or os.getenv("JEV_STAND_IN_EDGE") or "25").strip()
    try:
        expected_move_bp = Decimal(move_raw)
    except Exception:
        expected_move_bp = Decimal("25")
    toxic = (os.getenv("JEV_STAND_IN_TOXIC") or "").strip().lower() in {"1", "true", "yes", "on"}
    return JevSignal(
        side=side,
        confidence=confidence,
        expected_move_bp=expected_move_bp,
        book_toxic=toxic,
        latency_ms=latency_ms,
        cost_quote=Decimal("0"),
    )


def _systemone_payload(payload: dict[str, Any]) -> dict[str, Any]:
    state = payload.get("state") if isinstance(payload.get("state"), dict) else payload
    return {
        "state": state,
        "model": _JEV_MODEL,
        "questions": {
            "side": {
                "type": "choice",
                "instructions": (
                    "Directional BTCUSDT scalp this cycle: post-only BUY at best bid, "
                    "SELL at best ask, or HOLD (send nothing)."
                ),
                "criteria": {
                    "BUY": "Post-only buy",
                    "SELL": "Post-only sell",
                    "HOLD": "Do not send",
                },
            },
            "expected_move_bp": {
                "type": "number",
                "instructions": (
                    "Expected absolute price move in basis points over the next 900 s "
                    "lookback horizon for the chosen side."
                ),
            },
            "book_toxic": {
                "type": "noul",
                "instructions": "Is the book toxic so we must not post?",
            },
        },
    }


def _noul_yes(answer: Any) -> bool:
    return _decimal(_as_dict(answer).get("noul")) >= Decimal("0.5")


def _side_confidence(side_answer: dict[str, Any]) -> Decimal:
    if side_answer.get("confidence") is not None:
        return _decimal(side_answer.get("confidence"))
    choice = str(side_answer.get("choice") or "").strip()
    probs = _as_dict(side_answer.get("probabilities"))
    if choice and choice in probs:
        return _decimal(probs.get(choice))
    upper = choice.upper()
    if upper and upper in probs:
        return _decimal(probs.get(upper))
    return Decimal("0")


def _expected_move_bp(answers: dict[str, Any]) -> Decimal:
    raw = answers.get("expected_move_bp")
    if isinstance(raw, dict):
        if raw.get("number") is not None:
            return _decimal(raw.get("number"))
        if raw.get("value") is not None:
            return _decimal(raw.get("value"))
    return _decimal(raw)


def _map_systemone(parsed: Any, *, latency_ms: int) -> JevSignal:
    data = _as_dict(parsed)
    answers = _as_dict(data.get("answers"))
    if not answers:
        return _hold_signal(latency_ms)
    side_answer = _as_dict(answers.get("side"))
    return JevSignal(
        side=_parse_side(side_answer.get("choice")),
        confidence=_side_confidence(side_answer),
        expected_move_bp=_expected_move_bp(answers),
        book_toxic=_noul_yes(answers.get("book_toxic")),
        latency_ms=latency_ms,
        cost_quote=Decimal("0"),
    )


def request_jev(payload: dict[str, Any], *, timeout_s: Optional[float] = None) -> JevSignal:
    """One HTTP call. Timeout defaults to the 1.5 s late gate."""
    started = time.perf_counter()
    timeout = float(timeout_s if timeout_s is not None else (JEV_LATE_MS / 1000.0))
    key = jev_api_key()
    if not key:
        if _stand_in_enabled():
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            return stand_in_signal(latency_ms=max(1, elapsed_ms))
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        return _hold_signal(elapsed_ms)

    url = _endpoint_url()
    body = json.dumps(_systemone_payload(payload), separators=(",", ":")).encode("utf-8")
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
        return _hold_signal(elapsed_ms)
    except Exception as exc:
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        logger.warning("Jev request failed latency_ms=%s err=%s", elapsed_ms, _redact(str(exc)))
        return _hold_signal(
            max(elapsed_ms, JEV_LATE_MS + 1 if elapsed_ms >= JEV_LATE_MS else elapsed_ms)
        )

    elapsed_ms = int((time.perf_counter() - started) * 1000)
    try:
        return _map_systemone(parsed, latency_ms=elapsed_ms)
    except Exception:
        return _hold_signal(elapsed_ms)
