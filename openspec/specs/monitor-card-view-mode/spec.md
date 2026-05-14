# monitor-card-view-mode Specification

## Purpose
TBD - created by archiving change monitor-card-mode-and-portfolio. Update Purpose after archive.
## Requirements
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

### Requirement: Chart modal opens with decision context visible
The Monitor chart modal SHALL expose signal context, risk/stop, and signal history in the default opening path for a Monitor opportunity.

#### Scenario: Default chart modal shows operational context
- **WHEN** a user opens the detailed chart from a Monitor opportunity
- **THEN** the modal SHALL show signal context without requiring a manual layout switch
- **AND** the modal SHALL show risk/stop information when available
- **AND** the modal SHALL show signal history when the opportunity payload includes it

