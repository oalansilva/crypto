## ADDED Requirements

### Requirement: The ruler obtains OHLCV access from the environment without changing its invocation

The read-only Jev ruler (`scripts/scalp_jev_eval.py`) SHALL obtain its OHLCV access from the **environment** (the application database URL resolved by `app.database`), and its **invocation SHALL NOT change**: no new argument or environment variable SHALL be introduced to pass the connection. The ruler SHALL declare the connection it uses, and SHALL remain read-only.

#### Scenario: Access comes from the environment

- **WHEN** the ruler reads the stored OHLCV
- **THEN** the connection SHALL come from the environment (the application database URL) and not from a new command-line argument
- **AND** the ruler SHALL NOT write to product, trading state or the database

#### Scenario: The invocation carries no connection parameter

- **WHEN** the operator invokes the ruler
- **THEN** the invocation SHALL NOT require a connection/DSN argument that did not exist before this change
- **AND** the access path SHALL be the same environment-resolved path the ruler already used

### Requirement: The ruler declares in the report which connection and user it used

The ruler SHALL declare in the report which **connection and user** it used, both when it measures and when it fails to measure. The declared identity SHALL name the user, host, port and database, and its source, and SHALL NOT expose the password or the full DSN.

#### Scenario: A successful measurement declares the connection used

- **WHEN** the ruler measures the realized side successfully
- **THEN** the report SHALL identify the user, host, port and database used and the source of the connection
- **AND** the report SHALL NOT contain the password or the full DSN

#### Scenario: A failed measurement still declares the intended connection

- **WHEN** the ruler fails to read the OHLCV and the realized side is `não medido`
- **THEN** the report SHALL still declare the connection/user the ruler used (or intended to use) and its source
- **AND** the report SHALL NOT expose the password or the full DSN

### Requirement: The real cause of a read failure is visible in the report

The ruler SHALL expose the **real cause** of an OHLCV read failure in the report — for example a peer-authentication failure naming the user, or the missing module of an import failure — not only the exception class name. The exposed cause SHALL be bounded and sanitized of credentials.

#### Scenario: A read failure exposes the real cause, not only the class name

- **WHEN** reading the OHLCV raises an error
- **THEN** the report SHALL include the underlying error message (bounded and sanitized) in addition to the exception class name
- **AND** the report SHALL NOT include credentials or the full DSN

#### Scenario: An import failure names the missing module

- **WHEN** the OHLCV repository cannot be imported because a module is missing
- **THEN** the report SHALL name the missing module in the failure note
- **AND** the failure SHALL be classified as a non-measured realized side, not as insufficient sample
