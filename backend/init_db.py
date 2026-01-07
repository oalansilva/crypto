# file: backend/init_db.py
from app.database import engine, Base
from app.models import BacktestRun, BacktestResult

print("Creating database tables locally (SQLite)...")
Base.metadata.create_all(bind=engine)
print(" Tables created in backtest.db")
