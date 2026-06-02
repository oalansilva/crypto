## MODIFIED Requirements

### Requirement: Load all strategies from database
The system SHALL load all valid combo strategies (pre-built, examples, custom) from the runtime PostgreSQL database instead of hard-coded Python classes. GET /api/combos/templates returns prebuilt, examples, custom arrays with each available template's name, public description, and read-only state.

#### Scenario: Load strategies from database
- **GIVEN** combo strategies exist in the runtime PostgreSQL database
- **WHEN** GET /api/combos/templates is called
- **THEN** prebuilt, examples, and custom arrays are returned
- **AND** the arrays include the available templates with `name`, `description`, and `is_readonly`
- **AND** no hard-coded Python classes are used

#### Scenario: Combo screen receives available templates
- **GIVEN** valid combo templates exist in the runtime PostgreSQL `combo_templates` table
- **WHEN** the Combo selection screen requests GET /api/combos/templates
- **THEN** the response contains at least one available template
- **AND** the screen MUST NOT display `0 strategies stored in database`

#### Scenario: Restore baseline templates when runtime table is empty
- **GIVEN** the runtime PostgreSQL `combo_templates` table is empty
- **WHEN** GET /api/combos/templates is called
- **THEN** the backend loads the versioned baseline combo template export into PostgreSQL
- **AND** the response contains the restored template arrays
