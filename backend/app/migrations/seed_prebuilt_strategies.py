"""
Migration: Seed pre-built combo strategies into database.

Converts the 6 hard-coded Python strategy classes into database records
with complete template_data and optimization_schema.
"""

import sqlite3
import json
from pathlib import Path


def seed_prebuilt_strategies(db_path: str = None):
    """Seed database with pre-built combo strategies. Uses same DB as backend (backend/backtest.db) when db_path is None."""
    
    if db_path is None:
        try:
            from app.database import DB_PATH
            db_path = str(DB_PATH)
        except Exception:
            project_root = Path(__file__).parent.parent.parent
            db_path = str(project_root / "backtest.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Define all 6 pre-built strategies
    strategies = [
        {
            "name": "multi_ma_crossover",
            "description": "Triple Moving Average Crossover Strategy - Classic trend following with three averages",
            "template_data": {
                "indicators": [
                    {"type": "sma", "alias": "short", "params": {"length": 9}},
                    {"type": "sma", "alias": "medium", "params": {"length": 21}},
                    {"type": "sma", "alias": "long", "params": {"length": 50}}
                ],
                "entry_logic": "crossover(short, medium) & (short > long)",
                "exit_logic": "crossunder(short, medium) | (short < long)",
                "stop_loss": 0.015
            },
            "optimization_schema": {
                "sma_short": {"min": 3, "max": 20, "step": 1, "default": 9},
                "sma_medium": {"min": 10, "max": 40, "step": 1, "default": 21},
                "sma_long": {"min": 20, "max": 100, "step": 1, "default": 50},
                "stop_loss": {"min": 0.005, "max": 0.13, "step": 0.002, "default": 0.015}
            }
        },
        {
            "name": "ema_rsi",
            "description": "EMA + RSI combo for trend following with momentum confirmation",
            "template_data": {
                "indicators": [
                    {"type": "ema", "alias": "fast", "params": {"length": 9}},
                    {"type": "ema", "alias": "slow", "params": {"length": 21}},
                    {"type": "rsi", "params": {"length": 14}}
                ],
                "entry_logic": "(close > fast) & (close > slow) & (RSI_14 > 30) & (RSI_14 < 50)",
                "exit_logic": "(RSI_14 > 70) | (close < fast)",
                "stop_loss": 0.015
            },
            "optimization_schema": {
                "ema_fast": {"min": 5, "max": 20, "step": 1, "default": 9},
                "ema_slow": {"min": 15, "max": 50, "step": 1, "default": 21},
                "rsi_period": {"min": 7, "max": 21, "step": 1, "default": 14},
                "rsi_min": {"min": 20, "max": 40, "step": 2, "default": 30},
                "rsi_max": {"min": 60, "max": 80, "step": 2, "default": 50},
                "stop_loss": {"min": 0.01, "max": 0.05, "step": 0.005, "default": 0.015}
            }
        },
        {
            "name": "ema_macd_volume",
            "description": "EMA + MACD + Volume combo for trend confirmation with volume filter",
            "template_data": {
                "indicators": [
                    {"type": "ema", "params": {"length": 20}},
                    {"type": "macd", "params": {"fast": 12, "slow": 26, "signal": 9}},
                    {"type": "volume_sma", "alias": "vol_avg", "params": {"length": 20}}
                ],
                "entry_logic": "(close > EMA_20) & (MACD_macd > MACD_signal) & (volume > vol_avg)",
                "exit_logic": "(MACD_macd < MACD_signal) | (close < EMA_20)",
                "stop_loss": 0.02
            },
            "optimization_schema": {
                "ema_length": {"min": 10, "max": 50, "step": 5, "default": 20},
                "macd_fast": {"min": 8, "max": 15, "step": 1, "default": 12},
                "macd_slow": {"min": 20, "max": 30, "step": 2, "default": 26},
                "macd_signal": {"min": 5, "max": 12, "step": 1, "default": 9},
                "volume_length": {"min": 10, "max": 30, "step": 5, "default": 20},
                "stop_loss": {"min": 0.01, "max": 0.03, "step": 0.005, "default": 0.02}
            }
        },
        {
            "name": "bollinger_rsi_adx",
            "description": "Bollinger Bands + RSI + ADX for mean reversion with trend filter",
            "template_data": {
                "indicators": [
                    {"type": "bbands", "alias": "bb", "params": {"length": 20, "std": 2}},
                    {"type": "rsi", "params": {"length": 14}},
                    {"type": "adx", "params": {"length": 14}}
                ],
                "entry_logic": "(close < bb_lower) & (RSI_14 < 30) & (ADX_14 > 20)",
                "exit_logic": "(close > bb_middle) | (RSI_14 > 70)",
                "stop_loss": 0.02
            },
            "optimization_schema": {
                "bb_length": {"min": 15, "max": 30, "step": 5, "default": 20},
                "bb_std": {"min": 1.5, "max": 2.5, "step": 0.5, "default": 2.0},
                "rsi_length": {"min": 10, "max": 20, "step": 2, "default": 14},
                "adx_length": {"min": 10, "max": 20, "step": 2, "default": 14},
                "adx_threshold": {"min": 15, "max": 30, "step": 5, "default": 20},
                "stop_loss": {"min": 0.01, "max": 0.03, "step": 0.005, "default": 0.02}
            }
        },
        {
            "name": "volume_atr_breakout",
            "description": "Volume + ATR Breakout strategy for volatility-based entries",
            "template_data": {
                "indicators": [
                    {"type": "volume_sma", "alias": "vol_avg", "params": {"length": 20}},
                    {"type": "atr", "params": {"length": 14}}
                ],
                "entry_logic": "(volume > vol_avg * 1.5) & (close > close.shift(1) + ATR_14 * 0.5)",
                "exit_logic": "close < (close.shift(1) - ATR_14 * 0.3)",
                "stop_loss": 0.025
            },
            "optimization_schema": {
                "volume_length": {"min": 10, "max": 30, "step": 5, "default": 20},
                "volume_multiplier": {"min": 1.2, "max": 2.0, "step": 0.1, "default": 1.5},
                "atr_length": {"min": 10, "max": 20, "step": 2, "default": 14},
                "atr_entry_mult": {"min": 0.3, "max": 1.0, "step": 0.1, "default": 0.5},
                "atr_exit_mult": {"min": 0.2, "max": 0.5, "step": 0.1, "default": 0.3},
                "stop_loss": {"min": 0.015, "max": 0.04, "step": 0.005, "default": 0.025}
            }
        },
        {
            "name": "ema_rsi_fibonacci",
            "description": "EMA + RSI + Fibonacci for trend following with retracement entries",
            "template_data": {
                "indicators": [
                    {"type": "ema", "alias": "trend", "params": {"length": 200}},
                    {"type": "rsi", "params": {"length": 14}}
                ],
                "entry_logic": "(close > trend) & (RSI_14 > 40) & (RSI_14 < 60)",
                "exit_logic": "(RSI_14 > 70) | (close < trend)",
                "stop_loss": 0.02
            },
            "optimization_schema": {
                "ema_length": {"min": 100, "max": 300, "step": 50, "default": 200},
                "rsi_length": {"min": 10, "max": 20, "step": 2, "default": 14},
                "fib_lookback": {"min": 30, "max": 100, "step": 10, "default": 50},
                "fib_tolerance": {"min": 0.01, "max": 0.05, "step": 0.01, "default": 0.02},
                "stop_loss": {"min": 0.01, "max": 0.03, "step": 0.005, "default": 0.02}
            }
        },
        {
            "name": "short_ema200_pullback",
            "description": "BTC Short Swing – EMA200 Pullback (Stop %). Short-only: bearish trend (close < EMA200), pullback to EMA21/50 (tolerance 1%), RSI 45–70, rejection candle (shooting star / bearish engulfing / strong bearish). Exit: stop % or trend/RSI reversal.",
            "template_data": {
                "indicators": [
                    {"type": "ema", "alias": "ema21", "params": {"length": 21}},
                    {"type": "ema", "alias": "ema50", "params": {"length": 50}},
                    {"type": "ema", "alias": "ema200", "params": {"length": 200}},
                    {"type": "rsi", "params": {"length": 14}}
                ],
                "entry_logic": (
                    "(close < ema200) "
                    "& ( ((close - ema21).abs() / ema21 * 100 <= 1.0) | ((high >= ema21) & (low <= ema21)) "
                    "| ((close - ema50).abs() / ema50 * 100 <= 1.0) | ((high >= ema50) & (low <= ema50)) ) "
                    "& (RSI_14 >= 45) & (RSI_14 <= 70) "
                    "& ((high - low) > 0) "
                    "& ( "
                    "  ( ((high - (open + close + (open - close).abs()) / 2) >= (close - open).abs() * 2) & (close < open) & (close < (low + (high - low) * 0.5)) ) "
                    "  | ( (close < open) & (open >= close.shift(1)) & (close <= open.shift(1)) ) "
                    "  | ( (close < open) & ((open - close) >= (high - low) * 0.5) ) "
                    ")"
                ),
                "exit_logic": "(close > ema200) | (RSI_14 < 45)",
                "stop_loss": 0.06
            },
            "optimization_schema": {
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
        }
    ]
    
    # Insert or update each strategy
    inserted_count = 0
    updated_count = 0
    for strategy in strategies:
        cursor.execute("SELECT id FROM combo_templates WHERE name = ?", (strategy["name"],))
        existing = cursor.fetchone()
        if existing:
            # Update prebuilt template so definition changes (e.g. short_ema200_pullback) are applied
            if strategy.get("is_prebuilt_update", False) or strategy["name"] == "short_ema200_pullback":
                cursor.execute("""
                    UPDATE combo_templates SET description = ?, template_data = ?, optimization_schema = ?
                    WHERE name = ?
                """, (
                    strategy["description"],
                    json.dumps(strategy["template_data"]),
                    json.dumps(strategy["optimization_schema"]),
                    strategy["name"],
                ))
                updated_count += 1
                print(f"[UPDATE] Strategy '{strategy['name']}' updated.")
            else:
                print(f"[SKIP] Strategy '{strategy['name']}' already exists, skipping...")
            continue

        cursor.execute("""
            INSERT INTO combo_templates 
            (name, description, is_prebuilt, is_example, template_data, optimization_schema)
            VALUES (?, ?, 1, 0, ?, ?)
        """, (
            strategy["name"],
            strategy["description"],
            json.dumps(strategy["template_data"]),
            json.dumps(strategy["optimization_schema"])
        ))
        inserted_count += 1
        print(f"[OK] Inserted strategy: {strategy['name']}")
    
    conn.commit()
    conn.close()
    
    print(f"\n[OK] Seeded {inserted_count} new, updated {updated_count} pre-built strategies")


def run_migration():
    """Run the migration."""
    print("Seeding pre-built combo strategies...")
    seed_prebuilt_strategies()
    print("[OK] Migration completed successfully!")


if __name__ == "__main__":
    run_migration()
