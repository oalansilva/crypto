# Proposal

## Change
Lock the `Portfolio` option in the Monitor screen for cryptocurrency assets whenever the user has a Binance connection configured, deriving the state from the Wallet holdings instead of allowing manual changes.

## Work item type
change

## Problem statement
The Monitor screen currently allows the user to change the `Portfolio` option even when a Binance connection is configured. For cryptocurrency assets, this creates a product inconsistency because the selected portfolio state can diverge from the assets that actually exist in the connected wallet.

Based on refinement, the intended behavior is to treat Binance as the source of truth for crypto holdings. When the connection exists, the user must not manually override the Monitor portfolio state for crypto assets.

## User story
As a crypto user with Binance connected,
I want the Monitor portfolio option to follow my Wallet holdings automatically,
So that the Monitor reflects my real owned assets and I cannot set a conflicting manual state.

## Value proposition
- Prevents divergence between Monitor and Wallet for crypto assets.
- Increases trust in the Monitor screen as a reflection of the real connected portfolio.
- Reduces user error caused by manual toggling of a state that should be system-derived.

## Scope in
- Apply the rule only to assets classified as cryptocurrency.
- Detect whether the user has an active Binance connection configured.
- When Binance is connected, make the Monitor `Portfolio` option non-editable for crypto assets.
- Derive the crypto portfolio state from Wallet holdings data.
- Define the expected empty-state behavior when Binance is connected but no qualifying crypto asset is held.
- Expose clear UI feedback explaining why the option is locked.

## Scope out
- Non-crypto assets, including any asset classes that are not classified as cryptocurrency.
- Manual portfolio behavior when Binance is not connected.
- Full Wallet redesign or broader Monitor redesign.
- Trading signal logic, favorites, or unrelated Monitor filters.
- Buy/sell synchronization beyond reflecting current Wallet holdings.

## Risks and dependencies
- Dependency: DEV must confirm the canonical source for Binance-connected holdings used by Wallet.
- Dependency: DESIGN is needed because the Monitor control must clearly communicate locked/auto-derived behavior.
- Risk: if asset-type classification is inconsistent, non-crypto assets may be locked incorrectly.
- Risk: if Wallet data freshness is unclear, users may not understand why Monitor changed or stayed locked.
- Risk: if Binance is connected but holdings are unavailable due to transient fetch failure, the product needs a safe fallback that does not silently enable conflicting edits.

## Functional framing
For cryptocurrency assets only:
1. If Binance connection is not configured, the `Portfolio` option remains manually editable.
2. If Binance connection is configured, the `Portfolio` option becomes read-only in Monitor.
3. The read-only value must be derived from Wallet holdings, using the same source of truth adopted by the Wallet feature.
4. If the crypto asset is present in Wallet holdings, Monitor must show it as included in portfolio.
5. If the crypto asset is absent from Wallet holdings, Monitor must show it as not in portfolio.
6. The UI must explain that the value is synced from Wallet/Binance and cannot be edited manually.
7. The rule must not affect non-crypto assets.

## Options considered
### Option A, hard lock with Wallet-derived state
- Lock the control whenever Binance is connected for crypto assets.
- Show the current value from Wallet holdings plus explanatory text.
- Best consistency and lowest ambiguity.
- Recommended.

### Option B, allow manual override with warning
- Preserves flexibility but keeps Monitor and Wallet potentially inconsistent.
- Contradicts the refinement intent.
- Not recommended.

## Recommendation
Adopt Option A. For cryptocurrency assets with Binance connected, the Monitor `Portfolio` option should be system-controlled and derived from Wallet holdings.

## Acceptance criteria
1. Given a cryptocurrency asset and no Binance connection configured, when the user opens Monitor, then the `Portfolio` option remains editable.
2. Given a cryptocurrency asset and a Binance connection configured, when the user opens Monitor, then the `Portfolio` option is read-only.
3. Given a cryptocurrency asset exists in Wallet holdings sourced from Binance, when Monitor loads, then the `Portfolio` state is shown as enabled/included.
4. Given a cryptocurrency asset does not exist in Wallet holdings sourced from Binance, when Monitor loads, then the `Portfolio` state is shown as disabled/not included.
5. Given the `Portfolio` option is locked by Binance sync, when the user inspects the control, then the UI explains that the value is synced from Wallet/Binance and cannot be changed manually.
6. Given an asset is not classified as cryptocurrency, when Monitor loads, then this Binance lock rule is not applied.
7. Given Binance is connected but holdings cannot be resolved, when Monitor loads a crypto asset, then the UI must not permit silent conflicting manual edits and must surface a deterministic fallback state/message defined by design and dev.
8. Given QA validates the Monitor with Binance connected and disconnected states, when comparing Monitor and Wallet, then the crypto portfolio state stays consistent with Wallet holdings in all tested scenarios.

## 5W2H
- What: Lock the Monitor portfolio option for crypto assets when Binance is connected.
- Why: Keep Monitor aligned with actual Wallet holdings.
- Who: Users managing crypto assets through Binance-connected Wallet data.
- Where: Monitor screen, `Portfolio` option for crypto assets.
- When: Whenever Binance connectivity and holdings are available for the signed-in user.
- How: Use Wallet/Binance holdings as source of truth and disable manual editing.
- How much: Small-to-medium UI and integration change with high consistency value.

## Prioritization
- Impact: 8
- Confidence: 8
- Ease: 6
- ICE: 384
