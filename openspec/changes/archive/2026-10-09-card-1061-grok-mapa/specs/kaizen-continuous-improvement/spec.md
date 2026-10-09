## MODIFIED Requirements

### Requirement: Release kaizen reads the role-model proxy
`/kaizen release` SHALL read REST issue comments of the package cards and look for `proxy modelo: <papel> → <rótulo> (<slug>)` lines recorded on Design, Apply, and Review handoffs. It SHALL compare Cursor lines to the vigente top-level `juizo`/`execucao` bands in `.cursor/model-map.yaml` and Grok Build lines to `juizo.grok`/`execucao.grok` (not to slugs hardcoded in the Cursor runbook, and not by scoring a Grok `grok-4.6` execução proxy as a miss against `composer-2.5`). Missing proxy on a card that spawned children SHALL be a finding, not a silent skip. The audit MUST NOT parse Cursor/Grok usage meters, MUST NOT add a dashboard, and MUST NOT print dollar amounts from a vendor API.

#### Scenario: Proxy lines are compared to the table
- **WHEN** `/kaizen release` runs for a package whose cards have Design/Apply/Review handoffs
- **THEN** it reports whether Cursor `proxy modelo:` lines match top-level `juizo` for juízo roles and top-level `execucao` for execução roles in `.cursor/model-map.yaml`
- **AND** it reports whether Grok `proxy modelo:` lines match `juizo.grok` for juízo roles and `execucao.grok` for execução roles
- **AND** a Grok reviewer proxy of Grok 4.6 (`grok-4.6`) is not a finding for differing from `composer-2.5`
- **AND** it does not call a vendor usage API

#### Scenario: Missing proxy is a finding
- **WHEN** a package card spawned isolated children and the handoff has no `proxy modelo:` line
- **THEN** the kaizen report records that gap as a finding
- **AND** the audit remains read-only
