import pandas as pd
import logging
import json
import threading
import time
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from app.strategies.combos.proximity_analyzer import ProximityAnalyzer
from app.strategies.combos.combo_strategy import ComboStrategy
from app.services.combo_service import ComboService
from app.services.asset_classification import classify_asset_type
from app.services.market_indicator_service import get_market_indicator_service
from app.services.market_data_providers import (
    CCXT_SOURCE,
    STOOQ_SOURCE,
    YahooMarketDataProvider,
    get_market_data_provider,
    resolve_data_source_for_symbol,
)
from app.symbols_config import get_excluded_symbols, is_excluded_symbol
from app.database import SessionLocal
from app.models import FavoriteStrategy

logger = logging.getLogger(__name__)
_OHLCV_CACHE_TTL_SECONDS = 300.0
_OHLCV_CACHE_LOCK = threading.Lock()
_OHLCV_CACHE: dict[str, dict[str, Any]] = {}

# Lista carregada de backend/config/excluded_symbols.json (compatibilidade com código que usa o nome)
UNSUPPORTED_SYMBOLS = get_excluded_symbols()


def _is_unsupported_symbol(symbol: str) -> bool:
    """True se o símbolo estiver em config/excluded_symbols.json."""
    return is_excluded_symbol(symbol)


def _history_days_for_timeframe(timeframe: str) -> int:
    tf = str(timeframe or "1d").strip().lower()
    if tf == "15m":
        return 5
    if tf == "1h":
        return 20
    if tf == "4h":
        return 75
    return 320


def _history_limit_for_timeframe(timeframe: str) -> int:
    tf = str(timeframe or "1d").strip().lower()
    if tf == "15m":
        return 320
    if tf == "1h":
        return 320
    if tf == "4h":
        return 320
    return 320


def _normalize_market_timeframe(symbol: str, requested_timeframe: str, data_source: str) -> str:
    tf = str(requested_timeframe or "1d").strip().lower()
    if data_source == STOOQ_SOURCE and tf != "1d":
        # US stocks/ETFs use only daily EOD candles in the current pipeline.
        # Keep backward compatibility by coercing legacy intraday favorites to 1d,
        # so monitor does not silently skip these strategies.
        logger.warning(
            "Coercing timeframe '%s' to '1d' for stooq symbol '%s' in monitor jobs",
            tf,
            symbol,
        )
        return "1d"
    return tf


def _coerce_positive_int(value: Any, default: int | None = None) -> int | None:
    try:
        parsed = int(float(value))
        if parsed <= 0:
            return default
        return parsed
    except Exception:
        return default


def _build_market_indicator_mappings(
    indicators: list[dict[str, Any]],
) -> dict[str, str]:
    """
    Build mapping from market_indicator table columns -> dataframe columns expected by logic.
    """
    mapping: dict[str, str] = {}
    for indicator in indicators:
        ind_type = str(indicator.get("type", "")).lower()
        params = indicator.get("params", {}) or {}
        alias = str(indicator.get("alias") or "").strip()

        if ind_type == "ema":
            length = _coerce_positive_int(params.get("length"), default=9)
            if length == 9:
                mapping["ema_9"] = alias if alias else "EMA_9"
            elif length == 21:
                mapping["ema_21"] = alias if alias else "EMA_21"
            continue

        if ind_type == "sma":
            length = _coerce_positive_int(params.get("length"), default=20)
            if length == 20:
                mapping["sma_20"] = alias if alias else "SMA_20"
            elif length == 50:
                mapping["sma_50"] = alias if alias else "SMA_50"
            continue

        if ind_type == "rsi":
            length = _coerce_positive_int(params.get("length", 14))
            if length == 14:
                mapping["rsi_14"] = "RSI_14"
                if alias and alias != "RSI_14":
                    mapping["rsi_14"] = alias
            continue

        if ind_type == "macd":
            fast = _coerce_positive_int(params.get("fast", 12))
            slow = _coerce_positive_int(params.get("slow", 26))
            signal = _coerce_positive_int(params.get("signal", 9))
            if fast == 12 and slow == 26 and signal == 9:
                prefix = alias if alias else "MACD"
                mapping["macd_line"] = f"{prefix}_macd"
                mapping["macd_signal"] = f"{prefix}_signal"
                mapping["macd_histogram"] = f"{prefix}_histogram"
            continue

    return mapping


def _hydrate_with_stored_indicators(
    df: pd.DataFrame,
    rows: list[dict[str, Any]],
    mappings: dict[str, str],
) -> tuple[pd.DataFrame, bool]:
    if df.empty or not rows or not mappings:
        return df, False

    source_df = pd.DataFrame(rows)
    if "ts" not in source_df.columns or source_df.empty:
        return df, False

    source_df["ts"] = pd.to_datetime(source_df["ts"], utc=True, errors="coerce")
    source_df = source_df.dropna(subset=["ts"]).set_index("ts").sort_index()

    target_df = df.copy()
    target_df.index = pd.to_datetime(target_df.index, utc=True, errors="coerce")
    used_mapping = False

    for source_col, target_col in mappings.items():
        if source_col not in source_df.columns:
            continue
        if target_col in target_df.columns:
            continue
        target_df = target_df.join(
            source_df[[source_col]].rename(columns={source_col: target_col}),
            how="left",
        )
        used_mapping = used_mapping or target_col in target_df.columns

    # Add compatibility columns used by legacy logic contracts.
    if "MACD_signal" in target_df.columns and "MACDs_12_26_9" not in target_df.columns:
        target_df["MACDs_12_26_9"] = target_df["MACD_signal"]
    if "MACD_histogram" in target_df.columns and "MACDh_12_26_9" not in target_df.columns:
        target_df["MACDh_12_26_9"] = target_df["MACD_histogram"]

    return target_df, used_mapping


def _read_ohlcv_cache(cache_key: str) -> Optional[pd.DataFrame]:
    now = time.time()
    with _OHLCV_CACHE_LOCK:
        cached = _OHLCV_CACHE.get(cache_key)
        if not cached:
            return None
        if float(cached.get("expires_at") or 0) <= now:
            _OHLCV_CACHE.pop(cache_key, None)
            return None
        df = cached.get("df")
        return df.copy() if isinstance(df, pd.DataFrame) else None


def _write_ohlcv_cache(cache_key: str, df: pd.DataFrame) -> None:
    with _OHLCV_CACHE_LOCK:
        _OHLCV_CACHE[cache_key] = {
            "df": df.copy(),
            "expires_at": time.time() + _OHLCV_CACHE_TTL_SECONDS,
        }


def _last_closed_candle_offset(timeframe: str, now: Optional[pd.Timestamp] = None) -> int:
    """
    Return the row offset (from the end) for the last *closed* candle, so values match TradingView/Binance.
    - For 1d: candle with index T closes at T+1day; we want the last row whose close time <= now.
    - If the last row is already closed (e.g. data has no "today" yet), use 0 (last row).
    - If the last row is still forming (e.g. we have "today"), use 1 (second-to-last).
    """
    if now is None:
        now = pd.Timestamp.utcnow()
    tf = (timeframe or "1d").strip().lower()
    if "d" in tf or tf == "1d":
        period = pd.Timedelta(days=1)
    elif "h" in tf:
        try:
            h = int("".join(c for c in tf if c.isdigit()) or 1)
            period = pd.Timedelta(hours=h)
        except Exception:
            period = pd.Timedelta(days=1)
    else:
        period = pd.Timedelta(days=1)
    return period


def _get_df_last_closed(
    df: pd.DataFrame, timeframe: str, now: Optional[pd.Timestamp] = None
) -> pd.DataFrame:
    """
    Return a 1-row DataFrame with the last *closed* candle (same convention as TradingView/Binance).
    Candle with index T is closed when T + period <= now (e.g. 1d bar at 31 Jan 00:00 closes at 1 Feb 00:00).
    """
    if df.empty:
        return df
    now = now or pd.Timestamp.utcnow()
    if getattr(now, "tzinfo", None) is None:
        now = now.tz_localize("UTC")
    period = _last_closed_candle_offset(timeframe, now)
    # Last row's close time
    last_ts = pd.Timestamp(df.index[-1])
    if getattr(last_ts, "tzinfo", None) is None and getattr(now, "tzinfo", None) is not None:
        last_ts = last_ts.tz_localize("UTC")
    close_time = last_ts + period
    if close_time <= now:
        # Last row is already closed (e.g. no "today" in data yet) -> use last row
        return df.iloc[-1:].copy()
    # Last row is forming -> use second-to-last
    if len(df) >= 2:
        return df.iloc[-2:-1].copy()
    return df.iloc[-1:].copy()


def _apply_crypto_continuity_fix(
    df: pd.DataFrame, timeframe: str, *, tail_rows: int = 60, threshold_pct: float = 0.5
) -> pd.DataFrame:
    """
    Heuristic repair for crypto OHLC caches:
    On continuous markets (Binance spot/futures), typically:
        open[t] ~= close[t-1]
    When our cache has a large gap (often due to partial/incorrect candle overwrite),
    indicator values (EMA/SMA) diverge from TradingView/Binance.

    This function adjusts ONLY the tail of the series, and ONLY the `close` of the previous candle:
        close[t-1] = open[t]
    when the mismatch exceeds `threshold_pct`.

    Notes:
    - We apply this in-memory (monitor/proximity only) to avoid rewriting historical cache.
    - We only need `close` continuity since our indicators are based on `close`.
    """
    tf = (timeframe or "").strip().lower()
    if df.empty:
        return df
    if "open" not in df.columns or "close" not in df.columns:
        return df
    # Apply only to daily/intraday candles (ignore weekly/monthly for now)
    if not any(x in tf for x in ("m", "h", "d")):
        return df

    out = df.copy()
    out = out.sort_index()

    # Work on tail only
    n = len(out)
    start_idx = max(0, n - tail_rows)
    tail = out.iloc[start_idx:].copy()

    next_open = tail["open"].shift(-1)
    prev_close = tail["close"]
    # mismatch as percentage of previous close
    mismatch = (next_open - prev_close).abs() / prev_close.replace(0, pd.NA)
    mask = next_open.notna() & mismatch.notna() & (mismatch > (threshold_pct / 100.0))

    if mask.any():
        # Set close[t] = open[t+1] for the mismatched rows (within tail window)
        tail.loc[mask, "close"] = next_open.loc[mask]
        # Write back into out
        out.iloc[start_idx:] = tail
    return out


def _index_position(index: pd.Index, value: Any) -> int | None:
    if value is None:
        return None
    try:
        loc = index.get_loc(value)
    except Exception:
        return None
    if isinstance(loc, slice):
        return int(loc.start)
    if isinstance(loc, (list, tuple)):
        return int(loc[0]) if loc else None
    if hasattr(loc, "__iter__") and not isinstance(loc, (str, bytes)):
        loc_list = list(loc)
        return int(loc_list[0]) if loc_list else None
    return int(loc)


def _signal_execution_price(
    df: pd.DataFrame,
    signal_idx: Any,
    *,
    direction: str,
) -> float | None:
    """
    Return the executed price for a generated signal.

    ComboStrategy emits signals on the candle where the order is executed,
    using that candle's open. The monitor must use the same convention or
    stop levels drift away from backtest/TradingView expectations.
    """
    if signal_idx is None or signal_idx not in df.index:
        return None

    row = df.loc[signal_idx]
    price_columns = ("open", "close") if direction == "entry" else ("open", "close")
    for column in price_columns:
        value = row.get(column) if hasattr(row, "get") else None
        if value is None or pd.isna(value):
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def _build_signal_history(
    df: pd.DataFrame, df_signals: pd.DataFrame, *, limit: int = 24
) -> list[dict[str, Any]]:
    if df.empty or df_signals.empty or "signal" not in df_signals.columns:
        return []

    signal_rows = df_signals[df_signals["signal"].isin([1, -1])]
    if signal_rows.empty:
        return []

    history: list[dict[str, Any]] = []
    for idx, row in signal_rows.tail(limit).iterrows():
        try:
            signal_value = int(row["signal"])
        except (TypeError, ValueError):
            continue

        signal_type = "entry" if signal_value == 1 else "exit"
        execution_price = _signal_execution_price(df, idx, direction=signal_type)
        raw_reason = row.get("signal_reason") if hasattr(row, "get") else None
        reason = (
            None
            if raw_reason is None or pd.isna(raw_reason) or str(raw_reason).strip() == ""
            else str(raw_reason)
        )

        history.append(
            {
                "timestamp": str(pd.Timestamp(idx).isoformat()),
                "signal": signal_value,
                "type": signal_type,
                "reason": reason,
                "price": round(float(execution_price), 8) if execution_price is not None else None,
            }
        )

    return history


def _resolve_position_state(
    *,
    short_above_long: bool,
    last_buy_pos: int | None,
    last_sell_pos: int | None,
    last_sell_reason: str | None,
    direction: str,
    last_price: float | None,
    stop_price: float | None,
) -> tuple[bool, bool, bool]:
    stop_breached_now = False
    if stop_price is not None and last_price is not None:
        if direction == "short":
            stop_breached_now = last_price >= stop_price
        else:
            stop_breached_now = last_price <= stop_price

    has_exit_after_entry = last_sell_pos is not None and (
        last_buy_pos is None or last_sell_pos > last_buy_pos
    )
    exited_by_stop = has_exit_after_entry and str(last_sell_reason or "").lower() == "stop_loss"
    if stop_breached_now or exited_by_stop:
        return False, True, stop_breached_now
    if has_exit_after_entry:
        return False, False, False
    return bool(short_above_long), False, False


class OpportunityService:
    """
    Service to manage Strategy Favorites and calculate Opportunities (Proximity to Signal).
    Reads from existing favorite_strategies table.
    """

    def __init__(self, db_path: str = None):
        self.db_path = db_path
        self.combo_service = ComboService(db_path)
        self.analyzer = ProximityAnalyzer()
        if db_path is None:
            self._session_factory = SessionLocal
        else:
            db_url = (
                "sqlite:///:memory:"
                if db_path == ":memory:"
                else db_path if "://" in db_path else None
            )
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker

            if db_url is None:
                raise ValueError(
                    "OpportunityService requires a valid database URL when db_path is provided."
                )

            if not os.getenv("PYTEST_CURRENT_TEST") and not db_url.lower().startswith("postgresql"):
                raise ValueError(
                    "OpportunityService requires a PostgreSQL URL when db_path is provided."
                )

            engine = create_engine(db_url, pool_pre_ping=True)
            self._session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def get_favorites(
        self, user_id: str, tier_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List relevant favorites for one user from existing table."""
        with self._session_factory() as db:
            query = db.query(FavoriteStrategy).filter(FavoriteStrategy.user_id == user_id)

            normalized_tier_filter = str(tier_filter or "").strip().lower()
            if not normalized_tier_filter or normalized_tier_filter == "all":
                query = query.filter(FavoriteStrategy.tier.in_([1, 2, 3]))
            elif normalized_tier_filter == "none":
                query = query.filter(FavoriteStrategy.tier.is_(None))
            else:
                allowed_tiers = [
                    int(t.strip()) for t in normalized_tier_filter.split(",") if t.strip().isdigit()
                ]
                if allowed_tiers:
                    query = query.filter(FavoriteStrategy.tier.in_(allowed_tiers))

            rows = query.all()

        favorites = []
        for row in rows:
            r = {
                "id": row.id,
                "name": row.name,
                "symbol": row.symbol,
                "timeframe": row.timeframe,
                "strategy_name": row.strategy_name,
                "parameters": row.parameters,
                "notes": row.notes,
                "tier": row.tier,
            }
            # Parse parameters JSON if string
            if isinstance(r["parameters"], str):
                try:
                    r["parameters"] = json.loads(r["parameters"])
                except Exception as e:
                    logger.warning(
                        f"Failed to parse parameters JSON for favorite {r.get('id')}: {e}"
                    )
                    r["parameters"] = {}
            favorites.append(r)

        logger.info(f"Loaded {len(favorites)} favorite strategies from database")
        for fav in favorites:
            logger.debug(
                f"  - ID {fav['id']}: {fav['symbol']} {fav['timeframe']} - {fav['strategy_name']}"
            )

        return favorites

    def _filter_by_tier(
        self, favorites: List[Dict[str, Any]], tier_filter: Optional[str]
    ) -> List[Dict[str, Any]]:
        """
        Filter favorites by tier before processing.

        Args:
            favorites: List of all favorites
            tier_filter: '1', '2', '3', '1,2', 'none' (null tier), 'all'/None (no filter)

        Returns:
            Filtered list of favorites
        """
        if not tier_filter or tier_filter.lower() == "all":
            # "All" = apenas Tier 1, 2 e 3 (excluir Sem tier)
            return [f for f in favorites if f.get("tier") in (1, 2, 3)]

        tier_filter = tier_filter.lower().strip()

        # Handle 'none' (null tier) - explícito quando usuário quer ver só Sem tier
        if tier_filter == "none":
            return [f for f in favorites if f.get("tier") is None]

        # Handle comma-separated tiers (e.g. '1,2')
        try:
            allowed_tiers = {int(t.strip()) for t in tier_filter.split(",") if t.strip().isdigit()}
        except ValueError:
            logger.warning(f"Invalid tier_filter '{tier_filter}', returning all favorites")
            return favorites

        if not allowed_tiers:
            return favorites

        return [f for f in favorites if f.get("tier") in allowed_tiers]

    def get_opportunities(
        self, user_id: str, tier_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze favorites and return their current status (is_holding, distance_to_next_status).

        Args:
            tier_filter: Filter by tier(s). Examples: '1', '1,2', '3', 'none' (null tier), 'all'/None (no filter)

        IMPORTANT: Buy/sell rules (entry_logic and exit_logic) are loaded dynamically from database:
        - Template metadata is fetched from combo_templates table
        - entry_logic (buy rule) and exit_logic (sell rule) come from template_data JSON field
        - Each favorite strategy uses its own template's rules from the database
        """
        favorites = self.get_favorites(user_id=user_id, tier_filter=tier_filter)

        opportunities = []

        logger.info(f"Processing {len(favorites)} favorite strategies (tier_filter={tier_filter})")

        # Cache for data to avoid refetching same symbol/timeframe
        data_cache = {}
        fetch_errors: dict[str, str] = {}
        indicator_cache: dict[str, list[dict[str, Any]]] = {}

        # Track skipped strategies for debugging
        skipped_strategies = []

        unique_market_jobs: dict[str, dict[str, Any]] = {}
        for fav in favorites:
            symbol = fav["symbol"]
            tf = fav["timeframe"]
            params = fav.get("parameters") or {}
            data_source = resolve_data_source_for_symbol(symbol, params.get("data_source"))
            if data_source == CCXT_SOURCE and _is_unsupported_symbol(symbol):
                continue
            normalized_tf = _normalize_market_timeframe(symbol, tf, data_source)
            cache_key = f"{data_source}:{symbol}_{normalized_tf}"
            if cache_key in unique_market_jobs:
                continue
            unique_market_jobs[cache_key] = {
                "data_source": data_source,
                "symbol": symbol,
                "timeframe": normalized_tf,
            }

        def _fetch_market_job(job: dict[str, Any]) -> tuple[str, pd.DataFrame]:
            cache_key = f"{job['data_source']}:{job['symbol']}_{job['timeframe']}"
            cached_df = _read_ohlcv_cache(cache_key)
            if cached_df is not None:
                return cache_key, cached_df

            history_days = _history_days_for_timeframe(job["timeframe"])
            history_limit = _history_limit_for_timeframe(job["timeframe"])
            start_date = (datetime.now() - timedelta(days=history_days)).strftime("%Y-%m-%d")

            provider = get_market_data_provider(job["data_source"])
            try:
                df = provider.fetch_ohlcv(
                    symbol=job["symbol"],
                    timeframe=job["timeframe"],
                    since_str=start_date,
                    limit=history_limit,
                )
            except Exception as exc:
                if job["data_source"] == STOOQ_SOURCE and job["timeframe"] == "1d":
                    logger.warning(
                        "Falling back to Yahoo for stock symbol '%s' after stooq error: %s",
                        job["symbol"],
                        exc,
                    )
                    df = YahooMarketDataProvider().fetch_ohlcv(
                        symbol=job["symbol"],
                        timeframe=job["timeframe"],
                        since_str=start_date,
                        limit=history_limit,
                    )
                else:
                    raise

            _write_ohlcv_cache(cache_key, df)
            return cache_key, df

        if unique_market_jobs:
            with ThreadPoolExecutor(max_workers=min(8, len(unique_market_jobs))) as executor:
                future_map = {
                    executor.submit(_fetch_market_job, job): cache_key
                    for cache_key, job in unique_market_jobs.items()
                }
                for future in as_completed(future_map):
                    cache_key = future_map[future]
                    try:
                        result_key, df = future.result()
                        data_cache[result_key] = df
                    except Exception as exc:
                        fetch_errors[cache_key] = str(exc)

        for fav in favorites:
            try:
                symbol = fav["symbol"]
                tf = fav["timeframe"]
                template_name = fav["strategy_name"]
                params = fav.get("parameters") or {}
                data_source = resolve_data_source_for_symbol(symbol, params.get("data_source"))
                normalized_tf = _normalize_market_timeframe(symbol, tf, data_source)

                logger.debug(
                    f"Processing strategy {fav['id']}: {symbol} {normalized_tf} - {template_name} (source={data_source})"
                )

                # 0. Skip known unsupported symbols (delisted / no data) before fetching
                if data_source == CCXT_SOURCE and _is_unsupported_symbol(symbol):
                    skipped_strategies.append(
                        {
                            "id": fav["id"],
                            "symbol": symbol,
                            "timeframe": normalized_tf,
                            "reason": "Symbol delisted or not available on exchange (e.g. Binance leveraged tokens)",
                        }
                    )
                    continue

                # 1. Fetch Data (1D usually)
                cache_key = f"{data_source}:{symbol}_{normalized_tf}"
                if cache_key not in data_cache:
                    fetch_exc = fetch_errors.get(cache_key)
                    if fetch_exc:
                        skipped_strategies.append(
                            {
                                "id": fav["id"],
                                "symbol": symbol,
                                "timeframe": normalized_tf,
                                "reason": f"Error fetching data ({data_source}): {fetch_exc}",
                            }
                        )
                        continue
                    skipped_strategies.append(
                        {
                            "id": fav["id"],
                            "symbol": symbol,
                            "timeframe": normalized_tf,
                            "reason": f"No cached market data available for {cache_key}",
                        }
                    )
                    continue

                df = data_cache[cache_key].copy()

                if df.empty:
                    skipped_strategies.append(
                        {
                            "id": fav["id"],
                            "symbol": symbol,
                            "timeframe": normalized_tf,
                            "reason": "No data (symbol may be delisted, or cache/API issue)",
                        }
                    )
                    continue

                # Heuristic: fix corrupted tail candles (open[t] != close[t-1]) so MAs match TradingView/Binance.
                # This is especially important for the last closed candle used in distance calculations.
                if data_source == CCXT_SOURCE:
                    df = _apply_crypto_continuity_fix(df, normalized_tf)

                normalized_symbol = symbol.strip().upper()
                indicator_cache_key = f"{normalized_symbol}:{normalized_tf}:indicators"

                # 2. Get Template Metadata from Database (entry_logic and exit_logic)
                # This dynamically loads the buy/sell rules from combo_templates table
                meta = self.combo_service.get_template_metadata(template_name)
                if not meta:
                    logger.warning(
                        f"Strategy {fav['id']} ({symbol} {normalized_tf}): Template '{template_name}' not found"
                    )
                    skipped_strategies.append(
                        {
                            "id": fav["id"],
                            "symbol": symbol,
                            "timeframe": normalized_tf,
                            "template_name": template_name,
                            "reason": f"Template '{template_name}' not found",
                        }
                    )
                    continue

                # Metadata is already flattened (contains indicators, entry_logic, exit_logic from DB)
                template_data = meta

                # 3. Merge Saved Params into Template Data
                # We need to inject params into indicators to make sure we use the favorited settings
                indicators = template_data.get("indicators", [])

                # Create a deep copy of indicators to modify
                # Helper to update indicator params based on alias/name matching
                final_indicators = []
                for ind in indicators:
                    ind_new = ind.copy()
                    ind_new["params"] = ind_new.get("params", {}).copy()

                    alias = ind_new.get("alias", "")
                    ind_type = ind_new.get("type", "").lower()

                    # Debug: Log indicator info for SOL
                    if symbol == "SOL/USDT":
                        logger.info(
                            f"SOL/USDT - Processing indicator: alias={alias}, type={ind_type}, current_params={ind_new['params']}"
                        )

                    # Improved parameter mapping logic
                    # Supports formats: ema_short, sma_medium, sma_long, etc.
                    for pk, pv in params.items():
                        if pk in {"stop_loss", "direction", "data_source"}:
                            continue

                        pk_lower = pk.lower()
                        matched = False

                        # 1. Exact alias match (e.g., pk='short', alias='short')
                        if pk == alias:
                            matched = True
                        # 2. Format: type_alias (e.g., pk='ema_short', type='ema', alias='short')
                        # Also match if param has different type prefix but same alias (e.g., ema_short matches sma with alias short)
                        elif ind_type and alias:
                            expected_format = f"{ind_type}_{alias}"
                            # Match exact format
                            if pk_lower == expected_format.lower():
                                matched = True
                            # Also match if alias matches even if type differs (e.g., ema_short matches sma_short)
                            elif pk_lower.endswith(f"_{alias}") or pk_lower.startswith(f"{alias}_"):
                                matched = True
                        # 3. Alias contained in param key (e.g., pk='ema_short', alias='short')
                        elif alias and alias.lower() in pk_lower:
                            matched = True
                        # 4. Param key contained in alias (less common, but possible)
                        elif alias and pk_lower in alias.lower():
                            matched = True

                        if matched:
                            # Determine which parameter to update
                            # Most indicators use 'length' or 'period'
                            old_value = ind_new["params"].get("length") or ind_new["params"].get(
                                "period"
                            )
                            if "length" in ind_new["params"]:
                                ind_new["params"]["length"] = int(pv)
                                if symbol == "SOL/USDT":
                                    logger.info(
                                        f"SOL/USDT - Updated {alias} ({ind_type}) length from {old_value} to {pv} using param {pk}"
                                    )
                            elif "period" in ind_new["params"]:
                                ind_new["params"]["period"] = int(pv)
                                if symbol == "SOL/USDT":
                                    logger.info(
                                        f"SOL/USDT - Updated {alias} ({ind_type}) period from {old_value} to {pv} using param {pk}"
                                    )
                            else:
                                # Fallback: try to infer the main parameter
                                # For most indicators, 'length' is the default
                                ind_new["params"]["length"] = int(pv)
                                if symbol == "SOL/USDT":
                                    logger.info(
                                        f"SOL/USDT - Updated {alias} ({ind_type}) length (fallback) to {pv} using param {pk}"
                                    )

                    final_indicators.append(ind_new)

                # Debug: Log final indicators for SOL
                if symbol == "SOL/USDT":
                    logger.info(f"SOL/USDT - Final indicators config:")
                    for ind in final_indicators:
                        logger.info(
                            f"  - {ind.get('alias')} ({ind.get('type')}): {ind.get('params')}"
                        )

                mapped_df = df
                indicator_rows = indicator_cache.get(indicator_cache_key)
                if indicator_rows is None:
                    try:
                        indicator_rows = get_market_indicator_service().get_time_series(
                            symbol=symbol,
                            timeframe=normalized_tf,
                            limit=len(df),
                        )
                    except Exception as exc:
                        indicator_rows = []
                        logger.warning(
                            "Falha ao carregar indicadores persistidos de %s (%s): %s",
                            symbol,
                            normalized_tf,
                            exc,
                        )
                    indicator_cache[indicator_cache_key] = indicator_rows

                mapped_df, used_stored_indicators = _hydrate_with_stored_indicators(
                    df,
                    indicator_rows,
                    _build_market_indicator_mappings(final_indicators),
                )
                if used_stored_indicators:
                    logger.debug(
                        "Indicadores persistidos carregados para %s (%s): %s",
                        symbol,
                        normalized_tf,
                        sorted(set(mapped_df.columns) - set(df.columns)),
                    )

                # 4. Instantiate Strategy with rules from database
                # entry_logic and exit_logic come from combo_templates.template_data (JSON field)
                sl_param = params.get("stop_loss", template_data.get("stop_loss", 0.0))

                # Extract buy/sell rules dynamically from database template
                entry_logic = template_data.get("entry_logic", "")  # Buy rule from DB
                exit_logic = template_data.get("exit_logic", "")  # Sell rule from DB

                strategy = ComboStrategy(
                    indicators=final_indicators,
                    entry_logic=entry_logic,  # Dynamic buy rule from database
                    exit_logic=exit_logic,  # Dynamic sell rule from database
                    stop_loss=float(sl_param),
                    force_recompute=False,
                )

                df_with_inds = strategy.calculate_indicators(mapped_df)

                # Debug: Log indicator values for SOL if symbol matches
                if symbol == "SOL/USDT":
                    last_row = df_with_inds.iloc[-1]
                    logger.info(
                        f"SOL/USDT - Last row (current candle) indicators: {[k for k in last_row.index if k not in ['open', 'high', 'low', 'close', 'volume', 'timestamp']]}"
                    )
                    # Log specific indicators if they exist
                    for ind_name in [
                        "ema_short",
                        "sma_medium",
                        "sma_long",
                        "short",
                        "medium",
                        "long",
                    ]:
                        if ind_name in last_row:
                            logger.info(f"SOL/USDT - {ind_name} (current): {last_row[ind_name]}")
                    logger.info(f"SOL/USDT - close (current): {last_row['close']}")
                    logger.info(f"SOL/USDT - entry_logic: {strategy.entry_logic}")
                    logger.info(f"SOL/USDT - params used: {params}")

                # 5. Analyze Entry Proximity using buy rule from database
                # Use LAST CLOSED candle (same as TradingView/Binance: close 76.968,21 for 31/01)
                df_current = df_with_inds.iloc[-1:].copy()  # Current candle for HOLD/signal checks
                df_closed = df_with_inds.iloc[:-1].copy()  # Closed candles for signal detection
                df_for_distance = _get_df_last_closed(
                    df_with_inds, tf
                )  # Last closed by close time <= now

                # Debug: Log current candle values for SOL
                if symbol == "SOL/USDT" and not df_current.empty:
                    current_row = df_current.iloc[-1]
                    logger.info(f"SOL/USDT - Current candle (for distance calc) indicators:")
                    for ind_name in ["short", "medium", "long"]:
                        if ind_name in current_row:
                            logger.info(f"SOL/USDT - {ind_name} (current): {current_row[ind_name]}")
                    logger.info(f"SOL/USDT - close (current): {current_row['close']}")

                # Check if short is above medium (entry condition) BEFORE analyzing
                # NEW CONCEPT: HOLD is determined by short > medium (not short > long)
                current_row = df_current.iloc[-1] if not df_current.empty else None
                short_above_medium = False
                if current_row is not None and "short" in current_row and "medium" in current_row:
                    short_val = current_row["short"]
                    medium_val = current_row["medium"]
                    short_above_medium = short_val > medium_val

                # Also check short > long for reference
                short_above_long = False
                if current_row is not None and "short" in current_row and "long" in current_row:
                    short_val = current_row["short"]
                    long_val = current_row["long"]
                    short_above_long = short_val > long_val

                # Analyze proximity using LAST CLOSED candle so distance % matches TradingView
                analysis = self.analyzer.analyze(df_for_distance, strategy.entry_logic)

                # But verify signal on closed candles (stable signals only)
                if not df_closed.empty:
                    signal_analysis = self.analyzer.analyze(df_closed, strategy.entry_logic)
                    if signal_analysis.get("status") == "SIGNAL":
                        # Signal confirmed on closed candle, but use current distance
                        analysis["status"] = "SIGNAL"
                        analysis["badge"] = "success"
                        analysis["message"] = "Signal Active"
                        analysis["distance"] = 0.0

                # Debug: Log analysis result for SOL
                if symbol == "SOL/USDT":
                    logger.info(
                        f"SOL/USDT - Analysis result: status={analysis.get('status')}, distance={analysis.get('distance')}, message={analysis.get('message')}"
                    )
                    # Calculate manual distance for BOTH crossovers to verify
                    if not df_current.empty:
                        current_row = df_current.iloc[-1]
                        if (
                            "short" in current_row
                            and "long" in current_row
                            and "medium" in current_row
                        ):
                            short_val = current_row["short"]
                            long_val = current_row["long"]
                            medium_val = current_row["medium"]

                            # Distance to cross UP long
                            dist_to_long = (
                                (long_val - short_val) / abs(long_val) * 100
                                if short_val < long_val
                                else 0
                            )
                            # Distance to cross UP medium
                            dist_to_medium = (
                                (medium_val - short_val) / abs(medium_val) * 100
                                if short_val < medium_val
                                else 0
                            )

                            # The minimum distance (closest crossover)
                            min_dist = (
                                min(dist_to_long, dist_to_medium)
                                if dist_to_long > 0 and dist_to_medium > 0
                                else (dist_to_long if dist_to_long > 0 else dist_to_medium)
                            )

                            logger.info(f"SOL/USDT - Manual distance calc:")
                            logger.info(
                                f"  - CROSS_UP long: ({long_val:.4f} - {short_val:.4f}) / {long_val:.4f} * 100 = {dist_to_long:.2f}%"
                            )
                            logger.info(
                                f"  - CROSS_UP medium: ({medium_val:.4f} - {short_val:.4f}) / {medium_val:.4f} * 100 = {dist_to_medium:.2f}%"
                            )
                            logger.info(f"  - Minimum distance (closest): {min_dist:.2f}%")

                direction = str(params.get("direction", "long") or "long").lower()
                last_price = float(df.iloc[-1]["close"]) if not df.empty else None

                # Compute entry distance override based on trend gate
                # - If trend up is false (short <= long): use short -> long distance
                # - If trend up is true (short > long): use short -> medium distance
                entry_distance_override = None
                if not df_for_distance.empty:
                    row_used = df_for_distance.iloc[-1]
                    if all(k in row_used for k in ("short", "medium", "long")):
                        try:
                            short_val = float(row_used["short"])
                            medium_val = float(row_used["medium"])
                            long_val = float(row_used["long"])
                            if short_above_long:
                                # Trend up true -> distance to short crossing medium (red -> orange)
                                if short_val < medium_val:
                                    denom = min(short_val, medium_val)
                                    if denom > 0:
                                        entry_distance_override = (
                                            (medium_val - short_val) / denom * 100
                                        )
                                    else:
                                        entry_distance_override = 0
                                else:
                                    entry_distance_override = 0
                            else:
                                # Trend up false -> distance to short crossing long (red -> blue)
                                if short_val < long_val:
                                    denom = min(short_val, long_val)
                                    if denom > 0:
                                        entry_distance_override = (
                                            (long_val - short_val) / denom * 100
                                        )
                                    else:
                                        entry_distance_override = 0
                                else:
                                    entry_distance_override = 0
                        except (TypeError, ValueError):
                            entry_distance_override = None
                # Run backtest logic on closed candles for reference (but don't use for HOLD determination)
                df_signals = strategy.generate_signals(df_closed)

                last_buy_idx = df_signals[df_signals["signal"] == 1].last_valid_index()
                last_sell_idx = df_signals[df_signals["signal"] == -1].last_valid_index()
                last_buy_pos = _index_position(df_closed.index, last_buy_idx)
                last_sell_pos = _index_position(df_closed.index, last_sell_idx)
                signal_history = _build_signal_history(df_closed, df_signals)
                last_sell_reason = None
                if (
                    last_sell_idx is not None
                    and last_sell_idx in df_signals.index
                    and "signal_reason" in df_signals.columns
                ):
                    raw_reason = df_signals.loc[last_sell_idx, "signal_reason"]
                    if raw_reason is not None and not pd.isna(raw_reason):
                        last_sell_reason = str(raw_reason)

                # Compute stop-loss proximity (optional display on Monitor cards)
                entry_price = None
                stop_price = None
                distance_to_stop_pct = None
                try:
                    sl_raw = params.get("stop_loss", template_data.get("stop_loss", None))
                    sl = None
                    if sl_raw is not None:
                        sl = float(sl_raw)
                        # Normalize: user uses 0.09 for 9%. If someone uses 9, treat as 9% too.
                        if sl > 1:
                            sl = sl / 100.0

                    if sl is not None and sl > 0:
                        # Use last confirmed BUY signal as entry
                        if last_buy_idx is not None and last_buy_idx in df_closed.index:
                            entry_price = _signal_execution_price(
                                df_closed,
                                last_buy_idx,
                                direction="entry",
                            )
                        elif short_above_long and not df_closed.empty:
                            # Fallback: infer entry from last bullish crossover on closed candles.
                            # This is useful when the signal generator doesn't emit explicit BUYs,
                            # but we still mark HOLD via trend condition.
                            try:
                                s = df_closed["short"]
                                m = df_closed["medium"] if "medium" in df_closed.columns else None
                                l = df_closed["long"] if "long" in df_closed.columns else None

                                inferred_idx = None
                                if l is not None:
                                    cross_long = (s.shift(1) <= l.shift(1)) & (s > l)
                                    if cross_long.any():
                                        inferred_idx = cross_long[cross_long].index[-1]

                                if inferred_idx is None and m is not None:
                                    cross_med = (s.shift(1) <= m.shift(1)) & (s > m)
                                    if cross_med.any():
                                        inferred_idx = cross_med[cross_med].index[-1]

                                if inferred_idx is not None and inferred_idx in df_closed.index:
                                    entry_price = float(df_closed.loc[inferred_idx, "close"])
                            except Exception:
                                pass

                        if entry_price and last_price and last_price > 0:
                            if direction == "short":
                                stop_price = entry_price * (1.0 + sl)
                                distance_to_stop_pct = (
                                    (stop_price - last_price) / last_price * 100.0
                                )
                            else:
                                stop_price = entry_price * (1.0 - sl)
                                distance_to_stop_pct = (
                                    (last_price - stop_price) / last_price * 100.0
                                )

                            if distance_to_stop_pct is not None:
                                distance_to_stop_pct = round(float(distance_to_stop_pct), 2)
                            if stop_price is not None:
                                stop_price = round(float(stop_price), 8)
                            if entry_price is not None:
                                entry_price = round(float(entry_price), 8)
                except Exception:
                    # Never fail opportunity generation due to stop computation
                    entry_price = None
                    stop_price = None
                    distance_to_stop_pct = None

                is_holding, is_stopped_out, stop_breached_now = _resolve_position_state(
                    short_above_long=short_above_long,
                    last_buy_pos=last_buy_pos,
                    last_sell_pos=last_sell_pos,
                    last_sell_reason=last_sell_reason,
                    direction=direction,
                    last_price=last_price,
                    stop_price=stop_price,
                )

                # Debug for TRX
                if symbol == "TRX/USDT":
                    logger.info(
                        f"TRX/USDT - short_above_medium={short_above_medium}, short_above_long={short_above_long}, "
                        f"is_holding={is_holding}, is_stopped_out={is_stopped_out}, "
                        f"last_buy_pos={last_buy_pos}, last_sell_pos={last_sell_pos}, stop_price={stop_price}, last_price={last_price}"
                    )
                    if current_row is not None:
                        if "short" in current_row and "medium" in current_row:
                            logger.info(
                                f"TRX/USDT - Current candle: short={current_row['short']:.4f}, medium={current_row['medium']:.4f}"
                            )
                        if "short" in current_row and "long" in current_row:
                            logger.info(
                                f"TRX/USDT - short={current_row['short']:.4f}, long={current_row['long']:.4f}"
                            )

                # Debug for ETH
                if symbol == "ETH/USDT":
                    logger.info(
                        f"ETH/USDT - short_above_medium={short_above_medium}, short_above_long={short_above_long}, "
                        f"is_holding={is_holding}, is_stopped_out={is_stopped_out}, "
                        f"last_buy_pos={last_buy_pos}, last_sell_pos={last_sell_pos}, stop_price={stop_price}, last_price={last_price}"
                    )
                    if current_row is not None:
                        if "short" in current_row and "medium" in current_row:
                            logger.info(
                                f"ETH/USDT - short={current_row['short']:.4f}, medium={current_row['medium']:.4f}"
                            )
                        if "short" in current_row and "long" in current_row:
                            logger.info(
                                f"ETH/USDT - short={current_row['short']:.4f}, long={current_row['long']:.4f}"
                            )

                # -------------------------------------------------------------------------
                # With new concept: is_holding is already determined by short_above_long
                # No need for special cases - if short > long, we're in HOLD
                # Stop loss history is ignored for HOLD determination
                # -------------------------------------------------------------------------

                # Removed: Complex logic checking stop loss history
                # Now: Simple - if short > long, we're in HOLD

                # (Old complex logic removed - not needed with new concept)
                if False:  # This block is disabled with new concept
                    # Check if entry logic would be satisfied on current candle
                    # For entry_logic like: (crossover(short, long) | crossover(short, medium)) & (short > long)
                    # If short > long is True, we need to check if there was a recent crossover

                    # Check previous closed candle to see if short was below long
                    if not df_closed.empty and len(df_closed) > 0:
                        prev_closed_row = df_closed.iloc[-1]
                        if "short" in prev_closed_row and "long" in prev_closed_row:
                            prev_short = prev_closed_row["short"]
                            prev_long = prev_closed_row["long"]
                            prev_short_above_long = prev_short > prev_long

                            # If previous candle had short <= long, but current has short > long,
                            # it means we crossed over on current candle -> we're in HOLD
                            if not prev_short_above_long and short_above_long:
                                # Crossover happened on current candle -> we're in HOLD
                                is_holding = True
                                if symbol == "TRX/USDT":
                                    logger.info(
                                        f"TRX/USDT - Crossover detected on current candle! prev: short={prev_short:.4f} <= long={prev_long:.4f}, current: short={current_row['short']:.4f} > long={current_row['long']:.4f}"
                                    )
                                    logger.info(
                                        f"TRX/USDT - Setting is_holding=True because entry happened on current candle"
                                    )
                            elif prev_short_above_long and short_above_long:
                                # Both previous and current have short > long
                                # Check how many candles ago was the last stop
                                if last_sig_idx is not None and last_sig_idx in df_closed.index:
                                    try:
                                        last_stop_pos = df_closed.index.get_loc(last_sig_idx)
                                        current_date_pos = len(df_closed) - 1
                                        candles_since_stop = current_date_pos - last_stop_pos

                                        # If stop was recent (within last few candles) and we're still above,
                                        # we might have re-entered. Check if there was a crossover after stop
                                        if (
                                            candles_since_stop > 0 and candles_since_stop <= 10
                                        ):  # Within last 10 candles
                                            # Check if short was below long right after stop, then crossed
                                            # Look for crossover after stop
                                            after_stop_df = df_closed.iloc[last_stop_pos + 1 :]
                                            if len(after_stop_df) > 0:
                                                # Check if there was a period where short was below long after stop
                                                had_crossover = False
                                                for idx, row in after_stop_df.iterrows():
                                                    if "short" in row and "long" in row:
                                                        if row["short"] <= row["long"]:
                                                            had_crossover = True  # Found a period where short was below
                                                            break

                                                # If we had short below after stop, but now we're above, we crossed -> HOLD
                                                if had_crossover or candles_since_stop == 1:
                                                    is_holding = True
                                                    if symbol == "TRX/USDT":
                                                        logger.info(
                                                            f"TRX/USDT - short > long maintained since stop ({candles_since_stop} candles ago), assuming re-entry -> is_holding=True"
                                                        )
                                    except (KeyError, IndexError) as e:
                                        if symbol == "TRX/USDT":
                                            logger.warning(
                                                f"TRX/USDT - Error checking candles since stop: {e}"
                                            )

                # -------------------------------------------------------------------------
                # With new concept: if short > long, we're already in HOLD (is_holding = True)
                # No need for STOPPED_OUT or MISSED_ENTRY statuses when short > long
                # All cases where short > long are treated as HOLD
                # -------------------------------------------------------------------------

                # Standardize Entry Status Names for frontend clarity
                # BUT: If we're in HOLD, set status to HOLDING
                if is_stopped_out:
                    analysis["status"] = "STOPPED_OUT"
                    analysis["badge"] = "critical"
                    if stop_breached_now:
                        analysis["message"] = (
                            "STOP: preco atingiu o stop loss. Aguardando reentrada."
                        )
                    else:
                        analysis["message"] = (
                            "STOP ja confirmado no historico. Aguardando nova entrada."
                        )
                    if entry_distance_override is not None:
                        analysis["distance"] = round(entry_distance_override, 2)
                elif is_holding:
                    analysis["status"] = "HOLDING"
                    analysis["badge"] = "info"
                elif last_sell_pos is not None and (
                    last_buy_pos is None or last_sell_pos > last_buy_pos
                ):
                    analysis["status"] = "EXITED"
                    analysis["badge"] = "neutral"
                    analysis["message"] = (
                        "Saida confirmada pela regra de exit. Aguardando reentrada."
                    )
                    if entry_distance_override is not None:
                        analysis["distance"] = round(entry_distance_override, 2)
                elif analysis["status"] == "SIGNAL":
                    analysis["status"] = "BUY_SIGNAL"
                else:
                    # Override entry distance and proximity when not holding
                    if entry_distance_override is not None:
                        threshold_pct = self.analyzer.threshold * 100
                        if entry_distance_override <= threshold_pct:
                            analysis["status"] = "BUY_NEAR"
                            analysis["badge"] = "warning"
                            if short_above_long:
                                analysis["message"] = "Approaching short crossing medium"
                            else:
                                analysis["message"] = "Approaching short crossing long"
                        else:
                            analysis["status"] = "NEUTRAL"
                            analysis["badge"] = "neutral"
                            analysis["message"] = "Waiting for setup"
                        analysis["distance"] = round(entry_distance_override, 2)
                    elif analysis["status"] == "NEAR":
                        analysis["status"] = "BUY_NEAR"
                # -------------------------------------------------------------------------
                # NEW: Stateful Check (Stop Loss / Confirmed Signals)
                # Proximity Analyzer is stateless (doesn't know if we hit -5% SL logic).
                # We assume "HOLDING" if Proximity says so, BUT we must check if strategy killed it.
                # -------------------------------------------------------------------------

                # Override Logic: REMOVED with new concept
                # We no longer check stop loss history to determine HOLD status
                # HOLD is determined ONLY by short > long (entry conditions met)
                if False:  # Disabled - not needed with new concept
                    # If the Sell was on the very last closed candle, it's an EXIT SIGNAL (Actionable)
                    if last_sig_idx == df_closed.index[-1]:
                        analysis["status"] = "EXIT_SIGNAL"
                        analysis["badge"] = "critical"
                        # Show Re-entry Distance (calculated by ProximityAnalyzer for Entry Logic)
                        re_entry_dist = analysis.get("distance", 0.0)
                        analysis["message"] = f"EXIT: Stop Loss Dist: {re_entry_dist}%"
                        # Keep the distance to show proximity to re-entry
                        pass
                    else:
                        # If Sell was older, we are effectively WAITING (Neutral), not Holding.
                        # Unless Proximity sees a NEW Buy Signal right now.
                        if analysis["status"] == "HOLDING":
                            analysis["status"] = "NEUTRAL"
                            analysis["badge"] = "neutral"
                            re_entry_dist = analysis.get("distance", 0.0)
                            analysis["message"] = f"Waiting (Re-entry Dist: {re_entry_dist}%)"
                            # Preserve distance logic
                            pass

                # 6. Secondary Analysis: Exit Proximity using sell rule from database
                # Only check exit if we are technically Holding (is_holding == True)
                # This is critical: when in HOLD, we need to show distance to EXIT, not to entry
                if is_holding:
                    if (
                        strategy.exit_logic
                    ):  # exit_logic comes from database (combo_templates.template_data)
                        # Use df_closed here too for consistency
                        # Analyze proximity to exit signal using exit_logic from database
                        exit_analysis = self.analyzer.analyze(df_closed, strategy.exit_logic)

                        # LOGIC CHANGE: If we are HOLDING, the relevant distance is ALWAYS the Exit Distance.
                        # Even if it's NEUTRAL (not < 1%), we want to see "Distance to Sell", not "Distance to Buy" (which is history).

                        # 1. Critical/Warning: Exit is NEAR or SIGNAL
                        if exit_analysis["status"] in ["SIGNAL", "NEAR"]:
                            analysis["status"] = (
                                "EXIT_NEAR" if exit_analysis["status"] == "NEAR" else "EXIT_SIGNAL"
                            )
                            analysis["badge"] = (
                                "critical" if exit_analysis["status"] == "SIGNAL" else "warning"
                            )
                            analysis["message"] = f"EXIT: {exit_analysis['message']}"
                            analysis["distance"] = exit_analysis.get("distance")
                            analysis["exit_details"] = exit_analysis
                            if isinstance(analysis.get("details"), dict):
                                analysis["details"]["exit_analysis"] = exit_analysis

                            # 2. Informational: Exit is NEUTRAL (Far away), but we are HOLDING
                        else:
                            # We're in HOLD, exit is not near, but we still want to show exit distance
                            # Keep status as HOLDING, but update specific details to reflect Exit focus
                            # Use the Exit distance
                            exit_dist = exit_analysis.get("distance", 999)
                            analysis["distance"] = exit_dist if exit_dist < 999 else None
                            # Update message to be clear we are tracking exit
                            if exit_dist < 999:
                                analysis["message"] = (
                                    f"Em Hold. Distância para saída: {exit_dist:.2f}%"
                                )
                            else:
                                analysis["message"] = "Em Hold. Aguardando sinal de saída."
                            analysis["exit_details"] = exit_analysis
                            # Safety: Ensure details is not overwritten or accessed incorrectly if string
                            if isinstance(analysis.get("details"), dict):
                                analysis["details"]["exit_analysis"] = exit_analysis
                            else:
                                # Convert string detail to dict if needed, or just ignore
                                pass
                    else:
                        # No exit_logic defined, but we're in HOLD
                        # Set a default message
                        analysis["status"] = "HOLDING"
                        analysis["badge"] = "info"
                        analysis["message"] = "Em Hold. Sem regra de saída definida."
                        if symbol in ["ETH/USDT", "TRX/USDT"]:
                            logger.info(f"{symbol} - In HOLD but no exit_logic defined")

                # is_holding was already determined above based on short_above_long
                is_missed_entry = False  # Disabled with new concept

                # Calculate distance to next status
                # If holding: distance to exit, else: distance to entry
                if is_holding:
                    # Use exit analysis if available (from step 6)
                    if "exit_details" in analysis and analysis.get("exit_details"):
                        exit_details = analysis["exit_details"]
                        if isinstance(exit_details, dict):
                            distance_to_next = exit_details.get("distance", 999)
                        else:
                            distance_to_next = analysis.get("distance", 999)
                    elif "distance" in analysis:
                        # Fallback: use distance from analysis (might be entry distance, but better than nothing)
                        distance_to_next = analysis.get("distance", 999)
                    else:
                        distance_to_next = 999
                    next_status_label = "exit"
                elif is_stopped_out or is_missed_entry:
                    # For stopped out or missed entry, use the spread distance we calculated
                    distance_to_next = analysis.get("distance", None)
                    if is_stopped_out:
                        next_status_label = "re-entry"
                    else:
                        next_status_label = "confirmation"
                else:
                    # Distance to entry (from entry analysis)
                    distance_to_next = analysis.get("distance", 999)
                    next_status_label = "entry"

                # Ensure distance is always a number (not None) for sorting and display
                final_distance = None
                if distance_to_next is not None and distance_to_next < 999:
                    final_distance = round(distance_to_next, 2)
                elif is_stopped_out or is_missed_entry:
                    # For stopped out/missed entry, use the spread distance we calculated
                    final_distance = analysis.get("distance")
                    if final_distance is not None:
                        final_distance = round(final_distance, 2)

                # Indicator values used for distance (last closed candle) — for display on card
                indicator_values = {}
                indicator_values_candle_time = (
                    None  # date/time of candle so user can match TradingView
                )
                if not df_for_distance.empty:
                    row_used = df_for_distance.iloc[-1]
                    for key in ("short", "medium", "long", "fast", "slow", "inter"):
                        if key in row_used and pd.notna(row_used.get(key)):
                            try:
                                indicator_values[key] = round(float(row_used[key]), 2)
                            except (TypeError, ValueError):
                                pass
                    # Include open/close of that candle so user can compare with TradingView (O=76,968.22, C=...)
                    for key in ("open", "close"):
                        if key in row_used and pd.notna(row_used.get(key)):
                            try:
                                indicator_values[key] = round(float(row_used[key]), 2)
                            except (TypeError, ValueError):
                                pass
                    try:
                        idx = df_for_distance.index[-1]
                        indicator_values_candle_time = (
                            str(pd.Timestamp(idx).isoformat()) if idx is not None else None
                        )
                    except Exception:
                        pass

                opportunities.append(
                    {
                        "id": fav["id"],
                        "symbol": symbol,
                        "asset_type": classify_asset_type(symbol),
                        "timeframe": normalized_tf,
                        "template_name": template_name,
                        "name": fav["name"],  # User custom name
                        "notes": fav.get("notes"),
                        "tier": fav.get("tier"),
                        "parameters": fav.get("parameters") or {},
                        "is_holding": is_holding,
                        "distance_to_next_status": final_distance,
                        "next_status_label": next_status_label,
                        "indicator_values": indicator_values if indicator_values else None,
                        "indicator_values_candle_time": indicator_values_candle_time,
                        "signal_history": signal_history,
                        "entry_price": entry_price,
                        "stop_price": stop_price,
                        "distance_to_stop_pct": distance_to_stop_pct,
                        # Keep legacy fields for backward compatibility
                        "status": analysis["status"],
                        "badge": analysis["badge"],
                        "message": analysis["message"],
                        "details": analysis,
                        "last_price": float(df.iloc[-1]["close"]),
                        "timestamp": str(df.index[-1]),
                    }
                )

            except Exception as e:
                import traceback

                logger.error(
                    f"Error analyzing favorite {fav.get('id', 'unknown')} ({fav.get('symbol', 'unknown')} {fav.get('timeframe', 'unknown')}): {e}"
                )
                logger.error(traceback.format_exc())
                skipped_strategies.append(
                    {
                        "id": fav.get("id", "unknown"),
                        "symbol": fav.get("symbol", "unknown"),
                        "timeframe": fav.get("timeframe", "unknown"),
                        "reason": f"Exception: {str(e)}",
                    }
                )
                continue

        # Sort by distance to next status (closest first)
        # Holding positions first, then by distance
        opportunities.sort(
            key=lambda x: (
                0 if x["is_holding"] else 1,  # Holding first
                x["distance_to_next_status"] if x["distance_to_next_status"] is not None else 999,
            )
        )

        # Log summary
        logger.info(
            f"Successfully processed {len(opportunities)} strategies out of {len(favorites)} favorites"
        )
        if skipped_strategies:
            symbols_str = ", ".join(s.get("symbol", "?") for s in skipped_strategies)
            logger.warning(
                f"Skipped {len(skipped_strategies)} strategies (no data / delisted): {symbols_str}"
            )
            for skipped in skipped_strategies:
                logger.debug(
                    f"  ID {skipped['id']}: {skipped.get('symbol', '?')} {skipped.get('timeframe', '?')} — {skipped['reason']}"
                )

        return opportunities
