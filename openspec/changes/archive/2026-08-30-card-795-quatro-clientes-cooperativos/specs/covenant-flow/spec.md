## MODIFIED Requirements

### Requirement: Product README lists four clients and Auto versus cooperative
The stranger block of the product README SHALL name Cursor, Grok, OpenCode, and dsh. It SHALL state that the four clients are cooperative. It SHALL state that Cursor is cooperative by contract and that Grok, OpenCode, and dsh remain cooperative until a deny essay PASS on the integration branch. It SHALL state that overlay `clients.*.auto` is a machine claim and does **not** drive the `AGENTS.md` stub. It SHALL state that Auto does **not** authorize crossing columns. The README MUST NOT claim that Auto is Cursor overlay `clients.cursor.auto: true`. The README MUST NOT claim Auto on Grok, OpenCode, or dsh. The README MUST NOT mention IDE/CLI `approvalMode` or Run Everything.

#### Scenario: Stranger block names four cooperative clients
- **WHEN** a visitor reads the client portion of the product README
- **THEN** Cursor, Grok, OpenCode, and dsh appear by name
- **AND** the text states that the four are cooperative
- **AND** the text does not state that Auto is Cursor `clients.cursor.auto: true`
- **AND** the text states that Auto does not authorize crossing columns
- **AND** the text does not claim Auto on Grok, OpenCode, or dsh

### Requirement: Pin example is the deliverable tag and pin does not copy README
The operator section of the product README SHALL document `--init` / `--pin` / Layout in PT-BR **after** the stranger and walkthrough blocks. The `--pin` example MUST be the semver tag of the commit that ships that README (this deliverable: `v1.1.5`; a later tagged README MUST update the example to that new tag). The example MUST NOT be `latest` or an unnumbered placeholder. `install.sh --pin` MUST NOT copy product `README.md` into the consumer. This change SHALL rewrite `render_agents()` and therefore the generated `AGENTS.md`. Overlay schema, `install.sh` copy list, skills, hooks, yaml law, Guard, and adapters MUST NOT be rewritten as part of this change. #787 MUST NOT be reopened as Apply.

#### Scenario: Operator section follows the stranger and uses the deliverable tag
- **WHEN** a visitor who already understood the product scrolls to Install / Pin / Layout
- **THEN** those sections are in PT-BR
- **AND** the `--pin` example is the deliverable tag (`v1.1.5` for this change)

#### Scenario: Pin still does not copy README into the consumer
- **WHEN** overlay is valid and `implantar --pin` completes on a consumer
- **THEN** the consumer tree does not receive a copy of the product `README.md` as a pin payload file
- **AND** #773, #784, and #787 are not reopened as Apply as a consequence of this change

## ADDED Requirements

### Requirement: render_agents hardcodes four cooperative clients
`render_agents()` SHALL hardcode four cooperative clients. The generated stub MUST contain exactly these two client lines, in this order: `Clientes: Cursor Agent (cooperativo); Grok Build, OpenCode e dsh (cooperativos até ensaio deny na branch de integração).` and `Não reivindique modo Auto no Cursor, no Grok, no OpenCode nem no dsh.` The function MUST NOT interpolate overlay `clients.*.auto`. The stub MUST NOT contain `Auto permitido`. The stub MUST NOT claim Auto Grok, Auto OpenCode, or Auto dsh. The deny-essay clause MUST apply only to Grok, OpenCode, and dsh. Cursor is cooperative by contract, not by a pending essay. The stub MUST remain at most 40 non-empty lines. `SCHEMA_MAJOR` SHALL remain `1`. `CLIENT_KEYS` SHALL remain `("cursor", "grok", "opencode")`.

#### Scenario: Generated stub is four cooperative clients
- **WHEN** `render_agents()` runs after this change
- **THEN** the text names Cursor Agent, Grok Build, OpenCode, and dsh
- **AND** it does not contain `Auto permitido`
- **AND** it does not contain Auto Grok, Auto OpenCode, or Auto dsh
- **AND** the deny-essay phrase applies only to Grok, OpenCode, and dsh
- **AND** overlay `clients.cursor.auto: true` in a fixture does not change the stub text

#### Scenario: Pin regenerates AGENTS.md from the new hardcode
- **WHEN** `implantar --pin` of this change's product tag completes on Cripto
- **THEN** consumer `AGENTS.md` matches the new `render_agents()` output
- **AND** `Auto permitido` is absent
- **AND** the stub was not hand-edited as the success path

### Requirement: Cripto overlay cooperative claim is false without schema break
Cripto overlay SHALL record `clients.cursor.auto: false` (grok, opencode, and dsh remain `false`). `validate_overlay` SHALL still accept that overlay (`SCHEMA_MAJOR` 1, `CLIENT_KEYS` three, extra `dsh` allowed) and MUST NOT start reading the `auto` boolean as a stub or Guard switch. This change's product tag SHALL be a patch (expected `v1.1.5`; Apply confirms origin has no newer tag, else the next unused patch). Apply MUST NOT change Guard, T0–T17, local Cursor IDE/CLI config, or Cripto `backend/**` / `frontend/src/**`.

#### Scenario: Overlay with four auto false validates
- **WHEN** `validate_overlay` runs on Cripto overlay with `clients.cursor.auto: false` and the other three `false`
- **THEN** validation passes
- **AND** `SCHEMA_MAJOR` is 1
- **AND** `CLIENT_KEYS` remains three names
- **AND** extra `clients.dsh.auto: false` is still accepted
