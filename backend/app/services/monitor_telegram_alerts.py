from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable

import requests
from sqlalchemy.orm import Session

from app.models import MonitorObservedStatus, MonitorTelegramAlert
from app.services.opportunity_service import OpportunityService
from app.services.system_preferences_service import (
    get_system_preference_bool,
    get_system_preference_int,
    get_system_preference_value,
)

MONITOR_TELEGRAM_ALERTS_ENABLED_KEY = "monitor_telegram_alerts_enabled"
MONITOR_TELEGRAM_CHAT_ID_KEY = "monitor_telegram_chat_id"
MONITOR_TELEGRAM_ALLOWED_CHAT_IDS_KEY = "monitor_telegram_allowed_chat_ids"
MONITOR_TELEGRAM_THREAD_ID_KEY = "monitor_telegram_thread_id"
MONITOR_TELEGRAM_MIN_REPEAT_MINUTES_KEY = "monitor_telegram_min_repeat_minutes"
MONITOR_TELEGRAM_RATE_LIMIT_COUNT_KEY = "monitor_telegram_rate_limit_count"
MONITOR_TELEGRAM_RATE_LIMIT_WINDOW_MINUTES_KEY = "monitor_telegram_rate_limit_window_minutes"
MONITOR_TELEGRAM_TIER_FILTER_KEY = "monitor_telegram_tier_filter"

SENDABLE_STATUSES = {
    "BUY_SIGNAL",
    "BUY_NEAR",
    "EXIT_SIGNAL",
    "EXIT_NEAR",
    "HOLDING",
    "STOPPED_OUT",
}


@dataclass(frozen=True)
class MonitorTelegramAlertSettings:
    enabled: bool
    bot_token: str | None
    chat_id: str | None
    allowed_chat_ids: set[str]
    thread_id: str | None
    min_repeat_minutes: int
    rate_limit_count: int
    rate_limit_window_minutes: int
    tier_filter: str

    @property
    def destination_allowed(self) -> bool:
        return bool(self.chat_id and self.chat_id in self.allowed_chat_ids)

    @property
    def can_send(self) -> bool:
        return bool(self.enabled and self.bot_token and self.destination_allowed)


@dataclass(frozen=True)
class MonitorAlertCandidate:
    symbol: str
    timeframe: str
    previous_status: str | None
    new_status: str
    severity: str
    message: str
    payload: dict[str, Any]
    payload_hash: str


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except (TypeError, ValueError):
        return default


def _split_csv(value: str | None) -> set[str]:
    return {item.strip() for item in str(value or "").split(",") if item.strip()}


def _status_label(status: str | None) -> str:
    labels = {
        "BUY_SIGNAL": "Compra",
        "BUY_NEAR": "Compra proxima",
        "EXIT_SIGNAL": "Venda",
        "EXIT_NEAR": "Venda proxima",
        "HOLDING": "Acompanhamento",
        "STOPPED_OUT": "Risco aumentado",
    }
    return labels.get(str(status or "").strip().upper(), str(status or "Novo").strip())


def _action_label(status: str | None) -> str:
    normalized = str(status or "").strip().upper()
    if normalized in {"BUY_SIGNAL", "BUY_NEAR"}:
        return "Compra"
    if normalized in {"EXIT_SIGNAL", "EXIT_NEAR", "STOPPED_OUT"}:
        return "Venda"
    return _status_label(status)


def _format_alert_value(value: Any) -> str:
    if value is None or value == "":
        return "N/D"
    if isinstance(value, (int, float)):
        return f"{float(value):,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    try:
        return f"{float(value):,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    except (TypeError, ValueError):
        return str(value)


def _alert_date(opportunity: dict[str, Any]) -> str:
    raw = opportunity.get("timestamp") or opportunity.get("indicator_values_candle_time")
    if not raw:
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    try:
        parsed = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        return parsed.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return str(raw)


def _entry_value(opportunity: dict[str, Any]) -> Any:
    return (
        opportunity.get("entry_price")
        or opportunity.get("trigger_price")
        or opportunity.get("last_price")
        or opportunity.get("current_price")
    )


def _severity_for_status(status: str) -> str:
    normalized = str(status or "").strip().upper()
    if normalized in {"EXIT_SIGNAL", "STOPPED_OUT"}:
        return "Acao necessaria"
    if normalized in {"BUY_SIGNAL", "EXIT_NEAR"}:
        return "Atencao"
    return "Informativo"


def _sendable_status(status: str | None) -> bool:
    return str(status or "").strip().upper() in SENDABLE_STATUSES


def _json_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def load_monitor_telegram_alert_settings(db: Session) -> MonitorTelegramAlertSettings:
    enabled = get_system_preference_bool(
        db,
        MONITOR_TELEGRAM_ALERTS_ENABLED_KEY,
        _env_bool("MONITOR_TELEGRAM_ALERTS_ENABLED", default=False),
    )
    chat_id = (
        get_system_preference_value(db, MONITOR_TELEGRAM_CHAT_ID_KEY)
        or os.getenv("MONITOR_TELEGRAM_CHAT_ID")
        or ""
    ).strip()
    allowed = _split_csv(
        get_system_preference_value(db, MONITOR_TELEGRAM_ALLOWED_CHAT_IDS_KEY)
        or os.getenv("MONITOR_TELEGRAM_ALLOWED_CHAT_IDS")
    )
    thread_id = (
        get_system_preference_value(db, MONITOR_TELEGRAM_THREAD_ID_KEY)
        or os.getenv("MONITOR_TELEGRAM_THREAD_ID")
        or ""
    ).strip()
    tier_filter = (
        get_system_preference_value(db, MONITOR_TELEGRAM_TIER_FILTER_KEY)
        or os.getenv("MONITOR_TELEGRAM_TIER_FILTER")
        or "all"
    ).strip()

    return MonitorTelegramAlertSettings(
        enabled=enabled,
        bot_token=(os.getenv("MONITOR_TELEGRAM_BOT_TOKEN") or "").strip() or None,
        chat_id=chat_id or None,
        allowed_chat_ids=allowed,
        thread_id=thread_id or None,
        min_repeat_minutes=get_system_preference_int(
            db,
            MONITOR_TELEGRAM_MIN_REPEAT_MINUTES_KEY,
            _env_int("MONITOR_TELEGRAM_MIN_REPEAT_MINUTES", 360),
        ),
        rate_limit_count=get_system_preference_int(
            db,
            MONITOR_TELEGRAM_RATE_LIMIT_COUNT_KEY,
            _env_int("MONITOR_TELEGRAM_RATE_LIMIT_COUNT", 5),
        ),
        rate_limit_window_minutes=get_system_preference_int(
            db,
            MONITOR_TELEGRAM_RATE_LIMIT_WINDOW_MINUTES_KEY,
            _env_int("MONITOR_TELEGRAM_RATE_LIMIT_WINDOW_MINUTES", 60),
        ),
        tier_filter=tier_filter or "all",
    )


def _observed_status_for_pair(
    db: Session, *, symbol: str, timeframe: str
) -> MonitorObservedStatus | None:
    return (
        db.query(MonitorObservedStatus)
        .filter(
            MonitorObservedStatus.symbol == symbol,
            MonitorObservedStatus.timeframe == timeframe,
        )
        .first()
    )


def _upsert_observed_status(
    db: Session, *, opportunity: dict[str, Any], status: str
) -> MonitorObservedStatus:
    symbol = str(opportunity.get("symbol") or "").strip().upper()
    timeframe = str(opportunity.get("timeframe") or "").strip().lower()
    row = _observed_status_for_pair(db, symbol=symbol, timeframe=timeframe)
    payload = {
        "status": status,
        "opportunity_id": opportunity.get("id"),
        "entry_price": _entry_value(opportunity),
        "stop_price": opportunity.get("stop_price") or opportunity.get("stop_loss"),
        "timestamp": opportunity.get("timestamp"),
    }
    if row is None:
        row = MonitorObservedStatus(
            symbol=symbol,
            timeframe=timeframe,
            status=status,
            opportunity_id=(
                str(opportunity.get("id")) if opportunity.get("id") is not None else None
            ),
            payload_json=payload,
        )
        db.add(row)
    else:
        row.status = status
        row.observed_at = datetime.utcnow()
        row.opportunity_id = (
            str(opportunity.get("id")) if opportunity.get("id") is not None else None
        )
        row.payload_json = payload
    db.commit()
    db.refresh(row)
    return row


def _has_duplicate_recent(
    db: Session,
    *,
    symbol: str,
    timeframe: str,
    status: str,
    since: datetime,
) -> bool:
    return (
        db.query(MonitorTelegramAlert)
        .filter(
            MonitorTelegramAlert.symbol == symbol,
            MonitorTelegramAlert.timeframe == timeframe,
            MonitorTelegramAlert.new_status == status,
            MonitorTelegramAlert.created_at >= since,
            MonitorTelegramAlert.result_status.in_(("sent", "dry_run")),
        )
        .first()
        is not None
    )


def _sent_count_since(db: Session, *, since: datetime) -> int:
    return (
        db.query(MonitorTelegramAlert)
        .filter(
            MonitorTelegramAlert.created_at >= since,
            MonitorTelegramAlert.result_status.in_(("sent", "dry_run")),
        )
        .count()
    )


def build_monitor_alert_candidate(
    opportunity: dict[str, Any],
    *,
    previous_status: str | None,
) -> MonitorAlertCandidate | None:
    status = str(opportunity.get("status") or "").strip().upper()
    if not _sendable_status(status):
        return None

    symbol = str(opportunity.get("symbol") or "").strip().upper()
    timeframe = str(opportunity.get("timeframe") or "").strip().lower()
    if not symbol or not timeframe:
        return None

    severity = _severity_for_status(status)
    action = _action_label(status)
    entry_value = _entry_value(opportunity)
    stop_value = opportunity.get("stop_price") or opportunity.get("stop_loss")
    alert_date = _alert_date(opportunity)
    message = (
        "Cripto Farol - Alerta Monitor\n\n"
        f"Ativo: {symbol}\n"
        f"TimeFrame: {timeframe}\n"
        f"Acao: {action}\n"
        f"Data: {alert_date}\n"
        f"Valor Entrada: {_format_alert_value(entry_value)}\n"
        f"Stop: {_format_alert_value(stop_value)}"
    )
    payload = {
        "symbol": symbol,
        "timeframe": timeframe,
        "previous_status": previous_status,
        "new_status": status,
        "action": action,
        "entry_price": entry_value,
        "stop_price": stop_value,
        "alert_date": alert_date,
        "severity": severity,
        "message": message,
        "source": "monitor",
        "opportunity_id": opportunity.get("id"),
        "next_status_label": opportunity.get("next_status_label"),
        "distance_to_next_status": opportunity.get("distance_to_next_status"),
    }
    return MonitorAlertCandidate(
        symbol=symbol,
        timeframe=timeframe,
        previous_status=previous_status,
        new_status=status,
        severity=severity,
        message=message,
        payload=payload,
        payload_hash=_json_hash(payload),
    )


def send_telegram_message(settings: MonitorTelegramAlertSettings, text: str) -> dict[str, Any]:
    if not settings.can_send:
        return {"ok": True, "dry_run": True}

    request_payload: dict[str, Any] = {
        "chat_id": settings.chat_id,
        "text": text,
        "disable_web_page_preview": True,
    }
    if settings.thread_id:
        request_payload["message_thread_id"] = settings.thread_id

    response = requests.post(
        f"https://api.telegram.org/bot{settings.bot_token}/sendMessage",
        json=request_payload,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def _record_alert(
    db: Session,
    candidate: MonitorAlertCandidate,
    *,
    settings: MonitorTelegramAlertSettings,
    result_status: str,
    error_text: str | None = None,
) -> MonitorTelegramAlert:
    row = MonitorTelegramAlert(
        symbol=candidate.symbol,
        timeframe=candidate.timeframe,
        previous_status=candidate.previous_status,
        new_status=candidate.new_status,
        severity=candidate.severity,
        destination_chat_id=settings.chat_id,
        destination_thread_id=settings.thread_id,
        result_status=result_status,
        error_text=error_text,
        payload_hash=candidate.payload_hash,
        source="monitor",
        payload_json=candidate.payload,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def run_monitor_telegram_alert_scan(
    db: Session,
    *,
    user_id: str,
    settings: MonitorTelegramAlertSettings | None = None,
    opportunity_service: OpportunityService | None = None,
    sender: Callable[[MonitorTelegramAlertSettings, str], dict[str, Any]] = send_telegram_message,
    force_dry_run: bool = False,
) -> dict[str, Any]:
    settings = settings or load_monitor_telegram_alert_settings(db)
    service = opportunity_service or OpportunityService()
    summary = {
        "enabled": settings.enabled,
        "dry_run": force_dry_run or not settings.can_send,
        "candidates": 0,
        "sent": 0,
        "dry_run_count": 0,
        "duplicates": 0,
        "rate_limited": 0,
        "skipped": 0,
        "failed": 0,
        "destination_allowed": settings.destination_allowed,
        "results": [],
    }

    if not settings.enabled and not force_dry_run:
        summary["skipped"] += 1
        summary["results"].append({"status": "disabled"})
        return summary

    opportunities = service.get_catalog_opportunities(
        tier_filter=settings.tier_filter,
        alerts_only=True,
    )
    duplicate_since = datetime.utcnow() - timedelta(minutes=max(settings.min_repeat_minutes, 1))
    rate_limit_since = datetime.utcnow() - timedelta(
        minutes=max(settings.rate_limit_window_minutes, 1)
    )

    for opportunity in opportunities:
        symbol = str(opportunity.get("symbol") or "").strip().upper()
        timeframe = str(opportunity.get("timeframe") or "").strip().lower()
        status = str(opportunity.get("status") or "").strip().upper()
        observed = _observed_status_for_pair(db, symbol=symbol, timeframe=timeframe)
        previous_status = observed.status if observed else None
        unchanged = bool(previous_status and previous_status == status)
        candidate = build_monitor_alert_candidate(opportunity, previous_status=previous_status)
        if symbol and timeframe and status:
            _upsert_observed_status(db, opportunity=opportunity, status=status)
        if unchanged:
            summary["skipped"] += 1
            summary["results"].append(
                {
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "status": status,
                    "result": "unchanged",
                }
            )
            continue
        if candidate is None:
            summary["skipped"] += 1
            continue

        summary["candidates"] += 1
        if _has_duplicate_recent(
            db,
            symbol=candidate.symbol,
            timeframe=candidate.timeframe,
            status=candidate.new_status,
            since=duplicate_since,
        ):
            summary["duplicates"] += 1
            summary["results"].append(
                {
                    "symbol": candidate.symbol,
                    "timeframe": candidate.timeframe,
                    "status": candidate.new_status,
                    "result": "duplicate",
                }
            )
            continue

        if _sent_count_since(db, since=rate_limit_since) >= max(settings.rate_limit_count, 0):
            summary["rate_limited"] += 1
            summary["results"].append(
                {
                    "symbol": candidate.symbol,
                    "timeframe": candidate.timeframe,
                    "status": candidate.new_status,
                    "result": "rate_limited",
                }
            )
            continue

        try:
            if force_dry_run or not settings.can_send:
                _record_alert(db, candidate, settings=settings, result_status="dry_run")
                summary["dry_run_count"] += 1
                result_status = "dry_run"
            else:
                sender(settings, candidate.message)
                _record_alert(db, candidate, settings=settings, result_status="sent")
                summary["sent"] += 1
                result_status = "sent"
        except Exception as exc:
            _record_alert(
                db,
                candidate,
                settings=settings,
                result_status="failed",
                error_text=str(exc),
            )
            summary["failed"] += 1
            result_status = "failed"

        summary["results"].append(
            {
                "symbol": candidate.symbol,
                "timeframe": candidate.timeframe,
                "status": candidate.new_status,
                "result": result_status,
            }
        )

    return summary
