
import sqlite3
import json

db_path = "backend/data/crypto_backtest.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Fetch current data
cursor.execute("SELECT template_data, optimization_schema FROM combo_templates WHERE name = 'multi_ma_crossover'")
row = cursor.fetchone()

if row:
    template_data = json.loads(row[0])
    opt_schema = json.loads(row[1])
    
    print("Old Stop Loss (Template):", template_data.get("stop_loss"))
    
    # 1. Disable Stop Loss in Template (0.0)
    # Using specific dict format if previously used, or just float
    template_data["stop_loss"] = 0.0
    
    # 2. Disable Default in Optimization Schema
    params = opt_schema.get("parameters", {})
    if "stop_loss" in params:
        print("Old Stop Loss Default (Schema):", params["stop_loss"].get("default"))
        params["stop_loss"]["default"] = 0.0
        opt_schema["parameters"] = params

    # Save changes
    cursor.execute("""
        UPDATE combo_templates 
        SET template_data = ?, optimization_schema = ? 
        WHERE name = 'multi_ma_crossover'
    """, (json.dumps(template_data), json.dumps(opt_schema)))
    
    conn.commit()
    print("✅ Database updated: Stop Loss Default = 0.0")

else:
    print("Template not found.")

conn.close()
