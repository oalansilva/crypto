# Wallet Screen Improvements (External Balances) — Specification

## Scope
This spec defines UX and API behavior to improve the Wallet screen at:
- UI route: `/external/balances`
- API endpoint: `GET /api/external/binance/spot/balances`

It builds on `openspec/specs/external-balances/spec.md`.

## Requirements (API)

### Requirement: Balances API MUST return an `as_of` timestamp
The system MUST include an `as_of` field in the response so the UI can display when the snapshot was taken.

#### Scenario: Timestamp present
- **WHEN** the user calls `GET /api/external/binance/spot/balances`
- **THEN** the response MUST include `as_of` representing the snapshot time
- **AND** `as_of` SHOULD be either an ISO-8601 UTC string or unix milliseconds

### Requirement: Balances API MUST support a dust threshold override
The balances API MUST allow the UI to control which rows are filtered out as dust.

- Query param: `min_usd` (optional float)
- Default: `0.02`
- Clamping: backend MUST clamp to a sane range (e.g., 0..1_000_000)

#### Scenario: Default behavior preserved
- **WHEN** the user calls the endpoint without `min_usd`
- **THEN** the system MUST behave as today (hide rows where `value_usd < 0.02`)

#### Scenario: Include dust
- **WHEN** the user calls the endpoint with `min_usd=0`
- **THEN** the system MUST include rows that were previously hidden due to dust filtering

## Requirements (UI)

### Requirement: Wallet UI MUST provide search by asset
- **WHEN** the user types into the search field
- **THEN** the list MUST filter to rows whose `asset` matches the query (case-insensitive)

### Requirement: Wallet UI MUST provide a locked-only filter
- **WHEN** the user enables "Locked only"
- **THEN** the list MUST only show rows where `locked > 0`

### Requirement: Wallet UI MUST be responsive
- **WHEN** the viewport is narrow (mobile)
- **THEN** the UI MUST present balances without requiring horizontal scrolling
- **AND** it SHOULD use a card list pattern with expandable details

### Requirement: Wallet UI MUST display summary information
- **WHEN** balances are loaded
- **THEN** the UI MUST display total USD value (from `total_usd`)
- **AND** it MUST display the snapshot time (from `as_of` or derived `lastUpdated`)

### Requirement: Wallet UI MUST clarify PnL limitations
- **WHEN** `pnl_usd` / `pnl_pct` are missing for some rows
- **THEN** the UI MUST NOT imply that total PnL is complete
- **AND** it SHOULD present a short note such as "PnL available for top positions only" (wording may vary)

## Non-Functional Requirements

- The system MUST remain read-only (no trading, no withdrawals).
- The UI MUST avoid aggressive polling; refresh is user-triggered.
