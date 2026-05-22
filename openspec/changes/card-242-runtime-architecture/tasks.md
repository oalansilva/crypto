## 1. Runtime Boundaries

- [x] 1.1 Add explicit FastAPI non-critical service gates for OHLCV ingestion, backfill scheduler, and Binance realtime connector.
- [x] 1.2 Add safe runtime status helpers for boolean flags, worker enablement, candle writer lock, and latest writer state.
- [x] 1.3 Expose a runtime status API endpoint without secrets or raw connection strings.

## 2. Candle Writer Operation

- [x] 2.1 Add file-lock protection to the one-shot canonical candle writer command.
- [x] 2.2 Persist latest candle writer run state for operational evidence.
- [x] 2.3 Add opt-in systemd user service and timer templates for the dedicated candle writer.
- [x] 2.4 Add installer script for the candle writer timer without enabling it from the default stack service.

## 3. Documentation

- [x] 3.1 Document runtime architecture, startup order, flags, service ownership, logs, and verification commands.
- [x] 3.2 Link the runtime architecture runbook from the project hub.

## 4. Validation

- [x] 4.1 Add focused tests for runtime status payload and writer lock behavior.
- [x] 4.2 Run focused backend tests for runtime, API, and candle writer behavior.
- [x] 4.3 Validate the OpenSpec change.

Note: use project skills when applicable for architecture, tests, debugging, and frontend work.
