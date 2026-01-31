"""
Migration: Replace is_portfolio with tier column in favorite_strategies table.

This migration replaces the boolean is_portfolio flag with a tier system:
- Tier 1: Core obrigatório (green)
- Tier 2: Bons complementares (gold)
- Tier 3: Outros (red)
- NULL: Sem tier (no tier assigned)
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


def migrate_to_tier_system(db_path: str = None):
    """Replace is_portfolio column with tier column."""
    db_path = _get_db_path(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if tier column already exists
    cursor.execute("PRAGMA table_info(favorite_strategies)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'tier' in columns:
        print("WARNING: Column 'tier' already exists, skipping migration...")
        conn.close()
        return
    
    # Check if is_portfolio exists
    has_portfolio_column = 'is_portfolio' in columns
    
    if has_portfolio_column:
        # Add tier column
        cursor.execute("""
            ALTER TABLE favorite_strategies 
            ADD COLUMN tier INTEGER
        """)
        
        # Migrate data: if is_portfolio was True, set tier to 1 (Core obrigatório)
        cursor.execute("""
            UPDATE favorite_strategies 
            SET tier = 1 
            WHERE is_portfolio = 1
        """)
        
        # Drop old is_portfolio column (SQLite doesn't support DROP COLUMN directly)
        # We'll need to recreate the table
        print("Migrating data and recreating table structure...")
        
        # Get all data
        cursor.execute("SELECT * FROM favorite_strategies")
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        
        # Create new table without is_portfolio
        cursor.execute("""
            CREATE TABLE favorite_strategies_new (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                symbol TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                strategy_name TEXT NOT NULL,
                parameters TEXT NOT NULL,
                metrics TEXT,
                created_at TIMESTAMP,
                notes TEXT,
                tier INTEGER
            )
        """)
        
        # Copy data (excluding is_portfolio column)
        portfolio_idx = column_names.index('is_portfolio')
        for row in rows:
            row_list = list(row)
            # Remove is_portfolio value
            row_list.pop(portfolio_idx)
            # Ensure tier is set if is_portfolio was True
            tier_idx = len(row_list) - 1  # tier is last column
            if row[portfolio_idx]:  # if is_portfolio was True
                row_list[tier_idx] = 1
            cursor.execute("""
                INSERT INTO favorite_strategies_new 
                (id, name, symbol, timeframe, strategy_name, parameters, metrics, created_at, notes, tier)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, row_list)
        
        # Drop old table and rename new one
        cursor.execute("DROP TABLE favorite_strategies")
        cursor.execute("ALTER TABLE favorite_strategies_new RENAME TO favorite_strategies")
        
        print("SUCCESS: Migrated from is_portfolio to tier system")
    else:
        # Just add tier column if is_portfolio doesn't exist
        cursor.execute("""
            ALTER TABLE favorite_strategies 
            ADD COLUMN tier INTEGER
        """)
        print("SUCCESS: Added 'tier' column to favorite_strategies table")
    
    conn.commit()
    conn.close()


def run_migration():
    """Run the migration."""
    print("Running tier system migration...")
    migrate_to_tier_system()
    print("Migration completed successfully!")


if __name__ == "__main__":
    run_migration()
