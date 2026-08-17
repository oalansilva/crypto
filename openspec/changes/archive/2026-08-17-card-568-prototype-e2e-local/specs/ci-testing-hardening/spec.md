## ADDED Requirements

### Requirement: Automated tests of static prototypes are hermetic
The CI Playwright job MUST be able to pass on a docs/harness-only commit without depending on the live DEV frontend being rebuilt or reachable.

#### Scenario: Harness-only push does not need live DEV
- **WHEN** a commit changes only harness/docs and the prototype files exist in the checkout
- **THEN** `e2e-playwright` MUST NOT fail because `https://dev.criptofarol.com.br` timed out
