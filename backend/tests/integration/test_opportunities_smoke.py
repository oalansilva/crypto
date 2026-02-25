from __future__ import annotations

import os
from time import perf_counter

from fastapi import FastAPI
import httpx

from app.routes import opportunity_routes


async def test_opportunities_tier_all_smoke_performance(monkeypatch):
    max_seconds = float(os.getenv("OPPORTUNITIES_SMOKE_MAX_SECONDS", "2.0"))

    captured = {"tier": None}

    class _FakeOpportunityService:
        def get_opportunities(self, tier_filter=None):
            captured["tier"] = tier_filter
            return []

    monkeypatch.setattr(opportunity_routes, "OpportunityService", _FakeOpportunityService)

    test_app = FastAPI()
    test_app.include_router(opportunity_routes.router)

    transport = httpx.ASGITransport(app=test_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        start = perf_counter()
        response = await client.get("/api/opportunities/?tier=all")
        elapsed = perf_counter() - start

    assert response.status_code == 200, response.text
    assert response.json() == []
    assert captured["tier"] == "all"
    assert elapsed <= max_seconds, f"/api/opportunities took {elapsed:.3f}s (> {max_seconds:.3f}s)"
