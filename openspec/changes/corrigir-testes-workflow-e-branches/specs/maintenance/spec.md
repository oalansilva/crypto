## ADDED Requirements

### Requirement: Maintenance operations for test, branch, and file hygiene
The system SHALL perform maintenance operations to keep the project in a clean, operational state.

#### Scenario: Integration tests pass
- **WHEN** `pytest backend/tests/integration` is run
- **THEN** all tests pass or failures are documented as known issues with timestamps and issue references

#### Scenario: No stale feature branches remain
- **WHEN** `git branch -a` is run
- **THEN** no merged feature branches remain (feature/long-change, feature/monitor-candles-async-ui, feature/remover-locked-only-tela-carteira, feature/repemsar-layout, feature/workflow-backend-enforcement)

#### Scenario: test-results do not block upstream guard
- **WHEN** the upstream guard runs
- **THEN** `frontend/test-results/` is either ignored via .gitignore or committed, with no untracked files blocking the guard
