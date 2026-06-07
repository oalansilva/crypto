## 1. Governança e Preflight

- [x] 1.1 Ler `AGENTS.md`, `rules.md`, `alan-workflow`, `github-project-board` e `crypto-btc-favorite-search`.
- [x] 1.2 Criar issue/card #262, adicionar ao Project 1 e definir `Status=In Progress` antes da execução técnica.
- [x] 1.3 Criar branch/worktree limpa a partir de `origin/develop`.
- [x] 1.4 Publicar artefatos OpenSpec no card #262 antes de snapshot/backtest.

## 2. Snapshot T0 e Benchmarks

- [x] 2.1 Carregar ambiente DEV/PostgreSQL e confirmar endpoints/API/runtime necessários.
- [x] 2.2 Gerar snapshot T0 versionável com Favorites, templates, public mappings, Pine scripts e período completo.
- [x] 2.3 Revalidar todos os Favorites BTC/USDT 1d Long com Deep Backtest, capital 100 USD, 100% in/out, sem parcial e sem pyramiding.
- [x] 2.4 Definir e registrar BENCHMARK_RETURN, BENCHMARK_DD, BENCHMARK_SHARPE, BENCHMARK_PF e PARETO inicial.

## 3. Busca Sequencial

- [x] 3.1 Executar ciclos adaptativos para WINNER_1 com candidatos deep finais, stress tests e anti-duplicata.
- [x] 3.2 Validar contrato público, salvar WINNER_1, confirmar API/trades/tela e recalibrar benchmarks.
- [x] 3.3 Executar ciclos adaptativos para WINNER_2 contra T0, Pareto e WINNER_1.
- [x] 3.4 Validar contrato público, salvar WINNER_2, confirmar API/trades/tela e recalibrar benchmarks.
- [x] 3.5 Executar ciclos adaptativos para WINNER_3 contra T0, Pareto e WINNER_1-2.
- [x] 3.6 Validar contrato público, salvar WINNER_3, confirmar API/trades/tela e recalibrar benchmarks.
- [x] 3.7 Executar ciclos adaptativos para WINNER_4 contra T0, Pareto e WINNER_1-3.
- [x] 3.8 Validar contrato público, salvar WINNER_4, confirmar API/trades/tela e recalibrar benchmarks.
- [x] 3.9 Executar ciclos adaptativos para WINNER_5 contra T0, Pareto e WINNER_1-4.
- [x] 3.10 Validar contrato público, salvar WINNER_5, confirmar API/trades/tela e recalibrar benchmarks.

## 4. Artefatos, Validação e Fechamento Técnico

- [x] 4.1 Gerar Pine Script versionável para cada winner validada.
- [x] 4.2 Corrigir e validar qualquer bug/mapeamento público necessário pelo fluxo versionável do projeto.
- [x] 4.3 Executar testes focados, `openspec validate` da change e validações API/UI/runtime aplicáveis.
- [x] 4.4 Comentar no card relatório completo com T0, benchmarks, ranking, winners ou bloqueio.
- [x] 4.5 Mover card para `Code Review`, executar review Codex do diff exato e corrigir/classificar achados.
- [ ] 4.6 Commitar e integrar em `develop`, executar `./restart`, revalidar DEV e mover card para `Done` técnico quando aplicável.

Nota: usar skills do projeto quando aplicáveis; `openspec-apply-change` e `openspec-verify-change` permanecem obrigatórias para implementação/verificação.
