## Why

The current Lab run flow has state inconsistencies, weak retry handling, and lacks timeouts, which can confuse the UI and leave runs stuck. Hardening the run lifecycle improves reliability, debuggability, and user trust.

## What Changes

- Align run `status`/`phase` transitions with actual execution state.
- Replace raw threads with managed background execution for runs.
- Improve Trader retry logic to use `reasons` when `required_fixes` are missing.
- Validate Trader/Dev structured outputs with schema checks and fallback handling.
- Add per-node and total run timeouts with clear diagnostics.

## Capabilities

### New Capabilities
- `lab-run-hardening`: Reliability guardrails for Lab run execution (state, retries, timeouts, output validation).

### Modified Capabilities
- (none)

## Impact

- Backend Lab run orchestration (`lab.py`, `lab_graph.py`).
- Trace/logging fields and diagnostics for runs.
- No API contract breaking changes expected; adds more consistent state and error data.
