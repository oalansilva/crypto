
import sqlite3
from pathlib import Path

def inspect():
    project_root = Path(__file__).parent.parent
    db_path = str(project_root / "backend" / "backtest.db")
    print(f"Inspecting: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("\nTables found:")
    for t in tables:
        print(f" - {t[0]}")
        
    conn.close()

if __name__ == "__main__":
    inspect()
