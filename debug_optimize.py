
import requests
import json

url = "http://127.0.0.1:8001/api/backtest/optimize"

# Case 1: Valid payload
payload_valid = {
  "mode": "optimize",
  "exchange": "binance",
  "symbol": "BTC/USDT",
  "timeframe": "1d",
  "timeframes": ["1d"],
  "since": "2024-01-01 00:00:00",
  "strategies": [
    {
      "name": "rsi",
      "length": {"min": 10.0, "max": 20.0, "step": 2.0}
    }
  ],
  "params": {
      "rsi": {
          "length": {"min": 10.0, "max": 20.0, "step": 2.0}
      }
  },
  "cash": 10000,
  "fee": 0.001,
  "stop_pct": {"min": 1.0, "max": 5.0, "step": 0.5},
  "take_pct": {"min": 2.0, "max": 10.0, "step": 1.0}
}

# Case 2: Invalid payload with null (simulating NaN)
payload_invalid = {
  "mode": "optimize",
  "exchange": "binance",
  "symbol": "BTC/USDT",
  "timeframe": "1d",
  "timeframes": ["1d"],
  "since": "2024-01-01 00:00:00",
  "strategies": [
    {
      "name": "rsi",
      "length": {"min": None, "max": 20.0, "step": 2.0}
    }
  ],
  "cash": 10000
}

print("--- Sending Valid Payload ---")
try:
    r = requests.post(url, json=payload_valid)
    print(f"Status: {r.status_code}")
    print(r.text)
except Exception as e:
    print(e)
    
print("\n--- Sending Invalid Payload (None) ---")
try:
    r = requests.post(url, json=payload_invalid)
    print(f"Status: {r.status_code}")
    print(r.text)
except Exception as e:
    print(e)
