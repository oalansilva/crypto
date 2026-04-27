from __future__ import annotations

from datetime import datetime, timezone

import httpx
import pytest

from app.services.glassnode_service import (
    GLASSNODE_MINING_METRICS,
    GLASSNODE_METRICS,
    GLASSNODE_SUPPLY_DISTRIBUTION_METRICS,
    GlassnodeConfigError,
    GlassnodeRateLimitError,
    GlassnodeService,
)


class FakeClock:
    def __init__(self) -> None:
        self.value = 1000.0

    def monotonic(self) -> float:
        return self.value

    async def sleep(self, seconds: float) -> None:
        self.value += seconds


class FakeGlassnodeClient:
    def __init__(self, status_code: int = 200) -> None:
        self.status_code = status_code
        self.calls: list[dict] = []

    async def get(self, url: str, params=None, headers=None):
        self.calls.append({"url": url, "params": params, "headers": headers})
        return httpx.Response(
            self.status_code,
            json=[{"t": 1726790400, "v": 1.23}],
            request=httpx.Request("GET", url),
        )


@pytest.mark.asyncio
async def test_fetch_metric_requires_configured_api_key_before_network_call() -> None:
    client = FakeGlassnodeClient()
    service = GlassnodeService(api_key="", client=client, rate_limit_per_minute=0)

    with pytest.raises(GlassnodeConfigError):
        await service.fetch_metric("mvrv", "BTC")

    assert client.calls == []


@pytest.mark.asyncio
async def test_fetch_metric_uses_api_key_header_and_glassnode_params() -> None:
    client = FakeGlassnodeClient()
    service = GlassnodeService(api_key="secret", client=client, rate_limit_per_minute=0)

    result = await service.fetch_metric("mvrv", "BTC", since=1, until=2)

    assert result.asset == "BTC"
    assert result.metric == "mvrv"
    assert result.latest == {"t": 1726790400, "v": 1.23}
    assert client.calls == [
        {
            "url": "https://api.glassnode.com/v1/metrics/market/mvrv",
            "params": {"a": "BTC", "i": "24h", "f": "json", "s": 1, "u": 2},
            "headers": {"X-Api-Key": "secret"},
        }
    ]


@pytest.mark.asyncio
async def test_fetch_metric_caches_identical_query_for_15_minutes() -> None:
    clock = FakeClock()
    client = FakeGlassnodeClient()
    service = GlassnodeService(
        api_key="secret",
        client=client,
        cache_ttl_seconds=900,
        rate_limit_per_minute=0,
        monotonic=clock.monotonic,
        sleep=clock.sleep,
    )

    first = await service.fetch_metric("nvt", "ETH")
    second = await service.fetch_metric("nvt", "ETH")
    clock.value += 901
    third = await service.fetch_metric("nvt", "ETH")

    assert first.cached is False
    assert second.cached is True
    assert third.cached is False
    assert len(client.calls) == 2


@pytest.mark.asyncio
async def test_rate_limiter_spaces_uncached_requests() -> None:
    clock = FakeClock()
    client = FakeGlassnodeClient()
    service = GlassnodeService(
        api_key="secret",
        client=client,
        cache_ttl_seconds=900,
        rate_limit_per_minute=30,
        monotonic=clock.monotonic,
        sleep=clock.sleep,
    )

    await service.fetch_metric("mvrv", "BTC", since=1)
    await service.fetch_metric("nvt", "BTC", since=1)

    assert len(client.calls) == 2
    assert clock.value == pytest.approx(1002.0)


@pytest.mark.asyncio
async def test_fetch_metrics_covers_btc_and_eth_required_metrics() -> None:
    for asset in ("BTC", "ETH"):
        client = FakeGlassnodeClient()
        service = GlassnodeService(api_key="secret", client=client, rate_limit_per_minute=0)

        payload = await service.fetch_metrics(asset)

        assert payload["asset"] == asset
        assert [item["metric"] for item in payload["metrics"]] == list(GLASSNODE_METRICS)
        assert len(client.calls) == 4


@pytest.mark.asyncio
async def test_glassnode_429_raises_rate_limit_error() -> None:
    service = GlassnodeService(
        api_key="secret",
        client=FakeGlassnodeClient(status_code=429),
        rate_limit_per_minute=0,
    )

    with pytest.raises(GlassnodeRateLimitError):
        await service.fetch_metric("sopr", "BTC")


def test_unsupported_asset_and_metric_are_rejected() -> None:
    service = GlassnodeService(api_key="secret", client=FakeGlassnodeClient())

    with pytest.raises(ValueError, match="Unsupported Glassnode asset"):
        service._normalize_asset("SOL")

    with pytest.raises(ValueError, match="Unsupported Glassnode metric"):
        service._normalize_metric("foo")


@pytest.mark.asyncio
async def test_fetch_metric_supports_mining_metric_endpoints() -> None:
    client = FakeGlassnodeClient()
    service = GlassnodeService(api_key="secret", client=client, rate_limit_per_minute=0)

    result = await service.fetch_metric("hash_rate", "BTC", since=1, until=2)

    assert result.metric == "hash_rate"
    assert result.endpoint == GLASSNODE_MINING_METRICS["hash_rate"]
    assert client.calls == [
        {
            "url": "https://api.glassnode.com/v1/metrics/mining/hash_rate_mean",
            "params": {"a": "BTC", "i": "24h", "f": "json", "s": 1, "u": 2},
            "headers": {"X-Api-Key": "secret"},
        }
    ]


@pytest.mark.asyncio
async def test_fetch_metric_supports_supply_distribution_metric_endpoints() -> None:
    client = FakeGlassnodeClient()
    service = GlassnodeService(api_key="secret", client=client, rate_limit_per_minute=0)

    result = await service.fetch_metric("entity_supply_1k_10k", "BTC", since=1, until=2)

    assert result.metric == "entity_supply_1k_10k"
    assert result.endpoint == GLASSNODE_SUPPLY_DISTRIBUTION_METRICS["entity_supply_1k_10k"]
    assert client.calls == [
        {
            "url": "https://api.glassnode.com/v1/metrics/entities/supply_balance_1k_10k",
            "params": {"a": "BTC", "i": "24h", "f": "json", "s": 1, "u": 2},
            "headers": {"X-Api-Key": "secret"},
        }
    ]


def test_normalize_points_preserves_glassnode_value_shapes() -> None:
    payload = [
        {"t": 1, "v": 1.2},
        {"t": 2, "v": {"short_term": 0.9, "long_term": 1.1}, "o": {"quality": "ok"}},
        {"t": 3, "v": [1, 2, 3]},
        {"t": 4, "v": float("nan")},
    ]

    points = GlassnodeService._normalize_points(payload)

    assert points[:3] == payload[:3]
    assert points[3] == {"t": 4, "v": None}
