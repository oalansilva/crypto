"""Alertas do Monitor no Telegram (card #747; origem por favorito desde o card #1122).

Card #1122 (regra de 27/10/2026, Design d2):
- origem = estratégias próprias que cada usuário acompanha no Monitor: favoritos com estrela
  (``tier`` 1, 2 ou 3) e alerta ligado (``notify_telegram``); o catálogo nunca alerta e o filtro de
  estrelas do sistema (``monitor_telegram_tier_filter``) é ignorado;
- a carteira não decide: entrada e saída saem nas três classes, com ou sem o ativo na carteira; a
  varredura não lê a carteira Binance e não manda aviso operacional;
- estado por favorito (``monitor_favorite_alert_states``); a primeira leitura é só base;
- evento com identidade (``event_key``) e reserva ``sending`` antes do envio; ``sending`` antigo
  vira ``unknown`` sem reenvio; ``failed`` volta enquanto o evento for o atual;
- sem limite por hora para sinal e atraso (decisão 4 de Alan);
- aviso único de atraso real por usuário, ativo e episódio, a quem tem o ativo no Monitor com
  alerta ligado; mercado fechado nunca manda mensagem;
- aviso único de transição para quem recebia pelo catálogo (sem marca em dry-run nem com falha).
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Callable

import pandas as pd
import requests
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import (
    FavoriteStrategy,
    MonitorFavoriteAlertState,
    MonitorTelegramAlert,
    User,
)
from app.services.opportunity_service import (
    MONITOR_TIERS,
    OpportunityService,
    is_known_non_admin,
)
from app.services.system_preferences_service import (
    get_system_preference_bool,
    get_system_preference_int,
    get_system_preference_value,
    set_system_preference_value,
)
from app.services.user_telegram_service import list_eligible_alert_users

logger = logging.getLogger(__name__)

MONITOR_TELEGRAM_ALERTS_ENABLED_KEY = "monitor_telegram_alerts_enabled"
MONITOR_TELEGRAM_MIN_REPEAT_MINUTES_KEY = "monitor_telegram_min_repeat_minutes"
MONITOR_TELEGRAM_RATE_LIMIT_COUNT_KEY = "monitor_telegram_rate_limit_count"
MONITOR_TELEGRAM_RATE_LIMIT_WINDOW_MINUTES_KEY = "monitor_telegram_rate_limit_window_minutes"
MONITOR_TELEGRAM_TIER_FILTER_KEY = "monitor_telegram_tier_filter"
# Card #1122: instante da troca de origem (catálogo → favoritos), gravado pela migração.
MONITOR_TELEGRAM_FAVORITE_ORIGIN_AT_KEY = "monitor_telegram_favorite_origin_at"
# Primeira varredura depois da troca: a única que decide o aviso "Mudança nos alertas".
MONITOR_TELEGRAM_TRANSITION_SCAN_AT_KEY = "monitor_telegram_transition_scan_at"
# O aviso é do dia da troca: uma varredura bem depois dela (timer parado) não avisa.
TRANSITION_NOTICE_WINDOW = timedelta(days=2)

SENDABLE_STATUSES = {"HOLD", "EXIT"}
RESERVED_RESULTS = ("sending", "sent", "dry_run", "unknown")
# Avisos (atraso, transição) só contam quando a entrega foi tentada; ``duplicate`` não conta.
NOTICE_COUNTED_RESULTS = ("sent", "dry_run", "failed")
# Reserva ``sending`` mais antiga que isto vira ``unknown`` (no máximo uma vez; P3).
SENDING_TIMEOUT = timedelta(minutes=10)
EDUCATIONAL_DISCLAIMER = (
    "\n\nAviso: ferramenta educacional de apoio à decisão. "
    "Não constitui recomendação financeira nem ordem de compra/venda."
)
NO_ORDER_LINE = "Este alerta não envia ordem: é só o sinal da estratégia."
# Decisão 10 (r2): como parar de receber.
STOP_SIGNAL_LINE = (
    'Para não receber mais desta estratégia: desligue o "Alerta" dela no Monitor '
    "ou tire a estrela em Favoritos."
)
BRT = "America/Sao_Paulo"
_WEEKDAYS = ("seg.", "ter.", "qua.", "qui.", "sex.", "sáb.", "dom.")
_MONTHS = (
    "jan.",
    "fev.",
    "mar.",
    "abr.",
    "mai.",
    "jun.",
    "jul.",
    "ago.",
    "set.",
    "out.",
    "nov.",
    "dez.",
)
_CLASS_LABEL = {"crypto": "Cripto", "stock": "Ação", "etf": "ETF"}


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
    try:
        return f"{float(value):,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    except (TypeError, ValueError):
        return str(value)


def _format_money(value: Any, currency: str | None) -> str:
    text = _format_alert_value(value)
    if text == "N/D" or not currency:
        return text
    return f"{text} {currency}"


def _utc_ts(value: Any) -> pd.Timestamp | None:
    if value is None or str(value).strip() == "":
        return None
    try:
        ts = pd.Timestamp(value)
    except Exception:
        return None
    if pd.isna(ts):
        return None
    return ts.tz_localize("UTC") if ts.tzinfo is None else ts.tz_convert("UTC")


def format_day_pt(day: Any) -> str:
    """``sex., 23 out. 2026``."""

    return f"{_WEEKDAYS[day.weekday()]}, {day.day:02d} {_MONTHS[day.month - 1]} {day.year}"


def _is_equity_class(asset_class: str | None) -> bool:
    return str(asset_class or "").lower() in {"stock", "etf"}


def describe_candle(candle_time: Any, timeframe: str, asset_class: str | None) -> str:
    """Data do candle fechado para a mensagem, com o horário do fechamento em BRT."""

    start = _utc_ts(candle_time)
    if start is None:
        return "N/D"
    tf = str(timeframe or "1d").strip().lower()
    if _is_equity_class(asset_class):
        from app.services.market_history import nyse_calendar

        if tf == "1d":
            day = (start + pd.Timedelta(hours=12)).tz_convert(nyse_calendar.NY).date()
            close = None
            try:
                window = nyse_calendar.session_window(day)
                close = window.close_utc if window is not None else None
            except Exception:
                close = None
            if close is not None:
                return (
                    f"{format_day_pt(day)} (pregão fechou às "
                    f"{close.tz_convert(BRT).strftime('%H:%M')} BRT)"
                )
            return format_day_pt(day)
        end = None
        try:
            end = nyse_calendar.session_close_for_candle(start, tf)
        except Exception:
            end = None
        local = start.tz_convert(BRT)
        text = f"{format_day_pt(local.date())}, {local.strftime('%H:%M')}"
        if end is not None:
            text += f"–{end.tz_convert(BRT).strftime('%H:%M')}"
        return f"{text} BRT"
    if tf == "1d":
        close = (start + pd.Timedelta(days=1)).tz_convert(BRT)
        return f"{format_day_pt(start.date())} (fechou às {close.strftime('%H:%M')} BRT)"
    local = start.tz_convert(BRT)
    return f"{format_day_pt(local.date())}, {local.strftime('%H:%M')} BRT"


def _alert_date(opportunity: dict[str, Any]) -> str:
    raw = (
        opportunity.get("candle_time")
        or opportunity.get("indicator_values_candle_time")
        or opportunity.get("timestamp")
    )
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


def _key(*parts: Any) -> str:
    return hashlib.sha256("|".join(str(p or "") for p in parts).encode("utf-8")).hexdigest()


def signal_event_key(user_id: str, favorite_id: Any, new_status: str, candle_time: Any) -> str:
    """Chave do alerta de sinal: usuário, favorito, leitura nova e início do candle fechado."""

    candle = _utc_ts(candle_time)
    return _key(
        user_id,
        favorite_id,
        str(new_status).upper(),
        candle.isoformat() if candle is not None else candle_time,
    )


def delay_event_key(user_id: str, data_source: str, symbol: str, episode_id: str) -> str:
    return _key(user_id, "delay", data_source, symbol, episode_id)


def transition_event_key(user_id: str) -> str:
    return _key(user_id, "transition")


def _is_stop_reason(opportunity: dict[str, Any]) -> bool:
    raw = str(opportunity.get("raw_analysis_status") or "").strip().upper()
    return bool(opportunity.get("stop_breached_now")) or raw == "STOPPED_OUT"


def signal_direction(previous_status: str | None, new_status: str | None) -> str | None:
    """Sentido da mudança de leitura (card #1122, decisão 6: a carteira não decide).

    ``EXIT→HOLD`` = entrada (``buy``) e ``HOLD→EXIT`` = saída (``sell``), em cripto, ação e ETF,
    com ou sem o ativo na carteira e com ou sem saldo na Binance. Outra combinação não é sinal.
    """

    prev = str(previous_status or "").strip().upper()
    new = str(new_status or "").strip().upper()
    if prev == "EXIT" and new == "HOLD":
        return "buy"
    if prev == "HOLD" and new == "EXIT":
        return "sell"
    return None


def is_monitored_alert_on(item: dict[str, Any]) -> bool:
    """Estratégia própria no Monitor com alerta ligado: estrela (1–3) e ``notify_telegram``.

    A linha do catálogo (vitrine) nunca alerta, nem com a estrela da preferência de quem vê.
    """

    if item.get("is_curated_fallback") or not item.get("notify_telegram"):
        return False
    try:
        tier = int(item["tier"]) if item.get("tier") is not None else None
    except (TypeError, ValueError):
        return False
    return tier in MONITOR_TIERS


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
        # Card #1122: a janela por tempo deixa de decidir duplicata (fica até o archive).
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


def tier_filter_ignored(db: Session) -> str | None:
    """O filtro de estrelas do sistema preenchido (preferência ou ambiente), que a varredura ignora
    desde a regra de 27/10/2026 (decisão 2). ``None`` quando vazio ou ``all``."""

    raw = (
        get_system_preference_value(db, MONITOR_TELEGRAM_TIER_FILTER_KEY)
        or os.getenv("MONITOR_TELEGRAM_TIER_FILTER")
        or ""
    ).strip()
    if not raw or raw.lower() == "all":
        return None
    return raw


def _asset_line(opportunity: dict[str, Any], symbol: str) -> str:
    asset_class = str(opportunity.get("asset_class") or "").lower()
    if not asset_class:
        asset_class = "crypto" if "/" in symbol else "stock"
    currency = opportunity.get("currency") or (symbol.partition("/")[2] if "/" in symbol else "USD")
    return f"{symbol} ({_CLASS_LABEL.get(asset_class, 'Ação')} · {currency})"


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
    asset_class = str(opportunity.get("asset_class") or "").lower() or (
        "crypto" if "/" in symbol else "stock"
    )
    currency = opportunity.get("currency") or (symbol.partition("/")[2] if "/" in symbol else "USD")
    configuration = (
        opportunity.get("configuration")
        if isinstance(opportunity.get("configuration"), dict)
        else {}
    )
    configuration_label = configuration.get("label_long") or (
        "Binance Spot · 24/7" if asset_class == "crypto" else "N/D"
    )
    candle_time = opportunity.get("candle_time") or opportunity.get("indicator_values_candle_time")
    prev_label = _action_label(previous_status)
    message = (
        "Cripto Farol - Alerta Monitor\n\n"
        f"Ativo: {_asset_line(opportunity, symbol)}\n"
        f"Estratégia: {strategy_name}\n"
        f"Configuração: {configuration_label}\n"
        f"TimeFrame: {timeframe}\n"
        f"Leitura anterior: {prev_label}\n"
        f"Leitura atual: {action}\n"
        f"Candle: {describe_candle(candle_time, timeframe, asset_class)}\n"
        f"Valor Entrada: {_format_money(entry_value, currency)}\n"
        f"Stop: {_format_money(stop_value, currency)}"
    )
    if stop_reason:
        message += "\nMotivo=Stop"
    message += f"\n{NO_ORDER_LINE}"
    message += f"\n{STOP_SIGNAL_LINE}"
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
        "favorite_id": opportunity.get("id"),
        "configuration": {
            key: configuration.get(key)
            for key in ("data_source", "session", "adjustment", "label_long")
            if configuration.get(key) is not None
        },
        "asset_class": asset_class,
        "currency": currency,
        "candle_time": candle_time,
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


def build_delay_message(
    *,
    symbol: str,
    asset_class: str | None,
    currency: str | None,
    configuration: dict[str, Any] | None,
    timeframe: str,
    last_candle: Any,
    expected_candle: Any,
    waiting_favorites: int = 1,
) -> str:
    cls = str(asset_class or ("crypto" if "/" in symbol else "stock")).lower()
    source_label = str((configuration or {}).get("label_short") or "").split(" · ")[0]
    if (configuration or {}).get("data_source") == "stooq":
        source_label = "Stooq (fonte antiga)"
    last = _utc_ts(last_candle)
    expected = _utc_ts(expected_candle)

    def day_of(ts: pd.Timestamp | None) -> str:
        if ts is None:
            return "nenhum"
        if _is_equity_class(cls) and str(timeframe).lower() == "1d":
            from app.services.market_history import nyse_calendar

            return format_day_pt((ts + pd.Timedelta(hours=12)).tz_convert(nyse_calendar.NY).date())
        if str(timeframe).lower() == "1d":
            return format_day_pt(ts.date())
        local = ts.tz_convert(BRT)
        return f"{format_day_pt(local.date())}, {local.strftime('%H:%M')} BRT"

    expected_note = "o pregão já fechou" if _is_equity_class(cls) else "o candle já fechou"
    waiting = f" ({waiting_favorites} favoritos seus em espera)" if waiting_favorites > 1 else ""
    return (
        "Cripto Farol - Dados atrasados\n\n"
        f"Ativo: {symbol} ({_CLASS_LABEL.get(cls, 'Ação')} · {currency or 'USD'})"
        + (f" · {source_label}" if source_label else "")
        + "\n"
        f"Último candle recebido: {day_of(last)} ({timeframe})\n"
        f"Esperado: {day_of(expected)} ({expected_note})\n"
        f"Os sinais deste ativo ficam em espera até o dado normalizar{waiting}. "
        "Você não recebe outro aviso enquanto o atraso durar.\n"
        f'Para não receber avisos de {symbol}: desligue o "Alerta" das estratégias de {symbol} '
        "no Monitor."
    )


def build_transition_message(symbols: list[str]) -> str:
    listed = ", ".join(symbols[:-1]) + (" e " + symbols[-1] if len(symbols) > 1 else "")
    listed = listed or (symbols[0] if symbols else "")
    received = f" Você recebia: {listed}." if listed else ""
    return (
        "Cripto Farol - Mudança nos alertas\n\n"
        "Os alertas do Telegram agora vêm das estratégias que você acompanha no Monitor, e não "
        f"mais do catálogo do Cripto Farol.{received} Para voltar a receber, salve a estratégia "
        "nos Favoritos e dê pelo menos 1 estrela: o alerta já vem ligado e você desliga no "
        "Monitor. Esta mensagem não se repete."
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


def _settings_diagnostics(settings: MonitorTelegramAlertSettings) -> dict[str, Any]:
    return {
        "token_configured": bool(settings.bot_token),
        "can_send": settings.can_send,
    }


def _event_reserved(db: Session, *, user_id: str, event_key: str) -> bool:
    return (
        db.query(MonitorTelegramAlert.id)
        .filter(
            MonitorTelegramAlert.user_id == user_id,
            MonitorTelegramAlert.event_key == event_key,
            MonitorTelegramAlert.result_status.in_(RESERVED_RESULTS),
        )
        .first()
        is not None
    )


def _event_failed(db: Session, *, user_id: str, event_key: str) -> bool:
    return (
        db.query(MonitorTelegramAlert.id)
        .filter(
            MonitorTelegramAlert.user_id == user_id,
            MonitorTelegramAlert.event_key == event_key,
            MonitorTelegramAlert.result_status == "failed",
        )
        .first()
        is not None
    )


def _expire_stale_reservations(db: Session, *, now: datetime, summary: dict[str, Any]) -> None:
    """``sending`` antigo vira ``unknown`` e nunca é reenviado (no máximo uma vez)."""

    rows = (
        db.query(MonitorTelegramAlert)
        .filter(
            MonitorTelegramAlert.result_status == "sending",
            MonitorTelegramAlert.created_at < now - SENDING_TIMEOUT,
        )
        .all()
    )
    for row in rows:
        row.result_status = "unknown"
        row.error_text = (row.error_text or "") + "reserva sem resultado: não reenviada"
        payload = row.payload_json if isinstance(row.payload_json, dict) else {}
        summary["unknown"] += 1
        summary["results"].append(
            {
                "user_id": row.user_id,
                "symbol": row.symbol,
                "timeframe": row.timeframe,
                "favorite_id": row.favorite_id,
                "candle_time": payload.get("candle_time"),
                "status": row.new_status,
                "result": "unknown",
            }
        )
        logger.warning(
            "Monitor Telegram: reserva %s (favorito %s, %s %s) virou unknown sem reenvio",
            row.id,
            row.favorite_id,
            row.symbol,
            row.timeframe,
        )
    if rows:
        db.commit()


def _deliver(
    db: Session,
    *,
    user: User,
    event_key: str,
    message: str,
    source: str,
    symbol: str,
    timeframe: str,
    previous_status: str | None,
    new_status: str,
    severity: str,
    payload: dict[str, Any],
    favorite_id: int | None,
    settings: MonitorTelegramAlertSettings,
    sender: Callable[..., dict[str, Any]],
    dry_run: bool,
    summary: dict[str, Any],
    kind: str,
    now: datetime | None = None,
    record_dry_run: bool = True,
) -> str:
    """Reserva o evento, chama o Telegram e grava o resultado. Uma mensagem por evento.

    ``record_dry_run=False``: em dry-run nada é gravado (nem a reserva), para o ensaio não
    consumir a chave (aviso de transição, residual P2 da w3).
    """

    uid = str(user.id)
    chat_id = str(user.telegram_chat_id or "").strip()
    result_entry = {
        "user_id": uid,
        "kind": kind,
        "favorite_id": favorite_id,
        "symbol": symbol,
        "timeframe": timeframe,
        "status": new_status,
        "candle_time": payload.get("candle_time"),
    }
    if _event_reserved(db, user_id=uid, event_key=event_key):
        summary["duplicates"] += 1
        summary["results"].append({**result_entry, "result": "duplicate"})
        return "duplicate"
    if dry_run and not record_dry_run:
        summary["dry_run_count"] += 1
        summary["results"].append({**result_entry, "result": "dry_run", "recorded": False})
        return "dry_run"
    row = MonitorTelegramAlert(
        created_at=now or datetime.utcnow(),
        user_id=uid,
        symbol=symbol,
        timeframe=timeframe,
        previous_status=previous_status,
        new_status=new_status,
        severity=severity,
        destination_chat_id=chat_id,
        destination_thread_id=None,
        result_status="dry_run" if dry_run else "sending",
        payload_hash=_json_hash(payload),
        source=source,
        payload_json={**payload, "message": message},
        favorite_id=favorite_id,
        event_key=event_key,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        # Varredura concorrente já reservou o mesmo evento (índice único parcial).
        db.rollback()
        summary["duplicates"] += 1
        summary["results"].append({**result_entry, "result": "duplicate"})
        return "duplicate"
    if dry_run:
        summary["dry_run_count"] += 1
        summary["results"].append({**result_entry, "result": "dry_run"})
        return "dry_run"
    try:
        sender(bot_token=settings.bot_token, chat_id=chat_id, text=message, dry_run=False)
    except Exception as exc:
        row.result_status = "failed"
        row.error_text = str(exc)[:2000]
        db.commit()
        summary["failed"] += 1
        summary["results"].append({**result_entry, "result": "failed"})
        return "failed"
    row.result_status = "sent"
    db.commit()
    summary["sent"] += 1
    summary["results"].append({**result_entry, "result": "sent"})
    return "sent"


# ---------------------------------------------------------------- estado por favorito


def _observe_favorite(
    db: Session, opportunity: dict[str, Any], *, now: datetime
) -> dict[str, Any] | None:
    """Atualiza o estado do favorito e devolve a transição (ou ``None``).

    A primeira leitura é só base. Leitura igual só atualiza o horário. Leitura nova grava o
    evento atual no estado (para a nova tentativa de um ``failed``).
    """

    favorite_id = opportunity.get("id")
    status = str(opportunity.get("status") or "").strip().upper()
    if favorite_id is None or not status:
        return None
    candle_time = opportunity.get("candle_time") or opportunity.get("indicator_values_candle_time")
    state = db.get(MonitorFavoriteAlertState, int(favorite_id))
    if state is None:
        exists = db.get(FavoriteStrategy, int(favorite_id))
        if exists is None:
            return None
        db.add(
            MonitorFavoriteAlertState(
                favorite_id=int(favorite_id),
                status=status,
                candle_time=str(candle_time) if candle_time else None,
                observed_at=now,
                payload_json={"opportunity_id": favorite_id, "baseline": True},
            )
        )
        db.commit()
        return {"kind": "baseline"}
    previous = str(state.status or "").strip().upper()
    payload = dict(state.payload_json or {}) if isinstance(state.payload_json, dict) else {}
    if previous == status:
        state.observed_at = now
        db.commit()
        pending = payload.get("last_event")
        if isinstance(pending, dict) and pending.get("new_status") == status:
            return {"kind": "current", "event": pending}
        return {"kind": "unchanged"}
    event = {
        "previous_status": previous,
        "new_status": status,
        "candle_time": str(candle_time) if candle_time else None,
        "observed_at": now.isoformat(),
    }
    state.status = status
    state.candle_time = str(candle_time) if candle_time else None
    state.observed_at = now
    state.payload_json = {**payload, "last_event": event, "baseline": False}
    db.commit()
    return {"kind": "transition", "event": event}


# ---------------------------------------------------------------- transição do catálogo


def _origin_at(db: Session) -> datetime | None:
    raw = get_system_preference_value(db, MONITOR_TELEGRAM_FAVORITE_ORIGIN_AT_KEY)
    if not raw:
        return None
    try:
        return datetime.fromisoformat(str(raw).replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return None


def _transition_scan_at(db: Session) -> str | None:
    return get_system_preference_value(db, MONITOR_TELEGRAM_TRANSITION_SCAN_AT_KEY)


def _transition_scan_due(db: Session, origin_at: datetime | None, now: datetime) -> bool:
    """O aviso de transição sai só na primeira varredura depois da troca, no dia dela.

    Sem o instante da troca não há dia da troca: nenhum aviso. Depois da primeira varredura
    (marcada em ``MONITOR_TELEGRAM_TRANSITION_SCAN_AT_KEY``), quem dá e tira a estrela de um
    favorito semanas depois não recebe o aviso.
    """

    if origin_at is None or now < origin_at:
        return False
    if now - origin_at > TRANSITION_NOTICE_WINDOW:
        return False
    return _transition_scan_at(db) is None


def _catalog_alert_rows(db: Session, user_id: str, origin_at: datetime | None):
    """Alertas do catálogo enviados antes da troca (sem favorito nem chave de evento)."""

    query = db.query(MonitorTelegramAlert).filter(
        MonitorTelegramAlert.user_id == user_id,
        MonitorTelegramAlert.source == "monitor",
        MonitorTelegramAlert.result_status == "sent",
        MonitorTelegramAlert.favorite_id.is_(None),
        MonitorTelegramAlert.event_key.is_(None),
    )
    if origin_at is not None:
        query = query.filter(MonitorTelegramAlert.created_at < origin_at)
    return query


def _monitored_favorites(db: Session, user_id: str):
    """Favoritos próprios com estrela: os que estão no Monitor."""

    return db.query(FavoriteStrategy).filter(
        FavoriteStrategy.user_id == user_id,
        FavoriteStrategy.tier.in_(MONITOR_TIERS),
    )


def _has_monitored_alert_on(db: Session, user_id: str) -> bool:
    """Tem estratégia própria com estrela e alerta ligado (critério da transição, decisão 16)."""

    return (
        _monitored_favorites(db, user_id)
        .filter(FavoriteStrategy.notify_telegram.is_(True))
        .with_entities(FavoriteStrategy.id)
        .first()
        is not None
    )


def alert_origin_for_user(db: Session, user_id: str) -> dict[str, Any]:
    """Faixa da vitrine no Monitor (decisão 16).

    ``show_banner`` = o Monitor mostra o catálogo: quem não é admin e não tem favorito próprio com
    estrela, com ou sem Telegram ligado. A frase datada só vale para quem recebia pelo catálogo.
    """

    user = db.query(User).filter(User.id == user_id).first()
    enabled = bool(user and user.telegram_alerts_enabled)
    monitored = _monitored_favorites(db, str(user_id)).all()
    alerts_on = sum(1 for row in monitored if row.notify_telegram)
    origin_at = _origin_at(db)
    rows = _catalog_alert_rows(db, str(user_id), origin_at)
    received = rows.first() is not None
    until = None
    if received:
        if origin_at is not None:
            until = origin_at.date().isoformat()
        else:
            last = rows.order_by(MonitorTelegramAlert.created_at.desc()).first()
            until = last.created_at.date().isoformat() if last and last.created_at else None
    return {
        "telegram_alerts_enabled": enabled,
        "has_monitored_strategy": bool(monitored),
        "alerts_on": alerts_on,
        "received_catalog_alerts": received,
        "catalog_until": until,
        "show_banner": bool(
            user is not None and not monitored and is_known_non_admin(db, str(user_id))
        ),
    }


# ---------------------------------------------------------------- varredura


def _new_summary(settings: MonitorTelegramAlertSettings, dry_run: bool) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "enabled": settings.enabled,
        "dry_run": dry_run,
        "eligible_users": 0,
        "favorites_evaluated": 0,
        "candidates": 0,
        "signal_events": 0,
        "delay_notices": 0,
        "transition_notices": 0,
        "baselines": 0,
        "held_by_delay": 0,
        "sent": 0,
        "dry_run_count": 0,
        "duplicates": 0,
        # Card #1122 (decisão 4 de Alan): sinal e atraso nunca ficam como ``rate_limited``.
        "rate_limited": 0,
        "unknown": 0,
        "skipped": 0,
        "failed": 0,
        "results": [],
    }
    summary.update(_settings_diagnostics(settings))
    return summary


def _own_series_stale(opp: dict[str, Any]) -> bool:
    market = opp.get("market_state") if isinstance(opp.get("market_state"), dict) else {}
    own = market.get("stale_timeframe")
    if own is None and not market.get("stale_detail"):
        return True  # linha sem detalhe de outro tempo gráfico: o atraso é da própria série
    return str(own or "").lower() == str(opp.get("timeframe") or "").lower()


def _delay_series(opp: dict[str, Any]) -> tuple[str, Any, Any]:
    """Tempo gráfico, último e esperado do aviso de atraso, sempre da mesma série.

    Se o ativo está em espera por outro tempo gráfico, o aviso mostra os horários e o rótulo
    desse tempo gráfico, nunca os de um com o rótulo do outro (card #1122, residual P2).
    """

    market = opp.get("market_state") if isinstance(opp.get("market_state"), dict) else {}
    if not _own_series_stale(opp):
        detail = market.get("stale_detail") or {}
        return (
            str(detail.get("timeframe") or market.get("stale_timeframe") or "1d"),
            detail.get("last_candle"),
            detail.get("expected_candle"),
        )
    return (
        str(opp.get("timeframe") or "1d"),
        market.get("last_candle"),
        market.get("expected_candle"),
    )


def _alert_opportunities(service: Any, now: Any) -> list[dict[str, Any]]:
    """Favoritos com estrela e alerta ligado de todos os donos (sem filtro de estrelas)."""

    getter = getattr(service, "get_alert_opportunities", None)
    if getter is None:
        return []
    try:
        return list(getter(now=now) or [])
    except TypeError:
        return list(getter() or [])


def run_monitor_telegram_alert_scan(
    db: Session,
    *,
    user_id: str | None = None,
    settings: MonitorTelegramAlertSettings | None = None,
    opportunity_service: OpportunityService | None = None,
    sender: Callable[..., dict[str, Any]] = send_telegram_message,
    force_dry_run: bool = False,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Varredura diária: cada usuário recebe só os alertas das próprias estratégias no Monitor
    (favorito com estrela e alerta ligado), em cripto, ação e ETF, sem consultar a carteira.

    ``user_id`` não limita nada (a varredura é de todos); fica por compatibilidade.
    """

    del user_id
    settings = settings or load_monitor_telegram_alert_settings(db)
    service = opportunity_service or OpportunityService()
    dry_run = force_dry_run or not settings.can_send
    summary = _new_summary(settings, dry_run)
    now = now or datetime.utcnow()

    if not settings.enabled and not force_dry_run:
        summary["skipped"] += 1
        summary["results"].append({"status": "disabled"})
        return summary

    _expire_stale_reservations(db, now=now, summary=summary)

    eligible_users = [
        user for user in list_eligible_alert_users(db) if str(user.telegram_chat_id or "").strip()
    ]
    summary["eligible_users"] = len(eligible_users)
    users_by_id = {str(user.id): user for user in eligible_users}
    # Decisão 2: o filtro de estrelas do sistema não muda quem recebe; fica só no resumo.
    ignored_filter = tier_filter_ignored(db)
    if ignored_filter:
        summary["tier_filter_ignored"] = ignored_filter

    # (c) a união das estratégias com estrela e alerta ligado, avaliada uma vez (a coleta
    # deduplica fonte:símbolo_tempo). O catálogo nunca entra.
    opportunities = [
        opp
        for opp in _alert_opportunities(service, pd.Timestamp(now))
        if is_monitored_alert_on(opp)
    ]
    summary["favorites_evaluated"] = len(opportunities)

    # (d) transição por favorito; o dono decide se recebe.
    signal_items: list[dict[str, Any]] = []
    delay_groups: dict[tuple[str, str, str], dict[str, Any]] = {}
    for opp in opportunities:
        owner = str(opp.get("user_id") or "")
        market = opp.get("market_state") if isinstance(opp.get("market_state"), dict) else {}
        state = str(market.get("state") or "")
        symbol = str(opp.get("symbol") or "").strip().upper()
        configuration = (
            opp.get("configuration") if isinstance(opp.get("configuration"), dict) else {}
        )
        data_source = str(configuration.get("data_source") or "")
        if state == "insufficient":
            # Dado insuficiente: sem sinal nem aviso; a leitura completa vira base.
            summary["skipped"] += 1
            continue
        if state == "stale":
            # Sinal em espera enquanto o ativo estiver atrasado (a leitura incompleta não decide).
            summary["held_by_delay"] += 1
            episode_id = market.get("episode_id") or market.get("stale_since")
            if owner and episode_id:
                group = delay_groups.setdefault(
                    (owner, data_source, symbol),
                    {"opportunity": opp, "episode_id": str(episode_id), "count": 0},
                )
                # O aviso usa, de preferência, um favorito cuja própria série está atrasada.
                if _own_series_stale(opp) and not _own_series_stale(group["opportunity"]):
                    group["opportunity"] = opp
                group["count"] += 1
            continue
        observed = _observe_favorite(db, opp, now=now)
        if observed is None:
            continue
        if observed["kind"] == "baseline":
            summary["baselines"] += 1
            continue
        if observed["kind"] == "unchanged":
            continue
        event = observed["event"]
        if observed["kind"] == "current":
            # Só volta o evento atual que falhou antes de o Telegram aceitar; depois de um
            # reenvio aceito a linha ``failed`` fica, mas a reserva ``sent`` encerra o evento.
            key = signal_event_key(
                owner, opp.get("id"), event["new_status"], event.get("candle_time")
            )
            if (
                not owner
                or not _event_failed(db, user_id=owner, event_key=key)
                or _event_reserved(db, user_id=owner, event_key=key)
            ):
                continue
        if not _sendable_status(event.get("new_status")):
            continue
        signal_items.append({"opportunity": opp, "event": event, "owner": owner})

    # Alertas de sinal: uma mensagem por favorito, sem limite por hora e sem carteira (decisão 6).
    for item in signal_items:
        opp = item["opportunity"]
        event = item["event"]
        owner = item["owner"]
        user = users_by_id.get(owner)
        symbol = str(opp.get("symbol") or "").strip().upper()
        base_entry = {
            "user_id": owner,
            "favorite_id": opp.get("id"),
            "symbol": symbol,
            "timeframe": opp.get("timeframe"),
            "status": event.get("new_status"),
        }
        if user is None:
            summary["results"].append({**base_entry, "result": "owner_not_eligible"})
            continue
        if signal_direction(event.get("previous_status"), event.get("new_status")) is None:
            summary["results"].append({**base_entry, "result": "not_a_signal"})
            continue
        candle_time = event.get("candle_time") or opp.get("candle_time")
        candidate = build_monitor_alert_candidate(
            {**opp, "candle_time": candle_time},
            previous_status=event.get("previous_status"),
        )
        if candidate is None:
            continue
        summary["candidates"] += 1
        summary["signal_events"] += 1
        _deliver(
            db,
            user=user,
            event_key=signal_event_key(owner, opp.get("id"), candidate.new_status, candle_time),
            message=candidate.message,
            source="monitor",
            symbol=candidate.symbol,
            timeframe=candidate.timeframe,
            previous_status=candidate.previous_status,
            new_status=candidate.new_status,
            severity=candidate.severity,
            payload={**candidate.payload, "candle_time": candle_time},
            favorite_id=int(opp["id"]) if opp.get("id") is not None else None,
            settings=settings,
            sender=sender,
            dry_run=dry_run,
            summary=summary,
            kind="signal",
            now=now,
        )

    # Avisos de atraso: um por usuário, ativo e episódio, a quem tem o ativo no Monitor com alerta
    # ligado (decisão 9); a carteira não entra.
    for (owner, data_source, symbol), group in delay_groups.items():
        user = users_by_id.get(owner)
        if user is None:
            continue
        opp = group["opportunity"]
        asset_class = str(opp.get("asset_class") or ("crypto" if "/" in symbol else "stock"))
        market = opp.get("market_state") or {}
        delay_timeframe, delay_last, delay_expected = _delay_series(opp)
        message = build_delay_message(
            symbol=symbol,
            asset_class=asset_class,
            currency=opp.get("currency"),
            configuration=opp.get("configuration"),
            timeframe=delay_timeframe,
            last_candle=delay_last,
            expected_candle=delay_expected,
            waiting_favorites=int(group["count"]),
        )
        delivered = _deliver(
            db,
            user=user,
            event_key=delay_event_key(owner, data_source, symbol, group["episode_id"]),
            message=message,
            source="delay",
            symbol=symbol,
            timeframe=delay_timeframe,
            previous_status=None,
            new_status="DELAYED",
            severity="Atencao",
            payload={
                "kind": "delay",
                "data_source": data_source,
                "episode_id": group["episode_id"],
                "last_candle": delay_last,
                "expected_candle": delay_expected,
                "stale_since": market.get("stale_since"),
            },
            favorite_id=None,
            settings=settings,
            sender=sender,
            dry_run=dry_run,
            summary=summary,
            kind="delay",
            now=now,
        )
        if delivered in NOTICE_COUNTED_RESULTS:
            summary["delay_notices"] += 1

    # Transição: aviso único, só na primeira varredura depois da troca (o dia da troca), para
    # quem recebia pelo catálogo e não tem estratégia própria com estrela e alerta ligado.
    origin_at = _origin_at(db)
    transition_users = users_by_id if _transition_scan_due(db, origin_at, now) else {}
    transition_failed = False
    for uid, user in transition_users.items():
        if _has_monitored_alert_on(db, uid):
            continue
        transition_key = transition_event_key(uid)
        if _event_reserved(db, user_id=uid, event_key=transition_key):
            # Aviso já reservado: não relê o histórico do catálogo a cada varredura.
            continue
        rows = _catalog_alert_rows(db, uid, origin_at).all()
        if not rows:
            continue
        symbols = sorted({str(row.symbol) for row in rows if row.symbol})
        delivered = _deliver(
            db,
            user=user,
            event_key=transition_key,
            message=build_transition_message(symbols),
            source="transition",
            symbol="SYSTEM",
            timeframe="na",
            previous_status=None,
            new_status="TRANSITION",
            severity="Informativo",
            payload={"kind": "transition", "symbols": symbols},
            favorite_id=None,
            settings=settings,
            sender=sender,
            dry_run=dry_run,
            summary=summary,
            kind="transition",
            now=now,
            # Em dry-run nem a reserva da chave ``transition`` é gravada (residual P2 da w3).
            record_dry_run=False,
        )
        if delivered == "failed":
            transition_failed = True
        if delivered in NOTICE_COUNTED_RESULTS:
            summary["transition_notices"] += 1
    # A marca só é gravada numa varredura real em que nenhuma entrega de transição falhou: o
    # ensaio em dry-run não fecha a janela, e quem falhou é tentado de novo na varredura seguinte.
    if (
        not dry_run
        and not transition_failed
        and origin_at is not None
        and now >= origin_at
        and _transition_scan_at(db) is None
    ):
        set_system_preference_value(
            db,
            key=MONITOR_TELEGRAM_TRANSITION_SCAN_AT_KEY,
            value=now.isoformat(),
            updated_by_user_id="monitor_telegram_scan",
        )

    if not opportunities and summary["transition_notices"] == 0:
        summary["skipped"] += 1
        summary["results"].append({"result": "no_opportunities"})
    return summary


__all__ = [
    "MonitorAlertCandidate",
    "MonitorTelegramAlertSettings",
    "alert_origin_for_user",
    "build_delay_message",
    "build_monitor_alert_candidate",
    "build_transition_message",
    "describe_candle",
    "is_monitored_alert_on",
    "load_monitor_telegram_alert_settings",
    "run_monitor_telegram_alert_scan",
    "send_telegram_message",
    "signal_direction",
    "tier_filter_ignored",
]
