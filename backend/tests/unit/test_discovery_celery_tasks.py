from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from app.tasks import discovery_celery_tasks, discovery_tasks


def test_resolve_optimizer_date_range_maps_discovery_periods():
    now = datetime(2026, 8, 15, 12, 0, tzinfo=timezone.utc)

    assert discovery_tasks.resolve_optimizer_date_range({"period_type": "6m"}, now) == (
        "2026-02-15",
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


def test_orchestrator_reconciles_progress_after_each_combination(monkeypatch):
    events: list[str] = []
    combinations = [SimpleNamespace(id="c1"), SimpleNamespace(id="c2")]

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

    class FakeDb:
        def close(self):
            events.append("close")

    monkeypatch.setattr(discovery_celery_tasks, "DiscoveryService", FakeService)
    monkeypatch.setattr(discovery_celery_tasks, "SessionLocal", FakeDb)
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
