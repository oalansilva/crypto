from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from app.jwt_secret import resolve_jwt_secret

JWT_SECRET = resolve_jwt_secret()

_JS_MAX_SAFE_INTEGER = (1 << 53) - 1


def _canonicalize(value: Any) -> Any:
    if isinstance(value, bool):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("OOS promotion proof payload contains a non-finite number")
        if value.is_integer() and abs(value) <= _JS_MAX_SAFE_INTEGER:
            return int(value)
        return value
    if isinstance(value, int):
        if abs(value) <= _JS_MAX_SAFE_INTEGER:
            return value
        try:
            canonical = float(value)
        except OverflowError as exc:
            raise ValueError(
                "OOS promotion proof payload integer exceeds finite IEEE-754 range"
            ) from exc
        if not math.isfinite(canonical):
            raise ValueError("OOS promotion proof payload integer exceeds finite IEEE-754 range")
        return canonical
    if isinstance(value, dict):
        return {key: _canonicalize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_canonicalize(item) for item in value]
    return value


def _canonical_digest(payload: dict[str, Any]) -> str:
    canonical = _canonicalize(payload)
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(encoded).hexdigest()


def promotion_payload(
    *,
    template_name: str,
    symbol: str,
    timeframe: str,
    start_date: str | None,
    end_date: str | None,
    period_type: str | None,
    parameters: dict[str, Any],
    metrics: dict[str, Any],
    oos_metrics: dict[str, Any],
    oos_verdict: dict[str, Any],
) -> dict[str, Any]:
    return {
        "template_name": template_name,
        "symbol": symbol,
        "timeframe": timeframe,
        "start_date": start_date,
        "end_date": end_date,
        "period_type": period_type,
        "parameters": parameters,
        "metrics": metrics,
        "oos_metrics": oos_metrics,
        "oos_verdict": oos_verdict,
    }


def issue_oos_promotion_proof(payload: dict[str, Any]) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "purpose": "oos-favorite-promotion",
            "digest": _canonical_digest(payload),
            "iat": now,
            "exp": now + timedelta(hours=6),
        },
        JWT_SECRET,
        algorithm="HS256",
    )


def verify_oos_promotion_proof(proof: str, payload: dict[str, Any]) -> bool:
    try:
        claims = jwt.decode(
            proof,
            JWT_SECRET,
            algorithms=["HS256"],
        )
        digest = _canonical_digest(payload)
    except (jwt.PyJWTError, ValueError):
        return False
    return claims.get("purpose") == "oos-favorite-promotion" and claims.get("digest") == digest
