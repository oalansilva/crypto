import sqlite3
import json

DB_PATH = "backend/backtest.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT template_data FROM combo_templates WHERE name = 'multi_ma_crossover'")
row = cursor.fetchone()

if row:
    data = json.loads(row[0])
    print("Entry Logic:", data.get('entry_logic'))
    print("Indicators:", json.dumps(data.get('indicators'), indent=2))
else:
    print("Template not found")

conn.close()
