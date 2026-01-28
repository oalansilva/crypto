import os
import time
import ccxt
import pandas as pd
from datetime import datetime, timedelta
import logging

# Configure logger
logger = logging.getLogger(__name__)

class IncrementalLoader:
    def __init__(self, exchange_id='binance', cache_dir='data/storage'):
        self.exchange_id = exchange_id
        self.cache_dir = cache_dir
        self.exchange = getattr(ccxt, exchange_id)({
            'enableRateLimit': True,
        })
        
        # Ensure deep storage path
        # storage/exchange/
        self.base_path = os.path.join(cache_dir, exchange_id)
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

    def _get_parquet_path(self, symbol, timeframe):
        safe_symbol = symbol.replace('/', '_')
        # Structure: data/storage/binance/BTC_USDT_1h.parquet
        filename = f"{safe_symbol}_{timeframe}.parquet"
        return os.path.join(self.base_path, filename)

    def fetch_data(self, symbol, timeframe, since_str, until_str=None, limit=1000, progress_callback=None, _retry_count=0):
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
        # Parse Dates (Ensure UTC)
        # Handle None values - default to full history
        if since_str is None:
            since_dt = pd.Timestamp('2017-01-01', tz='UTC')
        else:
            since_dt = pd.to_datetime(since_str).tz_localize('UTC') if pd.to_datetime(since_str).tz is None else pd.to_datetime(since_str)
        
        if until_str is None:
            until_dt = pd.Timestamp.now(tz='UTC')
        else:
            until_dt = pd.to_datetime(until_str).tz_localize('UTC') if pd.to_datetime(until_str).tz is None else pd.to_datetime(until_str)
        
        # Parquet Path
        parquet_path = self._get_parquet_path(symbol, timeframe)
        
        # 1. Load Local State
        df_local = pd.DataFrame()
        last_ts = None
        
        if os.path.exists(parquet_path):
            logger.info(f"Local cache found for {symbol} {timeframe}: {parquet_path}")
            try:
                # Read metadata or full file?
                # Reading full file is fast enough for <1GB.
                df_local = pd.read_parquet(parquet_path)
                if not df_local.empty:
                     # timestamp_utc is likely the index or column
                     if 'timestamp' in df_local.columns:
                         last_ts_val = df_local['timestamp'].max()
                         # Ensure last_ts is a valid integer, not None or NaN
                         if pd.notna(last_ts_val):
                             last_ts = int(last_ts_val)
                         else:
                             last_ts = None
                     elif 'timestamp_utc' in df_local.columns:
                         # Try timestamp_utc column
                         last_ts_dt = df_local['timestamp_utc'].max()
                         if pd.notna(last_ts_dt):
                             # Convert datetime to timestamp in milliseconds
                             if isinstance(last_ts_dt, pd.Timestamp):
                                 last_ts = int(last_ts_dt.timestamp() * 1000)
                             else:
                                 last_ts = None
                         else:
                             last_ts = None
                     else:
                         # try index if datetime
                         last_ts = None
            except Exception as e:
                logger.error(f"Error reading local parquet: {e}. Will redownload.")
                df_local = pd.DataFrame() # Corrupt?
                last_ts = None
        
        # 2. Determine Download Range
        # Default: Download from requested 'since'
        fetch_since_ts = int(since_dt.timestamp() * 1000)
        
        if not df_local.empty and last_ts is not None and isinstance(last_ts, (int, float)):
            # We have data up to last_ts.
            # If our stored data covers up to 'now' (approx), we might not need to download much.
            
            # Logic: We define "Full Life" as: 
            # If we have data, we assume it starts from "inception" OR from wherever we started last time.
            # We ONLY check the TAIL.
            
            # If last_ts < until_dt: We need to update tail.
            # Start download from last_ts + 1 candle duration approx.
            # Safest is last_ts + 1ms (CCXT handles overlap usually exclusive/inclusive depending on exchange, 
            # but standard is inclusive. So +1ms avoids dup of last candle).
            
            until_ts_int = int(until_dt.timestamp() * 1000)
            if last_ts < until_ts_int:
                 fetch_since_ts = int(last_ts) + 1
                 logger.info(f"Incremental update needed. Downloading from {datetime.fromtimestamp(fetch_since_ts/1000)}")
            else:
                 logger.info("Local data covers request. No network fetch needed.")
                 fetch_since_ts = None # No fetch needed
        
        # 3. Fetch New Data (if needed)
        df_new = pd.DataFrame()
        if fetch_since_ts is not None:
            # If fetching, and we have NO local data, maybe we want to fetch from INCEPTION?
            # User said: "baixar toda a vida do ativo mas apenas uma vez"
            # So if local is empty, we probably should ignore 'since_str' (which might be 2023) and download from 2017?
            # BUT 'fetch_data' is called by BacktestService with a specific range.
            # If we enforce "Full Life", we should set `fetch_since_ts` to 2017-01-01 IF df_local is empty.
            if df_local.empty:
                logger.info("First run (empty cache). Downloading from 2017-01-01 (Full History mode).")
                inception_ts = int(datetime(2017, 1, 1).timestamp() * 1000)
                # But wait, if user requested 2023, and we download 2017, it takes minimal time extra and saves future.
                fetch_since_ts = inception_ts
            
            until_ts_download = int(datetime.now().timestamp() * 1000) # Always update to NOW
            
            df_new = self._download_loop(symbol, timeframe, fetch_since_ts, until_ts_download, limit)
        
        # 4. Merge and Save
        if not df_new.empty:
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
             # Ensure directory exists again just in case
             os.makedirs(os.path.dirname(parquet_path), exist_ok=True)
             df_combined.to_parquet(parquet_path, index=False)
             
             df_final = df_combined
        else:
             df_final = df_local
             
        if df_final.empty:
            # If we have a cache file but it's empty, try to force a full re-download (only once to prevent infinite recursion)
            if os.path.exists(parquet_path) and _retry_count == 0:
                logger.warning(f"Cache file exists for {symbol} {timeframe} but is empty. Attempting full re-download...")
                try:
                    os.remove(parquet_path)
                    logger.info(f"Deleted empty cache file. Retrying download for {symbol} {timeframe}...")
                    # Retry with fresh download from inception (with retry flag to prevent infinite loop)
                    return self.fetch_data(symbol, timeframe, since_str, until_str, limit, progress_callback, _retry_count=1)
                except Exception as e:
                    logger.error(f"Error removing cache file: {e}")
            else:
                if _retry_count > 0:
                    logger.error(f"Still no data after retry for {symbol} {timeframe}. This may indicate the symbol is not available on the exchange or the timeframe is invalid.")
                else:
                    logger.warning(f"No data available for {symbol} {timeframe} and no cache file exists.")
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
                    return self.fetch_data(symbol, timeframe, since_str, until_str, limit, progress_callback, _retry_count=1)
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
                                    df_combined.to_parquet(parquet_path, index=False)
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
                    return self.fetch_data(symbol, timeframe, since_str, until_str, limit, progress_callback, _retry_count=1)
                except:
                    pass
        
        logger.info(f"Returning {len(df_slice)} rows for {symbol} {timeframe} from {since_dt} to {until_dt}")
        return df_slice
    
    def fetch_intraday_data(self, symbol, timeframe='15m', since_str=None, until_str=None):
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
        return self.fetch_data(symbol, timeframe, since_str, until_str)
    
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
        
        logger.info(f"Starting download loop for {symbol} from {datetime.fromtimestamp(since_ts_int/1000)} "
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
