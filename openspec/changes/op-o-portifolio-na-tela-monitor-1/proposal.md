# Proposal: Opção Portifolio na tela Monitor - 1

## User Story

As a crypto user with Binance wallet integration, when I use the Monitor screen, I want the Portfolio option to be defined automatically from my wallet instead of manually edited, so that the Monitor reflects my real crypto holdings consistently.

## Value Proposition

**Current state:** The Monitor allows manual Portfolio selection even when crypto holdings can already be inferred from the user's Binance-connected wallet.

**Target state:** For crypto assets with Binance configured, Portfolio becomes a derived value from Wallet data and is no longer manually editable.

**Benefits:**
- Prevents divergence between wallet holdings and Monitor configuration
- Reduces manual setup for Binance-connected crypto users
- Makes the Monitor behavior more trustworthy and easier to understand

## Scope In

- Apply the rule only on the Monitor screen
- Apply the rule only for assets classified as cryptocurrency
- Disable manual Portfolio editing when the user has Binance configured
- Derive the displayed Portfolio value from the user's Wallet data
- Show helper text explaining that Portfolio is defined automatically by the wallet
- Preserve current behavior for non-crypto assets and for users without Binance configured

## Scope Out

- Changing Portfolio behavior for non-crypto assets
- Redesigning Wallet synchronization flows
- Supporting manual override while Binance remains configured
- Expanding the rule beyond Monitor
- Defining new Binance account scopes beyond the existing integration contract

## Dependencies

1. Wallet integration must expose the crypto holdings used as the canonical source for Portfolio
2. Asset type classification must reliably distinguish cryptocurrency from other asset types
3. Backend must enforce the same restriction to avoid manual bypass outside the UI

## Risks

1. Ambiguity around what counts as "Binance configured" if integration state is not explicit
2. Wallet data may be empty or stale, requiring deterministic fallback behavior from implementation
3. UI-only blocking would leave the rule vulnerable to API bypass
4. Missing explanatory text could make the blocked field look like an error

## Product Decisions

1. The lock applies when the user has Binance configured for the wallet integration
2. The Portfolio value shown in Monitor must come from Wallet-held crypto assets in that scenario
3. Non-crypto assets keep the current editable behavior
4. The UX must explain why the field is locked and where the value comes from

## Acceptance Criteria

1. Given a cryptocurrency asset and a user with Binance configured, when the Monitor form is shown, then Portfolio is not editable
2. Given a cryptocurrency asset and a user with Binance configured, when Monitor data loads, then the Portfolio value is populated from Wallet data
3. Given a non-crypto asset, when the Monitor form is shown, then Portfolio remains editable
4. Given a crypto asset without Binance configured, when the Monitor form is shown, then Portfolio remains editable
5. Given a locked Portfolio field, when the UI renders it, then helper text explains that the value is defined automatically by the user's wallet
6. Given a manual update attempt for a locked crypto Portfolio, when the request reaches the backend, then the change is rejected

## UX Note

This is a UI-affecting change. DESIGN should provide a prototype for the locked state, helper text, and normal editable contrast before any Approval-stage advancement.
