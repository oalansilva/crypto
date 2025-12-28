import os
import time
import ccxt
import pandas as pd
from datetime import datetime
import hashlib

class CCXTLoader:
    def __init__(self, exchange_id='binance', cache_dir='data'):
        self.exchange_id = exchange_id
        self.cache_dir = cache_dir
        self.exchange = getattr(ccxt, exchange_id)({
            'enableRateLimit': True,  # CCXT handles rate limiting automatically
        })
        
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def fetch_data(self, symbol, timeframe, since_str, until_str=None, limit=1000):
        """
        Fetches OHLCV data with pagination and caching.
        
        :param symbol: Trading pair symbol (e.g., 'BTC/USDT')
        :param timeframe: Timeframe string (e.g., '1h', '4h', '1d')
        :param since_str: Start date string (e.g., '2023-01-01 00:00:00')
        :param until_str: End date string (e.g., '2024-01-01 00:00:00') - Optional
        :param limit: Number of candles per request (default: 1000)
        :return: DataFrame with OHLCV data
        """
        since_dt = datetime.strptime(since_str, '%Y-%m-%d %H:%M:%S')
        until_dt = datetime.strptime(until_str, '%Y-%m-%d %H:%M:%S') if until_str else datetime.now()
        
        since_ts = int(since_dt.timestamp() * 1000)
        until_ts = int(until_dt.timestamp() * 1000)
        
        # Determine cache file path
        # Generate a unique hash for the request key
        request_key = f"{self.exchange_id}_{symbol}_{timeframe}_{since_ts}_{until_ts}"
        # Sanitize symbol for filename
        safe_symbol = symbol.replace('/', '_')
        cache_filename = f"{self.exchange_id}_{safe_symbol}_{timeframe}_{since_ts}_{until_ts}.csv"
        cache_path = os.path.join(self.cache_dir, cache_filename)

        # Check cache
        if os.path.exists(cache_path):
            print(f"Loading from cache: {cache_path}")
            df = pd.read_csv(cache_path)
            # Ensure timestamp_utc is datetime
            df['timestamp_utc'] = pd.to_datetime(df['timestamp_utc'])
            return df

        print(f"Fetching data from {self.exchange_id} for {symbol}...")
        
        all_ohlcv = []
        current_since = since_ts
        
        while current_since < until_ts:
            try:
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since=current_since, limit=limit)
                
                if not ohlcv:
                    print("No more data returned.")
                    break
                
                # Filter out candles beyond 'until_ts'
                # ohlcv is list of [timestamp, open, high, low, close, volume]
                last_candle_ts = ohlcv[-1][0]
                first_candle_ts = ohlcv[0][0]
                
                print(f"Fetched {len(ohlcv)} candles. From {datetime.fromtimestamp(first_candle_ts/1000)} to {datetime.fromtimestamp(last_candle_ts/1000)}")

                # Check if we didn't move forward (prevent infinite loop)
                if last_candle_ts == current_since and len(ohlcv) == 1:
                     # Sometimes exchanges return the same starting candle if no new data
                     break

                # Append valid candles
                for candle in ohlcv:
                    if candle[0] < until_ts:
                        all_ohlcv.append(candle)
                
                # Update current_since for next batch
                # Use the timestamp of the last candle + 1 timeframe duration (approx) 
                # OR just last_candle_ts + 1ms to query 'since' usually works for exclusive start in some APIs, 
                # but CCXT standard is inclusive 'since'.
                # Safest is to take the last timestamp fetched and use it as next 'since' 
                # BUT we must handle overlaps. 
                # Actually, standard way: current_since = ohlcv[-1][0] + 1
                
                next_since = last_candle_ts + 1
                
                if next_since <= current_since:
                     # Edge case where time didn't advance
                     break
                     
                current_since = next_since
                
                if last_candle_ts >= until_ts:
                    break

                # Sleep to respect rate limits if not handled by 'enableRateLimit' (though it is)
                # self.exchange.sleep(self.exchange.rateLimit / 1000) 

            except Exception as e:
                print(f"Error fetching data: {e}")
                time.sleep(5) # Backoff on error
                continue

        # Convert to DataFrame
        df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # Drop duplicates just in case
        df.drop_duplicates(subset=['timestamp'], inplace=True)
        # Sort
        df.sort_values('timestamp', inplace=True)
        
        # Convert timestamp to human readable UTC
        df['timestamp_utc'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        
        # Select and reorder columns
        df = df[['timestamp_utc', 'open', 'high', 'low', 'close', 'volume']]
        
        # Save to cache
        if not df.empty:
            print(f"Saving to cache: {cache_path}")
            df.to_csv(cache_path, index=False)
        else:
            print("Warning: No data fetched.")

        return df

if __name__ == "__main__":
    # Simple test
    loader = CCXTLoader()
    df = loader.fetch_data('BTC/USDT', '1d', '2023-01-01 00:00:00', '2023-02-01 00:00:00')
    print(df.head())
    print(df.tail())
    print(f"Total rows: {len(df)}")
