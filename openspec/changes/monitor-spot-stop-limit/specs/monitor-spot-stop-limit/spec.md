## ADDED Requirements

### Requirement: Monitor chart can place a Spot stop-limit protective order
When the Monitor chart is open for a long HOLD opportunity with a defined `stop_price`, the authenticated user MUST be able to place a Binance Spot `STOP_LOSS_LIMIT` sell order at that stop price for 100% of their free base-asset balance, after explicit confirmation.

#### Scenario: Place protective stop from chart
- **WHEN** the user confirms Proteger stop on a long HOLD chart with `stop_price` and free Spot balance of the base asset
- **THEN** the system MUST create a Spot `STOP_LOSS_LIMIT` `SELL` order using the user's Binance credentials with:
  - `stopPrice` equal to the opportunity `stop_price` (tick-rounded)
  - `limitPrice` equal to `stopPrice * (1 - 0.001)` (tick-rounded)
  - `quantity` equal to 100% of free base-asset balance (lot-rounded and meeting exchange filters)
  - a `newClientOrderId` prefixed with `cfstop_`

#### Scenario: Confirmation required before place
- **WHEN** the user activates Proteger stop
- **THEN** the UI MUST show a confirmation that includes asset, quantity, stop price, and limit price before calling the place API

### Requirement: Monitor chart can remove the app protective stop order
The authenticated user MUST be able to cancel the Cripto Farol protective stop order for the chart symbol without canceling unrelated Binance orders.

#### Scenario: Remove protective stop
- **WHEN** an open order with `clientOrderId` prefix `cfstop_` exists for the symbol and the user confirms Remover stop
- **THEN** the system MUST cancel that order via the user's Binance credentials and refresh status to unprotected

#### Scenario: Foreign orders are not canceled
- **WHEN** open orders exist on the symbol without the `cfstop_` prefix
- **THEN** Remover stop MUST NOT cancel those orders

### Requirement: Protective stop status is visible on the chart
Opening an eligible chart MUST load whether a protective stop already exists and expose place or remove accordingly.

#### Scenario: Status when unprotected
- **WHEN** the chart opens for a long HOLD opportunity with `stop_price` and no `cfstop_` open order
- **THEN** the UI MUST offer Proteger stop (enabled if free balance and trade-capable credentials exist)

#### Scenario: Status when protected
- **WHEN** a matching `cfstop_` open order exists
- **THEN** the UI MUST show Remover stop and a short summary of quantity, stop, and limit

### Requirement: Ineligible chart states disable protective actions
The system MUST disable protective place/remove with a clear reason when the opportunity or account cannot support Spot stop protection.

#### Scenario: Short or exited opportunity
- **WHEN** the opportunity is short or EXIT / already exited / missing `stop_price`
- **THEN** Proteger stop MUST be unavailable with a clear reason

#### Scenario: Missing free balance
- **WHEN** the user has no free Spot balance for the base asset
- **THEN** Proteger stop MUST be disabled with a clear reason

#### Scenario: Credentials cannot trade
- **WHEN** Binance credentials are missing or lack Spot trading permission
- **THEN** place MUST fail closed with an actionable message to configure a trade-capable key in Meu Perfil
