# Snapshot de crítica de Design — #1091

Issue: https://github.com/oalansilva/crypto/issues/1091
Change: card-1091-discovery-cache-numba
Data: 2026-10-12
Status recebido do orquestrador: Design; nenhuma transição realizada.
Branch/worktree informado: card-1091-discovery-cache-numba / /srv/apps/dev/criptofarol/crypto-worktrees/card-1091-discovery-cache-numba.
Escopo desta revisão: Design SEM TELA, única crítica, sem implementação nem benchmarks.

## Artefato e fontes

Design revisado: openspec/changes/card-1091-discovery-cache-numba/design.md
SHA-256 dos bytes do design: 754926c21219549a38e74fe8a7fc32b6c0dfa4a9689339d4a412af7438221e59
Wordcount design.md: 1278 (split por whitespace).
HTML gerado/copied: N/A; não há protótipo.

Lidos: skills canônicas covenant-flow e design-critic; body vivo do issue via REST gh api; proposal.md, design.md, tasks.md, specs/combo-optimizer/spec.md e evidence/README.md. Não foi executada inspeção de produto ou benchmark. Os anexos de investigação não foram revalidados: seus números permanecem evidência histórica declarada, não resultados desta crítica.

## Rubrica e verificação de escopo/aceite

- Gate sem tela: PASS. O primeiro autor traz UI impact: none, live_route: N/A e surface: none em linhas próprias, com justificativa de processamento interno sem alteração de interação/apresentação. Nenhuma rota emprestada.
- Briefing: PASS. Proposal preserva Problema, História, Entra, critérios de aceite e Não entra do issue consultado. O design detalha a abordagem e declara limites da evidência experimental.
- Busca e contratos: PASS. Mesmos candidatos, tentativas, rodadas, filtros, score, desempate, métricas, TA-Lib e consumidores compartilhados. Referência de 21.210 tentativas/zero falhas permanece requisito, não resultado afirmado desta etapa.
- Equivalência: PASS. Comparação estrutural de indicadores, máscaras, índices, trades completos, treino/holdout e GO/NO-GO sem tolerância/rounding; NaN nas mesmas posições; campos voláteis identificados previamente. Hash não substitui comparação estrutural.
- Isolamento e memória: PASS. Contextos separados de treino/final/holdout, burn-in e filtro atuais, snapshots privados, identidade integral, ownership, limites de entradas/bytes, eviction e invalidação adversarial. Não há escolha por informação de holdout.
- Desempenho: PASS. Cinco pares alternados, três workers, mesmo ambiente/dados, mediana menor e pelo menos três pares melhores. 25% é objetivo; 24,91 s não é SLA. Cenários secundários têm cinco pares e regressão sustentada definida. Preparação/snapshots/transporte entram no tempo normal; JIT inicial é separado.
- Componentes: PASS. Cache por indicador condicionado a ablação repetida contra fingerprint+Numba, sem aceitar hit rate como benefício. Núcleos numéricos preservam semântica e deixam TA-Lib/PnL/métricas nas fontes atuais.
- Fallback/reversão: PASS. Fallback Python equivalente não mascara erro de negócio; reversão integral pós-945 distinta da flag pre-945, com matriz de precedência e processo novo/caches limpos.
- Abrangência/evidência: PASS. Tasks cobrem 14 templates, dois símbolos, long/short, 1d/4h, Deep/fallback, casos adversariais, consumidores, memória, pins e harness durável. README distingue investigação e validação futura; referência inspecionada não é atribuída indevidamente ao experimento histórico.
- Exclusões: PASS. Sem UI/configuração de operador, mudança de busca/fórmulas, pool persistente, workers extras ou publicação nesta etapa.

## Achados e disposition

- P0: nenhum.
- P1: nenhum.
- P2: nenhum.
- P3: detalhes já aceitos no Design — representação serializável, nomes internos/flag, orçamento calibrado com RSS, pins confirmados por instalação e inclusão do cache individual conforme ablação. Disposition: aceitos como detalhe de Apply; preservar critérios explícitos e resolver nas tasks existentes, sem nova rodada ou ampliação do escopo.

Verdict de Design: favorável à submissão para Aprovação de Design, sem rework obrigatório. Não equivale à aprovação humana T7 nem comprova implementação ou ganho de produto. Teto aplicado: um autor + um crítico; nenhum novo P0 exige rodada adicional.

## Validação executada

openspec validate card-1091-discovery-cache-numba --strict: PASS (Change is valid).
Coleta de digest/wordcount: python3, leitura dos bytes locais. A tentativa inicial com python falhou por executável ausente; corrigida para python3. Nenhum teste de produto ou benchmark foi executado.

## Metadata do nascimento e runtime

model_selection_capture: /tmp/card-1091-design-critic-model.json
attempt_id: f1e2c328-e7ce-48d5-b4f2-547d593ce0ec
capture_sha256: 60cdc1bb71093b3c5455d8a0d0c0cd1bb0d0359393c664e838772d7fc66bdabb
Cliente solicitado: codex
Faixa/papel: juizo / design-critic
Modelo solicitado: gpt-6-astra (GPT-6 Astra)
Esforço solicitado: medium
Modelo observado por fonte autoritativa de runtime: unavailable
Esforço observado por fonte autoritativa de runtime: unavailable
Host/versão observados: unavailable
Runtime/trace autoritativo: unavailable
Configuração e pedido não comprovam valores observados. A revisão substantiva terminou; gate de correspondência do runtime permanece não comprovado e deve falhar enquanto exigir esses metadados. Não inferir sucesso desse gate a partir do verdict de Design.

proxy modelo: design-critic → GPT-6 Astra (gpt-6-astra)
Spawns realizados por este crítico: 0.
Status do trabalho de crítica: completed, com payload no retorno ao orquestrador.
