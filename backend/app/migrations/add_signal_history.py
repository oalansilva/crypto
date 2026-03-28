"""Add signal_history table and indexes.

Revision ID: add_signal_history
"""
from __future__ import annotations

import sqlite3
from pathlib import Path


def run_migration():
    from app.config import get_settings
    import os

    settings = get_settings()
    DB_PATH = Path(__file__).resolve().parent.parent.parent / "backtest.db"

    # Only run for SQLite
    if "postgresql" in os.getenv("DATABASE_URL", "") or "postgres" in os.getenv("DATABASE_URL", ""):
        print("Migration skipped: PostgreSQL detected")
        return

    conn = sqlite3.connect(str(DB_PATH))
    try:
        cur = conn.cursor()

        # Create table if not exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS signal_history (
                id TEXT PRIMARY KEY,
                asset TEXT NOT NULL,
                type TEXT NOT NULL,
                confidence INTEGER NOT NULL,
                target_price REAL NOT NULL,
                stop_loss REAL NOT NULL,
                indicators TEXT,
                created_at TIMESTAMP NOT NULL,
                risk_profile TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'ativo',
                entry_price REAL,
                exit_price REAL,
                quantity REAL,
                pnl REAL,
                trigger_price REAL,
                updated_at TIMESTAMP,
                archived TEXT DEFAULT 'no'
            )
        """)

        # Create indexes
        indexes = [
            "CREATE INDEX IF NOT EXISTS ix_signal_history_asset ON signal_history(asset)",
            "CREATE INDEX IF NOT EXISTS ix_signal_history_created_at ON signal_history(created_at)",
            "CREATE INDEX IF NOT EXISTS ix_signal_history_status ON signal_history(status)",
            "CREATE INDEX IF NOT EXISTS ix_signal_history_archived ON signal_history(archived)",
            "CREATE INDEX IF NOT EXISTS ix_signal_history_asset_created ON signal_history(asset, created_at)",
            "CREATE INDEX IF NOT EXISTS ix_signal_history_status_created ON signal_history(status, created_at)",
        ]
        for idx_sql in indexes:
            cur.execute(idx_sql)

        conn.commit()
        print("Migration add_signal_history: OK")
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()
