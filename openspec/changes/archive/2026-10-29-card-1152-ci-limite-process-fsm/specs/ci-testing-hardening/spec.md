## ADDED Requirements

### Requirement: process-fsm job time limit tolerates runner speed variation
The CI job `process-fsm` in `.github/workflows/ci.yml` MUST declare `timeout-minutes: 10`. The same line MUST carry a comment stating the reason: the GitHub runner speed varies, the job was cancelled at the 5-minute limit with all tests passing, and 10 minutes is about twice the slowest run measured. The time limits of the other CI jobs MUST NOT change in this card. The `qa-gate` job MUST keep depending on `process-fsm` with no change to its `needs` or logic.

#### Scenario: Slow runner finishes the tests before the limit
- **WHEN** the `process-fsm` job runs on a slow runner and its steps take between 5 and 10 minutes with all tests passing
- **THEN** the job concludes `success` and is not cancelled by time

#### Scenario: A real test failure still turns the job red
- **WHEN** a test under `scripts/process-fsm` fails
- **THEN** the `process-fsm` job concludes `failure` and the `qa-gate` stays red

#### Scenario: The reason sits next to the limit
- **WHEN** a reader opens the `process-fsm` job in `.github/workflows/ci.yml`
- **THEN** the `timeout-minutes: 10` line has a comment with the reason for the value

#### Scenario: Other job limits are untouched
- **WHEN** the diff of this card against `develop` is inspected
- **THEN** the only changed line in `.github/workflows/ci.yml` is the `timeout-minutes` line of `process-fsm`
