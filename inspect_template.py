
import sqlite3
import json
import os

db_path = "backend/data/crypto_backtest.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT template_data, optimization_schema FROM combo_templates WHERE name = 'multi_ma_crossover'")
row = cursor.fetchone()

if row:
    data = json.loads(row[0])
    schema = json.loads(row[1])
    print("Template Data:")
    print(json.dumps(data, indent=2))
    print("\nOptimization Schema:")
    print(json.dumps(schema, indent=2))
else:
    print("Template not found")

conn.close()
