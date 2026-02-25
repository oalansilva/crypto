# dev-autonomous-features Specification

## Purpose
TBD - created by archiving change dev-autonomous-features. Update Purpose after archive.
## Requirements
### Requirement: Derived Feature Declaration
**Description:** The system SHALL allow the Dev agent to declare derived indicator columns (e.g., `rsi_prev`, `ema_slope`) as part of its structured output when needed for strategy logic.

#### Scenario: Dev declares derived feature
- **WHEN** the Dev output includes a list of derived columns
- **THEN** the system registers these columns for feature generation

### Requirement: Safe Derived Transform Set
**Description:** The system SHALL support a predefined set of safe derived transforms (e.g., lag/prev, slope, rolling mean) and reject unsupported ones with a diagnostic error.

#### Scenario: Supported derived transform
- **WHEN** the Dev requests a supported transform (e.g., `rsi_prev`)
- **THEN** the derived column is generated and made available to logic evaluation

#### Scenario: Unsupported derived transform
- **WHEN** the Dev requests an unsupported transform
- **THEN** the system rejects the request and records a diagnostic error

### Requirement: Prompt Guidance For Derived Features
**Description:** The system SHALL update the Dev prompt to explicitly allow derived columns and instruct the Dev to declare them when required.

#### Scenario: Prompt includes derived guidance
- **WHEN** the Dev prompt is generated
- **THEN** it includes instructions on declaring derived columns

