"""
SQL Migration: Add Grid Search metadata to CRUZAMENTOMEDIAS template

This script adds correlation metadata to enable Grid Search optimization
for the CRUZAMENTOMEDIAS template.
"""

import sqlite3
import json

db_path = 'backend/data/crypto_backtest.db'

# Define the optimization schema with correlation metadata
optimization_schema = {
    "correlated_groups": [
        ["media_curta", "media_inter", "media_longa"]
    ],
    "parameters": {
        "media_curta": {
            "min": 3,
            "max": 15,
            "step": 2
        },
        "media_inter": {
            "min": 15,
            "max": 35,
            "step": 4
        },
        "media_longa": {
            "min": 25,
            "max": 60,
            "step": 5
        },
        "stop_loss": {
            "min": 0.005,
            "max": 0.13,
            "step": 0.002,
            "default": 0.03  # 3% default for crypto
        }
    }
}

print("=" * 60)
print("SQL Migration: Add Grid Search to CRUZAMENTOMEDIAS")
print("=" * 60)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check current state
cursor.execute("""
    SELECT name, optimization_schema 
    FROM combo_templates 
    WHERE name = 'Example: CRUZAMENTOMEDIAS'
""")

row = cursor.fetchone()

if not row:
    print("❌ Template 'Example: CRUZAMENTOMEDIAS' not found!")
    conn.close()
    exit(1)

name = row[0]
current_schema = row[1]

print(f"\nTemplate: {name}")
print(f"Current optimization_schema: {'SET' if current_schema else 'NULL'}")

if current_schema:
    print("\nCurrent schema:")
    print(json.dumps(json.loads(current_schema), indent=2))
    
    # Ask for confirmation
    response = input("\n⚠️  Schema already exists. Overwrite? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Migration cancelled")
        conn.close()
        exit(0)

# Update the template
print("\nUpdating template with Grid Search metadata...")

cursor.execute("""
    UPDATE combo_templates 
    SET optimization_schema = ? 
    WHERE name = 'Example: CRUZAMENTOMEDIAS'
""", (json.dumps(optimization_schema),))

conn.commit()

# Verify update
cursor.execute("""
    SELECT optimization_schema 
    FROM combo_templates 
    WHERE name = 'Example: CRUZAMENTOMEDIAS'
""")

updated_schema = cursor.fetchone()[0]

print("\n✅ Migration successful!")
print("\nNew optimization_schema:")
print(json.dumps(json.loads(updated_schema), indent=2))

print("\n" + "=" * 60)
print("Grid Search Configuration:")
print("=" * 60)
print(f"Correlated groups: {optimization_schema['correlated_groups']}")
print(f"Parameters: {list(optimization_schema['parameters'].keys())}")

# Calculate grid size
grid_size = 1
for param in optimization_schema['correlated_groups'][0]:
    param_config = optimization_schema['parameters'][param]
    min_val = param_config['min']
    max_val = param_config['max']
    step = param_config['step']
    
    # Calculate number of values
    num_values = int((max_val - min_val) / step) + 1
    grid_size *= num_values
    
    print(f"  {param}: {num_values} values ({min_val} to {max_val}, step {step})")

print(f"\nTotal Grid combinations: {grid_size}")

# Calculate stop_loss tests
stop_config = optimization_schema['parameters']['stop_loss']
stop_tests = int((stop_config['max'] - stop_config['min']) / stop_config['step']) + 1
print(f"Stop loss tests: {stop_tests}")

print(f"\n🎯 Total tests: {grid_size} + {stop_tests} = {grid_size + stop_tests}")
print("=" * 60)

conn.close()
