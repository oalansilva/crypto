## 1. Runtime Controls

- [x] 1.1 Add CPU sampling, refresh state persistence, and throttled cycle summary to the favorite refresh service.
- [x] 1.2 Add configurable defaults for daily interval, batch size, CPU ceiling, and pauses in the stack startup path.

## 2. Observability

- [x] 2.1 Expose sanitized latest favorite refresh cycle state through `/api/runtime/status`.
- [x] 2.2 Keep per-favorite audit behavior in `auto_backtest_runs` unchanged for success and failure.

## 3. Validation

- [x] 3.1 Add focused tests for CPU guardrail, batch limiting, runtime worker enablement, and runtime status state.
- [x] 3.2 Run OpenSpec validation and focused backend tests for the changed modules.

Note: use project skills when applicable for architecture, tests, debugging, or frontend validation.
