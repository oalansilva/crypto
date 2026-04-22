# file: backend/app/database.py
import os
import logging
import sys
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import get_settings

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "backtest.db"
_LOCAL_RUNTIME_ENVIRONMENTS = {
    "dev",
    "development",
    "devserver",
    "local",
    "localdev",
    "qa",
    "test",
    "testing",
}


def _is_local_runtime() -> bool:
    env = (
        os.getenv("APP_ENV")
        or os.getenv("APP_ENVIRONMENT")
        or os.getenv("ENV")
        or os.getenv("RUNTIME_ENV")
        or ""
    ).strip().lower()
    if env in _LOCAL_RUNTIME_ENVIRONMENTS:
        return True
    return False


def _policy_checks_enabled() -> bool:
    override = os.getenv("MARKET_OHLCV_VERIFY_POLICIES", "").strip().lower()
    if override in {"0", "false", "no", "off"}:
        return False
    if override in {"1", "true", "yes", "on"}:
        return True
    return not _is_local_runtime()


def _allow_sqlite_for_tests() -> bool:
    raw = os.getenv("ALLOW_SQLITE_FOR_TESTS", "").strip().lower()
    if raw in {"1", "true", "yes", "on"}:
        return True
    return any("pytest" in arg for arg in sys.argv)


def _is_postgres_url(url: str) -> bool:
    normalized = (url or "").strip().lower()
    return normalized.startswith("postgresql://") or normalized.startswith("postgresql+psycopg2://")


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
logger = logging.getLogger(__name__)

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
            if "status" not in cols:
                cur.execute("ALTER TABLE users ADD COLUMN status TEXT NOT NULL DEFAULT 'active'")
                conn.commit()
            if "suspended_until" not in cols:
                cur.execute("ALTER TABLE users ADD COLUMN suspended_until DATETIME")
                conn.commit()
            if "suspension_reason" not in cols:
                cur.execute("ALTER TABLE users ADD COLUMN suspension_reason TEXT")
                conn.commit()
            if "is_banned" not in cols:
                cur.execute("ALTER TABLE users ADD COLUMN is_banned INTEGER NOT NULL DEFAULT 0")
                conn.commit()
            if "notes" not in cols:
                cur.execute("ALTER TABLE users ADD COLUMN notes TEXT")
                conn.commit()

        # admin_action_logs table
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='admin_action_logs'"
        )
        if not cur.fetchone():
            cur.execute("""
                CREATE TABLE admin_action_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    actor_user_id TEXT NOT NULL,
                    target_user_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    target_subject TEXT,
                    reason TEXT NOT NULL,
                    metadata_json TEXT,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """)
            cur.execute(
                "CREATE INDEX IF NOT EXISTS ix_admin_action_logs_actor ON admin_action_logs (actor_user_id)"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS ix_admin_action_logs_target ON admin_action_logs (target_user_id)"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS ix_admin_action_logs_action ON admin_action_logs (action)"
            )
            cur.execute(
                "CREATE INDEX IF NOT EXISTS ix_admin_action_logs_created_at ON admin_action_logs (created_at)"
            )
            conn.commit()

        # favorite_strategies: add user_id if missing and backfill legacy rows to the default owner when known
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='favorite_strategies'"
        )
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
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='monitor_preferences'"
        )
        row = cur.fetchone()
        if row:
            cur.execute("PRAGMA table_info(monitor_preferences)")
            cols = {r[1] for r in cur.fetchall()}  # r[1] = name
            if "price_timeframe" not in cols:
                cur.execute(
                    "ALTER TABLE monitor_preferences ADD COLUMN price_timeframe TEXT DEFAULT '1d'"
                )
                conn.commit()

            # monitor_preferences: add theme if missing
            if "theme" not in cols:
                cur.execute(
                    "ALTER TABLE monitor_preferences ADD COLUMN theme TEXT NOT NULL DEFAULT 'dark-green'"
                )
                conn.commit()

            # monitor_preferences started as single-tenant with PK(symbol). Rebuild with PK(user_id, symbol).
            if "user_id" not in cols:
                cur.execute("ALTER TABLE monitor_preferences RENAME TO monitor_preferences_legacy")
                cur.execute("""
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
                    """)
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

    if DB_URL.startswith("sqlite:"):
        return

    with engine.begin() as conn:
        conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'active'
                """))
        conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS suspended_until TIMESTAMP NULL
                """))
        conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS suspension_reason TEXT NULL
                """))
        conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS is_banned BOOLEAN NOT NULL DEFAULT FALSE
                """))
        conn.execute(text("""
                ALTER TABLE users
                ADD COLUMN IF NOT EXISTS notes TEXT NULL
                """))

        conn.execute(text("""
                UPDATE users
                SET status = 'active'
                WHERE status IS NULL OR btrim(status) = ''
                """))
        conn.execute(text("""
                CREATE TABLE IF NOT EXISTS admin_action_logs (
                    id SERIAL PRIMARY KEY,
                    actor_user_id VARCHAR NOT NULL,
                    target_user_id VARCHAR NOT NULL,
                    action VARCHAR NOT NULL,
                    target_subject VARCHAR NULL,
                    reason TEXT NOT NULL,
                    metadata_json TEXT NULL,
                    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
                """))
        conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_admin_action_logs_actor
                ON admin_action_logs (actor_user_id)
                """))
        conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_admin_action_logs_target
                ON admin_action_logs (target_user_id)
                """))
        conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_admin_action_logs_action
                ON admin_action_logs (action)
                """))
        conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_admin_action_logs_created_at
                ON admin_action_logs (created_at)
                """))

        timescale_functions_available = True
        try:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb"))
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS market_ohlcv (
                        symbol TEXT NOT NULL,
                        timeframe TEXT NOT NULL,
                        candle_time TIMESTAMPTZ NOT NULL,
                        open NUMERIC NOT NULL,
                        high NUMERIC NOT NULL,
                        low NUMERIC NOT NULL,
                        close NUMERIC NOT NULL,
                        volume NUMERIC NOT NULL,
                        source TEXT NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        PRIMARY KEY (symbol, timeframe, candle_time, source)
                    )
                    """
                )
            )
            conn.execute(
                text(
                    """
                    CREATE UNIQUE INDEX IF NOT EXISTS uq_market_ohlcv_symbol_timeframe_candle_time
                    ON market_ohlcv (symbol, timeframe, candle_time)
                    """
                )
            )
            conn.execute(
                text(
                    """
                    CREATE INDEX IF NOT EXISTS idx_market_ohlcv_symbol_timeframe_time
                    ON market_ohlcv (symbol, timeframe, candle_time DESC)
                    """
                )
            )
            conn.execute(
                text(
                    """
                    CREATE INDEX IF NOT EXISTS idx_market_ohlcv_symbol_timeframe_source
                    ON market_ohlcv (symbol, timeframe, source)
                    """
                )
            )

            # Best effort Timescale migration path.
            try:
                conn.execute(
                    text(
                        "SELECT create_hypertable('market_ohlcv', 'candle_time', if_not_exists => TRUE)"
                    )
                )
            except Exception as exc:
                logger.warning(
                    "Could not create hypertable market_ohlcv.",
                    extra={
                        "event": "ohlcv_timescale_hypertable_error",
                        "table": "market_ohlcv",
                        "error": str(exc),
                    },
                )

            try:
                conn.execute(
                    text(
                        "SELECT add_retention_policy('market_ohlcv', INTERVAL '2 years', if_not_exists => TRUE)"
                    )
                )
            except Exception as exc:
                logger.warning(
                    "Could not apply timescale retention policy for market_ohlcv.",
                    extra={
                        "event": "ohlcv_timescale_retention_policy_error",
                        "table": "market_ohlcv",
                        "error": str(exc),
                    },
                )
                timescale_functions_available = False

            try:
                conn.execute(
                    text(
                        "ALTER TABLE market_ohlcv SET (timescaledb.compress, "
                        "timescaledb.compress_orderby = 'candle_time DESC', "
                        "timescaledb.compress_segmentby = 'symbol, timeframe, source')"
                    )
                )
            except Exception as exc:
                logger.warning(
                    "Could not set compression settings for market_ohlcv.",
                    extra={
                        "event": "ohlcv_timescale_compression_setting_error",
                        "table": "market_ohlcv",
                        "error": str(exc),
                    },
                )
                timescale_functions_available = False

            try:
                conn.execute(
                    text(
                        "SELECT add_compression_policy('market_ohlcv', INTERVAL '30 days', if_not_exists => TRUE)"
                    )
                )
            except Exception as exc:
                logger.warning(
                    "Could not apply timescale compression policy for market_ohlcv.",
                    extra={
                        "event": "ohlcv_timescale_compression_policy_error",
                        "table": "market_ohlcv",
                        "error": str(exc),
                    },
                )
                timescale_functions_available = False
            if _policy_checks_enabled():
                _verify_market_ohlcv_timescale_policies(
                    conn, timescale_functions_available=timescale_functions_available
                )
        except Exception as exc:
            logger.warning(
                "Timescale configuration for market_ohlcv failed, keeping table as regular table.",
                extra={
                    "event": "ohlcv_timescale_setup_error",
                    "table": "market_ohlcv",
                    "error": str(exc),
                },
            )


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
        "admin_action_logs",
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
                        COALESCE((SELECT MAX(id) FROM """
                    + table_name
                    + """), 0) + 1,
                        false
                    )
                    """
                ),
                {"sequence_name": sequence_name},
            )


def _verify_market_ohlcv_timescale_policies(
    conn,
    *,
    timescale_functions_available: bool = True,
) -> None:
    """Best-effort startup check for Timescale policy presence on market_ohlcv."""

    checks = {
        "hypertable": False,
        "retention_policy": False,
        "compression_setting": False,
        "compression_policy": False,
    }

    try:
        checks["hypertable"] = bool(
            conn.execute(
                text(
                    """
                    SELECT EXISTS(
                        SELECT 1
                        FROM timescaledb_information.hypertables
                        WHERE hypertable_name = 'market_ohlcv'
                          AND hypertable_schema = 'public'
                    )
                    """
                )
            ).scalar()
        )

        if timescale_functions_available:
            for check_name, proc_name in (
                ("retention_policy", "policy_retention"),
                ("compression_policy", "policy_compression"),
            ):
                checks[check_name] = bool(
                    conn.execute(
                        text(
                            """
                            SELECT EXISTS(
                                SELECT 1
                                FROM timescaledb_information.jobs
                                WHERE proc_name = :proc_name
                                  AND hypertable_name = 'market_ohlcv'
                            )
                            """
                        ),
                        {"proc_name": proc_name},
                    ).scalar()
                )

            checks["compression_setting"] = bool(
                conn.execute(
                    text(
                        """
                        SELECT EXISTS(
                            SELECT 1
                            FROM pg_class c
                            JOIN pg_namespace n ON n.oid = c.relnamespace
                            WHERE c.relname = 'market_ohlcv'
                              AND n.nspname = 'public'
                              AND EXISTS (
                                    SELECT 1
                                    FROM unnest(c.reloptions) AS opt(v)
                                    WHERE lower(v::text) LIKE 'timescaledb.compress=%'
                              )
                        )
                        """
                    )
                ).scalar()
            )

        missing = sorted(name for name, is_ok in checks.items() if not is_ok)
        if missing:
            logger.warning(
                "Timescale policy verification is incomplete for market_ohlcv.",
                extra={
                    "event": "ohlcv_timescale_policy_verification_incomplete",
                    "table": "market_ohlcv",
                    "checks": checks,
                    "missing": missing,
                },
            )
            return

        logger.info(
            "Timescale policies for market_ohlcv verified as active.",
            extra={
                "event": "ohlcv_timescale_policies_verified",
                "table": "market_ohlcv",
                "checks": checks,
            },
        )
    except Exception as exc:
        logger.warning(
            "Could not complete timescale policy verification for market_ohlcv.",
            extra={
                "event": "ohlcv_timescale_policy_verification_error",
                "table": "market_ohlcv",
                "error": str(exc),
            },
        )
