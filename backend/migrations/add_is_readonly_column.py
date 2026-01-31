"""
Migration: Add is_readonly column to combo_templates table

This migration adds a new column to support protecting pre-built templates
from accidental modifications. Pre-built templates must be cloned before editing.
"""
import sqlite3
import sys
from pathlib import Path

def _get_db_path():
    # backend/migrations -> backend/app/database
    backend_app = Path(__file__).resolve().parent.parent / "app"
    if str(backend_app.parent) not in sys.path:
        sys.path.insert(0, str(backend_app.parent))
    try:
        from app.database import DB_PATH
        return str(DB_PATH)
    except Exception:
        return str(Path(__file__).resolve().parent.parent / "backtest.db")

def migrate():
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
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
