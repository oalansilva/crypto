import os
import time
import uuid
import ccxt
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Optional

# Configure logger
logger = logging.getLogger(__name__)

class IncrementalLoader:
    def __init__(self, exchange_id='binance', cache_dir=None):
        self.exchange_id = exchange_id
        
        # Resolve cache_dir to absolute path relative to project root
        # If cache_dir is None or relative, resolve from project root
        if cache_dir is None:
            # Find project root (look for common markers like .git, backend/, frontend/)
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent  # src/data/incremental_loader.py -> project root
            cache_dir = project_root / "data" / "storage"
        elif not os.path.isabs(cache_dir):
            # Relative path - resolve from project root
            current_file = Path(__file__).resolve()
            project_root = current_file.parent.parent.parent
            cache_dir = project_root / cache_dir
        
        self.cache_dir = str(cache_dir)
        self.exchange = getattr(ccxt, exchange_id)({
            'enableRateLimit': True,
        })
        
        # Ensure deep storage path
        # storage/exchange/
        self.base_path = os.path.join(self.cache_dir, exchange_id)
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

    def _get_parquet_path(self, symbol, timeframe):
        safe_symbol = symbol.replace('/', '_')
        # Structure: data/storage/binance/BTC_USDT_1h.parquet
        filename = f"{safe_symbol}_{timeframe}.parquet"
        return os.path.join(self.base_path, filename)

    @staticmethod
    def _parse_datetime_utc(value: Optional[str], default: pd.Timestamp) -> pd.Timestamp:
        """
        Parse a datetime input into a timezone-aware UTC pandas Timestamp.

        Behavior:
        - If `value` is None/empty → returns `default` (expected to be UTC-aware).
        - If `value` has timezone info → converts to UTC.
        - If `value` is naive → assumes it is already in UTC (keeps behavior stable across environments).
        """
        if value is None:
            return default
        if isinstance(value, str) and value.strip() == "":
            return default
        ts = pd.to_datetime(value, errors="coerce")
        if pd.isna(ts):
            return default
        if getattr(ts, "tz", None) is None:
            return ts.tz_localize("UTC")
        return ts.tz_convert("UTC")

    def _read_parquet_slice(self, parquet_path: str, since_dt: pd.Timestamp, until_dt: pd.Timestamp) -> pd.DataFrame:
        """
        Read only the requested time slice from parquet (predicate pushdown when supported).
        This avoids loading the entire dataset into memory, which is critical for 15m data.
        """
        cols = ['timestamp', 'timestamp_utc', 'open', 'high', 'low', 'close', 'volume']
        since_ms = int(since_dt.timestamp() * 1000)
        until_ms = int(until_dt.timestamp() * 1000)

        # Prefer filtering by integer millisecond timestamp (no timezone edge cases)
        try:
            df = pd.read_parquet(
                parquet_path,
                columns=cols,
                filters=[('timestamp', '>=', since_ms), ('timestamp', '<=', until_ms)]
            )
        except Exception:
            # Fallback: read without filters (or if filters/columns not supported by engine)
            df = pd.read_parquet(parquet_path)

        if df.empty:
            return df

        # Normalize timestamp_utc
        if 'timestamp_utc' not in df.columns and 'timestamp' in df.columns:
            df['timestamp_utc'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)

        # Ensure slice (in case filters were not applied)
        if 'timestamp_utc' in df.columns:
            df = df[(df['timestamp_utc'] >= since_dt) & (df['timestamp_utc'] <= until_dt)].copy()
            df.set_index('timestamp_utc', inplace=True)
        return df

    def _atomic_to_parquet(self, df: pd.DataFrame, parquet_path: str) -> None:
        """
        Write parquet atomically to avoid leaving empty/corrupt files if the process
        is interrupted mid-write. Writes to a temp file in the same directory and
        then replaces the target.
        """
        # Use a unique temp path to avoid collisions across concurrent writers.
        tmp_path = f"{parquet_path}.{os.getpid()}.{uuid.uuid4().hex}.tmp"
        try:
            os.makedirs(os.path.dirname(parquet_path), exist_ok=True)
            try:
                df.to_parquet(tmp_path, index=False)
            except Exception as e:
                msg = str(e)
                if "Unable to find a usable engine" in msg and ("pyarrow" in msg or "fastparquet" in msg):
                    raise RuntimeError(
                        "DEPENDENCY_MISSING: parquet engine not available. "
                        "Instale um engine parquet (recomendado: `pip install pyarrow`) "
                        "ou `pip install fastparquet`."
                    ) from e
                raise
            os.replace(tmp_path, parquet_path)
        finally:
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass

    def fetch_data(
        self,
        symbol,
        timeframe,
        since_str,
        until_str=None,
        limit=1000,
        progress_callback=None,
        _retry_count=0,
        read_only: bool = False,
        full_history_if_empty: bool = True,
        allow_large_backfill: bool = False,
    ):
        """
        Smart fetch: Check local Parquet -> Download Delta -> Append -> Return Slice
        
        Args:
            _retry_count: Internal parameter to prevent infinite recursion (max 1 retry)
        """
        # Normalize limit: some callers may explicitly pass None
        # Ensure we always use a positive integer to avoid TypeError in len(ohlcv) < limit
        if not isinstance(limit, int) or limit <= 0:
            logger.warning(f"Received invalid limit={limit} for fetch_data({symbol}, {timeframe}). "
                           f"Defaulting to 1000.")
            limit = 1000

        # Parse Dates (UTC)
        # NOTE: If the caller sends naive datetimes, we assume they are already UTC.
        # This avoids environment-dependent shifts (e.g. local timezone differences).
        since_dt = self._parse_datetime_utc(since_str, pd.Timestamp("2017-01-01", tz="UTC"))
        until_dt = self._parse_datetime_utc(until_str, pd.Timestamp.now(tz="UTC"))
        if until_dt < since_dt:
            logger.warning(
                "until_dt (%s) < since_dt (%s) for %s %s. Swapping to keep a valid range.",
                str(until_dt), str(since_dt), symbol, timeframe
            )
            since_dt, until_dt = until_dt, since_dt
        
        # Parquet Path
        parquet_path = self._get_parquet_path(symbol, timeframe)

        # Read-only mode: never download/write. Just read what exists (slice) and return.
        if read_only:
            if not os.path.exists(parquet_path):
                logger.info(f"Read-only: no cache file for {symbol} {timeframe}. Returning empty DF.")
                return pd.DataFrame()
            try:
                df_slice = self._read_parquet_slice(parquet_path, since_dt, until_dt)
                if not df_slice.empty:
                    logger.info(f"Read-only: returning {len(df_slice)} rows for {symbol} {timeframe}")
                return df_slice
            except Exception as e:
                logger.error(f"Read-only: failed reading parquet slice for {symbol} {timeframe}: {e}")
                return pd.DataFrame()
        
        # 1. Load Local State
        df_local = pd.DataFrame()
        last_ts = None
        first_ts = None
        cache_exists = os.path.exists(parquet_path)
        cache_has_rows = False
        
        if cache_exists:
            logger.info(f"Local cache found for {symbol} {timeframe}: {parquet_path}")
            try:
                # Fast path: read only the timestamp column to decide if we need a delta download.
                # This avoids loading the full Parquet (critical for 15m).
                try:
                    df_ts = pd.read_parquet(parquet_path, columns=['timestamp'])
                    cache_has_rows = not df_ts.empty
                    if cache_has_rows:
                        last_ts_val = df_ts['timestamp'].max()
                        last_ts = int(last_ts_val) if pd.notna(last_ts_val) else None
                        first_ts_val = df_ts['timestamp'].min()
                        first_ts = int(first_ts_val) if pd.notna(first_ts_val) else None
                except Exception:
                    # Fallback for older files without 'timestamp' column
                    df_ts = pd.read_parquet(parquet_path, columns=['timestamp_utc'])
                    cache_has_rows = not df_ts.empty
                    if cache_has_rows:
                        last_ts_dt = df_ts['timestamp_utc'].max()
                        if pd.notna(last_ts_dt):
                            last_ts = int(pd.Timestamp(last_ts_dt).timestamp() * 1000)
                        first_ts_dt = df_ts['timestamp_utc'].min()
                        if pd.notna(first_ts_dt):
                            first_ts = int(pd.Timestamp(first_ts_dt).timestamp() * 1000)
            except Exception as e:
                logger.error(f"Error reading local parquet: {e}. Will redownload.")
                # Treat as corrupt cache; remove so we can rebuild cleanly.
                try:
                    os.remove(parquet_path)
                    logger.warning(f"Deleted corrupt cache file: {parquet_path}")
                    cache_exists = False
                except Exception as rm_e:
                    logger.warning(f"Failed to delete corrupt cache file {parquet_path}: {rm_e}")
                df_local = pd.DataFrame() # Corrupt?
                last_ts = None
                cache_has_rows = False
        
        # 2. Determine Download Range
        # Default: Download from requested 'since'
        fetch_since_ts = int(since_dt.timestamp() * 1000)
        backfill_until_ts: Optional[int] = None
        
        if cache_has_rows and last_ts is not None and isinstance(last_ts, (int, float)):
            # We have data up to last_ts.
            # If our stored data covers up to 'now' (approx), we might not need to download much.
            
            # Logic: We define "Full Life" as: 
            # If we have data, we assume it starts from "inception" OR from wherever we started last time.
            # We ONLY check the TAIL.
            
            # If last_ts < until_dt: We need to update tail.
            #
            # IMPORTANT (crypto continuity):
            # We MUST overlap by at least 1 candle when updating the tail. Otherwise, the last candle in cache
            # can remain "partial" (wrong close) and never gets refreshed after it closes (e.g. open[t] != close[t-1]
            # on continuous crypto markets like Binance). Overlapping 1 candle allows CCXT to return the last cached
            # candle again with its final close, and our dedupe logic (keep='last') will update it.
            
            until_ts_int = int(until_dt.timestamp() * 1000)

            # HEAD coverage check (important for intraday/deep backtest):
            # If cache starts AFTER requested since, we need to backfill at least to since_dt.
            if first_ts is not None and isinstance(first_ts, (int, float)) and int(first_ts) > fetch_since_ts:
                # For very large intraday backfills (e.g. 2017..now at 15m), avoid runaway downloads.
                # Callers should prefer bounded windows (6m/2y) for intraday.
                is_intraday = str(timeframe).endswith('m') or str(timeframe).endswith('h')
                requested_days = (until_dt - since_dt).days
                if is_intraday and requested_days > 900 and not allow_large_backfill:
                    logger.warning(
                        "Intraday cache does not cover requested start (%s %s). "
                        "Requested window=%sd (>900d). Skipping backfill to avoid huge download.",
                        symbol, timeframe, requested_days
                    )
                    # Do not attempt any fetch; we'll return what we have (caller may fallback).
                    fetch_since_ts = None
                else:
                    backfill_until_ts = int(first_ts)
                    logger.info(
                        "Cache starts at %s but requested since is %s. Backfilling missing head...",
                        datetime.utcfromtimestamp(int(first_ts) / 1000),
                        datetime.utcfromtimestamp(fetch_since_ts / 1000),
                    )
            elif last_ts < until_ts_int:
                # Overlap 1 candle to refresh last cached candle close
                tf = str(timeframe).strip().lower()
                overlap_ms = 0
                try:
                    if tf.endswith('m'):
                        overlap_ms = int(tf[:-1]) * 60_000
                    elif tf.endswith('h'):
                        overlap_ms = int(tf[:-1]) * 3_600_000
                    elif tf.endswith('d'):
                        overlap_ms = int(tf[:-1]) * 86_400_000
                    else:
                        overlap_ms = 86_400_000
                except Exception:
                    overlap_ms = 86_400_000

                fetch_since_ts = max(int(last_ts) - overlap_ms + 1, 0)
                logger.info(
                    "Incremental update needed. Downloading from %s (overlap=%ss)",
                    datetime.utcfromtimestamp(fetch_since_ts / 1000),
                    int(overlap_ms / 1000),
                )
            else:
                logger.info("Local data covers request. No network fetch needed.")
                fetch_since_ts = None  # No fetch needed
        
        # Fast return: no network fetch needed → read only the slice from parquet
        # (keeps behavior for empty-range fallback by falling back to the slow path when needed).
        if fetch_since_ts is None and cache_exists and cache_has_rows:
            try:
                df_slice_fast = self._read_parquet_slice(parquet_path, since_dt, until_dt)
                if not df_slice_fast.empty:
                    try:
                        real_start = df_slice_fast.index.min()
                        real_end = df_slice_fast.index.max()
                        logger.info(
                            "Returning %s rows for %s %s (slice read from parquet) [%s .. %s]",
                            len(df_slice_fast), symbol, timeframe, str(real_start), str(real_end)
                        )
                    except Exception:
                        logger.info(f"Returning {len(df_slice_fast)} rows for {symbol} {timeframe} (slice read from parquet)")
                    return df_slice_fast
            except Exception as e:
                logger.warning(f"Fast parquet slice read failed ({symbol} {timeframe}): {e}. Falling back to full read.")

            # We need the full DF for the existing empty-range fallback logic below.
            try:
                df_local = pd.read_parquet(parquet_path)
            except Exception as e:
                logger.error(f"Error reading local parquet for fallback: {e}. Will redownload.")
                df_local = pd.DataFrame()
                cache_has_rows = False

        # 3. Fetch New Data (if needed)
        df_new = pd.DataFrame()
        if fetch_since_ts is not None:
            # If fetching, and we have NO local data, maybe we want to fetch from INCEPTION?
            # User said: "baixar toda a vida do ativo mas apenas uma vez"
            # So if local is empty, we probably should ignore 'since_str' (which might be 2023) and download from 2017?
            # BUT 'fetch_data' is called by BacktestService with a specific range.
            # If we enforce "Full Life", we should set `fetch_since_ts` to 2017-01-01 IF df_local is empty.
            if not cache_has_rows and full_history_if_empty:
                logger.info("First run (empty cache). Downloading from 2017-01-01 (Full History mode).")
                inception_ts = int(pd.Timestamp("2017-01-01", tz="UTC").timestamp() * 1000)
                fetch_since_ts = inception_ts

            # Always download up to NOW by default, but for backfill we only need up to cache start.
            until_ts_download = int(datetime.now().timestamp() * 1000)
            if backfill_until_ts is not None:
                until_ts_download = int(backfill_until_ts)

            df_new = self._download_loop(symbol, timeframe, fetch_since_ts, until_ts_download, limit)
        
        # 4. Merge and Save
        if not df_new.empty:
             # If cache exists and has rows, load local DF now for merge (only when needed).
             if df_local.empty and cache_exists and cache_has_rows:
                 try:
                     df_local = pd.read_parquet(parquet_path)
                 except Exception as e:
                     logger.error(f"Error reading local parquet for merge: {e}. Will redownload.")
                     df_local = pd.DataFrame()
                     cache_has_rows = False

             if not df_local.empty:
                 logger.info(f"Merging {len(df_new)} new rows with {len(df_local)} local rows.")
                 # Concatenate
                 # Ensure types match
                 df_combined = pd.concat([df_local, df_new])
             else:
                 df_combined = df_new
            
             # Deduplicate
             df_combined.drop_duplicates(subset=['timestamp'], keep='last', inplace=True)
             df_combined.sort_values('timestamp', inplace=True)
             
             # Save
             logger.info(f"Saving updated cache to {parquet_path}")
             self._atomic_to_parquet(df_combined, parquet_path)
             
             df_final = df_combined
        else:
             # e.g. backfill returned no data (exchange has no older candles): keep existing cache
             if df_local.empty and cache_exists and cache_has_rows:
                 try:
                     df_local = pd.read_parquet(parquet_path)
                     logger.info(f"Backfill returned no new rows; using existing cache ({len(df_local)} rows) for {symbol} {timeframe}.")
                 except Exception as e:
                     logger.error(f"Error reading local parquet after empty fetch: {e}. Will redownload.")
             df_final = df_local
             
        if df_final.empty:
            # Only delete and retry when the cache FILE is actually empty (0 rows), not when df_final is empty for other reasons (e.g. backfill returned nothing but cache has data).
            if os.path.exists(parquet_path) and _retry_count == 0:
                try:
                    try:
                        df_verify = pd.read_parquet(parquet_path, columns=['timestamp'])
                    except Exception:
                        df_verify = pd.read_parquet(parquet_path, columns=['timestamp_utc'])
                    if df_verify.empty:
                        logger.warning(f"Cache file exists for {symbol} {timeframe} but is empty. Attempting full re-download...")
                        try:
                            os.remove(parquet_path)
                            logger.info(f"Deleted empty cache file. Retrying download for {symbol} {timeframe}...")
                            return self.fetch_data(
                                symbol,
                                timeframe,
                                since_str,
                                until_str,
                                limit=limit,
                                progress_callback=progress_callback,
                                _retry_count=1,
                                read_only=read_only,
                                full_history_if_empty=full_history_if_empty,
                                allow_large_backfill=allow_large_backfill,
                            )
                        except Exception as e:
                            logger.error(f"Error removing cache file: {e}")
                    else:
                        # File has data; return it (requested slice) instead of treating as failure
                        df_final = pd.read_parquet(parquet_path)
                except Exception as e:
                    logger.warning(f"Could not verify cache file for {symbol} {timeframe}: {e}. Attempting full re-download...")
                    try:
                        os.remove(parquet_path)
                        logger.info(f"Deleted unreadable cache file. Retrying download for {symbol} {timeframe}...")
                        return self.fetch_data(
                            symbol,
                            timeframe,
                            since_str,
                            until_str,
                            limit=limit,
                            progress_callback=progress_callback,
                            _retry_count=1,
                            read_only=read_only,
                            full_history_if_empty=full_history_if_empty,
                            allow_large_backfill=allow_large_backfill,
                        )
                    except Exception as rm_e:
                        logger.error(f"Error removing cache file: {rm_e}")
            else:
                if _retry_count > 0:
                    logger.error(f"Still no data after retry for {symbol} {timeframe}. This may indicate the symbol is not available on the exchange or the timeframe is invalid.")
                else:
                    logger.warning(f"No data available for {symbol} {timeframe} and no cache file exists.")
            if df_final.empty:
                return df_final
            
        # 5. Return Requested Slice
        # Filter by requested since_str / until_str
        # df_final has 'timestamp_utc' datetime column?
        # My _download_loop should ensure 'timestamp_utc' exists.
        
        # Slice
        mask = (df_final['timestamp_utc'] >= since_dt)
        if until_dt:
            mask &= (df_final['timestamp_utc'] <= until_dt)
            
        df_slice = df_final[mask].copy()
        
        # Set index to timestamp_utc for easier time-based operations
        if 'timestamp_utc' in df_slice.columns:
            df_slice.set_index('timestamp_utc', inplace=True)
        
        # If we have no data in the requested range, check if cache has usable data
        if df_slice.empty and os.path.exists(parquet_path) and _retry_count == 0:
            logger.warning(f"No data in requested range for {symbol} {timeframe}. Checking cache...")
            try:
                df_check = pd.read_parquet(parquet_path)
                if df_check.empty:
                    logger.warning(f"Cache file for {symbol} {timeframe} is empty. Attempting full re-download...")
                    # Delete the empty/corrupt cache file
                    os.remove(parquet_path)
                    # Retry with fresh download from inception (with retry flag to prevent infinite loop)
                    return self.fetch_data(
                        symbol,
                        timeframe,
                        since_str,
                        until_str,
                        limit=limit,
                        progress_callback=progress_callback,
                        _retry_count=1,
                        read_only=read_only,
                        full_history_if_empty=full_history_if_empty,
                        allow_large_backfill=allow_large_backfill,
                    )
                else:
                    # Cache has data but not in the requested range
                    if 'timestamp_utc' in df_check.columns:
                        cache_start = df_check['timestamp_utc'].min()
                        cache_end = df_check['timestamp_utc'].max()
                        logger.warning(f"Cache for {symbol} {timeframe} has data from {cache_start} to {cache_end}, but requested range is {since_dt} to {until_dt}")
                        
                        # If cache has recent data (within last 600 days), use it even if it doesn't cover the exact requested period
                        # This is useful for indicators that need historical data but can work with available data
                        days_diff = (until_dt - cache_end).days
                        if days_diff < 600 and len(df_check) > 100:  # Has reasonable amount of data
                            logger.info(f"Using available cache data (ends {days_diff} days before requested end date). This should be sufficient for indicator calculations.")
                            # Return all available cache data
                            df_check.set_index('timestamp_utc', inplace=True)
                            logger.info(f"Returning {len(df_check)} rows from cache for {symbol} {timeframe} (using available data)")
                            return df_check
                        else:
                            # Cache is too old or insufficient, try to download missing data
                            logger.info(f"Cache data is too old ({days_diff} days) or insufficient ({len(df_check)} rows). Attempting to download missing data...")
                            # Try to download from cache_end to until_dt
                            try:
                                cache_end_ts = int(cache_end.timestamp() * 1000)
                                until_ts_int = int(until_dt.timestamp() * 1000)
                                df_new = self._download_loop(symbol, timeframe, cache_end_ts + 1, until_ts_int, limit)
                                if not df_new.empty:
                                    # Merge new data with cache
                                    df_check_reset = df_check.reset_index()
                                    df_combined = pd.concat([df_check_reset, df_new])
                                    df_combined.drop_duplicates(subset=['timestamp'], keep='last', inplace=True)
                                    df_combined.sort_values('timestamp', inplace=True)
                                    self._atomic_to_parquet(df_combined, parquet_path)
                                    df_combined.set_index('timestamp_utc', inplace=True)
                                    logger.info(f"Successfully downloaded and merged new data. Returning {len(df_combined)} rows for {symbol} {timeframe}")
                                    return df_combined
                                else:
                                    # Download failed, but use available cache data if it's recent enough
                                    if days_diff < 600 and len(df_check) > 100:
                                        logger.warning(f"Download failed, but using available cache data (ends {days_diff} days before requested)")
                                        df_check.set_index('timestamp_utc', inplace=True)
                                        return df_check
                            except Exception as download_error:
                                logger.error(f"Error downloading missing data: {download_error}")
                                # Fallback: use available cache if reasonable
                                if days_diff < 600 and len(df_check) > 100:
                                    logger.warning(f"Using available cache data despite download error")
                                    df_check.set_index('timestamp_utc', inplace=True)
                                    return df_check
                    else:
                        logger.warning(f"Cache for {symbol} {timeframe} exists but timestamp_utc column not found")
            except Exception as e:
                logger.error(f"Error checking cache file: {e}. Attempting full re-download...")
                try:
                    os.remove(parquet_path)
                    return self.fetch_data(
                        symbol,
                        timeframe,
                        since_str,
                        until_str,
                        limit=limit,
                        progress_callback=progress_callback,
                        _retry_count=1,
                        read_only=read_only,
                        full_history_if_empty=full_history_if_empty,
                        allow_large_backfill=allow_large_backfill,
                    )
                except:
                    pass
        
        # Log the REAL returned range (not just the requested since/until).
        if not df_slice.empty:
            real_start = None
            real_end = None
            try:
                if isinstance(df_slice.index, pd.DatetimeIndex) and len(df_slice.index) > 0:
                    real_start = df_slice.index.min()
                    real_end = df_slice.index.max()
                elif 'timestamp_utc' in df_slice.columns:
                    s = pd.to_datetime(df_slice['timestamp_utc'], utc=True, errors='coerce')
                    real_start = s.min()
                    real_end = s.max()
                elif 'timestamp' in df_slice.columns:
                    s = pd.to_datetime(df_slice['timestamp'], unit='ms', utc=True, errors='coerce')
                    real_start = s.min()
                    real_end = s.max()
            except Exception:
                # If anything goes wrong, we still log the requested range below.
                real_start = None
                real_end = None

            if real_start is not None and real_end is not None:
                logger.info(
                    "Returning %s rows for %s %s [%s .. %s] (requested: %s .. %s)",
                    len(df_slice), symbol, timeframe, str(real_start), str(real_end), str(since_dt), str(until_dt)
                )
            else:
                logger.info(
                    "Returning %s rows for %s %s (requested: %s .. %s)",
                    len(df_slice), symbol, timeframe, str(since_dt), str(until_dt)
                )
        else:
            logger.info(
                "Returning 0 rows for %s %s (requested: %s .. %s)",
                symbol, timeframe, str(since_dt), str(until_dt)
            )
        return df_slice
    
    def fetch_intraday_data(
        self,
        symbol,
        timeframe='15m',
        since_str=None,
        until_str=None,
        read_only: bool = False,
        allow_large_backfill: bool = False,
    ):
        """
        Fetch intraday data (15m by default) for Deep Backtesting.
        This is a convenience wrapper around fetch_data with specific handling for intraday timeframes.
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Intraday timeframe (default: '15m', also supports '1h', '5m')
            since_str: Start date (ISO format)
            until_str: End date (ISO format)
            
        Returns:
            DataFrame with OHLCV data indexed by timestamp_utc
        """
        # Validate timeframe is intraday
        valid_intraday_tf = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h']
        if timeframe not in valid_intraday_tf:
            raise ValueError(f"Invalid intraday timeframe: {timeframe}. Must be one of {valid_intraday_tf}")
        
        logger.info(f"Fetching intraday data ({timeframe}) for {symbol}")
        
        # Use the standard fetch_data method (it already handles caching and incremental updates)
        # For intraday caches, do NOT force full-history download on first run.
        # Intraday from 2017 is enormous; callers should provide a bounded window (e.g. 6m/2y).
        return self.fetch_data(
            symbol,
            timeframe,
            since_str,
            until_str,
            read_only=read_only,
            full_history_if_empty=False,
            allow_large_backfill=allow_large_backfill,
        )
    
    def check_intraday_availability(self, symbol, timeframe='15m', since_str=None):
        """
        Check if intraday data is available in cache for the requested period.
        
        Args:
            symbol: Trading pair
            timeframe: Intraday timeframe
            since_str: Start date to check
            
        Returns:
            dict with 'available' (bool), 'coverage' (dict with start/end dates), 'reason' (str if not available)
        """
        parquet_path = self._get_parquet_path(symbol, timeframe)
        
        if not os.path.exists(parquet_path):
            return {
                'available': False,
                'reason': f'No cached {timeframe} data found for {symbol}',
                'coverage': None
            }
        
        try:
            df = pd.read_parquet(parquet_path)
            if df.empty:
                return {
                    'available': False,
                    'reason': 'Cache file exists but is empty',
                    'coverage': None
                }
            
            # Get coverage dates
            if 'timestamp_utc' in df.columns:
                start_date = df['timestamp_utc'].min()
                end_date = df['timestamp_utc'].max()
            else:
                # Fallback to timestamp column
                start_date = pd.to_datetime(df['timestamp'].min(), unit='ms', utc=True)
                end_date = pd.to_datetime(df['timestamp'].max(), unit='ms', utc=True)
            
            # Check if requested since_str is covered
            if since_str:
                since_dt = pd.to_datetime(since_str).tz_localize('UTC') if pd.to_datetime(since_str).tz is None else pd.to_datetime(since_str)
                if start_date > since_dt:
                    return {
                        'available': False,
                        'reason': f'Cached data starts at {start_date.date()}, but requested from {since_dt.date()}',
                        'coverage': {
                            'start': start_date.isoformat(),
                            'end': end_date.isoformat()
                        }
                    }
            
            return {
                'available': True,
                'coverage': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error checking intraday availability: {e}")
            return {
                'available': False,
                'reason': f'Error reading cache: {str(e)}',
                'coverage': None
            }

    def _download_loop(self, symbol, timeframe, since_ts, until_ts, limit):
        all_ohlcv = []
        current_since = since_ts
        
        # Ensure both timestamps are valid integers
        if since_ts is None or until_ts is None:
            logger.error(f"Invalid timestamps: since_ts={since_ts}, until_ts={until_ts}")
            return pd.DataFrame()
        
        try:
            since_ts_int = int(since_ts)
            until_ts_int = int(until_ts)
        except (TypeError, ValueError) as e:
            logger.error(f"Type error in download loop: {e}, since_ts={since_ts} ({type(since_ts)}), until_ts={until_ts} ({type(until_ts)})")
            return pd.DataFrame()
        
        # Safety: normalize limit inside download loop as well
        if not isinstance(limit, int) or limit <= 0:
            logger.warning(f"_download_loop received invalid limit={limit} for {symbol} {timeframe}. "
                           f"Using default 1000.")
            limit = 1000
        
        logger.info(f"Starting download loop for {symbol} from {datetime.utcfromtimestamp(since_ts_int/1000)} "
                    f"with limit={limit}")
        
        current_since = since_ts_int
        
        while current_since < until_ts_int:
            try:
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since=current_since, limit=limit)
                if not ohlcv:
                    break
                
                last_candle_ts = ohlcv[-1][0]
                
                # Ensure last_candle_ts is valid
                if last_candle_ts is None:
                    logger.error("Invalid last_candle_ts: None")
                    break
                
                try:
                    last_candle_ts_int = int(last_candle_ts)
                except (TypeError, ValueError):
                    logger.error(f"Invalid last_candle_ts type: {last_candle_ts} ({type(last_candle_ts)})")
                    break
                
                for candle in ohlcv:
                    candle_ts = candle[0] if candle and len(candle) > 0 else None
                    if candle_ts is not None:
                        try:
                            if int(candle_ts) < until_ts_int:
                                all_ohlcv.append(candle)
                        except (TypeError, ValueError):
                            continue
                        
                next_since = last_candle_ts_int + 1
                if next_since <= current_since:
                    break
                current_since = next_since
                
                if len(ohlcv) < limit:
                    break # Reached end of data
                    
            except Exception as e:
                logger.error(f"Download error: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                time.sleep(5)
                continue
                
        if not all_ohlcv:
            return pd.DataFrame()
            
        df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp_utc'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        return df
