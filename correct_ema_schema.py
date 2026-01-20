
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
    
    indicators = template_data.get("indicators", [])
    
    # 1. Revert Indicator to EMA
    if indicators and len(indicators) > 0:
        print(f"Current Indicator Type: {indicators[0]['type']}")
        if indicators[0]["type"] == "sma" and indicators[0]["alias"] == "short":
            print("Reverting 'short' indicator to EMA (as requested by user).")
            indicators[0]["type"] = "ema"
            template_data["indicators"] = indicators
    
    # 2. Fix Optimization Schema Key (sma_short -> ema_short)
    params = opt_schema.get("parameters", {})
    if "sma_short" in params:
        print("Renaming optimization parameter 'sma_short' to 'ema_short' to match indicator.")
        params["ema_short"] = params.pop("sma_short")
        opt_schema["parameters"] = params # Update back
        
        # Also update correlated_groups if present
        if "correlated_groups" in opt_schema:
            groups = opt_schema["correlated_groups"]
            new_groups = []
            for group in groups:
                new_group = [param.replace("sma_short", "ema_short") for param in group]
                new_groups.append(new_group)
            opt_schema["correlated_groups"] = new_groups
            print("Updated correlated_groups.")

    # Save changes
    cursor.execute("""
        UPDATE combo_templates 
        SET template_data = ?, optimization_schema = ? 
        WHERE name = 'multi_ma_crossover'
    """, (json.dumps(template_data), json.dumps(opt_schema)))
    
    conn.commit()
    print("✅ Database corrected: Indicator=EMA, Schema=ema_short.")

    # Verify final state
    print("\nFinal Schema Keys:", list(opt_schema.keys()))
    print("Final Indicator 0:", template_data["indicators"][0])

else:
    print("Template not found.")

conn.close()
