from src.data.ccxt_loader import CCXTLoader
import os

def test_loader():
    loader = CCXTLoader()
    print("Fetching data (First run - should hit API)...")
    # Fetch 1 month of BTC data
    df = loader.fetch_data('BTC/USDT', '1d', '2023-01-01 00:00:00', '2023-02-01 00:00:00')
    
    assert not df.empty, "DataFrame should not be empty"
    print(f"Rows fetched: {len(df)}")
    print(df.head(2))
    
    # Check if cache file exists
    files = os.listdir('data')
    print(f"Cache files: {files}")
    assert len(files) > 0, "Cache file should exist"

    print("\nFetching data (Second run - should hit Cache)...")
    start_time = os.times().elapsed
    df2 = loader.fetch_data('BTC/USDT', '1d', '2023-01-01 00:00:00', '2023-02-01 00:00:00')
    end_time = os.times().elapsed
    
    assert len(df) == len(df2), "Cached data should match fetched data"
    print(f"Rows fetched from cache: {len(df2)}")
    print(f"Time taken: {end_time - start_time:.4f}s (should be very fast)")

if __name__ == "__main__":
    test_loader()
