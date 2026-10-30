## MODIFIED Requirements

### Requirement: Static legacy landing lead funnel events

The legacy static landing SHALL emit non-sensitive lead funnel events when analytics is enabled. Submit events SHALL carry the form step (`step: 1` or `step: 2`).

#### Scenario: Lead submit succeeds

- **WHEN** a visitor submits a step of the lead form and the API accepts it
- **THEN** the landing SHALL capture `lead_form_submit_started` with the step
- **AND** it SHALL capture `lead_step1_completed` when step 1 is saved, and `lead_form_submit_accepted` with `step: 2` when step 2 is saved
- **AND** none of these events SHALL include name, email, WhatsApp, profile, free-text pain, tokens, full referrer paths, or complete URLs
- **AND** referrer context, when present, SHALL be reduced to a domain-only property

#### Scenario: Lead submit fails

- **WHEN** a visitor submits a step of the lead form and the API rejects/fails
- **THEN** the landing SHALL capture `lead_form_submit_failed` with the step
- **AND** the failure event SHALL include only the step, a bounded failure reason plus sanitized attribution

#### Scenario: Visitor skips step 2

- **WHEN** a visitor who saved step 1 skips step 2
- **THEN** the landing SHALL capture `lead_step2_skipped` without personal data

## ADDED Requirements

### Requirement: Landing CTA clicks are measured
The landing SHALL capture `landing_cta_clicked` when analytics is enabled and a visitor clicks a signup CTA, with `cta_location` set to `hero`, `nav` or `footer` and sanitized attribution, without personal data.

#### Scenario: Visitor clicks the hero CTA
- **WHEN** a visitor clicks "Quero meus 6 meses grátis" in the hero
- **THEN** the landing SHALL capture `landing_cta_clicked` with `cta_location: hero`

#### Scenario: Visitor clicks the navigation or footer CTA
- **WHEN** a visitor clicks the signup CTA in the navigation or in the footer
- **THEN** the landing SHALL capture `landing_cta_clicked` with `cta_location: nav` or `cta_location: footer`

### Requirement: Published landing has analytics configured
The production landing SHALL load PostHog with the same project as the app, through the first-party `/ingest` path, so the funnel events are recorded. The project key SHALL be written at deploy time and SHALL NOT be committed.

#### Scenario: Production landing loads
- **WHEN** a visitor opens `https://criptofarol.com.br/`
- **THEN** the runtime PostHog configuration served with the landing SHALL contain a non-empty project key
- **AND** the landing SHALL capture `$pageview` and `landing_pageview`

#### Scenario: Landing analytics stays within the Privacy Policy
- **WHEN** the landing initializes PostHog
- **THEN** it SHALL disable session recording and surveys and keep autocapture off, regardless of the project settings shared with the app
