# database-strategy-config Specification

## Purpose
TBD - created by syncing delta from change database-driven-strategies. Store and load strategy configuration from database.

## Requirements

### Requirement: Store optimization schemas in database
The system SHALL store optimization parameter schemas as JSON in the database. Each parameter SHALL include min, max, step, default. Schema SHALL be retrievable via GET /api/combos/meta/:template.

### Requirement: Load all strategies from database
The system SHALL load all combo strategies (pre-built, examples, custom) from the database instead of hard-coded Python classes. GET /api/combos/templates returns prebuilt, examples, custom arrays.

### Requirement: Instantiate strategy from database configuration
When creating a strategy instance for backtesting, the system SHALL read template_data JSON, parse indicators/entry_logic/exit_logic/stop_loss, and create ComboStrategy instance. Strategy SHALL function identically to hard-coded class.

### Requirement: Use database schemas for optimization
The optimization engine SHALL read parameter schemas from the database (optimization_schema column) instead of calling Python class methods.
