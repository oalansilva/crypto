"""
Migration: Set short_ema200_pullback optimization_schema with correlated_groups
so Round 1 uses one joint grid (like multi_ma_crossover) instead of 5 sequential stages.
Uses coarse step in R1 to keep combinations manageable (product of ~5×4×3×3×2).
"""

import sqlite3
import json
from pathlib import Path


def _get_db_path(db_path: str = None):
    if db_path:
        return db_path
    try:
        from app.database import DB_PATH
        return str(DB_PATH)
    except Exception:
        return str(Path(__file__).resolve().parent.parent.parent / "backtest.db")


def apply_short_ema200_correlated_groups(db_path: str = None):
    """Update short_ema200_pullback optimization_schema to parameters + correlated_groups."""
    path = _get_db_path(db_path)
    conn = sqlite3.connect(path)
    cursor = conn.cursor()

    optimization_schema = {
        "parameters": {
            "ema_ema21": {"min": 14, "max": 30, "step": 1, "default": 21},
            "ema_ema50": {"min": 40, "max": 70, "step": 2, "default": 50},
            "ema_ema200": {"min": 150, "max": 250, "step": 10, "default": 200},
            "rsi_length": {"min": 10, "max": 18, "step": 1, "default": 14},
            "stop_loss": {"min": 0.03, "max": 0.10, "step": 0.01, "default": 0.06},
        },
        "correlated_groups": [
            ["ema_ema21", "ema_ema50", "ema_ema200", "rsi_length", "stop_loss"]
        ],
    }

    cursor.execute("""
        UPDATE combo_templates
        SET optimization_schema = ?
        WHERE name = 'short_ema200_pullback'
    """, (json.dumps(optimization_schema),))

    if cursor.rowcount > 0:
        print("[OK] short_ema200_pullback: optimization_schema updated with correlated_groups (1 joint grid in R1)")
    else:
        print("[WARN] Template 'short_ema200_pullback' not found in database")

    conn.commit()
    conn.close()
    return cursor.rowcount


if __name__ == "__main__":
    apply_short_ema200_correlated_groups()
    print("\n[OK] Migration completed.")
