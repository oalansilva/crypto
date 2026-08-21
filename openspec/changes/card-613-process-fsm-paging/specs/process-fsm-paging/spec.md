## ADDED Requirements

### Requirement: sessionStart injects only the Moore page for q
`scripts/process-fsm/` SHALL expose a paging module that, given cwd/path and an injectable `status_provider` / `resolve_fn` / `fsm`, returns `additional_context` for the Cursor `sessionStart` hook. The page MUST include the resolved tuple `(q, bound_card, q_git)`, the verbatim `context_file[q]` stub from `.cursor/process-fsm.yaml` when `q` is a known state, and MUST NOT include the release playbook (`release-guard pre`/`post`, `subir lote`, deploy PROD). The page MUST be at most 20 lines. When `bound_card` is `⊥` or `q` is missing, the page MUST use a fixed unbound stub that denies product Write and MUST NOT use the Homologado or release frames. Unit tests MUST inject `status_provider` (the production path: provider result becomes `q`) and MUST NOT call GitHub, Cursor hooks, or the live Project board.

#### Scenario: Todo page omits the release playbook
- **WHEN** `page()` is invoked with injected `status_provider` returning `Todo` and a bound card on `card-<id>-*`
- **THEN** `additional_context` contains the yaml `context_file[Todo]` stub
- **AND** it does not contain `release-guard`, `subir lote`, or `deploy PROD`
- **AND** it has at most 20 lines

#### Scenario: Homologado page is still not the release playbook
- **WHEN** `page()` is invoked with injected `status_provider` returning `Homologado` and a bound card
- **THEN** `additional_context` contains the yaml `context_file[Homologado]` stub
- **AND** it does not contain `release-guard pre`, `release-guard post`, or `deploy PROD`

#### Scenario: Unbound does not load Homologado
- **WHEN** `page()` is invoked with `bound_card=⊥` or `status_provider` returning `None`
- **THEN** `additional_context` uses the unbound stub
- **AND** it does not contain the Homologado `context_file` stub nor the release playbook

#### Scenario: Pytest without GitHub
- **WHEN** a contributor runs `pytest scripts/process-fsm -q` at the repo root
- **THEN** paging fixtures execute with injected status/resolve
- **AND** no network call to GitHub is made

### Requirement: sessionStart adapter is registered and fail-open
`.cursor/hooks.json` SHALL register a `sessionStart` command hook invoking `.cursor/hooks/process-fsm-session-start.sh`. The hook MUST emit valid JSON with `additional_context`. `failClosed` MUST NOT be true on this hook. Existing Guard (`preToolUse`, `beforeShellExecution`) and Impeccable (`afterFileEdit`, `stop`) entries MUST remain unchanged by this requirement. If Python/PyYAML fails, the adapter MUST still emit a minimal unbound page and MUST NOT dump `AGENTS.md` or `docs/crypto-overlay.md`.

#### Scenario: hooks.json lists sessionStart
- **WHEN** `.cursor/hooks.json` is loaded
- **THEN** `sessionStart` invokes the process-fsm session-start adapter
- **AND** Guard and Impeccable hooks are still present as distinct entries

#### Scenario: Python missing still pages unbound
- **WHEN** the session-start adapter cannot import the paging module
- **THEN** stdout is JSON with an unbound `additional_context`
- **AND** the overlay files are not included
