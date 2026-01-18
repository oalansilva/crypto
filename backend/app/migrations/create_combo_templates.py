"""
Database migration script for combo_templates table.

Creates the combo_templates table and seeds it with pre-built and example templates.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime


def create_combo_templates_table(db_path: str = None):
    """Create combo_templates table if it doesn't exist."""
    
    if db_path is None:
        from pathlib import Path
        project_root = Path(__file__).parent.parent.parent
        db_path = str(project_root / "data" / "crypto_backtest.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS combo_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            is_example BOOLEAN DEFAULT 0,
            is_prebuilt BOOLEAN DEFAULT 0,
            template_data JSON NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    
    print("✅ Table combo_templates created successfully")


def seed_example_templates(db_path: str = None):
    """Seed database with 4 example templates."""
    
    if db_path is None:
        from pathlib import Path
        project_root = Path(__file__).parent.parent.parent
        db_path = str(project_root / "data" / "crypto_backtest.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    examples = [
        {
            "name": "Example: CRUZAMENTOMEDIAS",
            "description": "EMA 3 + SMA 37 + SMA 32 - Existing strategy as combo",
            "template_data": {
                "indicators": [
                    {"type": "ema", "alias": "fast", "params": {"length": 3}, "optimization_range": {"min": 3, "max": 15, "step": 1}},
                    {"type": "sma", "alias": "long", "params": {"length": 37}, "optimization_range": {"min": 30, "max": 50, "step": 1}},
                    {"type": "sma", "alias": "inter", "params": {"length": 32}, "optimization_range": {"min": 20, "max": 40, "step": 1}}
                ],
                "entry_logic": "(fast > long) and (crossover(fast, long) or crossover(fast, inter))",
                "exit_logic": "crossunder(fast, inter)",
                "stop_loss": {"default": 0.015, "optimization_range": {"min": 0.005, "max": 0.02, "step": 0.005}}
            }
        },
        {
            "name": "Example: Scalping EMA 5/13",
            "description": "Fast EMAs for scalping in short timeframes",
            "template_data": {
                "indicators": [
                    {"type": "ema", "alias": "fast", "params": {"length": 5}, "optimization_range": {"min": 3, "max": 10, "step": 1}},
                    {"type": "ema", "alias": "slow", "params": {"length": 13}, "optimization_range": {"min": 10, "max": 20, "step": 1}}
                ],
                "entry_logic": "crossover(fast, slow)",
                "exit_logic": "crossunder(fast, slow)",
                "stop_loss": {"default": 0.01, "optimization_range": {"min": 0.005, "max": 0.015, "step": 0.0025}}
            }
        },
        {
            "name": "Example: Swing RSI Divergence",
            "description": "RSI divergence detection for swing trading",
            "template_data": {
                "indicators": [
                    {"type": "rsi", "params": {"length": 14}, "optimization_range": {"min": 10, "max": 20, "step": 1}}
                ],
                "entry_logic": "(RSI_14 < 30) and (close < close.shift(5))",
                "exit_logic": "(RSI_14 > 70)",
                "stop_loss": {"default": 0.02, "optimization_range": {"min": 0.01, "max": 0.03, "step": 0.005}}
            }
        },
        {
            "name": "Example: Breakout with Volume",
            "description": "Price breakout confirmed by volume spike",
            "template_data": {
                "indicators": [
                    {"type": "volume_sma", "alias": "vol_avg", "params": {"length": 20}, "optimization_range": {"min": 10, "max": 30, "step": 5}}
                ],
                "entry_logic": "(volume > vol_avg * 2) and (close > high.shift(1))",
                "exit_logic": "(close < close.shift(1).rolling(5).max())",
                "stop_loss": {"default": 0.015, "optimization_range": {"min": 0.01, "max": 0.025, "step": 0.005}}
            }
        }
    ]
    
    for example in examples:
        cursor.execute("""
            INSERT INTO combo_templates (name, description, is_example, is_prebuilt, template_data)
            VALUES (?, ?, 1, 0, ?)
        """, (
            example["name"],
            example["description"],
            json.dumps(example["template_data"])
        ))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Seeded {len(examples)} example templates")


def run_migration():
    """Run the complete migration."""
    print("🔄 Running combo_templates migration...")
    
    # Ensure data directory exists
    Path("backend/data").mkdir(parents=True, exist_ok=True)
    
    # Create table
    create_combo_templates_table()
    
    # Seed examples
    seed_example_templates()
    
    print("✅ Migration completed successfully!")


if __name__ == "__main__":
    run_migration()
