"""
Migration: Add multi_ma_crossoverV2 template (BTC MEDIAS - trend filter fixo).

Strategy from TradingView:
- EMA curta (18), SMA intermediária (20), SMA longa (35)
- Filtro de tendência: EMA > SMA longa (só compra em tendência de alta)
- Entrada: (crossover(EMA, SMA longa) OU crossover(EMA, SMA inter)) E tendência alta
- Saída: EMA < SMA longa (crossunder)
- Stop Loss: 4.2%
"""

import sqlite3
import json
from pathlib import Path


def _get_db_path():
    try:
        from app.database import DB_PATH
        return str(DB_PATH)
    except Exception:
        return str(Path(__file__).resolve().parent.parent.parent / "backtest.db")


def add_multi_ma_crossover_v2():
    db_path = _get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    template_name = "multi_ma_crossoverV2"
    cursor.execute("SELECT id, optimization_schema FROM combo_templates WHERE name = ?", (template_name,))
    row = cursor.fetchone()
    if row:
        # Update existing template to nested optimization_schema (parameters + correlated_groups) so Edit page shows ranges
        existing_schema = json.loads(row[1]) if row[1] else {}
        if not existing_schema.get("parameters"):
            optimization_schema = {
                "parameters": {
                    "ema_short": {"min": 10, "max": 28, "step": 1, "default": 18},
                    "sma_medium": {"min": 14, "max": 30, "step": 1, "default": 20},
                    "sma_long": {"min": 28, "max": 50, "step": 1, "default": 35},
                    "stop_loss": {"min": 0.02, "max": 0.08, "step": 0.005, "default": 0.042},
                },
                "correlated_groups": [["ema_short", "sma_medium", "sma_long", "stop_loss"]],
            }
            cursor.execute(
                "UPDATE combo_templates SET optimization_schema = ? WHERE name = ?",
                (json.dumps(optimization_schema), template_name),
            )
            conn.commit()
            print(f"[OK] Template '{template_name}' updated with nested optimization_schema (parameters + correlated_groups).")
        conn.close()
        return

    template_data = {
        "indicators": [
            {"type": "ema", "alias": "short", "params": {"length": 18}},
            {"type": "sma", "alias": "medium", "params": {"length": 20}},
            {"type": "sma", "alias": "long", "params": {"length": 35}},
        ],
        "entry_logic": "(short > long) & (crossover(short, long) | crossover(short, medium))",
        "exit_logic": "crossunder(short, long)",
        "stop_loss": 0.042,
    }

    # Same structure as multi_ma_crossover: parameters + correlated_groups for grid (backend and frontend expect .parameters for Edit page)
    optimization_schema = {
        "parameters": {
            "ema_short": {"min": 10, "max": 28, "step": 1, "default": 18},
            "sma_medium": {"min": 14, "max": 30, "step": 1, "default": 20},
            "sma_long": {"min": 28, "max": 50, "step": 1, "default": 35},
            "stop_loss": {"min": 0.02, "max": 0.08, "step": 0.005, "default": 0.042},
        },
        "correlated_groups": [
            ["ema_short", "sma_medium", "sma_long", "stop_loss"]
        ],
    }

    description = (
        "BTC MEDIAS (FINAL - trend filter fixo). "
        "EMA curta + SMA inter + SMA longa. Entrada: (crossover short/long ou short/medium) e tendência alta (short > long). Saída: crossunder(short, long). Stop % configurável."
    )

    cursor.execute("""
        INSERT INTO combo_templates (name, description, is_prebuilt, is_example, template_data, optimization_schema)
        VALUES (?, ?, 1, 0, ?, ?)
    """, (
        template_name,
        description,
        json.dumps(template_data),
        json.dumps(optimization_schema),
    ))

    conn.commit()
    conn.close()
    print(f"[OK] Template '{template_name}' added successfully.")


if __name__ == "__main__":
    add_multi_ma_crossover_v2()
