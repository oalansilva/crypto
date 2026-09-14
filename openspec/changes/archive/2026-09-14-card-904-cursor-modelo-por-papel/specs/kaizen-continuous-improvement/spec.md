## ADDED Requirements

### Requirement: Release kaizen reads the role-model proxy
`/kaizen release` SHALL read REST issue comments of the package cards and look for `proxy modelo: <papel> → <rótulo> (<slug>)` lines recorded on Design, Apply, and Review handoffs. It SHALL compare those lines to the vigente juízo/execução table in the Cursor runbook. Missing proxy on a card that spawned children SHALL be a finding, not a silent skip. The audit MUST NOT parse Cursor/Grok usage meters, MUST NOT add a dashboard, and MUST NOT print dollar amounts from a vendor API.

#### Scenario: Proxy lines are compared to the table
- **WHEN** `/kaizen release` runs for a package whose cards have Design/Apply/Review handoffs
- **THEN** it reports whether `proxy modelo:` lines match Grok 4.6 for juízo and Composer 2.5 for execução
- **AND** it does not call a vendor usage API

#### Scenario: Missing proxy is a finding
- **WHEN** a package card spawned isolated children and the handoff has no `proxy modelo:` line
- **THEN** the kaizen report records that gap as a finding
- **AND** the audit remains read-only
