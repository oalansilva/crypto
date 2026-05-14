# strategy-template-descriptions Specification

## Purpose
Expose short, trader-friendly descriptions for visible strategy templates without exposing protected parameters or making performance promises.

## Requirements

### Requirement: Public Strategy Descriptions
The system SHALL expose a short, trader-friendly, non-promissory description for each visible strategy/template.

#### Scenario: Combo template list includes description
- **WHEN** an admin opens the Combo template selection flow
- **THEN** each listed template SHALL include a high-level description beside the template name
- **AND** the description SHALL avoid parameter dumps and profit promises.

#### Scenario: Favorites shows strategy and description
- **WHEN** a user opens Favorites
- **THEN** each favorite row/card SHALL show the visible strategy label
- **AND** SHALL show a high-level description when available.

#### Scenario: Monitor shows strategy description
- **WHEN** a user opens Monitor opportunities
- **THEN** the visible strategy identity SHALL include a high-level description when available.
