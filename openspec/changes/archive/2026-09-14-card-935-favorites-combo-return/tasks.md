# Tasks — card-935-favorites-combo-return

> Execução SOMENTE após `Status=Pronto para Dev` (T8). Este filho de Design NÃO implementa.

## 1. Formatador do resumo e do Ver Trades

- [x] 1.1 — Em `/combo/results`, «Retorno total» da mesma linha já preenchida em Favoritos usa o composto canónico grande (razão 985,91 / pontos 98591,56 → ~+98.591%; 169,51 / 16951 → +16.951%), não o número ~100× menor.
- [x] 1.2 — A heurística `|valor| > 1 ⇒ já é %` NÃO encolhe retorno composto > 100%; acerto e Max DD (razões < 1) continuam iguais à grade.
- [x] 1.3 — Composto < 100% (ex. +35%) continua ~+35% nos três sítios — não 0,35% nem 3.500%.
- [x] 1.4 — Em `/monitor` Ver Trades, `StrategyTradesTable` deixa de imprimir sempre `(displayMetrics.total_return * 100).toFixed(2)%` quando `GET /favorites/{id}/trades` passa `payload.metrics` em unidades mistas; o cartão «Retorno total» alinha-se à grade.

## 2. Paridade visível (três sítios)

- [x] 2.1 — Incidente SOL/USDT 1d «Médias Móveis: Tendência Confirmada»: grade RETURN +98.591,56%, resumo «Retorno total» o mesmo composto, Monitor Ver Trades «Retorno total» o mesmo composto; Sharpe 0,45 / win 68,75% / Max DD 14,15% / 32 ops intocados.
- [x] 2.2 — «Voltar aos favoritos» deixa a grade com o composto grande de antes.
- [x] 2.3 — Qualquer origem (combo salvo ou Descoberta) com retorno já visível: se a unidade quebra, este card; métrica ausente permanece #897.

## 3. UI e evidência

- [x] 3.1 — Grade `/favorites` alinhada ao proto (`index.html`): landmarks intactos; linha SOL com RETURN canónico grande; linha +35% sem regressão.
- [x] 3.2 — Análise alinhada ao proto extra (`analise.html`): «Retorno total» = composto grande; acerto/DD/32 ops iguais à grade.
- [x] 3.3 — Monitor alinhado ao proto extra (`monitor.html`): landmarks `/monitor`; Ver Trades da linha SOL com «Retorno total» = composto grande; acerto e n batem; Status/Preço/Distância/tags/Operar intocados.
- [x] 3.4 — Testes do formatador (grande / <100% / 169,51→+16.951%) e Playwright `/favorites` + `/combo/results` + `/monitor` Ver Trades desktop+mobile contra o proto. Lista 33 negócios fora.
- [x] 3.5 — `openspec verify` desta change.
