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
The release workflow MUST compare publication state using `origin/develop` and `origin/main` after fetching remote refs.

#### Scenario: Local main is stale
- **WHEN** local `main` differs from `origin/main`
- **THEN** the release guard uses `origin/main` for merge-state decisions and reports local `main` drift as informational or warning context.

### Requirement: Post-release cleanup gate
The release workflow MUST run a post-release guard before reporting final cleanup complete.

#### Scenario: Release merged but orphaned work remains
- **WHEN** `origin/develop` and `origin/main` are aligned but a stash, temporary worktree, unmerged branch, or tracked generated file remains
- **THEN** the post-release guard fails and requires classification or cleanup before the release is reported as clean.

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
Após uma ou mais falhas de snapshot, o release guard SHALL consultar o endpoint REST de rate limit no máximo uma vez por execução e incluir `graphql.remaining` e `reset` quando disponíveis. O diagnóstico MUST preservar a causa original. O guard MUST NOT consultar esse diagnóstico preventivamente e MUST NOT executar retry, polling ou espera automática.

#### Scenario: Snapshot falha com diagnóstico disponível
- **WHEN** uma carga de snapshot falha e o endpoint REST informa saldo e reset GraphQL
- **THEN** a mensagem inclui esses valores e preserva a falha original conforme o modo

#### Scenario: Snapshot é carregado com sucesso
- **WHEN** os snapshots são válidos
- **THEN** o guard não consulta rate limit para diagnóstico preventivo

#### Scenario: Ambos os snapshots falham
- **WHEN** Project e PRs falham na mesma execução
- **THEN** o guard consulta rate limit no máximo uma vez e preserva as falhas originais

### Requirement: Orçamento GraphQL é limitado por modo
O release guard MUST respeitar estes máximos por execução: `pre` com zero `item-list`, zero `pr list`, zero páginas de idade e zero diagnóstico de rate limit; `post` com até um `item-list`, até um `pr list` e zero páginas de idade; `audit` com até um `item-list`, até um `pr list` e até 19 páginas GraphQL de idade. Requisições REST de comments por card para homologação ou divergência de título SHALL permanecer permitidas em `post|audit` e excluídas desse orçamento GraphQL.

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

