## ADDED Requirements

### Requirement: Backend stores Monitor preferences per symbol
The backend MUST persist Monitor preferences per symbol.

Preferences include:
- `in_portfolio` (boolean)
- `card_mode` (enum: price | strategy)

#### Scenario: Persist preferences
- **WHEN** the client updates preferences for a symbol
- **THEN** the backend stores the preferences and returns them on subsequent reads

#### Scenario: Default preferences
- **WHEN** no preferences exist yet for a symbol
- **THEN** the backend returns defaults (in_portfolio=false, card_mode=price)

### Requirement: Backend exposes a preferences API
The backend MUST expose an API for reading and updating Monitor preferences.

#### Scenario: Read all preferences
- **WHEN** the client requests preferences
- **THEN** the backend returns the preferences keyed by symbol

#### Scenario: Update preferences
- **WHEN** the client updates preferences for a symbol
- **THEN** the backend validates input and persists the update
