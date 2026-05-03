# strategy-secret-visibility Specification

## Purpose
Define which strategy implementation details are visible to common users and which remain admin-only.

## Requirements

### Requirement: Strategy secrets are only visible to admin users
The system MUST expose clear strategy identifiers, strategy parameters, indicator values, and analyzer detail payloads only to admin users.

#### Scenario: Non-admin receives protected strategy payload
- **WHEN** a non-admin user requests an API response containing strategy data
- **THEN** the response MUST replace clear strategy identifiers with a protected label
- **AND** the response MUST omit strategy parameter values
- **AND** the response MUST omit indicator values and analyzer detail payloads
- **AND** the response MUST mark the strategy as protected

#### Scenario: Admin receives full strategy payload
- **WHEN** an admin user requests the same API response
- **THEN** the response MUST include the original strategy identifiers, parameter values, indicator values, and analyzer details
- **AND** the response MUST mark the strategy as not protected

#### Scenario: Operational decision context remains visible
- **WHEN** a non-admin user receives a protected strategy payload
- **THEN** the response MUST still include operational decision fields needed inside the product, including symbol, timeframe, decision status, distance, price context, tier, notes, and signal history where available

### Requirement: Strategy tooling is admin-only
The system MUST restrict APIs and routes that expose strategy templates, optimization schema, backtest configuration internals, or strategy mutation controls to admin users.

#### Scenario: Non-admin requests strategy tooling API
- **WHEN** a non-admin user requests a combo template, strategy metadata, backtest, optimization, or template mutation API
- **THEN** the system MUST reject the request with an authorization error

#### Scenario: Admin requests strategy tooling API
- **WHEN** an admin user requests a combo template, strategy metadata, backtest, optimization, or template mutation API
- **THEN** the system MUST preserve the existing admin behavior
