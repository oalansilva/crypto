from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.tasks import discovery_celery_tasks, discovery_tasks

CALENDAR_CASES = json.loads(
    (Path(__file__).resolve().parents[1] / "fixtures/sweep-calendar-parity.json").read_text()
)


@pytest.mark.parametrize(
    "reference,period,start_date",
    [
        (case["reference"], period, start_date)
        for case in CALENDAR_CASES
        for period, start_date in case["starts"].items()
    ],
)
def test_resolve_optimizer_date_range_calendar_parity(reference, period, start_date):
    now = datetime.fromisoformat(f"{reference}T23:59:59+00:00")
    expected = (start_date, reference)
    assert discovery_tasks.resolve_optimizer_date_range({"period_type": period}, now) == expected
    # Frontend-resolved dates in a snapshot remain authoritative after the clock moves.
    assert (
        discovery_tasks.resolve_optimizer_date_range(
            {"period_type": period, "start_date": start_date, "end_date": reference},
            datetime(2030, 1, 1, tzinfo=timezone.utc),
        )
        == expected
    )


def test_resolve_optimizer_date_range_maps_discovery_periods():
    now = datetime(2026, 8, 15, 12, 0, tzinfo=timezone.utc)

    assert discovery_tasks.resolve_optimizer_date_range({"period_type": "15d"}, now) == (
        "2026-07-31",
        "2026-08-15",
    )
    assert discovery_tasks.resolve_optimizer_date_range({"period_type": "1m"}, now) == (
        "2026-07-15",
        "2026-08-15",
    )
    assert discovery_tasks.resolve_optimizer_date_range({"period_type": "3m"}, now) == (
        "2026-05-15",
        "2026-08-15",
    )
    assert discovery_tasks.resolve_optimizer_date_range({"period_type": "6m"}, now) == (
        "2026-02-15",
        "2026-08-15",
    )
    assert discovery_tasks.resolve_optimizer_date_range({"period_type": "1y"}, now) == (
        "2025-08-15",
        "2026-08-15",
    )
    assert discovery_tasks.resolve_optimizer_date_range({"period_type": "2y"}, now) == (
        "2024-08-15",
        "2026-08-15",
    )
    assert discovery_tasks.resolve_optimizer_date_range({"period_type": "all"}, now) == (
        None,
        None,
    )
    assert discovery_tasks.resolve_optimizer_date_range(
        {"period_type": "6m", "start_date": "2025-01-01", "end_date": "2025-12-31"},
        now,
    ) == ("2025-01-01", "2025-12-31")


@pytest.mark.parametrize(
    "snapshot,expected",
    [
        (
            {"period_type": "custom", "start_date": "2026-01-01", "end_date": "2026-06-01"},
            ("2026-01-01", "2026-06-01"),
        ),
        ({"period_type": "custom"}, (None, None)),
        ({"period_type": "custom", "start_date": "2026-01-01"}, ("2026-01-01", None)),
        ({"period_type": "custom", "end_date": "2026-06-01"}, (None, "2026-06-01")),
        ({"period_type": "all"}, (None, None)),
        ({}, (None, None)),
    ],
)
def test_resolve_optimizer_date_range_other_modes(snapshot, expected):
    assert (
        discovery_tasks.resolve_optimizer_date_range(
            snapshot, datetime(2026, 8, 15, tzinfo=timezone.utc)
        )
        == expected
    )


@pytest.mark.parametrize(
    "reference,period,start_date",
    [("2026-03-31", "1m", "2026-02-28"), ("2024-02-29", "1y", "2023-02-28")],
)
@pytest.mark.parametrize("explicit_dates", [False, True])
def test_run_combination_passes_calendar_window_to_optimizer(
    monkeypatch, reference, period, start_date, explicit_dates
):
    """Card #1093: the calendar window is frozen at claim time and the supervised
    run (optimizer boundary) receives exactly the frozen window."""
    from app.services import discovery_recovery, discovery_supervisor
    from app.services.combo_service import ComboService

    snapshot = {"period_type": period}
    if explicit_dates:
        snapshot.update(start_date=start_date, end_date=reference)
    sweep = SimpleNamespace(state="running", snapshot=snapshot)
    stamp = datetime.fromisoformat(f"{reference}T00:30:00")  # DB clock, naive UTC
    row = SimpleNamespace(
        id="calendar-combination",
        sweep_id="calendar-sweep",
        template_id="template",
        symbol="BTC/USDT",
        timeframe="1d",
        direction="long",
        state="pending",
        attempts=0,
        lease_generation=0,
        lease_owner=None,
        lease_expires_at=None,
        heartbeat_at=None,
        progress_at=None,
        next_attempt_at=None,
        updated_at=None,
        input_snapshot=None,
    )
    added = []
    db = SimpleNamespace(add=added.append, rollback=lambda: None)
    monkeypatch.setattr(
        discovery_recovery, "circuit", lambda _db: SimpleNamespace(opened_at=None, environment="t")
    )
    monkeypatch.setattr(ComboService, "get_template_metadata", lambda *_: {"name": "template"})
    assert discovery_recovery.claim_attempt(db, sweep, row, stamp)
    frozen = row.input_snapshot
    assert (frozen["start_date"], frozen["end_date"]) == (start_date, reference)

    # Stop at the optimizer boundary: this test must not execute a backtest or
    # exercise unrelated result/ranking persistence.
    class OptimizerBoundary(BaseException):
        pass

    supervised_calls = []

    def run_supervised(config, beat):
        supervised_calls.append(config)
        raise OptimizerBoundary()

    monkeypatch.setattr(discovery_supervisor, "run_supervised", run_supervised)
    monkeypatch.setattr(
        discovery_recovery, "locked_possession", lambda _db, _token: (sweep, row, stamp)
    )
    with pytest.raises(OptimizerBoundary):
        discovery_tasks.run_combination(db, row, row.lease_owner)
    assert len(supervised_calls) == 1
    call = supervised_calls[0]
    assert (call["start_date"], call["end_date"]) == (start_date, reference)


def test_orchestrator_reconciles_progress_after_each_combination(monkeypatch):
    events: list[str] = []
    combinations = [
        SimpleNamespace(id="c1", lease_owner="o1"),
        SimpleNamespace(id="c2", lease_owner="o2"),
    ]

    class FakeService:
        def claim_combinations(self, sweep_id, owner, db):
            return combinations

        def release_expired_leases(self, db):
            events.append("release")

        def count_claimable(self, sweep_id, db):
            return 0

        def ack_outbox(self, sweep_id, generation, db):
            events.append("ack")
            return 1

        def ensure_sweep_wakeup(self, db, sweep_id, sweep=None, rotate_from=None):
            events.append("ensure")
            return {}

    class FakeDb:
        def query(self, *args, **kwargs):
            # Probe de estado do sweep (card #853): sem sweep → caminho normal.
            class _EmptyQuery:
                def filter(self, *args, **kwargs):
                    return self

                def first(self):
                    return None

            return _EmptyQuery()

        def close(self):
            events.append("close")

    monkeypatch.setattr(discovery_celery_tasks, "DiscoveryService", FakeService)
    monkeypatch.setattr(discovery_celery_tasks, "SessionLocal", FakeDb)
    # Lease/attempt reconciliation needs PostgreSQL clock; covered by
    # integration/test_discovery_memory_recovery.py.
    monkeypatch.setattr(
        "app.services.discovery_recovery.reconcile_expired", lambda db, sweep_id: None
    )
    monkeypatch.setattr(
        discovery_tasks,
        "run_combination",
        lambda db, combination, owner: events.append(f"run:{combination.id}"),
    )
    monkeypatch.setattr(
        discovery_tasks,
        "reconcile_sweep",
        lambda sweep_id, db: events.append("reconcile") or {"state": "completed"},
    )

    result = discovery_celery_tasks.run_sweep_orchestrator("sweep-1", 1)

    assert result == {"state": "completed"}
    assert events == [
        "run:c1",
        "reconcile",
        "run:c2",
        "reconcile",
        "release",
        "reconcile",
        "ack",
        "close",
    ]


def test_orchestrator_rotates_wakeup_before_ack(monkeypatch):
    events: list[str] = []
    combinations = [SimpleNamespace(id="c1", lease_owner="o1")]

    class FakeService:
        def claim_combinations(self, sweep_id, owner, db):
            return combinations

        def release_expired_leases(self, db):
            events.append("release")

        def count_claimable(self, sweep_id, db):
            return 3

        def ensure_sweep_wakeup(self, db, sweep_id, sweep=None, rotate_from=None):
            events.append(f"ensure:{rotate_from}")
            return {"created": True}

        def ack_outbox(self, sweep_id, generation, db):
            events.append("ack")
            return 1

    class FakeDb:
        def query(self, *args, **kwargs):
            # Probe de estado do sweep (card #853): sem sweep → caminho normal.
            class _EmptyQuery:
                def filter(self, *args, **kwargs):
                    return self

                def first(self):
                    return None

            return _EmptyQuery()

        def close(self):
            events.append("close")

    monkeypatch.setattr(discovery_celery_tasks, "DiscoveryService", FakeService)
    monkeypatch.setattr(discovery_celery_tasks, "SessionLocal", FakeDb)
    # Lease/attempt reconciliation needs PostgreSQL clock; covered by
    # integration/test_discovery_memory_recovery.py.
    monkeypatch.setattr(
        "app.services.discovery_recovery.reconcile_expired", lambda db, sweep_id: None
    )
    monkeypatch.setattr(
        discovery_tasks,
        "run_combination",
        lambda db, combination, owner: events.append(f"run:{combination.id}"),
    )
    monkeypatch.setattr(
        discovery_tasks,
        "reconcile_sweep",
        lambda sweep_id, db: events.append("reconcile") or {"state": "running"},
    )

    discovery_celery_tasks.run_sweep_orchestrator("sweep-1", 4)
    assert events == [
        "run:c1",
        "reconcile",
        "release",
        "reconcile",
        "ensure:4",
        "ack",
        "close",
    ]
