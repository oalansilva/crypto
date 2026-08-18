# Design — card-517-kaizen-guard-terminal

## Contexto

- Card: `#517`
- Change: `card-517-kaizen-guard-terminal`
- Status observado no packet: `Design`
- Superfície: `scripts/release-guard`, seção `OpenSpec terminal changes (post/audit)`, e seus testes de integração.
- **UI impact: none** — a alteração é exclusivamente de tooling/processo em Bash e de higiene OpenSpec. Não há frontend, tela, componente, copy, rota visual ou interação de usuário.

## Problema

O guard atual só chega ao board quando a change tem `proposal.md`, `design.md`, `tasks.md`, diretório `specs/`, zero tasks abertas e nome iniciado por `card-<n>`/`issue-<n>`. Isso cria dois pontos cegos independentes:

1. changes sem id no slug nunca recebem `card_num`, embora o snapshot do board e `RELEASE_CARDS` contenham os cards do pacote;
2. changes com task pendente são descartadas antes da consulta ao status, embora um card em `Pronto`/`Cancelado` com change in-progress seja precisamente uma inconsistência que o closeout deve denunciar.

Na release 2026-08-14, os seis slugs sem id `walk-forward-gate`, `kaizen-homologacao-evidence-comment`, `kaizen-stuck-cards-age-alert`, `kaizen-board-issue-rename-note`, `hide-quant-test-templates` e `design-planner-grok-4-6`, mais o caso histórico in-progress `card-509-release-guard-graphql-budget`, escaparam do check. O resultado foi auditoria com falso negativo e changes de cards já terminais mantidas ativas.

## Hipótese

Se o guard enumerar todas as changes ativas, resolver a associação change→card de forma determinística usando primeiro o id do slug e depois títulos do snapshot limitados/priorizados por `RELEASE_CARDS`, e só então consultar terminalidade, ele detectará tanto dívida completa quanto inconsistência in-progress sem nova consulta remota e sem depender de convenção perfeita de nomes.

## Resultado esperado

- `audit` emite warning para cada change ativa mapeada a card `Pronto`/`Cancelado`, seja `complete` ou `in-progress`.
- `post` emite blocker para qualquer change ativa mapeada a card terminal; cards de `CANONICAL_CARDS` têm prioridade explícita e, portanto, uma change ativa do pacote não pode passar silenciosamente.
- Cada achado informa change, card, status, estado local (`complete|in-progress`) e fonte do vínculo (`name|title`).
- O snapshot completo do board continua sendo carregado uma única vez por execução; o fallback não chama `gh` por change.
- Após o archive autorizado das changes terminais, o bloco termina sem warnings/blockers de changes terminais.

## Escopo e não escopo

### Em escopo

- Refatorar somente a detecção `OpenSpec terminal changes (post/audit)` e helpers locais necessários.
- Reusar `BOARD_JSON`, `BOARD_STATE`, `CANONICAL_CARDS`, `card_status` e a normalização existente de `RELEASE_CARDS`.
- Adicionar títulos aos fixtures do snapshot e cenários de regressão no teste existente com `gh` falso.
- Preparar a limpeza das dez changes ativas terminais identificadas no packet, executada apenas após autorização.

### Fora de escopo

- Alterar estados no board, publicar release, mover card ou autoaprovar Design.
- Mudar a CLI OpenSpec, a estrutura do archive ou o contrato de sync de specs.
- Inferir card por referências numéricas soltas dentro de proposal/design; esses documentos frequentemente mencionam cards relacionados e essa estratégia seria ambígua.
- Criar cache remoto entre runs ou nova consulta `gh` por change.
- Alterar código de produto, API, frontend, dados ou serviços.

## Decisões

### D1 — Enumerar primeiro; conclusão deixa de ser filtro

O guard SHALL enumerar todo diretório diretamente abaixo de `openspec/changes/`, excluindo `archive` e entradas não diretório. Para cada change, calculará apenas um rótulo de progresso:

- `complete`: os quatro grupos esperados existem (`proposal.md`, `design.md`, `tasks.md`, `specs/`) e não há checklist `- [ ]` pendente;
- `in-progress`: qualquer artefato obrigatório está ausente ou existe ao menos uma task aberta.

Esse rótulo entra na mensagem, mas não decide elegibilidade. A elegibilidade é `change ativa + card mapeado + status do card terminal`.

**Racional:** task pendente em card terminal não é razão para ignorar; é evidência adicional da inconsistência.

### D2 — Mapeamento em duas camadas, com id autoritativo

1. **Nome com id:** extrair `card_num` de `^(card|issue)-([0-9]+)(-|$)`. Esse vínculo é autoritativo e não passa pelo matcher de título.
2. **Fallback por título:** somente quando o slug não contém id, comparar o título da issue no `BOARD_JSON` com uma impressão local da change formada por `change_name` + `proposal.md`.

O fallback SHALL usar apenas itens de `oalansilva/crypto`. Quando `CANONICAL_CARDS` estiver preenchido, esses cards formam o primeiro conjunto de candidatos; sem pacote explícito, o audit/post pode considerar os cards terminais do snapshot completo. Nenhuma chamada remota adicional é permitida.

**Racional:** o nome cobre o caminho estável e barato; título + proposal cobre slugs legados sem confiar em números citados no corpo.

### D3 — Matcher de título determinístico e conservador

O matcher será implementado como comparação de tokens, não como substring livre:

1. normalizar slug, título e proposal para minúsculas ASCII, separadores por espaço e tokens únicos;
2. remover stopwords, ids isolados e termos estruturais sem poder discriminante (`card`, `issue`, `change`);
3. aceitar igualdade ou radical comum de pelo menos quatro caracteres para variações simples (`alert`/`alerta`, `test`/`teste`);
4. para cada token significativo do título, contar no máximo um hit no slug e um no corpus da proposal; calcular `score = (5 × slug_hits) + proposal_hits`;
5. qualificar o par somente com `slug_hits >= 2` ou `proposal_hits >= 4`, e aceitar apenas um candidato com maior score estritamente único; empate no maior score é ambiguidade.

Um empate ou score abaixo do piso não gera associação silenciosa. Em `audit`, o caso fica diagnóstico; em `post` com pacote explícito, ambiguidade que impeça provar a higiene do pacote é blocker e exige renomear a change com id ou classificá-la antes do closeout.

**Racional:** títulos e slugs podem diferir de idioma ou verbo (`hide` versus `Excluir`), mas proposal e termos de domínio fornecem sinais suficientes. O limiar e a unicidade evitam associação por uma palavra genérica.

### D4 — Terminalidade vem exclusivamente do snapshot

Após o vínculo, `card_status(card_num)` é a fonte de estado. Apenas `Pronto` e `Cancelado` são terminais. Status vazio, item ausente ou duplicado não deve ser tratado como não terminal: `audit` avisa e `post` falha fechado conforme o contrato já usado pelos snapshots.

Não se usa status citado em Markdown, nome da pasta ou tasks para decidir terminalidade.

### D5 — Semântica por modo

- `audit`: warning para toda change ativa mapeada a card terminal, com `progress=complete|in-progress` e `mapping=name|title`; retorno geral continua diagnóstico.
- `post`: blocker para toda change ativa mapeada a card terminal. Quando `RELEASE_CARDS` existe, a mensagem identifica `package=yes`; nenhuma change ativa de card do pacote pode permitir PASS.
- `pre`: permanece fora do check e sem consulta de board/PR.

A mensagem de sucesso deixa de dizer apenas “with all artifacts done” e passa a afirmar que não há change ativa mapeada a card terminal.

### D6 — Casos de regressão da issue

| Change | Card | Estado a simular | Fonte esperada | Resultado `audit` / `post` |
|---|---:|---|---|---|
| `walk-forward-gate` | #470 | complete | title | warn / blocker |
| `kaizen-homologacao-evidence-comment` | #480 | complete | title | warn / blocker |
| `kaizen-stuck-cards-age-alert` | #481 | complete | title | warn / blocker |
| `kaizen-board-issue-rename-note` | #482 | complete | title | warn / blocker |
| `hide-quant-test-templates` | #489 | complete | title, incluindo diferença `hide`/`Excluir` | warn / blocker |
| `design-planner-grok-4-6` | #491 | complete | title | warn / blocker |
| `card-509-release-guard-graphql-budget` | #509 | in-progress | name | warn / blocker |

O #509 já aparece arquivado nesta worktree em `openspec/changes/archive/2026-08-14-card-509-release-guard-graphql-budget/`; o teste recria o estado ativo in-progress que originou o falso negativo.

### D7 — Limpeza separada e autorizada

Depois da implementação/testes e somente com autorização de Alan, `/opsx:bulk-archive` verificará e arquivará as dez changes atualmente ativas e completas listadas no packet:

- `kaizen-dedupe-card-comments` (#456)
- `kaizen-guard-branch-inventory` (#457)
- `kaizen-bulk-archive-terminal-changes` (#458)
- `fix-saldo-usdt-compra` (#463)
- `walk-forward-gate` (#470)
- `kaizen-homologacao-evidence-comment` (#480)
- `kaizen-stuck-cards-age-alert` (#481)
- `kaizen-board-issue-rename-note` (#482)
- `hide-quant-test-templates` (#489; a doc da release usa o alias histórico `delete-quant-templates`)
- `design-planner-grok-4-6` (#491)

Antes de cada archive, confirmar card terminal e instruções da CLI; sincronizar delta specs quando aplicável. O #509 não entra novamente porque já está arquivado no estado observado.

## Riscos e mitigação

- **P1 — Falso positivo por título genérico:** mitigado por conjunto candidato do pacote, peso do slug, corpus da proposal, piso mínimo e exigência de melhor candidato único.
- **P1 — Falso negativo por título renomeado ou idioma muito diferente:** mitigado pelo corpus da proposal e pelo fail-closed de mapeamento ambíguo no `post`; recomendação durável continua sendo nomear novas changes com id.
- **P1 — Post bloqueado por dívida fora do pacote:** `CANONICAL_CARDS` prioriza o pacote e a saída identifica `package=yes`; achados globais permanecem auditáveis, sem esconder dívida. Os testes devem fixar a semântica para não ampliar o escopo por acidente.
- **P1 — Snapshot sem título/repositório/status:** não inferir; diagnosticar e falhar fechado no modo estrito quando a prova do pacote ficar incompleta.
- **P2 — Custo/latência:** processamento local pode crescer com changes × cards, mas o board tem ordem de centenas e não há nova chamada remota. Teste preserva uma única chamada `project item-list` e uma `pr list` por run.
- **P2 — Archive sincronizar delta antigo sobre spec atual:** executar `/opsx:bulk-archive` por change, revisar instruções e usar exceção `--skip-specs` somente com justificativa registrada.
- **P2 — Proposal ausente em change muito inicial:** classificar como `in-progress`; o fallback por título pode usar apenas slug. Se não houver score seguro, não fabricar vínculo.

## Design Critique

### Achados por severidade

- **P1 resolvido no desenho — filtro por tasks contradizia o objetivo:** a decisão D1 torna progresso apenas metadado e cobre explicitamente in-progress terminal.
- **P1 resolvido no desenho — fallback ingênuo poderia ligar a card citado incidentalmente:** D2 proíbe extrair números do conteúdo e D3 exige similaridade de título com unicidade.
- **P1 resolvido no desenho — heurística fail-open em closeout:** D3/D4 tornam ambiguidade e snapshot incompleto bloqueantes no `post` quando impedem comprovar o pacote.
- **P2 resolvido no desenho — regressão de orçamento GraphQL:** D2 reutiliza `BOARD_JSON`; os testes verificam contagem constante de chamadas.
- **P2 aceito — slugs legados continuam menos confiáveis que nomes com id:** o fallback é compatibilidade para dívida existente; a convenção recomendada continua `card-<id>-<slug>`.

### Avaliação

- **Produto/processo:** o check passa a fiscalizar o requisito real — nenhuma change ativa de card terminal — sem confundir task pendente com isenção. OK.
- **Escopo:** limitado ao guard, testes e archive autorizado; nenhuma superfície visual ou runtime do produto ficou sem classificação. OK.
- **Operação:** mensagens incluem origem do vínculo e progresso, permitindo corrigir por archive, rename ou classificação. OK.
- **Testabilidade:** sete regressões da issue, ambiguidades, status não terminal, remoção por archive e orçamento remoto têm asserts determinísticos. OK.

Referências avaliadas: `scripts/release-guard` linhas 56–223 e 574–649; `backend/tests/integration/test_release_guard.py`; changes/release docs citadas no packet. Prototype: N/A.

## Impeccable Brief

N/A — `UI impact: none`; não existe interface a moldar ou direção visual a definir.

## Impeccable Critique

N/A — `UI impact: none`; produto/UX visual, acessibilidade e responsividade não se aplicam ao script operacional. A crítica operacional está em `Design Critique`.

## Impeccable Audit

N/A — `UI impact: none`; não há DOM, CSS, theming, performance de renderização ou interação visual para auditar.

## Impeccable Trace

N/A — `UI impact: none`; pipeline Impeccable e critics A/B visuais não são acionados.

## Prototype

N/A — a change não cria nem altera superfície visual; a evidência adequada é saída determinística do guard e testes com snapshot/`gh` falso.

## Prototype Validation

N/A — sem protótipo e sem browser gate por `UI impact: none`. A implementação deverá ser validada por testes focados do `release-guard`, `audit` com os casos da issue e validação OpenSpec, somente após aprovação humana.

## Veredito

Design Agent verdict: PASS

O problema, a hipótese, o algoritmo, os limites fail-closed, os sete casos de regressão e a limpeza autorizada estão especificados sem achado P0/P1 aberto. Este PASS conclui apenas o gate de autoria/crítica; não aprova desenvolvimento nem autoriza archive.
