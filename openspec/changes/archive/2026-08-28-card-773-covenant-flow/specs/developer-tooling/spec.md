## MODIFIED Requirements

### Requirement: Skills e fluxo OpenSpec disponíveis no Cursor
O Cursor SHALL carregar as skills do projeto (OpenSpec `/opsx-*`, design-critic, impeccable, playwright-cli, kaizen, `covenant-flow`, `covenant-flow-environments`, `implantar`) a partir de `.cursor/skills/`, `.cursor/commands/` e `.agents/skills/`, sem duplicar o conteúdo canônico das skills de produto.

#### Scenario: Skills carregadas automaticamente
- **WHEN** o Cursor inicia no repo pinado
- **THEN** as skills `openspec-*`, `design-critic`, `impeccable`, `playwright-cli`, `kaizen`, `covenant-flow`, `covenant-flow-environments` e `implantar` estão disponíveis

#### Scenario: Commands opsx disponíveis
- **WHEN** o usuário invoca `/opsx-new`, `/opsx-ff`, `/opsx-apply`, `/opsx-verify`, `/opsx-archive` ou equivalentes
- **THEN** o command em `.cursor/commands/` executa o fluxo OpenSpec via CLI

### Requirement: Global environments skill is part of developer tooling
Developer tooling SHALL keep `covenant-flow-environments` aligned with overlay `environments.*`. A stale OpenClaw gateway map is a tooling defect, not an acceptable default. Packaged skill text MUST NOT hardcode Cripto unit names as the only topology; those values live in the consumer overlay.

#### Scenario: Skill content is audited
- **WHEN** the environments skill is reviewed
- **THEN** it does not list `openclaw-gateway.service` as an active service
- **AND** it reads Hermes and Cripto/Clara DEV/PROD units from overlay when present
- **AND** a project without `environments.prod` is treated as DEV-only

## REMOVED Requirements

### Requirement: Versioned review rules exist in the repo
**Reason:** Card #773 removes Cursor Bugbot and the file `BUGBOT.md` (name and content) from the portable product. Review constraints move into `diff-reviewer` and `code-reviewer`.
**Migration:** Encode former `BUGBOT.md` constraints in `.cursor/agents/diff-reviewer.md` and `.cursor/agents/code-reviewer.md`. Optional consumer `REVIEW.md` MUST NOT mention Bugbot. Delete `.cursor/BUGBOT.md`, `backend/.cursor/BUGBOT.md`, and `frontend/.cursor/BUGBOT.md` at Cripto pin (not as aliases).

## ADDED Requirements

### Requirement: Review stance lives in local reviewer agents
The repository SHALL contain `.cursor/agents/diff-reviewer.md` and `.cursor/agents/code-reviewer.md`, each with `readonly: true` and `model: inherit`, and those files SHALL carry review constraints (Design/`Pronto para Dev` not skippable, no secrets in commits, consumer overlay `runtime.database` when present, tests when backend changes, Playwright visual when UI changes). `REVIEW.md` MAY exist and MUST NOT mention Bugbot. `BUGBOT.md` MUST NOT exist. Cursor Bugbot MUST NOT be the Code Review path.

#### Scenario: Reviewer files carry the stance
- **WHEN** a local `diff-reviewer` run starts
- **THEN** `.cursor/agents/diff-reviewer.md` exists and encodes the review constraints
- **AND** `.cursor/BUGBOT.md` does not exist

#### Scenario: Nested BUGBOT.md is gone
- **WHEN** the reviewed diff includes `backend/` or `frontend/` files
- **THEN** no nested `BUGBOT.md` is required
- **AND** the same agent files apply

### Requirement: Consumer git commits materialized harness skins
A pinned consumer SHALL keep `.cursor/`, `.grok/`, `.opencode/`, `scripts/process-fsm/`, `.agents/skills/` (impeccable, design-critic, playwright-cli), and generated `AGENTS.md` as committed trees produced by `implantar --pin`. Those paths MUST NOT be gitignored as the install method and MUST NOT be a submodule as the v1 channel.

#### Scenario: Pinned consumer shows skins in git
- **WHEN** Cripto is pinned in the card worktree
- **THEN** `git ls-files` includes `.cursor/hooks.json`, `.grok/` adapter files, `.opencode/plugin/`, `scripts/process-fsm/`, `.agents/skills/impeccable/`, and `AGENTS.md`
- **AND** overlay `.covenant-flow/overlay.yaml` contains `pin` matching the product tag
