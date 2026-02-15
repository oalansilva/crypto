## 1. Preflight Logic Flow

- [x] 1.1 Remove fallback simplification path for invalid `entry_logic` and `exit_logic` in backend preflight.
- [x] 1.2 Enforce Dev rewrite loop that accepts only valid boolean expressions before execution.
- [x] 1.3 Return validation failure and stop run when Dev rewrite cannot produce valid boolean logic.

## 2. Trace Logging

- [x] 2.1 Persist correction metadata: original logic, rewritten logic, reason, validation outcome, and no-fallback marker.
- [x] 2.2 Add/adjust backend tests for rewrite success, rewrite failure, and explicit no-EMA/RSI-fallback behavior.

Note: Use relevant project skills under `.codex/skills` when implementing (backend/testing/debugging) where applicable.
