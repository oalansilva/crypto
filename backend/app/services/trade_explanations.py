"""Build safe, event-time explanations for Monitor and Favorite trades."""

from __future__ import annotations

import math
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Iterable

from app.schemas.strategy_transparency import (
    StrategyLogicBlock,
    StrategyTransparency,
    TradeEvidenceItem,
    TradeExplanation,
)


def _direction(value: Any) -> str:
    return "short" if str(value or "").strip().lower() == "short" else "long"


def _parse_timestamp(value: Any) -> datetime | None:
    if value is None:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _price(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def _rule(manifest: StrategyTransparency, participation: str) -> StrategyLogicBlock | None:
    return next(
        (block for block in manifest.logic_blocks if block.participation == participation),
        None,
    )


def _event_timestamps(
    manifest: StrategyTransparency,
    participation: str,
    direction: str,
) -> list[datetime]:
    timestamps: set[datetime] = set()
    for indicator in manifest.indicators:
        if participation not in indicator.participation:
            continue
        for point in indicator.series:
            parsed = _parse_timestamp(point.timestamp_utc)
            if parsed is not None:
                timestamps.add(parsed)
    market_key = (
        "high"
        if participation == "risk" and direction == "short"
        else "low" if participation == "risk" else "close"
    )
    for point in manifest.market_series.get(market_key, []):
        parsed = _parse_timestamp(point.timestamp_utc)
        if parsed is not None:
            timestamps.add(parsed)
    return sorted(timestamps)


def _decision_candle(
    manifest: StrategyTransparency,
    *,
    participation: str,
    execution_time: Any,
    same_candle: bool,
    direction: str,
) -> datetime | None:
    execution = _parse_timestamp(execution_time)
    if execution is None:
        return None
    candidates = _event_timestamps(manifest, participation, direction)
    if same_candle:
        eligible = [candidate for candidate in candidates if candidate <= execution]
    else:
        eligible = [candidate for candidate in candidates if candidate < execution]
        if not eligible:
            eligible = [candidate for candidate in candidates if candidate <= execution]
    return eligible[-1] if eligible else None


def _evidence_at(
    manifest: StrategyTransparency,
    *,
    participation: str,
    decision_time: datetime | None,
    state: str,
    direction: str,
) -> list[TradeEvidenceItem]:
    if decision_time is None:
        return []

    evidence: list[TradeEvidenceItem] = []
    market_key = (
        "high"
        if participation == "risk" and direction == "short"
        else "low" if participation == "risk" else "close"
    )
    market_labels = {
        "close": "Fechamento do candle",
        "low": "Mínima do candle",
        "high": "Máxima do candle",
    }
    market_candidates = []
    for point in manifest.market_series.get(market_key, []):
        timestamp = _parse_timestamp(point.timestamp_utc)
        if timestamp is not None and timestamp <= decision_time:
            market_candidates.append((timestamp, point))
    if market_candidates:
        timestamp, point = max(market_candidates, key=lambda item: item[0])
        evidence.append(
            TradeEvidenceItem(
                key=market_key,
                label=market_labels[market_key],
                value=point.value,
                timestamp_utc=timestamp.isoformat(),
                state=state,
            )
        )
    seen: set[str] = set()
    for indicator in manifest.indicators:
        if participation not in indicator.participation or indicator.key in seen:
            continue
        point_candidates = []
        for point in indicator.series:
            timestamp = _parse_timestamp(point.timestamp_utc)
            if timestamp is not None and timestamp <= decision_time:
                point_candidates.append((timestamp, point))
        if not point_candidates:
            continue
        timestamp, point = max(point_candidates, key=lambda item: item[0])
        evidence.append(
            TradeEvidenceItem(
                key=indicator.key,
                label=indicator.label,
                value=point.value,
                timestamp_utc=timestamp.isoformat(),
                state=state,
            )
        )
        seen.add(indicator.key)
    return evidence


def _unavailable(
    *,
    direction: str,
    timeframe: str | None,
    action: str,
    trigger: str,
    execution_time: Any,
    execution_price: Any,
    reason: str,
) -> TradeExplanation:
    return TradeExplanation(
        status="unavailable",
        direction=direction,
        timeframe=timeframe,
        action=action,
        trigger=trigger,
        summary="Detalhes da decisão não estão disponíveis para este trade histórico.",
        execution_time=_iso(_parse_timestamp(execution_time)),
        execution_price=_price(execution_price),
        unavailable_reason=reason,
    )


def _event_explanation(
    manifest: StrategyTransparency,
    *,
    direction: str,
    timeframe: str | None,
    participation: str,
    trigger: str,
    execution_time: Any,
    execution_price: Any,
) -> TradeExplanation:
    is_entry = participation == "entry"
    action = (
        "Venda/Short"
        if is_entry and direction == "short"
        else "Compra" if is_entry else "Compra/Cobertura" if direction == "short" else "Venda"
    )
    rule = _rule(manifest, participation)
    if manifest.status != "available" or rule is None or rule.status == "unavailable":
        return _unavailable(
            direction=direction,
            timeframe=timeframe,
            action=action,
            trigger=trigger,
            execution_time=execution_time,
            execution_price=execution_price,
            reason=(rule.description if rule is not None else manifest.unavailable_reason)
            or "Manifesto executado indisponível.",
        )

    is_stop = trigger == "stop_loss"
    decision = _decision_candle(
        manifest,
        participation="risk" if is_stop else participation,
        execution_time=execution_time,
        same_candle=is_stop,
        direction=direction,
    )
    evidence = _evidence_at(
        manifest,
        participation="risk" if is_stop else participation,
        decision_time=decision,
        state="confirmed",
        direction=direction,
    )
    execution_iso = _iso(_parse_timestamp(execution_time))

    if is_stop:
        risk_rule = _rule(manifest, "risk")
        risk_text = risk_rule.description if risk_rule is not None else "O stop foi executado."
        summary = f"{action} executada pelo stop de proteção. {risk_text}"
        status = "available" if execution_iso and _price(execution_price) is not None else "partial"
    elif trigger == "take_profit":
        summary = f"{action} executada pelo objetivo configurado."
        status = "available" if execution_iso and _price(execution_price) is not None else "partial"
    else:
        if decision is None or not evidence:
            return _unavailable(
                direction=direction,
                timeframe=timeframe,
                action=action,
                trigger=trigger,
                execution_time=execution_time,
                execution_price=execution_price,
                reason="O candle do evento não pôde ser alinhado às séries históricas da estratégia.",
            )
        summary = f"{action} executada após confirmação. {rule.description}"
        status = "partial" if rule.status == "partial" else "available"

    return TradeExplanation(
        status=status,
        direction=direction,
        timeframe=timeframe,
        action=action,
        trigger=trigger,
        summary=summary,
        decision_candle_time=_iso(decision),
        execution_time=execution_iso,
        execution_price=_price(execution_price),
        evidence=evidence,
        unavailable_reason=(
            None
            if status == "available"
            else "A regra foi identificada, mas parte da evidência histórica não pôde ser alinhada."
        ),
    )


def _exit_trigger(reason: Any) -> str:
    normalized = str(reason or "").strip().lower()
    if "stop" in normalized:
        return "stop_loss"
    return "exit_rule"


def _latest_series_time(
    manifest: StrategyTransparency, participation: str, direction: str
) -> datetime | None:
    timestamps = _event_timestamps(manifest, participation, direction)
    return timestamps[-1] if timestamps else None


def _open_position_explanation(
    manifest: StrategyTransparency,
    *,
    direction: str,
    timeframe: str | None,
) -> TradeExplanation:
    action = "Venda/Short ativa" if direction == "short" else "Compra ativa"
    rule = _rule(manifest, "exit")
    decision = _latest_series_time(manifest, "exit", direction)
    evidence = _evidence_at(
        manifest,
        participation="exit",
        decision_time=decision,
        state="pending",
        direction=direction,
    )
    if manifest.status != "available" or rule is None:
        return _unavailable(
            direction=direction,
            timeframe=timeframe,
            action=action,
            trigger="open_position",
            execution_time=None,
            execution_price=None,
            reason="Regra pública de saída indisponível.",
        )

    risk_rule = _rule(manifest, "risk")
    if decision is None:
        return _unavailable(
            direction=direction,
            timeframe=timeframe,
            action=action,
            trigger="open_position",
            execution_time=None,
            execution_price=None,
            reason="Valores atuais da regra de saída não estão disponíveis.",
        )

    return TradeExplanation(
        status="available" if rule.status == "available" else "partial",
        direction=direction,
        timeframe=timeframe,
        action=action,
        trigger="open_position",
        summary=(
            "A posição continua aberta porque ainda não há saída confirmada. "
            "A saída técnica e o stop de proteção são acompanhados separadamente."
        ),
        rule_summary=rule.description,
        risk_summary=(
            risk_rule.description
            if risk_rule is not None and risk_rule.status == "available"
            else None
        ),
        decision_candle_time=_iso(decision),
        evidence=evidence,
        unavailable_reason=None,
    )


def explain_trades(
    trades: Iterable[dict[str, Any]],
    manifest: StrategyTransparency,
    *,
    direction: Any,
    timeframe: str | None,
) -> list[dict[str, Any]]:
    """Return copies of trades enriched with safe entry/exit/current-state explanations."""

    normalized_direction = _direction(direction)
    explained: list[dict[str, Any]] = []
    for raw_trade in trades:
        if not isinstance(raw_trade, dict):
            continue
        trade = deepcopy(raw_trade)
        trade["entry_explanation"] = _event_explanation(
            manifest,
            direction=normalized_direction,
            timeframe=timeframe,
            participation="entry",
            trigger="entry_rule",
            execution_time=trade.get("entry_time"),
            execution_price=trade.get("entry_price"),
        ).model_dump(mode="json")
        if trade.get("exit_time") is not None or trade.get("exit_price") is not None:
            trade["exit_explanation"] = _event_explanation(
                manifest,
                direction=normalized_direction,
                timeframe=timeframe,
                participation="exit",
                trigger=_exit_trigger(trade.get("exit_reason") or trade.get("signal_type")),
                execution_time=trade.get("exit_time"),
                execution_price=trade.get("exit_price"),
            ).model_dump(mode="json")
            trade["current_state_explanation"] = None
        else:
            trade["exit_explanation"] = None
            trade["current_state_explanation"] = _open_position_explanation(
                manifest,
                direction=normalized_direction,
                timeframe=timeframe,
            ).model_dump(mode="json")
        explained.append(trade)
    return explained


def explain_signal_history(
    history: Iterable[dict[str, Any]],
    manifest: StrategyTransparency,
    *,
    direction: Any,
    timeframe: str | None,
) -> list[dict[str, Any]]:
    normalized_direction = _direction(direction)
    explained: list[dict[str, Any]] = []
    for raw_item in history:
        if not isinstance(raw_item, dict):
            continue
        item = deepcopy(raw_item)
        is_entry = str(item.get("type") or "").lower() == "entry"
        item["explanation"] = _event_explanation(
            manifest,
            direction=normalized_direction,
            timeframe=timeframe,
            participation="entry" if is_entry else "exit",
            trigger="entry_rule" if is_entry else _exit_trigger(item.get("reason")),
            execution_time=item.get("timestamp"),
            execution_price=item.get("price"),
        ).model_dump(mode="json")
        explained.append(item)
    return explained


def explain_current_position(
    history: Iterable[dict[str, Any]],
    manifest: StrategyTransparency,
    *,
    direction: Any,
    timeframe: str | None,
    is_holding: bool,
) -> TradeExplanation | None:
    normalized_direction = _direction(direction)
    if is_holding:
        return _open_position_explanation(
            manifest,
            direction=normalized_direction,
            timeframe=timeframe,
        )
    latest = next((item for item in reversed(list(history)) if isinstance(item, dict)), None)
    if latest is None:
        return None
    is_entry = str(latest.get("type") or "").lower() == "entry"
    return _event_explanation(
        manifest,
        direction=normalized_direction,
        timeframe=timeframe,
        participation="entry" if is_entry else "exit",
        trigger="entry_rule" if is_entry else _exit_trigger(latest.get("reason")),
        execution_time=latest.get("timestamp"),
        execution_price=latest.get("price"),
    )
