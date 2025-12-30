from src.data.incremental_loader import IncrementalLoader
import shutil
import os
import time
import pandas as pd

def test_storage():
    # Setup
    if not os.path.exists('data/storage'):
        os.makedirs('data/storage')
        
    loader = IncrementalLoader(cache_dir='data/storage_test')
    symbol = "BTC/USDT"
    timeframe = "1d"
    
    # Clean up previous test
    path = loader._get_parquet_path(symbol, timeframe)
    if os.path.exists(path):
        os.remove(path)
    if os.path.exists(loader.base_path):
        try:
             # Remove files inside
             for f in os.listdir(loader.base_path):
                 os.remove(os.path.join(loader.base_path, f))
        except Exception:
             pass
        
    print(f"1. First Run (Download full history, expect 2017 -> Now)...")
    start = time.time()
    # Req: 2023-01 -> 2023-02
    # Loader logic: If empty, download from 2017.
    df1 = loader.fetch_data(symbol, timeframe, "2023-01-01 00:00:00", "2023-02-01 00:00:00")
    duration = time.time() - start
    print(f"   Done in {duration:.2f}s. Rows returned: {len(df1)}")
    
    # Check file exists
    if not os.path.exists(path):
        print(f"ERROR: Parquet file not found at {path}")
        return
        
    # Check file size/rows
    df_full = pd.read_parquet(path)
    print(f"   Storage contains {len(df_full)} rows. Min date: {df_full['timestamp_utc'].min()} Max date: {df_full['timestamp_utc'].max()}")
    
    # Verification: Should verify it has data BEFORE 2023 (since it dled from 2017)
    if df_full['timestamp_utc'].min() > pd.Timestamp("2020-01-01", tz='UTC'):
        print("WARNING: Data doesn't seem to start from 2017/Inception.")
    
    print("\n2. Second Run (Local Fetch - Slice)...")
    start = time.time()
    df2 = loader.fetch_data(symbol, timeframe, "2023-01-15 00:00:00", "2023-02-15 00:00:00")
    duration2 = time.time() - start
    print(f"   Done in {duration2:.2f}s. Rows returned: {len(df2)}")
    
    if duration2 > 2.0:
        print("WARNING: Second run took > 2s. Is it really using cache?")
    else:
        print("   Speed looks good (cached).")
    
    print("\nSUCCESS")

if __name__ == "__main__":
    test_storage()
