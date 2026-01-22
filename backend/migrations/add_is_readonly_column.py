"""
Migration: Add is_readonly column to combo_templates table

This migration adds a new column to support protecting pre-built templates
from accidental modifications. Pre-built templates must be cloned before editing.
"""
import sqlite3
from pathlib import Path

def migrate():
    # Get database path
    db_path = Path(__file__).parent.parent / "data" / "crypto_backtest.db"
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(combo_templates)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'is_readonly' in columns:
            print("✓ Column 'is_readonly' already exists. Skipping migration.")
            return
        
        print("Adding 'is_readonly' column to combo_templates...")
        
        # Add the new column with default value 0 (False)
        cursor.execute("""
            ALTER TABLE combo_templates 
            ADD COLUMN is_readonly BOOLEAN DEFAULT 0 NOT NULL
        """)
        
        # Set is_readonly=1 for all pre-built templates
        cursor.execute("""
            UPDATE combo_templates 
            SET is_readonly = 1 
            WHERE is_prebuilt = 1
        """)
        
        conn.commit()
        
        # Verify migration
        cursor.execute("SELECT COUNT(*) FROM combo_templates WHERE is_readonly = 1")
        readonly_count = cursor.fetchone()[0]
        
        print(f"✓ Migration complete! Set {readonly_count} pre-built templates as read-only.")
        
    except Exception as e:
        conn.rollback()
        print(f"✗ Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
