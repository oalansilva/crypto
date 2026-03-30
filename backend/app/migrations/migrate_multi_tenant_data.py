"""Migração multi-tenant: cria usuário padrão e associa dados existentes.

Revision ID: migrate_multi_tenant_data
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
import uuid
import bcrypt


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

        DEFAULT_EMAIL = "o.alan.silva@gmail.com"
        DEFAULT_PASSWORD = "TempPass123!"
        DEFAULT_NAME = "Alan Silva"

        # Hash password
        password_hash = bcrypt.hashpw(DEFAULT_PASSWORD.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")

        # Check if user already exists
        cur.execute("SELECT id FROM users WHERE email = ?", (DEFAULT_EMAIL.lower(),))
        row = cur.fetchone()

        if row:
            user_id = row[0]
            print(f"User {DEFAULT_EMAIL} already exists with id={user_id}")
        else:
            # Create user
            user_id = str(uuid.uuid4())
            cur.execute(
                """
                INSERT INTO users (id, email, password_hash, name, created_at)
                VALUES (?, ?, ?, ?, datetime('now'))
                """,
                (user_id, DEFAULT_EMAIL.lower(), password_hash, DEFAULT_NAME),
            )
            print(f"Created user {DEFAULT_EMAIL} with id={user_id}")

        # Associate existing signal_history records
        cur.execute("UPDATE signal_history SET user_id = ? WHERE user_id IS NULL", (user_id,))
        signals_updated = cur.rowcount
        print(f"Updated {signals_updated} signal_history records")

        # Associate existing portfolio_snapshots records
        cur.execute("UPDATE portfolio_snapshots SET user_id = ? WHERE user_id IS NULL", (user_id,))
        portfolio_updated = cur.rowcount
        print(f"Updated {portfolio_updated} portfolio_snapshots records")

        conn.commit()
        print("Migration migrate_multi_tenant_data: OK")
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()
