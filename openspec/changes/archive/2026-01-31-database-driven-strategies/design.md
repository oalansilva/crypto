# Design: Database-Driven Strategy Architecture

## Current Architecture

```
┌─────────────────────────────────────────┐
│         Frontend (React)                │
│  - ComboSelectPage                      │
│  - ComboConfigurePage                   │
│  - ComboOptimizePage                    │
└────────────┬────────────────────────────┘
             │ HTTP API
             ▼
┌─────────────────────────────────────────┐
│      Backend (FastAPI)                  │
│  ┌──────────────────────────────────┐   │
│  │   combo_routes.py                │   │
│  └──────────┬───────────────────────┘   │
│             │                            │
│             ▼                            │
│  ┌──────────────────────────────────┐   │
│  │   ComboService                   │   │
│  │  ┌────────────────────────────┐  │   │
│  │  │ PREBUILT_TEMPLATES (dict)  │  │   │ ❌ Hard-coded
│  │  │  - MultiMaCrossoverCombo   │  │   │
│  │  │  - EmaRsiCombo             │  │   │
│  │  │  - EmaMacdVolumeCombo      │  │   │
│  │  │  - BollingerRsiAdxCombo    │  │   │
│  │  │  - VolumeAtrBreakoutCombo  │  │   │
│  │  │  - EmaRsiFibonacciCombo    │  │   │
│  │  └────────────────────────────┘  │   │
│  └──────────┬───────────────────────┘   │
│             │                            │
│             ▼                            │
│  ┌──────────────────────────────────┐   │
│  │   Database (SQLite)              │   │
│  │  combo_templates                 │   │
│  │  - Example templates only        │   │ ⚠️ Partial
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

**Problems:**
- Dual source of truth (Python classes + Database)
- Inconsistent optimization schema access
- Requires code deployment for new strategies

---

## Proposed Architecture

```
┌─────────────────────────────────────────┐
│         Frontend (React)                │
│  - ComboSelectPage                      │
│  - ComboConfigurePage                   │
│  - ComboOptimizePage                    │
└────────────┬────────────────────────────┘
             │ HTTP API
             ▼
┌─────────────────────────────────────────┐
│      Backend (FastAPI)                  │
│  ┌──────────────────────────────────┐   │
│  │   combo_routes.py                │   │
│  └──────────┬───────────────────────┘   │
│             │                            │
│             ▼                            │
│  ┌──────────────────────────────────┐   │
│  │   ComboService                   │   │
│  │  - No hard-coded templates       │   │ ✅ Clean
│  │  - Reads all from database       │   │
│  └──────────┬───────────────────────┘   │
│             │                            │
│             ▼                            │
│  ┌──────────────────────────────────┐   │
│  │   Database (SQLite)              │   │
│  │  combo_templates                 │   │
│  │  ┌────────────────────────────┐  │   │
│  │  │ id, name, description      │  │   │
│  │  │ is_prebuilt, is_example    │  │   │
│  │  │ template_data (JSON)       │  │   │
│  │  │ optimization_schema (JSON) │  │   │ ✅ New
│  │  └────────────────────────────┘  │   │
│  │  - All templates (pre-built +   │   │
│  │    examples + custom)            │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

**Benefits:**
- Single source of truth (Database only)
- Consistent schema access for all templates
- No code deployment needed

---

## Database Schema

### Enhanced `combo_templates` Table

```sql
CREATE TABLE combo_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    is_example BOOLEAN DEFAULT 0,
    is_prebuilt BOOLEAN DEFAULT 0,
    template_data JSON NOT NULL,
    optimization_schema JSON,  -- NEW COLUMN
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### `template_data` Structure (Existing)

```json
{
  "indicators": [
    {
      "type": "ema",
      "alias": "fast",
      "params": {"length": 9}
    },
    {
      "type": "rsi",
      "params": {"length": 14}
    }
  ],
  "entry_logic": "(close > fast) & (RSI_14 > 30) & (RSI_14 < 50)",
  "exit_logic": "(RSI_14 > 70) | (close < fast)",
  "stop_loss": 0.015
}
```

### `optimization_schema` Structure (NEW)

```json
{
  "ema_fast": {
    "min": 5,
    "max": 20,
    "step": 1,
    "default": 9,
    "description": "Fast EMA period"
  },
  "ema_slow": {
    "min": 15,
    "max": 50,
    "step": 1,
    "default": 21,
    "description": "Slow EMA period"
  },
  "rsi_period": {
    "min": 7,
    "max": 21,
    "step": 1,
    "default": 14,
    "description": "RSI calculation period"
  },
  "rsi_min": {
    "min": 20,
    "max": 40,
    "step": 2,
    "default": 30,
    "description": "Minimum RSI for entry"
  },
  "rsi_max": {
    "min": 60,
    "max": 80,
    "step": 2,
    "default": 50,
    "description": "Maximum RSI for entry"
  },
  "stop_loss": {
    "min": 0.01,
    "max": 0.05,
    "step": 0.005,
    "default": 0.015,
    "description": "Stop loss percentage"
  }
}
```

---

## Service Layer Changes

### Before: `ComboService`

```python
class ComboService:
    PREBUILT_TEMPLATES = {
        "ema_rsi": EmaRsiCombo,
        "multi_ma_crossover": MultiMaCrossoverCombo,
        # ... 4 more hard-coded classes
    }
    
    def get_template_metadata(self, template_name: str):
        # Check Python classes first
        if template_name in self.PREBUILT_TEMPLATES:
            cls = self.PREBUILT_TEMPLATES[template_name]
            if hasattr(cls, 'get_optimization_schema'):
                schema = cls.get_optimization_schema()
            # ...
        
        # Then check database
        # ...
```

### After: `ComboService`

```python
class ComboService:
    # No PREBUILT_TEMPLATES dictionary
    
    def get_template_metadata(self, template_name: str):
        # Query database only
        cursor.execute("""
            SELECT template_data, optimization_schema
            FROM combo_templates
            WHERE name = ?
        """, (template_name,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        template_data = json.loads(row[0])
        optimization_schema = json.loads(row[1]) if row[1] else None
        
        return {
            "template_data": template_data,
            "optimization_schema": optimization_schema
        }
```

---

## Migration Strategy

### Step 1: Add Column (Non-Breaking)

```python
# Migration: add_optimization_schema.py
cursor.execute("""
    ALTER TABLE combo_templates 
    ADD COLUMN optimization_schema JSON
""")
```

### Step 2: Seed Pre-built Strategies

```python
# Migration: seed_prebuilt_strategies.py
prebuilt_strategies = [
    {
        "name": "ema_rsi",
        "description": "EMA + RSI combo for trend following",
        "is_prebuilt": 1,
        "template_data": {...},
        "optimization_schema": {...}
    },
    # ... 5 more
]

for strategy in prebuilt_strategies:
    cursor.execute("""
        INSERT INTO combo_templates 
        (name, description, is_prebuilt, template_data, optimization_schema)
        VALUES (?, ?, ?, ?, ?)
    """, (...))
```

### Step 3: Update Service (Breaking)

Remove `PREBUILT_TEMPLATES` and update all methods to query database.

### Step 4: Delete Python Classes

Remove 6 strategy class files.

---

## Optimization Schema Mapping

### Current: Python Method

```python
class EmaRsiCombo:
    @classmethod
    def get_optimization_schema(cls):
        return {
            "ema_fast": {"min": 5, "max": 20, "step": 1, "default": 9},
            "rsi_period": {"min": 7, "max": 21, "step": 1, "default": 14},
            # ...
        }
```

### Proposed: Database JSON

```json
{
  "ema_fast": {
    "min": 5,
    "max": 20,
    "step": 1,
    "default": 9
  },
  "rsi_period": {
    "min": 7,
    "max": 21,
    "step": 1,
    "default": 14
  }
}
```

**Access Pattern:**

```python
# Before
if hasattr(cls, 'get_optimization_schema'):
    schema = cls.get_optimization_schema()

# After
cursor.execute("SELECT optimization_schema FROM combo_templates WHERE name = ?", (name,))
schema = json.loads(cursor.fetchone()[0])
```

---

## Rollback Strategy

If migration fails:

1. **Database**: Restore from backup
2. **Code**: `git revert` to previous commit
3. **Service**: Re-add `PREBUILT_TEMPLATES` dictionary

**Backup Command:**
```bash
cp backend/data/crypto_backtest.db backend/data/crypto_backtest.db.backup
```

---

## Performance Considerations

### Database Queries

- **Before**: 0 queries for pre-built templates (in-memory)
- **After**: 1 query per template metadata request

**Mitigation**: Add caching layer in `ComboService`

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_template_metadata(self, template_name: str):
    # Query database
    # ...
```

### Expected Impact

- **Negligible**: Template metadata is fetched once per backtest/optimization
- **Benefit**: Reduced code complexity outweighs minimal query overhead

---

## Testing Strategy

### Unit Tests

```python
def test_get_template_from_database():
    """Test loading pre-built template from database."""
    service = ComboService()
    metadata = service.get_template_metadata("ema_rsi")
    
    assert metadata is not None
    assert "optimization_schema" in metadata
    assert metadata["optimization_schema"]["ema_fast"]["min"] == 5

def test_optimization_schema_from_database():
    """Test optimization uses DB schema."""
    optimizer = ComboOptimizer()
    stages = optimizer.generate_stages("ema_rsi", {...})
    
    assert len(stages) > 0
    assert stages[0]["parameter"] == "ema_fast"
```

### Integration Tests

```python
def test_end_to_end_backtest_with_db_template():
    """Test complete backtest flow with DB template."""
    response = client.post("/api/combos/backtest", json={
        "template_name": "ema_rsi",
        "symbol": "BTC/USDT",
        "timeframe": "1h",
        "start_date": "2024-01-01",
        "end_date": "2024-01-31"
    })
    
    assert response.status_code == 200
    assert response.json()["metrics"]["total_trades"] > 0
```

---

## Future Enhancements

This architecture enables:

1. **Visual Strategy Builder**: Drag-and-drop UI to create strategies
2. **Strategy Marketplace**: Share/import strategies as JSON
3. **Version Control**: Track strategy changes over time
4. **A/B Testing**: Compare multiple strategy versions
5. **Multi-tenancy**: User-specific strategy libraries

---

## Conclusion

Migrating to a database-driven architecture:
- ✅ Simplifies codebase (removes 6 Python classes)
- ✅ Enables runtime configuration (no code deployment)
- ✅ Provides consistent experience (all templates in DB)
- ✅ Unlocks future features (visual builder, marketplace)

**Trade-off**: Minimal performance overhead (1 DB query per template) for significant architectural benefits.
