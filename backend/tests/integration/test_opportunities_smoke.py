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


async def test_opportunities_route_keeps_signal_history_in_payload(monkeypatch):
    sample_payload = [{
        "id": 5,
        "symbol": "BTC/USDT",
        "timeframe": "1d",
        "template_name": "multi_ma_crossover",
        "name": "BTC Trend History",
        "notes": None,
        "tier": 1,
        "parameters": {},
        "is_holding": True,
        "distance_to_next_status": 0.88,
        "next_status_label": "exit",
        "indicator_values": {"short": 71346.57},
        "indicator_values_candle_time": "2026-04-15T00:00:00+00:00",
        "signal_history": [
            {
                "timestamp": "2026-04-10T00:00:00+00:00",
                "signal": 1,
                "type": "entry",
                "reason": "entry",
                "price": 70210.15,
            },
            {
                "timestamp": "2026-04-13T00:00:00+00:00",
                "signal": -1,
                "type": "exit",
                "reason": "exit_logic",
                "price": 72150.42,
            },
        ],
        "entry_price": 73980.37,
        "stop_price": 70873.19,
        "distance_to_stop_pct": 5.07,
        "status": "HOLDING",
        "badge": "info",
        "message": "Em Hold. Distância para saída: 0.88%",
        "last_price": 74924.0,
        "timestamp": "2026-04-16T00:00:00Z",
        "details": {},
    }]

    class _FakeOpportunityService:
        def get_opportunities(self, user_id, tier_filter=None):
            return sample_payload

    monkeypatch.setattr(opportunity_routes, "OpportunityService", _FakeOpportunityService)

    response = await opportunity_routes.get_opportunities(tier="all", current_user_id="user-a")

    assert len(response) == 1
    assert response[0]["signal_history"][0]["type"] == "entry"
    assert response[0]["signal_history"][1]["type"] == "exit"
    assert response[0]["signal_history"][1]["reason"] == "exit_logic"
