"""
Migration: Add optimization_schema column to combo_templates table.

This migration adds support for storing optimization parameter schemas
directly in the database, enabling runtime configuration without code deployment.
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


def add_optimization_schema_column(db_path: str = None):
    """Add optimization_schema JSON column to combo_templates table."""
    db_path = _get_db_path(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if column already exists
    cursor.execute("PRAGMA table_info(combo_templates)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'optimization_schema' in columns:
        print("⚠️  Column 'optimization_schema' already exists, skipping...")
        conn.close()
        return
    
    # Add column
    cursor.execute("""
        ALTER TABLE combo_templates 
        ADD COLUMN optimization_schema JSON
    """)
    
    conn.commit()
    conn.close()
    
    print("✅ Added 'optimization_schema' column to combo_templates table")


def run_migration():
    """Run the migration."""
    print("🔄 Running optimization_schema migration...")
    add_optimization_schema_column()
    print("✅ Migration completed successfully!")


if __name__ == "__main__":
    run_migration()
