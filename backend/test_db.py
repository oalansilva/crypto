# file: backend/test_db.py
from app.supabase_client import get_supabase
from app.services.run_repository import RunRepository
from uuid import uuid4

print("Connecting to Supabase...")
supabase = get_supabase()

print("Connection object:", supabase)

repo = RunRepository(supabase)

run_data = {
    "status": "PENDING",
    "mode": "test",
    "exchange": "test_ex",
    "symbol": "TEST/USDT",
    "timeframe": "1h",
    "since": "2023-01-01T00:00:00",
    "until": "2023-01-02T00:00:00",
    "strategies": ["test"],
    "params": {}
}

print("Creating test run...")
try:
    run = repo.create_run(run_data)
    print("Run created:", run)
    
    print("Deleting test run...")
    repo.delete_run(run['id'])
    print("Run deleted")
    
except Exception as e:
    print(f"❌ Error: {e}")
