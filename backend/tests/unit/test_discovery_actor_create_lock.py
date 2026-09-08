"""Unit tests for the actor create-lock no-op branches (card #837)."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock

from app.services.discovery_service import _acquire_actor_create_lock


class _RaisingBind:
    """Fake session whose ``bind`` access raises (covers the except branch)."""

    @property
    def bind(self):  # noqa: D102
        raise RuntimeError("no bind available")


def test_acquire_lock_returns_when_bind_raises():
    _acquire_actor_create_lock(_RaisingBind(), actor="alan")  # must not raise


def test_acquire_lock_noop_for_non_postgres_dialect():
    execute = Mock()
    db = SimpleNamespace(
        bind=SimpleNamespace(dialect=SimpleNamespace(name="sqlite")),
        execute=execute,
    )

    _acquire_actor_create_lock(db, actor="alan")

    execute.assert_not_called()
