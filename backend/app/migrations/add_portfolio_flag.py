"""
Migration: Add is_portfolio column to favorite_strategies table.

This migration adds support for marking favorite strategies as part of
a portfolio for monitoring, allowing users to separate portfolio assets
from other strategies.
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
        return str(Path(__file__).resolve().parent.parent.parent / "backtest.db")


def add_portfolio_flag_column(db_path: str = None):
    """Add is_portfolio boolean column to favorite_strategies table."""
    db_path = _get_db_path(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if column already exists
    cursor.execute("PRAGMA table_info(favorite_strategies)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'is_portfolio' in columns:
        print("WARNING: Column 'is_portfolio' already exists, skipping...")
        conn.close()
        return
    
    # Add column with default value False
    cursor.execute("""
        ALTER TABLE favorite_strategies 
        ADD COLUMN is_portfolio BOOLEAN DEFAULT 0 NOT NULL
    """)
    
    conn.commit()
    conn.close()
    
    print("SUCCESS: Added 'is_portfolio' column to favorite_strategies table")


def run_migration():
    """Run the migration."""
    print("Running portfolio flag migration...")
    add_portfolio_flag_column()
    print("Migration completed successfully!")


if __name__ == "__main__":
    run_migration()
