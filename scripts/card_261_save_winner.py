#!/usr/bin/env python3
"""Persist the validated issue #261 winner template and Favorite."""

from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import jwt
import requests
from sqlalchemy import create_engine, text

from app.middleware.authMiddleware import ADMIN_EMAILS, JWT_SECRET


ROOT = Path(__file__).resolve().parents[1]
VALIDATION_PATH = ROOT / "qa_artifacts" / "card-261-hard-mode-v3-btc-pareto" / "winner_validation_20260607T014201Z.json"
ARTIFACT_DIR = ROOT / "qa_artifacts" / "card-261-hard-mode-v3-btc-pareto"
API_BASE = os.getenv("CARD_261_API_BASE", "http://127.0.0.1:8003")


def _admin_token(engine) -> tuple[str, str]:
    admin_emails = sorted(ADMIN_EMAILS)
    if not admin_emails:
        raise RuntimeError("ADMIN_EMAILS is empty")
    with engine.connect() as conn:
        user = conn.execute(
            text(
                """
                SELECT id, email
                FROM users
                WHERE lower(email) = ANY(:emails)
                ORDER BY email
                LIMIT 1
                """
            ),
            {"emails": admin_emails},
        ).mappings().first()
    if not user:
        raise RuntimeError("No admin user found for configured ADMIN_EMAILS")
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user["id"]),
        "email": str(user["email"]).lower(),
        "type": "access",
        "exp": now + timedelta(minutes=15),
        "iat": now,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256"), str(user["id"])


def _ensure_template(engine, validation: dict[str, Any]) -> str:
    candidate = validation["final_candidate"]
    name = candidate["strategy_name"]
    template_data = candidate["template_data"]
    optimization_schema = {
        "parameters": {
            "ema": {"min": 30, "max": 34, "default": 32, "step": 1},
            "roc": {"min": 8, "max": 10, "default": 9, "step": 1},
            "rsi": {"min": 10, "max": 10, "default": 10, "step": 1},
            "rsi_min": {"min": 38, "max": 42, "default": 40, "step": 1},
            "rsi_exit": {"min": 45, "max": 45, "default": 45, "step": 1},
            "stop_loss": {"min": 0.026, "max": 0.03, "default": 0.028, "step": 0.001},
        },
        "correlated_groups": [["ema", "roc", "rsi", "rsi_min", "rsi_exit", "stop_loss"]],
    }
    with engine.begin() as conn:
        existing = conn.execute(
            text("SELECT id FROM combo_templates WHERE name = :name"),
            {"name": name},
        ).mappings().first()
        if existing:
            return "existing"
        conn.execute(
            text(
                """
                INSERT INTO combo_templates
                    (name, description, is_prebuilt, is_example, is_readonly, template_data, optimization_schema, created_at, updated_at)
                VALUES
                    (:name, :description, false, false, false, :template_data, :optimization_schema, now(), now())
                """
            ),
            {
                "name": name,
                "description": candidate["strategy_description"],
                "template_data": json.dumps(template_data, ensure_ascii=False),
                "optimization_schema": json.dumps(optimization_schema, ensure_ascii=False),
            },
        )
    return "created"


def _favorite_exists(engine, strategy_name: str) -> dict[str, Any] | None:
    with engine.connect() as conn:
        return conn.execute(
            text(
                """
                SELECT id, name, strategy_name, created_at, metrics
                FROM favorite_strategies
                WHERE symbol = 'BTC/USDT'
                  AND timeframe = '1d'
                  AND strategy_name = :strategy_name
                ORDER BY id DESC
                LIMIT 1
                """
            ),
            {"strategy_name": strategy_name},
        ).mappings().first()


def main() -> None:
    validation = json.loads(VALIDATION_PATH.read_text(encoding="utf-8"))
    payload = validation["favorite_payload"]
    strategy_name = payload["strategy_name"]
    engine = create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)
    existing = _favorite_exists(engine, strategy_name)
    template_status = _ensure_template(engine, validation)
    token, user_id = _admin_token(engine)
    if existing:
        result = {
            "template_status": template_status,
            "favorite_status": "existing",
            "favorite": {k: str(existing[k]) for k in existing.keys() if k != "metrics"},
        }
    else:
        response = requests.post(
            f"{API_BASE}/api/favorites/",
            headers={"Authorization": f"Bearer {token}"},
            json=payload,
            timeout=60,
        )
        if not response.ok:
            raise RuntimeError(f"Favorite save failed: status={response.status_code} body={response.text[:500]}")
        result = {
            "template_status": template_status,
            "favorite_status": "created",
            "favorite": response.json(),
        }
    result["saved_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    result["admin_user_id"] = user_id
    output = ARTIFACT_DIR / "winner_save_result_20260607T014201Z.json"
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    favorite = result["favorite"]
    print(
        json.dumps(
            {
                "output": str(output.relative_to(ROOT)),
                "template_status": result["template_status"],
                "favorite_status": result["favorite_status"],
                "favorite_id": favorite.get("id"),
                "name": favorite.get("name"),
                "strategy_name": favorite.get("strategy_name"),
                "strategy_display_name": favorite.get("strategy_display_name"),
                "strategy_description": favorite.get("strategy_description"),
                "created_at": favorite.get("created_at"),
            },
            ensure_ascii=False,
            default=str,
        )
    )


if __name__ == "__main__":
    main()
