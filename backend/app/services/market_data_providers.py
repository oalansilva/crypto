"""Market data providers shared by backtest and opportunity monitor flows."""

from __future__ import annotations

import io
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Protocol

import httpx
import pandas as pd

from src.data.incremental_loader import IncrementalLoader

logger = logging.getLogger(__name__)

CCXT_SOURCE = "ccxt"
STOOQ_SOURCE = "stooq"

_CCXT_ALIASES = {"", "ccxt", "binance", "crypto", "default"}
_STOOQ_ALIASES = {"stooq", "stooq-eod", "stooq_eod"}


class MarketDataProvider(Protocol):
    source: str

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        since_str: Optional[str] = None,
        until_str: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        """Fetch OHLCV candles with a normalized dataframe contract."""


def normalize_data_source(data_source: Optional[str]) -> str:
    raw = str(data_source or "").strip().lower()
    if raw in _CCXT_ALIASES:
        return CCXT_SOURCE
    if raw in _STOOQ_ALIASES:
        return STOOQ_SOURCE
    raise ValueError(
        f"Unsupported data_source '{data_source}'. "
        "Supported values: 'ccxt' (default) or 'stooq'."
    )


def validate_data_source_timeframe(data_source: Optional[str], timeframe: str) -> str:
    source = normalize_data_source(data_source)
    tf = str(timeframe or "").strip().lower()
    if source == STOOQ_SOURCE and tf != "1d":
        raise ValueError("data_source=stooq supports only timeframe='1d' (EOD).")
    return source


def resolve_data_source_for_symbol(symbol: str, data_source: Optional[str] = None) -> str:
    if data_source is not None and str(data_source).strip():
        return normalize_data_source(data_source)
    # Fallback used by monitor/favorites: symbols without "/" are treated as US tickers.
    return STOOQ_SOURCE if "/" not in str(symbol or "") else CCXT_SOURCE


class CcxtMarketDataProvider:
    source = CCXT_SOURCE

    def __init__(self, loader: Optional[IncrementalLoader] = None):
        self.loader = loader or IncrementalLoader()

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        since_str: Optional[str] = None,
        until_str: Optional[str] = None,
        limit: Optional[int] = None,
        full_history_if_empty: bool = True,
    ) -> pd.DataFrame:
        return self.loader.fetch_data(
            symbol=symbol,
            timeframe=timeframe,
            since_str=since_str,
            until_str=until_str,
            limit=limit,
            full_history_if_empty=full_history_if_empty,
        )


class StooqEodProvider:
    """Free EOD-only US stock/ETF provider using Stooq CSV endpoint."""

    source = STOOQ_SOURCE
    DEFAULT_TTL_SECONDS = 12 * 60 * 60  # 12h is sufficient for daily EOD updates.
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_RETRY_BACKOFF_SECONDS = 1.0
    DEFAULT_TIMEOUT_SECONDS = 20.0

    def __init__(
        self,
        cache_dir: Optional[Path | str] = None,
        ttl_seconds: int = DEFAULT_TTL_SECONDS,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_backoff_seconds: float = DEFAULT_RETRY_BACKOFF_SECONDS,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    ):
        project_root = Path(__file__).resolve().parents[3]
        self.cache_dir = (
            Path(cache_dir) if cache_dir else (project_root / "data" / "storage" / "stooq")
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = max(60, int(ttl_seconds))
        self.max_retries = max(1, int(max_retries))
        self.retry_backoff_seconds = max(0.1, float(retry_backoff_seconds))
        self.timeout_seconds = max(1.0, float(timeout_seconds))

    @staticmethod
    def map_symbol(symbol: str) -> str:
        raw = str(symbol or "").strip()
        if not raw:
            raise ValueError("Stooq symbol must not be empty.")

        lowered = raw.lower().replace(" ", "")
        if lowered.endswith(".us"):
            base = lowered[:-3]
        else:
            if "/" in lowered:
                raise ValueError(
                    f"Invalid US ticker '{symbol}'. Use plain tickers like 'AAPL' for data_source=stooq."
                )
            base = lowered

        base = base.replace(".", "-").replace("_", "-")
        if not base or not base.replace("-", "").isalnum():
            raise ValueError(f"Invalid US ticker '{symbol}'. Allowed examples: AAPL, SPY, BRK.B.")
        return f"{base}.us"

    @staticmethod
    def _parse_datetime_utc(value: Optional[str]) -> Optional[pd.Timestamp]:
        if value is None:
            return None
        if isinstance(value, str) and value.strip() == "":
            return None
        ts = pd.to_datetime(value, errors="coerce")
        if pd.isna(ts):
            return None
        if getattr(ts, "tz", None) is None:
            return ts.tz_localize("UTC")
        return ts.tz_convert("UTC")

    @staticmethod
    def _is_protected_stooq_payload(body: str) -> bool:
        if not isinstance(body, str):
            return False
        lower = body.lower()
        return (
            "get your apikey" in lower
            or "captcha" in lower
            or "api key required" in lower
            or "protected response" in lower
        )

    def _normalize_timeframe(self, timeframe: str) -> str:
        tf = str(timeframe or "").strip().lower()
        if tf != "1d":
            raise ValueError("Stooq provider supports only timeframe '1d' (EOD candles).")
        return tf

    def _cache_paths(self, provider_symbol: str, timeframe: str) -> tuple[Path, Path]:
        safe_symbol = provider_symbol.replace("/", "_").replace(".", "_")
        stem = f"{safe_symbol}_{timeframe}"
        return self.cache_dir / f"{stem}.parquet", self.cache_dir / f"{stem}.meta.json"

    def _is_cache_fresh(self, meta_path: Path) -> bool:
        if not meta_path.exists():
            return False
        try:
            payload = json.loads(meta_path.read_text(encoding="utf-8"))
            fetched_at = str(payload.get("fetched_at") or "").strip()
            if not fetched_at:
                return False
            ts = datetime.fromisoformat(fetched_at)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            age_seconds = (datetime.now(timezone.utc) - ts).total_seconds()
            return age_seconds < self.ttl_seconds
        except Exception:
            return False

    @staticmethod
    def _slice_dataframe(
        df: pd.DataFrame,
        since_str: Optional[str] = None,
        until_str: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        if df.empty:
            return df
        out = df.copy()
        since_dt = StooqEodProvider._parse_datetime_utc(since_str)
        until_dt = StooqEodProvider._parse_datetime_utc(until_str)
        if since_dt is not None:
            out = out[out.index >= since_dt]
        if until_dt is not None:
            out = out[out.index <= until_dt]
        if isinstance(limit, int) and limit > 0:
            out = out.tail(limit)
        return out

    @staticmethod
    def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        if "timestamp_utc" not in out.columns:
            if "time" in out.columns:
                out["timestamp_utc"] = pd.to_datetime(out["time"], utc=True, errors="coerce")
            elif "timestamp" in out.columns:
                out["timestamp_utc"] = pd.to_datetime(
                    out["timestamp"], unit="ms", utc=True, errors="coerce"
                )

        if "time" not in out.columns and "timestamp_utc" in out.columns:
            out["time"] = pd.to_datetime(out["timestamp_utc"], utc=True, errors="coerce")

        if "timestamp" not in out.columns and "timestamp_utc" in out.columns:
            out["timestamp"] = (
                pd.to_datetime(out["timestamp_utc"], utc=True, errors="coerce").astype("int64")
                // 1_000_000
            )

        if "timestamp_utc" in out.columns:
            out["timestamp_utc"] = pd.to_datetime(out["timestamp_utc"], utc=True, errors="coerce")
            out = out.dropna(subset=["timestamp_utc"])
            out = out.sort_values("timestamp_utc")
            out = out.set_index("timestamp_utc", drop=False)

        for col in ("open", "high", "low", "close", "volume"):
            if col not in out.columns:
                out[col] = 0.0
            out[col] = pd.to_numeric(out[col], errors="coerce")

        out = out.dropna(subset=["open", "high", "low", "close"])
        out["volume"] = out["volume"].fillna(0.0)

        required = ["timestamp", "timestamp_utc", "time", "open", "high", "low", "close", "volume"]
        return out[[c for c in required if c in out.columns]]

    def _load_cache(self, parquet_path: Path) -> Optional[pd.DataFrame]:
        if not parquet_path.exists():
            return None
        try:
            df = pd.read_parquet(parquet_path)
            if df.empty:
                return None
            return self._standardize_columns(df)
        except Exception as exc:
            logger.warning("Stooq cache read failed (%s): %s", parquet_path, exc)
            return None

    def _save_cache(
        self,
        df: pd.DataFrame,
        parquet_path: Path,
        meta_path: Path,
        provider_symbol: str,
        timeframe: str,
    ) -> None:
        try:
            parquet_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_parquet(parquet_path, index=False)
            meta = {
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "source": self.source,
                "provider_symbol": provider_symbol,
                "timeframe": timeframe,
                "rows": int(len(df)),
            }
            meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as exc:
            logger.warning("Failed writing Stooq cache for %s: %s", provider_symbol, exc)

    def _download_csv(self, provider_symbol: str) -> str:
        url = "https://stooq.com/q/d/l/"
        last_error: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                response = httpx.get(
                    url,
                    params={"s": provider_symbol, "i": "d"},
                    timeout=self.timeout_seconds,
                )
                response.raise_for_status()
                body = response.text.strip()
                if not body:
                    raise ValueError("empty response body")
                if self._is_protected_stooq_payload(body):
                    raise ValueError(
                        f"Stooq returned protected response for '{provider_symbol}' (API key required)."
                    )
                if "no data" in body.lower():
                    raise ValueError(
                        f"No EOD data returned by Stooq for symbol '{provider_symbol}'."
                    )
                return body
            except Exception as exc:
                last_error = exc
                if attempt < self.max_retries:
                    wait_s = self.retry_backoff_seconds * (2 ** (attempt - 1))
                    time.sleep(wait_s)

        raise ValueError(
            f"Stooq request failed for symbol '{provider_symbol}' after {self.max_retries} attempts: {last_error}"
        )

    def _parse_stooq_csv(self, csv_text: str, provider_symbol: str) -> pd.DataFrame:
        try:
            df = pd.read_csv(io.StringIO(csv_text))
        except Exception as exc:
            raise ValueError(f"Failed parsing Stooq CSV for '{provider_symbol}': {exc}") from exc

        if df.empty:
            raise ValueError(f"Stooq returned no rows for '{provider_symbol}'.")

        lowered = {c: c.strip().lower() for c in df.columns}
        df = df.rename(columns=lowered)
        if "date" not in df.columns:
            raise ValueError(
                f"Unexpected Stooq payload for '{provider_symbol}': missing 'Date' column."
            )

        df = df.rename(columns={"date": "time"})
        for col in ("open", "high", "low", "close"):
            if col not in df.columns:
                raise ValueError(
                    f"Unexpected Stooq payload for '{provider_symbol}': missing '{col}' column."
                )

        if "volume" not in df.columns:
            df["volume"] = 0

        df["time"] = pd.to_datetime(df["time"], utc=True, errors="coerce")
        df = df.dropna(subset=["time"])

        for col in ("open", "high", "low", "close", "volume"):
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df.dropna(subset=["open", "high", "low", "close"])
        df["volume"] = df["volume"].fillna(0.0)

        df = df.sort_values("time").reset_index(drop=True)
        df["timestamp"] = (df["time"].astype("int64") // 1_000_000).astype("int64")
        df["timestamp_utc"] = df["time"]
        df = df[["timestamp", "timestamp_utc", "time", "open", "high", "low", "close", "volume"]]
        df = df.set_index("timestamp_utc", drop=False)
        return df

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        since_str: Optional[str] = None,
        until_str: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        tf = self._normalize_timeframe(timeframe)
        provider_symbol = self.map_symbol(symbol)
        parquet_path, meta_path = self._cache_paths(provider_symbol, tf)

        cached_df = self._load_cache(parquet_path)
        if cached_df is not None and self._is_cache_fresh(meta_path):
            return self._slice_dataframe(
                cached_df, since_str=since_str, until_str=until_str, limit=limit
            )

        try:
            csv_text = self._download_csv(provider_symbol)
            fresh_df = self._parse_stooq_csv(csv_text, provider_symbol=provider_symbol)
            self._save_cache(fresh_df, parquet_path, meta_path, provider_symbol, tf)
            return self._slice_dataframe(
                fresh_df, since_str=since_str, until_str=until_str, limit=limit
            )
        except Exception as exc:
            protected_source = self._is_protected_stooq_payload(str(exc))
            if cached_df is not None:
                if protected_source:
                    logger.warning(
                        "Stooq refresh blocked for %s; forcing caller-level fallback for '%s'.",
                        provider_symbol,
                        symbol,
                    )
                    raise
                logger.warning(
                    "Stooq refresh failed for %s; serving stale cache (%d rows): %s",
                    provider_symbol,
                    len(cached_df),
                    exc,
                )
                return self._slice_dataframe(
                    cached_df, since_str=since_str, until_str=until_str, limit=limit
                )
            if isinstance(exc, ValueError):
                raise
            raise ValueError(f"Failed fetching Stooq EOD data for '{symbol}': {exc}") from exc


class YahooMarketDataProvider:
    """Yahoo Finance provider used for US stocks intraday and daily candles."""

    source = "yahoo"
    DEFAULT_TIMEOUT_SECONDS = 20.0
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_RETRY_BACKOFF_SECONDS = 1.0
    _REQUEST_HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
    }

    _VALID_TIMEFRAMES = {"15m", "1h", "4h", "1d"}
    _DEFAULT_RANGE_BY_TF = {
        "15m": "1mo",  # ~30d
        "1h": "6mo",  # ~180d
        "4h": "1y",  # ~365d (aggregated from 1h)
        "1d": "10y",  # years
    }
    _INTERVAL_BY_TF = {
        "15m": "15m",
        "1h": "60m",
        "4h": "60m",
        "1d": "1d",
    }

    def __init__(
        self,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_backoff_seconds: float = DEFAULT_RETRY_BACKOFF_SECONDS,
    ):
        self.timeout_seconds = max(1.0, float(timeout_seconds))
        self.max_retries = max(1, int(max_retries))
        self.retry_backoff_seconds = max(0.2, float(retry_backoff_seconds))

    @staticmethod
    def _normalize_symbol(symbol: str) -> str:
        raw = str(symbol or "").strip().upper()
        if not raw:
            raise ValueError("Symbol must not be empty.")
        if "/" in raw:
            raise ValueError("Yahoo provider expects stock tickers without '/'.")
        return raw

    @classmethod
    def _normalize_timeframe(cls, timeframe: str) -> str:
        tf = str(timeframe or "").strip().lower()
        if tf not in cls._VALID_TIMEFRAMES:
            supported = ", ".join(sorted(cls._VALID_TIMEFRAMES))
            raise ValueError(f"Unsupported Yahoo timeframe '{timeframe}'. Supported: {supported}.")
        return tf

    @staticmethod
    def _range_for_since(since_str: Optional[str], default_range: str) -> str:
        since_dt = StooqEodProvider._parse_datetime_utc(since_str)
        if since_dt is None:
            return default_range

        days = max(1, int((datetime.now(timezone.utc) - since_dt.to_pydatetime()).days))
        if days <= 5:
            return "5d"
        if days <= 30:
            return "1mo"
        if days <= 90:
            return "3mo"
        if days <= 180:
            return "6mo"
        if days <= 365:
            return "1y"
        if days <= 365 * 2:
            return "2y"
        if days <= 365 * 5:
            return "5y"
        if days <= 365 * 10:
            return "10y"
        return "max"

    @staticmethod
    def _parse_payload(payload: dict, symbol: str) -> pd.DataFrame:
        chart = (payload or {}).get("chart") or {}
        if chart.get("error"):
            message = (
                chart["error"].get("description")
                or chart["error"].get("code")
                or "unknown yahoo error"
            )
            raise ValueError(f"Yahoo request failed for '{symbol}': {message}")

        result = chart.get("result") or []
        if not result:
            raise ValueError(f"No Yahoo candles returned for '{symbol}'.")

        row = result[0] or {}
        timestamps = row.get("timestamp") or []
        indicators = row.get("indicators") or {}
        quotes = (indicators.get("quote") or [{}])[0] or {}

        opens = quotes.get("open") or []
        highs = quotes.get("high") or []
        lows = quotes.get("low") or []
        closes = quotes.get("close") or []
        volumes = quotes.get("volume") or []

        rows: list[dict] = []
        total = min(len(timestamps), len(opens), len(highs), len(lows), len(closes))
        for idx in range(total):
            ts = timestamps[idx]
            o = opens[idx]
            h = highs[idx]
            l = lows[idx]
            c = closes[idx]
            v = volumes[idx] if idx < len(volumes) else 0
            if ts is None or o is None or h is None or l is None or c is None:
                continue
            t = pd.to_datetime(int(ts), unit="s", utc=True)
            rows.append(
                {
                    "time": t,
                    "timestamp_utc": t,
                    "timestamp": int(t.value // 1_000_000),
                    "open": float(o),
                    "high": float(h),
                    "low": float(l),
                    "close": float(c),
                    "volume": float(v or 0),
                }
            )

        if not rows:
            raise ValueError(f"Yahoo returned no valid OHLC rows for '{symbol}'.")

        df = pd.DataFrame(rows).sort_values("timestamp_utc")
        df = df.set_index("timestamp_utc", drop=False)
        return df

    @staticmethod
    def _aggregate_to_4h(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df

        agg = (
            df.resample("4h", on="timestamp_utc")
            .agg(
                {
                    "open": "first",
                    "high": "max",
                    "low": "min",
                    "close": "last",
                    "volume": "sum",
                }
            )
            .dropna(subset=["open", "high", "low", "close"])
            .reset_index()
        )

        if agg.empty:
            return agg

        agg["time"] = pd.to_datetime(agg["timestamp_utc"], utc=True)
        agg["timestamp"] = (agg["time"].astype("int64") // 1_000_000).astype("int64")
        agg = agg[["timestamp", "timestamp_utc", "time", "open", "high", "low", "close", "volume"]]
        agg = agg.set_index("timestamp_utc", drop=False).sort_index()
        return agg

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        since_str: Optional[str] = None,
        until_str: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        ticker = self._normalize_symbol(symbol)
        tf = self._normalize_timeframe(timeframe)

        interval = self._INTERVAL_BY_TF[tf]
        range_param = self._range_for_since(since_str, self._DEFAULT_RANGE_BY_TF[tf])
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"

        payload: dict = {}
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = httpx.get(
                    url,
                    params={
                        "interval": interval,
                        "range": range_param,
                        "includePrePost": "false",
                        "events": "div,splits",
                    },
                    headers=self._REQUEST_HEADERS,
                    timeout=self.timeout_seconds,
                )
                if response.status_code == 429:
                    raise ValueError(f"HTTP 429 Too Many Requests from Yahoo for '{ticker}'.")
                response.raise_for_status()
                payload = response.json()
                break
            except Exception as exc:
                last_error = exc
                if attempt < self.max_retries and isinstance(exc, ValueError) and "429" in str(exc):
                    time.sleep(self.retry_backoff_seconds * (2 ** (attempt - 1)))
                    continue
                if attempt >= self.max_retries:
                    raise ValueError(f"Yahoo request failed for '{ticker}': {exc}") from exc
                time.sleep(self.retry_backoff_seconds)
                continue

        out = self._parse_payload(payload, symbol=ticker)
        if tf == "4h":
            out = self._aggregate_to_4h(out)

        since_dt = StooqEodProvider._parse_datetime_utc(since_str)
        until_dt = StooqEodProvider._parse_datetime_utc(until_str)
        if since_dt is not None:
            out = out[out.index >= since_dt]
        if until_dt is not None:
            out = out[out.index <= until_dt]
        if isinstance(limit, int) and limit > 0:
            out = out.tail(limit)

        return out


_PROVIDERS: dict[str, MarketDataProvider] = {}


def get_market_data_provider(data_source: Optional[str]) -> MarketDataProvider:
    source = normalize_data_source(data_source)
    provider = _PROVIDERS.get(source)
    if provider is not None:
        return provider

    if source == STOOQ_SOURCE:
        provider = StooqEodProvider()
    else:
        provider = CcxtMarketDataProvider()

    _PROVIDERS[source] = provider
    return provider


class AlphaVantageMarketDataProvider:
    """Free-tier intraday stock candles via Alpha Vantage.

    Notes:
    - Requires env var ALPHAVANTAGE_API_KEY.
    - Rate-limited; should be used as fallback behind caching.
    """

    source = "alphavantage"
    DEFAULT_TIMEOUT_SECONDS = 20.0

    _INTERVAL_MAP = {
        "15m": "15min",
        "1h": "60min",
        # Alpha Vantage does not provide 4h directly. We'll use 60min and resample.
        "4h": "60min",
        "1d": "Daily",
    }

    def __init__(self, api_key: str, timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS):
        self.api_key = str(api_key or "").strip()
        if not self.api_key:
            raise ValueError("ALPHAVANTAGE_API_KEY is not configured")
        self.timeout_seconds = max(1.0, float(timeout_seconds))

    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        since_str: Optional[str] = None,
        until_str: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        tf = str(timeframe or "").strip().lower()
        interval = self._INTERVAL_MAP.get(tf)
        if interval is None:
            raise ValueError(f"Alpha Vantage does not support timeframe '{timeframe}'.")

        raw_symbol = str(symbol or "").strip().upper()
        if not raw_symbol or "/" in raw_symbol:
            raise ValueError(f"Alpha Vantage expects a stock ticker (e.g. AAPL). Got '{symbol}'.")

        # Alpha Vantage endpoints
        if tf == "1d":
            url = "https://www.alphavantage.co/query"
            params = {
                "function": "TIME_SERIES_DAILY_ADJUSTED",
                "symbol": raw_symbol,
                "outputsize": "compact",
                "apikey": self.api_key,
            }
            r = httpx.get(url, params=params, timeout=self.timeout_seconds)
            if r.status_code == 429:
                raise RuntimeError("Alpha Vantage rate limited (HTTP 429)")
            r.raise_for_status()
            payload = r.json()
            series = payload.get("Time Series (Daily)")
            if not isinstance(series, dict) or not series:
                raise RuntimeError(f"Alpha Vantage returned no daily data for {raw_symbol}")

            rows = []
            for date_str, values in series.items():
                rows.append(
                    {
                        "timestamp_utc": pd.to_datetime(date_str, utc=True),
                        "open": float(values.get("1. open")),
                        "high": float(values.get("2. high")),
                        "low": float(values.get("3. low")),
                        "close": float(values.get("4. close")),
                        "volume": float(values.get("6. volume", 0) or 0),
                    }
                )
            df = pd.DataFrame(rows).sort_values("timestamp_utc")
            df["time"] = df["timestamp_utc"]
            df["timestamp"] = df["timestamp_utc"].astype("int64") // 1_000_000
            df = df[
                ["timestamp", "timestamp_utc", "time", "open", "high", "low", "close", "volume"]
            ]
            df = df.set_index("timestamp_utc", drop=False)
            return StooqEodProvider._slice_dataframe(
                df, since_str=since_str, until_str=until_str, limit=limit
            )

        # intraday
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_INTRADAY",
            "symbol": raw_symbol,
            "interval": interval,
            "outputsize": "compact",
            "apikey": self.api_key,
        }
        r = httpx.get(url, params=params, timeout=self.timeout_seconds)
        if r.status_code == 429:
            raise RuntimeError("Alpha Vantage rate limited (HTTP 429)")
        r.raise_for_status()
        payload = r.json()
        key = f"Time Series ({interval})"
        series = payload.get(key)
        if not isinstance(series, dict) or not series:
            # AlphaVantage returns {"Note": ...} when throttled
            note = payload.get("Note") or payload.get("Information")
            if note:
                raise RuntimeError(str(note))
            raise RuntimeError(f"Alpha Vantage returned no intraday data for {raw_symbol}")

        rows = []
        for ts_str, values in series.items():
            t = pd.to_datetime(ts_str, utc=True)
            rows.append(
                {
                    "timestamp_utc": t,
                    "open": float(values.get("1. open")),
                    "high": float(values.get("2. high")),
                    "low": float(values.get("3. low")),
                    "close": float(values.get("4. close")),
                    "volume": float(values.get("5. volume", 0) or 0),
                }
            )

        df = pd.DataFrame(rows).sort_values("timestamp_utc")
        df["time"] = df["timestamp_utc"]
        df["timestamp"] = df["timestamp_utc"].astype("int64") // 1_000_000
        df = df[["timestamp", "timestamp_utc", "time", "open", "high", "low", "close", "volume"]]
        df = df.set_index("timestamp_utc", drop=False)

        if tf == "4h":
            # Aggregate 60m candles into 4h.
            agg = (
                df.resample("4h", on="timestamp_utc")
                .agg(
                    {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"}
                )
                .dropna(subset=["open", "high", "low", "close"])
                .reset_index()
            )
            agg["time"] = pd.to_datetime(agg["timestamp_utc"], utc=True)
            agg["timestamp"] = (
                pd.to_datetime(agg["timestamp_utc"], utc=True).astype("int64") // 1_000_000
            )
            agg = agg[
                ["timestamp", "timestamp_utc", "time", "open", "high", "low", "close", "volume"]
            ]
            agg = agg.set_index("timestamp_utc", drop=False).sort_index()
            df = agg

        return StooqEodProvider._slice_dataframe(
            df, since_str=since_str, until_str=until_str, limit=limit
        )
