# product-analytics Specification

## Purpose
TBD - created by archiving change card-268-posthog-analytics. Update Purpose after archive.
## Requirements
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

### Requirement: Static legacy landing PostHog tracking

The legacy static landing SHALL support PostHog funnel tracking through runtime configuration without hardcoded project keys.

#### Scenario: Runtime config is absent

- **WHEN** the landing loads without `window.CRIPTOFAROL_POSTHOG.key`
- **THEN** it SHALL not load the PostHog SDK
- **AND** lead capture SHALL continue without analytics errors

#### Scenario: Runtime config is present

- **WHEN** the landing loads with a PostHog key and host
- **THEN** it SHALL initialize PostHog using that runtime configuration
- **AND** it SHALL capture a `landing_pageview` event with sanitized attribution

### Requirement: Static legacy landing lead funnel events

The legacy static landing SHALL emit non-sensitive lead funnel events when analytics is enabled.

#### Scenario: Lead submit succeeds

- **WHEN** a visitor submits the lead form and the API accepts it
- **THEN** the landing SHALL capture `lead_form_submit_started`
- **AND** it SHALL capture `lead_form_submit_accepted`
- **AND** neither event SHALL include name, email, WhatsApp, profile, free-text pain, tokens, full referrer paths, or complete URLs
- **AND** referrer context, when present, SHALL be reduced to a domain-only property

#### Scenario: Lead submit fails

- **WHEN** a visitor submits the lead form and the API rejects/fails
- **THEN** the landing SHALL capture `lead_form_submit_failed`
- **AND** the failure event SHALL include only a bounded failure reason plus sanitized attribution

### Requirement: Static landing standard pageview tracking
The static landing served at the production root SHALL emit a standard PostHog `$pageview` event when analytics is enabled.

#### Scenario: Root landing loads with analytics enabled
- **WHEN** a visitor opens `https://criptofarol.com.br/` with a configured PostHog project token
- **THEN** the landing SHALL initialize PostHog from runtime configuration
- **AND** it SHALL capture `$pageview`
- **AND** it SHALL also capture `landing_pageview` for funnel-specific reporting

#### Scenario: Pageview properties are sanitized
- **WHEN** the root landing captures `$pageview`
- **THEN** the event SHALL include a sanitized `$current_url` containing only scheme, host, and path
- **AND** it SHALL include `$pathname`
- **AND** it SHALL NOT include querystrings, URL fragments, tokens, full referrer paths, name, email, WhatsApp, profile, or free-text pain

### Requirement: Static landing first-party PostHog routing
The static landing SHALL support first-party PostHog routing through runtime configuration.

#### Scenario: Runtime config uses first-party ingest path
- **WHEN** `window.CRIPTOFAROL_POSTHOG.host` is `/ingest`
- **THEN** the landing SHALL initialize PostHog with `api_host` set to `/ingest`
- **AND** it SHALL set `ui_host` from runtime configuration when provided
- **AND** the SDK asset URL derived by the static snippet SHALL remain under `/ingest`

#### Scenario: Runtime config uses direct PostHog host
- **WHEN** `window.CRIPTOFAROL_POSTHOG.host` is absent
- **THEN** the landing SHALL initialize PostHog with `https://us.i.posthog.com`
- **AND** analytics calls SHALL continue to be no-ops without throwing when the project token is absent

