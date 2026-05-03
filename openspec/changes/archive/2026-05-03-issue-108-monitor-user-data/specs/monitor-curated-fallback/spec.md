## ADDED Requirements

### Requirement: Common users without favorites receive curated Monitor data
The system SHALL return safe curated Monitor opportunities for an authenticated user who has no own Monitor-ready favorite strategies matching the requested Monitor filter.

#### Scenario: Common user has no favorites
- **WHEN** a common authenticated user requests `/api/opportunities/`
- **AND** that user has no crypto Monitor candidate favorite strategies for the requested tier filter
- **THEN** the system returns opportunities computed from the configured admin-curated favorite set
- **AND** the response is redacted according to non-admin strategy visibility rules
- **AND** admin-authored fallback names and notes are not exposed to the common user

#### Scenario: Common user has own favorites
- **WHEN** a common authenticated user requests `/api/opportunities/`
- **AND** that user has crypto Monitor candidate favorite strategies for the requested tier filter
- **THEN** the system returns opportunities computed from that user's own favorites
- **AND** the system does not mix in curated fallback favorites

#### Scenario: User favorites are outside Monitor scope
- **WHEN** a common authenticated user requests `/api/opportunities/`
- **AND** that user has favorites but none are crypto Monitor candidates for the requested tier filter
- **THEN** the system returns opportunities computed from the configured admin-curated favorite set

#### Scenario: No curated favorites exist
- **WHEN** a user without favorites requests `/api/opportunities/`
- **AND** no configured admin user has crypto Monitor candidate favorite strategies for the requested tier filter
- **THEN** the system returns an empty list without raising an error
