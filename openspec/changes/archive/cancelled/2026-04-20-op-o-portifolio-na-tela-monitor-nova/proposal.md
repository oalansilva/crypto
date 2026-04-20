# Proposal

## Change
Lock the `Portfolio` option in the Monitor screen for cryptocurrency assets when the user has a valid Binance wallet connection, deriving the displayed state from wallet holdings instead of allowing manual edits.

## Work item type
change

## Problem statement
The Monitor screen currently allows manual changes to `Portfolio`. For cryptocurrency assets this can conflict with the wallet source of truth when the user has Binance connected, creating inconsistency between Monitor and the integrated wallet.

## User story
As a user with Binance connected,
I want the `Portfolio` state for cryptocurrency assets in Monitor to be derived automatically from my wallet holdings,
So that the Monitor does not show a manual state that conflicts with my real wallet.

## Value proposition
- Prevents inconsistent portfolio status for crypto assets.
- Aligns Monitor with the integrated wallet source of truth.
- Reduces confusion by making the rule explicit and deterministic.

## Scope in
- Apply the rule only to assets classified as cryptocurrency.
- Activate the rule only when the user has a valid Binance connection for wallet reading.
- Make `Portfolio` read-only in Monitor while the rule is active.
- Derive the displayed state from current wallet holdings.
- Keep the control blocked even when holdings are empty, reflecting a derived inactive state.
- Show clear UI feedback that the value is managed automatically by the wallet integration.
- Define fallback behavior for wallet sync delay or unavailability.

## Scope out
- Non-crypto assets.
- Rework of Binance onboarding or connection setup.
- New portfolio accounting logic outside the current wallet contract.
- Broad Monitor redesign beyond the locked-state UX needed for this rule.

## Dependencies
- Canonical asset classification for cryptocurrency assets.
- Binance connection status exposed to the Monitor flow.
- Wallet holdings data available for the monitored asset.
- DESIGN prototype for the locked/derived UI state before approval.

## Risks
- Wallet sync delay can make the derived state appear stale.
- Asset identifier mismatch between Monitor and wallet can derive the wrong state.
- Missing explanatory copy can make the blocked control look broken.

## Functional framing
1. If the asset is cryptocurrency and Binance is validly connected, `Portfolio` becomes read-only.
2. The displayed `Portfolio` state comes from wallet holdings, not manual input.
3. If the wallet shows holdings for the asset, Monitor displays the asset as in portfolio.
4. If the wallet shows no holdings, Monitor displays the asset as not in portfolio.
5. If wallet sync is unavailable or stale, the control stays blocked and the UI indicates unavailable or outdated wallet data.
6. If the asset is not cryptocurrency, current behavior remains unchanged.
7. If Binance is not validly connected, current behavior remains unchanged.

## Options considered
### Option A, lock and derive from wallet holdings
- Matches the product request.
- Eliminates source-of-truth ambiguity.
- Recommended.

### Option B, keep manual toggle and only suggest wallet state
- Lower effort.
- Still allows inconsistency.
- Not recommended.

## Recommendation
Adopt Option A. For cryptocurrency assets with valid Binance wallet connection, `Portfolio` must be wallet-derived and non-editable.

## Acceptance criteria
1. Given a cryptocurrency asset in Monitor and a valid Binance connection, when the card is rendered, then `Portfolio` is not manually editable.
2. Given a cryptocurrency asset in Monitor and wallet holdings include the asset, when the card is rendered, then `Portfolio` appears active based on wallet data.
3. Given a cryptocurrency asset in Monitor and wallet holdings do not include the asset, when the card is rendered, then `Portfolio` appears inactive based on wallet data.
4. Given a cryptocurrency asset with Binance connected, when the user attempts to change `Portfolio`, then no manual change is applied.
5. Given wallet sync is unavailable or stale while the Binance rule is active, when the card is rendered, then `Portfolio` remains blocked and the UI indicates that wallet data is unavailable or outdated.
6. Given a non-crypto asset, when the Monitor card is rendered, then this rule does not alter the existing behavior.
7. Given there is no valid Binance connection, when a cryptocurrency asset is rendered, then the Monitor follows the existing editable behavior.

## 5W2H
- What: Lock and auto-derive `Portfolio` for Monitor cryptocurrency assets.
- Why: Keep Monitor aligned with the integrated wallet source of truth.
- Who: Users who monitor crypto assets with Binance wallet connection.
- Where: Monitor screen.
- When: In this change.
- How: Use asset type + Binance connection + wallet holdings to derive the state.
- How much: Small-to-medium UI and integration adjustment.

## Prioritization
- Impact: 8
- Confidence: 8
- Ease: 6
- ICE: 384
