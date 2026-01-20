# Adding Correlation Metadata for Hybrid Grid Optimization

## Overview

The **Hybrid Grid Optimization** system solves the "Local Maximum Trap" inherent in sequential optimization. By defining groups of **correlated parameters** (e.g., three moving averages that must respect `Fast < Inter < Slow`), the optimizer can perform a **Grid Search** on these groups jointly, finding the true global maximum within the search space.

## Architecture

The optimizer operates in a Hybrid Mode:
1.  **Grid Search Stages:** Correlated parameters are optimized jointly in a single stage (e.g., testing 336 combinations of 3 MAs).
2.  **Sequential Stages:** Independent parameters (e.g., RSI Length, Stop Loss) are optimized sequentially.
3.  **Single Round:** If *any* Grid Search stage is present, **Iterative Refinement is disabled** (`max_rounds=1`). Grid Search guarantees the best within-bounds result, making refinement redundant.

## Migration Guide

To enable Grid Search for a strategy template, you must add `correlated_groups` and range definitions to its `optimization_schema` in the database.

### 1. Identify Correlated Parameters
Look for parameters that depend on each other. Common examples:
- **Moving Averages:** `fast_length`, `slow_length`, `signal_length` (MACD) or 3 MAs.
- **Bands:** `length`, `std_dev`.
- **Oscillators:** `rsi_length`, `rsi_upper`, `rsi_lower`.

### 2. Prepare the Schema
Construct a JSON schema with:
- `correlated_groups`: List of lists of parameter names.
- `parameters`: Range definitions (`min`, `max`, `step`) for Grid generation.

**Example JSON:**
```json
{
  "correlated_groups": [
    ["media_curta", "media_inter", "media_longa"]
  ],
  "parameters": {
    "media_curta": { "min": 3, "max": 15, "step": 2 },
    "media_inter": { "min": 15, "max": 35, "step": 4 },
    "media_longa": { "min": 25, "max": 60, "step": 5 },
    "stop_loss": { "min": 0.01, "max": 0.1, "step": 0.01 }
  }
}
```

### 3. Create Migration Script
Use the provided template in `scripts/migrate_cruzamentomedias.py`.

```python
import sqlite3
import json

db_path = 'backend/data/crypto_backtest.db'
template_name = 'Example: YOUR_STRATEGY'

# Define schema (as above)
optimization_schema = { ... }

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
    UPDATE combo_templates 
    SET optimization_schema = ? 
    WHERE name = ?
""", (json.dumps(optimization_schema), template_name))

conn.commit()
conn.close()
```

## Grid Size Limits & Recommendations

Grid Search grows exponentially ($O(n^m)$). To ensure performance:

- **Soft Limit:** The system warns if combinations > **1,000**.
- **Hard Recommendation:** Keep total grid search < **2,000** tests per stage.
- **Optimization Time:** ~100 tests take ~1 minute (parallelized). 1,000 tests ≈ 10 minutes.

**Strategies to reduce grid size:**
1.  **Increase Step Size:** Use `step: 5` instead of `step: 1` for long periods (e.g., Length 20-200).
2.  **Narrow Ranges:** Use domain knowledge to restrict `min`/`max`.
3.  **Split Groups:** If parameters are weakly correlated, keep them sequential.

## Stage Execution Order

The `ComboOptimizer` generates stages in this specific order:

1.  **Timeframe (User Selected):** Not optimized unless explicitly enabled (usually fixed).
2.  **Grid Search Stages:** Correlated groups are processed first. This establishes a strong "base configuration".
3.  **Sequential Stages:** Independent parameters are optimized one by one against the fixed base from the Grid Search.

## UI Considerations (Future Phase 2)

Currently, the UI does not natively support defining correlated groups visually.
- **Current State:** Users select single parameter ranges.
- **Metadata Override:** The database metadata takes precedence for stage generation.
- **Future Enhancement:** Update the frontend to allow "grouping" parameters and defining joint grid steps visually.
