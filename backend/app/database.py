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
# Single source of truth: all migrations and scripts should use this path (backend/backtest.db)
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "backtest.db"
# Use absolute path for SQLite
DB_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH}")

# Force SQLite if DATABASE_URL not explicitly set
if "DATABASE_URL" not in os.environ:
    DB_URL = f"sqlite:///{DB_PATH}"

if "postgres" in DB_URL or "postgresql" in DB_URL:
    engine = create_engine(DB_URL)
else:
    # SQLite needs specific args for multithreading check
    engine = create_engine(
        DB_URL, connect_args={"check_same_thread": False}
    )
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def ensure_sqlite_migrations() -> None:
    """Apply lightweight SQLite migrations that SQLAlchemy create_all won't handle.

    We keep this minimal: add missing columns when the table already exists.
    """

    if not DB_URL.startswith("sqlite:"):
        return

    import sqlite3

    conn = sqlite3.connect(str(DB_PATH))
    try:
        cur = conn.cursor()

        def _resolve_default_user_id() -> str | None:
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if not cur.fetchone():
                return None
            cur.execute(
                "SELECT id FROM users WHERE lower(email) = ? LIMIT 1",
                ("o.alan.silva@gmail.com",),
            )
            row = cur.fetchone()
            return str(row[0]) if row and row[0] else None

        default_user_id = _resolve_default_user_id()

        # favorite_strategies: add user_id if missing and backfill legacy rows to the default owner when known
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='favorite_strategies'")
        row = cur.fetchone()
        if row:
            cur.execute("PRAGMA table_info(favorite_strategies)")
            cols = {r[1] for r in cur.fetchall()}
            if "user_id" not in cols:
                cur.execute("ALTER TABLE favorite_strategies ADD COLUMN user_id TEXT")
                conn.commit()
                if default_user_id:
                    cur.execute(
                        "UPDATE favorite_strategies SET user_id = ? WHERE user_id IS NULL",
                        (default_user_id,),
                    )
                    conn.commit()

        # monitor_preferences: add price_timeframe if missing
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='monitor_preferences'")
        row = cur.fetchone()
        if row:
            cur.execute("PRAGMA table_info(monitor_preferences)")
            cols = {r[1] for r in cur.fetchall()}  # r[1] = name
            if "price_timeframe" not in cols:
                cur.execute("ALTER TABLE monitor_preferences ADD COLUMN price_timeframe TEXT DEFAULT '1d'")
                conn.commit()

            # monitor_preferences: add theme if missing
            if "theme" not in cols:
                cur.execute("ALTER TABLE monitor_preferences ADD COLUMN theme TEXT NOT NULL DEFAULT 'dark-green'")
                conn.commit()

            # monitor_preferences started as single-tenant with PK(symbol). Rebuild with PK(user_id, symbol).
            if "user_id" not in cols:
                cur.execute("ALTER TABLE monitor_preferences RENAME TO monitor_preferences_legacy")
                cur.execute(
                    """
                    CREATE TABLE monitor_preferences (
                        user_id TEXT NOT NULL,
                        symbol TEXT NOT NULL,
                        in_portfolio BOOLEAN NOT NULL DEFAULT 0,
                        card_mode TEXT NOT NULL DEFAULT 'price',
                        price_timeframe TEXT NOT NULL DEFAULT '1d',
                        theme TEXT NOT NULL DEFAULT 'dark-green',
                        updated_at DATETIME,
                        PRIMARY KEY (user_id, symbol)
                    )
                    """
                )
                if default_user_id:
                    cur.execute(
                        """
                        INSERT INTO monitor_preferences (
                            user_id, symbol, in_portfolio, card_mode, price_timeframe, theme, updated_at
                        )
                        SELECT ?, symbol, in_portfolio, card_mode, COALESCE(price_timeframe, '1d'),
                               COALESCE(theme, 'dark-green'), updated_at
                        FROM monitor_preferences_legacy
                        """,
                        (default_user_id,),
                    )
                cur.execute("DROP TABLE monitor_preferences_legacy")
                conn.commit()
    finally:
        conn.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
