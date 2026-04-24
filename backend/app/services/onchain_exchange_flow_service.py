from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Any

from app.services.glassnode_service import (
    DEFAULT_GLASSNODE_INTERVAL,
    GLASSNODE_EXCHANGE_FLOW_METRICS,
    GlassnodeMetricSeries,
    get_glassnode_service,
)

SUPPORTED_EXCHANGE_FLOW_WINDOWS: dict[str, timedelta] = {
    "24h": timedelta(days=1),
    "7d": timedelta(days=7),
    "30d": timedelta(days=30),
}


class ExchangeFlowService:
    def __init__(self, *, glassnode_service=None, now=None) -> None:
        self._glassnode_service = glassnode_service or get_glassnode_service()
        self._now = now or (lambda: datetime.now(timezone.utc))

    async def fetch_exchange_flows(
        self,
        asset: str,
        *,
        window: str,
        interval: str = DEFAULT_GLASSNODE_INTERVAL,
    ) -> dict[str, Any]:
        normalized_window = normalize_exchange_flow_window(window)
        until_dt = self._now()
        since_dt = until_dt - SUPPORTED_EXCHANGE_FLOW_WINDOWS[normalized_window]
        since = int(since_dt.timestamp())
        until = int(until_dt.timestamp())

        metric_rows: dict[str, GlassnodeMetricSeries] = {}
        for metric in GLASSNODE_EXCHANGE_FLOW_METRICS:
            metric_rows[metric] = await self._glassnode_service.fetch_metric(
                metric,
                asset,
                interval=interval,
                since=since,
                until=until,
            )

        aggregation = aggregate_exchange_flow_series(metric_rows)
        sources = {
            metric: {
                "endpoint": series.endpoint,
                "points": len(series.points),
                "cached": series.cached,
                "fetched_at": series.fetched_at,
                "cached_until": series.cached_until,
            }
            for metric, series in metric_rows.items()
        }
        normalized_asset = self._glassnode_service._normalize_asset(asset)
        return {
            "asset": normalized_asset,
            "window": normalized_window,
            "interval": interval,
            "since": since,
            "until": until,
            "cached": all(series.cached for series in metric_rows.values()),
            "total": aggregation["total"],
            "exchanges": aggregation["exchanges"],
            "sources": sources,
        }


def normalize_exchange_flow_window(window: str) -> str:
    normalized = str(window or "").strip().lower()
    if normalized not in SUPPORTED_EXCHANGE_FLOW_WINDOWS:
        supported = ", ".join(SUPPORTED_EXCHANGE_FLOW_WINDOWS)
        raise ValueError(f"Unsupported exchange flow window '{window}'. Supported: {supported}")
    return normalized


def aggregate_exchange_flow_series(
    series_by_metric: dict[str, GlassnodeMetricSeries],
) -> dict[str, Any]:
    buckets: dict[str, dict[str, float]] = {}

    for metric, series in series_by_metric.items():
        for point in series.points:
            _add_exchange_flow_value(buckets, metric, point.get("v"))

    total = {
        "inflow": 0.0,
        "outflow": 0.0,
        "netflow": 0.0,
    }
    exchanges: list[dict[str, Any]] = []
    for exchange, values in sorted(buckets.items()):
        inflow = values.get("inflow", 0.0)
        outflow = values.get("outflow", 0.0)
        netflow = values.get("netflow", inflow - outflow)

        if exchange == "total":
            total["inflow"] += inflow
            total["outflow"] += outflow
            total["netflow"] += netflow
            continue

        exchanges.append(
            {
                "exchange": exchange,
                "inflow": inflow,
                "outflow": outflow,
                "netflow": netflow,
            }
        )
        total["inflow"] += inflow
        total["outflow"] += outflow
        total["netflow"] += netflow

    return {
        "total": total,
        "exchanges": exchanges,
    }


def _add_exchange_flow_value(
    buckets: dict[str, dict[str, float]],
    metric: str,
    raw_value: Any,
) -> None:
    numeric = _numeric_or_none(raw_value)
    if numeric is not None:
        bucket = buckets.setdefault("total", {})
        bucket[metric] = bucket.get(metric, 0.0) + numeric
        return

    if not isinstance(raw_value, dict):
        return

    for exchange, value in raw_value.items():
        parsed = _numeric_or_none(value)
        if parsed is None:
            continue
        bucket = buckets.setdefault(_normalize_exchange_name(exchange), {})
        bucket[metric] = bucket.get(metric, 0.0) + parsed


def _numeric_or_none(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(parsed):
        return None
    return parsed


def _normalize_exchange_name(value: Any) -> str:
    normalized = str(value or "").strip().lower()
    return normalized or "unknown"


_SERVICE: ExchangeFlowService | None = None


def get_exchange_flow_service() -> ExchangeFlowService:
    global _SERVICE
    if _SERVICE is None:
        _SERVICE = ExchangeFlowService()
    return _SERVICE
