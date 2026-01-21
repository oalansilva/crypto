
import sqlite3
import json
from pathlib import Path

def inspect():
    project_root = Path(__file__).parent.parent
    db_path = str(project_root / "backend" / "data" / "crypto_backtest.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT optimization_schema FROM combo_templates WHERE name = 'multi_ma_crossover'")
    row = cursor.fetchone()
    
    if row and row[0]:
        schema = json.loads(row[0])
        print(json.dumps(schema, indent=2))
    else:
        print("No schema found")
        
    conn.close()

if __name__ == "__main__":
    inspect()
