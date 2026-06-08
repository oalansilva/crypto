## ADDED Requirements

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
