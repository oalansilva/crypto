# Tasks

- [ ] Confirm how Monitor currently identifies asset type `cryptocurrency`.
- [ ] Confirm how the runtime exposes whether the user has a Binance connection configured.
- [ ] Define the Wallet data contract used to derive the Portfolio value/state for the affected Monitor flow.
- [ ] Design the read-only/disabled UI state for the Portfolio option when the rule applies.
- [ ] Define empty-state behavior when Binance is configured but Wallet has no relevant owned crypto assets.
- [ ] Implement the business rule: crypto asset + Binance configured => Portfolio is not manually editable.
- [ ] Implement the source-of-truth rule: affected Portfolio value/state comes from Wallet-held assets.
- [ ] Preserve current behavior for non-crypto assets.
- [ ] Preserve current behavior for crypto assets without Binance configured.
- [ ] Add/update product and technical validation coverage for the affected Monitor scenarios.
- [ ] QA validate with UI evidence that the Portfolio option is read-only only in the intended scenario and remains unchanged elsewhere.

## QA checklist
- [ ] Scenario 1: crypto asset with Binance configured shows Portfolio as read-only.
- [ ] Scenario 2: crypto asset with Binance configured derives Portfolio from Wallet data.
- [ ] Scenario 3: non-crypto asset keeps current behavior.
- [ ] Scenario 4: crypto asset without Binance configured keeps current behavior.
- [ ] Scenario 5: UI messaging makes the non-editable state understandable.