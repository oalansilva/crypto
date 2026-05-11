## ADDED Requirements

### Requirement: Favorites does not expose agent chat action
The Favorites page SHALL NOT expose a "Chat com agente", "Trader", or equivalent agent-chat action from `/favorites`, while preserving the existing Favorites analysis, ranking, filtering, selection, and administrative delete actions.

#### Scenario: Desktop Favorites row hides agent chat
- **WHEN** an admin user opens `/favorites` on a desktop viewport
- **THEN** each visible favorite SHALL keep the analysis action
- **AND** administrative users SHALL keep the delete action
- **AND** the row actions SHALL NOT include "Chat com agente", "Trader", or a chat icon action that opens the agent chat modal

#### Scenario: Mobile Favorites card hides agent chat
- **WHEN** an admin user opens `/favorites` on a mobile viewport
- **THEN** each visible favorite card SHALL keep the analysis action
- **AND** administrative users SHALL keep the delete action
- **AND** the card actions SHALL NOT include "Chat com agente", "Trader", or a chat icon action that opens the agent chat modal
