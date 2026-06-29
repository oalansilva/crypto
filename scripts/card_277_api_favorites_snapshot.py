#!/usr/bin/env python3
"""Capture served Favorites API T0 readback for issue #277 without printing tokens."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import jwt
import requests

from app.database import SessionLocal
from app.middleware.authMiddleware import ADMIN_EMAILS
from app.models import User


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "qa_artifacts" / "card-277-hard-mode-v5-btc-long"


def _direction(parameters: Any) -> str:
    if isinstance(parameters, dict):
        return str(parameters.get("direction") or "long").lower()
    return "long"


def _admin_user() -> User:
    emails = sorted(ADMIN_EMAILS)
    with SessionLocal() as session:
        user = session.query(User).filter(User.email.in_(emails)).order_by(User.email.asc()).first()
        if not user:
            raise SystemExit("No admin user found for configured ADMIN_EMAILS")
        session.expunge(user)
        return user


def _access_token(user: User) -> str:
    secret = os.getenv("JWT_SECRET", "dev-secret-change-in-production")
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id),
        "user_id": str(user.id),
        "email": user.email,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=15),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", default="http://127.0.0.1:8003")
    parser.add_argument("--symbol", default="BTC/USDT")
    parser.add_argument("--timeframe", default="1d")
    parser.add_argument("--direction", choices=["long", "short"], default="long")
    args = parser.parse_args()

    user = _admin_user()
    response = requests.get(
        f"{args.api.rstrip('/')}/api/favorites/",
        headers={"Authorization": f"Bearer {_access_token(user)}"},
        timeout=30,
    )
    payload: dict[str, Any] = {
        "card": 277,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "api": args.api,
        "status_code": response.status_code,
        "symbol": args.symbol,
        "timeframe": args.timeframe,
        "direction": args.direction,
    }
    if response.ok:
        rows = response.json()
        payload["favorites"] = [
            row
            for row in rows
            if row.get("symbol") == args.symbol
            and row.get("timeframe") == args.timeframe
            and _direction(row.get("parameters")) == args.direction
        ]
    else:
        payload["error"] = response.text[:1000]

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = payload["captured_at"].replace(":", "").replace("+", "Z")
    output = ARTIFACT_DIR / f"api-favorites-t0-{stamp}.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    latest = ARTIFACT_DIR / "api-favorites-t0-latest.json"
    latest.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    print(output)
    print(
        json.dumps(
            {
                "status_code": payload["status_code"],
                "favorites": len(payload.get("favorites") or []),
                "output": str(output),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0 if response.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
