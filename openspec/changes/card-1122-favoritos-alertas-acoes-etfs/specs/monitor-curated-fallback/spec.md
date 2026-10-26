## MODIFIED Requirements

### Requirement: Common users without favorites receive curated Monitor data
The system SHALL return safe curated Monitor opportunities for an authenticated user who has no own favorite strategies of any class (crypto, ação or ETF). The curated fallback is display only: it SHALL NOT make the user receive Telegram alerts. `GET /api/favorites/` SHALL follow the same rule.

#### Scenario: Common user has no favorites
- **WHEN** a common authenticated user requests `/api/opportunities/`
- **AND** that user has no own favorite strategies
- **THEN** the system returns opportunities computed from the configured admin-curated favorite set
- **AND** the response is redacted according to non-admin strategy visibility rules
- **AND** admin-authored fallback names and notes are not exposed to the common user

#### Scenario: Common user has own favorites
- **WHEN** a common authenticated user requests `/api/opportunities/`
- **AND** that user has own favorite strategies of any class
- **THEN** the system returns opportunities computed from that user's own favorites
- **AND** the system does not mix in curated fallback favorites

#### Scenario: User has only ação or ETF favorites
- **WHEN** a common authenticated user has only an NVDA favorite
- **THEN** `/api/opportunities/` and `/api/favorites/` return that user's NVDA favorite
- **AND** they do not return the curated catalog

#### Scenario: No curated favorites exist
- **WHEN** a user without favorites requests `/api/opportunities/`
- **AND** no configured admin user has Monitor candidate favorite strategies for the requested tier filter
- **THEN** the system returns an empty list without raising an error
