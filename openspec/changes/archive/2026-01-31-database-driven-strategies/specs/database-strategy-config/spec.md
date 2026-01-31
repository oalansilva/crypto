# Spec: Database-Driven Strategy Configuration

## ADDED Requirements

### Requirement: Store optimization schemas in database

The system SHALL store optimization parameter schemas as JSON in the database to enable runtime configuration of strategy optimization without code deployment.

#### Scenario: Store optimization schema for pre-built strategy

**Given** a pre-built combo strategy "ema_rsi"  
**When** the strategy is seeded into the database  
**Then** the `optimization_schema` column SHALL contain a JSON object with parameter definitions  
**And** each parameter SHALL include `min`, `max`, `step`, and `default` values  
**And** the schema SHALL be retrievable via the `/api/combos/meta/:template` endpoint

**Example schema:**
```json
{
  "ema_fast": {
    "min": 5,
    "max": 20,
    "step": 1,
    "default": 9
  },
  "rsi_period": {
    "min": 7,
    "max": 21,
    "step": 1,
    "default": 14
  }
}
```

#### Scenario: Retrieve optimization schema from database

**Given** a combo strategy exists in the database with an optimization schema  
**When** a client requests template metadata via GET `/api/combos/meta/:template`  
**Then** the response SHALL include the `optimization_schema` field  
**And** the schema SHALL be valid JSON  
**And** all parameters SHALL have required fields (min, max, step, default)

---

### Requirement: Load all strategies from database

The system SHALL load all combo strategies (pre-built, examples, and custom) from the database instead of hard-coded Python classes.

#### Scenario: List all strategies from database

**Given** the database contains pre-built strategies with `is_prebuilt=1`  
**And** the database contains example strategies with `is_example=1`  
**And** the database contains custom strategies with `is_prebuilt=0` and `is_example=0`  
**When** a client requests GET `/api/combos/templates`  
**Then** the response SHALL include all three categories  
**And** pre-built strategies SHALL be returned in the `prebuilt` array  
**And** example strategies SHALL be returned in the `examples` array  
**And** custom strategies SHALL be returned in the `custom` array

#### Scenario: Instantiate strategy from database configuration

**Given** a combo strategy "ema_rsi" exists in the database  
**When** the system needs to create a strategy instance for backtesting  
**Then** it SHALL read the `template_data` JSON from the database  
**And** it SHALL parse the indicators, entry_logic, exit_logic, and stop_loss  
**And** it SHALL create a `ComboStrategy` instance using the parsed configuration  
**And** the strategy SHALL function identically to a hard-coded Python class

---

### Requirement: Use database schemas for optimization

The optimization engine SHALL read parameter schemas from the database instead of calling Python class methods.

#### Scenario: Generate optimization stages from database schema

**Given** a combo strategy "ema_rsi" has an `optimization_schema` in the database  
**When** the optimizer generates optimization stages  
**Then** it SHALL read the schema from the `optimization_schema` column  
**And** it SHALL NOT call `get_optimization_schema()` method on Python classes  
**And** it SHALL generate stages for each parameter in the schema  
**And** each stage SHALL use the min, max, and step values from the schema

#### Scenario: Optimize strategy with database-driven schema

**Given** a client requests optimization for "ema_rsi"  
**When** POST `/api/combos/optimize` is called  
**Then** the optimizer SHALL use the database schema for parameter ranges  
**And** the optimization SHALL complete successfully  
**And** the results SHALL include optimized parameter values  
**And** the performance SHALL be equivalent to Python class-based optimization

---

## REMOVED Requirements

### Requirement: Hard-coded strategy classes

The system SHALL NOT use hard-coded Python classes for pre-built combo strategies.

#### Scenario: Remove Python strategy class files

**Given** the migration to database-driven strategies is complete  
**When** the codebase is inspected  
**Then** the following files SHALL NOT exist:
- `backend/app/strategies/combos/multi_ma_crossover.py`
- `backend/app/strategies/combos/ema_rsi_combo.py`
- `backend/app/strategies/combos/ema_macd_volume_combo.py`
- `backend/app/strategies/combos/bollinger_rsi_adx_combo.py`
- `backend/app/strategies/combos/volume_atr_breakout_combo.py`
- `backend/app/strategies/combos/ema_rsi_fibonacci_combo.py`

**And** the `PREBUILT_TEMPLATES` dictionary SHALL NOT exist in `ComboService`

#### Scenario: No Python class method calls for optimization

**Given** the system is running with database-driven strategies  
**When** the optimizer generates stages  
**Then** it SHALL NOT call `get_optimization_schema()` on any Python class  
**And** it SHALL NOT import strategy classes from `backend/app/strategies/combos/`  
**And** all optimization schemas SHALL come from the database

---

## MODIFIED Requirements

### Requirement: Database schema for combo templates

The `combo_templates` table SHALL be extended to support optimization schemas.

#### Scenario: Add optimization_schema column

**Given** the database migration is executed  
**When** the `combo_templates` table is inspected  
**Then** it SHALL have an `optimization_schema` column of type JSON  
**And** the column SHALL be nullable (for backward compatibility)  
**And** existing templates SHALL continue to work without the column populated

**Schema:**
```sql
CREATE TABLE combo_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    is_example BOOLEAN DEFAULT 0,
    is_prebuilt BOOLEAN DEFAULT 0,
    template_data JSON NOT NULL,
    optimization_schema JSON,  -- NEW
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

### Requirement: ComboService template loading

The `ComboService` SHALL load all templates from the database without checking Python classes.

#### Scenario: Get template metadata from database only

**Given** a template "ema_rsi" exists in the database  
**When** `ComboService.get_template_metadata("ema_rsi")` is called  
**Then** it SHALL query the database for the template  
**And** it SHALL NOT check the `PREBUILT_TEMPLATES` dictionary  
**And** it SHALL return the `template_data` and `optimization_schema` from the database  
**And** it SHALL return None if the template does not exist in the database

#### Scenario: Backward compatibility with existing templates

**Given** an existing template without an `optimization_schema` column value  
**When** the template metadata is retrieved  
**Then** the system SHALL NOT fail  
**And** the `optimization_schema` field SHALL be None or empty  
**And** the template SHALL still be usable for backtesting

---

## Migration Requirements

### Requirement: Safe database migration

The migration SHALL preserve existing data and provide rollback capability.

#### Scenario: Add column without data loss

**Given** the database contains existing combo templates  
**When** the migration adds the `optimization_schema` column  
**Then** all existing templates SHALL remain intact  
**And** the `template_data` column SHALL be unchanged  
**And** no templates SHALL be deleted or corrupted

#### Scenario: Seed pre-built strategies

**Given** the migration script is executed  
**When** pre-built strategies are seeded into the database  
**Then** 6 strategies SHALL be inserted with `is_prebuilt=1`  
**And** each strategy SHALL have a complete `optimization_schema`  
**And** the strategies SHALL match the functionality of the removed Python classes  
**And** existing example templates SHALL not be affected

#### Scenario: Rollback capability

**Given** the migration has been applied  
**When** a rollback is needed  
**Then** the database backup SHALL be restorable  
**And** the Python strategy classes SHALL be recoverable from git  
**And** the system SHALL function with the previous architecture

---

## Performance Requirements

### Requirement: Acceptable query performance

Database queries for template metadata SHALL not significantly impact system performance.

#### Scenario: Template metadata retrieval performance

**Given** a combo strategy exists in the database  
**When** template metadata is requested 100 times  
**Then** the average response time SHALL be less than 50ms  
**And** the system SHALL support caching to reduce database queries  
**And** the performance SHALL be comparable to the Python class-based approach

---

## Testing Requirements

### Requirement: Comprehensive test coverage

The database-driven strategy system SHALL have comprehensive automated tests.

#### Scenario: Unit tests for database loading

**Given** the test suite is executed  
**When** unit tests for `ComboService` run  
**Then** tests SHALL verify template loading from database  
**And** tests SHALL verify optimization schema retrieval  
**And** tests SHALL verify strategy instantiation from JSON  
**And** all tests SHALL pass

#### Scenario: Integration tests for end-to-end flow

**Given** a pre-built strategy exists in the database  
**When** integration tests run  
**Then** tests SHALL verify complete backtest flow  
**And** tests SHALL verify complete optimization flow  
**And** tests SHALL verify results match expected metrics  
**And** all tests SHALL pass
