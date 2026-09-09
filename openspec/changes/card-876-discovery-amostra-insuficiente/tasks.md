# Tasks — card-876-discovery-amostra-insuficiente

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.

## 1. Persistência e invariante

- [x] 1.1 — Alembic: coluna `discovery_sweeps.insufficient_sample INTEGER NOT NULL DEFAULT 0`; combinação aceita estado `insufficient_sample`; payload de sweep/histórico expõe o quarto contador (leituras antigas = 0).
- [x] 1.2 — Reconcile `_reconcile_locked`: `processed = succeeded + failed + skipped + insufficient_sample`; `failed=0` e `insufficient_sample>0` (mesmo com `succeeded=0`) → `completed`; ramo skipped-only operacional permanece; testes do invariante de 3 termos atualizados.
- [x] 2.1 — Helper: `fetch_ohlcv` no símbolo×timeframe×período do snapshot + `split_train_holdout(..., 0.7)`; corte se listagem vazia/`<2` ou `len(train) < MIN_ELIGIBLE_TRADES`; **antes** de `generate_stages` / `run_optimization`.
- [x] 2.2 — `run_combination`: no corte, persistir `DiscoveryResult` com `eligibility=insufficient_sample`, métricas ranking nulas, combinação `insufficient_sample`; não contar como `succeeded`/`skipped`/`failed`; caminho feliz e `low_sample` pós-grid intactos; «1 por sweep» intacto.
- [x] 3.1 — Decidir lista `insufficient_sample`: rank null, selo `Amostra insuficiente` (não `Baixa amostra`), Calmar/Max DD/Trades `N/A`, **sem** CTA Promover; Excluir permanece; `low_sample` continua com Promover desabilitado.
- [x] 3.2 — Parciais top-5 do Acompanhar excluem `insufficient_sample`.
- [x] 4.1 — Fórmula `N processadas = X sucesso + Y falha + Z ignoradas + W amostra insuficiente` em `data-testid=counter-invariant`; fidelidade ao proto; landmarks e modos #852 sem regressão.
- [x] 5.1 — Testes worker (27 diárias → segundos, sem grid), reconcile (só amostra insuficiente → completed), API/UI da fórmula e da linha Decidir; Playwright `/combo/discovery` desktop+mobile contra o proto.
- [x] 5.2 — `openspec verify` desta change.
