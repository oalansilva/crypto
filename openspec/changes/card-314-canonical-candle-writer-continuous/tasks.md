## 1. Runtime units and restart

- [x] 1.1 Add system systemd service/timer templates for DEV and PROD candle writers (API keeps writer disabled)
- [x] 1.2 Add/adjust installer scripts that enable exactly one writer timer per environment root
- [x] 1.3 Integrate DEV installer/enable into canonical `./restart`
- [x] 1.4 Update `docs/runtime-architecture.md` with DEV enablement and PROD release steps

## 2. API degraded signaling and lag observability

- [x] 2.1 Mark stale canonical candle responses as degraded with lag fields
- [x] 2.2 Expose lag/freshness evidence in candle metrics and/or runtime status
- [x] 2.3 Ensure writer lag alert path covers one-shot incremental runs

## 3. Tests and validation

- [x] 3.1 Add/extend tests for writer lock exclusion and incremental run state
- [x] 3.2 Add/extend tests for degraded API payload and fallback contingency
- [x] 3.3 Add/extend tests for lag alert/threshold behavior
- [x] 3.4 Validate OpenSpec change and focused backend tests
