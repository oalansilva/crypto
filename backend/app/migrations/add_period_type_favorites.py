"""
Migration: Add period_type to favorite_strategies.

Used for skip logic (6m / 2y / all) so "Últimos 6 meses" matches across runs.
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

    if "period_type" not in columns:
        cursor.execute("ALTER TABLE favorite_strategies ADD COLUMN period_type TEXT")

    # Backfill: existing favorites get period_type from start/end
    cursor.execute("SELECT id, start_date, end_date, period_type FROM favorite_strategies")
    rows = cursor.fetchall()
    for row in rows:
        fid, start_date, end_date, pt = row[0], row[1], row[2], row[3]
        if pt is not None:
            continue
        if start_date is None and end_date is None:
            cursor.execute("UPDATE favorite_strategies SET period_type = ? WHERE id = ?", ("all", fid))
            continue
        if start_date and end_date:
            try:
                from datetime import datetime
                a = datetime.strptime(start_date[:10], "%Y-%m-%d")
                b = datetime.strptime(end_date[:10], "%Y-%m-%d")
                days = (b - a).days
                if 150 <= days <= 220:
                    cursor.execute("UPDATE favorite_strategies SET period_type = ? WHERE id = ?", ("6m", fid))
                elif 600 <= days <= 800:
                    cursor.execute("UPDATE favorite_strategies SET period_type = ? WHERE id = ?", ("2y", fid))
            except Exception:
                pass
    conn.commit()
    conn.close()
    print("SUCCESS: Added period_type to favorite_strategies and backfilled existing rows")


if __name__ == "__main__":
    migrate()
