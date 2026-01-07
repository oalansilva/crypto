# file: backend/test_api.py
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8003"

print("=" * 60)
print("TESTE COMPLETO DO BACKEND")
print("=" * 60)

# 1. Health Check
print("\n1. Testing Health Check...")
response = requests.get(f"{BASE_URL}/api/health")
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")

# 2. Get Presets
print("\n2. Testing Presets...")
response = requests.get(f"{BASE_URL}/api/presets")
presets = response.json()
print(f"   Found {len(presets)} presets")
for preset in presets:
    print(f"   - {preset['name']}")

# 3. Start a Compare Backtest (small dataset for speed)
print("\n3. Starting Compare Backtest (BTC 1 month, 4h)...")
payload = {
    "mode": "compare",
    "exchange": "binance",
    "symbol": "BTC/USDT",
    "timeframe": "4h",
    "since": "2024-11-01 00:00:00",
    "until": "2024-12-01 00:00:00",
    "strategies": ["sma_cross", "rsi_reversal"],
    "params": {
        "sma_cross": {"fast": 10, "slow": 20},
        "rsi_reversal": {"rsi_period": 14, "oversold": 30, "overbought": 70}
    },
    "cash": 10000,
    "fee": 0.001,
    "slippage": 0.0005
}

response = requests.post(f"{BASE_URL}/api/backtest/compare", json=payload)
print(f"   Status: {response.status_code}")
try:
    result = response.json()
    print(f"   Response: {json.dumps(result, indent=2)}")
except json.JSONDecodeError:
    print(f"    Response text (Not JSON): {response.text}")
    exit(1)

run_id = result.get('run_id')

if not run_id:
    print("    Failed to start backtest")
    exit(1)

print(f"    Backtest started with run_id: {run_id}")

# 4. Poll Status
print("\n4. Polling Status...")
max_attempts = 60
attempt = 0

while attempt < max_attempts:
    response = requests.get(f"{BASE_URL}/api/backtest/status/{run_id}")
    status_data = response.json()
    status = status_data['status']
    
    print(f"   Attempt {attempt + 1}: Status = {status}")
    
    if status == "DONE":
        print("    Backtest completed!")
        break
    elif status == "FAILED":
        print(f"    Backtest failed: {status_data.get('error_message')}")
        exit(1)
    
    time.sleep(2)
    attempt += 1

if attempt >= max_attempts:
    print("    Timeout waiting for backtest")
    exit(1)

# 5. Get Result
print("\n5. Fetching Result...")
response = requests.get(f"{BASE_URL}/api/backtest/result/{run_id}")
result_data = response.json()

print(f"   Dataset: {result_data['dataset']['symbol']} {result_data['dataset']['timeframe']}")
print(f"   Candles: {result_data['dataset']['candle_count']}")
print(f"   Strategies: {len(result_data['results'])}")

print("\n   Results:")
for strategy_name, strategy_result in result_data['results'].items():
    metrics = strategy_result['metrics']
    print(f"\n   {strategy_name}:")
    print(f"     - Return: {metrics['total_return_pct']*100:.2f}%")
    print(f"     - Max Drawdown: {metrics['max_drawdown_pct']*100:.2f}%")
    print(f"     - Trades: {metrics['num_trades']}")
    print(f"     - Win Rate: {metrics['win_rate']*100:.2f}%")
    print(f"     - Sharpe: {metrics['sharpe']:.4f}")

# 6. List Runs
print("\n6. Listing Recent Runs...")
response = requests.get(f"{BASE_URL}/api/backtest/runs?limit=5")
runs = response.json()
print(f"   Found {len(runs)} recent runs:")
for run in runs:
    print(f"   - {run['id']}: {run['mode']} on {run['symbol']} ({run['status']})")

print("\n" + "=" * 60)
print(" TESTE COMPLETO FINALIZADO COM SUCESSO!")
print("=" * 60)
