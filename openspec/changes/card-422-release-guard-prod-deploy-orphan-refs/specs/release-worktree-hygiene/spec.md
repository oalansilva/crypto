## MODIFIED Requirements

### Requirement: Post-release branch alignment MUST be semantic and safe
The release guard MUST accept post-release alignment when `origin/develop` and `origin/main` reference the same commit, or when `origin/develop` is an ancestor of `origin/main` and both refs have identical trees. It MUST reject histories with material content divergence or with integration history not represented by production. The guard SHALL additionally inventory orphan refs/worktrees in `post` mode and require classification before cleanup.

#### Scenario: Remote refs have the same commit
- **WHEN** post-release validation compares identical `origin/develop` and `origin/main` commit IDs
- **THEN** the alignment check succeeds

#### Scenario: Main contains develop with an identical tree
- **WHEN** `origin/develop` is an ancestor of `origin/main`, their commit IDs differ, and their trees are identical
- **THEN** the alignment check succeeds without requiring a reverse synchronization PR

#### Scenario: Remote trees differ
- **WHEN** `origin/develop` and `origin/main` contain different file trees
- **THEN** strict post-release validation fails

#### Scenario: Develop is not represented by main
- **WHEN** `origin/develop` is not an ancestor of `origin/main` even though their trees are identical
- **THEN** strict post-release validation fails

## ADDED Requirements

### Requirement: Evidência de deploy PROD antes de Pronto
O `release-guard pre` SHALL validar a evidência de deploy PROD (commit publicado no source PROD, services reiniciados, URL pública validada) antes de liberar cards para `Pronto`. Sem essa evidência, o modo estrito falha.

#### Scenario: Cards em Pronto sem evidência de deploy
- **WHEN** há cards do pacote em `Pronto` sem evidência de deploy PROD registrada
- **THEN** `release-guard pre` falha em modo estrito com blocker listando os cards

#### Scenario: Deploy PROD validado
- **WHEN** o commit publicado no source PROD, services reiniciados e URL pública validada estão registrados
- **THEN** `release-guard pre` aceita a evidência de deploy PROD

### Requirement: Inventário de refs e worktrees órfãs no post
O `release-guard post` SHALL inventariar refs `runtime-*`/`rollback-*`/`release-post-*`/`sync-*` e worktrees `preserve/*`, exigindo classificação (integrar/preservar/limpar com autorização) e sinalizando WIP não commitado.

#### Scenario: Refs órfãs sem classificação
- **WHEN** existem refs `runtime-*`/`rollback-*`/`release-post-*`/`sync-*` não classificadas
- **THEN** `release-guard post` lista cada ref com instrução de classificação e sinaliza WIP não commitado

#### Scenario: Worktree preserve com WIP
- **WHEN** uma worktree `preserve/*` contém arquivos modificados/untracked não commitados
- **THEN** `release-guard post` sinaliza o WIP e exige classificação antes do fechamento

#### Scenario: Tudo classificado
- **WHEN** todas as refs e worktrees órfãs foram classificadas ou limpas com autorização
- **THEN** `release-guard post` não reporta blockers de inventário
