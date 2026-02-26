# monitor-theme-preference Specification

## Purpose
TBD - created by archiving change monitor-dark-green-theme. Update Purpose after archive.
## Requirements
### Requirement: Monitor theme preference is persisted in backend
The system MUST persist a Monitor theme preference in the backend.

#### Scenario: Default theme is dark-green
- **WHEN** the user opens the Monitor screen and no preference exists
- **THEN** the Monitor theme defaults to `dark-green`

#### Scenario: User theme persists across reload
- **WHEN** the user sets a theme and reloads
- **THEN** the Monitor renders using the persisted theme

#### Scenario: Preference persists across devices
- **WHEN** the user sets a theme on one device
- **THEN** another device sees the same theme after fetching preferences

