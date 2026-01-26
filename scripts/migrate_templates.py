import sqlite3
import json
import os

SOURCE_DB = "backend/data/crypto_backtest.db"
TARGET_DB = "backend/backtest.db"

if not os.path.exists(SOURCE_DB):
    print(f"❌ Source DB not found: {SOURCE_DB}")
    exit(1)

if not os.path.exists(TARGET_DB):
    print(f"❌ Target DB not found: {TARGET_DB}")
    exit(1)

conn_src = sqlite3.connect(SOURCE_DB)
curs_src = conn_src.cursor()

conn_tgt = sqlite3.connect(TARGET_DB)
curs_tgt = conn_tgt.cursor()

# Get all templates from source
curs_src.execute("""
    SELECT name, description, is_example, is_prebuilt, is_readonly,
           template_data, optimization_schema, created_at
    FROM combo_templates
""")
source_rows = curs_src.fetchall()
print(f"Found {len(source_rows)} templates in source.")

migrated = 0
skipped = 0

for row in source_rows:
    name, desc, is_ex, is_pre, is_ro, tpl_data, opt_schema, created_at = row
    
    # Check if exists in target
    curs_tgt.execute("SELECT 1 FROM combo_templates WHERE name = ?", (name,))
    if curs_tgt.fetchone():
        print(f"⏭️  Skipping existing: {name}")
        skipped += 1
        continue
    
    # Insert
    try:
        curs_tgt.execute("""
            INSERT INTO combo_templates (
                name, description, is_example, is_prebuilt, is_readonly,
                template_data, optimization_schema, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (name, desc, is_ex, is_pre, is_ro, tpl_data, opt_schema, created_at))
        migrated += 1
        print(f"✅ Migrated: {name}")
    except Exception as e:
        print(f"❌ Error migrating {name}: {e}")

conn_tgt.commit()
conn_src.close()
conn_tgt.close()

print("-" * 40)
print(f"Migration Complete: {migrated} migrated, {skipped} skipped.")
