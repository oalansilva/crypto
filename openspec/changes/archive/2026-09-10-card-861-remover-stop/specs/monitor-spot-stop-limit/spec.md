## MODIFIED Requirements

### Requirement: Monitor chart can remove the protective Spot stop order
The authenticated user MUST be able to cancel an open Spot protective stop (`STOP_LOSS` / `STOP_LOSS_LIMIT` SELL) for the chart symbol without canceling unrelated non-stop Binance orders. Removal MUST require an explicit confirmation and MUST be reachable when Posicionado (HOLD) with an open stop. Removal MUST never submit a sale on its own.

#### Scenario: Remove app-managed protective stop
- **WHEN** an open order with `clientOrderId` prefix `cfstop_` exists for the symbol and the user confirms Remover stop
- **THEN** the system MUST cancel that order via the user's Binance credentials and refresh status to unprotected

#### Scenario: Remove external Spot stop
- **WHEN** an open Spot `STOP_LOSS` / `STOP_LOSS_LIMIT` `SELL` exists without the `cfstop_` prefix (e.g. created on Binance Web) and the user confirms Remover stop
- **THEN** the system MUST cancel that stop order and MUST NOT cancel non-stop orders on the symbol

#### Scenario: Non-stop foreign orders are not canceled
- **WHEN** open orders exist on the symbol that are not Spot stop SELL protective orders
- **THEN** Remover stop MUST NOT cancel those orders

#### Scenario: Removal requires explicit confirmation
- **WHEN** the user activates Remover stop on the chart
- **THEN** the UI MUST show a confirmation identifying the stop (quantity, stop price, limit price, origin — app labeled explicitly e.g. "criada no app (Farol)", externa keeps its label) before calling the cancel API
- **AND** opening the confirmation MUST move focus to it (focusable container `tabindex="-1"` or primary button) with an adequate accessible signal (`role="group"` + `aria-label`, trigger `aria-expanded`/`aria-controls`); closing it (Cancelar or confirmar) MUST return focus to the trigger (or to the removal status when the trigger is gone)
- **AND** cancelling the confirmation MUST NOT cancel any order

#### Scenario: Removal reachable when Posicionado with open stop
- **WHEN** the opportunity is Posicionado (HOLD, long, `stop_price` defined) and an open Spot stop SELL exists for the symbol
- **THEN** the chart MUST offer Remover stop with confirmation

#### Scenario: Removal never sells alone
- **WHEN** the user confirms Remover stop
- **THEN** the system MUST cancel only the stop order and MUST NOT submit any buy or sell order

#### Scenario: Removal not offered without position or stop
- **WHEN** there is no HOLD position or no open Spot stop SELL for the symbol
- **THEN** the UI MUST NOT offer Remover stop
