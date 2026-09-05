# release-worktree-hygiene Specification

## Purpose
TBD - created by archiving change integrate-backup-wip-flow-cleanup. Update Purpose after archive.
## Requirements
### Requirement: Generated output excluded from release integration
The repository SHALL ignore root-level generated operational output so debug artifacts are not treated as releasable source files.

#### Scenario: Playwright debug output exists locally
- **WHEN** a local run creates files under `output/playwright`
- **THEN** `git status --short` does not report those files as untracked release work

### Requirement: Preserved WIP is classified before release cleanup
The release workflow MUST classify saved WIP as integrated, intentionally excluded, or still preserved before removing backup branches or worktrees.

#### Scenario: Backup branch contains source and debug artifacts
- **WHEN** a saved backup branch is reviewed after release
- **THEN** useful source changes are integrated through a normal branch and debug artifacts are excluded from `develop` and `main`

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

### Requirement: Automated release guard
The release workflow MUST provide a repository command that audits worktrees, branches, stashes, tracked ignored files, generated artifacts, and remote `develop`/`main` alignment.

#### Scenario: Agent audits release hygiene
- **WHEN** an agent runs the release guard in audit mode
- **THEN** the command reports detected hygiene issues without deleting or modifying repository work.

#### Scenario: Strict release gate finds hidden work
- **WHEN** an agent runs the release guard in a strict release mode and the repository has stashes, dirty worktrees, unmerged branches, or tracked ignored files
- **THEN** the command exits non-zero and lists the blocking items.

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

### Requirement: Snapshots remotos únicos e frescos por execução
O release guard MUST invocar os loaders de snapshots no shell principal por statements simples, nunca invocá-los dentro de command substitution, e SHALL permitir que cada loader use command substitution internamente para capturar `gh` desde que atribua seus próprios globals e trate o exit status. Em `post` e `audit`, o guard SHALL carregar no máximo uma vez o Project em `BOARD_JSON`/`BOARD_STATE` e no máximo uma vez os PRs abertos em `PRS_JSON`/`PRS_STATE`, reutilizando esses globals em todos os consumidores. O guard MUST NOT persistir ou compartilhar cache entre execuções e MUST NOT introduzir `flock` ou lock global.

#### Scenario: Múltiplas branches e checks usam os mesmos snapshots
- **WHEN** uma execução avalia múltiplas branches, changes terminais, campos, homologação e PRs abertos
- **THEN** o guard executa exatamente uma listagem do Project e uma listagem global de PRs e resolve os demais lookups localmente

#### Scenario: Nova execução começa
- **WHEN** o guard é executado novamente após um run anterior
- **THEN** ele refaz os snapshots e não reutiliza dados persistidos ou compartilhados

#### Scenario: Modo pre é executado
- **WHEN** o guard opera em `pre`
- **THEN** ele não executa listagem do Project, listagem de PRs nem inventário GraphQL de idade

### Requirement: Snapshot somente é válido quando completo e bem-sucedido
O snapshot do Project SHALL ser válido somente quando o comando terminar com exit code zero, o JSON for válido, `.items` for array, `totalCount` estiver presente como inteiro não negativo e o tamanho de `.items` for exatamente igual a `totalCount`. O snapshot de PRs SHALL ser válido somente quando o comando terminar com exit code zero, o JSON de topo for array, houver menos de 1.000 itens e cada entrada contiver `headRefName` e `headRepositoryOwner.login` como strings não vazias; atingir 1.000 itens SHALL significar truncamento. Snapshot inválido, malformado ou truncado MUST assumir estado `failed`.

#### Scenario: JSON válido acompanha exit code de falha
- **WHEN** um comando remoto retorna JSON parseável e exit code diferente de zero
- **THEN** o snapshot correspondente fica `failed`

#### Scenario: Project retorna menos itens que totalCount
- **WHEN** `.items` é array, mas seu tamanho é menor que `totalCount`
- **THEN** `BOARD_STATE` fica `failed` e nenhum lookup trata o conteúdo como autoritativo

#### Scenario: Project retorna mais itens que totalCount
- **WHEN** `.items` é array, mas seu tamanho é maior que `totalCount`
- **THEN** `BOARD_STATE` fica `failed` por divergência de completude

#### Scenario: totalCount está ausente ou malformado
- **WHEN** `totalCount` está ausente, é negativo ou não é inteiro
- **THEN** `BOARD_STATE` fica `failed`

#### Scenario: Project não retorna array de itens
- **WHEN** `.items` está ausente ou não é array
- **THEN** `BOARD_STATE` fica `failed`

#### Scenario: Lista de PRs atinge o limite
- **WHEN** a listagem global retorna 1.000 itens
- **THEN** `PRS_STATE` fica `failed` por possível truncamento

#### Scenario: Lista de PRs contém JSON inválido
- **WHEN** a resposta da listagem de PRs não pode ser validada
- **THEN** `PRS_STATE` fica `failed` e nenhum branch recebe `pr_open=no` a partir dessa resposta

#### Scenario: Resposta de PRs não é array
- **WHEN** a listagem de PRs retorna JSON válido cujo valor de topo não é array
- **THEN** `PRS_STATE` fica `failed` e a resposta não é tratada como lista vazia

#### Scenario: Entrada de PR não possui identidade completa
- **WHEN** qualquer entrada não possui `headRefName` ou `headRepositoryOwner.login` como string não vazia
- **THEN** `PRS_STATE` fica `failed` e nenhum lookup usa a fotografia

### Requirement: Lookups locais preservam estado desconhecido
O release guard MUST procurar cards pela chave `(repository=oalansilva/crypto, issue number canônico)` e MUST NOT aceitar item de outro repositório com o mesmo número. O guard MUST classificar a chave como `terminal` somente para Status `Pronto` ou `Cancelado`, como `non-terminal` para outro Status conhecido e como `unknown` para falha de snapshot, chave ausente ou duplicada, ou Status ausente. O lookup de PR MUST usar a chave `(headRepositoryOwner.login, headRefName)` e somente owner `oalansilva` com o nome da branch consultada SHALL corresponder à branch de `oalansilva/crypto`. O lookup MUST preservar `unknown` quando `PRS_STATE` não for autoritativo. `unknown` SHALL produzir blocker em `post` e warning em `audit`.

#### Scenario: Card terminal é encontrado uma vez
- **WHEN** exatamente um card possui o número esperado e Status `Pronto` ou `Cancelado`
- **THEN** o lookup local retorna `terminal`

#### Scenario: Card conhecido ainda está em fluxo
- **WHEN** exatamente um card possui o número esperado e outro Status não vazio
- **THEN** o lookup local retorna `non-terminal` sem representar falha remota

#### Scenario: Card está ausente, duplicado ou sem Status
- **WHEN** zero ou múltiplos cards correspondem à chave qualificada, ou o único item não possui Status
- **THEN** o lookup retorna `unknown`

#### Scenario: Branch referencia número presente em outro repositório
- **WHEN** o número derivado de uma branch existe somente em item de outro repositório do Project
- **THEN** o lookup retorna `unknown` e não classifica a branch a partir desse item

#### Scenario: Snapshot de PR falha
- **WHEN** `PRS_STATE` está `failed`
- **THEN** o lookup de qualquer branch retorna `unknown` e nunca `pr_open=no`

#### Scenario: Fork possui branch com o mesmo nome
- **WHEN** existe PR aberto com `headRefName` igual à branch consultada, mas `headRepositoryOwner.login` é diferente de `oalansilva`
- **THEN** esse PR não corresponde à chave da branch de `oalansilva/crypto` e, na ausência da chave qualificada alvo, o lookup produz `pr_open=no`

#### Scenario: Owner e branch correspondem
- **WHEN** existe PR aberto com `headRepositoryOwner.login=oalansilva` e `headRefName` igual à branch consultada
- **THEN** o lookup qualificado produz `pr_open=yes`

### Requirement: Falha de snapshot é global e imediata
O release guard MUST avaliar falhas de `BOARD_STATE` e `PRS_STATE` no nível global do modo, sem depender da existência ou ordem de consumidores. Qualquer falha SHALL ser blocker em `post` e warning em `audit`.

#### Scenario: Falha ocorre em post
- **WHEN** qualquer snapshot obrigatório falha em `post`
- **THEN** o guard registra blocker com causa explícita e termina sem sucesso

#### Scenario: A mesma falha ocorre em audit
- **WHEN** o mesmo snapshot falha em `audit`
- **THEN** o guard registra warning explícito e não apresenta o estado como conhecido

#### Scenario: Não há consumidores relevantes
- **WHEN** um snapshot falha sem branch ou card que o consumiria em uma seção posterior
- **THEN** a falha ainda é reportada imediatamente conforme o modo

### Requirement: RELEASE_CARDS possui identidade canônica e inequívoca
O release guard MUST normalizar `RELEASE_CARDS` uma única vez por trim, remoção de zeros à esquerda e deduplicação. Cada token SHALL ser um inteiro decimal entre 1 e 2147483647. Em `post`, formato inválido MUST bloquear antes de qualquer chamada remota. Em `audit`, formato inválido SHALL gerar warning, MUST impedir chamadas remotas dependentes do pacote e MUST permitir que checks independentes continuem. A identidade SHALL ser a tupla `(repository=oalansilva/crypto, issue number canônico)`. Cada tupla MUST aparecer exatamente uma vez no snapshot e possuir Status; item de outro repositório com o mesmo número MUST NOT corresponder. O mesmo item qualificado SHALL ser reutilizado nos checks de campos e homologação.

#### Scenario: Espaços e zeros à esquerda são normalizados
- **WHEN** `RELEASE_CARDS` contém ` 480, 0480 `
- **THEN** o guard produz um único ID canônico `480` e o valida uma vez

#### Scenario: Token é inválido
- **WHEN** `RELEASE_CARDS` contém token vazio, não numérico, zero, negativo ou maior que 2147483647 em `post`
- **THEN** o guard bloqueia antes de executar qualquer chamada remota

#### Scenario: Token é inválido em audit
- **WHEN** `RELEASE_CARDS` contém token inválido em `audit`
- **THEN** o guard emite warning, não executa chamadas remotas dependentes do pacote e continua checks independentes

#### Scenario: Card normalizado está ausente ou duplicado
- **WHEN** a tupla do repositório alvo e ID canônico aparece zero ou mais de uma vez no snapshot
- **THEN** `post` registra blocker para esse ID

#### Scenario: Mesmo número existe somente em outro repositório
- **WHEN** o snapshot contém o número canônico em outro repositório, mas não em `oalansilva/crypto`
- **THEN** o lookup não aceita esse item e retorna `unknown`

#### Scenario: Ambiguidade de identidade ocorre em audit
- **WHEN** a tupla alvo está ausente, duplicada ou sem Status em `audit`
- **THEN** o guard emite warning e não representa o card como conhecido

#### Scenario: Card normalizado não possui Status
- **WHEN** o único item correspondente não possui Status
- **THEN** `post` registra blocker e não valida campos ou homologação como bem-sucedidos

#### Scenario: Cards normalizados são inequívocos
- **WHEN** todos os IDs aparecem exatamente uma vez e possuem Status
- **THEN** campos obrigatórios e homologação usam os mesmos itens do snapshot sem nova listagem do Project

### Requirement: Diagnóstico de rate limit ocorre somente após falha
Após uma ou mais falhas de snapshot, o release guard SHALL imprimir remaining e reset dos **cabeçalhos GraphQL** da resposta da fotografia que falhou, no máximo uma vez por execução (Q2=A). O loader da fotografia MUST capturar esses cabeçalhos na mesma chamada GraphQL (`item-list` / equivalente `gh api graphql --include`). MUST NOT consultar o endpoint REST `GET /rate_limit` nem imprimir `.resources.graphql.remaining` do contador REST. MUST NOT abrir uma segunda query GraphQL só para ler cota. MUST NOT reabrir a fotografia completa do board além da uma por execução (#509). O diagnóstico MUST preservar a causa original. O guard MUST NOT imprimir esse diagnóstico preventivamente e MUST NOT executar retry, polling ou espera automática.

#### Scenario: Snapshot falha com diagnóstico disponível
- **WHEN** uma carga de snapshot GraphQL falha e os cabeçalhos dessa resposta informam remaining e reset
- **THEN** a mensagem inclui esses valores (não o contador REST) e preserva a falha original conforme o modo

#### Scenario: REST remaining 5000 is not printed as GraphQL quota
- **WHEN** uma fotografia GraphQL falha com cabeçalhos remaining=0 e o REST `GET /rate_limit` reportaria `resources.graphql.remaining=5000`
- **THEN** o diagnóstico imprime remaining=0 e o reset GraphQL
- **AND** o guard faz zero chamadas `GET /rate_limit` para este diagnóstico

#### Scenario: Snapshot é carregado com sucesso
- **WHEN** os snapshots são válidos
- **THEN** o guard não imprime diagnóstico de cota GraphQL preventivamente

#### Scenario: Ambos os snapshots falham
- **WHEN** Project e PRs falham na mesma execução
- **THEN** o guard imprime o diagnóstico de cabeçalhos GraphQL no máximo uma vez e preserva as falhas originais

### Requirement: Orçamento GraphQL é limitado por modo
O release guard MUST respeitar estes máximos por execução: `pre` com zero `item-list`, zero `pr list`, zero páginas de idade e zero diagnóstico de rate limit; `post` com até um `item-list`, até um `pr list` e zero páginas de idade; `audit` com até um `item-list`, até um `pr list` e até 19 páginas GraphQL de idade. Requisições REST de comments por card para homologação ou divergência de título SHALL permanecer permitidas em `pre|post|audit` e excluídas desse orçamento GraphQL.

#### Scenario: Post avalia várias branches
- **WHEN** `post` avalia qualquer quantidade de branches
- **THEN** ele não excede uma listagem do Project, uma listagem de PRs e não consulta páginas de idade

#### Scenario: Audit percorre inventário de idade extenso
- **WHEN** `audit` encontra mais páginas de idade após a décima nona requisição total
- **THEN** ele emite warning explícito de inventário parcial ou truncado e encerra a paginação sem executar a vigésima requisição

#### Scenario: Evidência exige comments por card
- **WHEN** homologação ou divergência de título requer leitura de comments REST
- **THEN** o guard pode consultar os comments por card sem contabilizá-los como chamadas GraphQL

### Requirement: Elegibilidade conhecida preserva a política atual
Para card de `RELEASE_CARDS` com Status conhecido diferente de `Homologado` ou `Pronto`, o check de evidência de homologação SHALL manter o resultado atual de “not applicable”. O guard MUST NOT transformar esta change em exigência de elegibilidade integral do pacote.

#### Scenario: Card do pacote possui Status conhecido não elegível
- **WHEN** um item inequívoco de `RELEASE_CARDS` possui Status conhecido diferente de `Homologado` e `Pronto`
- **THEN** o check de evidência de homologação permanece “not applicable” em vez de criar nova política de bloqueio

### Requirement: Estado remoto desconhecido nunca constitui preservação válida

Quando o snapshot do Project estiver ausente, inválido, incompleto ou em estado `failed`, o release guard MUST preservar o resultado de lookup como `unknown` e MUST NOT classificar qualquer branch dependente desse lookup como `preserved`, `card in flight` ou outro estado de negócio conhecido. O modo `post` MUST registrar blocker e terminar sem sucesso; o modo `audit` SHALL registrar warning explícito e continuar apenas como diagnóstico.

#### Scenario: Snapshot falha durante post com branch inventariada

- **WHEN** o fake `gh` faz o snapshot do Project falhar e existe uma branch cujo status dependeria do board
- **THEN** `post` retorna não zero com blocker da falha do snapshot e a saída não classifica essa branch como `preserved` nem `card in flight`

#### Scenario: Snapshot falha durante audit com branch inventariada

- **WHEN** a mesma falha ocorre em `audit`
- **THEN** o guard emite warning explícito de estado remoto desconhecido e a saída não classifica a branch como `preserved` nem `card in flight`

#### Scenario: Card conhecido está realmente em fluxo

- **WHEN** o snapshot é autoritativo e o card da branch possui Status conhecido não terminal
- **THEN** a classificação `preserved (card in flight; not deleted)` continua permitida

### Requirement: Limpeza de branches do pacote usa manifest e prova por ref

O closeout SHALL registrar o manifest nominal completo de branches do pacote antes da limpeza. Para cada branch, o executor MUST registrar o tip local/remoto disponível e MUST provar integração por ancestralidade, equivalência de árvore, equivalência de patch ou ausência de diff material nos arquivos tocados. Branch não integrada MUST NOT ser removida sem autorização humana explícita vinculada ao nome e à evidência comparada. Branch com worktree ativa MUST permanecer bloqueada para deleção.

#### Scenario: Branch integrada pode ser removida

- **WHEN** uma branch do manifest não possui worktree ativa e sua integração é provada contra `origin/develop`
- **THEN** as refs local e remota podem ser removidas e sua ausência é verificada depois de atualizar/prunar as refs

#### Scenario: Branch marcada como not merged possui autorização

- **WHEN** a árvore e os patches exclusivos foram revisados e Alan autorizou explicitamente descartar a branch identificada por nome e tip
- **THEN** a deleção forçada pode ocorrer com a autorização e a prova pós-deleção registradas no handoff

#### Scenario: Contagem sem nomes não prova limpeza

- **WHEN** a auditoria histórica informa apenas que existem 17 branches pendentes, mas o manifest nominal não foi recuperado
- **THEN** o closeout permanece incompleto mesmo que as branches conhecidas não apareçam em `git branch -a`

### Requirement: Medição GraphQL é vinculada a uma execução identificada

A evidência de orçamento SHALL registrar commit do guard, modo, horário, saldo GraphQL antes e depois e resultado terminal de uma única execução. O delta observado MUST ser de no máximo aproximadamente 500 pontos para satisfazer este card. Consumo concorrente conhecido ou não separável SHALL tornar a medição inconclusiva, e o executor MUST NOT repetir silenciosamente o run para selecionar um delta menor.

#### Scenario: Execução isolada permanece no orçamento

- **WHEN** uma execução identificada ocorre sem consumidor concorrente conhecido e o saldo GraphQL cai em até aproximadamente 500 pontos
- **THEN** o handoff registra o delta, a referência histórica de aproximadamente 4.900 pontos e o resultado do guard

#### Scenario: Cota sofre consumo concorrente

- **WHEN** outra automação usa a mesma credencial durante a janela e o delta não pode ser atribuído ao guard
- **THEN** a medição é registrada como inconclusiva e não conta como aceite do orçamento

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

### Requirement: Evidência kaizen da release bloqueia o post

Antes de concluir o `post`, o release guard MUST exigir que `docs/kaizen-log.md` esteja versionado e contenha um heading de nível 2 iniciado pela data canônica da release e identificado como auditoria de release por `Kaizen release` ou `/kaizen release`. Além do heading, o `post` MUST validar a materialização Kaizen (tabela `###` que começa com `Cards kaizen criados`: 1–3 issues novas sem linhas inválidas, ou dedupe `coberto por` com todos os `#N` em fluxo, ou marcador `Sem achados acionáveis` sem linhas de dados). Se houver dedupe e o snapshot do Project 1 estiver indisponível, o `post` MUST falhar fechado. Ausência do heading ou falha da materialização MUST ser blocker em `post`. O `post` bem-sucedido SHALL ocorrer antes de mover os cards do pacote para `Pronto`.

#### Scenario: Não existe entrada kaizen da data
- **WHEN** `post` não encontra heading canônico de auditoria para a data da release
- **THEN** o guard bloqueia o fechamento antes de `Pronto`

#### Scenario: Existe somente triagem do mesmo dia
- **WHEN** o log contém um heading da data, mas ele não identifica `Kaizen release` nem `/kaizen release`
- **THEN** essa entrada não satisfaz o gate

#### Scenario: Heading e materialização válidos
- **WHEN** o log versionado contém o heading canônico da data e a materialização Kaizen passa
- **THEN** o gate de evidência kaizen passa

#### Scenario: Heading presente mas materialização inválida
- **WHEN** o heading existe e a materialização falha
- **THEN** o `post` falha com blocker de materialização Kaizen

#### Scenario: Board snapshot down com dedupe
- **WHEN** a materialização depende de checar cobertura de dedupe e o snapshot do Project 1 falhou
- **THEN** o `post` falha fail-closed

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

### Requirement: Pre classifies preserved and merged worktrees and local branches without GraphQL
`scripts/release-guard pre` SHALL NOT treat an extra worktree as a blocker when its branch name is listed in `PRESERVED_BRANCHES` (trim, exact match), and SHALL NOT treat a dirty worktree as a blocker when that branch is listed (warn instead). `pre` SHALL NOT emit the unmerged local-branch blocker when the branch name is listed in `PRESERVED_BRANCHES`. `pre` SHALL NOT treat a dirty worktree as a blocker when the branch is merged into `origin/develop` (`branch_merged`) and every dirty/untracked path is exactly `docs/release-${RELEASE_DATE}.md`; porcelain rename lines MUST be blockers. An extra worktree whose branch is merged into `origin/develop` SHALL be a warning to remove at closeout, not a blocker, and MUST NOT require an empty commit. `pre` MUST NOT load a Project snapshot (`item-list`) or classify preserve via board Status. Unclassified extra worktrees, unclassified unmerged local branches, and other dirty paths remain blockers. The guard remains read-only.

#### Scenario: In-flight worktree listed in PRESERVED_BRANCHES
- **WHEN** `pre` runs with an extra worktree on `card-569-code-review-bugbot`
- **AND** `PRESERVED_BRANCHES` contains `card-569-code-review-bugbot`
- **THEN** the extra worktree is not a blocker
- **AND** if that worktree is dirty, the guard emits a warning rather than a blocker
- **AND** `pre` performs zero Project `item-list` calls

#### Scenario: In-flight local branch listed in PRESERVED_BRANCHES
- **WHEN** `pre` runs and a local branch `card-569-code-review-bugbot` is not merged into `origin/develop` or `origin/main`
- **AND** `PRESERVED_BRANCHES` contains `card-569-code-review-bugbot`
- **THEN** the guard MUST NOT emit `local branch not merged...` for that branch
- **AND** `pre` performs zero Project `item-list` calls

#### Scenario: Extra worktree or local branch without classification
- **WHEN** `pre` runs with an extra worktree or unmerged local branch whose name is not in `PRESERVED_BRANCHES` and is not merged into `origin/develop`
- **THEN** the guard emits the current blocker requiring classification or merge

#### Scenario: Merged card worktree with rollout checklist only
- **WHEN** `pre` runs with a worktree whose branch is merged into `origin/develop`
- **AND** the only dirty/untracked path is `docs/release-${RELEASE_DATE}.md`
- **THEN** the worktree is not a dirty blocker
- **AND** an extra worktree in that state is a warning to remove at closeout, not a blocker

#### Scenario: Merged card worktree dirty with other files
- **WHEN** a merged-branch worktree is dirty with any path other than `docs/release-${RELEASE_DATE}.md`
- **THEN** the guard emits a dirty-worktree blocker

#### Scenario: Pre does not query the board
- **WHEN** `pre` classifies worktrees or local branches
- **THEN** it uses `PRESERVED_BRANCHES` and local git merge state only
- **AND** it MUST NOT call `ensure_board_snapshot` or Project `item-list`

### Requirement: Homologation comment is verified in pre without GraphQL
`scripts/release-guard pre` SHALL call `normalize_release_cards` locally. Invalid `RELEASE_CARDS` tokens in strict `pre` MUST be blockers before any REST comment call. When `RELEASE_CARDS` is unset, the homologation-comment check SHALL warn and skip and MUST NOT invent a package list. When `CANONICAL_CARDS` is non-empty, `pre` SHALL fetch issue comments over REST for each canonical card ID and SHALL fail in strict mode if the marker `Homologado por Alan na develop.` is absent. This check MUST be a separate branch from the `post|audit` homologation section and MUST NOT call Project `item-list`, PR list, `ensure_snapshots`, or `card_status`. When `gh` is unavailable or unauthenticated while `RELEASE_CARDS` is set, the check SHALL be a blocker. REST comment reads in `pre|post|audit` are permitted and remain outside the GraphQL budget. In `pre`, every canonical ID SHALL require the marker (no Status-based not-applicable). Status-based not-applicable for cards not in `Homologado` or `Pronto` remains only in `post|audit`.

#### Scenario: Pre without comment
- **WHEN** `pre` runs with valid `RELEASE_CARDS` including card N
- **AND** issue N has no comment containing `Homologado por Alan na develop.`
- **THEN** the guard emits a blocker and exits non-zero in strict mode
- **AND** `pre` performs zero Project `item-list` calls

#### Scenario: Pre with canonical comment
- **WHEN** `pre` runs with valid `RELEASE_CARDS` including card N
- **AND** issue N has the canonical homologation marker
- **THEN** that card does not produce a homologation-comment blocker

#### Scenario: Pre without RELEASE_CARDS
- **WHEN** `pre` runs and `RELEASE_CARDS` is unset
- **THEN** the homologation-comment check warns and skips
- **AND** the guard does not invent a package list
- **AND** `pre` still performs zero Project `item-list` calls

#### Scenario: Pre cannot list comments
- **WHEN** `pre` runs with valid `RELEASE_CARDS` and `gh` cannot list comments for a card
- **THEN** the guard emits a blocker (fail-closed) and MUST NOT treat the card as evidenced

#### Scenario: Pre with invalid RELEASE_CARDS
- **WHEN** `pre` runs in strict mode with an invalid `RELEASE_CARDS` token
- **THEN** the guard emits a blocker
- **AND** it MUST NOT call `issues/.../comments`

#### Scenario: Pre does not use board Status
- **WHEN** `pre` has valid `CANONICAL_CARDS` and no `BOARD_JSON`
- **THEN** every canonical ID still requires the homologation marker
- **AND** Status-based not-applicable MUST NOT apply in `pre`

### Requirement: Pre on release-* does not require archive on origin/develop
Quando a branch corrente corresponde a `release-*`, `scripts/release-guard pre` SHALL permitir PASS sem exigir que o archive OpenSpec do pacote (nem a remoção da change ativa correspondente) já esteja presente em `origin/develop`. O `pre` MUST NOT emitir blocker cujo remédio prescrito seja publicar o archive em `origin/develop` antes de abrir o PR `release-* → main`. O guard permanece read-only. Comportamentos existentes que suportam este caminho (diff `origin/main...HEAD` para classificação code/documental em `release-*`; exclusão da branch corrente `release-*` do inventário de branches locais não mergeadas no `pre`) MUST ser preservados. Lacunas sobre a ref local `develop` com archive ainda não publicado em `origin/develop` pertencem ao card #618 e MUST NOT ser “consertadas” expandindo este requisito além do aceite do #617.

#### Scenario: Pre passes with archive only on release-* HEAD
- **WHEN** `scripts/release-guard pre` roda com `current_branch` matching `release-*`
- **AND** o HEAD da `release-*` contém o archive OpenSpec do pacote
- **AND** `origin/develop` ainda não contém esse archive
- **THEN** o `pre` NÃO falha por ausência do archive em `origin/develop`
- **AND** o comando pode atingir PASS quanto a essa condição (outros blockers legítimos de higiene permanecem)

#### Scenario: Pre does not prescribe push archive to develop first
- **WHEN** o archive existe apenas na tip da `release-*` usada pelo lote
- **THEN** a saída do `pre` MUST NOT instruir o operador a fazer push do archive para `origin/develop` como pré-condição do PR de release

#### Scenario: Existing release-* pre behaviors remain
- **WHEN** `pre` classifica o unpublished diff com branch corrente `release-*`
- **THEN** o diff usado é `origin/main...HEAD` (não `origin/main...origin/develop`)
- **AND** a seção de branches locais do `pre` não trata a própria `release-*` corrente como branch local não mergeada bloqueante

### Requirement: Pre on release branch ignores unmerged local develop without PRESERVED_BRANCHES
When `scripts/release-guard` runs in `pre` mode and the current branch matches `release-*`, the Local branches inventory SHALL NOT emit the unmerged-local-branch blocker for the local ref `develop`, even when `refs/heads/develop` is not merged into `origin/develop` or `origin/main` (for example local develop ahead with unpublished commits). This exemption MUST NOT require `PRESERVED_BRANCHES` to include `develop`. The existing warning when local `develop` differs from `origin/develop` MAY remain. Other unmerged local branches MUST continue to block unless classified via `PRESERVED_BRANCHES` or otherwise already exempt. Modes `post` and `audit`, and `pre` when the current branch is not `release-*`, are unchanged by this requirement. The guard remains read-only.

#### Scenario: Pre on release-* with local develop ahead of origin/develop
- **WHEN** `pre` runs with current branch `release-*`
- **AND** local `develop` exists and is ahead of `origin/develop` (not `branch_merged`)
- **AND** `PRESERVED_BRANCHES` is unset or does not list `develop`
- **THEN** the guard MUST NOT emit `local branch not merged...: develop` (nor any BLOCKER solely for that local develop ref)
- **AND** the guard MUST NOT require `PRESERVED_BRANCHES=develop`

#### Scenario: Pre on release-* still blocks other unmerged local branches
- **WHEN** `pre` runs with current branch `release-*`
- **AND** a local branch other than `develop` (for example `card-999-wip`) is not merged into `origin/develop` or `origin/main`
- **AND** that branch is not listed in `PRESERVED_BRANCHES`
- **THEN** the guard emits the current unmerged-local-branch blocker for that branch

#### Scenario: Existing diverge warn for develop remains available
- **WHEN** `pre` runs with current branch `release-*`
- **AND** `refs/heads/develop` differs from `origin/develop`
- **THEN** the guard MAY warn that release decisions use `origin/develop`
- **AND** that diverge alone MUST NOT become a Local-branches BLOCKER for `develop` under this requirement

