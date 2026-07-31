## ADDED Requirements

### Requirement: Wallet MUST list Spot stablecoin balances with USD value
The Wallet balances snapshot MUST include Spot balances for supported USD stables (at least `USDT` and `USDC`) whenever the account has `total > 0` for that asset. The system MUST value those assets with a stable USD reference (`price_usdt` of `1.0` unless a more accurate ticker is available) so `value_usd` is never omitted solely because no self-pair ticker exists.

#### Scenario: USDT balance is listed
- **WHEN** the authenticated user has Spot `USDT` with `total > 0`
- **THEN** the balances response MUST include a row with `asset=USDT`
- **AND** `price_usdt` MUST be `1.0` (or an equivalent stable ticker)
- **AND** `value_usd` MUST equal `total * price_usdt`
- **AND** that `value_usd` MUST be included in `total_usd`

#### Scenario: USDC balance is listed
- **WHEN** the authenticated user has Spot `USDC` with `total > 0`
- **THEN** the balances response MUST include a row with `asset=USDC`
- **AND** `price_usdt` MUST be `1.0` (or an equivalent stable ticker)
- **AND** `value_usd` MUST equal `total * price_usdt`
- **AND** that `value_usd` MUST be included in `total_usd`

#### Scenario: Stable listing is independent of avg-cost trade lookup
- **WHEN** a stable asset appears in the Spot snapshot
- **THEN** the system MUST NOT omit the row because avg-cost / trade-history lookup was skipped
- **AND** `avg_cost_usdt` for known stables MAY be `1.0` (PnL ≈ 0) without blocking display

### Requirement: Wallet UI MUST send dust threshold to the balances API
The Carteira UI MUST pass the user-selected dust threshold as `min_usd` on `GET /api/external/binance/spot/balances` so server-side filtering matches the control.

#### Scenario: Default threshold is forwarded
- **WHEN** the user opens Carteira with the default dust threshold
- **THEN** the UI MUST request balances with `min_usd` equal to that default

#### Scenario: Include-dust control reaches the API
- **WHEN** the user sets dust threshold to `0`
- **THEN** the UI MUST request balances with `min_usd=0`
- **AND** previously dust-filtered rows that the API returns MUST become visible

#### Scenario: Material stables remain visible under default dust
- **WHEN** USDT or USDC has `value_usd` at or above the active `min_usd`
- **THEN** the Carteira list MUST show the stable row
- **AND** the visible total MUST include its `value_usd`

## MODIFIED Requirements

### Requirement: Wallet API MUST support dust threshold override
The Wallet balances endpoint MUST accept a query param `min_usd` (optional float) to override dust filtering.

Dust filtering MUST NOT drop a supported stable (`USDT`, `USDC`, and other assets treated as USD stables for display pricing) that has `total > 0` when its computed `value_usd` is at or above the active threshold. Missing ticker data MUST NOT force-omit those stables: the endpoint MUST fall back to the stable USD reference price instead of skipping the row.

#### Scenario: Default dust behavior
- **WHEN** `min_usd` is not provided
- **THEN** the endpoint MUST behave with the default dust threshold (currently 0.02)

#### Scenario: Include dust
- **WHEN** `min_usd=0`
- **THEN** the endpoint MUST include rows that would otherwise be filtered as dust

#### Scenario: Stable without self-pair ticker is still valued
- **WHEN** a supported stable has Spot balance and no self-pair ticker exists in the price map
- **THEN** the endpoint MUST still return the row using the stable USD reference price
- **AND** MUST NOT skip the row with `value_usd=null`
