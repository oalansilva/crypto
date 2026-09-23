## ADDED Requirements

### Requirement: The entry hurdle uses the real maker fee with a conservative fallback

`_fee_terms` SHALL return the account's real **maker** commission rate per leg together with the BNB-burn state, read through the signed Binance client (`GET /api/v3/account` → `commissionRates.maker`; `GET /sapi/v1/bnbBurn` → `spotBNBBurn`) and cached per user. On any failure of those calls it SHALL return the conservative fallback `(10 bp, False)`. The entry hurdle formula SHALL remain `entry_hurdle_bp = 2 × fee_bp + spread_bp`: with the real maker rate the hurdle SHALL land in the **12–16 bp** band, and with the fallback it SHALL stay near 20 bp. The fee actually in use SHALL be visible in the scalp status output. The fee lookup SHALL NOT issue a signed request on every cycle.

#### Scenario: Maker rate is read from the account

- **WHEN** the scalp cycle resolves the fee terms for a user with Spot credentials
- **THEN** `_fee_terms` SHALL return the maker rate from `commissionRates.maker` and the BNB-burn state from `spotBNBBurn`
- **AND** the returned tuple SHALL keep the `(fee_bp, bnb_fee_active)` shape

#### Scenario: Hurdle reflects the maker cost

- **WHEN** the real maker rate applies to a cycle with a given spread
- **THEN** `entry_hurdle_bp` SHALL equal `2 × fee_bp + spread_bp` and land in the 12–16 bp band
- **AND** the status output SHALL show the fee rate in use

#### Scenario: Fee API failure falls back conservatively

- **WHEN** the account or BNB-burn call fails or times out
- **THEN** `_fee_terms` SHALL return `(10 bp, False)`
- **AND** the hurdle SHALL stay near 20 bp instead of assuming a cheaper maker rate

#### Scenario: No extra signed call per cycle

- **WHEN** many cycles run for the same user within the cache window
- **THEN** the fee lookup SHALL be served from the per-user cache
- **AND** the number of signed fee requests SHALL NOT grow with the cycle count
