"""
Migration: Add start_date and end_date to favorite_strategies.

Period (6m / 2y / todo) is part of the uniqueness key for batch skip logic.
"""

import sqlite3
from pathlib import Path


def _get_db_path(db_path):
    if db_path is not None:
        return db_path
    try:
        from app.database import DB_PATH
        return str(DB_PATH)
    except Exception:
        return str(Path(__file__).resolve().parents[2] / "backtest.db")


def migrate(db_path: str = None):
    db_path = _get_db_path(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(favorite_strategies)")
    columns = [row[1] for row in cursor.fetchall()]

    for col in ("start_date", "end_date"):
        if col in columns:
            continue
        cursor.execute(f"ALTER TABLE favorite_strategies ADD COLUMN {col} TEXT")
    conn.commit()
    conn.close()
    print("SUCCESS: Added start_date, end_date to favorite_strategies")


if __name__ == "__main__":
    migrate()
