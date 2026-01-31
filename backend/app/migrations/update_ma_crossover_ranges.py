"""
Update optimization schema for multi_ma_crossover template with expanded ranges.
"""

import sqlite3
import json
from pathlib import Path

def _get_db_path():
    try:
        from app.database import DB_PATH
        return str(DB_PATH)
    except Exception:
        return str(Path(__file__).parent.parent.parent / "backtest.db")


def update_multi_ma_crossover_ranges():
    """Update optimization ranges for multi_ma_crossover template."""
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # New expanded optimization schema
    new_optimization_schema = {
        "sma_short": {"min": 3, "max": 20, "step": 1, "default": 9},
        "sma_medium": {"min": 10, "max": 40, "step": 1, "default": 21},
        "sma_long": {"min": 20, "max": 100, "step": 1, "default": 50},
        "stop_loss": {"min": 0.005, "max": 0.13, "step": 0.002, "default": 0.015}
    }
    
    # Update the template
    cursor.execute("""
        UPDATE combo_templates 
        SET optimization_schema = ?
        WHERE name = 'multi_ma_crossover'
    """, (json.dumps(new_optimization_schema),))
    
    if cursor.rowcount > 0:
        print(f"✅ Updated optimization schema for multi_ma_crossover")
        print(f"   New ranges:")
        print(f"   - sma_short: 3 to 20 (was 5 to 15)")
        print(f"   - sma_medium: 10 to 40 (was 15 to 30)")
        print(f"   - sma_long: 20 to 100 (was 30 to 100)")
    else:
        print(f"⚠️  Template 'multi_ma_crossover' not found in database")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Database updated successfully!")

if __name__ == "__main__":
    update_multi_ma_crossover_ranges()
