## 1. Preflight Logic Flow

- [ ] 1.1 Remove fallback simplification path for invalid `entry_logic` and `exit_logic` in backend preflight.
- [ ] 1.2 Enforce Dev rewrite loop that accepts only valid boolean expressions before execution.
- [ ] 1.3 Return validation failure and stop run when Dev rewrite cannot produce valid boolean logic.

## 2. Trace Logging

- [ ] 2.1 Persist correction metadata: original logic, rewritten logic, reason, validation outcome, and no-fallback marker.
- [ ] 2.2 Add/adjust backend tests for rewrite success, rewrite failure, and explicit no-EMA/RSI-fallback behavior.

Note: Use relevant project skills under `.codex/skills` when implementing (backend/testing/debugging) where applicable.
