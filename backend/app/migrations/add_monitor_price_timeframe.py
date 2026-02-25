"""Add price_timeframe column to monitor_preferences if missing."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def run_migration(db_path: Path) -> bool:
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA table_info(monitor_preferences)")
        columns = {row[1] for row in cursor.fetchall()}
        if "price_timeframe" in columns:
            return False

        cursor.execute(
            "ALTER TABLE monitor_preferences ADD COLUMN price_timeframe TEXT NOT NULL DEFAULT '1d'"
        )
        conn.commit()
        return True
    finally:
        conn.close()


if __name__ == "__main__":
    from app.database import DB_PATH

    changed = run_migration(Path(DB_PATH))
    if changed:
        print("price_timeframe column added to monitor_preferences")
    else:
        print("price_timeframe column already exists")
