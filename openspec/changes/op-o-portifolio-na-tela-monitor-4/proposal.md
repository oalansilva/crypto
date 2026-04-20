# Proposal: Lock Monitor Portfolio option for crypto assets with Binance connection

## Summary
On the Monitor screen, the Portfolio option for crypto assets must stop being manually editable when the user has a configured Binance connection. In this scenario, the Portfolio value must be derived from the user's Wallet/held assets.

## Problem
Users can currently change the Portfolio option manually even when their crypto positions should come from Binance-linked wallet data. This creates inconsistency between Monitor behavior and the user's actual holdings.

## User story
As a crypto user with Binance connected,
I want the Monitor Portfolio option to be driven by my wallet holdings,
so that the Monitor reflects my real crypto positions and avoids manual mismatch.

## Value
- Reduces inconsistency between Monitor and Wallet data.
- Prevents incorrect manual selection for Binance-connected crypto assets.
- Makes the Monitor behavior more trustworthy for crypto use cases.

## Scope in
- Monitor screen behavior for assets of type `cryptocurrency`.
- Detection of whether the user has a Binance connection configured.
- Read-only Portfolio option in the affected scenario.
- Portfolio source derived from Wallet/held-asset data in the affected scenario.
- Clear UI state indicating the field is not manually editable.

## Scope out
- Changes to non-crypto asset behavior.
- Forced Wallet integration for users without Binance configured.
- Broader portfolio logic redesign outside the Monitor use case.
- Exchange integrations beyond the current Binance-based rule.

## Rules
1. If asset type is `cryptocurrency` and Binance connection is configured, Portfolio is not manually editable.
2. In that same scenario, Portfolio must reflect Wallet/owned-asset data.
3. If asset type is not `cryptocurrency`, current behavior remains unchanged.
4. If Binance connection is not configured, current behavior remains unchanged.

## Dependencies
- Reliable asset-type classification.
- Reliable Binance-connection status for the user.
- Wallet data source capable of exposing owned crypto assets to Monitor.
- UI design for disabled/read-only state.

## Risks
- Ambiguous wallet-to-monitor mapping could create user confusion.
- Hidden editability without clear UI messaging may look like a bug.
- Edge cases if wallet data is empty, stale, or unavailable.

## Option considered
### Option A, recommended
Lock manual editing and derive the value from Wallet when Binance is configured.
- Pros: consistent, low ambiguity, aligned with request.
- Cons: requires clear empty/error-state handling.

## 5W2H
- What: lock Portfolio editing for Binance-connected crypto assets and derive it from Wallet.
- Why: keep Monitor aligned with actual user holdings.
- Who: users configuring crypto assets in Monitor.
- Where: Monitor screen.
- When: whenever a crypto asset is handled and Binance is configured.
- How: check asset type + Binance connection, then switch Portfolio to Wallet-driven read-only mode.
- How much: limited-scope product change with UI and business-rule impact.

## Acceptance criteria
1. Given a cryptocurrency asset and a user with Binance configured, when the Monitor screen is opened, then the Portfolio option is displayed as non-editable.
2. Given a cryptocurrency asset and a user with Binance configured, when the Monitor screen loads, then the Portfolio value/state is derived from Wallet-held assets.
3. Given a non-cryptocurrency asset, when the Monitor screen is opened, then current Portfolio behavior remains unchanged.
4. Given a cryptocurrency asset and no Binance connection configured, when the Monitor screen is opened, then current Portfolio behavior remains unchanged.
5. The UI clearly communicates that the affected Portfolio option is read-only.
6. QA can validate the disabled/read-only state and source-of-truth behavior with UI evidence.