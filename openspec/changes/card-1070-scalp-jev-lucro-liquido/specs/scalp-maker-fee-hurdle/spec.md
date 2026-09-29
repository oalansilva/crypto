## MODIFIED Requirements

### Requirement: The entry hurdle uses the real maker fee with a conservative fallback

`_fee_terms` SHALL return the account's real **maker** commission rate per leg together with whether the BNB discount is in force, read through the signed Binance client (`GET /api/v3/account/commission` for BTCUSDT, `GET /sapi/v1/bnbBurn` → `spotBNBBurn`, and free Spot BNB). On any failure of those calls it SHALL return the conservative fallback `(10 bp, False)`. When discount is enabled for the account and the symbol, `spotBNBBurn` is on, and free BNB is enough to cover the fee of the 10-dollar clip, `fee_bp` SHALL be that maker rate **after one BNB discount** and SHALL NOT apply the discount a second time. When that balance is missing, `fee_bp` SHALL stay the undiscounted maker rate. The entry hurdle formula SHALL remain `entry_hurdle_bp = 2 × fee_bp + spread_bp`. The fee actually in use SHALL be visible in the scalp status output and SHALL match the commission charged on fills. The fee lookup SHALL NOT issue a signed request on every cycle.

#### Scenario: Maker rate is read from the account

- **WHEN** the scalp cycle resolves the fee terms for a user with Spot credentials
- **THEN** `_fee_terms` SHALL return the maker rate from the symbol commission endpoint and the BNB-burn state from `spotBNBBurn`
- **AND** the returned tuple SHALL keep the `(fee_bp, bnb_fee_active)` shape

#### Scenario: Discount enters when BNB covers the fee

- **WHEN** BNB discount is enabled, `spotBNBBurn` is on, and free BNB covers the clip fee
- **THEN** `fee_bp` SHALL be the maker rate after one BNB discount
- **AND** `entry_hurdle_bp` SHALL equal `2 × fee_bp + spread_bp`
- **AND** the status output SHALL show that discounted rate

#### Scenario: Hurdle reflects the maker cost without discount

- **WHEN** the real maker rate applies and BNB does not cover the fee
- **THEN** `entry_hurdle_bp` SHALL equal `2 ×` the undiscounted `fee_bp + spread_bp`
- **AND** the status output SHALL show the undiscounted fee rate in use

#### Scenario: Fee API failure falls back conservatively

- **WHEN** the account, commission, BNB-burn or BNB-balance call fails or times out
- **THEN** `_fee_terms` SHALL return `(10 bp, False)`
- **AND** the hurdle SHALL stay near 20 bp instead of assuming a cheaper maker rate

#### Scenario: No extra signed call per cycle

- **WHEN** many cycles run for the same user within the cache window
- **THEN** the fee lookup SHALL be served from the per-user cache
- **AND** the number of signed fee requests SHALL NOT grow with the cycle count

#### Scenario: Fill commission matches the rate on screen

- **WHEN** a scalp fill reports its commission
- **THEN** the fee in use on the screen and in the hurdle SHALL match that charged rate
- **AND** a mismatch SHALL be visible in the diagnosis rather than silent
