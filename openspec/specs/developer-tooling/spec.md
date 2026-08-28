# developer-tooling Specification

## Purpose
Configuração versionada da ferramenta de desenvolvimento ativa (Cursor Agent, Grok Build, OpenCode 1.18.18) e skills/commands OpenSpec, Impeccable e Kaizen.
## Requirements
### Requirement: Configuração versionada de ferramenta de desenvolvimento
O repositório SHALL conter configuração versionada do Cursor Agent em `.cursor/` (rules, skills, commands, hooks), do Grok Build em `.grok/`, e do adapter OpenCode 1.18.18 em `.opencode/plugin/` (auto-load). `opencode.json` MUST NOT permanecer como contrato ativo de modelo, MCP ou permission. `.opencode/plugins/` MUST NOT ser versionado em paralelo com `.opencode/plugin/`. Lock machine, `opencode.db` no kaizen, lease e attestation continuam proibidos.

#### Scenario: Config presente e válida
- **WHEN** o Cursor Agent inicia no repo
- **THEN** a configuração versionada em `.cursor/` é carregada
- **AND** nenhuma instrução Cursor aponta para `opencode.json` como fonte obrigatória de modelo/MCP/permission

#### Scenario: OpenCode plugin auto-load
- **WHEN** o OpenCode 1.18.18 inicia no repo
- **THEN** os módulos em `.opencode/plugin/` carregam sem `opencode.json`

#### Scenario: Sem segredos no repo
- **WHEN** a configuração versionada é inspecionada
- **THEN** nenhum token, chave ou credencial está presente nos arquivos versionados

### Requirement: Skills e fluxo OpenSpec disponíveis no Cursor
O Cursor SHALL carregar as skills do projeto (OpenSpec `/opsx-*`, design-critic, impeccable, playwright-cli, kaizen, `covenant-flow`, `covenant-flow-environments`, `implantar`) a partir de `.cursor/skills/`, `.cursor/commands/` e `.agents/skills/`, sem duplicar o conteúdo canônico das skills de produto.

#### Scenario: Skills carregadas automaticamente
- **WHEN** o Cursor inicia no repo pinado
- **THEN** as skills `openspec-*`, `design-critic`, `impeccable`, `playwright-cli`, `kaizen`, `covenant-flow`, `covenant-flow-environments` e `implantar` estão disponíveis

#### Scenario: Commands opsx disponíveis
- **WHEN** o usuário invoca `/opsx-new`, `/opsx-ff`, `/opsx-apply`, `/opsx-verify`, `/opsx-archive` ou equivalentes
- **THEN** o command em `.cursor/commands/` executa o fluxo OpenSpec via CLI

### Requirement: Proteção de design system na edição de UI
Edições de arquivos de UI em Cursor, Grok Build e OpenCode 1.18.18 SHALL acionar a detecção Impeccable no mesmo `.agents/skills/impeccable/scripts/hook.mjs` sem quebrar o turno. A pele só traduz o evento nativo. Não é um segundo detector.

#### Scenario: Hook de UI dispara na edição Cursor
- **WHEN** um arquivo de frontend é editado pelo Cursor
- **THEN** o hook em `.cursor/hooks.json` roda `.agents/skills/impeccable/scripts/hook.mjs` e reporta achados sem interromper a sessão

#### Scenario: Hook de UI dispara na edição Grok
- **WHEN** um arquivo de frontend é editado pelo Grok Build
- **THEN** `PostToolUse` / `Stop` em `.grok/hooks/` rodam o mesmo `hook.mjs` e reportam achados sem interromper a sessão

#### Scenario: Hook de UI dispara na edição OpenCode
- **WHEN** um arquivo de frontend é editado pelo OpenCode 1.18.18
- **THEN** `tool.execute.after` / `session.idle` no plugin rodam o mesmo `hook.mjs` e reportam achados sem interromper a sessão
- **AND** `tool.execute.after` mapeia `args.filePath` para `file_path` no stdin de `hook.mjs` com `hook_event_name=PostToolUse`
- **AND** `session.idle` mapeia `hook_event_name=Stop`

### Requirement: Subagent kaizen e command disponíveis
O Cursor SHALL expor o command `/kaizen` e um fluxo de auditoria read-only equivalente ao subagent kaizen.

#### Scenario: Command kaizen carregado
- **WHEN** o Cursor inicia no repo
- **THEN** `/kaizen` (e modos `card`/`release`) está disponível

#### Scenario: Auditoria sem mutação
- **WHEN** a auditoria kaizen é usada
- **THEN** ela não edita arquivos de produto, não altera board/Git/PRs e não reinicia serviços

### Requirement: Global environments skill is part of developer tooling
Developer tooling SHALL keep `covenant-flow-environments` aligned with overlay `environments.*`. A stale OpenClaw gateway map is a tooling defect, not an acceptable default. Packaged skill text MUST NOT hardcode Cripto unit names as the only topology; those values live in the consumer overlay.

#### Scenario: Skill content is audited
- **WHEN** the environments skill is reviewed
- **THEN** it does not list `openclaw-gateway.service` as an active service
- **AND** it reads Hermes and Cripto/Clara DEV/PROD units from overlay when present
- **AND** a project without `environments.prod` is treated as DEV-only

### Requirement: OpenSpec apply skill loads the approved prototype for UI cards
The `/opsx:apply` skill SHALL include a mandatory step for `UI impact: affected`: read `design.md` and the approved HTML prototype before editing product UI files. API specs remain integration contracts only.

#### Scenario: Apply skill lists the prototype step
- **WHEN** an agent runs `/opsx:apply` on a UI-affected change
- **THEN** the skill instructs loading `frontend/public/prototypes/<slug>/` before coding UI

### Requirement: Versioned local reviewer subagents exist
The repository SHALL contain `.cursor/agents/diff-reviewer.md` and `.cursor/agents/code-reviewer.md`, each with `readonly: true` and `model: inherit`.

#### Scenario: Reviewer files are versioned
- **WHEN** a Cursor Agent session starts in the repo
- **THEN** both agent files are available for delegation during Code Review
- **AND** each MUST declare `readonly: true` and `model: inherit`

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

