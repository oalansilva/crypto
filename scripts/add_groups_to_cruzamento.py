
import sqlite3
import json
from pathlib import Path

def migrate():
    project_root = Path(__file__).parent.parent
    db_path = str(project_root / "backend" / "data" / "crypto_backtest.db")
    print(f"Using database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT optimization_schema FROM combo_templates WHERE name = 'multi_ma_crossover'")
    row = cursor.fetchone()
    
    if not row:
        print("Template 'multi_ma_crossover' not found.")
        return

    current_schema = json.loads(row[0]) if row[0] else {}
    
    print("Current schema keys:", current_schema.keys())
    
    # Check if already migrated
    if "parameters" in current_schema and "correlated_groups" in current_schema:
        print("Schema already has parameters/groups structure.")
        # But we force update to ensure groups are correct
    
    # Construct new schema
    new_schema = {
        "parameters": {},
        "correlated_groups": [
            ["sma_short", "sma_medium", "sma_long"]
        ]
    }
    
    # If current schema is nested (already migrated or partially), extract parameters
    if "parameters" in current_schema:
        new_schema["parameters"] = current_schema["parameters"]
    else:
        # It's flat, so the whole thing is parameters
        new_schema["parameters"] = current_schema

    # Fix parameter name: ema_short -> sma_short
    if "ema_short" in new_schema["parameters"]:
        print("Renaming ema_short to sma_short...")
        new_schema["parameters"]["sma_short"] = new_schema["parameters"].pop("ema_short")
    
    # Ensure sma_short defaults match if created new/renamed
    if "sma_short" in new_schema["parameters"]:
         # Optional: Ensure defaults are what we expect? 
         # Let's trust the existing values but just ensure key is correct.
         pass
    else:
        # If neither existed, ensure sma_short is there (should have been from seed, but just in case)
        new_schema["parameters"]["sma_short"] = {"min": 3, "max": 20, "step": 1, "default": 9}

    # Verify stop_loss exists

    # Verify stop_loss exists
    if "stop_loss" not in new_schema["parameters"]:
        print("Adding default stop_loss to parameters...")
        new_schema["parameters"]["stop_loss"] = {"min": 0.005, "max": 0.13, "step": 0.002, "default": 0.015}

    print("New Schema Structure:")
    print(json.dumps(new_schema, indent=2))
    
    cursor.execute("""
        UPDATE combo_templates 
        SET optimization_schema = ?
        WHERE name = 'multi_ma_crossover'
    """, (json.dumps(new_schema),))
    
    conn.commit()
    conn.close()
    print("Migration successful.")

if __name__ == "__main__":
    migrate()
