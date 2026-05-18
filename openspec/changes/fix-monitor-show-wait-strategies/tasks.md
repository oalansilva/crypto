## 1. Implementation

- [x] Update Monitor signal resolver to remove visible/internal `wait` section from UI classification.
- [x] Normalize backend opportunity API status to only `HOLD` or `EXIT`.
- [x] Update Monitor Telegram status handling to use only `HOLD` or `EXIT`.
- [x] Update Monitor status grouping to use only Compra/Hold and Venda/Exit sections.
- [x] Update OpportunityCard styling/message handling for the removed `wait` section.
- [x] Add/adjust E2E coverage for same-symbol starred BTC strategies where one raw status is `BUY_NEAR`.

## 2. Validation

- [x] Run focused frontend E2E tests for Monitor state rendering.
- [x] Run frontend build.
- [x] Run OpenSpec validation for this change.
