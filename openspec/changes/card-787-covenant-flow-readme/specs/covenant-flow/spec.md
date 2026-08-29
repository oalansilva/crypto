## ADDED Requirements

### Requirement: Product README orients a stranger in PT-BR before install
The product repository `oalansilva/covenant-flow` SHALL ship a single root `README.md` written in PT-BR. The README MUST explain, **before** any clone or `install.sh` block: what Covenant Flow is, who uses it, nucleus versus consumer versus overlay, that canal v1 is copy-and-commit in the consumer git, and that the first consumer is Cripto (`oalansilva/crypto`). Clone MUST NOT be the first paragraph. The product README MUST NOT require host backup paths. The product MUST NOT add a second install file (`CONTRIBUTING.md` or `docs/` install) as part of this orientation.

#### Scenario: Fresh clone visitor reads the README top-down
- **WHEN** a visitor opens the product `README.md` from a fresh clone of `oalansilva/covenant-flow` without opening skill `covenant-flow`
- **THEN** the file is in PT-BR
- **AND** before any clone or `install.sh --init` / `--pin` block it explains what the product does, who uses it, nucleus versus consumer versus overlay, and canal v1
- **AND** the clone command is not the first paragraph
- **AND** there is no `CONTRIBUTING.md` or second install file added by this change
- **AND** the README does not require `/home/ubuntu/backups/covenant-flow-pre-773-*` or SHA `94f8ed41` to install

### Requirement: Product README lists four clients and Auto versus cooperative
The stranger block of the product README SHALL name Cursor, Grok, OpenCode, and dsh. It SHALL state that Auto is Cursor overlay `clients.cursor.auto: true` (the client MAY run without a per-tool permission prompt) and that Auto does **not** authorize crossing columns. It SHALL state that Grok, OpenCode, and dsh are cooperative (`clients.*.auto: false`) until a deny essay PASS on the integration branch. The README MUST NOT claim Auto on Grok, OpenCode, or dsh.

#### Scenario: Stranger block names clients and Auto versus cooperative
- **WHEN** a visitor reads the client portion of the product README
- **THEN** Cursor, Grok, OpenCode, and dsh appear by name
- **AND** Auto (Cursor) is distinguished from cooperative (the other three, until deny essay PASS)
- **AND** the text states that Auto does not authorize crossing columns

### Requirement: Product README walkthrough is one line per column plus one human-gates sentence
The product README SHALL walk through all twelve `process-fsm.yaml` column names in PT-BR, including `Cancelado` as terminal, at **one line per column** (name + meaning). It SHALL include **exactly one** sentence for the three human gates: Alan prioritizes Em Refinamento→Todo; only Alan Aprovação de Design→Pronto para Dev; Alan homologates Done→Homologado. That sentence MUST NOT contain T0–T17 identifiers. The README MUST NOT include a T0–T17 / I1–I9 table, a paragraph per column, or hooks / OpenSpec order / release playbook. Skill `covenant-flow` remains the operator runbook.

#### Scenario: Walkthrough has twelve PT-BR lines and one gates sentence
- **WHEN** a visitor counts the column walkthrough in the product README
- **THEN** there are the twelve yaml names including `Cancelado` as terminal, one line each, names in PT-BR
- **AND** there is exactly one sentence of the three human gates without T0–T17 identifiers
- **AND** there is no T0–T17 / I1–I9 table and no hooks / OpenSpec / release playbook

### Requirement: GitHub repository description is the frozen PT-BR sentence
The GitHub repository `oalansilva/covenant-flow` description SHALL be exactly `Covenant Flow — processo portátil de 12 colunas (núcleo + adapters)`. That string SHALL ship in the same deliverable as the PT-BR README. LICENSE and GitHub homepage MUST NOT be changed by this requirement.

#### Scenario: Repo page shows the frozen description
- **WHEN** a visitor reads the GitHub description of `oalansilva/covenant-flow` after this deliverable
- **THEN** the description is exactly `Covenant Flow — processo portátil de 12 colunas (núcleo + adapters)`
- **AND** it replaces the English description `Covenant Flow — portable 12-column process (nucleus + adapters)`

### Requirement: Pin example is the deliverable tag and pin does not copy README
The operator section of the product README SHALL document `--init` / `--pin` / Layout in PT-BR **after** the stranger and walkthrough blocks. The `--pin` example MUST be the semver tag of the commit that ships that README (this deliverable: `v1.1.2`; a later tagged README MUST update the example to that new tag). The example MUST NOT be `latest` or an unnumbered placeholder. `install.sh --pin` MUST NOT copy product `README.md` into the consumer. Overlay schema, `install.sh` copy list, skills, hooks, yaml, generated `AGENTS.md`, and adapters MUST NOT be rewritten as part of this documentation change.

#### Scenario: Operator section follows the stranger and uses the deliverable tag
- **WHEN** a visitor who already understood the product scrolls to Install / Pin / Layout
- **THEN** those sections are in PT-BR
- **AND** the `--pin` example is the deliverable tag (`v1.1.2` for this change)

#### Scenario: Pin still does not copy README into the consumer
- **WHEN** overlay is valid and `implantar --pin` completes on a consumer
- **THEN** the consumer tree does not receive a copy of the product `README.md` as a pin payload file
- **AND** #773 and #784 remain closed as a consequence of this change
