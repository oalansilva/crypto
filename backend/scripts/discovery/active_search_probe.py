"""Read-only probe: is there an active Discovery search in this environment? (#1110)

Active (blocks applying the PROD ceiling) means any of:
  * a sweep in ``running`` or ``cancelling``;
  * a combination holding a lease that is still valid on the PostgreSQL clock;
  * a ``discovery_attempts`` row with ``state='running'`` and no ``finished_at``.

Sweeps in ``pending`` (queued, nothing executing) and ``paused`` are listed but
never block. Fail closed: a query error counts as active.

Exit codes: 0 idle, 3 active (or error). Prints JSON with the sweeps found.
Run it with the backend environment of the database to inspect, for example:
``PYTHONPATH=<root>:<root>/backend backend/.venv/bin/python backend/scripts/discovery/active_search_probe.py``
"""

from __future__ import annotations

import json
import sys

EXIT_IDLE = 0
EXIT_ACTIVE = 3
ACTIVE_SWEEP_STATES = ("running", "cancelling")
LISTED_IDLE_STATES = ("pending", "paused")


def probe(db):
    """Return the probe report for an open SQLAlchemy session (read-only)."""
    from sqlalchemy import func

    from app.models_discovery import DiscoveryAttempt, DiscoveryCombination, DiscoverySweep
    from app.services.discovery_recovery import now

    stamp = now(db)  # PostgreSQL clock_timestamp(), never the host clock.
    reasons: dict[str, set[str]] = {}

    def flag(sweep_id, reason):
        reasons.setdefault(sweep_id, set()).add(reason)

    for (sweep_id,) in db.query(DiscoverySweep.id).filter(
        DiscoverySweep.state.in_(ACTIVE_SWEEP_STATES)
    ):
        flag(sweep_id, "sweep_state")
    for (sweep_id,) in (
        db.query(DiscoveryCombination.sweep_id)
        .filter(
            DiscoveryCombination.lease_owner.isnot(None),
            DiscoveryCombination.lease_expires_at > stamp,
        )
        .distinct()
    ):
        flag(sweep_id, "valid_lease")
    for (sweep_id,) in (
        db.query(DiscoveryCombination.sweep_id)
        .join(
            DiscoveryAttempt,
            DiscoveryAttempt.combination_id == DiscoveryCombination.id,
        )
        .filter(DiscoveryAttempt.state == "running", DiscoveryAttempt.finished_at.is_(None))
        .distinct()
    ):
        flag(sweep_id, "running_attempt")

    wanted = set(reasons)
    listed = db.query(DiscoverySweep).filter(
        DiscoverySweep.id.in_(wanted) | DiscoverySweep.state.in_(LISTED_IDLE_STATES)
    )
    sweeps = []
    for sweep in listed.order_by(DiscoverySweep.created_at, DiscoverySweep.id):
        sweeps.append(
            {
                "id": sweep.id,
                "state": sweep.state,
                "active": sweep.id in reasons,
                "reasons": sorted(reasons.get(sweep.id, ())),
                "processed": sweep.processed,
                "total": sweep.total,
            }
        )
    # A lease/attempt may reference a sweep id that no longer has a sweep row:
    # still active, never silently dropped.
    known = {item["id"] for item in sweeps}
    for sweep_id in sorted(wanted - known):
        sweeps.append(
            {
                "id": sweep_id,
                "state": "unknown",
                "active": True,
                "reasons": sorted(reasons[sweep_id]),
                "processed": None,
                "total": None,
            }
        )
    clock = db.query(func.clock_timestamp()).scalar()
    return {
        "active": bool(reasons),
        "error": None,
        "checked_at": clock.isoformat() if clock is not None else None,
        "sweeps": sweeps,
    }


def report_for(session_factory=None):
    """Run the probe; any failure yields an active report (fail closed)."""
    try:
        if session_factory is None:
            from app.database import SessionLocal as session_factory
        with session_factory() as db:
            return probe(db)
    except Exception as exc:  # noqa: BLE001 - every failure must read as active
        return {
            "active": True,
            "error": f"{type(exc).__name__}: {exc}"[:300],
            "checked_at": None,
            "sweeps": [],
        }


def main():
    report = report_for()
    print(json.dumps(report, sort_keys=True))
    return EXIT_ACTIVE if report["active"] else EXIT_IDLE


if __name__ == "__main__":
    sys.exit(main())
