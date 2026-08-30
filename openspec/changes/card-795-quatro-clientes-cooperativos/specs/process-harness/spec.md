## MODIFIED Requirements

### Requirement: Always-on delta lives in AGENTS.md
The short always-on law (resolve `(q, bound_card, q_git)`, chat wording is not authorization, NLU is not δ, `Em Refinamento` is the entry column, `Todo` is not implementation, Design columns must not be skipped, overlay is on-demand, Alan-only T1/T7/T15, T16 is `process_event fechar_release`) SHALL live in the root `AGENTS.md` stub so Cursor, Grok Build, OpenCode, and dsh ingest it. `AGENTS.md` MUST remain at most 40 non-empty lines and MUST point to the consumer `overlay_doc` path (Cripto: `docs/crypto-overlay.md`) for ports/Drive/PostgreSQL/release. It MUST name Cursor Agent, Grok Build, OpenCode, and dsh as clients. It MUST state that the four clients are cooperative. It MUST NOT state that Cursor Auto is allowed. It MUST NOT contain `Auto permitido`. It MUST state that Grok Build, OpenCode, and dsh remain cooperative until their deny essays PASS. The deny-essay clause MUST NOT apply to Cursor (Cursor is cooperative by contract). It MUST NOT claim Auto OpenCode, Auto Grok, Auto dsh, or Auto Cursor. It MUST NOT include the 12-column runbook or `release-guard pre`/`post` snippets. The file header MUST NOT say the stub is “não always-on” after this change. Naming dsh in the stub MUST NOT depend on overlay key `clients.dsh`. Overlay `clients.*.auto` MUST NOT interpolate the stub text.

#### Scenario: Four clients read the same always-on stub
- **WHEN** a Cursor session, a Grok session, an OpenCode session, and a dsh session start in the repo
- **THEN** all four load root `AGENTS.md`
- **AND** that file states that chat wording is not δ and that `Todo` is not implementation
- **AND** it states Alan-only T1/T7/T15
- **AND** it names Cursor Agent, Grok Build, OpenCode, and dsh
- **AND** it does not claim Cursor Auto, Grok Auto, OpenCode Auto, or dsh Auto is active
- **AND** it does not contain `Auto permitido`
- **AND** it does not contain `scripts/release-guard pre`
- **AND** it names the consumer `overlay_doc` path (Cripto: `docs/crypto-overlay.md`)

#### Scenario: Yaml auto does not drive the stub
- **WHEN** overlay `clients.cursor.auto` is `true` or `false`
- **THEN** `render_agents()` emits the same hardcoded cooperative client lines
- **AND** the stub still does not contain `Auto permitido`
