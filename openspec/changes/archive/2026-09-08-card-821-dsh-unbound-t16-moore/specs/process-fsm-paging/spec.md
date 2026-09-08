## MODIFIED Requirements

### Requirement: sessionStart injects only the Moore page for q
`scripts/process-fsm/` SHALL expose a paging module that, given cwd/path and an injectable `status_provider` / `resolve_fn` / `fsm`, returns `additional_context` for the Cursor `sessionStart` hook. The page MUST include the resolved tuple `(q, bound_card, q_git)`, the verbatim `context_file[q]` stub from `.cursor/process-fsm.yaml` when `q` is a known state, and MUST NOT dump the release playbook (`release-guard pre`/`post`, deploy PROD, Homologado `context_file` stub). Naming the chat phrases of an explicit closeout (`suba a release`, `fechar release`, `subir lote`) on the unbound stub is not a playbook dump. The page MUST be at most 20 lines. When `bound_card` is `⊥`, the page MUST use a fixed unbound stub that denies product Write, MUST NOT use the Homologado or release frames, MUST NOT contain the absolute order `Não carregue playbook de release.`, and MUST state that an explicit closeout pedido (`suba a release` / `fechar release` / `subir lote`) loads overlay on-demand and starts T16. `enabled_events: (unbound)` remains paging display and MUST NOT be treated as T16 law. Status-unread `unread_page()` (bound card N) is out of this unbound exception and MAY keep the prior playbook order. When `bound_card` is issue N and `q` is missing (GraphQL quota remaining=0, RATE_LIMIT including HTTP 200, timeout, JSON failure, or empty Status nodes), the page MUST keep `bound_card=N`, MUST set `q` to missing, MUST NOT use the unbound stub, MUST NOT treat the card as off the Project, and MUST include the GraphQL reset time when the provider reports a quota error with reset. Unit tests MUST inject `status_provider` (the production path: provider result becomes `q`) and MUST NOT call GitHub, Cursor hooks, or the live Project board.

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
- **WHEN** `page()` is invoked with `bound_card=⊥`
- **THEN** `additional_context` uses the unbound stub
- **AND** it does not contain the Homologado `context_file` stub
- **AND** it does not contain `release-guard` or `deploy PROD`
- **AND** it contains `bound_card=⊥`
- **AND** it contains `Write produto deny`
- **AND** it has at most 20 lines

#### Scenario: Unbound stub is not a T16 deny of explicit closeout
- **WHEN** `page()` is invoked with `bound_card=⊥` and `q_git=develop`
- **THEN** `additional_context` does not contain `Não carregue playbook de release.`
- **AND** it contains `suba a release` and `fechar release`
- **AND** it states that the explicit pedido loads overlay and starts T16
- **AND** `enabled_events: (unbound)` remains on the page as paging display

#### Scenario: Bound card with GraphQL quota 0 is not unbound
- **WHEN** `page()` is invoked with bound card N and the status provider fails immediately with GraphQL remaining=0 and a reset time
- **THEN** `additional_context` keeps `bound_card=N`
- **AND** it MUST NOT use the unbound stub
- **AND** it MUST NOT contain `bound_card=⊥`
- **AND** it includes the reset time
- **AND** it has at most 20 lines
- **AND** it does not contain the Homologado `context_file` stub nor the release playbook

#### Scenario: Bound card with unread Status is not unbound
- **WHEN** `page()` is invoked with bound card N and `status_provider` returning `None` without a quota reset (timeout or empty nodes)
- **THEN** `additional_context` keeps `bound_card=N`
- **AND** it MUST NOT use the unbound stub
- **AND** it MUST NOT treat the card as off the board
- **AND** it does not contain the Homologado `context_file` stub nor the release playbook

#### Scenario: Status unread stub keeps the old playbook order
- **WHEN** `unread_page()` is invoked with bound card N
- **THEN** the returned stub contains `Não carregue playbook de release.`
- **AND** it MUST NOT equal the unbound stub
- **AND** a `page()` for that bound card with unread Status MUST NOT use the unbound stub

#### Scenario: Pytest without GitHub
- **WHEN** a contributor runs `pytest scripts/process-fsm -q` at the repo root
- **THEN** paging fixtures execute with injected status/resolve
- **AND** no network call to GitHub is made

### Requirement: sessionStart adapter is registered and fail-open
`.cursor/hooks.json` SHALL register a `sessionStart` command hook invoking `.cursor/hooks/process-fsm-session-start.sh`. The hook MUST emit valid JSON with `additional_context`. `failClosed` MUST NOT be true on this hook. Existing Guard (`preToolUse`, `beforeShellExecution`) and Impeccable (`afterFileEdit`, `stop`) entries MUST remain unchanged by this requirement. If Python/PyYAML fails, the adapter MUST still emit a minimal unbound page whose stub text equals the paging module `UNBOUND_PAGE` constant (Write deny plus the explicit-closeout exception; MUST NOT contain `Não carregue playbook de release.`) and MUST NOT dump `AGENTS.md` or the consumer overlay body (`overlay_doc`, Cripto: `docs/crypto-overlay.md`). The fallback MUST NOT hardcode `docs/crypto-overlay.md` as the product overlay path.

#### Scenario: hooks.json lists sessionStart
- **WHEN** `.cursor/hooks.json` is loaded
- **THEN** `sessionStart` invokes the process-fsm session-start adapter
- **AND** Guard and Impeccable hooks are still present as distinct entries

#### Scenario: Python missing still pages unbound
- **WHEN** the session-start adapter cannot import the paging module
- **THEN** stdout is JSON with an unbound `additional_context`
- **AND** that context contains the same unbound stub as `UNBOUND_PAGE`
- **AND** the overlay files (`overlay_doc` and `.covenant-flow/overlay.yaml`) are not included
- **AND** the fallback does not dump `docs/crypto-overlay.md` as a hardcoded body
- **AND** the fallback does not contain `Não carregue playbook de release.`
