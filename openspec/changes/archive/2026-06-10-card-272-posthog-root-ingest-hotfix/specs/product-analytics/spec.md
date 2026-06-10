## ADDED Requirements

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
