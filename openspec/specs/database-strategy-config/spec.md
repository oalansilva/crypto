# database-strategy-config Specification

## Purpose
Store and load strategy configuration from database instead of hard-coded Python classes.

## Requirements

### Requirement: Store optimization schemas in database
The system SHALL store optimization parameter schemas as JSON in the database. Each parameter SHALL include min, max, step, default. Schema SHALL be retrievable via GET /api/combos/meta/:template.

#### Scenario: Retrieve optimization schema
- **GIVEN** optimization schemas are stored in the database
- **WHEN** GET /api/combos/meta/:template is called
- **THEN** the optimization schema JSON is returned with min, max, step, default for each parameter

### Requirement: Load all strategies from database
The system SHALL load all combo strategies (pre-built, examples, custom) from the database instead of hard-coded Python classes. GET /api/combos/templates returns prebuilt, examples, custom arrays.

#### Scenario: Load strategies from database
- **GIVEN** combo strategies exist in the database
- **WHEN** GET /api/combos/templates is called
- **THEN** prebuilt, examples, and custom arrays are returned
- **AND** no hard-coded Python classes are used

### Requirement: Instantiate strategy from database configuration
When creating a strategy instance for backtesting, the system SHALL read template_data JSON, parse indicators/entry_logic/exit_logic/stop_loss, and create ComboStrategy instance. Strategy SHALL function identically to hard-coded class.

#### Scenario: Instantiate from database config
- **GIVEN** a template exists in the database with template_data JSON
- **WHEN** a strategy instance is created for backtesting
- **THEN** the system reads template_data, parses indicators/entry_logic/exit_logic/stop_loss
- **AND** creates a ComboStrategy instance that functions identically to a hard-coded class

### Requirement: Use database schemas for optimization
The optimization engine SHALL read parameter schemas from the database (optimization_schema column) instead of calling Python class methods.

#### Scenario: Read schemas from database during optimization
- **GIVEN** optimization is triggered for a template
- **WHEN** the optimization engine runs
- **THEN** parameter schemas are read from the database optimization_schema column
- **AND** no Python class methods are called for schema retrieval
