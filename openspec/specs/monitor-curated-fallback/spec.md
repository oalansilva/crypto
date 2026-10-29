# monitor-curated-fallback Specification

## Purpose
Define the curated Monitor fallback for common users who do not yet have Monitor-ready favorite strategies.
## Requirements
### Requirement: Common users without favorites receive curated Monitor data
The system SHALL return safe curated Monitor opportunities (the vitrine) for an authenticated common user who has no own favorite with at least one star, of any class (crypto, ação or ETF). The vitrine is display only: it SHALL NOT make anyone receive Telegram alerts, including when the common user gives his own star to a catalog row (card #1122, decisão 3 de Alan, 27/10/2026). `GET /api/favorites/` SHALL return the vitrine only to a common user with no own favorite at all; a user whose only favorites have no star sees them in Favoritos and the vitrine in the Monitor.

#### Scenario: Common user has no favorites
- **WHEN** a common authenticated user requests `/api/opportunities/`
- **AND** that user has no own favorite strategies
- **THEN** the system returns opportunities computed from the configured admin-curated favorite set
- **AND** the response is redacted according to non-admin strategy visibility rules
- **AND** admin-authored fallback names and notes are not exposed to the common user
- **AND** every row has `is_curated_fallback=true` and `notify_telegram=false`

#### Scenario: Common user has own starred favorites
- **WHEN** a common authenticated user requests `/api/opportunities/`
- **AND** that user has own favorite strategies with at least one star, of any class
- **THEN** the system returns opportunities computed from that user's own favorites
- **AND** the system does not mix in curated fallback favorites

#### Scenario: User has only ação or ETF favorites
- **WHEN** a common authenticated user has only an NVDA favorite with 1 star
- **THEN** `/api/opportunities/` and `/api/favorites/` return that user's NVDA favorite
- **AND** they do not return the curated catalog

#### Scenario: User has only unstarred favorites
- **WHEN** a common authenticated user has only favorites without star, saved by a batch
- **THEN** `/api/favorites/` returns those favorites
- **AND** `/api/opportunities/` returns the vitrine, which sends no alert

#### Scenario: No curated favorites exist
- **WHEN** a user without favorites requests `/api/opportunities/`
- **AND** no configured admin user has Monitor candidate favorite strategies for the requested tier filter
- **THEN** the system returns an empty list without raising an error

