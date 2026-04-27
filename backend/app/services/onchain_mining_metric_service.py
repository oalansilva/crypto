from __future__ import annotations

import math
from typing import Any

from app.services.glassnode_service import (
    DEFAULT_GLASSNODE_INTERVAL,
    GLASSNODE_MINING_METRICS,
    GlassnodeMetricSeries,
    get_glassnode_service,
)

SHARP_DROP_THRESHOLD_PCT = 10.0
SHARP_DROP_RATIO = 1.0 - (SHARP_DROP_THRESHOLD_PCT / 100.0)
MOVING_AVERAGE_WINDOWS = (7, 30)
SUPPORTED_MINING_METRIC_INTERVAL = DEFAULT_GLASSNODE_INTERVAL


class MiningMetricService:
    def __init__(self, *, glassnode_service=None) -> None:
        self._glassnode_service = glassnode_service or get_glassnode_service()

    async def fetch_mining_metrics(
        self,
        asset: str,
        *,
        interval: str = DEFAULT_GLASSNODE_INTERVAL,
        since: int | None = None,
        until: int | None = None,
    ) -> dict[str, Any]:
        normalized_interval = normalize_mining_metric_interval(interval)
        metric_rows: dict[str, GlassnodeMetricSeries] = {}
        for metric in GLASSNODE_MINING_METRICS:
            metric_rows[metric] = await self._glassnode_service.fetch_metric(
                metric,
                asset,
                interval=normalized_interval,
                since=since,
                until=until,
            )

        normalized_asset = self._glassnode_service._normalize_asset(asset)
        return {
            "asset": normalized_asset,
            "interval": normalized_interval,
            "since": since,
            "until": until,
            "cached": all(series.cached for series in metric_rows.values()),
            "metrics": [enrich_mining_metric_series(series) for series in metric_rows.values()],
        }


def normalize_mining_metric_interval(interval: str) -> str:
    normalized = str(interval or "").strip().lower()
    if normalized != SUPPORTED_MINING_METRIC_INTERVAL:
        raise ValueError(
            "Unsupported mining metric interval "
            f"'{interval}'. Supported: {SUPPORTED_MINING_METRIC_INTERVAL}"
        )
    return normalized


def enrich_mining_metric_series(series: GlassnodeMetricSeries) -> dict[str, Any]:
    enriched_points = _enrich_points(series.points)
    latest = enriched_points[-1] if enriched_points else None
    ath = _ath_from_points(enriched_points)
    drop_pct_vs_ma_7d = _drop_pct_vs_ma_7d(latest)
    alerts = _alerts_for_latest(latest, drop_pct_vs_ma_7d)

    return {
        "metric": series.metric,
        "asset": series.asset,
        "interval": series.interval,
        "endpoint": series.endpoint,
        "points": enriched_points,
        "latest": latest,
        "ath": ath,
        "drop_pct_vs_ma_7d": drop_pct_vs_ma_7d,
        "alerts": alerts,
        "fetched_at": series.fetched_at,
        "cached_until": series.cached_until,
        "cached": series.cached,
    }


def _enrich_points(points: list[dict[str, Any]]) -> list[dict[str, Any]]:
    numeric_values: list[float] = []
    ath_value: float | None = None
    enriched: list[dict[str, Any]] = []

    for point in sorted(points, key=_point_sort_key):
        row = dict(point)
        value = _numeric_or_none(row.get("v"))
        if value is not None:
            numeric_values.append(value)
            if ath_value is None or value > ath_value:
                ath_value = value
            row["distance_from_ath_pct"] = _distance_from_ath_pct(value, ath_value)
            for window in MOVING_AVERAGE_WINDOWS:
                if len(numeric_values) >= window:
                    row[f"ma_{window}d"] = _moving_average(numeric_values, window)
        enriched.append(row)

    return enriched


def _ath_from_points(points: list[dict[str, Any]]) -> dict[str, Any] | None:
    ath: dict[str, Any] | None = None
    for point in points:
        value = _numeric_or_none(point.get("v"))
        if value is None:
            continue
        if ath is None or value > ath["v"]:
            ath = {"t": point.get("t"), "v": value}
    return ath


def _drop_pct_vs_ma_7d(latest: dict[str, Any] | None) -> float | None:
    if latest is None:
        return None
    latest_value = _numeric_or_none(latest.get("v"))
    ma_7d = _numeric_or_none(latest.get("ma_7d"))
    if latest_value is None or ma_7d is None or ma_7d == 0:
        return None
    return ((ma_7d - latest_value) / ma_7d) * 100.0


def _alerts_for_latest(
    latest: dict[str, Any] | None,
    drop_pct_vs_ma_7d: float | None,
) -> list[dict[str, Any]]:
    latest_value = _numeric_or_none((latest or {}).get("v"))
    ma_7d = _numeric_or_none((latest or {}).get("ma_7d"))
    if latest_value is None or ma_7d is None:
        return []
    if latest_value >= ma_7d * SHARP_DROP_RATIO:
        return []
    return [
        {
            "type": "sharp_drop",
            "threshold_pct": SHARP_DROP_THRESHOLD_PCT,
            "drop_pct_vs_ma_7d": drop_pct_vs_ma_7d,
        }
    ]


def _moving_average(values: list[float], window: int) -> float:
    return sum(values[-window:]) / float(window)


def _distance_from_ath_pct(value: float, ath_value: float | None) -> float | None:
    if ath_value is None:
        return None
    if ath_value == 0:
        return 0.0 if value == 0 else None
    return ((value - ath_value) / ath_value) * 100.0


def _point_sort_key(point: dict[str, Any]) -> tuple[int, float]:
    timestamp = _numeric_or_none(point.get("t"))
    if timestamp is None:
        return (1, math.inf)
    return (0, timestamp)


def _numeric_or_none(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(parsed):
        return None
    return parsed


_SERVICE: MiningMetricService | None = None


def get_mining_metric_service() -> MiningMetricService:
    global _SERVICE
    if _SERVICE is None:
        _SERVICE = MiningMetricService()
    return _SERVICE
