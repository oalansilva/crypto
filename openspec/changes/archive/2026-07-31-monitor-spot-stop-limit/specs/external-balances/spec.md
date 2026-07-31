## MODIFIED Requirements

### Requirement: Integration MUST be read-only
The Wallet / external-balances integration MUST remain read-only for balances, PnL, and trade history. The system MUST NOT withdraw funds.

As a scoped exception for the Monitor protective-stop capability, the authenticated Monitor Spot stop-limit endpoints MAY place or cancel only Spot `STOP_LOSS_LIMIT` sell orders with `clientOrderId` prefix `cfstop_`, using the logged-in user's credentials, after explicit user confirmation in the Monitor chart UI.

#### Scenario: Read-only enforcement for wallet
- **WHEN** the system serves Wallet / external balances flows
- **THEN** it MUST only call read-only Binance endpoints for those flows

#### Scenario: Scoped Monitor stop-limit exception
- **WHEN** the authenticated user confirms Proteger stop or Remover stop on the Monitor chart
- **THEN** the system MAY call Binance Spot order place/cancel endpoints solely for the protective `cfstop_` stop-limit flow
- **AND** it MUST NOT withdraw or place unrelated order types through this exception
