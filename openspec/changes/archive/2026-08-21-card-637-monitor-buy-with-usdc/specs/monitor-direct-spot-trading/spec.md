## ADDED Requirements

### Requirement: Purchase may use USDT or USDC as quote origin
On an eligible Monitor opportunity whose **strategy/signal symbol** is a Binance Spot pair with quote USDT, the authenticated user SHALL be able to choose the Spot free-balance asset used to fund a `BUY MARKET` order as either `USDT` or `USDC` (v1). Choosing an origin SHALL NOT change the strategy symbol, chart symbol, or opportunity identity. The submitted order SHALL use the Spot market symbol formed by the opportunity **base asset** plus the chosen origin (e.g. strategy `BTCUSDT` + origin `USDC` → order symbol `BTCUSDC`), and SHALL use `quoteOrderQty` denominated in that origin only. The system SHALL NOT silently convert between stables (no USDC→USDT hop).

#### Scenario: Buy with USDC while strategy is BASE/USDT
- **WHEN** the user opens Comprar on an eligible `BASEUSDT` opportunity, selects origin `USDC`, enters a positive amount within free Spot USDC, and the Spot symbol `BASEUSDC` is trading and accepts `MARKET` with `quoteOrderQty`
- **THEN** preview and submit SHALL target `BASEUSDC` with that USDC amount as `quoteOrderQty`
- **AND** the Monitor opportunity/strategy symbol SHALL remain `BASEUSDT`

#### Scenario: Buy with USDT unchanged
- **WHEN** the user selects origin `USDT` on an eligible `BASEUSDT` opportunity and confirms a valid amount
- **THEN** the order SHALL target `BASEUSDT` with `quoteOrderQty` in USDT as today

#### Scenario: Origin without tradable pair is blocked
- **WHEN** the chosen origin has no Spot symbol `BASE`+origin, the symbol is not TRADING, or it does not support `MARKET`/`quoteOrderQty`
- **THEN** the UI and backend SHALL reject before submission with an actionable reason
- **AND** SHALL NOT convert via another stable or submit on a different symbol

#### Scenario: Balance and validation follow chosen origin
- **WHEN** the user selects an origin
- **THEN** the free Spot balance shown, client validation, and server balance checks SHALL use that origin asset only
- **AND** amounts below min notional, above free balance, empty, or non-positive SHALL be rejected with an actionable message naming the origin

#### Scenario: Confirmation distinguishes strategy pair and order pair
- **WHEN** the user advances to purchase confirmation
- **THEN** the confirmation SHALL show strategy/signal pair (USDT), order symbol (`BASE`+origin), side Comprar, amount in the origin asset, free balance of that origin, indicative base quantity, market-price variation warning, and the final confirmation action

#### Scenario: Default and remembered origin
- **WHEN** the purchase surface opens
- **THEN** the default origin SHALL be `USDT` when that origin has a tradable pair (and preferably free balance); otherwise the first valid origin among `{USDT, USDC}`
- **AND** a session preference for the last chosen valid origin MAY be restored when still valid

### Requirement: Sale remains on the strategy USDT pair in this change
`Vender 100%` SHALL continue to liquidate free base balance on the strategy Spot symbol (`BASEUSDT`) and SHALL NOT offer quote-origin selection in this change.

#### Scenario: Sell ignores pay-with control
- **WHEN** the user selects `Vender 100%` on an eligible `BASEUSDT` opportunity
- **THEN** preview and submit SHALL use `BASEUSDT` / full free base quantity rules unchanged
- **AND** any pay-with control SHALL be hidden or inert for the sell side

## MODIFIED Requirements

### Requirement: Monitor exposes direct Spot trading for USDT pairs
The authenticated user SHALL be able to start a direct Binance Spot purchase or sale from an eligible crypto opportunity in the Monitor without navigating away from Cripto Farol. **Eligibility for showing trading actions** SHALL remain limited to opportunities whose **strategy/signal** Binance Spot symbol uses quote asset USDT. Purchase order submission MAY use quote origin USDT or USDC as specified in "Purchase may use USDT or USDC as quote origin". Credentials SHALL remain the Binance credentials linked to the authenticated user.

#### Scenario: Eligible USDT pair shows trading actions
- **WHEN** the Monitor renders a crypto opportunity whose Binance Spot strategy symbol is trading with quote asset USDT
- **THEN** the user SHALL be able to open a direct trading surface with `Comprar` and `Vender 100%` actions

#### Scenario: Ineligible symbol is blocked
- **WHEN** an opportunity is not a Binance Spot USDT strategy pair, is unavailable for Spot trading, or lacks a valid symbol mapping
- **THEN** the direct trading actions SHALL be unavailable with a clear reason and no order request SHALL be sent

### Requirement: Purchase uses a user-entered quote amount in the chosen origin
The direct purchase SHALL submit a Binance Spot `BUY MARKET` order using `quoteOrderQty` equal to the confirmed amount entered by the user in the **chosen origin asset** (`USDT` or `USDC`), on the Spot symbol `BASE`+origin.

#### Scenario: Confirm a valid purchase amount
- **WHEN** the user enters a positive amount in the chosen origin within the available free Spot balance of that origin and confirms the purchase
- **THEN** the backend SHALL submit `BUY MARKET` with that amount as `quoteOrderQty` on the resolved order symbol
- **AND** the order SHALL use the authenticated user's Binance credentials

#### Scenario: Reject invalid purchase amount
- **WHEN** the amount is empty, non-numeric, non-positive, above the free balance of the chosen origin, or below/above an applicable symbol notional filter for the order symbol
- **THEN** the UI and backend SHALL reject the request before order submission with an actionable message

### Requirement: Real orders require an explicit review and confirmation
The UI SHALL separate order setup from final confirmation and SHALL make the real, market-priced and potentially irreversible nature of the operation unambiguous. For purchases, confirmation SHALL distinguish the strategy/signal pair from the order pair when they differ.

#### Scenario: Review purchase before submission
- **WHEN** the user advances from a valid purchase amount
- **THEN** the confirmation SHALL show strategy pair, order symbol, `Comprar`, entered amount in the origin asset, available free balance of that origin, indicative asset quantity, market-price variation warning and the final confirmation action

#### Scenario: Review sale before submission
- **WHEN** the user advances to sell
- **THEN** the confirmation SHALL show strategy symbol, `Vender 100%`, refreshed free base-asset balance, indicative USDT value, possible residual/fee notice, market-price variation warning and the final confirmation action

#### Scenario: Cancel confirmation
- **WHEN** the user cancels or closes the confirmation
- **THEN** no order SHALL be submitted and the user SHALL return to a safe Monitor state
