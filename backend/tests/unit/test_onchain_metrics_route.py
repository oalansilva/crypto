from __future__ import annotations

from datetime import datetime, timezone

import pytest
from fastapi import HTTPException

from app.routes import onchain_metrics
from app.services.glassnode_service import GlassnodeConfigError, GlassnodeRateLimitError


class FakeGlassnodeService:
    async def fetch_metrics(self, asset: str, interval: str, since: int | None, until: int | None):
        assert asset == "BTC"
        assert interval == "24h"
        assert since == 1
        assert until == 2
        now = datetime(2026, 4, 24, tzinfo=timezone.utc)
        return {
            "asset": "BTC",
            "interval": "24h",
            "cached": False,
            "metrics": [
                {
                    "metric": "mvrv",
                    "asset": "BTC",
                    "interval": "24h",
                    "endpoint": "/v1/metrics/market/mvrv",
                    "points": [{"t": 1, "v": 2.0}],
                    "latest": {"t": 1, "v": 2.0},
                    "fetched_at": now,
                    "cached_until": now,
                    "cached": False,
                }
            ],
        }


class FakeExchangeFlowService:
    async def fetch_exchange_flows(self, asset: str, window: str):
        assert asset == "BTC"
        assert window == "7d"
        now = datetime(2026, 4, 24, tzinfo=timezone.utc)
        return {
            "asset": "BTC",
            "window": "7d",
            "interval": "24h",
            "since": 1,
            "until": 2,
            "cached": True,
            "total": {"inflow": 100.0, "outflow": 40.0, "netflow": 60.0},
            "exchanges": [
                {"exchange": "binance", "inflow": 100.0, "outflow": 40.0, "netflow": 60.0}
            ],
            "sources": {
                "inflow": {
                    "endpoint": "/v1/metrics/transactions/transfers_volume_to_exchanges_sum",
                    "points": 1,
                    "cached": True,
                    "fetched_at": now,
                    "cached_until": now,
                }
            },
        }


@pytest.mark.asyncio
async def test_glassnode_onchain_route_returns_service_payload(monkeypatch) -> None:
    monkeypatch.setattr(onchain_metrics, "get_glassnode_service", lambda: FakeGlassnodeService())

    payload = await onchain_metrics.get_glassnode_onchain_metrics(
        asset="BTC",
        interval="24h",
        since=1,
        until=2,
    )

    assert payload["asset"] == "BTC"
    assert payload["metrics"][0]["metric"] == "mvrv"


@pytest.mark.asyncio
async def test_glassnode_exchange_flows_route_returns_service_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        onchain_metrics,
        "get_exchange_flow_service",
        lambda: FakeExchangeFlowService(),
    )

    payload = await onchain_metrics.get_glassnode_exchange_flows(asset="BTC", window="7d")

    assert payload["asset"] == "BTC"
    assert payload["window"] == "7d"
    assert payload["total"]["netflow"] == 60.0
    assert payload["exchanges"][0]["exchange"] == "binance"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("exc", "status_code"),
    [
        (ValueError("bad asset"), 400),
        (GlassnodeConfigError("missing key"), 503),
        (GlassnodeRateLimitError("rate limited"), 429),
    ],
)
async def test_glassnode_onchain_route_maps_service_errors(
    monkeypatch, exc: Exception, status_code: int
) -> None:
    class FailingGlassnodeService:
        async def fetch_metrics(self, *_args, **_kwargs):
            raise exc

    monkeypatch.setattr(
        onchain_metrics,
        "get_glassnode_service",
        lambda: FailingGlassnodeService(),
    )

    with pytest.raises(HTTPException) as raised:
        await onchain_metrics.get_glassnode_onchain_metrics(asset="BTC")

    assert raised.value.status_code == status_code


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("exc", "status_code"),
    [
        (ValueError("bad window"), 400),
        (GlassnodeConfigError("missing key"), 503),
        (GlassnodeRateLimitError("rate limited"), 429),
    ],
)
async def test_glassnode_exchange_flows_route_maps_service_errors(
    monkeypatch, exc: Exception, status_code: int
) -> None:
    class FailingExchangeFlowService:
        async def fetch_exchange_flows(self, *_args, **_kwargs):
            raise exc

    monkeypatch.setattr(
        onchain_metrics,
        "get_exchange_flow_service",
        lambda: FailingExchangeFlowService(),
    )

    with pytest.raises(HTTPException) as raised:
        await onchain_metrics.get_glassnode_exchange_flows(asset="BTC")

    assert raised.value.status_code == status_code
