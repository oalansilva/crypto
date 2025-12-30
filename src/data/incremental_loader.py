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

    def fetch_data(self, symbol, timeframe, since_str, until_str=None, limit=1000):
        """
        Smart fetch: Check local Parquet -> Download Delta -> Append -> Return Slice
        """
        # Parse Dates (Ensure UTC)
        since_dt = pd.to_datetime(since_str).tz_localize('UTC') if pd.to_datetime(since_str).tz is None else pd.to_datetime(since_str)
        if until_str:
            until_dt = pd.to_datetime(until_str).tz_localize('UTC') if pd.to_datetime(until_str).tz is None else pd.to_datetime(until_str)
        else:
            until_dt = pd.Timestamp.now(tz='UTC')
        
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
                         last_ts = df_local['timestamp'].max()
                     else:
                         # try index if datetime
                         pass
            except Exception as e:
                logger.error(f"Error reading local parquet: {e}. Will redownload.")
                df_local = pd.DataFrame() # Corrupt?
        
        # 2. Determine Download Range
        # Default: Download from requested 'since'
        fetch_since_ts = int(since_dt.timestamp() * 1000)
        
        if not df_local.empty and last_ts is not None:
            # We have data up to last_ts.
            # If our stored data covers up to 'now' (approx), we might not need to download much.
            
            # Logic: We define "Full Life" as: 
            # If we have data, we assume it starts from "inception" OR from wherever we started last time.
            # We ONLY check the TAIL.
            
            # If last_ts < until_dt: We need to update tail.
            # Start download from last_ts + 1 candle duration approx.
            # Safest is last_ts + 1ms (CCXT handles overlap usually exclusive/inclusive depending on exchange, 
            # but standard is inclusive. So +1ms avoids dup of last candle).
            
            if last_ts < int(until_dt.timestamp() * 1000):
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
            logger.warning("No data available.")
            return df_final
            
        # 5. Return Requested Slice
        # Filter by requested since_str / until_str
        # df_final has 'timestamp_utc' datetime column?
        # My _download_loop should ensure 'timestamp_utc' exists.
        
        # Slice
        mask = (df_final['timestamp_utc'] >= since_dt)
        if until_dt:
            mask &= (df_final['timestamp_utc'] <= until_dt)
            
        return df_final.loc[mask].copy()

    def _download_loop(self, symbol, timeframe, since_ts, until_ts, limit):
        all_ohlcv = []
        current_since = since_ts
        
        logger.info(f"Starting download loop for {symbol} from {datetime.fromtimestamp(current_since/1000)}")
        
        while current_since < until_ts:
            try:
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since=current_since, limit=limit)
                if not ohlcv:
                    break
                
                last_candle_ts = ohlcv[-1][0]
                
                for candle in ohlcv:
                    if candle[0] < until_ts:
                        all_ohlcv.append(candle)
                        
                next_since = last_candle_ts + 1
                if next_since <= current_since:
                    break
                current_since = next_since
                
                if len(ohlcv) < limit:
                    break # Reached end of data
                    
            except Exception as e:
                logger.error(f"Download error: {e}")
                time.sleep(5)
                continue
                
        if not all_ohlcv:
            return pd.DataFrame()
            
        df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp_utc'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        return df
