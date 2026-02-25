# Migration Guide: Database-Driven Combo Strategies

## Overview

This guide helps you migrate from the old hard-coded Python strategy classes to the new 100% database-driven architecture.

## What Changed

### Before (Old Architecture)
- Pre-built strategies were Python classes in `backend/app/strategies/combos/`
- Optimization schemas defined in `get_optimization_schema()` methods
- Required code deployment for new strategies
- Dual source of truth (Python + Database)

### After (New Architecture)
- All strategies stored in `combo_templates` database table
- Optimization schemas stored as JSON in `optimization_schema` column
- No code deployment needed
- Single source of truth (Database only)

## Breaking Changes

### 1. Deleted Python Files

The following files have been **removed**:
```
backend/app/strategies/combos/multi_ma_crossover.py
backend/app/strategies/combos/ema_rsi_combo.py
backend/app/strategies/combos/ema_macd_volume_combo.py
backend/app/strategies/combos/bollinger_rsi_adx_combo.py
backend/app/strategies/combos/volume_atr_breakout_combo.py
backend/app/strategies/combos/ema_rsi_fibonacci_combo.py
```

### 2. Updated Imports

**Old:**
```python
from app.strategies.combos import (
    EmaRsiCombo,
    MultiMaCrossoverCombo,
    # ... other classes
)
```

**New:**
```python
from app.services.combo_service import ComboService

service = ComboService()
strategy = service.create_strategy('ema_rsi')
```

### 3. API Changes

**No API changes** - All endpoints remain the same. The implementation is transparent to API users.

## Migration Steps

### Step 1: Backup Database

```bash
# Create backup before migration
cp backend/data/crypto_backtest.db backend/data/crypto_backtest.db.backup
```

### Step 2: Run Migrations

```bash
# Add optimization_schema column
python backend/app/migrations/add_optimization_schema.py

# Seed pre-built strategies
python backend/app/migrations/seed_prebuilt_strategies.py
```

Expected output:
```
🔄 Running optimization_schema migration...
✅ Added 'optimization_schema' column to combo_templates table
✅ Migration completed successfully!

🔄 Seeding pre-built combo strategies...
✅ Inserted strategy: multi_ma_crossover
✅ Inserted strategy: ema_rsi
✅ Inserted strategy: ema_macd_volume
✅ Inserted strategy: bollinger_rsi_adx
✅ Inserted strategy: volume_atr_breakout
✅ Inserted strategy: ema_rsi_fibonacci
✅ Seeded 6 pre-built strategies
✅ Migration completed successfully!
```

### Step 3: Verify Migration

```bash
# Run test script
python test_database_driven.py
```

Expected output:
```
============================================================
TEST 1: List Templates
============================================================
✅ Prebuilt: 6 templates
   - multi_ma_crossover
   - ema_rsi
   - ema_macd_volume
   - bollinger_rsi_adx
   - volume_atr_breakout
   - ema_rsi_fibonacci
✅ Examples: 4 templates
✅ Custom: 0 templates

============================================================
TEST 2: Get Template Metadata
============================================================
✅ Template: ema_rsi
✅ Description: EMA + RSI combo for trend following...
✅ Indicators: 3
✅ Has optimization_schema: True
✅ Schema parameters: ['ema_fast', 'ema_slow', 'rsi_period', ...]

============================================================
TEST 3: Create Strategy Instance
============================================================
✅ Strategy created: ComboStrategy
✅ Indicators: 3
✅ Entry logic: (close > fast) & (close > slow) & ...

============================================================
✅ ALL TESTS PASSED!
============================================================
```

### Step 4: Update Custom Code

If you have custom code that imports strategy classes:

**Before:**
```python
from app.strategies.combos import EmaRsiCombo

strategy = EmaRsiCombo(ema_fast=10, rsi_period=12)
```

**After:**
```python
from app.services.combo_service import ComboService

service = ComboService()
strategy = service.create_strategy(
    'ema_rsi',
    parameters={'ema_fast': 10, 'rsi_period': 12}
)
```

### Step 5: Restart Services

```bash
# Stop services
./stop.sh

# Start services
./start.sh
```

## Rollback Procedure

If you need to rollback:

### 1. Restore Database Backup

```bash
cp backend/data/crypto_backtest.db.backup backend/data/crypto_backtest.db
```

### 2. Revert Code Changes

```bash
git revert HEAD~2  # Revert last 2 commits
```

### 3. Restart Services

```bash
./stop.sh
./start.sh
```

## New Features

### 1. Runtime Strategy Creation

Create strategies without code deployment:

```bash
curl -X POST http://localhost:8000/api/combos/templates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_new_strategy",
    "description": "Custom strategy",
    "indicators": [...],
    "entry_logic": "...",
    "exit_logic": "...",
    "optimization_schema": {
      "param1": {"min": 5, "max": 20, "step": 1, "default": 10}
    }
  }'
```

### 2. Optimization Schema in Database

Define optimization ranges directly in the database:

```sql
UPDATE combo_templates
SET optimization_schema = '{
  "ema_fast": {"min": 5, "max": 20, "step": 1, "default": 9},
  "rsi_period": {"min": 7, "max": 21, "step": 1, "default": 14}
}'
WHERE name = 'ema_rsi';
```

### 3. Easy Strategy Sharing

Export/import strategies as JSON:

```bash
# Export
curl http://localhost:8000/api/combos/meta/ema_rsi > ema_rsi.json

# Import (modify and POST to /api/combos/templates)
```

## Database Schema

### combo_templates Table

```sql
CREATE TABLE combo_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    is_example BOOLEAN DEFAULT 0,
    is_prebuilt BOOLEAN DEFAULT 1,
    template_data JSON NOT NULL,
    optimization_schema JSON,  -- NEW COLUMN
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### optimization_schema Format

```json
{
  "parameter_name": {
    "min": 5,
    "max": 20,
    "step": 1,
    "default": 10,
    "description": "Optional description"
  }
}
```

## Troubleshooting

### "Template not found" Error

**Cause**: Migration not run or strategies not seeded.

**Solution**:
```bash
python backend/app/migrations/seed_prebuilt_strategies.py
```

### "ModuleNotFoundError: No module named 'app.strategies.combos.ema_rsi_combo'"

**Cause**: Code still trying to import deleted classes.

**Solution**: Update imports to use `ComboService`:
```python
from app.services.combo_service import ComboService
service = ComboService()
strategy = service.create_strategy('ema_rsi')
```

### Tests Failing

**Cause**: Tests importing deleted classes.

**Solution**: Update test imports:
```python
# Old
from app.strategies.combos import EmaRsiCombo

# New
from app.services.combo_service import ComboService
service = ComboService()
strategy = service.create_strategy('ema_rsi')
```

## FAQ

### Q: Can I still create custom strategies?

**A**: Yes! Use the API to create custom strategies stored in the database.

### Q: Will my existing custom templates work?

**A**: Yes, all existing templates in the database continue to work.

### Q: How do I add a new pre-built strategy?

**A**: Insert into database instead of creating a Python class:
```python
import sqlite3
import json

conn = sqlite3.connect('backend/data/crypto_backtest.db')
cursor = conn.cursor()

strategy = {
    "name": "my_strategy",
    "description": "...",
    "template_data": {...},
    "optimization_schema": {...}
}

cursor.execute("""
    INSERT INTO combo_templates 
    (name, description, is_prebuilt, template_data, optimization_schema)
    VALUES (?, ?, 1, ?, ?)
""", (
    strategy["name"],
    strategy["description"],
    json.dumps(strategy["template_data"]),
    json.dumps(strategy["optimization_schema"])
))

conn.commit()
conn.close()
```

### Q: What happens to optimization?

**A**: Optimization now reads schemas from the database `optimization_schema` column instead of Python class methods.

### Q: Is there a performance impact?

**A**: Minimal. Template metadata is queried once per backtest/optimization. Consider adding caching if needed.

## Support

For migration issues:
1. Check migration logs
2. Verify database backup exists
3. Review test results
4. Consult technical documentation

---

**Migration completed**: Your combo strategies are now 100% database-driven! 🎉
