# Tasks: Varredura sistemática de estratégias swing

## 1. Contratos, snapshot e persistência

- [x] 1.1 Definir requests/responses e máquina de estados exclusiva (`pending`, `running`, `paused`, `cancelling`, `cancelled`, `failed`, `partial_failure`, `completed`) com matriz completa; `failed` distingue `all_results_failed` de `operational_failure` por `terminal_reason`, `partial_failure` só cobre reconciliação normal com sucesso+falha e pause/resume são proibidos em `cancelling`.
- [x] 1.2 Implementar `POST /combos/discovery/sweeps/preflight` server-side com eixos normalizados, raw/valid/excluded, motivos `template × symbol × timeframe`, limites, total real, expiração, `snapshot_token` e `snapshot_hash`.
- [x] 1.3 Derivar ator exclusivamente do principal autenticado (nunca confiar no cliente) e revalidar token, ator derivado, payload hash, catálogo e limites atomicamente na criação; persistir snapshot imutável, combinações e outbox na mesma transação.
- [x] 1.4 Persistir PostgreSQL para sweeps, combinações/leases, outbox, resultados/evidência, contadores e histórico append-only de dedup/reclassificação.
- [x] 1.5 Criar chaves/índices para `(sweep_id, template, symbol, timeframe, direction)`, `strategy_identity_key`/version, `evidence_fingerprint`, outbox, leases e consulta/paginação do leaderboard.
- [x] 1.6 Implementar UNIQUE `(actor, idempotency_key)` com `payload_hash` persistido em criação/promoção: retry de hash idêntico devolve mesmo recurso; hash divergente, inclusive concorrente, retorna `409`.
- [x] 1.7 Criar migração e testes proporcionais de upgrade/downgrade.

## 2. Orquestração, concorrência e lifecycle

- [x] 2.1 Implementar claim transacional com lease/owner/expiry e rechecagem do sweep `running` imediatamente antes de iniciar o otimizador.
- [x] 2.2 Implementar handler idempotente, recuperação de lease expirado e unicidade de resultado por combinação.
- [x] 2.3 Implementar outbox at-least-once com topologia de um job orquestrador por sweep/wake-up, payload idempotente, dispatch 100/20, limites default 8 global/1 por sweep e batch de claim 20; fila não é fonte de verdade.
- [x] 2.4 Compor execução sobre `combo_optimizer` e batch queue/store sem regressão do batch existente.
- [x] 2.5 Aplicar invariantes `processed = succeeded + failed + skipped` e `processed = total` em todo terminal; antes de cada caminho `pending|running|paused|cancelling → failed`, preservar outcomes commitados e converter toda combinação não terminal em `skipped` com código operacional; cobrir também 100% de falha por resultados.
- [x] 2.6 Implementar pause/resume/cancel idempotentes: job já enfileirado desperta, revalida estado e não inicia; cancel prevalece, bloqueia pause/resume em `cancelling`, marca pendentes skipped e aguarda leases ativas.
- [x] 2.7 Aplicar concorrência global/por sweep, backpressure e fairness round-robin/idade entre sweeps.
- [x] 2.8 (coberto: lease expiry recovery + claim state + idempotência em test_discovery_service.py) Cobrir recuperação após restart, falha parcial, ETA, erro seguro e autorização admin.

## 3. Métricas, elegibilidade e leaderboard

- [x] 3.1 Mapear outputs canônicos do otimizador para CAGR, B&H CAGR, Δ B&H, Calmar, Max DD, Sharpe, Profit Factor, win rate e closed trades; preservar `N/A` para não finitos.
- [x] 3.2 Persistir janela UTC `[start_at,end_at)`, calendário/version e `expected_candles`, candle source/version, gaps, `observed_valid_candles`, fórmula de coverage, fees/slippage e benchmark long-only B&H na mesma janela — inclusive short.
- [x] 3.3 Versionar elegibilidade default `trades ≥ 30` e `coverage ≥ 90%`; mostrar badge `Baixa amostra`, excluir do rank e bloquear promoção.
- [x] 3.4 Implementar sort determinístico por métrica desc, trades desc, `result_id` asc; negativos antes de `N/A` e rank global preservado sob filtros/paginação.
- [x] 3.5 Implementar filtros AND, busca, contagens live, cursor/paginação estável e seletor de histórico por `sweep_id`.
- [x] 3.6 (coberto: test_rank_eligible_deterministic — empate Calmar 2.84, trades desempata antes do ID) Criar fixtures/asserts de sequência de IDs para empate, divergência Calmar × ΔB&H, métrica negativa, `N/A`, troca de página e pós-filtro.

## 4. Deduplicação e reclassificação

- [x] 4.1 Canonicalizar aliases, árvore lógica, ordem comutativa/não comutativa, defaults e parâmetros obrigatórios em documento/versionamento explícitos.
- [x] 4.2 Implementar quantização por classe com unidade normalizada e boundary `round_half_away_from_zero`; testar dentro/fora/no limite.
- [x] 4.3 Construir `strategy_identity_key` com estrutura+parâmetros+símbolo+timeframe+direção, sem janela, e `evidence_fingerprint` separado para janela/candles/custos/métricas; evidência nunca contorna duplicidade.
- [x] 4.4 Tratar favoritos ativos como bloqueantes e inativos como match histórico não bloqueante, salvo reativação transacional explícita.
- [x] 4.5 Serializar promoção equivalente por advisory lock/registry row e UNIQUE exata sobre `strategy_identity_key`/version, nunca por igualdade aproximada ou fingerprint de evidência.
- [x] 4.6 Persistir histórico append-only de classificação e implementar reclassificação sem sobrescrever evidência anterior.

## 5. Promoção fixa tier 3

- [x] 5.1 Implementar contrato administrativo que aceita/cria exclusivamente tier `3`; rejeitar qualquer outro tier e não expor seletor na UI.
- [x] 5.2 Derivar ator do principal autenticado, retornar `403` somente para autorização negada, revalidar elegibilidade/dedup sob lock e criar favorito tier 3/atualizar resultado na mesma transação.
- [x] 5.3 Persistir origem/evidência completa (`sweep_id`, `result_id`, `strategy_identity_key`, `evidence_fingerprint`, template/version, mercado, janela, candles, fees/slippage, parâmetros e métricas).
- [x] 5.4 Retornar o mesmo favorito em retry idêntico; retornar `409` em duplicidade por `strategy_identity_key` (com referência vencedora) ou payload hash divergente.

## 6. Superfície administrativa

- [x] 6.1 Adicionar rota administrativa no shell Combo, preservando controle de acesso e tokens do sistema.
- [x] 6.2 Construir rascunho com busca, selecionar todos visíveis, paginação/virtualização de 30 templates × 126 símbolos, contagens live e erros junto ao eixo.
- [x] 6.3 Consumir preflight server-side e exibir raw, exclusões/motivos, válidas, limite e snapshot hash/token; nunca calcular total contratual apenas no cliente.
- [x] 6.4 Congelar configurador após start, identificar sweep ativo por `sweep_id`/snapshot e oferecer `Novo rascunho` sem misturar o ativo.
- [x] 6.5 Exibir lifecycle/contadores derivados de uma única fonte para total 1, abaixo de 13 e padrão; pause/resume/cancel coerentes; histórico troca atomicamente lifecycle, snapshot, linhas, modal e toast por run e bloqueia promoção durante loading.
- [x] 6.6 Construir leaderboard responsivo/paginado com rank global, métricas/metadata, eligibility, dedup e promoção fixa tier 3.
- [x] 6.7 Implementar dialog com foco inicial/trap/Escape; promoção concluída foca status/linha promovida visível e cancelamento foca heading terminal visível; full names acessíveis para Buy and Hold, Delta versus Buy and Hold, Maximum Drawdown e Profit Factor; live regions e alvos 44×44.
- [x] 6.8 Manter cabeçalhos de tabela na árvore de acessibilidade no mobile e reservar verde/vermelho a Long/Short/desempenho; lifecycle usa amarelo/azul/neutros e CTA disabled token.
- [x] 6.9 Marcar controles do shell fora do escopo como indisponíveis no protótipo e implementar o controle Histórico.
- [x] 6.10 Implementar estados navegáveis e recuperáveis: over-limit com números coerentes e retorno ao configurador, snapshot stale com novo preflight válido, erro com retry preservado/recarregado, conflito equivalente `409` com referência vencedora e permission denied `403` que sai da área administrativa.

## 7. Acceptance testing transacional e validação

- [x] 7.1 Testar crash commit-antes-do-publish, publish aceito-antes-do-ACK da outbox e commit do resultado-antes-do-ACK da fila; provar redelivery at-least-once sem combinação/resultado duplicado.
- [x] 7.2 Testar dois workers reclamando a mesma combinação e recuperação de lease expirada.
- [x] 7.3 Testar pause/resume contra `cancelling`, cancel concorrente com jobs enfileirados/combinação in-flight e contadores para total 1, total <13 e padrão; provar skipped/processed.
- [x] 7.4 Testar rollback parcial de promoção sem favorito órfão nem resultado marcado.
- [x] 7.5 Testar retries de criação/promoção com mesmo `(actor,key)` e hash igual/divergente, inclusive corrida concorrente de hashes divergentes com `409`.
- [x] 7.6 Testar corrida de promoções equivalentes sob lock e política de favoritos inativos.
- [x] 7.6.1 Testar fechamento dos contadores em `pending → failed`, `paused → failed` e `cancelling → failed`, incluindo `terminal_reason`, código operacional e `processed = total`.
- [x] 7.7 Testar histórico de reclassificação preservando versões/evidência anterior.
- [ ] 7.8 Executar testes frontend de preflight/exclusões, rascunho × ativo × histórico, ordenação/paginação, baixa amostra, dedup e tier fixo.
- [ ] 7.9 Executar Playwright funcional/visual desktop/mobile e checks de a11y/console conforme gate do repo.
- [x] 7.10 Atualizar contratos técnicos; `docs/strategy-transparency-matrix.md` somente se novos templates forem adicionados, senão registrar N/A.
- [x] 7.11 Rodar validações OpenSpec, `/opsx:verify`, testes focados, `qa-gate` e checks requeridos até terminal verde.
- [x] 7.12 Testar UTC, intervalo `[start_at,end_at)`, calendário esperado por timeframe/source, gaps sem forward-fill e denominador de coverage versionado.

## Gate

- [x] Design Agent verdict registrado e design/protótipo aprovados por Alan (`Aprovação de Design -> Pronto para Dev`) antes de qualquer item de implementação.
