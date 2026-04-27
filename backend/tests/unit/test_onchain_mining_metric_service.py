from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.services.glassnode_service import GlassnodeMetricSeries
from app.services.onchain_mining_metric_service import (
    MiningMetricService,
    enrich_mining_metric_series,
    normalize_mining_metric_interval,
)


def _series(metric: str, values: list[object], *, cached: bool = False) -> GlassnodeMetricSeries:
    now = datetime(2026, 4, 27, 12, 0, tzinfo=timezone.utc)
    return GlassnodeMetricSeries(
        metric=metric,
        asset="BTC",
        interval="24h",
        endpoint=f"/v1/metrics/mining/{metric}",
        points=[{"t": index + 1, "v": value} for index, value in enumerate(values)],
        fetched_at=now,
        cached_until=now,
        cached=cached,
    )


def test_mining_metric_enrichment_sorts_points_and_calculates_ma_and_ath() -> None:
    raw_points = [{"t": timestamp, "v": float(timestamp)} for timestamp in range(30, 0, -1)]
    now = datetime(2026, 4, 27, 12, 0, tzinfo=timezone.utc)
    series = GlassnodeMetricSeries(
        metric="hash_rate",
        asset="BTC",
        interval="24h",
        endpoint="/v1/metrics/mining/hash_rate_mean",
        points=raw_points,
        fetched_at=now,
        cached_until=now,
        cached=False,
    )

    payload = enrich_mining_metric_series(series)

    assert [point["t"] for point in payload["points"]] == list(range(1, 31))
    assert payload["latest"]["v"] == 30.0
    assert payload["latest"]["ma_7d"] == pytest.approx(27.0)
    assert payload["latest"]["ma_30d"] == pytest.approx(15.5)
    assert payload["latest"]["distance_from_ath_pct"] == pytest.approx(0.0)
    assert payload["ath"] == {"t": 30, "v": 30.0}
    assert payload["alerts"] == []


def test_mining_metric_enrichment_alerts_on_more_than_10_percent_drop() -> None:
    payload = enrich_mining_metric_series(
        _series("difficulty", [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 80.0])
    )

    assert payload["latest"]["ma_7d"] == pytest.approx(97.14285714285714)
    assert payload["drop_pct_vs_ma_7d"] == pytest.approx(17.647058823529413)
    assert payload["alerts"] == [
        {
            "type": "sharp_drop",
            "threshold_pct": 10.0,
            "drop_pct_vs_ma_7d": pytest.approx(17.647058823529413),
        }
    ]


def test_mining_metric_enrichment_does_not_alert_at_exact_10_percent_boundary() -> None:
    boundary_latest = 540.0 / 6.1
    payload = enrich_mining_metric_series(
        _series(
            "hash_rate",
            [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, boundary_latest],
        )
    )

    assert payload["drop_pct_vs_ma_7d"] == pytest.approx(10.0)
    assert payload["alerts"] == []


def test_mining_metric_enrichment_ignores_non_numeric_values_without_crashing() -> None:
    payload = enrich_mining_metric_series(
        _series("miner_revenue_total", ["bad", float("nan"), 10.0, None])
    )

    assert payload["ath"] == {"t": 3, "v": 10.0}
    assert "ma_7d" not in payload["points"][2]
    assert payload["latest"] == {"t": 4, "v": None}
    assert payload["drop_pct_vs_ma_7d"] is None
    assert payload["alerts"] == []


def test_mining_metric_enrichment_handles_empty_series() -> None:
    payload = enrich_mining_metric_series(_series("hash_rate", []))

    assert payload["points"] == []
    assert payload["latest"] is None
    assert payload["ath"] is None
    assert payload["drop_pct_vs_ma_7d"] is None
    assert payload["alerts"] == []


def test_mining_metric_interval_is_daily_only() -> None:
    assert normalize_mining_metric_interval("24H") == "24h"
    with pytest.raises(ValueError, match="Unsupported mining metric interval"):
        normalize_mining_metric_interval("1h")


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
        return _series(metric, [1.0, 2.0, 3.0], cached=True)

    def _normalize_asset(self, asset: str) -> str:
        return asset.upper()


@pytest.mark.asyncio
async def test_mining_metric_service_fetches_required_glassnode_metrics() -> None:
    fake_glassnode = FakeGlassnodeService()
    service = MiningMetricService(glassnode_service=fake_glassnode)

    payload = await service.fetch_mining_metrics("btc", since=1, until=2)

    assert payload["asset"] == "BTC"
    assert payload["interval"] == "24h"
    assert payload["since"] == 1
    assert payload["until"] == 2
    assert payload["cached"] is True
    assert [call["metric"] for call in fake_glassnode.calls] == [
        "hash_rate",
        "difficulty",
        "miner_revenue_total",
    ]
    assert {metric["metric"] for metric in payload["metrics"]} == {
        "hash_rate",
        "difficulty",
        "miner_revenue_total",
    }


@pytest.mark.asyncio
async def test_mining_metric_service_rejects_non_daily_interval_before_provider_call() -> None:
    fake_glassnode = FakeGlassnodeService()
    service = MiningMetricService(glassnode_service=fake_glassnode)

    with pytest.raises(ValueError, match="Unsupported mining metric interval"):
        await service.fetch_mining_metrics("btc", interval="1h")

    assert fake_glassnode.calls == []
