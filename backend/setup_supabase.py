# file: backend/setup_supabase.py
import os
from supabase import create_client

# Read schema SQL
with open('supabase_schema.sql', 'r', encoding='utf-8') as f:
    schema_sql = f.read()

# Get credentials from .env
from dotenv import load_dotenv
load_dotenv()

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

print(f"Connecting to Supabase: {url}")

# Create client
supabase = create_client(url, key)

# Execute SQL via RPC (using Supabase's SQL execution)
# Split by statement and execute
statements = [s.strip() for s in schema_sql.split(';') if s.strip()]

print(f"\nExecuting {len(statements)} SQL statements...")

for i, statement in enumerate(statements, 1):
    if not statement:
        continue
    try:
        # Use Supabase's rpc to execute raw SQL
        result = supabase.rpc('exec_sql', {'query': statement}).execute()
        print(f" Statement {i}/{len(statements)} executed")
    except Exception as e:
        # Try direct execution via PostgREST
        print(f"⚠ Statement {i}: {str(e)[:100]}")

print("\n Schema setup complete!")
print("\nVerifying tables...")

# Verify tables exist
try:
    runs = supabase.table('backtest_runs').select('*').limit(1).execute()
    print(" Table 'backtest_runs' exists")
except Exception as e:
    print(f" Table 'backtest_runs': {e}")

try:
    results = supabase.table('backtest_results').select('*').limit(1).execute()
    print(" Table 'backtest_results' exists")
except Exception as e:
    print(f" Table 'backtest_results': {e}")
