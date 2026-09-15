UI impact: none
live_route: N/A
surface: new
motor de otimizar (varredura + laboratório + lote + revalidação); zero copy/layout; proto N/A.

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

## Context

Card [#945](https://github.com/oalansilva/crypto/issues/945). Briefing = issue grelhado (`grill-card fronteira vazia`). Decisões de operador fechadas; este Design não as reabre.

Cada combinação no caminho comum Deep+WF leva ~1–2,5 min. Baseline journal no serviço da Descoberta em DEV: `multi_ma_crossover` × `1INCH/USDT` × `1d` × long = **148 s** (sweep `3d9bee8b…`; 697 combinações, 40,5 h). Decomposição (combinação 878, sweep `18dd9e6f…`, 152 s): setup ~4 s · R1 16 614 trials = 93 s (3 workers) · R2–R4 ~6 000 trials em 10 branches sequenciais = 53 s · final < 1 s. Trial shipped 12–13 ms, ~50/50 `generate_signals` / `simulate_execution_with_15m`.

**Audience:** operador da Descoberta (e quem dispara otimizar no laboratório, no lote e na revalidação / regenerar favorito).
**Outcome:** ~10× por combinação no caminho comum, Deep 15m + walk-forward 70/30 intactos, números bit-a-bit iguais ao oráculo.
**Direction:** só velocidade no motor. Zero copy, layout, rotas, first-paint. Proto N/A. Nunca emprestar `/combo/discovery`, `/combo/select`, `/monitor`, `/favorites`, `landing`.

## Goals / Non-Goals

**Goals:**

- Caminho comum acelerado para **qualquer estratégia que a Descoberta aceita** (catálogo 11+3=14). Prova de tempo na representativa; o código é o runner comum.
- Laboratório, gerar em lote, revalidação de favoritos e regenerar favorito usam o mesmo caminho rápido neste card.
- Relógio ≤ 14,8 s (R1–R4 somados ≤ 11 s) no **mesmo serviço DEV** que mediu 148 s, velas já no disco. Testes automáticos = igualdade exacta, não wall-clock.
- Só velocidade: mesmas chamadas `talib.*`, mesmas expressões, cache da **saída**, golden exacto (`assert_array_equal`, zero `allclose`).
- Quatro alavancas + corte do setup quando as velas daquele par já cobrem o fim do período.
- Ordem determinística antes do score; 1 combinação em voo; Deep+WF, grid, score, elegibilidade intactos.
- Andar A (oráculo + fixtures + testes verdes) antes do andar B (velocidade). Pin de `TA-Lib` / `numpy` / `pandas`. Revert git A/B + `COMBO_OPTIMIZER_LEGACY=1` até Homologado em **todas** as telas do motor.

**Non-Goals:**

- Atalho só de SMA / cruzamento de médias; atalho só da varredura.
- Exigir ≤ 14,8 s na máquina dos testes automáticos.
- Paralelizar o sweep (`OUTBOX_MAX_PER_SWEEP` > 1).
- Mudar grid, steps, rondas, `top_k`, heurística `short<inter<long`, `_select_top_candidates`, burn-in, `BATCH_SIZE` semântico, `max_workers`.
- Reimplementar indicadores; trocar `talib`; reescrever PnL / fee `0.00075` / stop / score `0.7*ns + 0.3*nr` / métricas.
- 10× da página Discovery, Playwright, first-paint, copy, layout, rotas.
- Leaderboard, promoção/dedup, limiares de elegibilidade, preflight/create/lease/reconcile.
- Deploy PROD, `./restart`, reexecutar as 697 combinações ao vivo como gate.
- Custom/quant fora do catálogo como prova ou golden.
- `git reset --hard`, force-push, squash A com B, apagar `_legacy_*` / oráculo neste card.
- Invalidar `result_id` já persistidos após revert (fora deste card).
- Barra própria de 14,8 s para 4h, laboratório, lote ou revalidação.

## Decisions

### 1. Caminho comum, não atalho de médias

O acelerado é `run_combination` → `ComboOptimizer.run_optimization` → `_worker_run_batch` → `_run_backtest_logic` → `ComboStrategy.generate_signals` + Deep 15m. Serve a todos os 14 templates do catálogo. Sem `if multi_ma` / SMA.

Rejeitado: otimizar só SMA / cruzamento de médias e deixar o resto no caminho lento.

### 2. Laboratório, lote e revalidação neste card

Quem já chama o mesmo motor (laboratório de combo, gerar em lote, revalidação de favoritos, regenerar favorito) passa a usar o caminho rápido. Um furo no rápido é visível nessas telas até interruptor de legado ou revert git. Sem barra própria de 14,8 s.

Rejeitado: atalho só da varredura.

### 3. Prova de relógio só no serviço DEV da Descoberta

Barra: representativa `multi_ma_crossover` × `1INCH/USDT` × `1d` × long, `period_type=all`, `deep_backtest=True`, `split_train_ratio=0.7`, velas 1d+15m daquele par já no disco e a cobrir o fim do período → combinação inteira ≤ 14,8 s **e** R1–R4 ≤ 11 s. Evidência = journal/comentário nesse serviço. CI/laptop **não** são esta barra. 4h usa o mesmo caminho, sem barra própria.

Rejeitado: wall-clock nos testes automáticos.

### 4. Só velocidade — mesmas expressões, mesma `talib.*`

Indicadores continuam a sair de `ComboStrategy.calculate_indicators` via as mesmas chamadas `talib.*` (mesma função, mesmos argumentos) sobre as mesmas séries. A cache guarda a saída, não reimplementa EMA/SMA/RSI/MACD/BBANDS/ATR/ADX/ROC. Loop de posição, sim 15m e `fast_1d` reescritos com a **mesma ordem de operações float**, não com fórmulas «equivalentes». Onde a métrica hoje é loop/pandas, manter a chamada — numpy pairwise `sum`/`mean`/`std` pode diferir no último bit.

Rejeitado: `allclose`, `rtol`, arredondar, numpy «equivalente» de indicador, vectorizar métricas.

### 5. Quatro alavancas no caminho comum

1. **Cache por processo worker** de indicadores + máscaras de entrada/saída. Chave = indicadores **já resolvidos** pelas 4 regras de override de `_run_backtest_logic` (tipo/alias/params finais) + `entry_logic` + `exit_logic` + `derived_features` + **identidade da janela** (primeiro/último timestamp, `len`, hash de `open/high/low/close/volume`). `stop_loss` **fora** da chave (entra no loop de posição; reusar a série de sinais entre stops **não** é equivalente). Saída imutável (arrays só-leitura ou `copy()`); nenhum trial escreve no objecto cacheado. Mesma coerção `pd.to_numeric(errors="coerce")` → `float64`/`NaN`.
2. **Loop de posição orientado a eventos** (numpy) com as mesmas comparações: `(low - entry)/entry <= -stop`, entrada no open do candle seguinte, `i > 0`, prioridade stop > exit logic, `continue` após saída. Short: stop **não** entra no loop diário (fica no extractor com `high`); golden cobre short explicitamente.
3. **Sim 15m em numpy:** `asi8`/`searchsorted` numpy, sem `iterrows`, sem `df.copy()` por trial, timestamps ISO pré-calculados 1× por worker; coverage guard 1× por worker no mesmo `df`/`df_15m` do batch. Fallback `fast_1d` (`extract_trades_from_signals`) recebe o mesmo tratamento numpy, semântica idêntica.
4. **R2–R4 com os 3 workers ocupados:** submeter ao pool os batches dos 10 branches da ronda em conjunto (ou batch menor que 200), sem alterar a selecção por ronda. Continua `OUTBOX_MAX_PER_SWEEP=1`.

Prova de viabilidade (15/set, fora do repo): 0 divergências em 600 trials / 15 269 trades; trial 12,2 → ~1,5 ms com timestamps pré-calculados. Estimativa combinação ≈ 15 s **só fecha** 14,8 s com alavanca 4 **e** corte do setup; sem elas fica ~60 s.

### 6. Setup fixo cortado só com velas já no disco

Os ~4 s (tail 15m/1d à exchange, `check_intraday_availability`, spawn do pool, load 15m) entram no relógio dos 14,8 s. Cortar **quando** 1d e 15m **daquele par** já estão no disco e cobrem o fim do período (meio da varredura, depois da primeira combinação daquele par). Par frio pode exceder 14,8 s; não falha o card. Sem mexer no preflight do sweep. Sem reduzir pickle (`df` já vai 1× por batch).

### 7. Ordem determinística antes do score

Hoje `results.extend` segue `as_completed`; o sort por score é estável, logo empates exactos seguem a ordem de chegada (45% dos tripletos do exemplo têm ≥ 1 empate exacto de (sharpe, return) entre stops). Ordenar por índice de batch/trial ou tie-break por params **antes** do score. Pré-requisito do golden do vencedor. Dois runs da mesma combinação no mesmo parquet escolhem o mesmo vencedor em empate.

### 8. Oráculo, fixtures e pin — andar A primeiro

Cópia literal do caminho actual (`calculate_indicators`, `_evaluate_logic_vectorized`, loop de `generate_signals`, `simulate_execution_with_15m`, `extract_trades_from_signals`, `_metrics_from_trades`) em `backend/tests/oracles/card_945_legacy.py`, só teste. Parquet congelado (≥ 2 símbolos, 1d + 15m) + `sha256` por coluna / lista de trades, gerados **antes** de qualquer mudança de produto, primeiro commit da branch. Regenerar fixture só com justificativa escrita no PR; diff de fixture = bloqueio de review. Pin de `TA-Lib`, `numpy` e `pandas` no lock na versão do VPS; o relatório de golden regista essas versões.

Goldens em camadas, exactos: indicadores (3 janelas, 14 templates, ≥ 50 params R1, `assert_array_equal`, mesmo dtype/ordem, sha256) → máscaras → cache fria/quente + A→B→A + sem hit cruzado entre janelas → trial (14 × long/short × ≥ 50, incl. stops extremos e `fast_1d`) → vencedor/holdout/GO/NO-GO da representativa.

### 9. Revert git (andares A/B) + kill-switch até Homologado

1. Arranque do Apply: comentar `baseline-945=<sha de origin/develop>`. Chão: revert volta a esse SHA ou a um commit deste card; nunca histórico reescrito.
2. Andar A = só oráculo + fixtures + testes verdes contra o código actual (produto intacto). Andar B = só velocidade em `combo_optimizer.py` / `combo_strategy.py` / `deep_backtest.py`. Sem squash A com B. `git revert` de B restaura o runner e **mantém** o golden.
3. Após merge em `develop`: emergência = `git revert -m 1 <merge-sha>` (commit novo). Sem `reset --hard`, sem `--force` / `--force-with-lease`.
4. Até Homologado: funções lentas ficam no produto como `_legacy_*`. `COMBO_OPTIMIZER_LEGACY=1` nos serviços que correm o motor (varredura, laboratório, lote, revalidação / regenerar favorito) volta aos números actuais sem merge. Default sem a flag = caminho rápido. Flag sai noutro card depois de Homologado. Git revert continua a ser o rollback permanente.

Revert de código **não** apaga `result_id` já persistidos. Operador relança o sweep se o rápido tiver corrido com bug. Política de invalidar resultados = fora deste card.

## Risks / Trade-offs

- [Risco] 14,8 s não fecha sem alavanca 4 + corte de setup (estimativa ≈ 15 s; sem elas ~60 s) → Mitigação: as duas alavancas são aceite, não opcionais; par frio pode exceder; evidência só no serviço DEV.
- [Risco] Igualdade quebra sem tocar em fórmula: chave sem janela (treino vs holdout+burn-in vs final); chave por params crus; objecto cacheado mutado (`df["signal"] = …`); dtype `object`; drift de TA-Lib/numpy/pandas → Mitigação: cada um tem teste no CA; pin no lock; saída imutável; chave com indicadores resolvidos + janela.
- [Risco] Trades iguais na prova de 15/set não provam indicadores bit a bit → Mitigação: golden de indicadores por coluna vem primeiro, exacto, 3 janelas.
- [Risco] Vectorizar métricas muda o último bit (pairwise sum) → Mitigação: não vectorizar `_metrics_from_trades` / `_calculate_heavy_metrics`; mesma chamada.
- [Risco] Reusar sinais entre stops (stop entra no loop diário em todo template) → Mitigação: `stop_loss` fora da chave; reuso só de indicadores e máscaras.
- [Risco] Short: stop no extractor com `high`, não no loop diário; varredura trata template sem direção como só-long → Mitigação: golden de short cobre o motor (laboratório pode pedir short).
- [Risco] Templates de grid pequeno (ex. `bollinger_rsi_adx` ~1 440 trials) ganham pouco na cache → aceite: 10× é prova no representativo; código comum.
- [Risco] Revert git não desfaz leaderboard já gravado → aceite; relançar sweep; invalidação = outro card.
- [Risco] Kill-switch só no worker da Descoberta deixa laboratório/lote/revalidação no rápido → Mitigação: a flag cobre **todas** as telas do motor.
- [P3 Apply] Função exacta da chave/hash da janela; API de submit R2–R4 ao pool; layout dos parquet/sha256; versões pinadas via `pip freeze` no VPS; wiring da env var por serviço; como saltar o tail check sem tocar no preflight.

## Migration Plan

- Apply só com `Status=Pronto para Dev` (T7 Alan). Este Design não implementa.
- Comentário `baseline-945=<sha>` no arranque do Apply.
- Commit A: oráculo + fixtures + testes verdes contra HEAD. Commit B+: velocidade; não toca oráculo nem fixtures.
- Default = caminho rápido. `COMBO_OPTIMIZER_LEGACY=1` até Homologado. Depois da homologação, a flag sai noutro card.
- Rollback: (1) flag, minutos, sem merge; (2) `git revert` de B; (3) após merge, `git revert -m 1`. Sem force-push.
- Sem schema. Sem deploy PROD neste card. Sem reexecutar as 697 combinações como gate.

## Open Questions

Nenhuma. Caminho comum, outras telas, prova de relógio só em DEV, só velocidade, revert A/B e kill-switch até Homologado estão fechados no issue.

## Prototype

N/A — card sem tela: acelera o motor de otimizar (varredura + laboratório + lote + revalidação). Zero copy, layout, rotas, first-paint. Sem HTML. MUST NOT criar `frontend/public/prototypes/card-945-discovery-combo-10x/`. MUST NOT pipeline Impeccable visual. Nunca emprestar `/combo/discovery`, `/combo/select`, `/monitor`, `/favorites`, `landing`.

## Impeccable

N/A — `UI impact: none`; não há superfície visual nem pipeline context → shape → prototype → critique → browser-gate. Gates de Design e aprovação humana permanecem.

## Apply contract

- Andar A (1º commit): `backend/tests/oracles/card_945_legacy.py`; parquet + sha256 versionados; testes de golden verdes **contra o código actual**. Produto intocado.
- Andar B: `combo_optimizer.py`, `combo_strategy.py`, `deep_backtest.py` — cache+janela, loop eventos, sim 15m numpy, `fast_1d` numpy, R2–R4 no pool, ordem determinística, corte de setup com velas no disco, `_legacy_*` + `COMBO_OPTIMIZER_LEGACY`.
- Pin `TA-Lib` / `numpy` / `pandas` no lock. Relatório de golden cita as versões.
- Callers (varredura, laboratório, lote, revalidação / regenerar favorito) sem ramo lento paralelo; a flag cobre todos.
- Testes automáticos: igualdade exacta. Relógio 14,8 s / R1–R4 ≤ 11 s = evidência no serviço DEV (comentário/journal), não assert de wall-clock.
- Review: listar cada função reescrita ao lado da original; recusar diff de fórmula `talib.*` / PnL / fee / stop / score / métricas; recusar diff de fixture sem justificativa; log com A e B; `baseline-945` no card.
- MUST NOT: frontend/src, rotas, copy, proto HTML, preflight/ranking/promoção, `OUTBOX_MAX_PER_SWEEP` ≠ 1, dual-write Hermes/`~/.codex`.
- P3 aceito (Apply): hash da janela; submit R2–R4; paths de fixture; pin strings; env var por serviço; skip de tail check.
- A secção de crítica fica para o pai depois do crítico.

## Design Critique

- **P0:** nenhum
- **P1:** nenhum
- **P2:** nenhum
- **P3** hash exacto da janela / chave da cache (ts, `len`, OHLCV) — aceite, detalhe de Apply
- **P3** API de submit R2–R4 ao pool (batches da ronda em conjunto vs batch < 200) — aceite, detalhe de Apply
- **P3** layout e paths dos parquet + sha256 versionados — aceite, detalhe de Apply
- **P3** strings de pin `TA-Lib` / `numpy` / `pandas` via `pip freeze` no VPS — aceite, detalhe de Apply
- **P3** wiring de `COMBO_OPTIMIZER_LEGACY` por serviço do motor — aceite, detalhe de Apply
- **P3** como saltar o tail check com velas no disco sem tocar no preflight — aceite, detalhe de Apply
- **P3** nomes internos de função / path (`_legacy_*`, `run_combination`, ficheiros do andar B) — aceite, detalhe de Apply

Pendências não bloqueantes: as P3 acima. Sem P0/P1 de produto/escopo/contrato visível. OpenSpec sintetiza o issue grelhado (`grill-card fronteira vazia`): caminho comum (não atalho de médias); laboratório / lote / revalidação no mesmo caminho rápido; 14,8 s só no serviço DEV da Descoberta (testes = igualdade, não relógio); só velocidade / golden exacto / andar A antes de B / revert git + kill-switch em todas as telas do motor. Qs de operador fechadas; não reabertas.

- Prototype: N/A — motor sem tela; zero copy/layout/rotas; sem HTML em `frontend/public/prototypes/card-945-discovery-combo-10x/`
- Snapshot: N/A justificado (sem superfície visual)
- Tokens: `UI impact: none` / `live_route: N/A` / `surface: new`

Design Agent verdict: PASS
