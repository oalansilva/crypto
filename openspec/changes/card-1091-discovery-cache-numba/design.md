## Context

#1091 evolui o motor acelerado de #945, referência inspecionada `64c1b97aec75b250ad4f32c0fd20692cf7a5f5b5`. Nenhum código de produto foi implementado no Design.

UI impact: none
live_route: N/A
surface: none

Justificativa: processamento interno compartilhado, sem mudanças de tela, interação ou apresentação. Impeccable: N/A pelo mesmo motivo. Prototype: N/A. HTML generated/copied: N/A.

`combo_optimizer.py::_window_identity` recalcula SHA-256 do OHLCV por tentativa, incluindo apenas extremos/tamanho do índice. `_indicator_cache_key` inclui indicadores após overrides, lógica e derived_features; `_WORKER_INDICATOR_CACHE` não tem teto explícito. `ComboStrategy.calculate_indicators` chama TA-Lib; `_fast_position_loop` controla posições. `deep_backtest.py::_fast_simulate_execution_with_15m` seleciona stops/saídas em arrays e monta trades/lucro em Python. `_ISO_CACHE` usa extremos/tamanho, insuficientes para índices internos diferentes. Final/holdout também usam `generate_signals` fora do worker.

Investigação: medianas 34,18598 s atual, 27,08589 s fingerprint, 24,90697 s combinação; 21.210 tentativas/hash completo igual. Triagens Numba+fingerprint e indicador+fingerprint tiveram só uma amostra cada. As 21 otimizações/404.586 tentativas sem falha, 2.800 comparações métricas/parâmetros e 568 edges são evidências experimentais, não validação de produto. Os 1.712 avisos preexistentes ficam preservados. Memoização por `id(df)` com referência forte e monkeypatch global TA-Lib do protótipo não são arquitetura pronta.

## Goals / Non-Goals

**Goals:** busca integral, equivalência exata de indicadores/máscaras/trades/métricas/vencedor/holdout/GO-NO-GO e ganho consistente. Objetivo 25%; aceite mediana menor e pelo menos três de cinco pares melhores. Preservar APIs e consumidores.

**Non-Goals:** mudar candidatos, rodadas, filtros, score, desempates, workers, fórmulas, TA-Lib, limiares; Optuna/random, pool persistente, UI ou configuração para operador. Medição de motor local não representa serviço ponta a ponta. Metas antigas de #945 não são piso incremental de #1091.

## Decisions

### Identidade segura e snapshots

Criar contexto interno por execução/janela, com cópia privada dos dados consumidos e arrays somente leitura, retendo referências fortes. Fingerprint uma vez por snapshot inclui todos os timestamps ordenados/timezone/unidade, esquema/dtypes, OHLCV completo e outras colunas consumidas. Contexto inclui geração da execução, fonte/símbolo/timeframe, papel da janela e limites de avaliação. Restabelecer imutabilidade no worker após serialização; DataFrame mutável externo não prova identidade.

Treino, final do treino e holdout com burn-in usam contextos distintos. Manter tail atual do treino + holdout para indicadores e filtro atual de entradas anteriores ao início do holdout. Nada do holdout entra na escolha. Releitura para resultado final cria snapshot novo; mudança OHLCV, índice interno, janela ou fonte invalida reuso.

DataFrame sem contexto confiável recebe fingerprint completo na entrada ou caminho atual sem memoização. `id(df)`, extremos/tamanho, metadata herdada ou token externo nunca provam imutabilidade. Batches desserializados transportam contexto validado internamente. Custos de snapshot/cópia/serialização entram no benchmark normal. Não reordenar dados além do atual nem cachear resultados completos de tentativa.

### Caches com ownership e limites

Caches tocados/introduzidos usam LRU por processo/execução, tetos simultâneos de entradas e bytes retidos, contando referências fortes. Orçamento inicial 64 MiB e 4.096 entradas por processo, até 32 snapshots; valores P3 calibráveis por RSS/benchmark. Item maior não entra; eviction recalcula. Limpar ao encerrar/trocar execução, inclusive no pai com chamadas sucessivas; medir RSS agregado dos três workers e overhead.

Reuso exige identidade completa e parâmetros após overrides/defaults/coerções atuais. Chave composta inclui lógica, derived_features e versão do esquema. Chave individual inclui função TA-Lib, entradas e todos os kwargs efetivos, períodos/tipos/desvios. Não colidir valores distintos por normalização. Stops/direção seguem como entradas dos loops; só ficam fora da chave do indicador se ele não os consumir.

Arrays cacheados somente leitura; sinais/colunas recebem buffers próprios/cópias, sem confiar em shallow copy pandas. `_ISO_CACHE` passa a identidade integral do índice/timezone com teto. Intraday/coverage vinculam geração/snapshot, evitando herdar candles antigos apenas por símbolo/datas iguais.

### Compilar apenas núcleos numéricos

Extrair funções puras do loop de posições e busca Deep, com adaptadores Python comuns. Entradas contíguas float64/bool/int64; saídas separam índices int64, códigos de motivo e preços float64. Não converter timestamps a float. Preservar expressões/ordem aritmética, NaN/inf/divisão por zero e precedência stop/sinal. `fastmath=False`, sem `parallel=True`/prange, novo pool ou mais workers. `nogil` não cria concorrência. Cache JIT em disco opcional; indisponível permite compilação em memória.

Deep mantém saída estritamente posterior, intervalo intraday semiaberto, primeiro stop, exclusão de posição sem saída final e sobreposição atual. Diário mantém entrada/saída no candle seguinte e precedência dos stops long; short mantém semântica atual. Não corrigir regras históricas aqui. TA-Lib, lógica vetorizada, strings/datas, PnL/custos e `_metrics_from_trades` continuam nas fontes atuais.

Adaptadores de ComboStrategy/Deep atendem Descoberta, laboratório, batch e favoritos. Fallback diário usa extrator atual com sinais equivalentes, inclusive 4h consumido; sem ramo exclusivo por template.

### Cache por indicador condicionado

Comparar repetidamente fingerprint, fingerprint+Numba e fingerprint+Numba+indicador. Integrar localmente no calculador TA-Lib, sem monkeypatch global/reimplementação. Tuplas MACD/BBANDS também protegidas. Incluir componente só com mediana menor e maioria dos pares melhor contra fingerprint+Numba, sem regressão sustentada secundária e dentro do orçamento. Sem benefício comprovado fica fora do caminho entregue; registrar ablação. Hit rate não basta.

### Dependências e reversão

Repo pina NumPy 2.4.6, pandas 3.0.3 e TA-Lib 0.6.8 em `backend/requirements.txt` e `requirements.lock`; Numba/llvmlite ausentes. Candidatos experimentais: Numba 0.68.0/llvmlite 0.50.0 com Python 3.12.3. Apply valida resolução/instalação limpa/import na plataforma suportada antes de piná-los nos dois arquivos; sem upgrades alheios nem garantia de outras plataformas.

Import tardio/opcional: ausência de compilador, compilação incompatível ou assinatura inelegível seleciona núcleo Python atual equivalente e diagnóstico operacional limitado. Não mascarar exceções de regra de negócio nem transformar erro em zero trades. Sem TA-Lib preservar falha/contrato atual, sem matemática substituta. Testar ausência de compilador, cache JIT indisponível e assinatura não suportada.

Controle interno `COMBO_OPTIMIZER_1091_DISABLED=1` desliga todos os componentes novos e volta ao atual acelerado de #945; nome P3, semântica obrigatória, sem UI/API. `COMBO_OPTIMIZER_LEGACY=1` conserva anterior a #945 e precedência se ambos ativos. Benchmark #1091 compara novo desligado/ligado com LEGACY ausente. Reversão usa processo novo/caches limpos; git revert adicional. Testar matriz de flags e igualdade exata.

## Validation

Versionar harness parametrizado por raiz/fixtures/commits, independente de `/tmp` e banco vivo para cálculos congelados. Protótipos anexados como texto são referência, não produto. Criar harness de testes sem monkeypatch global, manifesto SHA-256 e relatórios brutos. Comparar estruturas/arrays/índices completos e NaN nas mesmas posições sem tolerância/rounding. Campos voláteis identificados antes; por padrão nenhum excluído. Hash resume, não substitui comparação estrutural.

Cobrir 14 templates, dois símbolos, long/short, 50 parâmetros por combinação (2.800 casos) e pelo menos 568 edges, acrescentando indicadores/máscaras/datas/preços/lucro/motivos/treino/holdout/GO-NO-GO. Testar vazio, sem sinal, stop zero/extremo, conflito stop/sinal, NaN/inf/zero conforme baseline, fim sem saída, índice interno diferente de mesmos extremos, candle alterado sem alterar índice, metadata herdada, defaults/aliases equivalentes/distintos, A→B→A, fria/quente, eviction, mutação e execuções sucessivas. Validar 1d/4h, Deep e fallback por intraday vazio/incompleto, custos e consumidores comuns.

Primário: Multi-MA/1INCH/1d/long, 2023-01-01 a 2025-01-01, 70/30, Deep 15m, três workers. Cinco pares alternados atual/novo, mesmo hardware/ambiente, dados congelados, carga controlada, motor aquecido. Registrar tempos individuais, mediana/min/max/dispersão, ordem, CPU/RSS pai+workers, commits/deps, 21.210 tentativas/zero falhas e resultado completo igual. Mediana menor e três pares melhores bastam; 25% objetivo. AAVE short e EMA+RSI/1INCH long terão cinco pares: mediana pior e maioria pior define regressão sustentada que impede aceite até correção.

Medir primeira execução em processo novo e preparação JIT separadas, declarando imports/carregamento e cache JIT frio/quente. Investigação ~4,2 s inicial/~0,7 s seguintes não é limite contratual. Tempo aquecido inclui snapshots/transportes normais, exclui downloads/fila/persistência como estudo. CI decide equivalência/invariantes, nunca deadline. Nenhuma bateria longa executada durante Design.

## Risks / Trade-offs

- Cópias aumentam custo/memória → orçamento e benchmark incluindo preparação/RSS agregado.
- Chave incompleta contamina trades → identidade integral/contexto privado/testes adversariais.
- Numba muda bordas → kernels pequenos/compilação estrita/comparação exata.
- Ganho não se repete → pares/ablação, nunca reduzir busca.
- Dependência incompatível → instalação real/fallback testado, sem suporte presumido.

## Migration Plan

Após aprovação de Design e T8 implementar preservando baseline; validar dependências, equivalência, memória, consumidores e ganho. Sem migração de dados. Publicação pelo fluxo normal do pai, não executada neste Design. Reversão interna/processo novo com igualdade demonstrada.

## Open Questions

Sem decisão de produto pendente. P3 aceitos para Apply: nomes de helpers/flag, representação serializável, orçamento após medição, pins confirmados e inclusão de cache individual por ablação. Não reabrem escopo/aprovação humana.

## Design Critique

- P0–P2: nenhum. Disposition: sem bloqueio de produto, escopo ou contrato.
- P3: representação dos contextos, orçamento, pins e inclusão do cache individual por ablação. Disposition: aceitos para resolução no Apply.
- Verdict: favorável à submissão, sem rework obrigatório; OpenSpec estrito válido. Evidência de runtime dos filhos não comprovada, sem certificação de roteamento.
