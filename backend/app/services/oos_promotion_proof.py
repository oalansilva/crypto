from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt


def _canonicalize(value: Any) -> Any:
    if isinstance(value, float) and value.is_integer():
        return int(value)
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
        os.getenv("JWT_SECRET", "dev-secret-change-in-production"),
        algorithm="HS256",
    )


def verify_oos_promotion_proof(proof: str, payload: dict[str, Any]) -> bool:
    try:
        claims = jwt.decode(
            proof,
            os.getenv("JWT_SECRET", "dev-secret-change-in-production"),
            algorithms=["HS256"],
        )
    except jwt.PyJWTError:
        return False
    return claims.get("purpose") == "oos-favorite-promotion" and claims.get(
        "digest"
    ) == _canonical_digest(payload)
