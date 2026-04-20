## Why

On Monitor, the Portfolio option should stop being user-editable for cryptocurrency assets when the user has a Binance connection configured. In that scenario, the portfolio source of truth must come from the wallet/integration layer so the monitored crypto set reflects the user’s actual purchased assets instead of a manual selection that can drift from Binance reality.

This reduces data inconsistency, avoids misleading monitoring setups, and makes the crypto workflow align with the existing wallet integration intent.

## User Story

As a user who connected Binance,
I want the Portfolio selection on Monitor for cryptocurrency assets to be derived automatically from my wallet holdings,
so that Monitor reflects my real crypto positions and I cannot accidentally configure a conflicting manual portfolio.

## Scope In

- Detect when the user has a valid Binance connection configured.
- Apply the rule only to assets classified as cryptocurrency.
- Disable manual editing of the Portfolio option on Monitor for those crypto assets.
- Derive the Monitor portfolio state from wallet/holdings data sourced by the Binance-connected flow.
- Show the resulting state in the UI with clear non-editable behavior.
- Preserve existing editable behavior for non-cryptocurrency asset types.
- Define empty-holdings behavior for connected Binance users so the UI remains deterministic.

## Scope Out

- Changing how Binance credentials are configured.
- Reworking the wallet integration architecture beyond the data needed for Monitor.
- Applying the same locking rule to non-crypto assets.
- Portfolio rebalancing, trading execution, or holdings reconciliation beyond display/selection behavior.
- Broader redesign of the Monitor screen.

## Product Rules

1. If the user has Binance connected and the asset type is cryptocurrency, Monitor Portfolio must be read-only.
2. In that case, the Portfolio content must come from wallet holdings data, not from manual Monitor selection.
3. If the user does not have Binance connected, current manual behavior may remain available.
4. If the asset type is not cryptocurrency, this rule does not apply.
5. The UI must communicate why the control is disabled.
6. If Binance is connected but there are no eligible crypto holdings, Monitor must show a defined empty state instead of allowing manual override.

## UX Notes

- Keep the current Monitor interaction as unchanged as possible outside the protected crypto case.
- Use explicit disabled-state messaging, for example that portfolio is synced from Binance wallet for crypto assets.
- Avoid ambiguous states where a disabled control still looks manually configurable.
- If this touches visible UI behavior, DESIGN should provide the prototype before any approval gate beyond PO.

## Dependencies

- Reliable detection of Binance connection status.
- Reliable holdings data from the wallet/Binance integration.
- Asset taxonomy capable of distinguishing cryptocurrency from other asset types.
- Frontend support for disabled/read-only Monitor Portfolio state with explanatory copy.

## Risks

- Holdings source may be stale or unavailable, causing Monitor to appear empty or inconsistent.
- Asset classification gaps could apply the rule to the wrong asset type.
- Users may be confused if the control is disabled without clear explanation.
- Existing manual portfolio assumptions in frontend/backend may require fallback handling.

## Open Questions

- Which wallet dataset is the canonical source for “purchased assets” when Binance is connected?
- What is the precise empty state when Binance is connected but wallet returns no crypto holdings?
- Should Monitor refresh portfolio automatically on holdings refresh, on page load only, or both?

## Acceptance Criteria

### Scenario 1, Binance connected for cryptocurrency
- Given the user has a Binance connection configured
- And the selected asset type is cryptocurrency
- When the user opens Monitor
- Then the Portfolio option is displayed as non-editable
- And the portfolio content is populated from wallet/Binance holdings
- And the UI explains that the portfolio is synced automatically

### Scenario 2, manual override blocked
- Given the user has a Binance connection configured
- And the selected asset type is cryptocurrency
- When the user tries to change the Portfolio option
- Then Monitor does not allow manual changes
- And no conflicting manual portfolio state is persisted

### Scenario 3, non-crypto unaffected
- Given the user has a Binance connection configured
- And the selected asset type is not cryptocurrency
- When the user opens Monitor
- Then the Binance lock rule is not applied
- And existing behavior remains available

### Scenario 4, no Binance connection
- Given the user does not have a Binance connection configured
- When the user opens Monitor
- Then the existing manual Portfolio behavior remains available

### Scenario 5, connected Binance with no crypto holdings
- Given the user has a Binance connection configured
- And the selected asset type is cryptocurrency
- And the wallet returns no eligible crypto holdings
- When the user opens Monitor
- Then Monitor shows a defined empty state
- And the Portfolio option remains non-editable
- And the UI explains that there are no synced crypto assets available

## 5W2H

- What: Lock Monitor Portfolio editing for crypto when Binance is connected and sync from wallet holdings.
- Why: Prevent divergence between Monitor selection and real Binance-held assets.
- Who: Users monitoring cryptocurrency positions with Binance integration.
- Where: Monitor screen, specifically the Portfolio option/state.
- When: Whenever Monitor is used under the Binance-connected crypto scenario.
- How: Detect Binance connection + crypto asset type, fetch holdings, render read-only portfolio state.
- How much: Small-to-medium scoped behavior change with dependency on wallet integration reliability.

## Recommendation

Proceed as a change scoped to Monitor behavior, with DESIGN handoff if the disabled/read-only state changes visible UI interaction. The implementation should explicitly anchor to wallet holdings as the source of truth for crypto assets under Binance connection.
