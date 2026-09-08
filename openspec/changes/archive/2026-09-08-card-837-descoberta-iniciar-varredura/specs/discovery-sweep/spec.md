# Delta — discovery-sweep — Iniciar começa a varredura da seleção atual (card #837)

## MODIFIED Requirements

### Requirement: Start begins a new sweep from the on-screen draft

After a terminal sweep (cancelled, failed, partial_failure, completed), creation SHALL treat the on-screen selection (templates, symbols, timeframes, directions, period) as a new start: it SHALL persist a new sweep for the submitted selection even when that selection equals the dead run's, SHALL never reopen the dead run, and SHALL NOT return the draft-conflict rejection for this path. The happy path SHALL NOT require "Novo rascunho".

#### Scenario: Post-terminal start with changed selection

- **WHEN** the previous sweep is terminal and the operator changes the selection and clicks Iniciar
- **THEN** a new sweep with that selection is created and progress appears
- **AND** no draft-conflict failure is returned

#### Scenario: Post-terminal start with identical selection

- **WHEN** the previous sweep is terminal and the selection is unchanged and the operator clicks Iniciar
- **THEN** a new sweep is created
- **AND** the dead run is not reopened

#### Scenario: Reload after cancel does not pin to the old run

- **WHEN** the operator reloads after cancel, builds another selection and clicks Iniciar
- **THEN** a new sweep starts with no second button and no browser-data clearing

### Requirement: Start while a sweep is live never forks

While a sweep is non-terminal (pending, running, paused, cancelling), creation with a different selection SHALL create no second sweep and SHALL NOT replace the live one; the response and the UI SHALL direct the operator to cancel first. A repeat start for the same selection while its sweep is being created or is live SHALL return the existing sweep without duplication, and the screen SHALL show it.

#### Scenario: Other selection while live is blocked with guidance

- **WHEN** a sweep is live and the operator picks another selection and clicks Iniciar
- **THEN** no second sweep is created
- **AND** the screen directs the operator to cancel before starting another

#### Scenario: Repeat start on the same live selection shows the existing sweep

- **WHEN** Iniciar just fired (or that selection's sweep is still live) and the operator clicks again on the same selection
- **THEN** no duplicate is born
- **AND** the screen shows the existing sweep

### Requirement: Start failures speak operations language

Any start failure surfaced in the UI SHALL be an operations sentence (what to do next) and SHALL NOT expose JSON or jargon.

#### Scenario: Failure text is operational

- **WHEN** starting fails and the screen shows an error
- **THEN** the text is an operations instruction
- **AND** no JSON or jargon is shown
