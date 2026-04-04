# file: backend/app/database.py
import os
import sys
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import get_settings


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "backtest.db"


def _allow_sqlite_for_tests() -> bool:
    raw = os.getenv("ALLOW_SQLITE_FOR_TESTS", "").strip().lower()
    if raw in {"1", "true", "yes", "on"}:
        return True
    return any("pytest" in arg for arg in sys.argv)


def _is_postgres_url(url: str) -> bool:
    normalized = (url or "").strip().lower()
    return normalized.startswith("postgresql://") or normalized.startswith(
        "postgresql+psycopg2://"
    )


def resolve_db_url() -> str:
    """Resolve the main app DB URL.

    Priority:
    1. DATABASE_URL / settings.database_url (Postgres only in runtime)

    The workflow database is managed separately and must not be reused as the
    main application runtime database.
    """

    settings = get_settings()
    explicit_url = getattr(settings, "database_url", None) or os.getenv("DATABASE_URL")
    if explicit_url:
        if not _is_postgres_url(explicit_url) and not _allow_sqlite_for_tests():
            raise RuntimeError(
                "DATABASE_URL must point to PostgreSQL. SQLite is no longer supported in runtime."
            )
        return explicit_url

    if _allow_sqlite_for_tests():
        return f"sqlite:///{DB_PATH}"

    raise RuntimeError(
        "DATABASE_URL is required and must point to PostgreSQL. SQLite fallback was removed."
    )


DB_URL = resolve_db_url()

if DB_URL.startswith("sqlite:"):
    engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DB_URL, pool_pre_ping=True)

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

        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        row = cur.fetchone()
        if row:
            cur.execute("PRAGMA table_info(users)")
            cols = {r[1] for r in cur.fetchall()}
            if "last_login" not in cols:
                cur.execute("ALTER TABLE users ADD COLUMN last_login DATETIME")
                conn.commit()

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


def ensure_runtime_schema_migrations() -> None:
    """Backward-compatible runtime migration entrypoint used during app startup."""

    ensure_sqlite_migrations()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def sync_postgres_identity_sequences() -> None:
    """Advance Postgres integer PK sequences after importing explicit IDs."""

    if DB_URL.startswith("sqlite:"):
        return

    tables = (
        "favorite_strategies",
        "combo_templates",
        "auto_backtest_runs",
        "portfolio_snapshots",
        "optimization_results",
    )

    with engine.begin() as conn:
        for table_name in tables:
            sequence_name = conn.execute(
                text("SELECT pg_get_serial_sequence(:table_name, 'id')"),
                {"table_name": table_name},
            ).scalar()
            if not sequence_name:
                continue
            conn.execute(
                text(
                    """
                    SELECT setval(
                        :sequence_name,
                        COALESCE((SELECT MAX(id) FROM """ + table_name + """), 0) + 1,
                        false
                    )
                    """
                ),
                {"sequence_name": sequence_name},
            )
