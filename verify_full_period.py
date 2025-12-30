import requests
import json
import time

API_URL = "http://127.0.0.1:8000/api"

def test_full_period():
    payload = {
        "mode": "run",
        "exchange": "binance",
        "symbol": "BTC/USDT",
        "timeframe": "1d", # Use 1d for speed
        "full_period": True,
        "since": None,
        "strategies": ["sma_cross"],
        "cash": 10000,
        "fee": 0.001
    }
    
    print("Testing Full Period (since=None)...")
    print("Sending payload:", json.dumps(payload, indent=2))
    try:
        resp = requests.post(f"{API_URL}/backtest/run", json=payload)
        if resp.status_code != 200:
            print(f"Failed with status {resp.status_code}")
            print(resp.text)
            return False
            
        data = resp.json()
        print("Response:", data)
        run_id = data.get("run_id")
        if run_id:
            print(f"Job started: {run_id}")
            return True
        else:
            print("No run_id returned")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_5m_timeframe():
    # Test valid 5m timeframe (without full period for quick check)
    payload = {
        "mode": "run",
        "exchange": "binance",
        "symbol": "BTC/USDT",
        "timeframe": "5m", 
        "since": "2024-01-01 00:00:00",
        "until": "2024-01-02 00:00:00",
        "strategies": ["sma_cross"],
        "cash": 10000,
        "fee": 0.001
    }
    print("\nTesting 5m Timeframe...")
    try:
        resp = requests.post(f"{API_URL}/backtest/run", json=payload)
        if resp.status_code != 200:
             # Just checking if it accepts 5m, might fail on data download if not available, but should accept request
             print(f"Status {resp.status_code}")
             print(resp.text)
             # If validation error on timeframe, it returns 422
             return resp.status_code == 200
        print("Response:", resp.json())
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success_fp = test_full_period()
    success_5m = test_5m_timeframe()
    
    if success_fp and success_5m:
        print("\nVerification SUCCESS: All tests passed")
    else:
        print("\nVerification FAILED")
