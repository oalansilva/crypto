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
Após merge do PR `release-* → main` que carrega o archive (e demais paths de closeout do pacote), o runbook SHALL tornar **obrigatório e explícito** o sync `main → develop` no closeout desse caminho, de forma que `origin/main` fique ancestral de `origin/develop` (produção contida na develop) antes do `scripts/release-guard post` final e da promoção dos cards a `Pronto`. Extra na develop SHALL ser aviso, não blocker. Árvores idênticas MUST NOT ser exigidas. O sync MUST ser **um** PR de merge normal `main → develop`. O runbook MUST recusar: PR que substitui a ponta de develop pela árvore de produção; merge que descarta o lado da develop; apagar o Done da ponta e devolvê-lo depois. Se o primeiro `post` falhar porque develop não contém produção, o runbook SHALL orientar completar o merge normal e reexecutar `post`. Overlay passo 5b SHALL usar este predicado (containment + extra = aviso), não árvores idênticas.

#### Scenario: Post sees develop containing production after one merge-normal PR
- **WHEN** o lote entrou em `main` via `release-*` e ainda não está em `origin/develop`
- **THEN** o closeout documenta um único PR merge normal `main → develop` como passo obrigatório
- **AND** após esse merge, `release-guard post` valida alinhamento com produção contida na develop
- **AND** extra na develop é aviso, não blocker

#### Scenario: First post fails before sync
- **WHEN** o operador roda `scripts/release-guard post` após o merge em `main` mas antes do sync `main → develop`
- **AND** `origin/main` não é ancestral de `origin/develop`
- **THEN** o `post` falha (develop não contém produção)
- **AND** o runbook orienta completar o merge normal `main → develop` e reexecutar `post`

#### Scenario: Three-PR dance and replace-develop are refused
- **WHEN** o closeout documenta o sync pós-produção
- **THEN** o runbook recusa substituir a develop pela ponta de produção, merge que descarta o outro lado, e restore do Done
- **AND** o padrão de um merge normal (ensaio: #924) é o aceite
- **AND** o padrão #926 e a sequência #913+#914+#915 MUST NOT ser o aceite

