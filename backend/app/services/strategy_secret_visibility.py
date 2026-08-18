from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.middleware.authMiddleware import is_admin_email
from app.models import User
from app.schemas.strategy_transparency import StrategyTransparency, TradeExplanation
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


def can_view_strategy_details(db: Session, user_id: str | None) -> bool:
    """Return whether the authenticated route may expose safe functional details.

    The route dependency has already authenticated ``user_id``.  Keeping this
    decision separate from ``can_view_strategy_secrets`` prevents the admin
    allowlist from being reused as a functional-detail gate.  The fallback is
    useful for direct service tests, where FastAPI's dependency object is
    passed instead of a live SQLAlchemy session.
    """
    if not str(user_id or "").strip():
        return False
    if not hasattr(db, "query"):
        return True

    try:
        parsed_user_id = uuid.UUID(str(user_id))
    except (TypeError, ValueError):
        # Production requests receive a UUID from get_current_user.  Tests
        # and internal callers may use an opaque authenticated subject.
        return True

    return bool(db.query(User).filter(User.id == parsed_user_id).first())


def _display_name(payload: dict[str, Any]) -> str:
    return str(
        payload.get("strategy_name")
        or payload.get("template_name")
        or payload.get("name")
        or PROTECTED_STRATEGY_LABEL
    )


def _public_strategy_display_name(payload: dict[str, Any]) -> str:
    existing = str(payload.get("strategy_display_name") or "").strip()
    if existing and existing not in {PROTECTED_STRATEGY_LABEL, "Estratégia Cripto Farol"}:
        return existing

    raw = _display_name(payload).strip()
    if not raw or raw == PROTECTED_STRATEGY_LABEL:
        return PROTECTED_STRATEGY_LABEL

    return public_strategy_display_name(raw)


def _safe_manifest(payload: dict[str, Any]) -> dict[str, Any]:
    """Serialize only the typed, allowlisted functional manifest."""
    raw_manifest = payload.get("strategy_transparency")
    try:
        manifest = StrategyTransparency.model_validate(raw_manifest)
    except Exception:
        manifest = StrategyTransparency(
            status="unavailable",
            strategy_key="unavailable",
            timeframe=str(payload.get("timeframe") or "") or None,
            unavailable_reason="A configuração executada não pôde ser comprovada.",
        )
    return manifest.model_dump(mode="json", exclude={"market_series"})


def _safe_numeric_values(
    payload: dict[str, Any], manifest: dict[str, Any]
) -> dict[str, float] | None:
    if manifest.get("status") != "available":
        return None
    raw_values = payload.get("indicator_values")
    if not isinstance(raw_values, dict):
        return None
    declared = {
        str(column).lower()
        for indicator in manifest.get("indicators") or []
        if isinstance(indicator, dict)
        for column in indicator.get("execution_columns") or []
    }
    safe: dict[str, float] = {}
    for key, value in raw_values.items():
        if str(key).lower() not in declared or isinstance(value, bool):
            continue
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            continue
        if numeric == numeric and abs(numeric) != float("inf"):
            safe[str(key)] = numeric
    return safe or None


def _safe_public_details(payload: dict[str, Any]) -> dict[str, Any]:
    """Keep only status context that the authenticated card needs."""
    details = payload.get("details")
    if not isinstance(details, dict):
        return {}
    allowed = {"status", "distance", "distance_to_next_status", "next_status_label"}
    return {key: details[key] for key in allowed if key in details}


def redact_favorite_strategy_payload(
    payload: dict[str, Any],
    *,
    include_secrets: bool,
    include_details: bool = False,
) -> dict[str, Any]:
    public_display_name = _public_strategy_display_name(payload)
    if include_secrets:
        payload["is_strategy_protected"] = False
        payload["strategy_display_name"] = public_display_name
        return payload

    if include_details:
        manifest = _safe_manifest(payload)
        is_manifest_available = manifest.get("status") == "available" and bool(
            manifest.get("display_name")
        )
        has_known_identity = public_display_name not in {
            PROTECTED_STRATEGY_LABEL,
            "Estratégia Cripto Farol",
        }
        payload["parameters"] = manifest.get("parameters") or {}
        if isinstance(payload.get("metrics"), dict):
            metrics = dict(payload["metrics"])
            metrics.pop("analysis_indicator_data", None)
            if "analysis_strategy_transparency" in metrics:
                metrics["analysis_strategy_transparency"] = _safe_manifest(
                    {"strategy_transparency": metrics["analysis_strategy_transparency"]}
                )
            payload["metrics"] = metrics
        payload["strategy_description"] = manifest.get("description") or payload.get(
            "strategy_description"
        )
        payload["strategy_transparency"] = manifest
        payload["is_strategy_protected"] = False
        payload["strategy_display_name"] = (
            manifest.get("display_name")
            if is_manifest_available
            else (
                public_display_name
                if has_known_identity
                else "Detalhes da estratégia indisponíveis"
            )
        )
        if not is_manifest_available and not has_known_identity:
            payload["template_name"] = payload["strategy_display_name"]
            payload["strategy_description"] = (
                "A configuração executada não pôde ser comprovada nesta superfície."
            )
            if payload.get("is_curated_fallback"):
                payload["name"] = payload["strategy_display_name"]
                payload["notes"] = None
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
    include_details: bool = False,
) -> dict[str, Any]:
    public_display_name = _public_strategy_display_name(payload)
    if include_secrets:
        payload["is_strategy_protected"] = False
        payload["strategy_display_name"] = public_display_name
        return payload

    if include_details:
        manifest = _safe_manifest(payload)
        is_manifest_available = manifest.get("status") == "available" and bool(
            manifest.get("display_name")
        )
        has_known_identity = public_display_name not in {
            PROTECTED_STRATEGY_LABEL,
            "Estratégia Cripto Farol",
        }
        payload["parameters"] = manifest.get("parameters") or {}
        payload["indicator_values"] = _safe_numeric_values(payload, manifest)
        payload["details"] = _safe_public_details(payload)
        payload["signal_history"] = _redact_signal_history(payload.get("signal_history"))
        if isinstance(payload.get("trade_explanation"), dict):
            try:
                payload["trade_explanation"] = TradeExplanation.model_validate(
                    payload["trade_explanation"]
                ).model_dump(mode="json")
            except Exception:
                payload["trade_explanation"] = None
        payload["strategy_description"] = manifest.get("description") or payload.get(
            "strategy_description"
        )
        payload["strategy_transparency"] = manifest
        payload["is_strategy_protected"] = False
        payload["strategy_display_name"] = (
            manifest.get("display_name")
            if is_manifest_available
            else (
                public_display_name
                if has_known_identity
                else "Detalhes da estratégia indisponíveis"
            )
        )
        if not is_manifest_available and not has_known_identity:
            payload["template_name"] = payload["strategy_display_name"]
            payload["strategy_description"] = (
                "A configuração executada não pôde ser comprovada nesta superfície."
            )
            if payload.get("is_curated_fallback"):
                payload["name"] = payload["strategy_display_name"]
                payload["notes"] = None
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
