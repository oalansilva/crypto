# Design: Varredura sistemática de estratégias swing

## Status do gate

- Card: `#469`
- Change: `card-469-varredura-backtest`
- Status observado no packet: `Design`
- **UI impact: affected** — a change adiciona configurador, preflight, lifecycle, histórico, leaderboard, estados críticos e promoção dentro do shell autenticado de Combo.
- Aprovação humana: pendente. Este artefato não aprova nem move o card para `Pronto para Dev`.

## Problema

O administrador repete manualmente combinações de template, símbolo, timeframe e direção e reconcilia resultados fora do produto. O fluxo não antecipa o total executável, não preserva de forma explícita as fronteiras de retries/concorrência e pode misturar identidade de estratégia, evidência histórica e promoção.

## Usuário e contexto

Administrador do beta fechado realizando análise de longa duração. Ele conhece métricas de risco, mas precisa de evidência comparável, recuperação segura e separação inequívoca entre rascunho, sweep ativo e run histórico. A tarefa é desktop-first e permanece completa em mobile.

## Hipótese

Se a matriz de descoberta virar snapshot server-side revalidável, for executada por uma máquina de estados completa e produzir ranking determinístico com identidade de estratégia estável, proveniência separada e promoção exclusivamente tier 3, o administrador encontrará candidatos com menos repetição, ambiguidade e risco de duplicidade.

## Resultado esperado

- Preflight informa eixos normalizados, bruto, exclusões, limites, total válido, expiração, token e hash.
- Criação deriva `actor` do principal autenticado, usa UNIQUE `(actor, idempotency_key)` e compara `payload_hash` persistido; retry idêntico devolve o mesmo `sweep_id` e hash divergente retorna `409`.
- Lifecycle distingue falha operacional de 100% de falha por `terminal_reason`; cancelamento prevalece e bloqueia pause/resume em `cancelling`.
- `processed = succeeded + failed + skipped` deriva de uma única fonte para qualquer total, inclusive `1` e `<13`.
- Outbox/queue operam at-least-once sem duplicar combinação ou resultado após crash/redelivery.
- Ranking compara janelas UTC `[start_at,end_at)`, calendário/candles/custos e coverage com denominador reproduzível.
- `strategy_identity_key` detecta duplicidade sem janela; `evidence_fingerprint` registra proveniência e não serve de escape.
- Histórico troca lifecycle, snapshot, contagens, linhas, modal e feedback pelo `sweep_id` selecionado, bloqueando promoção durante loading.
- Promoção válida cria exatamente um favorito tier 3 e mantém foco em status visível após sucesso.

## Não objetivos

- Gerar templates inéditos ou promover automaticamente.
- Suportar timeframes fora de `4h` e `1d`.
- Alterar fórmulas do otimizador ou prometer desempenho futuro.
- Expor a ferramenta a não administradores.
- Redesenhar o shell ou outras superfícies do produto.

## Base visual e fidelidade

O protótipo preserva o shell autenticado de Combo: sidebar de 224 px, header de 80 px, canvas `#0b0e11`, superfícies `#181a20`/`#1e2329`, hairline `#2b3139`, CTA `#fcd535`, foco/info `#3b82f6`, editorial Inter e números tabulares IBM Plex Sans. `DESIGN.md` permaneceu read-only.

Tokens aplicados nesta rodada:

- `muted-strong #929aa5` em texto pequeno para atingir contraste AA;
- trading red base `#f6465d`, com tint acessível `#ff8294` para texto sobre superfície elevada;
- verde/vermelho apenas para Long/Short e desempenho financeiro;
- lifecycle e feedback operacional em azul, amarelo e neutros;
- CTA disabled `#3a3a1f`, raios de 4–12 px e superfícies planas.

## Decisões de produto, UX e contrato

### 1. Preflight server-side é a fonte do total

`POST /combos/discovery/sweeps/preflight` devolve eixos normalizados, `raw_total`, combinações válidas, exclusões por `template × symbol × timeframe`, limites, `valid_total`, expiração, `snapshot_token` e `snapshot_hash`. Criação revalida token, ator, hash, catálogo e limites na transação que persiste sweep, combinações e outbox.

### 2. Idempotência identifica a chave e compara o conteúdo

A restrição única é `(actor, idempotency_key)`, mas `actor` é sempre derivado do principal autenticado e nunca confiado do cliente. O registro guarda `payload_hash` normalizado/versionado e a identidade da resposta. Mesmo hash retorna o recurso original; hash divergente, inclusive em corrida concorrente, retorna `409` sem mutação. O mesmo contrato vale para criação e promoção. `403` fica reservado a autorização negada.

### 3. Máquina de estados completa

Estados: `pending`, `running`, `paused`, `cancelling`, `cancelled`, `failed`, `partial_failure`, `completed`. Terminais: `cancelled`, `failed`, `partial_failure`, `completed`.

| Origem | Destinos permitidos |
| --- | --- |
| `pending` | `running`, `cancelling`, `failed` |
| `running` | `paused`, `cancelling`, `completed`, `partial_failure`, `failed` |
| `paused` | `running`, `cancelling`, `failed` |
| `cancelling` | `cancelled`, `failed` |
| terminal | nenhum |

`failed` exige `terminal_reason`: `all_results_failed` para reconciliação normal com `succeeded=0` e `failed>0`, ou `operational_failure` com código de setup/execução/cancelamento. Antes de **qualquer** caminho para `failed`, outcomes commitados são preservados e toda combinação ainda não terminal vira `skipped`; assim `processed = succeeded + failed + skipped = total`. Em particular: `pending → failed` pula todas as não iniciadas; `running|paused → failed` preserva outcomes e pula pendências; `cancelling → failed` preserva leases resolvidas, pula o restante e mantém a intenção de cancelamento na auditoria. `partial_failure` fica exclusivo à reconciliação normal com sucessos e falhas; `completed` exige sucesso e zero falha. Cancelamento é intenção mais forte: pause/resume são rejeitados em `cancelling`.

### 4. Contadores derivam da combinação persistida

Em toda leitura: `processed = succeeded + failed + skipped`, `0 ≤ processed ≤ total`. Cancelamento converte pending em skipped depois de reconciliar leases ativas. O protótipo prova total padrão `46`, total `1` e total abaixo de `13` sem constantes `12+1` aplicadas fora do estado corrente.

### 5. Outbox at-least-once usa um orquestrador por sweep

Topologia escolhida: **um job orquestrador por sweep/wake-up**, não um job durável por combinação. O payload contém `sweep_id` e geração/versionamento; o job reclama combinações no PostgreSQL em lotes.

- dispatcher lê até 100 intents por poll e publica lotes de até 20;
- defaults de backpressure: 8 orquestradores globais e 1 por sweep;
- cada ativação reclama até 20 combinações;
- publish aceito antes do ACK da outbox pode redeliver;
- resultado commitado antes do ACK da fila é reconhecido pela unique key e não reexecutado;
- valores são configuráveis/versionados e fairness usa round-robin/idade.

### 6. Identidade de estratégia não é evidência

`strategy_identity_key` inclui estrutura/versionamento, parâmetros efetivos quantizados, símbolo, timeframe e direção. A janela não participa da identidade.

`evidence_fingerprint` inclui janela UTC, calendário, candle source/version, gaps/coverage, fees/slippage e snapshot de métricas. Evidência diferente permanece auditável, mas não contorna duplicidade de estratégia. Promoção serializa por lock/registry da `strategy_identity_key`.

### 7. Comparabilidade é explícita

Toda janela usa UTC e intervalo `[start_at,end_at)`. Cada source/version + timeframe define calendário esperado 24×7 e `expected_candles`. Coverage é `observed_valid_candles / expected_candles`; gaps não recebem forward-fill para melhorar elegibilidade. Duplicatas/out-of-order seguem normalização determinística. Resultados expõem calendário, source/version e custos antes de serem comparados.

Elegibilidade default/versionada: `trades ≥ 30` e `coverage ≥ 90%`. Abaixo disso, o resultado permanece auditável com `Baixa amostra`, sem rank e sem promoção.

### 8. Ranking é determinístico

Calmar é default; alternativa é Δ versus Buy and Hold. Ordem: métrica finita desc, trades desc, `result_id` asc. Negativo finito precede `N/A`. Filtro e paginação preservam rank global. Buy and Hold é benchmark long-only sobre os mesmos candles/janela, inclusive para short.

As fixtures `RS-1048` e `RS-1049` empatam em Calmar `2,84`, mas têm respectivamente `44` e `45` trades. O ranking coloca `RS-1049` primeiro apesar do ID maior, provando que trades desempata antes de `result_id`; um cenário separado preserva o desempate final por ID quando métrica e trades também empatam.

### 9. Histórico troca um snapshot inteiro

O seletor de runs entra em loading e desabilita promoção. A conclusão troca atomicamente lifecycle, snapshot, janela/candles, contagens e linhas. Dialog e toast usam o run/result selecionados. O sweep ativo continua identificado em bloco separado.

### 10. Promoção é exclusivamente tier 3 e gerencia foco

Não existe seletor de tier. O dialog mostra candidato, mercado, `sweep_id`, `result_id` e `Tier 3 · observação`. Após sucesso, a linha permanece visível, assume status `Favorito tier 3` e recebe foco. Cancelamento terminal move foco para o heading/status visível.

### 11. Estados críticos são navegáveis

O protótipo oferece fixtures coerentes e recuperação específica para: limite excedido (`1.248 > 1.000`, painel e CTA derivados do mesmo snapshot de cenário), snapshot expirado (gera outro snapshot válido), erro transitório (retry preserva/recarrega o erro), conflito equivalente de promoção (`409` com referência vencedora) e autorização negada (`403`, retorno sai da área administrativa). `Reduzir escopo` encerra o snapshot crítico, retorna ao preflight do rascunho recalculado e atualiza painel/CTA para o mesmo total (`46`). Qualquer alteração posterior dos eixos também recalcula ambos pela mesma fonte. Loading de histórico bloqueia promoção; ações incompatíveis ficam disabled.

### 12. Escala do protótipo representa topologia

Decisão P2 aceita: o protótipo prova busca, selecionar visíveis, live counts, filtro e paginação, mas usa amostra navegável em vez de materializar 30 templates × 126 símbolos. Produção deverá paginar ou virtualizar o catálogo completo conforme medição; a amostra não implica carregar todos os itens no DOM.

## Arquitetura proposta

- `DiscoverySweep`: ator, state, idempotency key/hash, snapshot imutável, counters, versões e timestamps.
- `DiscoveryCombination`: unique combination key, state, attempts, lease owner/expiry e result reference.
- `DiscoveryResult`: `strategy_identity_key`, `evidence_fingerprint`, parâmetros, métricas, coverage, elegibilidade e dedup corrente.
- `DiscoveryDedupEvidence`: histórico append-only de versões, dimensões e referência comparada.
- `DiscoveryOutbox`: wake-up do orquestrador, tentativas e ACK at-least-once.

API proposta:

- `POST /combos/discovery/sweeps/preflight`
- `POST /combos/discovery/sweeps`
- `GET /combos/discovery/sweeps/{sweep_id}`
- `POST /combos/discovery/sweeps/{sweep_id}/pause|resume|cancel`
- `GET /combos/discovery/sweeps/{sweep_id}/leaderboard`
- `POST /combos/discovery/results/{result_id}/promote`

## Riscos e mitigação

| Risco | Severidade | Mitigação |
| --- | --- | --- |
| Catálogo muda entre preflight/start | P1 | Token/hash expirável e revalidação atômica. |
| Publish aceito e crash antes do ACK | P1 | Outbox at-least-once, payload idempotente e redelivery. |
| Resultado commitado antes do ACK da fila | P1 | Unique result/combination e handler idempotente. |
| Pause/resume corre contra cancel | P1 | Matriz explícita; `cancelling` prevalece. |
| Outra janela evade duplicidade | P1 | Identidade sem janela; evidência separada. |
| Ranking mistura calendários/gaps | P1 | UTC, `[start,end)`, calendário/coverage versionados. |
| Histórico parece pertencer ao ativo | P1 UX | Fixtures/snapshot completos por run e loading bloqueante. |
| Catálogo completo degrada o DOM | P2 | Paginação/virtualização em produção; topologia explícita no protótipo. |
| Teste destrutivo herda `backend/.env` e aponta para DEV/PROD | P0 | Guard global executado no `conftest.py` raiz antes de importar a aplicação; somente bancos `*_test` ou PostgreSQL descartável do GitHub Actions são aceitos. |

## Prototype

- URL canônica: `https://dev.criptofarol.com.br/prototypes/card-469-varredura-backtest/`
- Caminho: `frontend/public/prototypes/card-469-varredura-backtest/index.html`
- SHA-256 final da rodada 5, validado localmente: `de4482aea9063326a9ba2539d658391d12a0bcad369308457a6a956b9b1e82bb`
- Base: shell autenticado atual de Combo; somente o delta da descoberta.
- Viewports: desktop `1440×1000` e mobile `390×844`.
- Versão: quinta rodada de correções pós-Assessment A/B, vinculada ao browser gate local final de 93 asserts.
- Evidência canônica publicada: a URL DEV serviu `bc3d908ef9d281da7c4fbfd5463297c4a7d22d7d32dd24b933c83d7af0e6d511` no gate canônico de 91/91 asserts, axe 12/12 e zero erros. A rodada 5 altera apenas a fixture de desempate e espera sincronização pela sessão principal para o digest final acima.

## Impeccable Brief

- **Job/audiência:** administrador executa descoberta swing em escala sem repetir runs ou perder origem; modo `Operate`.
- **Resultado:** snapshot observável, lifecycle recuperável, ranking comparável e promoção tier 3 somente para candidato elegível/único.
- **Direção:** extensão densa e sóbria do Combo; dark canvas, hairlines, números tabulares e CTA amarelo existentes.
- **Escopo:** superfície responsiva; shell e demais áreas permanecem intactos.
- **Estados:** default, preflight, total 1/<13/padrão, running/paused/cancelling/terminal, loading/histórico, erro, stale, over-limit, permission denied, conflito e promoção.
- **Restrições:** admin-only, WCAG AA, targets 44 px, sem promessa financeira, sem reescrever `DESIGN.md`.

## Impeccable Critique

### Assessment A/B e quinta rodada

- Assessment A: contexto read-only separado, `openai/gpt-5.6-sol`; reportou o P1 documental e o P2 da fixture. Após esta rodada, veredito final **APPROVE**.
- Assessment B: contexto read-only separado, `openai/gpt-5.6-sol`; reportou os mesmos P1 e P2. Após esta rodada, veredito final **APPROVE**.
- Igualdade observável: autor e assessments usam `openai/gpt-5.6-sol`; autor com reasoning effort `high`.

| Severidade | Finding | Correção e evidência |
| --- | --- | --- |
| P1 | `design.md` mantinha evidência e veredito obsoletos e pedia publicação/revalidação embora a URL canônica já tivesse servido `bc3d908e…` no gate verde. | **Resolvido:** a evidência canônica de `bc3d908e…`, 91/91 asserts, axe 12/12 e zero erros foi registrada; o texto operacional obsoleto foi removido. A rodada 5 tem digest esperado próprio e gate local pós-alteração. |
| P2 | `RS-1048` tinha mais trades e ID menor, portanto a ordem não isolava a precedência de trades sobre ID. | **Resolvido:** Calmar continua empatado em `2,84`, mas `RS-1049` agora tem 45 trades e `RS-1048`, 44. Asserts desktop/mobile provam `RS-1049` primeiro apesar do ID maior; a spec separa esse cenário do desempate final por ID. |

### Crítica final do autor

- Produto/UX: o administrador não recebe números contraditórios entre estado crítico e ação; a recuperação fecha o snapshot inválido de forma causal.
- Ranking: a ordem métrica desc → trades desc → ID asc agora isola o segundo critério contra a direção oposta do ID e mantém cenário separado para o terceiro.
- Acessibilidade: live regions, foco, Escape/ARIA, região rolável e targets permanecem íntegros; axe ficou verde.
- Responsividade/estados: gate completo em desktop/mobile, default e cinco críticos, sem overflow ou erros de navegador.
- P0/P1 aberto: **zero**. A sincronização do digest final para a URL DEV é handoff operacional da sessão principal, não uma aprovação humana nem um achado de design aberto.

## Impeccable Audit

| Dimensão | Score | Evidência |
| --- | ---: | --- |
| Acessibilidade | 4/4 | Axe WCAG A/AA em default + 5 críticos, desktop/mobile: 12 execuções, 0 violações; foco/ARIA assertados. |
| Performance | 4/4 | HTML autocontido, sem assets pesados ou catálogo integral no DOM. |
| Responsividade | 4/4 | Mobile `390×844` sem overflow; modal cabe; targets ≥44 px. |
| Theming | 4/4 | Tokens do `DESIGN.md`; `DESIGN.md` permaneceu read-only. |
| Integridade | 4/4 | Detector final `[]`; 93 asserts; fixtures específicas por run/estado/status HTTP e desempate adversarial. |
| **Total** | **20/20** | Zero finding determinístico e zero P0/P1 técnico aberto. |

### Detector final

- Comando: `node /srv/apps/dev/criptofarol/source/.agents/skills/impeccable/scripts/detect.mjs --json frontend/public/prototypes/card-469-varredura-backtest/index.html`
- Resultado após a última alteração do HTML: `[]`.

## Impeccable Trace

1. **Context:** `context.mjs` executado uma vez nesta sessão; PRODUCT/DESIGN carregados; `DESIGN.md` read-only.
2. **Shape:** modo Operate; preservar shell e corrigir somente coerência de cenário/ranking.
3. **Prototype:** HTML do caminho canônico corrigido na worktree, sem tocar produção.
4. **Critique:** Assessments A e B reportaram o mesmo P1 documental e P2 da fixture; ambos estão resolvidos e com veredito final `APPROVE`.
5. **Audit:** detector final `[]`; axe default + cinco críticos em ambos viewports.
6. **Targeted fixes:** evidência canônica reconciliada; fixture invertida para `RS-1049=45` versus `RS-1048=44`; cenários de trades e ID separados na spec.
7. **Polish:** narrativa, spec, fixture e asserts agora descrevem a mesma precedência determinística sem ambiguidade.
8. **Browser gate:** rodada 5 em Chromium real local, `93/93`; gate canônico anterior da versão publicada, `91/91`; ambos com zero console/page errors.

Metadados:

- Autor: `design-planner`, `openai/gpt-5.6-sol`, reasoning effort `high`.
- Assessments: contextos read-only separados, `openai/gpt-5.6-sol`; A e B `APPROVE` após resolução da rodada 5.
- Screenshots/pixel judgment: não utilizados; este agente não interpretou pixels.
- Digest final validado localmente: `de4482aea9063326a9ba2539d658391d12a0bcad369308457a6a956b9b1e82bb`.
- Digest validado na URL canônica antes da fixture da rodada 5: `bc3d908ef9d281da7c4fbfd5463297c4a7d22d7d32dd24b933c83d7af0e6d511`.

## Prototype Validation

- URL canônica: `https://dev.criptofarol.com.br/prototypes/card-469-varredura-backtest/`.
- Gate canônico concluído antes da rodada 5: URL canônica acima, digest publicado `bc3d908ef9d281da7c4fbfd5463297c4a7d22d7d32dd24b933c83d7af0e6d511`, **91/91 asserts**, axe **12/12**, 0 violações, 0 `console.error` e 0 `pageerror`.
- URL aberta no gate pós-alteração da rodada 5: `http://127.0.0.1:4180/prototypes/card-469-varredura-backtest/`, servida da worktree em `frontend/public`.
- Browser: Chromium real via Playwright; script `/tmp/opencode/card469-browser-gate-v3.cjs`.
- Viewports: desktop `1440×1000`; mobile `390×844`.
- Resultado final da rodada 5: **93/93 asserts, 0 falhas, 0 `console.error`, 0 `pageerror`.**
- Axe 4.10.3, WCAG A/AA: **12 execuções/0 violações** — default, over-limit, stale, retry-error, conflict 409 e permission-denied 403 em desktop e mobile (passes: desktop `28/29/29/29/29/30`; mobile `25/26/26/26/26/26`).
- Digest local/servido no gate da rodada 5: `de4482aea9063326a9ba2539d658391d12a0bcad369308457a6a956b9b1e82bb`.
- Digest publicado validado no gate canônico anterior: `bc3d908ef9d281da7c4fbfd5463297c4a7d22d7d32dd24b933c83d7af0e6d511`. A sessão principal sincronizará o HTML da rodada 5 para que a URL DEV passe a servir o digest esperado `de4482ae…`; nenhum arquivo fora da worktree foi editado nesta rodada.

### Asserts cobertos

- default/preflight: shell, `48` brutas, `2` excluídas, `46` válidas e nomes acessíveis de métricas;
- ranking: negativo finito antes de `N/A`; empate Calmar `2,84` com `RS-1049=45` e `RS-1048=44`, `RS-1049` primeiro apesar do ID maior em desktop/mobile; dedup/baixa amostra bloqueados;
- modal: Escape fecha a instância pós-clonagem, retorna foco ao gatilho visível e define `aria-expanded=false`, em desktop/mobile;
- over-limit: painel/preflight/CTA usam `1.248`; start disabled; redução retorna ao cenário normal e painel/preflight/CTA convergem em `46`, CTA enabled, copy e foco coerentes;
- stale: snapshot expirado é substituído por novo snapshot `REVALIDADO` válido;
- retry: nova tentativa mantém o estado de erro e recarrega copy com contador/erro preservado;
- conflito/autorização: equivalente usa `409` + referência vencedora `FT-8831`; permissão usa `403` e `Voltar ao Combo` remove a operação administrativa;
- acessibilidade crítica: `#table-wrap` focável e axe zero em cada estado crítico, nos dois viewports;
- lifecycle padrão: `13 = 12 + 1 + 0`, pause/resume, `cancelling` observável e pause bloqueado, cancel `46 = 12 + 1 + 33`;
- total `1`: `1 = 1 + 0 + 0`, terminal completed e controles bloqueados;
- total `<13` (`4`): running `1 = 1 + 0 + 0`, cancel `4 = 1 + 0 + 3`;
- foco de cancelamento: `activeElement=#progress-heading`, visível;
- histórico #04: loading/ação bloqueada, snapshot `#PF-293884-38`, lifecycle, UTC/candles e linhas `RS-930x`; ausência de `RS-1048`;
- promoção #04: modal/result/origem corretos, toast com #04 e foco no status promovido visível;
- mobile: shell, menu fora de escopo disabled, sem overflow, targets ≥44 px, ordenação negativa/N/A, Escape e todos os estados críticos;
- console/page errors: zero.

Qualquer alteração posterior no HTML/CSS/JS invalida este digest e exige novo detector/browser gate.

## Design Critique

### Veredito consolidado dos critics

Assessment A: **APPROVE pós-correção**. Assessment B: **APPROVE pós-correção**. A quinta rodada resolve o P1 de evidência/veredito obsoletos e o P2 da fixture que não isolava trades contra ID. Detector `[]`, axe `12/12`, gate canônico publicado `91/91` e gate local pós-alteração `93/93` estão verdes. Não há P0/P1 aberto.

### Veredito formal do gate

**Design Agent verdict: PASS**

Os dois assessments estão aprovados após a rodada 5, sem P0/P1 aberto. Este veredito é documental: não aprova o design em nome de Alan e não libera desenvolvimento. A sessão principal ainda deve sincronizar o digest final esperado para a URL DEV e pode mover somente `Design -> Aprovação de Design`; Alan decide exclusivamente `Aprovação de Design -> Pronto para Dev`.

## Handoff

- Rodada: 5; A `APPROVE`, B `APPROVE`; zero P0/P1 aberto.
- Protótipo final local/esperado na publicação: `de4482aea9063326a9ba2539d658391d12a0bcad369308457a6a956b9b1e82bb`.
- Evidência final: detector `[]`; Playwright local `93/93`; axe `12/12` sem violações; console/page errors zero. Evidência canônica publicada anterior: `bc3d908e…`, `91/91`, axe `12/12`, zero erros.
- Próximo responsável: sessão principal sincroniza o digest final na URL canônica, consolida/publica os artefatos e move no máximo `Design -> Aprovação de Design`.
- Aprovação humana: pendente; somente Alan pode mover `Aprovação de Design -> Pronto para Dev`.
