
import sqlite3
import logging
from datetime import datetime, timedelta
import pandas as pd
import pandas_ta as ta
from app.services.opportunity_service import OpportunityService
from app.strategies.combos.combo_strategy import ComboStrategy

logging.basicConfig(level=logging.INFO)
service = OpportunityService()

# DB Connection
conn = sqlite3.connect('backtest.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 0. Check for duplicates
cursor.execute("SELECT id, strategy_name, parameters FROM favorite_strategies WHERE symbol='BTC/USDT'")
all_btc = cursor.fetchall()
print(f"\n--- ALL BTC STRATEGIES ({len(all_btc)}) ---")
for r in all_btc:
    print(dict(r))


# Fetch Data
df = service.loader.fetch_data(
    symbol="BTC/USDT",
    timeframe="1d",
    since_str=(datetime.now() - timedelta(days=500)).strftime("%Y-%m-%d"),
    limit=None
)

print("\n--- SCENARIO 6: EMA 5 vs SMA 5 (Param Collision?) ---")
ind_6 = [
    {'type': 'ema', 'alias': 'short', 'params': {'length': 5}},
    {'type': 'sma', 'alias': 'medium', 'params': {'length': 5}}
]
strat_6 = ComboStrategy(ind_6, 'crossover(short, medium)', '', 0)
df_6 = strat_6.calculate_indicators(df)
row = df_6.iloc[-2]
d6 = abs(row['short'] - row['medium']) / abs(row['medium']) * 100
print(f"Jan 24 | EMA 5: {row['short']:.2f} | SMA 5: {row['medium']:.2f} | Dist: {d6:.2f}%")


# Setup Default Strategy (9/21/50)
indicators = [
    {'type': 'ema', 'alias': 'short', 'params': {'length': 9}},
    {'type': 'sma', 'alias': 'medium', 'params': {'length': 21}},
    {'type': 'sma', 'alias': 'long', 'params': {'length': 50}}
]

strategy = ComboStrategy(
    indicators=indicators,
    entry_logic='crossover(short, medium)',
    exit_logic='crossunder(short, medium)',
    stop_loss=0.0
)

df_calc = strategy.calculate_indicators(df)

# Check last 3 rows for multiple scenarios
print("\n--- SCENARIO 1: Correct per DB (EMA 5 / SMA 19) ---")
ind_1 = [
    {'type': 'ema', 'alias': 'short', 'params': {'length': 5}},
    {'type': 'sma', 'alias': 'medium', 'params': {'length': 19}}
]
strat_1 = ComboStrategy(ind_1, 'crossover(short, medium)', '', 0)
df_1 = strat_1.calculate_indicators(df)
row = df_1.iloc[-2] # Jan 24 Close
d1 = abs(row['short'] - row['medium']) / abs(row['medium']) * 100
print(f"Jan 24 | Short: {row['short']:.2f} | Med: {row['medium']:.2f} | Dist: {d1:.2f}%")

print("\n--- SCENARIO 2: All EMAs (EMA 5 / EMA 19) - Matching User? ---")
ind_2 = [
    {'type': 'ema', 'alias': 'short', 'params': {'length': 5}},
    {'type': 'ema', 'alias': 'medium', 'params': {'length': 19}}
]
strat_2 = ComboStrategy(ind_2, 'crossover(short, medium)', '', 0)
df_2 = strat_2.calculate_indicators(df)
row = df_2.iloc[-2]
d2 = abs(row['short'] - row['medium']) / abs(row['medium']) * 100
print(f"Jan 24 | Short: {row['short']:.2f} | Med: {row['medium']:.2f} | Dist: {d2:.2f}%")

print("\n--- SCENARIO 3: All SMAs (SMA 5 / SMA 19) ---")
ind_3 = [
    {'type': 'sma', 'alias': 'short', 'params': {'length': 5}},
    {'type': 'sma', 'alias': 'medium', 'params': {'length': 19}}
]
strat_3 = ComboStrategy(ind_3, 'crossover(short, medium)', '', 0)
df_3 = strat_3.calculate_indicators(df)
row = df_3.iloc[-2]
d3 = abs(row['short'] - row['medium']) / abs(row['medium']) * 100
print(f"Jan 24 | Short: {row['short']:.2f} | Med: {row['medium']:.2f} | Dist: {d3:.2f}%")

print("\n--- SCENARIO 4: Price vs Short (Is Dashboard showing this?) ---")
d4 = abs(row['close'] - row['short']) / abs(row['short']) * 100
print(f"Jan 24 | Price: {row['close']} | Short: {row['short']:.2f} | Dist: {d4:.2f}%")

print("\n--- SCENARIO 5: Price vs Medium ---")
d5 = abs(row['close'] - row['medium']) / abs(row['medium']) * 100
print(f"Jan 24 | Price: {row['close']} | Med: {row['medium']:.2f} | Dist: {d5:.2f}%")

