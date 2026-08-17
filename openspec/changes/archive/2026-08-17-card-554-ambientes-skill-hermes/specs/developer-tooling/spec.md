## ADDED Requirements

### Requirement: Global environments skill is part of developer tooling
Developer tooling SHALL keep `alan-workflow-ambientes` aligned with the live Oracle map. A stale OpenClaw gateway map is a tooling defect, not an acceptable default.

#### Scenario: Skill content is audited
- **WHEN** the environments skill is reviewed
- **THEN** it does not list `openclaw-gateway.service` as an active service
- **AND** it lists Hermes and the real Cripto/Clara DEV/PROD units
