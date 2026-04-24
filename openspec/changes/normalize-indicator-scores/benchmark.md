## Indicator Score Normalization Benchmark

### Goal

Measure the overhead of converting persisted `market_indicator` rows into normalized `0-10` scores for the composite engine.

### Command

```bash
cd backend
../backend/.venv/bin/python scripts/benchmark_indicator_score_service.py --rows 10000
```

### Method

- Builds synthetic rows containing all fields used by the default ruleset.
- Loads `backend/config/indicator_score_rules.v1.json`.
- Runs `IndicatorScoreService.score_rows`.
- Reports elapsed milliseconds, rows per second, generated score count, and ruleset version.

### Current Result

On the VPS/dev runtime, the default service produced this result for 10,000 rows:

```text
ruleset_version=technical-normalization/v1
rows=10000
scores=90000
elapsed_ms=897.310
rows_per_second=11144.42
```

### Acceptance Benchmark

The normalizer is an in-memory transformation with no database or network calls. For 10,000 rows on the VPS/dev runtime, expected throughput is at least 10,000 rows/second. This threshold is intentionally documented instead of enforced in CI to avoid noisy timing failures on shared runners.
