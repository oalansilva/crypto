## Context

O `release-guard` repete consultas remotas caras por check e por branch. A listagem completa do Project 1 custa cerca de 202 pontos GraphQL (medição com `totalCount=194`); cinco consumidores mais `card_is_terminal()` para 13 branches e `gh pr list` por branch podem esgotar a cota de 5.000 pontos/hora. Quando o board falha, o retorno atual também pode ser interpretado como card não terminal, preservando uma branch em `post` sem evidência autoritativa.

Stakeholders: Alan, que precisa de um fechamento de release confiável, e os agentes que executam o guard. A superfície afetada é exclusivamente `scripts/release-guard` e seus testes.

**UI impact: none.** Não há mudança de frontend, tela, componente, rota, copy ou interação; trata-se de controle operacional em Bash.

## Goals / Non-Goals

### Goals

- Fixar um orçamento remoto constante por modo, independentemente do número de branches e checks.
- Reutilizar dados completos e internamente consistentes durante um run, sem cache entre runs.
- Separar estados conhecidos de indisponibilidade ou ambiguidade remota.
- Fazer `post` falhar fechado e manter `audit` diagnóstico.
- Validar `RELEASE_CARDS` de modo canônico antes de decisões de pacote.
- Provar orçamento, completude e semântica de falha com testes determinísticos.

### Non-Goals

- Cache persistente/compartilhado, `flock` ou lock global.
- Retry, polling ou espera pelo reset da cota.
- Alterar autenticação, limite do GitHub, dados do board ou migrar o guard de Bash.
- Exigir que todo card de `RELEASE_CARDS` esteja `Homologado|Pronto`.
- Qualquer alteração de UI/UX.

## Decisions with Rationale

### D1 — Um snapshot por run, carregado no shell principal

Em `post|audit`, os loaders serão **invocados** como statements simples no fluxo principal, nunca dentro de `$(...)`, e carregarão no máximo uma vez `gh project item-list 1 --owner oalansilva --limit 500 --format json` em `BOARD_JSON`/`BOARD_STATE` e `gh pr list --repo oalansilva/crypto --state open --limit 1000 --json number,headRefName,headRepositoryOwner` em `PRS_JSON`/`PRS_STATE`. Dentro do loader, `json=$(gh ...)` é permitido para capturar a resposta, desde que o próprio loader atribua os globals e trate o exit status antes de retornar. Consumidores apenas leem esses globals. O Project só é válido se `.items` for array, `totalCount` estiver presente como inteiro não negativo e `length == totalCount`; ausência, tipo inválido ou qualquer diferença — para menos ou para mais — invalida o snapshot. A fotografia de PRs só é autoritativa se a resposta de topo for array e cada entrada possuir `headRefName` e `headRepositoryOwner.login` como strings não vazias; objeto, item malformado ou 1.000 entradas tornam `PRS_STATE=failed`. Exit code diferente de zero invalida o snapshot mesmo com JSON parseável.

**Racional:** command substitution executa em subshell e perderia mutações dos loaders, causando refetch. Um snapshot fresco por processo reduz chamadas e dá consistência interna sem aceitar dados obsoletos entre runs.

### D2 — Lookups locais tri-state

Cards serão procurados sempre pela chave `(repository=oalansilva/crypto, issue number canônico)` e classificados como `terminal` (`Pronto|Cancelado`), `non-terminal` ou `unknown`. Item de outro repositório com o mesmo número não corresponde. Falha de API, JSON inválido, snapshot incompleto, chave ausente/duplicada ou Status ausente resultam em `unknown`. PRs serão indexados pela chave `(headRepositoryOwner.login, headRefName)`; somente `(oalansilva, branch local)` corresponde à branch de `oalansilva/crypto`, portanto PR de fork com o mesmo nome não marca `pr_open=yes`. Falha ou estrutura não autoritativa preserva `unknown` e nunca equivale a `pr_open=no`. `unknown` é blocker em `post` e warning em `audit`.

**Racional:** indisponibilidade não é evidência de estado de negócio e não pode preservar branches silenciosamente.

### D3 — Falha de snapshot global e imediata

Qualquer falha de `BOARD_STATE` ou `PRS_STATE` será reportada imediatamente no nível do modo: blocker em `post`, warning em `audit`, inclusive quando nenhum consumidor relevante estiver ativo. `pre` não carrega snapshots.

**Racional:** condicionar a falha ao consumidor recriaria caminhos fail-open e tornaria o resultado dependente da ordem dos checks.

### D4 — `RELEASE_CARDS` normalizado uma vez

Antes de chamadas remotas, o guard fará trim, removerá zeros à esquerda (`0480` → `480`), deduplicará e validará cada ID como inteiro decimal entre 1 e 2147483647. Em `post`, formato inválido bloqueia antes de qualquer chamada remota. Em `audit`, formato inválido gera warning e impede somente chamadas/checks remotos dependentes do pacote; checks independentes continuam. A identidade de cada card será a tupla `(repository=oalansilva/crypto, issue number canônico)`: cada tupla deverá aparecer exatamente uma vez no snapshot e ter Status. Item de outro repositório com o mesmo número não corresponde; ausência, duplicidade no repositório alvo ou presença apenas em outro repositório produz `unknown`/blocker em `post`. O mesmo item qualificado alimentará campos obrigatórios e evidência de homologação.

**Racional:** elimina consultas duplicadas, divergência entre checks, ambiguidades como `480,0480` e colisões de número entre repositórios de um Project pertencente ao usuário.

### D5 — Rate limit apenas como diagnóstico pós-falha

Após uma ou mais falhas de snapshot, e somente então, o guard consultará no máximo uma vez por execução o endpoint REST `rate_limit` e incluirá `graphql.remaining` e `reset` quando disponíveis. O diagnóstico é complementar e nunca substitui nem altera a causa original. Não haverá retry, polling ou limiar preventivo.

**Racional:** o custo varia com o board; diagnóstico sob demanda não aumenta o caminho feliz nem mascara a falha original.

### D6 — Teto total de 19 páginas de idade

O inventário de idade de `audit`, que precisa de `updatedAt`, contará a página inicial no teto: uma inicial mais até 18 adicionais, no máximo 19 requisições GraphQL totais. Se `hasNextPage` ainda for verdadeiro após a 19ª resposta, o guard não fará a 20ª requisição e emitirá warning explícito de inventário parcial/truncado; `audit` permanece diagnóstico.

**Racional:** corrige o off-by-one atual em que `page=0..19` permite 21 chamadas.

### D7 — Orçamento por modo

| Modo | Project `item-list` | `pr list` | Páginas GraphQL de idade | REST permitido |
| --- | ---: | ---: | ---: | --- |
| `pre` | 0 | 0 | 0 | nenhuma chamada de diagnóstico ou comments |
| `post` | ≤1 | ≤1 | 0 | rate limit pós-falha e comments por card |
| `audit` | ≤1 | ≤1 | ≤19 | rate limit pós-falha e comments por card para homologação/divergência de título |

Comments REST permanecem permitidos por card e ficam fora do orçamento GraphQL.

**Racional:** o contrato torna regressões de custo observáveis sem remover evidências já coletadas via REST.

### D8 — Elegibilidade integral do pacote fora de escopo

Um card de `RELEASE_CARDS` com Status conhecido, mas diferente de `Homologado|Pronto`, mantém o comportamento atual de “not applicable” no check de evidência de homologação.

**Racional:** exigir o pacote inteiro nesses estados altera política de produto/release e deve ser decidido em card próprio; #509 corrige custo e fail-open.

## Risks / Trade-offs

- **Snapshot muda durante o run:** aceita-se consistência point-in-time; um segundo run sempre refaz as consultas.
- **JSON grande em globals Bash:** o Project atual tem 194 itens e limite 500; o custo local é menor que repetir chamadas remotas.
- **Fail-closed revela dívida antes mascarada:** é intencional; mensagens distinguem `non-terminal` de `unknown`.
- **PRs abertos podem alcançar 1.000 ou trazer metadados incompletos:** o guard falha como truncado/malformado, priorizando autoridade e identidade do owner sobre conveniência.
- **Inventário de idade ainda custa GraphQL:** permanece exclusivo de `audit` e limitado a 19 páginas porque `updatedAt` não está no snapshot principal; truncamento fica visível por warning.

## Migration Plan

1. Adicionar primeiro os testes com fake `gh` e log externo process-safe para os contadores de D1–D7.
2. Implementar normalização local de `RELEASE_CARDS` antes dos loaders (D4).
3. Implementar loaders no shell principal, validação e falha global (D1, D3, D5).
4. Migrar todos os consumidores para lookups tri-state e remover consultas por branch/check (D2).
5. Corrigir a paginação de idade e validar a matriz por modo (D6, D7).
6. Rodar testes focados e medir uma execução real somente na etapa de implementação autorizada.
7. Rollback: reverter a change; não há persistência, migração de banco ou cache a limpar.

## Prototype

N/A. `UI impact: none`: script operacional e testes não criam nem alteram superfície visual navegável.

## Prototype Validation

N/A. Não há protótipo, HTML, rota ou interação visual; portanto o browser gate de Design não se aplica.

## Impeccable Brief

N/A. O pipeline Impeccable é visual/UX e esta change é exclusivamente operacional.

## Impeccable Critique

N/A. Não há superfície visual para Assessments A/B; a crítica operacional está em `Design Critique`.

## Impeccable Audit

N/A. Acessibilidade, responsividade, theming e performance de frontend não são afetados.

## Impeccable Trace

N/A. Nenhum contexto, protótipo, polish ou browser gate visual foi executado, justificadamente por `UI impact: none`.

## Open Questions

- Em card futuro, o `post` deve exigir que todos os IDs de `RELEASE_CARDS` estejam em `Homologado|Pronto`, em vez de manter “not applicable” para estados conhecidos não elegíveis?

## Design Critique

- **Produto/escopo:** PASS — a solução ataca consumo GraphQL e fail-open sem alterar política de release (D8) ou UI.
- **Correção operacional:** PASS — loaders invocados no shell principal evitam perda de globals por subshell; `totalCount` tipado, arrays de PRs estruturalmente validados, exit code e truncamento impedem snapshots parciais silenciosos.
- **Segurança/fail-closed:** PASS — `unknown` é distinto de `non-terminal`, e D3 elimina dependência da presença/ordem de consumidores.
- **Identidade:** PASS — D4 qualifica cards por repositório e número; D2 qualifica PRs por owner e branch, impedindo que forks homônimos correspondam às branches de `oalansilva/crypto`; `audit` inválido fica diagnóstico sem bloquear checks independentes.
- **Custo:** PASS — a matriz D7 fixa chamadas do caminho principal; D5 limita diagnóstico a uma chamada e D6 corrige o teto com warning de truncamento.
- **Testabilidade:** PASS — fake `gh` com log externo verificará subprocessos, contagem exata, nova fotografia por run, `totalCount`, colisões entre repositórios, ambiguidades em `audit`, normalização, diagnóstico e ausência de chamadas indevidas.
- **Resolução da crítica independente:** PASS — além das correções anteriores, a fotografia de PRs agora exige array estruturalmente íntegro e o lookup usa `(headRepositoryOwner.login, headRefName)`, resolvendo os dois P1 sem caminho `pr_open=no` para resposta malformada ou fork homônimo.
- **Achados:** nenhum P0/P1 aberto. A elegibilidade integral do pacote é P2 aceito e explicitamente fora de escopo; o inventário de idade separado é trade-off necessário e limitado.
- **Referências avaliadas:** `proposal.md`, decisões D1–D8, delta `specs/release-worktree-hygiene/spec.md` e `tasks.md`; Prototype N/A justificado.

Design Agent verdict: PASS
