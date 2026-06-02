## MODIFIED Requirements

### Requirement: Favorites list ordering follows the selected sort option
The Favorites page MUST apply the selected ordering option as the primary sort key for the visible filtered Favorites list.

#### Scenario: User changes Favorites ordering
- **WHEN** an authenticated user opens `/favorites`
- **AND** selects an available option in the `Ordenar` control
- **THEN** the visible Favorites list MUST reorder according to that selected option
- **AND** the list MUST update immediately without requiring a page reload

#### Scenario: User changes Favorites ordering repeatedly
- **WHEN** the user changes the `Ordenar` control more than once
- **THEN** each selected ordering option MUST be reflected by the visible Favorites list
- **AND** ties MUST be resolved deterministically

#### Scenario: Favorites ordering handles small result sets
- **WHEN** the filtered Favorites list is empty or contains one item
- **THEN** changing the `Ordenar` control MUST NOT break the screen or show a visual error
