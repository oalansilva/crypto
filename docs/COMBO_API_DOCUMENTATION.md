# Combo Strategies API Documentation

Complete API reference for programmatic access to combo strategies.

**Base URL:** `http://localhost:8000/api/combos`

---

## Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/templates` | List all available templates |
| GET | `/meta/:template` | Get template metadata |
| POST | `/backtest` | Execute backtest |
| POST | `/optimize` | Run parameter optimization |
| POST | `/templates` | Create custom template |
| DELETE | `/templates/:id` | Delete custom template |

---

## 1. List Templates

Get all available combo strategy templates.

### Request

```http
GET /api/combos/templates
```

### Response

```json
{
  "prebuilt": [
    {
      "name": "multi_ma_crossover",
      "description": "Triple Moving Average Crossover Strategy"
    },
    {
      "name": "ema_rsi",
      "description": "EMA + RSI combo for trend following with momentum confirmation"
    }
  ],
  "examples": [
    {
      "name": "example_ema_cross",
      "description": "Simple EMA crossover example"
    }
  ],
  "custom": [
    {
      "name": "my_strategy",
      "description": "My custom strategy"
    }
  ]
}
```

### Response Fields

- `prebuilt`: Built-in professional templates
- `examples`: Sample templates for learning
- `custom`: User-created templates

---

## 2. Get Template Metadata

Retrieve detailed information about a specific template.

### Request

```http
GET /api/combos/meta/:template_name
```

**Path Parameters:**
- `template_name` (string, required): Template identifier

### Example

```http
GET /api/combos/meta/ema_rsi
```

### Response

```json
{
  "name": "ema_rsi",
  "description": "EMA + RSI combo for trend following",
  "is_prebuilt": true,
  "indicators": [
    {
      "type": "ema",
      "alias": "fast",
      "params": {
        "length": 9
      }
    },
    {
      "type": "ema",
      "alias": "slow",
      "params": {
        "length": 21
      }
    },
    {
      "type": "rsi",
      "params": {
        "length": 14
      }
    }
  ],
  "entry_logic": "(close > fast) & (close > slow) & (RSI_14 > 30) & (RSI_14 < 50)",
  "exit_logic": "(RSI_14 > 70) | (close < fast)",
  "stop_loss": 0.015
}
```

### Response Fields

- `name`: Template identifier
- `description`: Human-readable description
- `is_prebuilt`: Whether it's a built-in template
- `indicators`: Array of indicator configurations
- `entry_logic`: Entry condition expression
- `exit_logic`: Exit condition expression
- `stop_loss`: Default stop loss percentage

---

## 3. Run Backtest

Execute a backtest for a combo strategy.

### Request

```http
POST /api/combos/backtest
Content-Type: application/json
```

```json
{
  "template_name": "ema_rsi",
  "symbol": "BTC/USDT",
  "timeframe": "1h",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "parameters": {
    "ema_fast": 9,
    "ema_slow": 21,
    "rsi_period": 14,
    "rsi_min": 30,
    "rsi_max": 50
  }
}
```

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `template_name` | string | Yes | Template to backtest |
| `symbol` | string | Yes | Trading pair (e.g., "BTC/USDT") |
| `timeframe` | string | Yes | Candle timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d) |
| `start_date` | string | Yes | Start date (YYYY-MM-DD) |
| `end_date` | string | Yes | End date (YYYY-MM-DD) |
| `parameters` | object | No | Custom parameter values |

### Response

```json
{
  "template_name": "ema_rsi",
  "symbol": "BTC/USDT",
  "timeframe": "1h",
  "parameters": {
    "ema_fast": 9,
    "ema_slow": 21,
    "rsi_period": 14
  },
  "metrics": {
    "total_trades": 47,
    "winning_trades": 28,
    "losing_trades": 19,
    "win_rate": 0.5957,
    "total_return": 0.1534,
    "sharpe_ratio": 1.45,
    "max_drawdown": 0.0823,
    "profit_factor": 1.89
  },
  "trades": [
    {
      "entry_time": "2024-01-15T10:00:00",
      "entry_price": 42500.0,
      "exit_time": "2024-01-16T14:00:00",
      "exit_price": 43200.0,
      "profit": 0.0165,
      "type": "long"
    }
  ],
  "indicator_data": {
    "fast": [42000, 42100, 42150, ...],
    "slow": [41800, 41900, 42000, ...],
    "RSI_14": [45.2, 48.3, 52.1, ...]
  },
  "candles": [
    {
      "timestamp_utc": "2024-01-01T00:00:00",
      "open": 42000.0,
      "high": 42500.0,
      "low": 41800.0,
      "close": 42300.0,
      "volume": 1234.56
    }
  ]
}
```

### Response Fields

**Metrics:**
- `total_trades`: Number of completed trades
- `winning_trades`: Number of profitable trades
- `losing_trades`: Number of losing trades
- `win_rate`: Percentage of winning trades (0-1)
- `total_return`: Total return percentage (0-1)
- `sharpe_ratio`: Risk-adjusted return metric
- `max_drawdown`: Maximum peak-to-trough decline (0-1)
- `profit_factor`: Gross profit / Gross loss

**Trades:**
- `entry_time`: Trade entry timestamp (ISO 8601)
- `entry_price`: Entry price
- `exit_time`: Trade exit timestamp
- `exit_price`: Exit price
- `profit`: Trade profit/loss percentage
- `type`: Trade direction ("long" or "short")

**Indicator Data:**
- Key-value pairs of indicator names to value arrays
- Aligned with candle timestamps

**Candles:**
- OHLCV data for chart visualization
- Timestamps in UTC ISO 8601 format

---

## 4. Run Optimization

Find optimal parameters for a combo strategy.

### Request

```http
POST /api/combos/optimize
Content-Type: application/json
```

```json
{
  "template_name": "ema_rsi",
  "symbol": "BTC/USDT",
  "timeframe": "1h",
  "start_date": "2024-01-01",
  "end_date": "2024-06-30",
  "custom_ranges": {
    "ema_fast": {
      "min": 5,
      "max": 15,
      "step": 1
    },
    "ema_slow": {
      "min": 15,
      "max": 30,
      "step": 1
    },
    "rsi_period": {
      "min": 10,
      "max": 20,
      "step": 2
    }
  }
}
```

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `template_name` | string | Yes | Template to optimize |
| `symbol` | string | Yes | Trading pair |
| `timeframe` | string | No | Fixed timeframe (omit to optimize) |
| `start_date` | string | Yes | Start date |
| `end_date` | string | Yes | End date |
| `custom_ranges` | object | No | Parameter optimization ranges |

**Custom Ranges Format:**
```json
{
  "parameter_name": {
    "min": <number>,
    "max": <number>,
    "step": <number>
  }
}
```

### Response

```json
{
  "job_id": "combo_opt_1234567890",
  "template_name": "ema_rsi",
  "symbol": "BTC/USDT",
  "total_stages": 6,
  "stages": [
    {
      "stage_num": 1,
      "stage_name": "Optimize ema_fast",
      "parameter": "ema_fast",
      "values": [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
      "description": "Optimize ema_fast"
    }
  ],
  "best_parameters": {
    "ema_fast": 7,
    "ema_slow": 23,
    "rsi_period": 12,
    "rsi_min": 28,
    "rsi_max": 52,
    "stop_loss": 0.015
  },
  "best_metrics": {
    "sharpe_ratio": 1.68,
    "total_return": 0.1847,
    "win_rate": 0.6234,
    "total_trades": 52
  }
}
```

### Response Fields

- `job_id`: Unique optimization job identifier
- `total_stages`: Number of optimization stages
- `stages`: Array of stage configurations
- `best_parameters`: Optimal parameter values found
- `best_metrics`: Performance metrics for best parameters

### Notes

- Optimization uses sequential approach (one parameter at a time)
- Optimizes for Sharpe Ratio by default
- Can take several minutes for large parameter spaces
- Timeout: 5 minutes

---

## 5. Create Custom Template

Save a custom combo strategy template.

### Request

```http
POST /api/combos/templates
Content-Type: application/json
```

```json
{
  "name": "my_custom_strategy",
  "description": "My custom EMA + MACD strategy",
  "indicators": [
    {
      "type": "ema",
      "alias": "trend",
      "params": {
        "length": 50
      }
    },
    {
      "type": "macd",
      "params": {
        "fast": 12,
        "slow": 26,
        "signal": 9
      }
    }
  ],
  "entry_logic": "(close > trend) & (MACD_macd > MACD_signal)",
  "exit_logic": "(MACD_macd < MACD_signal) | (close < trend)",
  "stop_loss": 0.02
}
```

### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique template name (lowercase, underscores) |
| `description` | string | Yes | Template description |
| `indicators` | array | Yes | Indicator configurations |
| `entry_logic` | string | Yes | Entry condition expression |
| `exit_logic` | string | Yes | Exit condition expression |
| `stop_loss` | number | No | Default stop loss (0-1), default: 0.015 |

**Indicator Format:**
```json
{
  "type": "indicator_type",
  "alias": "optional_alias",
  "params": {
    "param1": value1,
    "param2": value2
  }
}
```

### Response

```json
{
  "template_id": 42,
  "name": "my_custom_strategy",
  "message": "Template created successfully"
}
```

### Validation Rules

- Template name must be unique
- All indicators must be supported types
- Logic expressions must be valid Python expressions
- Stop loss must be between 0 and 1

---

## 6. Delete Custom Template

Remove a custom template.

### Request

```http
DELETE /api/combos/templates/:template_id
```

**Path Parameters:**
- `template_id` (integer, required): Template database ID

### Response

```json
{
  "success": true,
  "message": "Template deleted successfully"
}
```

### Notes

- Can only delete custom templates (not pre-built or examples)
- Returns 404 if template not found or not deletable

---

## Error Responses

All endpoints return standard error responses:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

### Example Error

```json
{
  "detail": "Template 'invalid_template' not found"
}
```

---

## Rate Limiting

Currently no rate limiting is enforced. For production use, implement appropriate rate limiting.

---

## Authentication

Currently no authentication is required. For production use, implement proper authentication and authorization.

---

## Interactive Documentation

For interactive API testing, visit:
```
http://localhost:8000/docs
```

This provides a Swagger UI with all endpoints, request/response schemas, and a "Try it out" feature.

---

## Code Examples

### Python

```python
import requests

# List templates
response = requests.get('http://localhost:8000/api/combos/templates')
templates = response.json()

# Run backtest
backtest_request = {
    "template_name": "ema_rsi",
    "symbol": "BTC/USDT",
    "timeframe": "1h",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
}
response = requests.post(
    'http://localhost:8000/api/combos/backtest',
    json=backtest_request
)
results = response.json()
print(f"Sharpe Ratio: {results['metrics']['sharpe_ratio']}")
```

### JavaScript

```javascript
// List templates
const templates = await fetch('http://localhost:8000/api/combos/templates')
  .then(res => res.json());

// Run backtest
const backtestRequest = {
  template_name: 'ema_rsi',
  symbol: 'BTC/USDT',
  timeframe: '1h',
  start_date: '2024-01-01',
  end_date: '2024-12-31'
};

const results = await fetch('http://localhost:8000/api/combos/backtest', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(backtestRequest)
}).then(res => res.json());

console.log(`Sharpe Ratio: ${results.metrics.sharpe_ratio}`);
```

### cURL

```bash
# List templates
curl http://localhost:8000/api/combos/templates

# Run backtest
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

---

## Support

For additional help:
- Interactive docs: `http://localhost:8000/docs`
- Source code: `backend/app/routes/combo_routes.py`
- User guide: [COMBO_STRATEGIES_USER_GUIDE.md](./COMBO_STRATEGIES_USER_GUIDE.md)
