from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.services.glassnode_service import (
    GLASSNODE_SUPPLY_DISTRIBUTION_METRICS,
    GlassnodeMetricSeries,
)
from app.services.onchain_supply_distribution_service import (
    SupplyDistributionService,
    alerts_for_whale_movement,
    normalize_supply_distribution_basis,
    normalize_supply_distribution_interval,
    normalize_supply_distribution_window,
    summarize_numeric_series,
    summarize_whale_movement,
    supply_distribution_bounds,
)


def _series(metric: str, values: list[object], *, cached: bool = False) -> GlassnodeMetricSeries:
    now = datetime(2026, 4, 27, 12, 0, tzinfo=timezone.utc)
    return GlassnodeMetricSeries(
        metric=metric,
        asset="BTC",
        interval="24h",
        endpoint=f"/v1/metrics/{metric}",
        points=[{"t": index + 1, "v": value} for index, value in enumerate(values)],
        fetched_at=now,
        cached_until=now,
        cached=cached,
    )


def _series_with_points(
    metric: str,
    points: list[tuple[int, object]],
    *,
    cached: bool = False,
) -> GlassnodeMetricSeries:
    now = datetime(2026, 4, 27, 12, 0, tzinfo=timezone.utc)
    return GlassnodeMetricSeries(
        metric=metric,
        asset="BTC",
        interval="24h",
        endpoint=f"/v1/metrics/{metric}",
        points=[{"t": timestamp, "v": value} for timestamp, value in points],
        fetched_at=now,
        cached_until=now,
        cached=cached,
    )


def test_supply_distribution_normalizers_reject_unsupported_inputs() -> None:
    assert normalize_supply_distribution_basis("ENTITY") == "entity"
    assert normalize_supply_distribution_window("7D") == "7d"
    assert normalize_supply_distribution_interval("24H") == "24h"

    with pytest.raises(ValueError, match="Unsupported supply distribution basis"):
        normalize_supply_distribution_basis("address")
    with pytest.raises(ValueError, match="Unsupported supply distribution window"):
        normalize_supply_distribution_window("90d")
    with pytest.raises(ValueError, match="Unsupported supply distribution interval"):
        normalize_supply_distribution_interval("1h")


def test_supply_distribution_bounds_align_daily_series_and_fetch_extra_point() -> None:
    now = datetime(2026, 4, 27, 12, 30, tzinfo=timezone.utc)

    since, until, provider_since = supply_distribution_bounds(now, timedelta(days=1))

    assert since == int(datetime(2026, 4, 26, tzinfo=timezone.utc).timestamp())
    assert until == int(now.timestamp())
    assert provider_since == int(datetime(2026, 4, 25, tzinfo=timezone.utc).timestamp())


def test_summarize_numeric_series_sorts_and_handles_sparse_values() -> None:
    summary = summarize_numeric_series(
        [
            {"t": 3, "v": 30.0},
            {"t": 1, "v": 10.0},
            {"t": 2, "v": "bad"},
            {"t": 4, "v": float("nan")},
        ]
    )

    assert summary["latest"] == 30.0
    assert summary["latest_timestamp"] == 3
    assert summary["previous"] == 10.0
    assert summary["previous_timestamp"] == 1
    assert summary["change_abs"] == 20.0
    assert summary["change_pct"] == 200.0

    sparse = summarize_numeric_series([{"t": 1, "v": 10.0}])

    assert sparse["latest"] == 10.0
    assert sparse["previous"] is None
    assert sparse["change_abs"] is None


def test_summarize_numeric_series_uses_daily_window_baseline() -> None:
    day_25 = int(datetime(2026, 4, 25, tzinfo=timezone.utc).timestamp())
    day_26 = int(datetime(2026, 4, 26, tzinfo=timezone.utc).timestamp())
    day_27 = int(datetime(2026, 4, 27, tzinfo=timezone.utc).timestamp())

    summary = summarize_numeric_series(
        [
            {"t": day_25, "v": 100.0},
            {"t": day_26, "v": 130.0},
            {"t": day_27, "v": 160.0},
        ],
        window_seconds=24 * 60 * 60,
    )

    assert summary["latest"] == 160.0
    assert summary["previous"] == 130.0
    assert summary["change_abs"] == 30.0


def test_whale_movement_alerts_on_absolute_1000_btc_boundary() -> None:
    movement = summarize_whale_movement({"change_abs": 1000.0})

    assert movement == {
        "threshold_btc": 1000.0,
        "change_abs": 1000.0,
        "direction": "accumulation",
        "alert": True,
    }
    assert alerts_for_whale_movement(movement, "7d") == [
        {
            "type": "whale-alert",
            "threshold_btc": 1000.0,
            "change_abs": 1000.0,
            "direction": "accumulation",
            "window": "7d",
        }
    ]


def test_whale_movement_alerts_on_distribution_and_skips_below_threshold() -> None:
    distribution = summarize_whale_movement({"change_abs": -1500.0})
    quiet = summarize_whale_movement({"change_abs": 999.99})

    assert distribution["direction"] == "distribution"
    assert distribution["alert"] is True
    assert quiet["direction"] == "accumulation"
    assert quiet["alert"] is False
    assert alerts_for_whale_movement(quiet, "24h") == []


class FakeGlassnodeService:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def fetch_metric(
        self,
        metric: str,
        asset: str,
        interval: str,
        since: int | None,
        until: int | None,
    ):
        self.calls.append(
            {
                "metric": metric,
                "asset": asset,
                "interval": interval,
                "since": since,
                "until": until,
            }
        )
        values_by_metric = {
            "entity_supply_less_0001": [10.0, 11.0],
            "entity_supply_0001_001": [20.0, 22.0],
            "entity_supply_001_01": [30.0, 33.0],
            "entity_supply_01_1": [40.0, 44.0],
            "entity_supply_1_10": [50.0, 55.0],
            "entity_supply_10_100": [60.0, 66.0],
            "entity_supply_100_1k": [70.0, 77.0],
            "entity_supply_1k_10k": [2000.0, 2600.0],
            "entity_supply_10k_100k": [3000.0, 3500.0],
            "entity_supply_more_100k": [4000.0, 4100.0],
            "lth_supply": [8000.0, 8100.0],
        }
        return _series(metric, values_by_metric[metric], cached=True)

    def _normalize_asset(self, asset: str) -> str:
        return asset.upper()


class DailyFakeGlassnodeService:
    def __init__(self) -> None:
        self.calls: list[dict] = []
        self.day_25 = int(datetime(2026, 4, 25, tzinfo=timezone.utc).timestamp())
        self.day_26 = int(datetime(2026, 4, 26, tzinfo=timezone.utc).timestamp())

    async def fetch_metric(
        self,
        metric: str,
        asset: str,
        interval: str,
        since: int | None,
        until: int | None,
    ):
        self.calls.append(
            {
                "metric": metric,
                "asset": asset,
                "interval": interval,
                "since": since,
                "until": until,
            }
        )
        values_by_metric = {
            "entity_supply_1k_10k": [(self.day_25, 1000.0), (self.day_26, 1600.0)],
            "entity_supply_10k_100k": [(self.day_25, 2000.0), (self.day_26, 2500.0)],
            "entity_supply_more_100k": [(self.day_25, 3000.0), (self.day_26, 3100.0)],
            "lth_supply": [(self.day_25, 8000.0), (self.day_26, 8050.0)],
        }
        points = values_by_metric.get(metric, [(self.day_25, 100.0), (self.day_26, 100.0)])
        filtered = [
            (timestamp, value)
            for timestamp, value in points
            if (since is None or timestamp >= since) and (until is None or timestamp <= until)
        ]
        return _series_with_points(metric, filtered, cached=True)

    def _normalize_asset(self, asset: str) -> str:
        return asset.upper()


@pytest.mark.asyncio
async def test_supply_distribution_service_fetches_bands_and_aggregates_cohorts() -> None:
    fake_glassnode = FakeGlassnodeService()
    now = datetime(2026, 4, 27, 12, 0, tzinfo=timezone.utc)
    service = SupplyDistributionService(
        glassnode_service=fake_glassnode,
        now=lambda: now,
    )

    payload = await service.fetch_supply_distribution("btc", window="7d")

    assert payload["asset"] == "BTC"
    assert payload["basis"] == "entity"
    assert payload["window"] == "7d"
    expected_since = int(datetime(2026, 4, 20, tzinfo=timezone.utc).timestamp())
    expected_provider_since = int(datetime(2026, 4, 19, tzinfo=timezone.utc).timestamp())
    assert payload["since"] == expected_since
    assert payload["until"] == int(now.timestamp())
    assert payload["cached"] is True
    assert [call["metric"] for call in fake_glassnode.calls] == list(
        GLASSNODE_SUPPLY_DISTRIBUTION_METRICS
    )
    assert {call["interval"] for call in fake_glassnode.calls} == {"24h"}
    assert len(payload["bands"]) == 10
    assert {call["since"] for call in fake_glassnode.calls} == {expected_provider_since}
    assert payload["bands"][0]["id"] == "less_0001"
    assert payload["bands"][0]["change_abs"] == 1.0
    assert payload["bands"][0]["change_pct"] == 10.0
    assert payload["cohorts"]["shrimps"]["latest"] == 110.0
    assert payload["cohorts"]["shrimps"]["change_abs"] == 10.0
    assert payload["cohorts"]["whales"]["latest"] == 10200.0
    assert payload["cohorts"]["whales"]["change_abs"] == 1200.0
    assert payload["cohorts"]["hodlers"]["latest"] == 8100.0
    assert payload["whale_movement"]["alert"] is True
    assert payload["alerts"][0]["type"] == "whale-alert"
    assert payload["sources"]["entity_supply_1k_10k"]["cached"] is True


@pytest.mark.asyncio
async def test_supply_distribution_service_24h_fetches_prior_daily_point_for_delta() -> None:
    fake_glassnode = DailyFakeGlassnodeService()
    now = datetime(2026, 4, 27, 12, 0, tzinfo=timezone.utc)
    service = SupplyDistributionService(
        glassnode_service=fake_glassnode,
        now=lambda: now,
    )

    payload = await service.fetch_supply_distribution("btc", window="24h")

    expected_since = int(datetime(2026, 4, 26, tzinfo=timezone.utc).timestamp())
    expected_provider_since = int(datetime(2026, 4, 25, tzinfo=timezone.utc).timestamp())
    assert payload["since"] == expected_since
    assert {call["since"] for call in fake_glassnode.calls} == {expected_provider_since}
    assert payload["cohorts"]["whales"]["previous_timestamp"] == expected_provider_since
    assert payload["cohorts"]["whales"]["latest_timestamp"] == expected_since
    assert payload["cohorts"]["whales"]["change_abs"] == 1200.0
    assert payload["whale_movement"]["alert"] is True
    assert payload["alerts"][0]["type"] == "whale-alert"


@pytest.mark.asyncio
async def test_supply_distribution_service_rejects_invalid_basis_before_provider_call() -> None:
    fake_glassnode = FakeGlassnodeService()
    service = SupplyDistributionService(glassnode_service=fake_glassnode)

    with pytest.raises(ValueError, match="Unsupported supply distribution basis"):
        await service.fetch_supply_distribution("btc", basis="address", window="7d")

    assert fake_glassnode.calls == []
