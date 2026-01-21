
import sqlite3
import json
from pathlib import Path

def migrate_4d():
    project_root = Path(__file__).parent.parent
    db_path = str(project_root / "backend" / "data" / "crypto_backtest.db")
    print(f"Using database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Target Template
    template_name = 'multi_ma_crossover'
    
    cursor.execute("SELECT optimization_schema FROM combo_templates WHERE name = ?", (template_name,))
    row = cursor.fetchone()
    
    if not row:
        print(f"Template '{template_name}' not found.")
        return

    current_schema = json.loads(row[0]) if row[0] else {}
    
    # 1. Ensure 'stop_loss' is in parameters
    if "parameters" not in current_schema:
        current_schema["parameters"] = {}
        
    if "stop_loss" not in current_schema["parameters"]:
        print("Adding stop_loss to parameters...")
        # Default coarse range for Round 1
        current_schema["parameters"]["stop_loss"] = {
            "min": 0.005, 
            "max": 0.15, 
            "step": 0.005, 
            "default": 0.02
        }

    # 2. Update Correlated Groups to be 4D
    # [ema_short, sma_medium, sma_long, stop_loss]
    print("Updating correlated_groups to 4D...")
    
    new_group = ["ema_short", "sma_medium", "sma_long", "stop_loss"]
    
    # Validate all exist
    missing = [p for p in new_group if p not in current_schema["parameters"]]
    if missing:
        print(f"Error: Missing parameters {missing}")
        return

    current_schema["correlated_groups"] = [new_group]
    
    print("New Schema Structure:")
    print(json.dumps(current_schema, indent=2))
    
    cursor.execute("""
        UPDATE combo_templates 
        SET optimization_schema = ?
        WHERE name = ?
    """, (json.dumps(current_schema), template_name))
    
    conn.commit()
    conn.close()
    print("Migration successful. 4D Grid enabled.")

if __name__ == "__main__":
    migrate_4d()
