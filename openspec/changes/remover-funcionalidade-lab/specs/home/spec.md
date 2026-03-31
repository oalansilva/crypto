## MODIFIED Requirements

### Requirement: Home shows a Quick Actions section
The Home page MUST provide shortcuts only to workflows that remain supported by the product and MUST stop exposing Strategy Lab as a destination.

#### Scenario: User uses a Home shortcut
- **WHEN** the user clicks a shortcut card/button on Home
- **THEN** the system MUST navigate only to still-supported destinations
- **AND** no shortcut to Strategy Lab is rendered
