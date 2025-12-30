
import requests
import json

url = "http://127.0.0.1:8001/api/backtest/optimize"

# Case 3: Fee is null (simulating NaN input)
payload_fee_null = {
  "mode": "optimize",
  "exchange": "binance",
  "symbol": "BTC/USDT",
  "timeframe": "1d",
  "timeframes": ["1d"],
  "since": "2024-01-01 00:00:00",
  "strategies": [{"name": "rsi"}],
  "cash": 10000,
  "fee": None
}

print("\n--- Sending Fee=None ---")
try:
    r = requests.post(url, json=payload_fee_null)
    print(f"Status: {r.status_code}")
    print(r.text)
except Exception as e:
    print(e)
