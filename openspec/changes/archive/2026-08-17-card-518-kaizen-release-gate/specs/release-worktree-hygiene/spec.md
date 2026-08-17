# release-worktree-hygiene Delta Specification

## ADDED Requirements

### Requirement: Documentação canônica é validada antes do PR documental

O release guard SHALL resolver uma única data canônica por execução a partir de `RELEASE_DATE`, usando a data UTC corrente quando a variável estiver ausente. O valor MUST ser uma data válida no formato `YYYY-MM-DD`. Quando `docs/release-<data>.md` existir em `pre`, o arquivo MUST estar versionado, MUST estar livre dos placeholders `TBD`, `TODO`, `lorem`, `<!--`, `FIXME` e `<[A-Z_]+>`, e `PROD_DEPLOY_EVIDENCE` MUST estar preenchida. O `post` MUST repetir a validação da doc canônica. Dívida histórica fora da data canônica MUST NOT bloquear outra release em `pre`.

#### Scenario: PR de código ainda não possui doc final
- **WHEN** `pre` roda antes da publicação e `docs/release-<data>.md` ainda não existe
- **THEN** o check documental não exige uma evidência de deploy que ainda não pode existir

#### Scenario: Doc canônica contém placeholder
- **WHEN** `pre` encontra um dos padrões proibidos em `docs/release-<data>.md`
- **THEN** o guard falha com blocker que identifica arquivo e linha

#### Scenario: Doc canônica existe sem evidência final de deploy
- **WHEN** a doc da data existe em `pre`, mas `PROD_DEPLOY_EVIDENCE` está vazia
- **THEN** o guard bloqueia a entrada do PR documental

#### Scenario: Doc pós-deploy está pronta
- **WHEN** a doc da data está versionada, não contém placeholders e `PROD_DEPLOY_EVIDENCE` está preenchida
- **THEN** a validação documental do `pre` passa

#### Scenario: Data explícita é inválida
- **WHEN** `RELEASE_DATE` não representa uma data válida em `YYYY-MM-DD`
- **THEN** `pre` e `post` bloqueiam e `audit` reporta warning

### Requirement: Evidência kaizen da release bloqueia o post

Antes de concluir o `post`, o release guard MUST exigir que `docs/kaizen-log.md` esteja versionado e contenha um heading de nível 2 iniciado pela data canônica da release e identificado como auditoria de release por `Kaizen release` ou `/kaizen release`. Ausência dessa evidência MUST ser blocker em `post`. O `post` bem-sucedido SHALL ocorrer antes de mover os cards do pacote para `Pronto`.

#### Scenario: Não existe entrada kaizen da data
- **WHEN** `post` não encontra heading canônico de auditoria para a data da release
- **THEN** o guard bloqueia o fechamento antes de `Pronto`

#### Scenario: Existe somente triagem do mesmo dia
- **WHEN** o log contém um heading da data, mas ele não identifica `Kaizen release` nem `/kaizen release`
- **THEN** essa entrada não satisfaz o gate

#### Scenario: Auditoria da release está versionada
- **WHEN** o log versionado contém o heading canônico da data e a worktree está limpa
- **THEN** o gate de evidência kaizen passa

### Requirement: RELEASE_BRANCHES é entrada obrigatória e inequívoca do post

O `post` MUST exigir `RELEASE_BRANCHES` com pelo menos um nome. O guard SHALL normalizar por trim e deduplicação e MUST rejeitar token vazio, ref inválida ou nome fora dos prefixos `change-`, `card-` e `release-`. Após `git fetch --prune origin`, cada branch declarada MUST estar ausente em `refs/heads` e `refs/remotes/origin`; presença em qualquer lado MUST bloquear. O cleanup SHALL ocorrer antes de `Pronto`.

#### Scenario: Lista está ausente ou é vazia
- **WHEN** `post` recebe `RELEASE_BRANCHES` unset, vazia ou composta apenas por separadores/espaços
- **THEN** o guard bloqueia e não trata a prova de deleção como executada

#### Scenario: Token de branch é inválido
- **WHEN** a lista contém token vazio, ref inválida ou nome fora dos prefixos permitidos
- **THEN** o guard bloqueia com o token responsável

#### Scenario: Branch permanece localmente
- **WHEN** uma branch declarada ainda existe em `refs/heads`, mesmo ausente em `origin`
- **THEN** o guard bloqueia e informa `local=1 remote=0`

#### Scenario: Branch permanece remotamente
- **WHEN** uma branch declarada ainda existe em `refs/remotes/origin`, mesmo ausente localmente
- **THEN** o guard bloqueia e informa `local=0 remote=1`

#### Scenario: Todas as branches do pacote foram removidas
- **WHEN** todos os nomes canônicos estão ausentes local e remotamente após prune
- **THEN** o gate de package branch cleanup passa

## MODIFIED Requirements

### Requirement: Remote-first release comparison

The release workflow MUST compare publication state using `origin/develop` and `origin/main` after fetching remote refs. In `post`, local `main` MUST exist and equal `origin/main`; drift is a blocker until the operator performs an explicit fast-forward synchronization. The guard MUST NOT mutate local refs automatically.

#### Scenario: Local main is stale during audit or pre
- **WHEN** local `main` differs from `origin/main` outside the final `post`
- **THEN** the release guard uses `origin/main` for merge-state decisions and reports local drift as context according to the mode

#### Scenario: Local main is stale during post
- **WHEN** local `main` is absent or differs from `origin/main` in `post`
- **THEN** the guard blocks the closeout and instructs an explicit fast-forward sync

#### Scenario: Local main was fast-forwarded
- **WHEN** local `main` equals the freshly fetched `origin/main`
- **THEN** the local-main closeout gate passes

### Requirement: Post-release cleanup gate

The release workflow MUST run a strict post-release guard after deploy, versioned kaizen/release evidence, local-main synchronization and package branch deletion, and before moving package cards to `Pronto`. The gate MUST require `RELEASE_DATE`, or its UTC default, `RELEASE_CARDS`, `RELEASE_BRANCHES` and `PROD_DEPLOY_EVIDENCE` as applicable to their existing contracts.

#### Scenario: Release has incomplete closeout evidence
- **WHEN** remote refs are aligned but the kaizen entry is absent, local main is stale, package branches remain, or `RELEASE_BRANCHES` is absent
- **THEN** the post-release guard fails and cards remain before `Pronto`

#### Scenario: Release closeout is complete
- **WHEN** deploy evidence and canonical docs are present, kaizen is recorded, local main is aligned, package branches are absent and all other strict checks pass
- **THEN** `post` succeeds and the package may be handed off for promotion to `Pronto`
