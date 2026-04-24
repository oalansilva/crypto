from __future__ import annotations

import asyncio
import math
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import httpx

from app.config import get_settings

SUPPORTED_GLASSNODE_ASSETS = {"BTC", "ETH"}
DEFAULT_GLASSNODE_INTERVAL = "24h"
GLASSNODE_METRICS: dict[str, str] = {
    "mvrv": "/v1/metrics/market/mvrv",
    "nvt": "/v1/metrics/indicators/nvt",
    "realized_cap": "/v1/metrics/market/marketcap_realized_usd",
    "sopr": "/v1/metrics/indicators/sopr",
}


class GlassnodeConfigError(RuntimeError):
    pass


class GlassnodeRateLimitError(RuntimeError):
    pass


@dataclass(frozen=True)
class GlassnodeMetricSeries:
    metric: str
    asset: str
    interval: str
    endpoint: str
    points: list[dict[str, Any]]
    fetched_at: datetime
    cached_until: datetime
    cached: bool

    @property
    def latest(self) -> dict[str, Any] | None:
        return self.points[-1] if self.points else None

    def as_dict(self) -> dict[str, Any]:
        return {
            "metric": self.metric,
            "asset": self.asset,
            "interval": self.interval,
            "endpoint": self.endpoint,
            "points": list(self.points),
            "latest": self.latest,
            "fetched_at": self.fetched_at,
            "cached_until": self.cached_until,
            "cached": self.cached,
        }


class GlassnodeService:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        cache_ttl_seconds: int | None = None,
        rate_limit_per_minute: int | None = None,
        client: httpx.AsyncClient | None = None,
        sleep=asyncio.sleep,
        monotonic=time.monotonic,
        now=None,
    ) -> None:
        settings = get_settings()
        self.api_key = (api_key if api_key is not None else settings.glassnode_api_key) or ""
        self.base_url = (base_url if base_url is not None else settings.glassnode_base_url).rstrip(
            "/"
        )
        self.cache_ttl_seconds = int(
            cache_ttl_seconds
            if cache_ttl_seconds is not None
            else settings.glassnode_cache_ttl_seconds
        )
        self.rate_limit_per_minute = int(
            rate_limit_per_minute
            if rate_limit_per_minute is not None
            else settings.glassnode_rate_limit_per_minute
        )
        self._client = client
        self._owns_client = client is None
        self._sleep = sleep
        self._monotonic = monotonic
        self._now = now or (lambda: datetime.now(timezone.utc))
        self._cache: dict[tuple[str, str, str, int | None, int | None], GlassnodeMetricSeries] = {}
        self._cache_expires_at: dict[tuple[str, str, str, int | None, int | None], float] = {}
        self._rate_lock = asyncio.Lock()
        self._last_request_at: float | None = None

    async def close(self) -> None:
        if self._owns_client and self._client is not None:
            await self._client.aclose()
            self._client = None

    async def fetch_metrics(
        self,
        asset: str,
        *,
        interval: str = DEFAULT_GLASSNODE_INTERVAL,
        since: int | None = None,
        until: int | None = None,
    ) -> dict[str, Any]:
        normalized_asset = self._normalize_asset(asset)
        metric_rows = []
        for metric in GLASSNODE_METRICS:
            row = await self.fetch_metric(
                metric,
                normalized_asset,
                interval=interval,
                since=since,
                until=until,
            )
            metric_rows.append(row.as_dict())
        return {
            "asset": normalized_asset,
            "interval": interval,
            "cached": all(row["cached"] for row in metric_rows),
            "metrics": metric_rows,
        }

    async def fetch_metric(
        self,
        metric: str,
        asset: str,
        *,
        interval: str = DEFAULT_GLASSNODE_INTERVAL,
        since: int | None = None,
        until: int | None = None,
    ) -> GlassnodeMetricSeries:
        normalized_metric = self._normalize_metric(metric)
        normalized_asset = self._normalize_asset(asset)
        cache_key = (normalized_metric, normalized_asset, interval, since, until)
        cached = self._read_cache(cache_key)
        if cached is not None:
            return GlassnodeMetricSeries(
                metric=cached.metric,
                asset=cached.asset,
                interval=cached.interval,
                endpoint=cached.endpoint,
                points=cached.points,
                fetched_at=cached.fetched_at,
                cached_until=cached.cached_until,
                cached=True,
            )

        if not self.api_key.strip():
            raise GlassnodeConfigError("GLASSNODE_API_KEY is required to fetch Glassnode metrics")

        await self._respect_rate_limit()
        endpoint = GLASSNODE_METRICS[normalized_metric]
        client = self._get_client()
        params: dict[str, Any] = {
            "a": normalized_asset,
            "i": interval,
            "f": "json",
        }
        if since is not None:
            params["s"] = int(since)
        if until is not None:
            params["u"] = int(until)

        response = await client.get(
            f"{self.base_url}{endpoint}",
            params=params,
            headers={"X-Api-Key": self.api_key},
        )
        if response.status_code == 429:
            raise GlassnodeRateLimitError("Glassnode API rate limit exceeded")
        response.raise_for_status()

        fetched_at = self._now()
        cached_until = datetime.fromtimestamp(
            fetched_at.timestamp() + self.cache_ttl_seconds,
            tz=timezone.utc,
        )
        series = GlassnodeMetricSeries(
            metric=normalized_metric,
            asset=normalized_asset,
            interval=interval,
            endpoint=endpoint,
            points=self._normalize_points(response.json()),
            fetched_at=fetched_at,
            cached_until=cached_until,
            cached=False,
        )
        self._write_cache(cache_key, series)
        return series

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=float(get_settings().glassnode_request_timeout_seconds)
            )
        return self._client

    async def _respect_rate_limit(self) -> None:
        if self.rate_limit_per_minute <= 0:
            return
        min_interval = 60.0 / float(self.rate_limit_per_minute)
        async with self._rate_lock:
            now = self._monotonic()
            if self._last_request_at is not None:
                wait_seconds = min_interval - (now - self._last_request_at)
                if wait_seconds > 0:
                    await self._sleep(wait_seconds)
                    now = self._monotonic()
            self._last_request_at = now

    def _read_cache(
        self, key: tuple[str, str, str, int | None, int | None]
    ) -> GlassnodeMetricSeries | None:
        expires_at = self._cache_expires_at.get(key)
        if expires_at is None:
            return None
        if self._monotonic() >= expires_at:
            self._cache.pop(key, None)
            self._cache_expires_at.pop(key, None)
            return None
        return self._cache.get(key)

    def _write_cache(
        self,
        key: tuple[str, str, str, int | None, int | None],
        value: GlassnodeMetricSeries,
    ) -> None:
        self._cache[key] = value
        self._cache_expires_at[key] = self._monotonic() + self.cache_ttl_seconds

    @staticmethod
    def _normalize_metric(metric: str) -> str:
        normalized = str(metric or "").strip().lower()
        if normalized not in GLASSNODE_METRICS:
            supported = ", ".join(sorted(GLASSNODE_METRICS))
            raise ValueError(f"Unsupported Glassnode metric '{metric}'. Supported: {supported}")
        return normalized

    @staticmethod
    def _normalize_asset(asset: str) -> str:
        normalized = str(asset or "").strip().upper()
        if normalized not in SUPPORTED_GLASSNODE_ASSETS:
            supported = ", ".join(sorted(SUPPORTED_GLASSNODE_ASSETS))
            raise ValueError(f"Unsupported Glassnode asset '{asset}'. Supported: {supported}")
        return normalized

    @staticmethod
    def _normalize_points(payload: Any) -> list[dict[str, Any]]:
        if not isinstance(payload, list):
            return []
        points: list[dict[str, Any]] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            point = dict(item)
            value = point.get("v")
            if isinstance(value, float) and not math.isfinite(value):
                point["v"] = None
            points.append(point)
        return points


_SERVICE: GlassnodeService | None = None


def get_glassnode_service() -> GlassnodeService:
    global _SERVICE
    if _SERVICE is None:
        _SERVICE = GlassnodeService()
    return _SERVICE
