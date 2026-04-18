"""Adiciona coluna user_id às tabelas signal_history e portfolio_snapshots.

Revision ID: add_user_id_columns
"""

from __future__ import annotations

import sqlite3
from pathlib import Path


def run_migration():
    import os

    DB_PATH = Path(__file__).resolve().parent.parent.parent / "backtest.db"

    # Only run for SQLite
    if "postgresql" in os.getenv("DATABASE_URL", "") or "postgres" in os.getenv("DATABASE_URL", ""):
        print("Migration skipped: PostgreSQL detected")
        return

    conn = sqlite3.connect(str(DB_PATH))
    try:
        cur = conn.cursor()

        # Add user_id to signal_history if not exists
        cur.execute("PRAGMA table_info(signal_history)")
        signal_cols = {r[1] for r in cur.fetchall()}
        if "user_id" not in signal_cols:
            cur.execute("ALTER TABLE signal_history ADD COLUMN user_id INTEGER")
            print("Added user_id to signal_history")
        else:
            print("user_id already exists in signal_history")

        # Add user_id to portfolio_snapshots if not exists
        cur.execute("PRAGMA table_info(portfolio_snapshots)")
        portfolio_cols = {r[1] for r in cur.fetchall()}
        if "user_id" not in portfolio_cols:
            cur.execute("ALTER TABLE portfolio_snapshots ADD COLUMN user_id INTEGER")
            print("Added user_id to portfolio_snapshots")
        else:
            print("user_id already exists in portfolio_snapshots")

        conn.commit()
        print("Migration add_user_id_columns: OK")
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()
