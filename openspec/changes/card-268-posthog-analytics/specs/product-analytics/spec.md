## ADDED Requirements

### Requirement: Configurable PostHog initialization
The frontend SHALL initialize PostHog analytics only when a PostHog project key is configured for the current Vite environment.

#### Scenario: PostHog key configured
- **WHEN** `VITE_POSTHOG_KEY` is present during frontend runtime
- **THEN** the frontend SHALL initialize PostHog using that key
- **AND** it SHALL use `VITE_POSTHOG_HOST` when provided

#### Scenario: PostHog key missing
- **WHEN** `VITE_POSTHOG_KEY` is absent
- **THEN** the frontend SHALL continue to work normally
- **AND** analytics capture calls SHALL be no-ops without throwing errors

### Requirement: Initial pageview tracking
The frontend SHALL capture an initial pageview event with non-sensitive context when analytics is enabled.

#### Scenario: Visitor opens the app with UTM attribution
- **WHEN** a visitor opens the frontend with UTM parameters and analytics is enabled
- **THEN** the frontend SHALL capture an initial pageview event
- **AND** the event SHALL include sanitized attribution fields already captured by the attribution module
- **AND** the event SHALL NOT include name, email, WhatsApp, free-text pain, auth token, or other PII

### Requirement: Safe analytics wrapper
The system SHALL route product analytics events through a local wrapper instead of calling PostHog directly from product code.

#### Scenario: Product code emits an analytics event
- **WHEN** frontend code records a product analytics event
- **THEN** it SHALL call the local analytics wrapper
- **AND** the wrapper SHALL be responsible for provider availability and failure isolation
