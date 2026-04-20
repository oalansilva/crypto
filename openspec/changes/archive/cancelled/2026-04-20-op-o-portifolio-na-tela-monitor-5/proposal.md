# Proposal

## Change
Lock the `Portfolio` option in the Monitor screen for crypto assets when the user has a configured Binance connection, deriving the state from wallet holdings instead of allowing manual edits.

## Work item type
change

## Problem statement
Today the Monitor screen allows the user to toggle the `Portfolio` option manually. For crypto assets, this becomes misleading when Binance is connected because the portfolio state should reflect the user's real holdings, not a manual choice. The current behavior creates inconsistency between the Monitor UI and the wallet/integration source of truth.

## User story
As a user with Binance connected,
I want crypto assets in Monitor to have their `Portfolio` state derived automatically from my wallet holdings,
So that I cannot manually set an incorrect portfolio state.

## Value proposition
- Prevents wrong portfolio classification for crypto assets.
- Aligns Monitor behavior with real wallet holdings.
- Reduces user confusion by removing a toggle that should not be editable in this scenario.

## Scope in
- Apply the rule only to assets of type `cryptocurrency`.
- Detect when the user has an active/configured Binance connection.
- Disable manual editing of the Monitor `Portfolio` option for eligible crypto assets.
- Derive the displayed `Portfolio` state from wallet holdings/integration data.
- Keep the UI state deterministic and testable when wallet data changes.
- Define QA-ready acceptance criteria for connected and disconnected scenarios.

## Scope out
- Non-crypto asset types.
- Reworking the whole wallet module or Binance onboarding flow.
- Manual portfolio editing rules for assets without Binance connection.
- Historical portfolio accounting or PnL changes.

## Dependencies
- Existing Binance connection status must be available to the Monitor flow.
- Wallet/holdings data must expose whether the user currently holds the crypto asset.
- DESIGN is needed for the UI state of a disabled/non-editable portfolio control in Monitor.

## Risks
- If holdings freshness is unclear, the UI can appear inconsistent after trades.
- If Monitor and wallet use different asset identifiers, mapping errors may lock the wrong state.
- If no explicit empty-state copy is defined, users may not understand why the control is disabled.

## Functional framing
For crypto assets in Monitor:
1. If Binance connection is configured, the `Portfolio` option is read-only.
2. The read-only state must reflect wallet holdings for that asset.
3. If holdings indicate the asset is owned, Monitor shows it as in portfolio.
4. If holdings indicate the asset is not owned, Monitor shows it as not in portfolio.
5. Manual toggle interaction must not change this state while Binance is connected.

For non-crypto assets, current behavior remains unchanged unless another rule already exists.

## Options considered
### Option A, auto-derived and locked when Binance is connected
- Most aligned with the request.
- Prevents conflicting manual edits.
- Recommended.

### Option B, keep manual toggle but show Binance as suggestion
- Lower implementation effort.
- Keeps source-of-truth ambiguity.
- Not recommended.

## Recommendation
Adopt Option A. For crypto assets, Binance-connected users must see a locked `Portfolio` state driven by wallet holdings.

## Acceptance criteria
1. Given a crypto asset in Monitor and a configured Binance connection, when the card is rendered, then the `Portfolio` option is not manually editable.
2. Given a crypto asset in Monitor and wallet holdings show the asset is owned, when the card is rendered, then `Portfolio` appears enabled/active based on holdings.
3. Given a crypto asset in Monitor and wallet holdings show the asset is not owned, when the card is rendered, then `Portfolio` appears disabled/inactive based on holdings.
4. Given a crypto asset with Binance connected, when the user tries to change the `Portfolio` option, then no manual change is applied.
5. Given a non-crypto asset, when the Monitor card is rendered, then this Binance-lock rule does not alter the existing behavior.
6. Given there is no Binance connection configured, when a crypto asset is rendered, then the Monitor follows the existing non-locked behavior.
7. Given wallet holdings change after a refresh, when Monitor reloads the asset state, then the `Portfolio` indicator matches the latest holdings data.

## 5W2H
- What: Lock Monitor `Portfolio` for crypto assets when Binance is connected.
- Why: Portfolio state must reflect real holdings, not manual toggles.
- Who: Users who monitor crypto assets with wallet integration.
- Where: Monitor screen asset cards/settings.
- When: In this change.
- How: Use Binance connection + wallet holdings as source of truth.
- How much: Small-to-medium UI and integration adjustment.

## Prioritization
- Impact: 8
- Confidence: 8
- Ease: 6
- ICE: 384
