"""
Migration: Add is_portfolio column to favorite_strategies table.

This migration adds support for marking favorite strategies as part of
a portfolio for monitoring, allowing users to separate portfolio assets
from other strategies.
"""

import sqlite3
from pathlib import Path


def add_portfolio_flag_column(db_path: str = None):
    """Add is_portfolio boolean column to favorite_strategies table."""
    
    if db_path is None:
        project_root = Path(__file__).parent.parent.parent
        # Try both possible locations
        db_path1 = project_root / "backtest.db"
        db_path2 = project_root / "data" / "crypto_backtest.db"
        if db_path1.exists():
            db_path = str(db_path1)
        elif db_path2.exists():
            db_path = str(db_path2)
        else:
            # Default to backend/backtest.db
            db_path = str(project_root / "backtest.db")
    
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
