## ADDED Requirements

### Requirement: Users can like Monitor strategies
The system SHALL allow an authenticated user to persist whether a Monitor opportunity strategy is liked by that user.

#### Scenario: User likes a Monitor strategy
- **WHEN** an authenticated user sets a Monitor strategy preference for a favorite strategy ID with `liked=true`
- **THEN** the system persists the liked state for that user and favorite strategy ID

#### Scenario: User unlikes a Monitor strategy
- **WHEN** an authenticated user sets a Monitor strategy preference for a favorite strategy ID with `liked=false`
- **THEN** the system persists the unliked state for that user and favorite strategy ID

#### Scenario: User lists liked Monitor strategies
- **WHEN** an authenticated user requests Monitor strategy preferences
- **THEN** the system returns only that user's persisted liked strategy IDs and liked states

### Requirement: Monitor favorite filter uses liked strategies
The Monitor UI SHALL use user-level liked strategy preferences for the `Favoritos` filter.

#### Scenario: Favoritos filter is selected
- **WHEN** the user selects the `Favoritos` filter in Monitor
- **THEN** Monitor shows only opportunities whose favorite strategy ID is liked by that user

#### Scenario: User toggles strategy preference
- **WHEN** the user clicks the star control on a Monitor row
- **THEN** the UI updates the liked state and persists the preference through the Monitor API
