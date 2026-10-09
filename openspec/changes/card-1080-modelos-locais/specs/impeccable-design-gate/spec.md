## ADDED Requirements

### Requirement: Design model checks use birth captures
Design model verification SHALL use each child's captured machine selection. Historical requirements to read `.cursor/model-map.yaml`, use fixed Cursor/Grok slugs, or keep the later critic equal to an earlier author SHALL be superseded by this selection contract. Same-wave A/B equality, juizo roles, isolated prompts, snapshot-only writes, critique ceiling and human approval SHALL remain unchanged. Missing runtime trace SHALL remain unavailable and MUST NOT become a degraded PASS.

#### Scenario: Later critic on updated choice
- **WHEN** author and later critic differ because a local edit occurred between their spawns
- **THEN** each is checked against its own capture, while the same A/B wave still requires coherent selection
