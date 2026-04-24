from __future__ import annotations

import json
import logging
import threading
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import pandas as pd
import talib
from sqlalchemy import text

from app.database import engine
from app.services.chart_pattern_service import detect_chart_patterns

logger = logging.getLogger(__name__)

ACTIVE_TIMEFRAMES = ["1m", "5m", "15m", "1h", "4h", "1d"]
LOOKBACK_BARS = 300
MAX_HISTORY_BARS = 2000

MAX_LOOKBACK_LOOKUP = {
    "1m": timedelta(minutes=1),
    "5m": timedelta(minutes=5),
    "15m": timedelta(minutes=15),
    "1h": timedelta(hours=1),
    "4h": timedelta(hours=4),
    "1d": timedelta(days=1),
}

DEFAULT_TIMEFRAMES = ("1m", "5m", "15m", "1h", "4h", "1d")
PROVIDER_NAME = "talib"
ADVANCED_INDICATOR_COLUMNS = (
    "bb_upper_20_2",
    "bb_middle_20_2",
    "bb_lower_20_2",
    "atr_14",
    "stoch_k_14_3_3",
    "stoch_d_14_3_3",
    "obv",
    "ichimoku_tenkan_9",
    "ichimoku_kijun_26",
    "ichimoku_senkou_a_9_26_52",
    "ichimoku_senkou_b_9_26_52",
    "ichimoku_chikou_26",
)
PIVOT_LEVEL_COLUMNS = (
    "pivot_point",
    "support_1",
    "support_2",
    "support_3",
    "resistance_1",
    "resistance_2",
    "resistance_3",
)


def _normalize_timeframe(value: str) -> str:
    return str(value or "").strip().lower()


def _normalize_symbol(value: str) -> str:
    return str(value or "").strip().upper()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _to_utc_timestamp(value: Any) -> datetime | None:
    if value is None:
        return None
    parsed = pd.to_datetime(value, utc=True, errors="coerce")
    if pd.isna(parsed):
        return None
    if isinstance(parsed, pd.Timestamp):
        parsed = parsed.to_pydatetime()
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _required_interval(tf: str) -> timedelta:
    return MAX_LOOKBACK_LOOKUP.get(_normalize_timeframe(tf), timedelta(hours=1))


def _nullable_float(value: Any) -> float | None:
    return None if pd.isna(value) else float(value)


def _json_or_none(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    if isinstance(value, list) and not value:
        return None
    return json.dumps(value)


def _rolling_midpoint(high: pd.Series, low: pd.Series, period: int) -> pd.Series:
    highest_high = high.rolling(window=period, min_periods=period).max()
    lowest_low = low.rolling(window=period, min_periods=period).min()
    return (highest_high + lowest_low) / 2


def _classic_pivot_levels(
    high: pd.Series, low: pd.Series, close: pd.Series
) -> dict[str, pd.Series]:
    previous_high = high.shift(1)
    previous_low = low.shift(1)
    previous_close = close.shift(1)
    pivot = (previous_high + previous_low + previous_close) / 3
    previous_range = previous_high - previous_low
    return {
        "pivot_point": pivot,
        "support_1": (2 * pivot) - previous_high,
        "support_2": pivot - previous_range,
        "support_3": previous_low - (2 * (previous_high - pivot)),
        "resistance_1": (2 * pivot) - previous_low,
        "resistance_2": pivot + previous_range,
        "resistance_3": previous_high + (2 * (pivot - previous_low)),
    }


class MarketIndicatorService:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._jobs: dict[str, dict[str, Any]] = {}
        self._active: dict[str, str] = {}

    def _resolve_timeframes(self, timeframes: list[str] | None) -> list[str]:
        if not timeframes:
            return list(DEFAULT_TIMEFRAMES)
        normalized = [_normalize_timeframe(tf) for tf in timeframes]
        filtered = [tf for tf in dict.fromkeys(normalized) if tf in ACTIVE_TIMEFRAMES]
        return filtered or list(DEFAULT_TIMEFRAMES)

    def _list_symbols_and_timeframes(self, symbol: str, timeframes: list[str]) -> list[str]:
        normalized_symbol = _normalize_symbol(symbol)
        normalized_timeframes = [_normalize_timeframe(tf) for tf in timeframes]
        with engine.begin() as conn:
            if not normalized_timeframes:
                return []

            rows = conn.execute(
                text("""
                    SELECT DISTINCT timeframe
                    FROM market_ohlcv
                    WHERE symbol = :symbol
                    """),
                {"symbol": normalized_symbol},
            ).fetchall()
        available = {str(r[0]).strip().lower() for r in rows}
        return [tf for tf in normalized_timeframes if tf in available]

    def _fetch_latest_rows(self, symbol: str, timeframe: str, limit: int) -> list[dict[str, Any]]:
        with engine.begin() as conn:
            rows = (
                conn.execute(
                    text("""
                        SELECT
                            symbol,
                            timeframe,
                            ts,
                            ema_9,
                            ema_21,
                            sma_20,
                            sma_50,
                            rsi_14,
                            macd_line,
                            macd_signal,
                            macd_histogram,
                            bb_upper_20_2,
                            bb_middle_20_2,
                            bb_lower_20_2,
                            atr_14,
                            stoch_k_14_3_3,
                            stoch_d_14_3_3,
                            obv,
                            ichimoku_tenkan_9,
                            ichimoku_kijun_26,
                            ichimoku_senkou_a_9_26_52,
                            ichimoku_senkou_b_9_26_52,
                            ichimoku_chikou_26,
                            chart_patterns,
                            pivot_point,
                            support_1,
                            support_2,
                            support_3,
                            resistance_1,
                            resistance_2,
                            resistance_3,
                            source,
                            provider,
                            source_window,
                            row_count,
                            is_recomputed,
                            updated_at
                        FROM market_indicator
                        WHERE symbol = :symbol
                          AND timeframe = :timeframe
                        ORDER BY ts DESC
                        LIMIT :limit
                        """),
                    {
                        "symbol": _normalize_symbol(symbol),
                        "timeframe": _normalize_timeframe(timeframe),
                        "limit": int(limit),
                    },
                )
                .mappings()
                .all()
            )
        return [dict(row) for row in rows]

    def _read_ohlcv(self, symbol: str, timeframe: str, since: datetime | None) -> pd.DataFrame:
        with engine.begin() as conn:
            if since is None:
                rows = (
                    conn.execute(
                        text("""
                            SELECT candle_time, open, high, low, close, volume
                            FROM market_ohlcv
                            WHERE symbol = :symbol
                              AND timeframe = :timeframe
                            ORDER BY candle_time ASC
                            """),
                        {"symbol": _normalize_symbol(symbol), "timeframe": timeframe},
                    )
                    .mappings()
                    .all()
                )
            else:
                rows = (
                    conn.execute(
                        text("""
                            WITH previous_candle AS (
                                SELECT candle_time
                                FROM market_ohlcv
                                WHERE symbol = :symbol
                                  AND timeframe = :timeframe
                                  AND candle_time < :since
                                ORDER BY candle_time DESC
                                LIMIT 1
                            )
                            SELECT candle_time, open, high, low, close, volume
                            FROM market_ohlcv
                            WHERE symbol = :symbol
                              AND timeframe = :timeframe
                              AND (
                                  candle_time >= :since
                                  OR candle_time = (SELECT candle_time FROM previous_candle)
                              )
                            ORDER BY candle_time ASC
                            """),
                        {
                            "symbol": _normalize_symbol(symbol),
                            "timeframe": timeframe,
                            "since": since,
                        },
                    )
                    .mappings()
                    .all()
                )

        if not rows:
            return pd.DataFrame(columns=["ts", "close"])

        df = pd.DataFrame(rows)
        df["ts"] = pd.to_datetime(df["candle_time"], utc=True)
        return df[["ts", "open", "high", "low", "close", "volume"]]

    def _fetch_existing_latest_ts(self, symbol: str, timeframe: str) -> datetime | None:
        with engine.begin() as conn:
            row = conn.execute(
                text("""
                    SELECT MAX(ts) AS ts
                    FROM market_indicator
                    WHERE symbol = :symbol
                      AND timeframe = :timeframe
                    """),
                {"symbol": _normalize_symbol(symbol), "timeframe": timeframe},
            ).fetchone()
        if not row or row[0] is None:
            return None
        return _to_utc_timestamp(row[0])

    def _compute_window_start(self, timeframe: str, base_ts: datetime | None) -> datetime:
        if base_ts is None:
            return _utcnow() - timedelta(days=365 * 2)
        return base_ts - (_required_interval(timeframe) * LOOKBACK_BARS)

    def _compute_indicators(self, df: pd.DataFrame, timeframe: str, symbol: str) -> pd.DataFrame:
        if df.empty:
            return df.copy()

        close = df["close"].astype(float).to_numpy()
        high = df["high"].astype(float).to_numpy()
        low = df["low"].astype(float).to_numpy()
        volume = df["volume"].astype(float).to_numpy()
        ema_9 = talib.EMA(close, timeperiod=9)
        ema_21 = talib.EMA(close, timeperiod=21)
        sma_20 = talib.SMA(close, timeperiod=20)
        sma_50 = talib.SMA(close, timeperiod=50)
        rsi_14 = talib.RSI(close, timeperiod=14)
        macd_line, macd_signal, macd_hist = talib.MACD(
            close, fastperiod=12, slowperiod=26, signalperiod=9
        )
        bb_upper, bb_middle, bb_lower = talib.BBANDS(
            close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0
        )
        atr_14 = talib.ATR(high, low, close, timeperiod=14)
        stoch_k, stoch_d = talib.STOCH(
            high,
            low,
            close,
            fastk_period=14,
            slowk_period=3,
            slowk_matype=0,
            slowd_period=3,
            slowd_matype=0,
        )
        obv = talib.OBV(close, volume)

        numeric_high = pd.to_numeric(df["high"], errors="coerce")
        numeric_low = pd.to_numeric(df["low"], errors="coerce")
        numeric_close = pd.to_numeric(df["close"], errors="coerce")
        ichimoku_tenkan = _rolling_midpoint(numeric_high, numeric_low, 9)
        ichimoku_kijun = _rolling_midpoint(numeric_high, numeric_low, 26)
        ichimoku_senkou_a = (ichimoku_tenkan + ichimoku_kijun) / 2
        ichimoku_senkou_b = _rolling_midpoint(numeric_high, numeric_low, 52)
        ichimoku_chikou = numeric_close
        pivot_levels = _classic_pivot_levels(numeric_high, numeric_low, numeric_close)

        out = df.copy()
        out["ema_9"] = ema_9
        out["ema_21"] = ema_21
        out["sma_20"] = sma_20
        out["sma_50"] = sma_50
        out["rsi_14"] = rsi_14
        out["macd_line"] = macd_line
        out["macd_signal"] = macd_signal
        out["macd_histogram"] = macd_hist
        out["bb_upper_20_2"] = bb_upper
        out["bb_middle_20_2"] = bb_middle
        out["bb_lower_20_2"] = bb_lower
        out["atr_14"] = atr_14
        out["stoch_k_14_3_3"] = stoch_k
        out["stoch_d_14_3_3"] = stoch_d
        out["obv"] = obv
        out["ichimoku_tenkan_9"] = ichimoku_tenkan
        out["ichimoku_kijun_26"] = ichimoku_kijun
        out["ichimoku_senkou_a_9_26_52"] = ichimoku_senkou_a
        out["ichimoku_senkou_b_9_26_52"] = ichimoku_senkou_b
        out["ichimoku_chikou_26"] = ichimoku_chikou
        for column, values in pivot_levels.items():
            out[column] = values
        out["chart_patterns"] = detect_chart_patterns(out)
        out["symbol"] = _normalize_symbol(symbol)
        out["timeframe"] = _normalize_timeframe(timeframe)
        out["source"] = "technical"
        out["provider"] = PROVIDER_NAME
        out["row_count"] = int(len(out))
        source_window = {
            "timeframe": timeframe,
            "engine": PROVIDER_NAME,
            "lookback_bars": LOOKBACK_BARS,
            "max_history_bars": MAX_HISTORY_BARS,
            "advanced_indicators": {
                "bollinger": {"length": 20, "stddev": 2, "matype": "sma"},
                "atr": {"length": 14, "smoothing": "talib_atr_wilder"},
                "stochastic": {"fast_k": 14, "slow_k": 3, "slow_d": 3, "matype": "sma"},
                "obv": {"inputs": ["close", "volume"]},
                "ichimoku": {
                    "tenkan": 9,
                    "kijun": 26,
                    "senkou_b": 52,
                    "displacement": 26,
                    "storage": "source_candle_aligned",
                },
            },
            "support_resistance": {
                "pivot": {
                    "method": "classic",
                    "source": "previous_candle_ohlc",
                    "levels": [
                        "pivot_point",
                        "support_1",
                        "support_2",
                        "support_3",
                        "resistance_1",
                        "resistance_2",
                        "resistance_3",
                    ],
                },
            },
        }
        out["source_window"] = [source_window] * len(out)
        return out

    def _upsert_indicators(self, rows: pd.DataFrame, *, is_recomputed: bool) -> None:
        if rows.empty:
            return

        write_rows = []
        for _, row in rows.iterrows():
            write_rows.append(
                {
                    "symbol": row["symbol"],
                    "timeframe": row["timeframe"],
                    "ts": row["ts"].to_pydatetime(),
                    "ema_9": _nullable_float(row["ema_9"]),
                    "ema_21": _nullable_float(row["ema_21"]),
                    "sma_20": _nullable_float(row["sma_20"]),
                    "sma_50": _nullable_float(row["sma_50"]),
                    "rsi_14": _nullable_float(row["rsi_14"]),
                    "macd_line": _nullable_float(row["macd_line"]),
                    "macd_signal": _nullable_float(row["macd_signal"]),
                    "macd_histogram": _nullable_float(row["macd_histogram"]),
                    **{
                        column: _nullable_float(row[column])
                        for column in ADVANCED_INDICATOR_COLUMNS
                    },
                    **{column: _nullable_float(row[column]) for column in PIVOT_LEVEL_COLUMNS},
                    "chart_patterns": _json_or_none(row.get("chart_patterns")),
                    "source": row["source"],
                    "provider": row["provider"],
                    "source_window": json.dumps(row["source_window"]),
                    "row_count": int(row["row_count"]),
                    "is_recomputed": bool(is_recomputed),
                    "updated_at": _utcnow(),
                }
            )

        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO market_indicator (
                        symbol,
                        timeframe,
                        ts,
                        ema_9,
                        ema_21,
                        sma_20,
                        sma_50,
                        rsi_14,
                        macd_line,
                        macd_signal,
                        macd_histogram,
                        bb_upper_20_2,
                        bb_middle_20_2,
                        bb_lower_20_2,
                        atr_14,
                        stoch_k_14_3_3,
                        stoch_d_14_3_3,
                        obv,
                        ichimoku_tenkan_9,
                        ichimoku_kijun_26,
                        ichimoku_senkou_a_9_26_52,
                        ichimoku_senkou_b_9_26_52,
                        ichimoku_chikou_26,
                        chart_patterns,
                        pivot_point,
                        support_1,
                        support_2,
                        support_3,
                        resistance_1,
                        resistance_2,
                        resistance_3,
                        source,
                        provider,
                        source_window,
                        row_count,
                        is_recomputed,
                        updated_at
                    )
                    VALUES (
                        :symbol,
                        :timeframe,
                        :ts,
                        :ema_9,
                        :ema_21,
                        :sma_20,
                        :sma_50,
                        :rsi_14,
                        :macd_line,
                        :macd_signal,
                        :macd_histogram,
                        :bb_upper_20_2,
                        :bb_middle_20_2,
                        :bb_lower_20_2,
                        :atr_14,
                        :stoch_k_14_3_3,
                        :stoch_d_14_3_3,
                        :obv,
                        :ichimoku_tenkan_9,
                        :ichimoku_kijun_26,
                        :ichimoku_senkou_a_9_26_52,
                        :ichimoku_senkou_b_9_26_52,
                        :ichimoku_chikou_26,
                        :chart_patterns,
                        :pivot_point,
                        :support_1,
                        :support_2,
                        :support_3,
                        :resistance_1,
                        :resistance_2,
                        :resistance_3,
                        :source,
                        :provider,
                        :source_window,
                        :row_count,
                        :is_recomputed,
                        :updated_at
                    )
                    ON CONFLICT (symbol, timeframe, ts)
                    DO UPDATE SET
                        ema_9 = EXCLUDED.ema_9,
                        ema_21 = EXCLUDED.ema_21,
                        sma_20 = EXCLUDED.sma_20,
                        sma_50 = EXCLUDED.sma_50,
                        rsi_14 = EXCLUDED.rsi_14,
                        macd_line = EXCLUDED.macd_line,
                        macd_signal = EXCLUDED.macd_signal,
                        macd_histogram = EXCLUDED.macd_histogram,
                        bb_upper_20_2 = EXCLUDED.bb_upper_20_2,
                        bb_middle_20_2 = EXCLUDED.bb_middle_20_2,
                        bb_lower_20_2 = EXCLUDED.bb_lower_20_2,
                        atr_14 = EXCLUDED.atr_14,
                        stoch_k_14_3_3 = EXCLUDED.stoch_k_14_3_3,
                        stoch_d_14_3_3 = EXCLUDED.stoch_d_14_3_3,
                        obv = EXCLUDED.obv,
                        ichimoku_tenkan_9 = EXCLUDED.ichimoku_tenkan_9,
                        ichimoku_kijun_26 = EXCLUDED.ichimoku_kijun_26,
                        ichimoku_senkou_a_9_26_52 = EXCLUDED.ichimoku_senkou_a_9_26_52,
                        ichimoku_senkou_b_9_26_52 = EXCLUDED.ichimoku_senkou_b_9_26_52,
                        ichimoku_chikou_26 = EXCLUDED.ichimoku_chikou_26,
                        chart_patterns = EXCLUDED.chart_patterns,
                        pivot_point = EXCLUDED.pivot_point,
                        support_1 = EXCLUDED.support_1,
                        support_2 = EXCLUDED.support_2,
                        support_3 = EXCLUDED.support_3,
                        resistance_1 = EXCLUDED.resistance_1,
                        resistance_2 = EXCLUDED.resistance_2,
                        resistance_3 = EXCLUDED.resistance_3,
                        source = EXCLUDED.source,
                        provider = EXCLUDED.provider,
                        source_window = EXCLUDED.source_window,
                        row_count = EXCLUDED.row_count,
                        is_recomputed = EXCLUDED.is_recomputed,
                        updated_at = EXCLUDED.updated_at
                    """),
                write_rows,
            )

    def _estimated_bars(self, symbol: str, timeframe: str) -> int:
        with engine.begin() as conn:
            value = conn.execute(
                text("""
                    SELECT COUNT(*)
                    FROM market_ohlcv
                    WHERE symbol = :symbol
                      AND timeframe = :timeframe
                    """),
                {"symbol": _normalize_symbol(symbol), "timeframe": timeframe},
            ).scalar()
        try:
            return int(value or 0)
        except Exception:
            return 0

    def _run_recompute(
        self,
        *,
        job_id: str,
        symbol: str,
        timeframes: list[str],
        force_full: bool,
    ) -> None:
        normalized_symbol = _normalize_symbol(symbol)
        try:
            for timeframe in timeframes:
                self._jobs[job_id]["status"] = "running"
                self._jobs[job_id]["current_timeframe"] = timeframe

                available = self._list_symbols_and_timeframes(normalized_symbol, [timeframe])
                if timeframe not in available:
                    logger.info("No ohlcv rows found for %s/%s", normalized_symbol, timeframe)
                    continue

                since = None
                if not force_full:
                    last_indicator_ts = self._fetch_existing_latest_ts(normalized_symbol, timeframe)
                    if last_indicator_ts is not None:
                        since = self._compute_window_start(timeframe, last_indicator_ts)
                ohlcv_df = self._read_ohlcv(normalized_symbol, timeframe, since)
                if ohlcv_df.empty:
                    continue

                if since is not None and len(ohlcv_df) > MAX_HISTORY_BARS:
                    ohlcv_df = ohlcv_df.tail(MAX_HISTORY_BARS).copy()

                output = self._compute_indicators(ohlcv_df, timeframe, normalized_symbol)
                self._upsert_indicators(output, is_recomputed=not force_full)

                self._jobs[job_id]["processed_timeframes"] = (
                    self._jobs[job_id].get("processed_timeframes", 0) + 1
                )
                self._jobs[job_id]["estimated_bars_remaining"] = max(
                    0, int(self._jobs[job_id].get("estimated_bars_remaining") or 0) - len(ohlcv_df)
                )
        except Exception:
            logger.exception("Indicator recompute failed for job=%s", job_id)
            self._jobs[job_id]["status"] = "failed"
            self._jobs[job_id]["error"] = "indicator recompute failed"
        else:
            self._jobs[job_id]["status"] = "completed"
            self._jobs[job_id]["estimated_bars_remaining"] = 0
        finally:
            with self._lock:
                for timeframe in timeframes:
                    self._active.pop(
                        f"{_normalize_symbol(normalized_symbol)}:{_normalize_timeframe(timeframe)}",
                        None,
                    )
                self._jobs[job_id]["finished_at"] = _utcnow().isoformat()

    def start_recompute(
        self, symbol: str, timeframes: list[str] | None, force_full: bool
    ) -> dict[str, Any]:
        normalized_symbol = _normalize_symbol(symbol)
        resolved_timeframes = self._resolve_timeframes(timeframes)

        with self._lock:
            for tf in resolved_timeframes:
                key = f"{normalized_symbol}:{_normalize_timeframe(tf)}"
                if key in self._active:
                    raise RuntimeError(f"recompute already running for {key}")

            estimated_bars = sum(
                self._estimated_bars(normalized_symbol, tf) for tf in resolved_timeframes
            )
            job_id = str(uuid.uuid4())
            self._jobs[job_id] = {
                "job_id": job_id,
                "symbol": normalized_symbol,
                "timeframes": resolved_timeframes,
                "force_full": bool(force_full),
                "status": "accepted",
                "estimated_bars": int(estimated_bars),
                "estimated_bars_remaining": int(estimated_bars),
                "processed_timeframes": 0,
                "created_at": _utcnow().isoformat(),
                "started_at": _utcnow().isoformat(),
                "finished_at": None,
                "current_timeframe": None,
            }
            for tf in resolved_timeframes:
                self._active[f"{normalized_symbol}:{_normalize_timeframe(tf)}"] = job_id

            thread = threading.Thread(
                target=self._run_recompute,
                kwargs={
                    "job_id": job_id,
                    "symbol": normalized_symbol,
                    "timeframes": resolved_timeframes,
                    "force_full": bool(force_full),
                },
                daemon=True,
            )
            self._jobs[job_id]["thread"] = thread
            thread.start()

            return self._jobs[job_id]

    def get_job(self, job_id: str) -> dict[str, Any] | None:
        job = self._jobs.get(str(job_id))
        if not job:
            return None
        copy = dict(job)
        copy.pop("thread", None)
        copy.setdefault("status", "running")
        return copy

    def get_latest(self, symbol: str, timeframe: str, limit: int = 1) -> list[dict[str, Any]]:
        normalized_symbol = _normalize_symbol(symbol)
        normalized_timeframe = _normalize_timeframe(timeframe)
        if not normalized_symbol or normalized_timeframe not in ACTIVE_TIMEFRAMES:
            return []

        rows = self._fetch_latest_rows(normalized_symbol, normalized_timeframe, int(limit) or 1)
        return rows

    def get_time_series(self, symbol: str, timeframe: str, limit: int) -> list[dict[str, Any]]:
        normalized_symbol = _normalize_symbol(symbol)
        normalized_timeframe = _normalize_timeframe(timeframe)
        if not normalized_symbol or normalized_timeframe not in ACTIVE_TIMEFRAMES:
            return []

        rows = self._fetch_latest_rows(
            normalized_symbol,
            normalized_timeframe,
            int(limit) if int(limit) > 0 else 0,
        )
        return list(reversed(rows))


_SERVICE: MarketIndicatorService | None = None


def get_market_indicator_service() -> MarketIndicatorService:
    global _SERVICE
    if _SERVICE is None:
        _SERVICE = MarketIndicatorService()
    return _SERVICE
