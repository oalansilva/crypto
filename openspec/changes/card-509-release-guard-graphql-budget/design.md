## Context

O `release-guard` consulta o GitHub Project em cinco pontos independentes. Um deles, `card_is_terminal`, baixa o board completo para cada branch inventariada; a listagem de PRs abertos também ocorre por branch. Uma listagem completa do Project custou 202 pontos GraphQL em medição real, e execuções concorrentes esgotaram a cota horária de 5.000 pontos.

Além do custo, falhas remotas não têm representação explícita: `card_is_terminal` retorna o mesmo código para card não terminal, JSON inválido, rate limit e falha de autenticação. O inventário pode então preservar a branch como "card in flight" mesmo sem evidência autoritativa.

Stakeholders: Alan (fechamento de release), Codex/opencode (execução do guard) e cards incluídos no pacote. O script Bash e seus testes de integração são a superfície afetada.

UI impact: none. A mudança é restrita a script operacional e testes; nenhuma tela, rota, componente, copy ou interação visual muda.

## Goals / Non-Goals

**Goals:**

- Limitar a uma listagem completa do Project e uma listagem global de PRs por execução.
- Preservar uma fotografia fresca e privada por processo, reutilizada somente no run atual.
- Distinguir `terminal`, `non-terminal` e `unknown` em decisões dependentes do GitHub.
- Manter `post` fail-closed e `audit` informativo quando dados remotos forem desconhecidos.
- Diagnosticar rate limit com saldo e reset sem polling ou retry loop.
- Provar o orçamento de chamadas e os estados de falha por testes determinísticos.

**Non-Goals:**

- Criar cache persistente ou compartilhado entre execuções.
- Alterar o limite GraphQL do GitHub, credenciais ou autenticação.
- Migrar o guard de Bash ou redesenhar checks não relacionados.
- Alterar o frontend, o board ou o fluxo de release.

## Decisions

### D1 - Snapshot único por execução, carregado no shell principal

O guard carregará no máximo uma fotografia completa do Project (`gh project item-list 1 --owner oalansilva --limit 500 --format json`) e uma fotografia global de PRs abertos (`gh pr list --repo oalansilva/crypto --state open --limit 1000 --json number,headRefName`) por execução.

**Completude verificável:** o `item-list` expõe `totalCount` (medido: 194 itens no Project 1). O snapshot do Project é considerado válido somente se `.items` for array **e** `.items | length == .totalCount`. A listagem de PRs é considerada truncada (estado `failed`) se atingir o limite de 1.000 itens.

**Execução no shell principal:** os loaders `ensure_board_snapshot` e `ensure_pr_snapshot` são invocados como statements simples no fluxo principal (nunca dentro de `$( )`), gravando globals `BOARD_JSON`/`BOARD_STATE` e `PRS_JSON`/`PRS_STATE`. Os consumidores somente leem os globals. Isso evita o problema de variáveis mutadas em subshell (command substitution) não retornarem ao shell pai e o download ser repetido.

Alternativas rejeitadas:

- Cache em `/tmp` entre processos: pode aprovar uma release com Status/campos obsoletos e exige invalidação e segurança adicional.
- `flock` global: serializa, mas não reduz o número de consultas e pode bloquear operações longas.
- Query dirigida por card: multiplica round-trips e volta a crescer com branches/cards.

### D2 - Índices locais e decisão tri-state

Os consumidores consultarão o snapshot local por número do card. Zero ou mais de uma correspondência, Status ausente, snapshot inválido ou falha de API produzem `unknown`; exatamente uma correspondência produz `terminal` para `Pronto|Cancelado` e `non-terminal` nos demais estados.

No modo estrito, `unknown` incrementa blockers. Em `audit`, incrementa warnings. O guard nunca traduz indisponibilidade remota para "card em andamento".

### D3 - Falha de snapshot é global e imediata (regra única)

Falha de API/JSON/validação em qualquer snapshot (Project ou PRs) produz estado `failed` global: em `post`, blocker com causa explícita e terminação com falha; em `audit`, warning explícito. A regra é única e não condicional por consumidor — não existe caminho em que um snapshot falho seja silenciosamente ignorado porque nenhum consumidor "dependia" dele.

### D4 - Validação única do pacote

`RELEASE_CARDS` será normalizado uma vez: trim de espaços, remoção de zeros à esquerda (`0480` → `480`), deduplicação e validação numérica (1..2147483647). Formato inválido já bloqueia em `post` antes de qualquer consulta. Cada ID normalizado deverá existir exatamente uma vez no snapshot do Project e ter Status. A mesma fotografia alimentará a validação de campos obrigatórios e de evidência de homologação, evitando consultas duplicadas e inconsistência entre seções.

### D5 - Diagnóstico somente após falha

Não haverá limiar preventivo fixo, pois o custo varia com o tamanho do board. Se o carregamento falhar, o guard consultará o endpoint REST de rate limit e acrescentará `remaining` e `reset` à mensagem quando disponíveis. Não haverá espera ou retry automático.

### D6 - Paginação com contagem total

O inventário de idade continuará separado porque requer `updatedAt`, ausente no JSON do `gh project item-list`. O contador incluirá a primeira página no limite total (`page -lt 20` vira `page -lt 19` com a inicial contada), eliminando a diferença atual entre "20 páginas" e 21 requisições possíveis.

### D7 - Matriz de orçamento por modo (contrato de chamadas)

| Modo | `gh project item-list` | `gh pr list` | Age GraphQL (páginas) | REST permitidas |
| --- | --- | --- | --- | --- |
| `pre` | 0 | 0 | 0 | rate limit (somente em falha) |
| `post` | ≤ 1 | ≤ 1 | 0 | rate limit + comments por card (`repos/.../issues/N/comments`) |
| `audit` | ≤ 1 | ≤ 1 | ≤ 19 no total (1 inicial + até 18 adicionais) | rate limit + comments por card (homologação) + comments por divergência de título |

Chamadas REST de comments não contam na cota GraphQL e são o mecanismo legítimo de evidência de homologação/divergência; permanecem por card como hoje.

### D8 - Lacunas conhecidas fora de escopo

Status conhecido porém não `Homologado|Pronto` em card de `RELEASE_CARDS` continua com o comportamento atual ("not applicable" no check de homologação). Exigir pacote integralmente `Homologado|Pronto` no `post` é decisão de produto de card futuro, registrada em Open Questions.

## Risks / Trade-offs

- [Snapshot pode ficar alguns segundos defasado durante o mesmo run] -> O run é curto e precisa de consistência interna; um novo `post` sempre faz novo carregamento.
- [Variáveis Bash podem copiar JSON grande] -> O board atual tem menos de 500 itens; reutilizar uma variável é menor risco que chamadas remotas repetidas.
- [Validação fail-closed pode revelar dívida antes mascarada] -> É comportamento intencional; mensagens distinguirão card não terminal de estado remoto desconhecido.
- [Consulta de idade ainda consome GraphQL no audit] -> Ela é exclusiva de `audit`, tem paginação limitada e cobre um dado que o snapshot principal não fornece.
- [Custo do Project cresce com o board] -> A quantidade de listagens permanece constante; medição antes/depois registra o orçamento real.

## Migration Plan

1. Adicionar testes de contagem e falha contra o fake `gh` (cenários em `Design Critique`).
2. Implementar loaders `ensure_board_snapshot`/`ensure_pr_snapshot` no shell principal, com validação de completude (`totalCount`, truncamento).
3. Migrar cada consumidor para os globals do snapshot único e remover chamadas por branch/seção.
4. Medir o delta GraphQL em uma execução real de `audit` após reset da cota.
5. Rollback: reverter o commit da change; não há dados persistidos nem migração de banco.

## Prototype

N/A. `UI impact: none`; não existe superfície visual, portanto protótipo e browser gate de Design não se aplicam.

## Prototype Validation

N/A. Nenhum HTML, rota ou componente visual é criado ou alterado.

## Impeccable Brief

N/A. A change é operacional e não altera UI/UX.

## Impeccable Critique

N/A. Não há superfície visual para os Assessments A/B; a crítica aplicável é operacional e está em `Design Critique`.

## Impeccable Audit

N/A. Acessibilidade, responsividade, theming e performance de frontend não são afetados.

## Impeccable Trace

N/A. Nenhum pipeline visual, protótipo ou browser gate é aplicável a `UI impact: none`.

## Design Critique

- Escopo: concentrado em `scripts/release-guard` e testes; sem mudança de produto ou interface.
- Correção operacional: snapshot por processo elimina multiplicidade sem aceitar dados obsoletos entre runs.
- Segurança/fail-closed: falhas e ambiguidades deixam de ser confundidas com estados válidos.
- Risco de regressão: saída de sucesso deve permanecer compatível; contadores no fake `gh` provarão que a redução não remove checks.
- Pendência não bloqueante: a consulta de idade permanece separada por depender de `updatedAt`.
- Prototype: N/A, justificado por `UI impact: none`.

### Resolução da crítica independente (design-planner, openai/gpt-5.6-sol)

A primeira crítica retornou `BLOCKED` com 7 achados. Resolução registrada:

- P1-1 Completude dos snapshots → D1: validação de `.items | length == .totalCount` no Project e detecção de truncamento na listagem de PRs (limite 1.000); ambos falham com estado `failed`.
- P1-2 Orçamento ambíguo → D7: matriz de chamadas por modo (`pre`/`post`/`audit`), com contagem de invocações CLI, páginas GraphQL da idade e chamadas REST excluídas.
- P1-3 Loader lazy em subshell → D1: loaders executados no shell principal como statements simples, globals somente leitura nos consumidores.
- P1-4 Semântica de falha de PR contraditória → D3: regra única e global (falha de qualquer snapshot = blocker em `post`/warn em `audit`, imediato, não condicional).
- P2-5 Normalização de `RELEASE_CARDS` → D4: trim, strip de zeros à esquerda, dedupe e validação numérica antes de qualquer consumidor.
- P2-6 Status conhecido inadequado → D8: registrado como lacuna fora de escopo; comportamento atual preservado.
- P2-7 Testes → plano de cenários abaixo, incluindo ativação de todos os consumidores e nova fotografia por execução.

Plano de testes (fake `gh` com contador de chamadas):

1. Múltiplas branches + checks (changes terminais, branches, campos, homologação) → exatamente 1 `item-list` e 1 `pr list`.
2. Segunda execução refaz os downloads (sem cache persistente).
3. JSON válido mas exit code != 0 → snapshot `failed`.
4. Truncamento (`items.length < totalCount`) → `failed` em `post`.
5. Card ausente/duplicado/sem Status em `RELEASE_CARDS` → blocker em `post`.
6. Listagem de PRs truncada ou JSON inválido → `failed` (nunca `pr_open=no`).
7. `post` blocker vs `audit` warning para a mesma falha, inclusive sem consumidores relevantes ativos (falha global imediata).
8. Paginação de idade respeita o limite total (1 inicial + máx. 18 adicionais = 19).
9. Normalização de `RELEASE_CARDS`: trim, zeros à esquerda, dedupe (`480,0480`), intervalo e token inválido (sem consulta remota).

A revalidação read-only do design-planner (openai/gpt-5.6-sol) confirmou PASS com três residuais P2, todos resolvidos: matriz D7 agora lista comments REST de homologação no `audit`; o delta spec formaliza a normalização de `RELEASE_CARDS`; e o cenário de falha global sem consumidores ativos entrou no spec e nos testes.

Design Agent verdict: PASS

## Open Questions

- Exigir que todo card de `RELEASE_CARDS` esteja em `Homologado|Pronto` no `post` é decisão de produto fora do escopo do #509 (registrado em D8); o comportamento atual ("not applicable") permanece.
- Demais decisões (falha estrita e ausência de cache persistente) foram definidas no card #509.
