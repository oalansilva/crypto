"""
Check current CRUZAMENTOMEDIAS template in database
"""

import sqlite3
import json

db_path = 'backend/data/crypto_backtest.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get current template
cursor.execute("""
    SELECT name, optimization_schema, template_data 
    FROM combo_templates 
    WHERE name = 'CRUZAMENTOMEDIAS'
""")

row = cursor.fetchone()

if row:
    name = row[0]
    optimization_schema = row[1]
    template_data = row[2]
    
    print(f"Template: {name}")
    print(f"\nCurrent optimization_schema:")
    if optimization_schema:
        schema = json.loads(optimization_schema)
        print(json.dumps(schema, indent=2))
    else:
        print("  NULL (not set)")
    
    print(f"\nTemplate data:")
    if template_data:
        data = json.loads(template_data)
        print(json.dumps(data, indent=2))
else:
    print("Template 'CRUZAMENTOMEDIAS' not found in database")

conn.close()
