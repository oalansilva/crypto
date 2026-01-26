import sys
import os
import json
from datetime import datetime

# Add backent to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.database import engine, SessionLocal, Base
from app.models import ComboTemplate

def seed_templates():
    # 1. Create Tables if not exist (catches the new combo_templates)
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # 2. Check if templates exist
    count = db.query(ComboTemplate).count()
    if count > 0:
        print(f"Templates already exist ({count}). Skipping seed.")
        return

    print("Seeding templates...")
    
    # 3. Define Seed Data
    templates = [
        {
            "name": "RSI_EMA_Scalping",
            "description": "Simple RSI + EMA crossover strategy for scalping.",
            "is_prebuilt": True,
            "template_data": {
                "indicators": [
                    {"type": "RSI", "params": {"length": 14}, "alias": "rsi"},
                    {"type": "EMA", "params": {"length": 9}, "alias": "ema_fast"},
                    {"type": "EMA", "params": {"length": 21}, "alias": "ema_slow"}
                ],
                "entry_logic": "rsi < 30 and close > ema_fast",
                "exit_logic": "rsi > 70 or close < ema_slow",
                "stop_loss": 0.02
            },
            "optimization_schema": {
                "rsi_length": {"min": 5, "max": 25, "step": 1},
                "ema_fast_length": {"min": 5, "max": 15, "step": 1},
                "ema_slow_length": {"min": 15, "max": 50, "step": 5}
            }
        },
        {
            "name": "Bollinger_Breakout",
            "description": "Volatility breakout strategy using Bollinger Bands.",
            "is_prebuilt": True,
            "template_data": {
                "indicators": [
                    {"type": "BBANDS", "params": {"length": 20, "std": 2.0}, "alias": "bb"}
                ],
                "entry_logic": "close > bb.upper",
                "exit_logic": "close < bb.middle",
                "stop_loss": 0.03
            },
            "optimization_schema": {
                "bb_length": {"min": 10, "max": 50, "step": 5},
                "bb_std": {"min": 1.5, "max": 3.0, "step": 0.1}
            }
        },
        {
            "name": "MACD_Cross",
            "description": "Standard MACD Trend Following.",
            "is_prebuilt": True,
            "template_data": {
                "indicators": [
                    {"type": "MACD", "params": {"fast": 12, "slow": 26, "signal": 9}, "alias": "macd"}
                ],
                "entry_logic": "macd.macd > macd.signal",
                "exit_logic": "macd.macd < macd.signal",
                "stop_loss": 0.05
            },
            "optimization_schema": {
                "macd_fast": {"min": 8, "max": 20, "step": 2},
                "macd_slow": {"min": 20, "max": 40, "step": 2},
                "macd_signal": {"min": 5, "max": 15, "step": 1}
            }
        }
    ]
    
    for t in templates:
        db_obj = ComboTemplate(
            name=t['name'],
            description=t['description'],
            is_prebuilt=t['is_prebuilt'],
            template_data=t['template_data'],
            optimization_schema=t['optimization_schema']
        )
        db.add(db_obj)
    
    db.commit()
    print("✅ Seeded 3 templates successfully.")
    db.close()

if __name__ == "__main__":
    seed_templates()
