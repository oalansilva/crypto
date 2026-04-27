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


class FakeMiningMetricService:
    async def fetch_mining_metrics(
        self,
        asset: str,
        interval: str,
        since: int | None,
        until: int | None,
    ):
        assert asset == "BTC"
        assert interval == "24h"
        assert since == 1
        assert until == 2
        now = datetime(2026, 4, 27, tzinfo=timezone.utc)
        return {
            "asset": "BTC",
            "interval": "24h",
            "since": 1,
            "until": 2,
            "cached": False,
            "metrics": [
                {
                    "metric": "hash_rate",
                    "asset": "BTC",
                    "interval": "24h",
                    "endpoint": "/v1/metrics/mining/hash_rate_mean",
                    "points": [{"t": 1, "v": 100.0}],
                    "latest": {"t": 1, "v": 100.0},
                    "ath": {"t": 1, "v": 100.0},
                    "drop_pct_vs_ma_7d": None,
                    "alerts": [],
                    "fetched_at": now,
                    "cached_until": now,
                    "cached": False,
                }
            ],
        }


class FakeSupplyDistributionService:
    async def fetch_supply_distribution(self, asset: str, basis: str, window: str):
        assert asset == "BTC"
        assert basis == "entity"
        assert window == "7d"
        now = datetime(2026, 4, 27, tzinfo=timezone.utc)
        return {
            "asset": "BTC",
            "basis": "entity",
            "window": "7d",
            "interval": "24h",
            "since": 1,
            "until": 2,
            "cached": True,
            "bands": [
                {
                    "id": "1k_10k",
                    "metric": "entity_supply_1k_10k",
                    "label": "1k - 10k BTC",
                    "min_btc": 1000.0,
                    "max_btc": 10000.0,
                    "latest": 2600.0,
                    "latest_timestamp": 2,
                    "previous": 1000.0,
                    "previous_timestamp": 1,
                    "change_abs": 1600.0,
                    "change_pct": 160.0,
                    "share_pct": 40.0,
                }
            ],
            "cohorts": {
                "whales": {
                    "id": "whales",
                    "label": "Whales (>= 1000 BTC)",
                    "band_ids": ["1k_10k"],
                    "latest": 2600.0,
                    "latest_timestamp": 2,
                    "previous": 1000.0,
                    "previous_timestamp": 1,
                    "change_abs": 1600.0,
                    "change_pct": 160.0,
                    "share_pct": 40.0,
                }
            },
            "whale_movement": {
                "threshold_btc": 1000.0,
                "change_abs": 1600.0,
                "direction": "accumulation",
                "alert": True,
            },
            "alerts": [
                {
                    "type": "whale-alert",
                    "threshold_btc": 1000.0,
                    "change_abs": 1600.0,
                    "direction": "accumulation",
                    "window": "7d",
                }
            ],
            "sources": {
                "entity_supply_1k_10k": {
                    "endpoint": "/v1/metrics/entities/supply_balance_1k_10k",
                    "points": 2,
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
async def test_glassnode_mining_metrics_route_returns_service_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        onchain_metrics,
        "get_mining_metric_service",
        lambda: FakeMiningMetricService(),
    )

    payload = await onchain_metrics.get_glassnode_mining_metrics(
        asset="BTC",
        interval="24h",
        since=1,
        until=2,
    )

    assert payload["asset"] == "BTC"
    assert payload["metrics"][0]["metric"] == "hash_rate"
    assert payload["metrics"][0]["ath"] == {"t": 1, "v": 100.0}


@pytest.mark.asyncio
async def test_glassnode_supply_distribution_route_returns_service_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        onchain_metrics,
        "get_supply_distribution_service",
        lambda: FakeSupplyDistributionService(),
    )

    payload = await onchain_metrics.get_glassnode_supply_distribution(
        asset="BTC",
        basis="entity",
        window="7d",
    )

    assert payload["asset"] == "BTC"
    assert payload["basis"] == "entity"
    assert payload["bands"][0]["id"] == "1k_10k"
    assert payload["cohorts"]["whales"]["change_abs"] == 1600.0
    assert payload["alerts"][0]["type"] == "whale-alert"


@pytest.mark.asyncio
async def test_glassnode_mining_metrics_route_rejects_non_daily_interval(monkeypatch) -> None:
    class RejectingMiningMetricService:
        async def fetch_mining_metrics(self, *_args, **_kwargs):
            raise ValueError("Unsupported mining metric interval '1h'. Supported: 24h")

    monkeypatch.setattr(
        onchain_metrics,
        "get_mining_metric_service",
        lambda: RejectingMiningMetricService(),
    )

    with pytest.raises(HTTPException) as raised:
        await onchain_metrics.get_glassnode_mining_metrics(asset="BTC", interval="1h")

    assert raised.value.status_code == 400


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
        (ValueError("bad asset"), 400),
        (GlassnodeConfigError("missing key"), 503),
        (GlassnodeRateLimitError("rate limited"), 429),
    ],
)
async def test_glassnode_mining_metrics_route_maps_service_errors(
    monkeypatch, exc: Exception, status_code: int
) -> None:
    class FailingMiningMetricService:
        async def fetch_mining_metrics(self, *_args, **_kwargs):
            raise exc

    monkeypatch.setattr(
        onchain_metrics,
        "get_mining_metric_service",
        lambda: FailingMiningMetricService(),
    )

    with pytest.raises(HTTPException) as raised:
        await onchain_metrics.get_glassnode_mining_metrics(asset="BTC")

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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("exc", "status_code"),
    [
        (ValueError("bad basis"), 400),
        (GlassnodeConfigError("missing key"), 503),
        (GlassnodeRateLimitError("rate limited"), 429),
    ],
)
async def test_glassnode_supply_distribution_route_maps_service_errors(
    monkeypatch, exc: Exception, status_code: int
) -> None:
    class FailingSupplyDistributionService:
        async def fetch_supply_distribution(self, *_args, **_kwargs):
            raise exc

    monkeypatch.setattr(
        onchain_metrics,
        "get_supply_distribution_service",
        lambda: FailingSupplyDistributionService(),
    )

    with pytest.raises(HTTPException) as raised:
        await onchain_metrics.get_glassnode_supply_distribution(asset="BTC")

    assert raised.value.status_code == status_code
