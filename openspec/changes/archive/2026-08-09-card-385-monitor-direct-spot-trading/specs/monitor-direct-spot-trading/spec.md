## ADDED Requirements

### Requirement: Monitor exposes direct Spot trading for USDT pairs
The authenticated user SHALL be able to start a direct Binance Spot purchase or sale from an eligible crypto opportunity in the Monitor without navigating away from Cripto Farol. The action SHALL be limited to symbols whose quote asset is USDT and SHALL use only the Binance credentials linked to the authenticated user.

#### Scenario: Eligible USDT pair shows trading actions
- **WHEN** the Monitor renders a crypto opportunity whose Binance Spot symbol is trading with quote asset USDT
- **THEN** the user SHALL be able to open a direct trading surface with `Comprar` and `Vender 100%` actions

#### Scenario: Ineligible symbol is blocked
- **WHEN** an opportunity is not a Binance Spot USDT pair, is unavailable for Spot trading, or lacks a valid symbol mapping
- **THEN** the direct trading actions SHALL be unavailable with a clear reason and no order request SHALL be sent

### Requirement: Purchase uses a user-entered USDT amount
The direct purchase SHALL submit a Binance Spot `BUY MARKET` order using `quoteOrderQty` equal to the confirmed USDT amount entered by the user.

#### Scenario: Confirm a valid purchase amount
- **WHEN** the user enters a positive USDT amount within the available free USDT balance and confirms the purchase
- **THEN** the backend SHALL submit `BUY MARKET` with that amount as `quoteOrderQty`
- **AND** the order SHALL use the authenticated user's Binance credentials

#### Scenario: Reject invalid purchase amount
- **WHEN** the USDT amount is empty, non-numeric, non-positive, above the free USDT balance, or below/above an applicable symbol notional filter
- **THEN** the UI and backend SHALL reject the request before order submission with an actionable message

### Requirement: Sale liquidates the full free base-asset balance at market
The direct sale SHALL submit a Binance Spot `SELL MARKET` order for 100% of the authenticated user's current `free` balance of the symbol's base asset, reduced only by deterministic downward rounding required by the applicable market lot-size filters.

#### Scenario: Confirm full-balance sale
- **WHEN** the user confirms `Vender 100%` for an eligible symbol with a valid free base-asset balance
- **THEN** the backend SHALL refresh the account balance immediately before submission
- **AND** SHALL submit `SELL MARKET` with the maximum valid quantity not exceeding 100% of that refreshed free balance

#### Scenario: Rounded residual remains
- **WHEN** the free balance cannot be submitted exactly because of `MARKET_LOT_SIZE` or `LOT_SIZE` step precision
- **THEN** the backend SHALL round quantity down without exceeding the free balance
- **AND** the confirmation/result SHALL explain that a non-tradable residual may remain

#### Scenario: Sale fails minimum filters
- **WHEN** the maximum valid free-balance quantity does not meet the applicable minimum quantity or notional rule
- **THEN** the backend SHALL reject the sale before submission and the UI SHALL explain that the balance is below Binance's minimum

### Requirement: Real orders require an explicit review and confirmation
The UI SHALL separate order setup from final confirmation and SHALL make the real, market-priced and potentially irreversible nature of the operation unambiguous.

#### Scenario: Review purchase before submission
- **WHEN** the user advances from a valid purchase amount
- **THEN** the confirmation SHALL show symbol, `Comprar`, entered USDT amount, available USDT balance, indicative asset quantity, market-price variation warning and the final confirmation action

#### Scenario: Review sale before submission
- **WHEN** the user advances to sell
- **THEN** the confirmation SHALL show symbol, `Vender 100%`, refreshed free base-asset balance, indicative USDT value, possible residual/fee notice, market-price variation warning and the final confirmation action

#### Scenario: Cancel confirmation
- **WHEN** the user cancels or closes the confirmation
- **THEN** no order SHALL be submitted and the user SHALL return to a safe Monitor state

### Requirement: Direct orders validate exchange rules and fail closed
The backend SHALL validate the current symbol status, supported order type, quote/base assets, balances and applicable `MARKET_LOT_SIZE`, `LOT_SIZE`, `MIN_NOTIONAL` and `NOTIONAL` rules before submitting an order. Credentials SHALL require Spot Trade permission and SHALL never fall back to system-wide exchange secrets.

#### Scenario: Missing or read-only credentials
- **WHEN** Binance credentials are missing, invalid or lack Spot Trade permission
- **THEN** the request SHALL fail closed with guidance to configure a trade-capable key in Meu Perfil
- **AND** the guidance SHALL never request withdraw permission

#### Scenario: Symbol or balance changes before confirmation completes
- **WHEN** the symbol becomes unavailable or the relevant free balance changes between setup and final submission
- **THEN** the backend SHALL use current Binance data, reject stale invalid values, and return the updated reason without submitting an unsafe order

#### Scenario: Sensitive data is protected
- **WHEN** any direct order succeeds or fails
- **THEN** API keys, secrets, signatures, raw signed URLs and private Binance payloads SHALL NOT be returned to the frontend or written to user-visible logs/errors

### Requirement: Duplicate submissions and unknown outcomes are reconciled safely
Each user-confirmed order SHALL carry a server-controlled idempotency key mapped to a deterministic Binance `newClientOrderId`. Repeated requests for the same confirmation SHALL return the existing outcome and SHALL NOT create a second economic order.

#### Scenario: Repeated confirmation request
- **WHEN** the same authenticated user repeats a request with the same idempotency key because of double click, retry or delayed response
- **THEN** the backend SHALL return the existing request/order state without submitting another Binance order

#### Scenario: Binance timeout leaves status unknown
- **WHEN** Binance returns a timeout or transport/server failure for which execution status may be unknown
- **THEN** the backend SHALL query the order by the deterministic client order id before allowing any resubmission
- **AND** the UI SHALL show `Verificando execução` rather than success or failure until a terminal state is known

#### Scenario: Unknown state cannot be resolved immediately
- **WHEN** reconciliation cannot determine whether the order executed
- **THEN** the request SHALL remain blocked from resubmission while the outcome is being confirmed and the UI SHALL instruct the user to wait/recheck without creating another order
- **AND** reconciliation SHALL be bounded: after the configured grace period plus a bounded strike count of repeated not-found or non-auth query errors, the record SHALL transition to a terminal state (`rejected` with `BINANCE_ORDER_NOT_FOUND` or `BINANCE_QUERY_FAILED`) so the per-symbol lock is never held indefinitely
- **AND** before a terminal not-found rejection is committed, the backend SHALL run one final live order query so a fill that only became visible late is still recorded as executed
- **AND** terminal state transitions SHALL be conditional on the current non-terminal state so concurrent reconciliations never regress a committed terminal result
- **AND** the terminal UI SHALL show an honest outcome (e.g. `Resultado não confirmado` with balance-check guidance) instead of asserting non-execution when the execution status was unknown

### Requirement: Order results and balances are reconciled in the Monitor
The UI SHALL present a safe, user-readable outcome and refresh relevant balances after a terminal Binance response without exposing internal identifiers unnecessarily.

#### Scenario: Order fills completely
- **WHEN** Binance returns a filled order
- **THEN** the UI SHALL show side, symbol, executed base quantity, executed quote amount and average execution price
- **AND** SHALL refresh Monitor/portfolio balances

#### Scenario: Order is partially filled
- **WHEN** Binance returns a partial execution state or fills that do not cover the requested economic amount
- **THEN** the UI SHALL distinguish the executed and remaining amounts and SHALL refresh balances before offering another action

#### Scenario: Order is rejected
- **WHEN** Binance rejects an order
- **THEN** the UI SHALL show a sanitized actionable reason, preserve the Monitor context and permit a corrected new request only when no unknown prior execution exists

### Requirement: Direct trading surface is accessible and responsive
The direct trading flow SHALL preserve the existing Monitor shell and design tokens, work by keyboard and touch, expose semantic labels and focus management, and remain usable on desktop and mobile without horizontal page scrolling.

#### Scenario: Keyboard confirmation flow
- **WHEN** a keyboard user opens direct trading, chooses a side, enters/reviews values and closes or confirms
- **THEN** focus SHALL move predictably, the modal/drawer SHALL have an accessible name, controls SHALL have programmatic labels, and focus SHALL return to the trigger on close

#### Scenario: Mobile trading flow
- **WHEN** the direct trading surface is used at a mobile viewport
- **THEN** content, balances, warnings and confirmation controls SHALL remain visible and touch-usable without clipping or horizontal overflow

