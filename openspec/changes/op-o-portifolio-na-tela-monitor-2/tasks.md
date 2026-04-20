## 1. Product and data contract

- [ ] 1.1 Confirm the wallet/Binance holdings source used as the canonical portfolio source for cryptocurrency assets in Monitor.
- [ ] 1.2 Confirm the asset taxonomy rule that identifies when the selected asset type is cryptocurrency.
- [ ] 1.3 Define the empty-state behavior when Binance is connected but no eligible crypto holdings are returned.

## 2. Frontend behavior on Monitor

- [ ] 2.1 Detect the Binance-connected + cryptocurrency scenario when loading the Monitor portfolio control.
- [ ] 2.2 Render the Portfolio option as disabled/read-only in that scenario.
- [ ] 2.3 Show explanatory UI copy stating that the crypto portfolio is synced from Binance wallet holdings.
- [ ] 2.4 Preserve current editable behavior when Binance is not connected.
- [ ] 2.5 Preserve current editable behavior for non-cryptocurrency asset types.
- [ ] 2.6 Render the defined empty state when no synced crypto holdings are available.

## 3. Backend and integration behavior

- [ ] 3.1 Expose the Binance connection state needed by Monitor.
- [ ] 3.2 Expose the wallet holdings payload needed to derive Monitor portfolio content for crypto assets.
- [ ] 3.3 Prevent persistence of manual Monitor portfolio edits in the Binance-connected cryptocurrency scenario.
- [ ] 3.4 Ensure the returned portfolio dataset is limited to eligible cryptocurrency holdings.

## 4. Validation

- [ ] 4.1 Add backend/integration coverage for the lock rule by scenario: Binance connected crypto, Binance disconnected, and non-crypto.
- [ ] 4.2 Add UI or Playwright validation that the Portfolio option is blocked for crypto when Binance is connected.
- [ ] 4.3 Add validation that the synced portfolio matches wallet holdings and that manual override is not persisted.
- [ ] 4.4 Add validation for the empty-state scenario with Binance connected and no crypto holdings.

## 5. Workflow follow-up

- [ ] 5.1 DESIGN: provide prototype for the blocked/read-only Monitor Portfolio state before any approval gate beyond PO.
