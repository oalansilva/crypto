# developer-tooling Specification

## Purpose
Configuração versionada da ferramenta de desenvolvimento ativa (Cursor Agent) e skills/commands OpenSpec, Impeccable e Kaizen.
## Requirements
### Requirement: Configuração versionada de ferramenta de desenvolvimento
O repositório SHALL conter configuração versionada do Cursor Agent em `.cursor/` (rules, skills, commands, hooks). `opencode.json` e `.opencode/` MUST NOT permanecer como contrato ativo.

#### Scenario: Config presente e válida
- **WHEN** o Cursor Agent inicia no repo
- **THEN** a configuração versionada em `.cursor/` é carregada
- **AND** nenhuma instrução ativa aponta para `.opencode/` como fonte obrigatória

#### Scenario: Sem segredos no repo
- **WHEN** a configuração versionada é inspecionada
- **THEN** nenhum token, chave ou credencial está presente nos arquivos versionados

### Requirement: Skills e fluxo OpenSpec disponíveis no Cursor
O Cursor SHALL carregar as skills do projeto (OpenSpec `/opsx-*`, design-critic, impeccable, playwright-cli, kaizen) a partir de `.cursor/skills/`, `.cursor/commands/` e `.agents/skills/`, sem duplicar o conteúdo canônico das skills de produto.

#### Scenario: Skills carregadas automaticamente
- **WHEN** o Cursor inicia no repo
- **THEN** as skills `openspec-*`, `design-critic`, `impeccable`, `playwright-cli` e `kaizen` estão disponíveis

#### Scenario: Commands opsx disponíveis
- **WHEN** o usuário invoca `/opsx-new`, `/opsx-ff`, `/opsx-apply`, `/opsx-verify`, `/opsx-archive` ou equivalentes
- **THEN** o command em `.cursor/commands/` executa o fluxo OpenSpec via CLI

### Requirement: Proteção de design system na edição de UI
Edições de arquivos de UI no Cursor SHALL acionar a detecção Impeccable sem quebrar o turno.

#### Scenario: Hook de UI dispara na edição
- **WHEN** um arquivo de frontend é editado pelo Cursor
- **THEN** o hook em `.cursor/hooks.json` roda `.agents/skills/impeccable/scripts/hook.mjs` e reporta achados sem interromper a sessão

### Requirement: Subagent kaizen e command disponíveis
O Cursor SHALL expor o command `/kaizen` e um fluxo de auditoria read-only equivalente ao subagent kaizen.

#### Scenario: Command kaizen carregado
- **WHEN** o Cursor inicia no repo
- **THEN** `/kaizen` (e modos `card`/`release`) está disponível

#### Scenario: Auditoria sem mutação
- **WHEN** a auditoria kaizen é usada
- **THEN** ela não edita arquivos de produto, não altera board/Git/PRs e não reinicia serviços

### Requirement: Global environments skill is part of developer tooling
Developer tooling SHALL keep `alan-workflow-ambientes` aligned with the live Oracle map. A stale OpenClaw gateway map is a tooling defect, not an acceptable default.

#### Scenario: Skill content is audited
- **WHEN** the environments skill is reviewed
- **THEN** it does not list `openclaw-gateway.service` as an active service
- **AND** it lists Hermes and the real Cripto/Clara DEV/PROD units

### Requirement: OpenSpec apply skill loads the approved prototype for UI cards
The `/opsx:apply` skill SHALL include a mandatory step for `UI impact: affected`: read `design.md` and the approved HTML prototype before editing product UI files. API specs remain integration contracts only.

#### Scenario: Apply skill lists the prototype step
- **WHEN** an agent runs `/opsx:apply` on a UI-affected change
- **THEN** the skill instructs loading `frontend/public/prototypes/<slug>/` before coding UI

### Requirement: Versioned review rules exist in the repo
The repository SHALL contain `.cursor/BUGBOT.md` at the project root and nested `backend/.cursor/BUGBOT.md` and `frontend/.cursor/BUGBOT.md`. Local reviewers SHALL read these files. Cursor project rules (`*.mdc`) MUST NOT be treated as a substitute.

#### Scenario: Root BUGBOT.md is present
- **WHEN** a local `diff-reviewer` run starts
- **THEN** `.cursor/BUGBOT.md` exists and encodes Cripto review constraints (PostgreSQL required, no SQLite, Design/`Pronto para Dev` not skippable, no secrets in commits, tests when `backend/**` changes, Playwright visual when UI changes)

#### Scenario: Nested rules apply by tree
- **WHEN** the reviewed diff includes `backend/` files
- **THEN** `backend/.cursor/BUGBOT.md` is available for that review
- **WHEN** the reviewed diff includes `frontend/` files
- **THEN** `frontend/.cursor/BUGBOT.md` is available for that review

### Requirement: Versioned local reviewer subagents exist
The repository SHALL contain `.cursor/agents/diff-reviewer.md` and `.cursor/agents/code-reviewer.md`, each with `readonly: true` and `model: inherit`.

#### Scenario: Reviewer files are versioned
- **WHEN** a Cursor Agent session starts in the repo
- **THEN** both agent files are available for delegation during Code Review
- **AND** each MUST declare `readonly: true` and `model: inherit`
