"""
Migration: Add start_date and end_date to favorite_strategies.

Period (6m / 2y / todo) is part of the uniqueness key for batch skip logic.
"""

import sqlite3
from pathlib import Path


def migrate(db_path: str = None):
    if db_path is None:
        project_root = Path(__file__).resolve().parents[2]
        db_path = str(project_root / "backtest.db")
        if not Path(db_path).exists():
            db_path = str(project_root / "data" / "crypto_backtest.db")

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
