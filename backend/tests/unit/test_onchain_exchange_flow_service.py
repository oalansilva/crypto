from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.services.glassnode_service import GlassnodeMetricSeries
from app.services.onchain_exchange_flow_service import (
    ExchangeFlowService,
    aggregate_exchange_flow_series,
    normalize_exchange_flow_window,
)


def _series(metric: str, values: list[object], *, cached: bool = False) -> GlassnodeMetricSeries:
    now = datetime(2026, 4, 24, 12, 0, tzinfo=timezone.utc)
    return GlassnodeMetricSeries(
        metric=metric,
        asset="BTC",
        interval="24h",
        endpoint=f"/v1/metrics/transactions/{metric}",
        points=[{"t": 1 + index, "v": value} for index, value in enumerate(values)],
        fetched_at=now,
        cached_until=now,
        cached=cached,
    )


def test_exchange_flow_aggregation_groups_object_payload_by_exchange() -> None:
    result = aggregate_exchange_flow_series(
        {
            "inflow": _series(
                "inflow",
                [
                    {"Binance": 100.0, "Coinbase": 50.0},
                    {"Binance": 25.0, "Coinbase": 10.0},
                ],
            ),
            "outflow": _series(
                "outflow",
                [
                    {"Binance": 40.0, "Coinbase": 20.0},
                    {"Binance": 5.0, "Coinbase": 15.0},
                ],
            ),
            "netflow": _series(
                "netflow",
                [
                    {"Binance": 60.0, "Coinbase": 30.0},
                    {"Binance": 20.0, "Coinbase": -5.0},
                ],
            ),
        }
    )

    assert result["exchanges"] == [
        {"exchange": "binance", "inflow": 125.0, "outflow": 45.0, "netflow": 80.0},
        {"exchange": "coinbase", "inflow": 60.0, "outflow": 35.0, "netflow": 25.0},
    ]
    assert result["total"] == {"inflow": 185.0, "outflow": 80.0, "netflow": 105.0}


def test_exchange_flow_aggregation_derives_missing_exchange_netflow() -> None:
    result = aggregate_exchange_flow_series(
        {
            "inflow": _series("inflow", [{"Binance": 100.0}]),
            "outflow": _series("outflow", [{"Binance": 40.0}]),
            "netflow": _series("netflow", []),
        }
    )

    assert result["exchanges"] == [
        {"exchange": "binance", "inflow": 100.0, "outflow": 40.0, "netflow": 60.0}
    ]
    assert result["total"] == {"inflow": 100.0, "outflow": 40.0, "netflow": 60.0}


def test_exchange_flow_aggregation_uses_scalar_payload_as_total() -> None:
    result = aggregate_exchange_flow_series(
        {
            "inflow": _series("inflow", [100.0, 50.0]),
            "outflow": _series("outflow", [20.0, 10.0]),
            "netflow": _series("netflow", [80.0, 40.0]),
        }
    )

    assert result["exchanges"] == []
    assert result["total"] == {"inflow": 150.0, "outflow": 30.0, "netflow": 120.0}


def test_exchange_flow_window_validation() -> None:
    assert normalize_exchange_flow_window("24H") == "24h"
    assert normalize_exchange_flow_window("7d") == "7d"
    assert normalize_exchange_flow_window("30d") == "30d"
    with pytest.raises(ValueError, match="Unsupported exchange flow window"):
        normalize_exchange_flow_window("90d")


class FakeGlassnodeService:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def fetch_metric(self, metric: str, asset: str, interval: str, since: int, until: int):
        self.calls.append(
            {
                "metric": metric,
                "asset": asset,
                "interval": interval,
                "since": since,
                "until": until,
            }
        )
        return _series(metric, [{"Binance": 1.0}], cached=True)

    def _normalize_asset(self, asset: str) -> str:
        return asset.upper()


@pytest.mark.asyncio
async def test_exchange_flow_service_fetches_required_metrics_for_7d_window() -> None:
    fake_glassnode = FakeGlassnodeService()
    service = ExchangeFlowService(
        glassnode_service=fake_glassnode,
        now=lambda: datetime(2026, 4, 24, 12, 0, tzinfo=timezone.utc),
    )

    payload = await service.fetch_exchange_flows("btc", window="7d")

    assert payload["asset"] == "BTC"
    assert payload["window"] == "7d"
    assert payload["interval"] == "24h"
    assert payload["until"] == 1777032000
    assert payload["since"] == 1776427200
    assert payload["cached"] is True
    assert [call["metric"] for call in fake_glassnode.calls] == [
        "inflow",
        "outflow",
        "netflow",
    ]
    assert {call["asset"] for call in fake_glassnode.calls} == {"btc"}
