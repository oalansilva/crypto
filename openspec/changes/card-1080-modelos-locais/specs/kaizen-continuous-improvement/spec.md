## ADDED Requirements

### Requirement: Model audit uses historical captures
Kaizen model audit SHALL compare each proxy to its client/band capture at birth, replacing comparison with the current Git map or current machine choice. Missing proxy/capture SHALL be reported explicitly. Audits SHALL distinguish requested and observed and MUST NOT infer runtime identity. Usage parsing, dashboards and vendor-dollar reporting SHALL remain out of scope.

#### Scenario: Model edited after the card
- **WHEN** Kaizen audits a completed spawn after another operational model edit
- **THEN** it checks the recorded birth capture and does not report the old valid choice as divergence merely because configuration changed
