from __future__ import annotations

from datetime import datetime, timezone

from app.services import sweep_period


def test_validate_custom_period_messages():
    now = datetime(2026, 8, 15, tzinfo=timezone.utc)
    assert (
        sweep_period.validate_custom_period(None, None, now=now)
        == "Seleccione Data Inicial e Data Final."
    )
    assert (
        sweep_period.validate_custom_period("2026-01-01", None, now=now) == "Seleccione Data Final."
    )
    assert (
        sweep_period.validate_custom_period(None, "2026-01-01", now=now)
        == "Seleccione Data Inicial."
    )
    assert (
        sweep_period.validate_custom_period("2026-02-01", "2026-01-01", now=now)
        == "Data Inicial não pode ser depois da Data Final."
    )
    assert (
        sweep_period.validate_custom_period("2026-01-01", "2026-08-16", now=now)
        == "Data Final não pode ser depois de hoje."
    )
    assert sweep_period.validate_custom_period("2026-01-01", "2026-08-15", now=now) is None


def test_normalize_sweep_period_resolves_fixed_window():
    now = datetime(2026, 8, 15, tzinfo=timezone.utc)
    ptype, start, end, errors = sweep_period.normalize_sweep_period(
        period_type="15d", start_date=None, end_date=None, now=now
    )
    assert errors == {}
    assert ptype == "15d"
    assert start == "2026-07-31"
    assert end == "2026-08-15"
