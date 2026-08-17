## MODIFIED Requirements

### Requirement: Documentação canônica é validada antes do PR documental
O release guard SHALL resolver uma única data canônica por execução a partir de `RELEASE_DATE`, usando a data UTC corrente quando a variável estiver ausente. O valor MUST ser uma data válida no formato `YYYY-MM-DD`. Em `pre`, a existência de `docs/release-<data>.md` MUST NOT por si só exigir `PROD_DEPLOY_EVIDENCE`. O guard SHALL classificar o `pre` pelo diff de arquivos: `origin/main...HEAD` when the current branch matches `release-*`, otherwise `origin/main...origin/develop`. If that diff cannot be computed, the `pre` SHALL treat the PR as documental (fail-closed). A path is closeout/documental if it matches `docs/**`, `openspec/changes/archive/**`, `openspec/specs/**`, `AGENTS.md`, or `rules.md`. The PR is a **code PR** when the unpublished diff contains any path outside that allowlist. The PR is a **documental PR** when the canonical doc for the date exists and the unpublished diff is empty or a subset of the allowlist. `pre` SHALL require `PROD_DEPLOY_EVIDENCE`, a versioned file, and absence of placeholders `TBD`, `TODO`, `lorem`, `<!--`, `FIXME` and `<[A-Z_]+>` only for a documental PR. For a code PR on a day whose canonical doc already exists, `pre` MUST NOT require previous-lote evidence and SHALL warn that the doc will be updated after this package's deploy. MUST NOT exist a second doc for the same date. In `post`, when `PROD_DEPLOY_EVIDENCE` is set, the first token MUST resolve to a git object that is an **ancestor** of `origin/main` (equality allowed), `git diff --name-only <evidence>..origin/main` MUST be a subset of the closeout allowlist, and an abbreviation of that commit (≥7 hex, word-boundary) MUST appear at least once in the canonical doc. This MUST reject previous-lote evidence even if that SHA still appears in the doc. Equality of `origin/develop` and `origin/main` MUST NOT be the classifier for this section. The evidence SHA is the published **code/PROD** tip, not the post-documental-PR `origin/main` when that tip is docs-only ahead of the evidence. Dívida histórica fora da data canônica MUST NOT bloquear outra release em `pre`.

#### Scenario: PR de código ainda não possui doc final
- **WHEN** `pre` roda antes da publicação e `docs/release-<data>.md` ainda não existe
- **THEN** o check documental não exige uma evidência de deploy que ainda não pode existir

#### Scenario: PR de código no mesmo dia de uma doc já publicada
- **WHEN** `pre` roda e o unpublished diff contém path fora do allowlist de closeout
- **AND** `docs/release-<data>.md` já existe
- **AND** `PROD_DEPLOY_EVIDENCE` está vazia ou contém evidência de outro lote
- **THEN** o `pre` não emite blocker por ausência/reuso de evidência documental
- **AND** emite warning de que a doc canônica do dia será atualizada após o deploy deste pacote

#### Scenario: PR documental com develop diferente de main
- **WHEN** `pre` roda, a doc canônica da data existe
- **AND** o unpublished diff está vazio ou ⊆ allowlist (docs/kaizen/archive)
- **AND** `PROD_DEPLOY_EVIDENCE` está vazia
- **THEN** o guard bloqueia (PR documental do #518; `origin/develop` pode divergir de `origin/main`)

#### Scenario: Doc canônica contém placeholder no PR documental
- **WHEN** o PR é documental e `pre` encontra um dos padrões proibidos em `docs/release-<data>.md`
- **THEN** o guard falha com blocker que identifica arquivo e linha

#### Scenario: Doc pós-deploy está pronta
- **WHEN** o PR é documental, a doc da data está versionada, não contém placeholders e `PROD_DEPLOY_EVIDENCE` está preenchida
- **THEN** a validação documental do `pre` passa

#### Scenario: Post exige o SHA de código deste lote na doc
- **WHEN** `post` roda com `PROD_DEPLOY_EVIDENCE` cujo primeiro token é ancestral de `origin/main` mas `git diff --name-only <evidence>..origin/main` contém path fora do allowlist
- **THEN** o guard bloqueia (evidência de lote anterior; o SHA antigo pode ainda aparecer na doc)
- **WHEN** o token é ancestral de `origin/main`, o diff `evidence..origin/main` ⊆ allowlist, e uma abreviação (≥7 hex, word-boundary) aparece pelo menos uma vez na doc canônica
- **THEN** esse check passa mesmo se `origin/main` estiver à frente só com o PR documental

#### Scenario: Uma doc por data
- **WHEN** um segundo pacote é fechado no mesmo `RELEASE_DATE`
- **THEN** o fluxo atualiza o mesmo `docs/release-YYYY-MM-DD.md`
- **AND** MUST NOT adicionar uma segunda doc da mesma data

#### Scenario: Data explícita é inválida
- **WHEN** `RELEASE_DATE` não representa uma data válida em `YYYY-MM-DD`
- **THEN** `pre` e `post` bloqueiam e `audit` reporta warning
