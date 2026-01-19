"""
Migration: Add optimization_schema column to combo_templates table.

This migration adds support for storing optimization parameter schemas
directly in the database, enabling runtime configuration without code deployment.
"""

import sqlite3
from pathlib import Path


def add_optimization_schema_column(db_path: str = None):
    """Add optimization_schema JSON column to combo_templates table."""
    
    if db_path is None:
        project_root = Path(__file__).parent.parent.parent
        db_path = str(project_root / "data" / "crypto_backtest.db")
    
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
