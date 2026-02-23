## ADDED Requirements

### Requirement: Provide NASDAQ-100 ticker universe
The system MUST maintain a NASDAQ-100 ticker universe and expose it for selection in Combo Optimize.

#### Scenario: Fetch NASDAQ-100 ticker list
- **WHEN** the UI requests the NASDAQ-100 universe
- **THEN** the system returns an ordered list of tickers (e.g., `AAPL`, `MSFT`, `NVDA`, ...) suitable for a symbol picker

### Requirement: Universe is stable and versioned
The system MUST store the NASDAQ-100 ticker list in a versioned repository artifact so changes are reviewable.

#### Scenario: Update NASDAQ-100 list
- **WHEN** the NASDAQ-100 list needs updating
- **THEN** it is updated via a code change (PR/commit) rather than an ad-hoc runtime edit
