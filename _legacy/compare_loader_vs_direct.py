
import pandas as pd
import sys
import os
 
# Add project root to path
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'backend'))
 
from src.data.incremental_loader import IncrementalLoader
 
import pandas_ta as ta

async def run_comparison():
    print("--- COMPARING LOADER VS DIRECT READ ---")
    
    # 1. Get Data via IncrementalLoader (as used in compare_strategies_full.py)
    loader = IncrementalLoader()
    # Mocking the request parameters
    symbol = "BTC/USDT"
    timeframe = "1d"
    start_date = "2017-10-01"
    end_date = "2026-01-01"
    
    print(f"Fetching via Loader: {start_date} to {end_date}")
    df_service = loader.fetch_data(symbol, timeframe, start_date, end_date)
    
    # Calculate SMA 37 on Service Data
    df_service['sma37'] = ta.sma(df_service['close'], length=37)
    
    # 2. Get Data via Direct Read (as used in verify_source_match.py)
    print("Fetching via Direct Read...")
    df_direct = pd.read_parquet('data/storage/binance/BTC_USDT_1d.parquet')
    
    # Apply manual fix used in verification
    if 'timestamp' in df_direct.columns:
        df_direct['timestamp'] = pd.to_datetime(df_direct['timestamp'], unit='ms', utc=True)
        df_direct.set_index('timestamp', inplace=True)
        
    # Apply truncation
    start_dt = pd.to_datetime(start_date).tz_localize('UTC')
    end_dt = pd.to_datetime(end_date).tz_localize('UTC')
    
    df_direct = df_direct[(df_direct.index >= start_dt) & (df_direct.index <= end_dt)]
    
    df_direct['sma37'] = ta.sma(df_direct['close'], length=37)
    
    # 3. Compare
    print(f"\nService Rows: {len(df_service)}")
    print(f"Direct Rows: {len(df_direct)}")
    
    # Compare Sep 29 2025
    target = pd.Timestamp('2025-09-29', tz='UTC')
    
    if target in df_service.index:
        sma_s = df_service.loc[target, 'sma37']
        sma_d = df_direct.loc[target, 'sma37']
        print(f"\nTarget Date {target}:")
        print(f"Service SMA 37: {sma_s}")
        print(f"Direct SMA 37: {sma_d}")
    else:
        print(f"Target date missing!")
        
    # Check alignemnt of last 50 days before Sep 29
    # This is calculating SMA 37
    check_start = target - pd.Timedelta(days=50)
    
    df_s_zoom = df_service[(df_service.index >= check_start) & (df_service.index <= target)]
    df_d_zoom = df_direct[(df_direct.index >= check_start) & (df_direct.index <= target)]
    
    if not df_s_zoom.equals(df_d_zoom[['close']]): # Simple check if logic allows
         # Compare iterated
         print("\n--- DETAILED ROW COMPARISON (Last 10 discrepancies) ---")
         
         # Align indices
         common_idx = df_s_zoom.index.intersection(df_d_zoom.index)
         
         diff_count = 0
         for idx in common_idx:
             c_s = df_s_zoom.loc[idx, 'close']
             c_d = df_d_zoom.loc[idx, 'close']
             if abs(c_s - c_d) > 0.001:
                 print(f"{idx}: Service={c_s}, Direct={c_d}")
                 diff_count += 1
         
         if diff_count == 0:
             print("Close prices match on common indices.")
         else:
             print(f"Found {diff_count} price mismatches!")
             
         # Check missing indices
         missing_in_service = df_d_zoom.index.difference(df_s_zoom.index)
         missing_in_direct = df_s_zoom.index.difference(df_d_zoom.index)
         
         if not missing_in_service.empty:
             print(f"\nDates in Direct but MISSING in Service ({len(missing_in_service)}):")
             print(missing_in_service[:5])
             
         if not missing_in_direct.empty:
             print(f"\nDates in Service but MISSING in Direct ({len(missing_in_direct)}):")
             print(missing_in_direct[:5])
             
    else:
        print("Dataframes identical in this window.")
 
if __name__ == "__main__":
    import asyncio
    asyncio.run(run_comparison())
