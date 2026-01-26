import sqlite3
import os

files = [
    "backtest.db",
    "backend/backtest.db",
    "backend/data/crypto_backtest.db"
]

print(f"{'File':<40} | {'Table':<20} | {'Count':<5}")
print("-" * 70)

for f in files:
    if not os.path.exists(f):
        print(f"{f:<40} | [NOT FOUND]")
        continue
        
    try:
        conn = sqlite3.connect(f)
        cursor = conn.cursor()
        
        # Check favorites
        try:
            cursor.execute("SELECT COUNT(*) FROM favorite_strategies")
            fav_count = cursor.fetchone()[0]
        except:
            fav_count = "ERR"
            
        # Check templates
        try:
            cursor.execute("SELECT COUNT(*) FROM combo_templates")
            tpl_count = cursor.fetchone()[0]
        except:
            tpl_count = "ERR"
            
        print(f"{f:<40} | favorites            | {fav_count}")
        print(f"{'':<40} | combo_templates      | {tpl_count}")
        conn.close()
    except Exception as e:
        print(f"{f:<40} | [ERROR: {e}]")
    print("-" * 70)
