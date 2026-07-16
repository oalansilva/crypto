from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.middleware.authMiddleware import is_admin_email
from app.models import User
from app.schemas.strategy_transparency import TradeExplanation
from app.services.strategy_descriptions import public_strategy_display_name

PROTECTED_STRATEGY_LABEL = "Estratégia protegida"
PROTECTED_STRATEGY_CODE = "estrategia_protegida"


def can_view_strategy_secrets(db: Session, user_id: str | None) -> bool:
    """Return True only for users in the configured admin email allowlist."""
    if not user_id:
        return False
    if not hasattr(db, "query"):
        return False

    try:
        parsed_user_id = uuid.UUID(str(user_id))
    except (TypeError, ValueError):
        return False

    user = db.query(User).filter(User.id == parsed_user_id).first()
    return bool(user and is_admin_email(user.email))


def _display_name(payload: dict[str, Any]) -> str:
    return str(
        payload.get("strategy_name")
        or payload.get("template_name")
        or payload.get("name")
        or PROTECTED_STRATEGY_LABEL
    )


def _public_strategy_display_name(payload: dict[str, Any]) -> str:
    raw = _display_name(payload).strip()
    if not raw or raw == PROTECTED_STRATEGY_LABEL:
        return PROTECTED_STRATEGY_LABEL

    return public_strategy_display_name(raw)


def redact_favorite_strategy_payload(
    payload: dict[str, Any],
    *,
    include_secrets: bool,
) -> dict[str, Any]:
    public_display_name = _public_strategy_display_name(payload)
    if include_secrets:
        payload["is_strategy_protected"] = False
        payload["strategy_display_name"] = public_display_name
        return payload

    payload["strategy_name"] = PROTECTED_STRATEGY_LABEL
    payload["parameters"] = {}
    payload["is_strategy_protected"] = True
    payload["strategy_display_name"] = public_display_name
    return payload


def _protected_message(payload: dict[str, Any]) -> str:
    raw_status = str(payload.get("status") or "").strip().upper()
    is_holding = bool(payload.get("is_holding"))

    if raw_status == "EXIT":
        return "Saida registrada. Acompanhe o sistema para a proxima janela."
    if raw_status == "HOLD" or is_holding:
        return "Posicao ativa. Acompanhe o sistema para a proxima decisao."
    return "Saida registrada. Acompanhe o sistema para a proxima janela."


def _redact_signal_history(history: Any) -> list[dict[str, Any]] | None:
    if not isinstance(history, list):
        return history

    redacted: list[dict[str, Any]] = []
    for item in history:
        if not isinstance(item, dict):
            continue
        signal_type = str(item.get("type") or "").strip().lower()
        public_item = {
            "timestamp": item.get("timestamp"),
            "signal": item.get("signal"),
            "type": signal_type if signal_type in {"entry", "exit"} else item.get("type"),
            "reason": "entry" if signal_type == "entry" else "exit",
            "price": item.get("price"),
        }
        if isinstance(item.get("explanation"), dict):
            try:
                public_item["explanation"] = TradeExplanation.model_validate(
                    item["explanation"]
                ).model_dump(mode="json")
            except Exception:
                pass
        redacted.append(public_item)
    return redacted


def redact_opportunity_payload(
    payload: dict[str, Any],
    *,
    include_secrets: bool,
) -> dict[str, Any]:
    public_display_name = _public_strategy_display_name(payload)
    if include_secrets:
        payload["is_strategy_protected"] = False
        payload["strategy_display_name"] = public_display_name
        return payload

    payload["template_name"] = PROTECTED_STRATEGY_LABEL
    if payload.get("is_curated_fallback"):
        payload["name"] = PROTECTED_STRATEGY_LABEL
        payload["notes"] = None
    payload["parameters"] = {}
    payload["indicator_values"] = None
    payload["details"] = {}
    payload["message"] = _protected_message(payload)
    payload["signal_history"] = _redact_signal_history(payload.get("signal_history"))
    if isinstance(payload.get("trade_explanation"), dict):
        try:
            payload["trade_explanation"] = TradeExplanation.model_validate(
                payload["trade_explanation"]
            ).model_dump(mode="json")
        except Exception:
            payload["trade_explanation"] = None
    payload["is_strategy_protected"] = True
    payload["strategy_display_name"] = public_display_name
    return payload
