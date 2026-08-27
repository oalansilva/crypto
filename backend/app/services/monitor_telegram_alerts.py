from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable

import requests
from sqlalchemy.orm import Session

from app.models import MonitorObservedStatus, MonitorTelegramAlert, User
from app.services.monitor_portfolio_status import (
    fetch_user_wallet_holdings,
    resolve_portfolio_status_for_user,
)
from app.services.opportunity_service import OpportunityService
from app.services.system_preferences_service import (
    get_system_preference_bool,
    get_system_preference_int,
    get_system_preference_value,
)
from app.services.user_telegram_service import list_eligible_alert_users

MONITOR_TELEGRAM_ALERTS_ENABLED_KEY = "monitor_telegram_alerts_enabled"
MONITOR_TELEGRAM_MIN_REPEAT_MINUTES_KEY = "monitor_telegram_min_repeat_minutes"
MONITOR_TELEGRAM_RATE_LIMIT_COUNT_KEY = "monitor_telegram_rate_limit_count"
MONITOR_TELEGRAM_RATE_LIMIT_WINDOW_MINUTES_KEY = "monitor_telegram_rate_limit_window_minutes"
MONITOR_TELEGRAM_TIER_FILTER_KEY = "monitor_telegram_tier_filter"

SENDABLE_STATUSES = {"HOLD", "EXIT"}
EDUCATIONAL_DISCLAIMER = (
    "\n\nAviso: ferramenta educacional de apoio à decisão. "
    "Não constitui recomendação financeira nem ordem de compra/venda."
)


@dataclass(frozen=True)
class MonitorTelegramAlertSettings:
    enabled: bool
    bot_token: str | None
    min_repeat_minutes: int
    rate_limit_count: int
    rate_limit_window_minutes: int
    tier_filter: str

    @property
    def can_send(self) -> bool:
        return bool(self.enabled and self.bot_token)


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
    stop_reason: bool = False


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


def _action_label(status: str | None) -> str:
    normalized = str(status or "").strip().upper()
    if normalized in {"HOLD", "BUY_SIGNAL", "BUY_NEAR"}:
        return "Compra"
    if normalized in {"EXIT", "EXIT_SIGNAL", "EXIT_NEAR", "STOPPED_OUT"}:
        return "Venda"
    return normalized or "N/D"


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
    if normalized in {"EXIT", "EXIT_SIGNAL", "STOPPED_OUT"}:
        return "Acao necessaria"
    if normalized in {"HOLD", "BUY_SIGNAL", "EXIT_NEAR"}:
        return "Atencao"
    return "Informativo"


def _sendable_status(status: str | None) -> bool:
    return str(status or "").strip().upper() in SENDABLE_STATUSES


def _json_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _is_stop_reason(opportunity: dict[str, Any]) -> bool:
    raw = str(opportunity.get("raw_analysis_status") or "").strip().upper()
    return bool(opportunity.get("stop_breached_now")) or raw == "STOPPED_OUT"


def should_send_position_aware_alert(
    *,
    previous_status: str | None,
    new_status: str,
    has_spot_position: bool,
    in_portfolio: bool,
) -> tuple[bool, str]:
    if not in_portfolio:
        return False, "outside_portfolio_scope"
    prev = str(previous_status or "").strip().upper()
    new = str(new_status or "").strip().upper()
    if prev == new:
        return False, "unchanged"
    if has_spot_position:
        if prev == "HOLD" and new == "EXIT":
            return True, "sell"
        if prev == "EXIT" and new == "HOLD":
            return False, "suppressed_reentry"
    else:
        if prev == "EXIT" and new == "HOLD":
            return True, "buy"
        if prev == "HOLD" and new == "EXIT":
            return False, "suppressed_flat_exit"
    return False, "suppressed_by_position_matrix"


def load_monitor_telegram_alert_settings(db: Session) -> MonitorTelegramAlertSettings:
    enabled = get_system_preference_bool(
        db,
        MONITOR_TELEGRAM_ALERTS_ENABLED_KEY,
        _env_bool("MONITOR_TELEGRAM_ALERTS_ENABLED", default=False),
    )
    tier_filter = (
        get_system_preference_value(db, MONITOR_TELEGRAM_TIER_FILTER_KEY)
        or os.getenv("MONITOR_TELEGRAM_TIER_FILTER")
        or "all"
    ).strip()

    return MonitorTelegramAlertSettings(
        enabled=enabled,
        bot_token=(os.getenv("MONITOR_TELEGRAM_BOT_TOKEN") or "").strip() or None,
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
    user_id: str,
    symbol: str,
    timeframe: str,
    status: str,
    since: datetime,
) -> bool:
    return (
        db.query(MonitorTelegramAlert)
        .filter(
            MonitorTelegramAlert.user_id == user_id,
            MonitorTelegramAlert.symbol == symbol,
            MonitorTelegramAlert.timeframe == timeframe,
            MonitorTelegramAlert.new_status == status,
            MonitorTelegramAlert.created_at >= since,
            MonitorTelegramAlert.result_status.in_(("sent", "dry_run")),
        )
        .first()
        is not None
    )


def _sent_count_since(db: Session, *, user_id: str, since: datetime) -> int:
    return (
        db.query(MonitorTelegramAlert)
        .filter(
            MonitorTelegramAlert.user_id == user_id,
            MonitorTelegramAlert.created_at >= since,
            MonitorTelegramAlert.result_status.in_(("sent", "dry_run")),
            MonitorTelegramAlert.source == "monitor",
        )
        .count()
    )


def _operational_sent_recently(
    db: Session,
    *,
    user_id: str,
    since: datetime,
) -> bool:
    return (
        db.query(MonitorTelegramAlert)
        .filter(
            MonitorTelegramAlert.user_id == user_id,
            MonitorTelegramAlert.source == "operational",
            MonitorTelegramAlert.created_at >= since,
            MonitorTelegramAlert.result_status.in_(("sent", "dry_run")),
        )
        .first()
        is not None
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

    stop_reason = _is_stop_reason(opportunity)
    severity = _severity_for_status(status)
    action = _action_label(status)
    entry_value = _entry_value(opportunity)
    stop_value = opportunity.get("stop_price") or opportunity.get("stop_loss")
    alert_date = _alert_date(opportunity)
    strategy_name = (
        opportunity.get("strategy_display_name")
        or opportunity.get("name")
        or opportunity.get("template_name")
        or "Estrategia"
    )
    prev_label = _action_label(previous_status)
    message = (
        "Cripto Farol - Alerta Monitor\n\n"
        f"Ativo: {symbol}\n"
        f"Estrategia: {strategy_name}\n"
        f"TimeFrame: {timeframe}\n"
        f"Leitura anterior: {prev_label}\n"
        f"Leitura atual: {action}\n"
        f"Data: {alert_date}\n"
        f"Valor Entrada: {_format_alert_value(entry_value)}\n"
        f"Stop: {_format_alert_value(stop_value)}"
    )
    if stop_reason:
        message += "\nMotivo=Stop"
    message += EDUCATIONAL_DISCLAIMER

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
        "stop_reason": stop_reason,
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
        stop_reason=stop_reason,
    )


def send_telegram_message(
    *,
    bot_token: str | None,
    chat_id: str,
    text: str,
    dry_run: bool = False,
) -> dict[str, Any]:
    if dry_run or not bot_token:
        return {"ok": True, "dry_run": True}

    response = requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": True,
        },
        timeout=10,
    )
    response.raise_for_status()
    return response.json()


def _record_alert(
    db: Session,
    candidate: MonitorAlertCandidate | None,
    *,
    user_id: str,
    chat_id: str,
    result_status: str,
    source: str = "monitor",
    symbol: str | None = None,
    timeframe: str | None = None,
    previous_status: str | None = None,
    new_status: str | None = None,
    severity: str = "Informativo",
    payload: dict[str, Any] | None = None,
    payload_hash: str | None = None,
    error_text: str | None = None,
) -> MonitorTelegramAlert:
    body = payload or (candidate.payload if candidate else {})
    row = MonitorTelegramAlert(
        user_id=user_id,
        symbol=candidate.symbol if candidate else (symbol or "SYSTEM"),
        timeframe=candidate.timeframe if candidate else (timeframe or "na"),
        previous_status=candidate.previous_status if candidate else previous_status,
        new_status=candidate.new_status if candidate else (new_status or "INFO"),
        severity=candidate.severity if candidate else severity,
        destination_chat_id=chat_id,
        destination_thread_id=None,
        result_status=result_status,
        error_text=error_text,
        payload_hash=payload_hash or (candidate.payload_hash if candidate else _json_hash(body)),
        source=source,
        payload_json=body,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _settings_diagnostics(settings: MonitorTelegramAlertSettings) -> dict[str, Any]:
    return {
        "token_configured": bool(settings.bot_token),
        "can_send": settings.can_send,
    }


def _collect_transitions(
    db: Session,
    opportunities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    transitions: list[dict[str, Any]] = []
    for opportunity in opportunities:
        symbol = str(opportunity.get("symbol") or "").strip().upper()
        timeframe = str(opportunity.get("timeframe") or "").strip().lower()
        status = str(opportunity.get("status") or "").strip().upper()
        observed = _observed_status_for_pair(db, symbol=symbol, timeframe=timeframe)
        previous_status = observed.status if observed else None
        if symbol and timeframe and status:
            _upsert_observed_status(db, opportunity=opportunity, status=status)
        if previous_status and previous_status == status:
            continue
        candidate = build_monitor_alert_candidate(opportunity, previous_status=previous_status)
        if candidate is None:
            continue
        transitions.append(
            {
                "opportunity": opportunity,
                "candidate": candidate,
                "previous_status": previous_status,
            }
        )
    return transitions


def _send_operational_pause_dm(
    db: Session,
    *,
    user: User,
    settings: MonitorTelegramAlertSettings,
    sender: Callable[..., dict[str, Any]],
    rate_limit_since: datetime,
    dry_run: bool,
    summary: dict[str, Any],
) -> None:
    if _operational_sent_recently(db, user_id=str(user.id), since=rate_limit_since):
        return
    message = (
        "Cripto Farol - Aviso operacional\n\n"
        "Sua carteira Binance está indisponível no momento. "
        "Alertas position-aware pausados até a sincronização voltar."
        + EDUCATIONAL_DISCLAIMER
    )
    chat_id = str(user.telegram_chat_id or "")
    try:
        if dry_run:
            _record_alert(
                db,
                None,
                user_id=str(user.id),
                chat_id=chat_id,
                result_status="dry_run",
                source="operational",
                new_status="PAUSED",
                payload={"message": message},
            )
            summary["operational_dms"] = summary.get("operational_dms", 0) + 1
        else:
            sender(bot_token=settings.bot_token, chat_id=chat_id, text=message, dry_run=False)
            _record_alert(
                db,
                None,
                user_id=str(user.id),
                chat_id=chat_id,
                result_status="sent",
                source="operational",
                new_status="PAUSED",
                payload={"message": message},
            )
            summary["operational_dms"] = summary.get("operational_dms", 0) + 1
    except Exception as exc:
        _record_alert(
            db,
            None,
            user_id=str(user.id),
            chat_id=chat_id,
            result_status="failed",
            source="operational",
            new_status="PAUSED",
            payload={"message": message},
            error_text=str(exc),
        )
        summary["failed"] += 1


def run_monitor_telegram_alert_scan(
    db: Session,
    *,
    user_id: str,
    settings: MonitorTelegramAlertSettings | None = None,
    opportunity_service: OpportunityService | None = None,
    sender: Callable[..., dict[str, Any]] = send_telegram_message,
    force_dry_run: bool = False,
) -> dict[str, Any]:
    settings = settings or load_monitor_telegram_alert_settings(db)
    service = opportunity_service or OpportunityService()
    dry_run = force_dry_run or not settings.can_send
    summary: dict[str, Any] = {
        "enabled": settings.enabled,
        "dry_run": dry_run,
        "eligible_users": 0,
        "candidates": 0,
        "sent": 0,
        "dry_run_count": 0,
        "duplicates": 0,
        "rate_limited": 0,
        "skipped": 0,
        "suppressed_by_position_matrix": 0,
        "failed": 0,
        "binance_sync_failed_users": 0,
        "operational_dms": 0,
        "results": [],
    }
    summary.update(_settings_diagnostics(settings))

    if not settings.enabled and not force_dry_run:
        summary["skipped"] += 1
        summary["results"].append({"status": "disabled"})
        return summary

    opportunities = service.get_catalog_opportunities(
        tier_filter=settings.tier_filter,
        alerts_only=True,
    )
    if not opportunities:
        summary["skipped"] += 1
        summary["results"].append({"result": "no_opportunities"})
        return summary

    transitions = _collect_transitions(db, opportunities)
    if not transitions:
        summary["skipped"] += 1
        summary["results"].append({"result": "no_transitions"})
        return summary

    eligible_users = list_eligible_alert_users(db)
    summary["eligible_users"] = len(eligible_users)
    if not eligible_users:
        summary["skipped"] += 1
        summary["results"].append({"result": "no_eligible_users"})
        return summary

    symbols = sorted(
        {
            str(item["candidate"].symbol)
            for item in transitions
            if item.get("candidate") is not None
        }
    )
    duplicate_since = datetime.utcnow() - timedelta(minutes=max(settings.min_repeat_minutes, 1))
    rate_limit_since = datetime.utcnow() - timedelta(
        minutes=max(settings.rate_limit_window_minutes, 1)
    )

    for user in eligible_users:
        chat_id = str(user.telegram_chat_id or "").strip()
        if not chat_id:
            continue
        uid = str(user.id)
        holdings, sync_ok = fetch_user_wallet_holdings(db, uid, min_usd=1.0)
        portfolio = resolve_portfolio_status_for_user(
            db,
            uid,
            symbols,
            wallet_holdings=holdings,
            binance_sync_ok=sync_ok,
        )
        if any(item.sync_failed for item in portfolio.values()):
            summary["binance_sync_failed_users"] += 1
            _send_operational_pause_dm(
                db,
                user=user,
                settings=settings,
                sender=sender,
                rate_limit_since=rate_limit_since,
                dry_run=dry_run,
                summary=summary,
            )
            continue

        for item in transitions:
            candidate: MonitorAlertCandidate = item["candidate"]
            opp = item["opportunity"]
            symbol_status = portfolio.get(candidate.symbol)
            if symbol_status is None:
                continue
            should_send, reason = should_send_position_aware_alert(
                previous_status=item["previous_status"],
                new_status=candidate.new_status,
                has_spot_position=symbol_status.has_spot_position,
                in_portfolio=symbol_status.in_portfolio,
            )
            if not should_send:
                if reason == "suppressed_by_position_matrix" or reason.startswith("suppressed"):
                    summary["suppressed_by_position_matrix"] += 1
                summary["results"].append(
                    {
                        "user_id": uid,
                        "symbol": candidate.symbol,
                        "timeframe": candidate.timeframe,
                        "status": candidate.new_status,
                        "result": reason,
                    }
                )
                continue

            summary["candidates"] += 1
            if _has_duplicate_recent(
                db,
                user_id=uid,
                symbol=candidate.symbol,
                timeframe=candidate.timeframe,
                status=candidate.new_status,
                since=duplicate_since,
            ):
                summary["duplicates"] += 1
                summary["results"].append(
                    {
                        "user_id": uid,
                        "symbol": candidate.symbol,
                        "timeframe": candidate.timeframe,
                        "status": candidate.new_status,
                        "result": "duplicate",
                    }
                )
                continue

            if _sent_count_since(db, user_id=uid, since=rate_limit_since) >= max(
                settings.rate_limit_count, 0
            ):
                summary["rate_limited"] += 1
                summary["results"].append(
                    {
                        "user_id": uid,
                        "symbol": candidate.symbol,
                        "timeframe": candidate.timeframe,
                        "status": candidate.new_status,
                        "result": "rate_limited",
                    }
                )
                continue

            try:
                if dry_run:
                    _record_alert(
                        db,
                        candidate,
                        user_id=uid,
                        chat_id=chat_id,
                        result_status="dry_run",
                    )
                    summary["dry_run_count"] += 1
                    result_status = "dry_run"
                else:
                    sender(
                        bot_token=settings.bot_token,
                        chat_id=chat_id,
                        text=candidate.message,
                        dry_run=False,
                    )
                    _record_alert(
                        db,
                        candidate,
                        user_id=uid,
                        chat_id=chat_id,
                        result_status="sent",
                    )
                    summary["sent"] += 1
                    result_status = "sent"
            except Exception as exc:
                _record_alert(
                    db,
                    candidate,
                    user_id=uid,
                    chat_id=chat_id,
                    result_status="failed",
                    error_text=str(exc),
                )
                summary["failed"] += 1
                result_status = "failed"

            summary["results"].append(
                {
                    "user_id": uid,
                    "symbol": candidate.symbol,
                    "timeframe": candidate.timeframe,
                    "status": candidate.new_status,
                    "result": result_status,
                }
            )

    return summary
