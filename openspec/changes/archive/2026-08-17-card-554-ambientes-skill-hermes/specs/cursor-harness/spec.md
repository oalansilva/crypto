## ADDED Requirements

### Requirement: Cursor loads the current environments skill
The Cursor harness SHALL treat `alan-workflow-ambientes` as the environment map and SHALL NOT treat OpenClaw Gateway as the active runtime in that skill.

#### Scenario: Skill available in Cursor
- **WHEN** a Cursor session starts a task that can affect DEV or PROD
- **THEN** the environments skill is loaded with Hermes as the active agent runtime map
