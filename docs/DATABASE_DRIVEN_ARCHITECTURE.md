# Database-Driven Combo Strategies

## Architecture Overview

All combo strategies are now **100% database-driven**. No hard-coded Python classes required!

### Key Benefits

- ✅ **No Code Deployment**: Create/modify strategies without deploying code
- ✅ **Runtime Configuration**: Changes take effect immediately
- ✅ **Easy Sharing**: Export/import strategies as JSON
- ✅ **Version Control**: Track changes via database backups
- ✅ **Consistent Experience**: All templates (pre-built, examples, custom) work the same way

### How It Works

```
┌─────────────────────────────────────────┐
│         Frontend (React)                │
│  - Select Template                      │
│  - Configure Parameters                 │
│  - Run Backtest/Optimization            │
└────────────┬────────────────────────────┘
             │ HTTP API
             ▼
┌─────────────────────────────────────────┐
│      Backend (FastAPI)                  │
│  ┌──────────────────────────────────┐   │
│  │   ComboService                   │   │
│  │  - Loads all from database       │   │
│  │  - No hard-coded classes         │   │
│  └──────────┬───────────────────────┘   │
│             │                            │
│             ▼                            │
│  ┌──────────────────────────────────┐   │
│  │   Database (SQLite)              │   │
│  │  combo_templates                 │   │
│  │  ┌────────────────────────────┐  │   │
│  │  │ template_data (JSON)       │  │   │
│  │  │ optimization_schema (JSON) │  │   │
│  │  └────────────────────────────┘  │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## Quick Start

### 1. Select a Template

6 pre-built strategies available:
- **Multi-MA Crossover**: Triple moving average trend following
- **EMA + RSI**: Trend with momentum confirmation
- **EMA + MACD + Volume**: Multi-indicator confirmation
- **Bollinger + RSI + ADX**: Mean reversion with trend filter
- **Volume + ATR Breakout**: Volatility-based entries
- **EMA + RSI + Fibonacci**: Trend with retracement levels

### 2. Backtest & Optimize

```bash
# Via UI
http://localhost:5173/combo/select

# Via API
curl -X POST http://localhost:8000/api/combos/backtest \
  -H "Content-Type: application/json" \
  -d '{
    "template_name": "ema_rsi",
    "symbol": "BTC/USDT",
    "timeframe": "1h",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }'
```

### 3. Create Custom Strategies

```bash
curl -X POST http://localhost:8000/api/combos/templates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_strategy",
    "description": "Custom EMA + MACD",
    "indicators": [
      {"type": "ema", "alias": "trend", "params": {"length": 50}},
      {"type": "macd", "params": {"fast": 12, "slow": 26, "signal": 9}}
    ],
    "entry_logic": "(close > trend) & (MACD_macd > MACD_signal)",
    "exit_logic": "(MACD_macd < MACD_signal)",
    "optimization_schema": {
      "ema_length": {"min": 30, "max": 70, "step": 5, "default": 50}
    }
  }'
```

## Database Schema

```sql
CREATE TABLE combo_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    is_example BOOLEAN DEFAULT 0,
    is_prebuilt BOOLEAN DEFAULT 1,
    template_data JSON NOT NULL,
    optimization_schema JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### template_data Format

```json
{
  "indicators": [
    {"type": "ema", "alias": "fast", "params": {"length": 9}},
    {"type": "rsi", "params": {"length": 14}}
  ],
  "entry_logic": "(close > fast) & (RSI_14 > 30) & (RSI_14 < 50)",
  "exit_logic": "(RSI_14 > 70) | (close < fast)",
  "stop_loss": 0.015
}
```

### optimization_schema Format

```json
{
  "ema_fast": {"min": 5, "max": 20, "step": 1, "default": 9},
  "rsi_period": {"min": 7, "max": 21, "step": 1, "default": 14}
}
```

## Migration from Old Architecture

If upgrading from hard-coded Python classes:

```bash
# 1. Backup database
cp backend/data/crypto_backtest.db backend/data/crypto_backtest.db.backup

# 2. Run migrations
python backend/app/migrations/add_optimization_schema.py
python backend/app/migrations/seed_prebuilt_strategies.py

# 3. Verify
python test_database_driven.py

# 4. Restart services
.\stop.ps1
.\start.ps1
```

See [MIGRATION_DATABASE_DRIVEN.md](./docs/MIGRATION_DATABASE_DRIVEN.md) for detailed migration guide.

## Documentation

- **[User Guide](./docs/COMBO_STRATEGIES_USER_GUIDE.md)**: Complete workflow and examples
- **[Templates Reference](./docs/COMBO_TEMPLATES_REFERENCE.md)**: All 6 pre-built templates documented
- **[API Documentation](./docs/COMBO_API_DOCUMENTATION.md)**: Full API reference
- **[Custom Examples](./docs/CUSTOM_COMBO_EXAMPLES.md)**: 6 practical custom strategy examples
- **[Migration Guide](./docs/MIGRATION_DATABASE_DRIVEN.md)**: Upgrade from old architecture

## Features

### ✅ Implemented

- 6 pre-built combo strategies (database-driven)
- 4 example templates for learning
- Custom template creation via API
- Parameter optimization (sequential approach)
- Chart visualization with indicators
- Backtest with comprehensive metrics
- Database-driven optimization schemas
- Runtime strategy configuration

### 🚧 Planned

- Visual combo builder UI
- Strategy marketplace/sharing
- Template export/import
- A/B testing framework
- Multi-tenancy support

## Technical Details

### Service Layer

```python
from app.services.combo_service import ComboService

# Load all templates from database
service = ComboService()
templates = service.list_templates()

# Create strategy instance
strategy = service.create_strategy('ema_rsi')

# With custom parameters
strategy = service.create_strategy(
    'ema_rsi',
    parameters={'ema_fast': 10, 'rsi_period': 12}
)
```

### Optimization

```python
from app.services.combo_optimizer import ComboOptimizer

optimizer = ComboOptimizer()

# Reads optimization_schema from database
result = optimizer.run_optimization(
    template_name='ema_rsi',
    symbol='BTC/USDT',
    timeframe='1h',
    start_date='2024-01-01',
    end_date='2024-06-30'
)

print(result['best_parameters'])
print(result['best_metrics'])
```

## Testing

```bash
# Unit tests
python -m pytest tests/test_combo_unit.py -v

# Integration tests
python -m pytest tests/test_combo_integration.py -v

# Database-driven tests
python test_database_driven.py
```

## Support

For issues or questions:
- Check [API docs](http://localhost:8000/docs)
- Review [User Guide](./docs/COMBO_STRATEGIES_USER_GUIDE.md)
- Consult [Migration Guide](./docs/MIGRATION_DATABASE_DRIVEN.md)

---

**Architecture**: 100% database-driven, zero hard-coded strategies! 🎉
