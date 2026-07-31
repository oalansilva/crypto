# monitor-spot-stop-limit Specification

## Purpose
Protective Spot stop-limit orders on the Monitor chart for long HOLD opportunities with a defined stop price.

## Requirements
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

### Requirement: Monitor chart can remove the protective Spot stop order
The authenticated user MUST be able to cancel an open Spot protective stop (`STOP_LOSS` / `STOP_LOSS_LIMIT` SELL) for the chart symbol without canceling unrelated non-stop Binance orders.

#### Scenario: Remove app-managed protective stop
- **WHEN** an open order with `clientOrderId` prefix `cfstop_` exists for the symbol and the user confirms Remover stop
- **THEN** the system MUST cancel that order via the user's Binance credentials and refresh status to unprotected

#### Scenario: Remove external Spot stop
- **WHEN** an open Spot `STOP_LOSS` / `STOP_LOSS_LIMIT` `SELL` exists without the `cfstop_` prefix (e.g. created on Binance Web) and the user confirms Remover stop
- **THEN** the system MUST cancel that stop order and MUST NOT cancel non-stop orders on the symbol

#### Scenario: Non-stop foreign orders are not canceled
- **WHEN** open orders exist on the symbol that are not Spot stop SELL protective orders
- **THEN** Remover stop MUST NOT cancel those orders

### Requirement: Protective stop status is visible on the chart
Opening an eligible chart MUST load whether a protective stop already exists and expose place or remove accordingly.

#### Scenario: Status when unprotected
- **WHEN** the chart opens for a long HOLD opportunity with `stop_price` and no open Spot stop SELL (`cfstop_` or external)
- **THEN** the UI MUST offer Proteger stop (enabled if free balance and trade-capable credentials exist)

#### Scenario: Status when protected by app
- **WHEN** a matching `cfstop_` open order exists
- **THEN** the UI MUST show Remover stop and a short summary of quantity, stop, and limit

#### Scenario: Status when protected by external Binance stop
- **WHEN** an open Spot `STOP_LOSS` / `STOP_LOSS_LIMIT` `SELL` exists without `cfstop_` prefix
- **THEN** the UI MUST treat the position as already protected, MUST NOT offer Proteger stop, MUST show Remover stop with a short summary, and MUST indicate the stop was created outside the app

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
