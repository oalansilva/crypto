# monitor-portfolio-watchlist Specification

## Purpose
TBD - created by archiving change monitor-card-mode-and-portfolio. Update Purpose after archive.
## Requirements
### Requirement: Favorites symbols can be marked as In Portfolio
The system MUST allow the user to mark a Favorites symbol as "In Portfolio".

#### Scenario: Mark symbol as In Portfolio
- **WHEN** the user toggles In Portfolio ON for a symbol
- **THEN** the backend persists the preference for that symbol

#### Scenario: Unmark symbol as In Portfolio
- **WHEN** the user toggles In Portfolio OFF for a symbol
- **THEN** the backend persists the preference for that symbol

### Requirement: Monitor defaults to In Portfolio symbols
The system MUST default the Monitor card list to symbols marked as In Portfolio.

#### Scenario: Monitor loads with In Portfolio filter enabled
- **WHEN** the user opens the Monitor screen
- **THEN** the visible list contains only symbols marked In Portfolio

#### Scenario: User can view all favorites symbols
- **WHEN** the user switches the filter from In Portfolio to All
- **THEN** the visible list contains all favorites symbols

