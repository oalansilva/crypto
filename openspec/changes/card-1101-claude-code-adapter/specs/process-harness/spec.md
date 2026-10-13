## MODIFIED Requirements

### Requirement: Always-on delta lives in AGENTS.md
The short always-on law (resolve `(q, bound_card, q_git)`, chat wording is not authorization, NLU is not δ, `Em Refinamento` is the entry column, `Todo` is not implementation, Design columns must not be skipped, overlay is on-demand, Alan-only T1/T7/T15/T18, T16 is `process_event fechar_release`) SHALL live in the root `AGENTS.md` stub so Cursor, Grok Build, OpenCode, dsh, and Codex local ingest it; Claude Code SHALL ingest the same stub through a root `CLAUDE.md` that only imports `AGENTS.md`. `AGENTS.md` MUST remain at most 40 non-empty lines and MUST point to the consumer `overlay_doc` path (Cripto: `docs/crypto-overlay.md`) for ports/Drive/PostgreSQL/release. It MUST name all five official clients and state they are cooperative. Claude Code is not an official client: `AGENTS.md` MUST NOT name it as a client, and naming it requires a separate follow-up change (renderer `render_agents`, pin and board description). It MUST NOT claim Auto for any client, interpolate `clients.*.auto`, contain `Auto permitido`, or copy the 12-column runbook or `release-guard pre`/`post` snippets. Its header MUST NOT say the stub is “não always-on”. The deny-essay clause for Grok/OpenCode/dsh/Codex MUST NOT turn Cursor into an Auto claim. Naming Codex or dsh MUST NOT depend on a new overlay key.

#### Scenario: Five clients read the same stub
- **WHEN** sessions in the five clients start in the repo
- **THEN** each loads root `AGENTS.md` with the same δ/Status/human-gate guidance
- **AND** Codex CLI and IDE local see the same file
- **AND** the stub names all five clients, Alan-only T1/T7/T15/T18 and consumer `overlay_doc`
- **AND** it contains no Auto claim, `Auto permitido`, FSM table, or release script body

#### Scenario: Overlay auto flags do not drive the stub
- **WHEN** an overlay `clients.*.auto` value changes
- **THEN** `render_agents()` still emits cooperative client wording
- **AND** it does not say `Auto permitido`

#### Scenario: Claude Code reads the stub without being named
- **WHEN** a Claude Code session starts in the repo
- **THEN** it loads `AGENTS.md` through `CLAUDE.md`
- **AND** `AGENTS.md` does not name Claude Code as a client
