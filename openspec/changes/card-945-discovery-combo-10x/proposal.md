## Why

Quem dispara uma varredura na Descoberta espera dezenas de horas (sweep `3d9bee8b…`: 40,5 h / 697 combinações, ~17/h) porque cada combinação no caminho comum Deep+WF leva ~1–2,5 min (representativa `multi_ma_crossover` × `1INCH/USDT` × `1d` × long = 148 s). O operador precisa do leaderboard no mesmo dia, **sem atalho só para médias móveis** e sem piorar o contrato (Deep 15m + walk-forward 70/30, um orquestrador por sweep).

## What Changes

- Cada combinação da varredura no caminho comum (`run_combination` → `ComboOptimizer.run_optimization`) termina cerca de 10× mais rápido. O ganho vale para **qualquer estratégia que a Descoberta aceita** (catálogo 11+3=14 no export versionado), não um ramo especial de cruzamento de médias.
- Laboratório de combo, gerar em lote, revalidação de favoritos e regenerar favorito usam o **mesmo caminho rápido** neste card. Não fica um atalho só da varredura.
- Prova de relógio: a representativa termina em ≤ 14,8 s **no mesmo serviço da Descoberta em DEV** que mediu os 148 s, com velas já no disco. Testes automáticos = igualdade exacta de números, não wall-clock.
- **Só velocidade:** nenhuma regra nem cálculo muda. Indicadores continuam a sair das mesmas chamadas `talib.*`; cache guarda a saída, não reimplementa indicador. Loop de posição, sim 15m e fallback `fast_1d` mantêm as mesmas expressões.
- Quatro alavancas no caminho comum: cache de indicadores + máscaras por chave (params resolvidos + janela; `stop_loss` fora da chave); loop de posição orientado a eventos; sim 15m em numpy; R2–R4 com os 3 workers ocupados (branches da ronda em conjunto; continua 1 combinação em voo por sweep).
- Corte do setup fixo (~4 s) quando as velas 1d e 15m daquele par já estão no disco e cobrem o fim do período. Primeira combinação de um par frio pode exceder 14,8 s; isso não falha o card.
- Ordem determinística dos resultados antes do score (pré-requisito do golden do vencedor).
- Oráculo congelado + fixtures parquet + goldens exactos (indicadores por coluna, máscaras, trial, vencedor) no **primeiro commit**, contra o código actual, antes de qualquer aceleração.
- Pin de `TA-Lib`, `numpy` e `pandas` no lock na versão em uso no VPS.
- Revert via git: `baseline-945` no comentário; andar A (oráculo/fixtures/testes) e andar B (só velocidade) sem squash entre si; emergência após merge = `git revert -m 1` sem force-push.
- Até Homologado, interruptor `COMBO_OPTIMIZER_LEGACY=1` volta ao caminho lento em **todas** as telas do motor. Default sem a flag = caminho rápido. Flag sai noutro card depois de Homologado.

**Não entra:** otimização só de SMA / cruzamento de médias; deixar laboratório / lote / revalidação no caminho lento; exigir ≤ 14,8 s na máquina dos testes; paralelizar o sweep (>1 combinação em voo); mudar grid, steps, rondas, `top_k`, score, leaderboard, promoção/dedup, elegibilidade; 10× da página Discovery / first-paint / Playwright; reimplementar indicadores; reescrever fórmulas de PnL/fee/stop/score/métricas; tolerâncias (`allclose`) nos goldens; `git reset --hard` / force-push; apagar `_legacy_*` / oráculo neste card; custom/quant fora do catálogo como prova.

## Capabilities

### New Capabilities

- (nenhuma) — o comportamento entra no motor já existente.

### Modified Capabilities

- `combo-optimizer`: caminho comum acelerado para qualquer template do catálogo da Descoberta e para laboratório / lote / revalidação / regenerar favorito; prova de relógio só no serviço DEV da Descoberta; golden exacto (indicadores, máscaras, trial, vencedor); ordem determinística; 1 combinação em voo; kill-switch `COMBO_OPTIMIZER_LEGACY` em todas as telas do motor; revert por andares A/B. Deep 15m + walk-forward 70/30, grid, score, elegibilidade e persistência permanecem.

## Impact

- Backend motor: `combo_optimizer.py`, `combo_strategy.py`, `deep_backtest.py` (andar B). Funções lentas permanecem como `_legacy_*` até Homologado.
- Testes: `backend/tests/oracles/card_945_legacy.py` (cópia literal, só teste); fixtures parquet (≥ 2 símbolos, 1d + 15m) + sha256; goldens exactos. Primeiro commit = só isto, verde contra o código actual.
- Lock do backend: pin de `TA-Lib`, `numpy`, `pandas`.
- Callers já no mesmo motor (varredura, laboratório, lote, revalidação / regenerar favorito) herdam o caminho; o interruptor cobre todos.
- Sem frontend, sem copy, sem layout, sem rotas, sem first-paint. Nunca emprestar `/combo/discovery`, `/combo/select`, `/monitor`, `/favorites`, `landing`. Proto N/A.
- Preflight / create / lease / reconcile / persistência / ranking / promoção inalterados.
- Sem dual-write Hermes/`~/.codex`.
