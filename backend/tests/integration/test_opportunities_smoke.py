from __future__ import annotations

import asyncio
import os
from time import perf_counter

from app.routes import opportunity_routes


async def test_opportunities_tier_all_smoke_performance(monkeypatch):
    max_seconds = float(os.getenv("OPPORTUNITIES_SMOKE_MAX_SECONDS", "2.0"))

    captured = {"tier": None, "user_id": None}

    class _FakeOpportunityService:
        def get_opportunities(self, user_id, tier_filter=None):
            captured["user_id"] = user_id
            captured["tier"] = tier_filter
            return []

    monkeypatch.setattr(opportunity_routes, "OpportunityService", _FakeOpportunityService)

    start = perf_counter()
    response = await opportunity_routes.get_opportunities(tier="all", current_user_id="user-a")
    elapsed = perf_counter() - start

    assert response == []
    assert captured["user_id"] == "user-a"
    assert captured["tier"] == "all"
    assert elapsed <= max_seconds, f"/api/opportunities took {elapsed:.3f}s (> {max_seconds:.3f}s)"
