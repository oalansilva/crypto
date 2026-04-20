# Tasks

## PO
- [x] Frame the change as Monitor-to-Wallet consistency for crypto portfolio ownership.
- [x] Define scope, risks, recommendation, and testable acceptance criteria.
- [x] Publish PO review package with direct OpenSpec paths.

## DESIGN
- [ ] Create the mandatory Monitor prototype for the locked `Portfolio` control when Binance is connected.
  - Acceptance: `prototype/prototype.html` or `prototype.html` shows editable and locked states for the same control.
- [ ] Define the visual language for Wallet-synced crypto portfolio state.
  - Acceptance: the UI clearly explains that the value is derived from Wallet/Binance and cannot be edited manually.
- [ ] Define the fallback state for Binance-connected crypto assets when holdings cannot be resolved.
  - Acceptance: the prototype shows a deterministic blocked state/message without enabling silent conflicting edits.

## DEV
- [ ] Detect whether the current asset is classified as cryptocurrency.
  - Acceptance: the lock rule runs only for crypto assets.
- [ ] Detect whether the user has a Binance connection configured.
  - Acceptance: the rule activates only when Binance connectivity is available.
- [ ] Derive the Monitor `Portfolio` state from the same Wallet/Binance holdings source of truth.
  - Acceptance: Monitor and Wallet return the same included/not-included state for the tested crypto asset.
- [ ] Disable manual editing of the crypto `Portfolio` option when Binance is connected.
  - Acceptance: the user cannot toggle the control manually in this scenario.
- [ ] Preserve manual editing behavior for non-crypto assets or users without Binance connection.
  - Acceptance: unaffected scenarios keep current editable behavior.
- [ ] Implement the agreed fallback for unresolved holdings data.
  - Acceptance: crypto controls do not silently become editable while the holdings state is unknown.

## QA
- [ ] Validate a crypto asset with Binance disconnected.
  - Acceptance: `Portfolio` remains editable.
- [ ] Validate a crypto asset with Binance connected and asset present in Wallet.
  - Acceptance: the control is locked and shown as included in portfolio.
- [ ] Validate a crypto asset with Binance connected and asset absent from Wallet.
  - Acceptance: the control is locked and shown as not included in portfolio.
- [ ] Validate a non-crypto asset with Binance connected.
  - Acceptance: the lock rule is not applied.
- [ ] Validate the unresolved-holdings fallback behavior.
  - Acceptance: the UI matches the approved deterministic fallback and never allows silent conflicting edits.
- [ ] Attach reproducible evidence, preferably Playwright-based.
  - Acceptance: QA provides proof for connected, disconnected, present, absent, and fallback scenarios.

## Notes
- Expected next owner: DESIGN.
- Prototype is mandatory before any move toward approval because the control behavior changes visibly in the UI.
- Main product rule: for crypto assets with Binance connected, Monitor must mirror Wallet holdings instead of accepting manual overrides.
- ICE: 384
