## ADDED Requirements

### Requirement: Leads systemd template does not use OpenClaw HOME
The leads service template SHALL NOT set `HOME` or `CODEX_HOME` to paths under `/root/.openclaw`. Canonical Hermes or repo-local paths SHALL be used instead.

#### Scenario: Leads unit has no OpenClaw home
- **WHEN** an operator inspects the installed leads unit
- **THEN** `HOME` and `CODEX_HOME` do not point at `/root/.openclaw`
