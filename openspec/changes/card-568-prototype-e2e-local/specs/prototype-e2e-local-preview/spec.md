## ADDED Requirements

### Requirement: Prototype e2e uses the Playwright preview, not live DEV
End-to-end checks of files under `frontend/public/prototypes/` SHALL navigate the job's Playwright webServer/`PLAYWRIGHT_BASE_URL` (local preview). They MUST NOT `goto` `https://dev.criptofarol.com.br`.

#### Scenario: Walk-forward prototype check in CI
- **WHEN** `e2e-playwright` runs `walkforward-prototype-check`
- **THEN** the spec loads the prototype from the local preview origin
- **AND** it does not open `https://dev.criptofarol.com.br`

#### Scenario: Prototype missing in checkout
- **WHEN** the prototype HTML is absent from the checkout
- **THEN** the spec fails immediately as a missing fixture
- **AND** it SHALL NOT wait ~30s on an external URL timeout

### Requirement: App visual QA contract is unchanged
Versioned visual snapshots of product screens SHALL remain on the existing Playwright visual projects. This change MUST NOT weaken or retarget those baselines to live DEV.

#### Scenario: Product visual suite still uses preview
- **WHEN** `test:e2e:visual` runs
- **THEN** it continues to use the configured Playwright `baseURL`/webServer, not `dev.criptofarol.com.br`
