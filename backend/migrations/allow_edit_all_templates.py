"""
Migration: Allow editing all combo templates

Sets is_readonly = 0 for all combo_templates so that every strategy
(including pre-built ones like multi_ma_crossover) can be edited directly
instead of requiring clone-first.
"""
import sqlite3
import sys
from pathlib import Path

def _get_db_path():
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
        cursor.execute("PRAGMA table_info(combo_templates)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'is_readonly' not in columns:
            print("[OK] Column 'is_readonly' not found. Run add_is_readonly_column first.")
            return

        cursor.execute("SELECT COUNT(*) FROM combo_templates WHERE is_readonly = 1")
        readonly_before = cursor.fetchone()[0]
        if readonly_before == 0:
            print("[OK] All templates are already editable. Nothing to do.")
            return

        cursor.execute("""
            UPDATE combo_templates
            SET is_readonly = 0
        """)
        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM combo_templates")
        total = cursor.fetchone()[0]
        print(f"[OK] Migration complete! All {total} templates are now editable.")
    except Exception as e:
        conn.rollback()
        print(f"[FAIL] Migration failed: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
