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
    assert captured["tier"] == "1,2,3"
    assert elapsed <= max_seconds, f"/api/opportunities took {elapsed:.3f}s (> {max_seconds:.3f}s)"


async def test_opportunities_route_preserves_admin_tier_all(monkeypatch):
    captured = {"tier": None}

    class _FakeOpportunityService:
        def get_opportunities(self, user_id, tier_filter=None):
            captured["tier"] = tier_filter
            return []

    monkeypatch.setattr(opportunity_routes, "OpportunityService", _FakeOpportunityService)
    monkeypatch.setattr(
        opportunity_routes, "can_view_strategy_secrets", lambda *_args, **_kwargs: True
    )

    response = await opportunity_routes.get_opportunities(tier="all", current_user_id="admin-user")

    assert response == []
    assert captured["tier"] == "all"


async def test_opportunities_route_blocks_common_user_untiered_filter(monkeypatch):
    captured = {"tier": None}

    class _FakeOpportunityService:
        def get_opportunities(self, user_id, tier_filter=None):
            captured["tier"] = tier_filter
            return []

    monkeypatch.setattr(opportunity_routes, "OpportunityService", _FakeOpportunityService)
    monkeypatch.setattr(
        opportunity_routes, "can_view_strategy_secrets", lambda *_args, **_kwargs: False
    )

    response = await opportunity_routes.get_opportunities(
        tier="none", current_user_id="common-user"
    )

    assert response == []
    assert captured["tier"] == "999"


async def test_opportunities_route_keeps_signal_history_in_payload(monkeypatch):
    sample_payload = [
        {
            "id": 5,
            "symbol": "BTC/USDT",
            "asset_type": "crypto",
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
        }
    ]

    class _FakeOpportunityService:
        def get_opportunities(self, user_id, tier_filter=None):
            return sample_payload

    monkeypatch.setattr(opportunity_routes, "OpportunityService", _FakeOpportunityService)

    response = await opportunity_routes.get_opportunities(tier="all", current_user_id="user-a")

    assert len(response) == 1
    assert response[0]["asset_type"] == "crypto"
    assert response[0]["template_name"] == "Estratégia protegida"
    assert response[0]["strategy_display_name"] == "Multi MA Crossover"
    assert response[0]["parameters"] == {}
    assert response[0]["indicator_values"] is None
    assert response[0]["details"] == {}
    assert response[0]["is_strategy_protected"] is True
    assert response[0]["signal_history"][0]["type"] == "entry"
    assert response[0]["signal_history"][1]["type"] == "exit"
    assert response[0]["signal_history"][1]["reason"] == "exit"


async def test_opportunities_route_keeps_admin_strategy_details(monkeypatch):
    sample_payload = [
        {
            "id": 5,
            "symbol": "BTC/USDT",
            "asset_type": "crypto",
            "timeframe": "1d",
            "template_name": "multi_ma_crossover",
            "name": "BTC Trend History",
            "notes": None,
            "tier": 1,
            "parameters": {"ema_short": 9, "sma_long": 50},
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
                }
            ],
            "entry_price": 73980.37,
            "stop_price": 70873.19,
            "distance_to_stop_pct": 5.07,
            "status": "HOLDING",
            "badge": "info",
            "message": "Em Hold. Distância para saída: 0.88%",
            "last_price": 74924.0,
            "timestamp": "2026-04-16T00:00:00Z",
            "details": {"exit_analysis": {"distance": 0.88}},
        }
    ]

    class _FakeOpportunityService:
        def get_opportunities(self, user_id, tier_filter=None):
            return sample_payload

    monkeypatch.setattr(opportunity_routes, "OpportunityService", _FakeOpportunityService)
    monkeypatch.setattr(
        opportunity_routes, "can_view_strategy_secrets", lambda *_args, **_kwargs: True
    )

    response = await opportunity_routes.get_opportunities(tier="all", current_user_id="admin-user")

    assert response[0]["template_name"] == "multi_ma_crossover"
    assert response[0]["parameters"] == {"ema_short": 9, "sma_long": 50}
    assert response[0]["indicator_values"] == {"short": 71346.57}
    assert response[0]["details"] == {"exit_analysis": {"distance": 0.88}}
    assert response[0]["is_strategy_protected"] is False


async def test_opportunities_route_redacts_curated_fallback_for_common_user(monkeypatch):
    captured = {"user_id": None}

    class _FakeOpportunityService:
        def get_opportunities(self, user_id, tier_filter=None):
            captured["user_id"] = user_id
            return [
                {
                    "id": 9,
                    "symbol": "BTC/USDT",
                    "asset_type": "crypto",
                    "timeframe": "1d",
                    "template_name": "secret_admin_strategy",
                    "name": "Admin curated secret",
                    "notes": "admin note with strategy context",
                    "tier": 1,
                    "parameters": {"ema_short": 9},
                    "is_holding": False,
                    "distance_to_next_status": 1.25,
                    "next_status_label": "entry",
                    "indicator_values": {"short": 70100.0},
                    "indicator_values_candle_time": "2026-04-15T00:00:00+00:00",
                    "signal_history": [],
                    "entry_price": None,
                    "stop_price": None,
                    "distance_to_stop_pct": None,
                    "status": "WAITING",
                    "badge": "neutral",
                    "message": "secret context",
                    "last_price": 70000.0,
                    "timestamp": "2026-04-16T00:00:00Z",
                    "details": {"entry_analysis": {"distance": 1.25}},
                    "is_curated_fallback": True,
                }
            ]

    monkeypatch.setattr(opportunity_routes, "OpportunityService", _FakeOpportunityService)
    monkeypatch.setattr(
        opportunity_routes, "can_view_strategy_secrets", lambda *_args, **_kwargs: False
    )

    response = await opportunity_routes.get_opportunities(tier="all", current_user_id="common-user")

    assert captured["user_id"] == "common-user"
    assert response[0]["template_name"] == "Estratégia protegida"
    assert response[0]["strategy_display_name"] == "Secret Admin Strategy"
    assert response[0]["name"] == "Estratégia protegida"
    assert response[0]["notes"] is None
    assert response[0]["parameters"] == {}
    assert response[0]["indicator_values"] is None
    assert response[0]["details"] == {}
    assert response[0]["is_strategy_protected"] is True
