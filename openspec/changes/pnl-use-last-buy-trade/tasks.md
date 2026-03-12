## 1. Discovery / PO

- [x] 1.1 Confirm desired rule: for each asset, use only the latest buy trade as the purchase reference for PnL.
- [x] 1.2 Confirm screen in scope: `/external/balances`.
- [ ] 1.3 Identify current backend/frontend code path where average buy price is derived.

## 2. Implementation

- [ ] 2.1 Replace average-buy aggregation with latest-buy-trade lookup per asset.
- [ ] 2.2 Ensure the API fields consumed by `/external/balances` expose the latest buy trade price consistently.
- [ ] 2.3 Keep safe fallback behavior for assets with no buy trades.
- [ ] 2.4 Verify the UI reflects the new purchase reference and resulting PnL values.

## 3. Testing

- [ ] 3.1 Add/update automated test for an asset with multiple buy trades where only the most recent buy trade must be used.
- [ ] 3.2 Add/update regression coverage for no-buy-trade fallback behavior.
- [ ] 3.3 Run relevant backend/frontend tests for `/external/balances`.

## 4. Review / Handoff

- [ ] 4.1 Prepare a short PT-BR review summary for Alan.
- [ ] 4.2 Move through DEV -> QA -> Alan homologation in the normal workflow.
