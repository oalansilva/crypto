## ADDED Requirements

### Requirement: Lead form emits non-sensitive funnel events
The frontend lead capture flow SHALL emit non-sensitive analytics events for lead form submission outcomes when analytics is enabled.

#### Scenario: Lead form submission starts
- **WHEN** a visitor submits the beta lead form
- **THEN** the frontend SHALL capture a lead submission started event
- **AND** the event SHALL include attribution and technical context only
- **AND** the event SHALL NOT include name, email, WhatsApp, profile, pain text, auth token, or other PII

#### Scenario: Lead form submission succeeds
- **WHEN** the beta lead API accepts the submission
- **THEN** the frontend SHALL capture a lead submission accepted event
- **AND** the event SHALL include attribution and technical context only

#### Scenario: Lead form submission fails
- **WHEN** the beta lead API rejects or fails the submission
- **THEN** the frontend SHALL capture a lead submission failed event
- **AND** the event SHALL include a non-sensitive failure classification only
