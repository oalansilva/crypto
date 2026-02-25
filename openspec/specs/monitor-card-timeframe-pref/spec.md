# monitor-card-timeframe-pref Specification

## Purpose
TBD - created by archiving change monitor-unified-cards-timeframe-prefs. Update Purpose after archive.
## Requirements
### Requirement: Per-symbol price timeframe preference is persisted
The system MUST allow storing a per-symbol price timeframe preference used by the Monitor card in Price mode.

#### Scenario: Default timeframe is 1d
- **WHEN** no preference exists for a symbol
- **THEN** the system uses `price_timeframe=1d` for that symbol

#### Scenario: User sets a new timeframe
- **WHEN** the user selects a timeframe for a symbol in Price mode
- **THEN** the backend persists the `price_timeframe` for that symbol

#### Scenario: Preference persists across reload
- **WHEN** the user reloads the Monitor screen
- **THEN** the symbol card uses the last persisted `price_timeframe`

### Requirement: Timeframe options depend on asset type
The system MUST enforce timeframe constraints per asset type.

#### Scenario: Crypto supports intraday
- **WHEN** the symbol is Crypto
- **THEN** allowed timeframes include {15m, 1h, 4h, 1d}

#### Scenario: Stocks are 1d only
- **WHEN** the symbol is Stocks
- **THEN** allowed timeframes include {1d} only

