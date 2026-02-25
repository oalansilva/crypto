## Why

Current handling for invalid `entry_logic`/`exit_logic` can fall back to simplified default logic, which hides real strategy errors and changes intended behavior. This change enforces deterministic correction: Dev must rewrite logic into valid boolean expressions or the run must fail.

## What Changes

- Remove fallback logic that simplifies invalid `entry_logic`/`exit_logic` (including EMA/RSI fallback).
- Require Dev to rewrite invalid entry/exit expressions into valid boolean format before execution.
- If Dev cannot produce valid boolean logic, fail preflight and stop execution.
- Log each correction attempt and applied correction in run trace metadata.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `backend`: invalid entry/exit handling now requires Dev boolean rewrite, disallows simplification fallback, and enforces correction logging.

## Impact

- Affected code: backend preflight validation/correction path and run trace logging.
- API/runtime behavior: invalid logic no longer auto-simplifies; runs fail when valid boolean rewrite is not achieved.
- Validation/tests: backend tests for rewrite success, rewrite failure, and correction log fields.
