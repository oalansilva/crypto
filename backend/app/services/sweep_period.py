"""Normalização de período para Descoberta e Combo (card #1078)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.tasks.discovery_tasks import resolve_optimizer_date_range

CUSTOM_PERIOD = "custom"
ALL_PERIOD = "all"


def validate_custom_period(
    start_date: str | None,
    end_date: str | None,
    *,
    now: datetime | None = None,
) -> str | None:
    """Retorna mensagem de operador ou None se válido."""
    if not start_date and not end_date:
        return "Seleccione Data Inicial e Data Final."
    if not start_date:
        return "Seleccione Data Inicial."
    if not end_date:
        return "Seleccione Data Final."
    if start_date > end_date:
        return "Data Inicial não pode ser depois da Data Final."
    today = (now or datetime.now(timezone.utc)).date().isoformat()
    if end_date > today:
        return "Data Final não pode ser depois de hoje."
    return None


def normalize_sweep_period(
    *,
    period_type: str | None,
    start_date: str | None,
    end_date: str | None,
    now: datetime | None = None,
) -> tuple[str | None, str | None, str | None, dict[str, str]]:
    """Resolve period_type + datas para snapshot/preflight."""
    errors: dict[str, str] = {}
    ptype = period_type or ALL_PERIOD

    if ptype == CUSTOM_PERIOD:
        msg = validate_custom_period(start_date, end_date, now=now)
        if msg:
            errors["period"] = msg
        return ptype, start_date, end_date, errors

    if ptype == ALL_PERIOD:
        return ptype, None, None, errors

    snap: dict[str, Any] = {"period_type": ptype, "start_date": None, "end_date": None}
    resolved_start, resolved_end = resolve_optimizer_date_range(snap, now=now)
    if resolved_start is None and resolved_end is None:
        errors["period"] = f"período não suportado: {ptype}"
    return ptype, resolved_start, resolved_end, errors
