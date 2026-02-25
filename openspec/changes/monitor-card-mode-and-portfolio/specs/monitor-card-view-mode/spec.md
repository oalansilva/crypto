## ADDED Requirements

### Requirement: Per-symbol card mode can be toggled
The system MUST allow the user to toggle a Monitor card between Price mode and Strategy mode.

#### Scenario: Toggle to Price mode
- **WHEN** the user toggles a symbol card to Price mode
- **THEN** the UI shows price-oriented content for that symbol (candles + basic price metrics)

#### Scenario: Toggle to Strategy mode
- **WHEN** the user toggles a symbol card to Strategy mode
- **THEN** the UI shows strategy-oriented content for that symbol (current strategy metrics/status)

### Requirement: Card mode is persisted in the backend
The system MUST persist the per-symbol card mode preference.

#### Scenario: Preference persists across reload
- **WHEN** the user sets a symbol card mode and reloads the page
- **THEN** the symbol card renders using the last persisted mode

#### Scenario: Preference persists across devices
- **WHEN** the user sets a symbol card mode on one device
- **THEN** another device sees the same card mode for the symbol after fetching preferences
