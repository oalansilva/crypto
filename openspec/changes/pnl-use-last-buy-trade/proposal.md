## Why

The current PnL calculation on `/external/balances` is averaging multiple buy trades for the same asset. Alan's trading model for this wallet is based on a single active buy reference, so the UI should treat only the most recent buy trade for each asset as the purchase reference price.

## What Changes

- Change the PnL purchase-price reference for each asset on `/external/balances`.
- Stop using historical average buy price across multiple buy trades.
- Use only the latest buy trade for the asset as the `average_buy_price` / purchase reference shown and used by PnL.
- Keep behavior explicit when an asset has no buy trade history.

## Scope

In scope:
- Backend logic that derives purchase reference price for balances/PnL.
- API response fields used by `/external/balances` for buy reference and PnL.
- UI validation on `/external/balances` for the updated PnL behavior.
- Automated tests covering the latest-buy-trade rule.

Out of scope:
- FIFO/LIFO cost basis models.
- Full historical realized PnL redesign.
- Changes to unrelated wallet screens.

## Success Criteria

- For an asset with multiple historical buy trades, PnL uses only the most recent buy trade price.
- The displayed purchase reference on `/external/balances` matches the latest buy trade for that asset.
- Assets without any buy trade continue to behave safely and predictably.
- Tests cover at least one multi-buy scenario proving the old average behavior no longer applies.
