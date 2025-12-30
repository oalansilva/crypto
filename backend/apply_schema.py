# file: backend/apply_schema.py
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Read schema
with open('supabase_schema.sql', 'r', encoding='utf-8') as f:
    schema_sql = f.read()

# Connection string
# Format: postgresql://postgres:[PASSWORD]@db.fgyxpxvkmzsifwdayesu.supabase.co:5432/postgres
conn_str = "postgresql://postgres:F27*morem19*@db.fgyxpxvkmzsifwdayesu.supabase.co:5432/postgres"

print("Connecting to Supabase Postgres...")

try:
    conn = psycopg2.connect(conn_str)
    cursor = conn.cursor()
    
    print("Executing schema SQL...")
    cursor.execute(schema_sql)
    conn.commit()
    
    print("✅ Schema applied successfully!")
    
    # Verify tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('backtest_runs', 'backtest_results')
    """)
    
    tables = cursor.fetchall()
    print(f"\n✓ Found {len(tables)} tables:")
    for table in tables:
        print(f"  - {table[0]}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
