"""Fail-closed JWT_SECRET resolution. No repository default."""

from __future__ import annotations

import os

KNOWN_DEFAULT_JWT_SECRET = "dev-secret-change-in-production"
MIN_JWT_SECRET_LENGTH = 32
_INVALID_JWT_SECRET = "JWT_SECRET is invalid"


def resolve_jwt_secret() -> str:
    raw = os.getenv("JWT_SECRET")
    if raw is None:
        raise RuntimeError(_INVALID_JWT_SECRET)
    secret = raw.strip()
    if not secret:
        raise RuntimeError(_INVALID_JWT_SECRET)
    if secret == KNOWN_DEFAULT_JWT_SECRET:
        raise RuntimeError(_INVALID_JWT_SECRET)
    if len(secret) < MIN_JWT_SECRET_LENGTH:
        raise RuntimeError(_INVALID_JWT_SECRET)
    return secret
