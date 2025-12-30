import sys
import os

# Add current dir to path so imports work
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models import BacktestRun

def fix_stale_runs():
    db = SessionLocal()
    try:
        stale_runs = db.query(BacktestRun).filter(BacktestRun.status == "RUNNING").all()
        count = 0
        for run in stale_runs:
            print(f"Fixing stale run: {run.id}")
            run.status = "FAILED"
            run.error_message = "Stopped due to server restart"
            count += 1
        
        db.commit()
        print(f"Fixed {count} stale runs.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    fix_stale_runs()
