# file: backend/app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings
import os

settings = get_settings()

# Construct connection string
# Format: postgresql://postgres:[PASSWORD]@[HOST]:[PORT]/postgres
# We need to extract password from settings or env
# Since settings currently has the service_role key, we need to adapt .env to include DB password
# OR we can parse the connection string if provided.
# Let's verify what we have in settings. Since we set up .env with service_role key,
# we need to add SUPABASE_DB_URL to .env or config.

# For now, let's default to SQLite for stable local development
# This bypasses connection issues with remote Supabase
DB_URL = os.getenv("DATABASE_URL", "sqlite:///./backtest.db")

# Force SQLite if DATABASE_URL not explicitly set
if "DATABASE_URL" not in os.environ:
    DB_URL = "sqlite:///./backtest.db"

if "postgres" in DB_URL or "postgresql" in DB_URL:
    engine = create_engine(DB_URL)
else:
    # SQLite needs specific args for multithreading check
    engine = create_engine(
        DB_URL, connect_args={"check_same_thread": False}
    )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
