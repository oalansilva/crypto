# file: backend/app/database.py
import os
import logging
import sys

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import get_settings

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
        (
            os.getenv("APP_ENV")
            or os.getenv("APP_ENVIRONMENT")
            or os.getenv("ENV")
            or os.getenv("RUNTIME_ENV")
            or ""
        )
        .strip()
        .lower()
    )
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


def _is_postgres_url(url: str) -> bool:
    normalized = (url or "").strip().lower()
    return normalized.startswith("postgresql://") or normalized.startswith("postgresql+psycopg2://")


def resolve_db_url() -> str:
    """Resolve the main app DB URL.

    Production and QA runtime are PostgreSQL-only.
    """

    settings = get_settings()
    explicit_url = getattr(settings, "database_url", None) or os.getenv("DATABASE_URL")
    if explicit_url:
        if not _is_postgres_url(explicit_url):
            raise RuntimeError(
                "DATABASE_URL must point to PostgreSQL. Set DATABASE_URL/postgres://..."
            )
        return explicit_url

    raise RuntimeError(
        "DATABASE_URL is required and must point to PostgreSQL."
    )


DB_URL = resolve_db_url()

engine = create_engine(DB_URL, pool_pre_ping=True)
logger = logging.getLogger(__name__)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def ensure_runtime_schema_migrations() -> None:
    """Backward-compatible runtime migration entrypoint used during app startup."""

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
        conn.execute(text("""
                CREATE TABLE IF NOT EXISTS market_indicator (
                    id BIGSERIAL PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    ts TIMESTAMPTZ NOT NULL,
                    ema_9 NUMERIC,
                    ema_21 NUMERIC,
                    sma_20 NUMERIC,
                    sma_50 NUMERIC,
                    rsi_14 NUMERIC,
                    macd_line NUMERIC,
                    macd_signal NUMERIC,
                    macd_histogram NUMERIC,
                    source TEXT NOT NULL DEFAULT 'market',
                    provider TEXT NOT NULL DEFAULT 'talib',
                    source_window JSONB,
                    row_count INTEGER,
                    is_recomputed BOOLEAN NOT NULL DEFAULT FALSE,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE (symbol, timeframe, ts)
                )
                """))
        conn.execute(text("""
                CREATE INDEX IF NOT EXISTS uq_market_indicator_symbol_timeframe_ts
                ON market_indicator (symbol, timeframe, ts)
                """))
        conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_market_indicator_symbol_timeframe_ts
                ON market_indicator (symbol, timeframe, ts DESC)
                """))
        conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_market_indicator_updated_at
                ON market_indicator (updated_at)
                """))

    timescale_functions_available = True
    try:
        with engine.begin() as conn:
            conn.execute(text("""
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
                """))
            conn.execute(text("""
                CREATE UNIQUE INDEX IF NOT EXISTS uq_market_ohlcv_symbol_timeframe_candle_time
                ON market_ohlcv (symbol, timeframe, candle_time)
                """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_market_ohlcv_symbol_timeframe_time
                ON market_ohlcv (symbol, timeframe, candle_time DESC)
                """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_market_ohlcv_symbol_timeframe_source
                ON market_ohlcv (symbol, timeframe, source)
                """))
            logger.info("market_ohlcv table and indexes ensured.")
    except Exception as exc:
        logger.warning(
            "Could not create or migrate market_ohlcv table/indexes.",
            extra={
                "event": "ohlcv_schema_create_error",
                "table": "market_ohlcv",
                "error": str(exc),
            },
        )
        return

    try:
        with engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb"))
        timescale_functions_available = True
    except Exception as exc:
        logger.warning(
            "Timescale configuration for market_ohlcv failed, keeping table as regular table.",
            extra={
                "event": "ohlcv_timescale_setup_error",
                "table": "market_ohlcv",
                "error": str(exc),
            },
        )
        timescale_functions_available = False

    if timescale_functions_available:
        with engine.begin() as conn:
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
                timescale_functions_available = False

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

        if _policy_checks_enabled() and timescale_functions_available:
            connect = getattr(engine, "connect", None)
            context = connect() if callable(connect) else engine.begin()
            with context as conn:
                _verify_market_ohlcv_timescale_policies(
                    conn, timescale_functions_available=timescale_functions_available
                )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def sync_postgres_identity_sequences() -> None:
    """Advance Postgres integer PK sequences after importing explicit IDs."""

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
        checks["hypertable"] = bool(conn.execute(text("""
                    SELECT EXISTS(
                        SELECT 1
                        FROM timescaledb_information.hypertables
                        WHERE hypertable_name = 'market_ohlcv'
                          AND hypertable_schema = 'public'
                    )
                    """)).scalar())

        if timescale_functions_available:
            for check_name, proc_name in (
                ("retention_policy", "policy_retention"),
                ("compression_policy", "policy_compression"),
            ):
                checks[check_name] = bool(
                    conn.execute(
                        text("""
                            SELECT EXISTS(
                                SELECT 1
                                FROM timescaledb_information.jobs
                                WHERE proc_name = :proc_name
                                  AND hypertable_name = 'market_ohlcv'
                            )
                            """),
                        {"proc_name": proc_name},
                    ).scalar()
                )

            checks["compression_setting"] = bool(conn.execute(text("""
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
                        """)).scalar())

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
