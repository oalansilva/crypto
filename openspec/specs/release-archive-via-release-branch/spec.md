# release-archive-via-release-branch Specification

## Purpose
TBD - created by archiving change card-617-release-archive-via-release-branch. Update Purpose after archive.
## Requirements
### Requirement: Runbook documents release-* archive when develop push is protected
O runbook on-demand de release (`overlay_doc`, Cripto: `docs/crypto-overlay.md`, e a skill `covenant-flow` no consumidor pinado) SHALL documentar o caminho de closeout via branch `release-*` quando o push para `refs/heads/develop` é recusado por branch protection (incluindo required check `qa-gate`), **mesmo** quando `origin/develop` contém somente conteúdo Homologado do pacote. O stub always-on `AGENTS.md` MUST NOT carregar o playbook completo; MUST continuar apontando o overlay on-demand (`overlay_doc`) para tarefas de release. O caminho feliz `develop → main` MUST permanecer documentado para o caso em que o push do archive em `develop` é aceito.

#### Scenario: Protected develop blocks archive push with Homologado-only content
- **WHEN** o operador tenta publicar o archive OpenSpec do lote em `develop` e o remoto recusa com proteção que exige `qa-gate` (ou equivalente)
- **AND** `origin/develop` contém somente conteúdo Homologado do pacote
- **THEN** o runbook instrui criar/usar `release-*` com o archive, abrir PR para `main`, e NÃO exige bypass administrativo da proteção de `develop`

#### Scenario: Happy path develop to main still documented
- **WHEN** o push do archive para `develop` é aceito pela proteção
- **THEN** o runbook ainda documenta PR `develop → main` como caminho feliz
- **AND** `release-*` permanece o fallback sob proteção ou conteúdo não homologado

#### Scenario: Always-on stub stays thin
- **WHEN** um agente lê apenas `AGENTS.md` sem overlay
- **THEN** não encontra o playbook completo de `release-guard`/lote/PROD
- **AND** encontra indicação de carregar o path `overlay_doc` (Cripto: `docs/crypto-overlay.md`) para release

### Requirement: Closeout requires explicit main to develop sync after release-* merge
Após merge do PR `release-* → main` que carrega o archive (e demais paths de closeout do pacote), o runbook SHALL tornar **obrigatório e explícito** o sync `main → develop` (via PR ou merge) no closeout desse caminho, de forma que `origin/develop` e `origin/main` fiquem com o mesmo commit ou com árvores de conteúdo idênticas antes do `scripts/release-guard post` final e da promoção dos cards a `Pronto`. Se o primeiro `post` falhar por árvores divergentes, o runbook SHALL orientar reexecutar `post` após o sync.

#### Scenario: Post sees identical trees after sync
- **WHEN** o archive entrou em `main` via `release-*` e ainda não está em `origin/develop`
- **THEN** o closeout documenta sync `main → develop` como passo obrigatório
- **AND** após o sync, `release-guard post` pode validar alinhamento de refs/árvores sem blocker de conteúdo divergente causado pelo archive

#### Scenario: First post fails before sync
- **WHEN** o operador roda `scripts/release-guard post` após o merge em `main` mas antes do sync `main → develop`
- **AND** as árvores de `origin/develop` e `origin/main` diferem pelo archive
- **THEN** o `post` falha (contrato existente de alinhamento)
- **AND** o runbook orienta completar o sync e reexecutar `post`

