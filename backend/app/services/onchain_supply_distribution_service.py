from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from app.services.glassnode_service import (
    DEFAULT_GLASSNODE_INTERVAL,
    GLASSNODE_SUPPLY_DISTRIBUTION_METRICS,
    GlassnodeMetricSeries,
    get_glassnode_service,
)

SUPPORTED_SUPPLY_DISTRIBUTION_BASIS = "entity"
SUPPORTED_SUPPLY_DISTRIBUTION_INTERVAL = DEFAULT_GLASSNODE_INTERVAL
SUPPORTED_SUPPLY_DISTRIBUTION_WINDOWS: dict[str, timedelta] = {
    "24h": timedelta(days=1),
    "7d": timedelta(days=7),
    "30d": timedelta(days=30),
}
DAILY_PROVIDER_LOOKBACK = timedelta(days=1)
WHALE_ALERT_THRESHOLD_BTC = 1000.0


@dataclass(frozen=True)
class SupplyBandDefinition:
    id: str
    metric: str
    label: str
    min_btc: float | None
    max_btc: float | None


ENTITY_SUPPLY_BANDS: tuple[SupplyBandDefinition, ...] = (
    SupplyBandDefinition("less_0001", "entity_supply_less_0001", "< 0.001 BTC", None, 0.001),
    SupplyBandDefinition("0001_001", "entity_supply_0001_001", "0.001 - 0.01 BTC", 0.001, 0.01),
    SupplyBandDefinition("001_01", "entity_supply_001_01", "0.01 - 0.1 BTC", 0.01, 0.1),
    SupplyBandDefinition("01_1", "entity_supply_01_1", "0.1 - 1 BTC", 0.1, 1.0),
    SupplyBandDefinition("1_10", "entity_supply_1_10", "1 - 10 BTC", 1.0, 10.0),
    SupplyBandDefinition("10_100", "entity_supply_10_100", "10 - 100 BTC", 10.0, 100.0),
    SupplyBandDefinition("100_1k", "entity_supply_100_1k", "100 - 1k BTC", 100.0, 1000.0),
    SupplyBandDefinition("1k_10k", "entity_supply_1k_10k", "1k - 10k BTC", 1000.0, 10000.0),
    SupplyBandDefinition(
        "10k_100k",
        "entity_supply_10k_100k",
        "10k - 100k BTC",
        10000.0,
        100000.0,
    ),
    SupplyBandDefinition("more_100k", "entity_supply_more_100k", "> 100k BTC", 100000.0, None),
)
SHRIMP_BAND_IDS = {"less_0001", "0001_001", "001_01", "01_1"}
WHALE_BAND_IDS = {"1k_10k", "10k_100k", "more_100k"}


class SupplyDistributionService:
    def __init__(self, *, glassnode_service=None, now=None) -> None:
        self._glassnode_service = glassnode_service or get_glassnode_service()
        self._now = now or (lambda: datetime.now(timezone.utc))

    async def fetch_supply_distribution(
        self,
        asset: str,
        *,
        basis: str = SUPPORTED_SUPPLY_DISTRIBUTION_BASIS,
        window: str,
        interval: str = SUPPORTED_SUPPLY_DISTRIBUTION_INTERVAL,
    ) -> dict[str, Any]:
        normalized_basis = normalize_supply_distribution_basis(basis)
        normalized_window = normalize_supply_distribution_window(window)
        normalized_interval = normalize_supply_distribution_interval(interval)
        window_delta = SUPPORTED_SUPPLY_DISTRIBUTION_WINDOWS[normalized_window]
        since, until, provider_since = supply_distribution_bounds(self._now(), window_delta)

        metric_rows: dict[str, GlassnodeMetricSeries] = {}
        for metric in GLASSNODE_SUPPLY_DISTRIBUTION_METRICS:
            metric_rows[metric] = await self._glassnode_service.fetch_metric(
                metric,
                asset,
                interval=normalized_interval,
                since=provider_since,
                until=until,
            )

        band_rows = [
            summarize_supply_band(
                definition,
                metric_rows[definition.metric],
                int(window_delta.total_seconds()),
            )
            for definition in ENTITY_SUPPLY_BANDS
        ]
        represented_supply = sum(
            value
            for value in (_numeric_or_none(row.get("latest")) for row in band_rows)
            if value is not None
        )
        for row in band_rows:
            latest = _numeric_or_none(row.get("latest"))
            row["share_pct"] = _share_pct(latest, represented_supply)

        cohorts = {
            "shrimps": summarize_supply_cohort(
                "shrimps",
                "Shrimps (< 1 BTC)",
                [row for row in band_rows if row["id"] in SHRIMP_BAND_IDS],
                represented_supply,
            ),
            "whales": summarize_supply_cohort(
                "whales",
                "Whales (>= 1000 BTC)",
                [row for row in band_rows if row["id"] in WHALE_BAND_IDS],
                represented_supply,
            ),
            "hodlers": summarize_hodler_cohort(
                metric_rows["lth_supply"],
                represented_supply,
                int(window_delta.total_seconds()),
            ),
        }
        whale_movement = summarize_whale_movement(cohorts["whales"])
        alerts = alerts_for_whale_movement(whale_movement, normalized_window)
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
            "basis": normalized_basis,
            "window": normalized_window,
            "interval": normalized_interval,
            "since": since,
            "until": until,
            "cached": all(series.cached for series in metric_rows.values()),
            "bands": band_rows,
            "cohorts": cohorts,
            "whale_movement": whale_movement,
            "alerts": alerts,
            "sources": sources,
        }


def normalize_supply_distribution_basis(basis: str) -> str:
    normalized = str(basis or "").strip().lower()
    if normalized != SUPPORTED_SUPPLY_DISTRIBUTION_BASIS:
        raise ValueError(
            "Unsupported supply distribution basis "
            f"'{basis}'. Supported: {SUPPORTED_SUPPLY_DISTRIBUTION_BASIS}"
        )
    return normalized


def normalize_supply_distribution_window(window: str) -> str:
    normalized = str(window or "").strip().lower()
    if normalized not in SUPPORTED_SUPPLY_DISTRIBUTION_WINDOWS:
        supported = ", ".join(SUPPORTED_SUPPLY_DISTRIBUTION_WINDOWS)
        raise ValueError(
            f"Unsupported supply distribution window '{window}'. Supported: {supported}"
        )
    return normalized


def normalize_supply_distribution_interval(interval: str) -> str:
    normalized = str(interval or "").strip().lower()
    if normalized != SUPPORTED_SUPPLY_DISTRIBUTION_INTERVAL:
        raise ValueError(
            "Unsupported supply distribution interval "
            f"'{interval}'. Supported: {SUPPORTED_SUPPLY_DISTRIBUTION_INTERVAL}"
        )
    return normalized


def supply_distribution_bounds(now: datetime, window: timedelta) -> tuple[int, int, int]:
    until_dt = _ensure_utc(now)
    anchor_dt = until_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    since_dt = anchor_dt - window
    provider_since_dt = since_dt - DAILY_PROVIDER_LOOKBACK
    return int(since_dt.timestamp()), int(until_dt.timestamp()), int(provider_since_dt.timestamp())


def summarize_supply_band(
    definition: SupplyBandDefinition,
    series: GlassnodeMetricSeries,
    window_seconds: int | None = None,
) -> dict[str, Any]:
    summary = summarize_numeric_series(series.points, window_seconds=window_seconds)
    return {
        "id": definition.id,
        "metric": definition.metric,
        "label": definition.label,
        "min_btc": definition.min_btc,
        "max_btc": definition.max_btc,
        **summary,
        "share_pct": None,
    }


def summarize_supply_cohort(
    cohort_id: str,
    label: str,
    bands: list[dict[str, Any]],
    represented_supply: float,
) -> dict[str, Any]:
    latest = _sum_optional(row.get("latest") for row in bands)
    previous = _sum_optional(row.get("previous") for row in bands)
    change_abs = _change_abs(latest, previous)
    return {
        "id": cohort_id,
        "label": label,
        "band_ids": [str(row["id"]) for row in bands],
        "latest": latest,
        "latest_timestamp": _max_timestamp(row.get("latest_timestamp") for row in bands),
        "previous": previous,
        "previous_timestamp": _min_timestamp(row.get("previous_timestamp") for row in bands),
        "change_abs": change_abs,
        "change_pct": _change_pct(change_abs, previous),
        "share_pct": _share_pct(latest, represented_supply),
    }


def summarize_hodler_cohort(
    series: GlassnodeMetricSeries,
    represented_supply: float,
    window_seconds: int | None = None,
) -> dict[str, Any]:
    summary = summarize_numeric_series(series.points, window_seconds=window_seconds)
    return {
        "id": "hodlers",
        "label": "Long-term holders",
        "band_ids": [],
        **summary,
        "share_pct": _share_pct(_numeric_or_none(summary.get("latest")), represented_supply),
    }


def summarize_numeric_series(
    points: list[dict[str, Any]],
    *,
    window_seconds: int | None = None,
) -> dict[str, Any]:
    numeric_points = _numeric_points(points)
    latest = numeric_points[-1] if numeric_points else None
    previous = _baseline_point(numeric_points, latest, window_seconds)
    latest_value = latest["v"] if latest else None
    previous_value = previous["v"] if previous else None
    change_abs = _change_abs(latest_value, previous_value)
    return {
        "latest": latest_value,
        "latest_timestamp": latest.get("t") if latest else None,
        "previous": previous_value,
        "previous_timestamp": previous.get("t") if previous else None,
        "change_abs": change_abs,
        "change_pct": _change_pct(change_abs, previous_value),
    }


def _baseline_point(
    numeric_points: list[dict[str, float | int | None]],
    latest: dict[str, float | int | None] | None,
    window_seconds: int | None,
) -> dict[str, float | int | None] | None:
    if latest is None or len(numeric_points) < 2:
        return None
    if window_seconds is None:
        return numeric_points[0]

    latest_timestamp = _timestamp_or_none(latest.get("t"))
    if latest_timestamp is None:
        return numeric_points[0]

    target_timestamp = latest_timestamp - window_seconds
    candidates = [
        point
        for point in numeric_points[:-1]
        if (timestamp := _timestamp_or_none(point.get("t"))) is not None
        and timestamp <= target_timestamp
    ]
    return candidates[-1] if candidates else numeric_points[0]


def summarize_whale_movement(whale_cohort: dict[str, Any]) -> dict[str, Any]:
    change_abs = _numeric_or_none(whale_cohort.get("change_abs"))
    direction = "flat"
    if change_abs is not None and change_abs > 0:
        direction = "accumulation"
    elif change_abs is not None and change_abs < 0:
        direction = "distribution"
    return {
        "threshold_btc": WHALE_ALERT_THRESHOLD_BTC,
        "change_abs": change_abs,
        "direction": direction,
        "alert": change_abs is not None and abs(change_abs) >= WHALE_ALERT_THRESHOLD_BTC,
    }


def alerts_for_whale_movement(
    whale_movement: dict[str, Any],
    window: str,
) -> list[dict[str, Any]]:
    if not whale_movement.get("alert"):
        return []
    return [
        {
            "type": "whale-alert",
            "threshold_btc": WHALE_ALERT_THRESHOLD_BTC,
            "change_abs": whale_movement.get("change_abs"),
            "direction": whale_movement.get("direction"),
            "window": window,
        }
    ]


def _numeric_points(points: list[dict[str, Any]]) -> list[dict[str, float | int | None]]:
    numeric: list[dict[str, float | int | None]] = []
    for point in sorted(points, key=_point_sort_key):
        value = _numeric_or_none(point.get("v"))
        if value is None:
            continue
        timestamp = _timestamp_or_none(point.get("t"))
        numeric.append({"t": timestamp, "v": value})
    return numeric


def _change_abs(latest: Any, previous: Any) -> float | None:
    latest_value = _numeric_or_none(latest)
    previous_value = _numeric_or_none(previous)
    if latest_value is None or previous_value is None:
        return None
    return latest_value - previous_value


def _change_pct(change_abs: Any, previous: Any) -> float | None:
    change_value = _numeric_or_none(change_abs)
    previous_value = _numeric_or_none(previous)
    if change_value is None or previous_value is None:
        return None
    if previous_value == 0:
        return 0.0 if change_value == 0 else None
    return (change_value / previous_value) * 100.0


def _share_pct(value: Any, represented_supply: float) -> float | None:
    numeric = _numeric_or_none(value)
    if numeric is None or represented_supply <= 0:
        return None
    return (numeric / represented_supply) * 100.0


def _sum_optional(values: Any) -> float | None:
    total = 0.0
    found = False
    for value in values:
        numeric = _numeric_or_none(value)
        if numeric is None:
            continue
        total += numeric
        found = True
    return total if found else None


def _max_timestamp(values: Any) -> int | None:
    timestamps = [
        value for value in (_timestamp_or_none(value) for value in values) if value is not None
    ]
    return max(timestamps) if timestamps else None


def _min_timestamp(values: Any) -> int | None:
    timestamps = [
        value for value in (_timestamp_or_none(value) for value in values) if value is not None
    ]
    return min(timestamps) if timestamps else None


def _point_sort_key(point: dict[str, Any]) -> tuple[int, float]:
    timestamp = _numeric_or_none(point.get("t"))
    if timestamp is None:
        return (1, math.inf)
    return (0, timestamp)


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _timestamp_or_none(value: Any) -> int | None:
    numeric = _numeric_or_none(value)
    if numeric is None:
        return None
    return int(numeric)


def _numeric_or_none(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(parsed):
        return None
    return parsed


_SERVICE: SupplyDistributionService | None = None


def get_supply_distribution_service() -> SupplyDistributionService:
    global _SERVICE
    if _SERVICE is None:
        _SERVICE = SupplyDistributionService()
    return _SERVICE
