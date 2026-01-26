import sqlite3
import json

old_db = "backend/data/crypto_backtest.db"
conn = sqlite3.connect(old_db)
cursor = conn.cursor()

cursor.execute("SELECT name, is_prebuilt, description FROM combo_templates")
rows = cursor.fetchall()

print(f"Found {len(rows)} templates in OLD DB:")
print("-" * 60)
for r in rows:
    name, is_prebuilt, desc = r
    type_str = "PREBUILT" if is_prebuilt else "CUSTOM"
    print(f"[{type_str}] {name} - {desc}")

conn.close()
