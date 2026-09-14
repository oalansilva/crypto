## Why

O administrador compara a mesma linha já preenchida em três sítios e lê retornos diferentes (~100×). Não consegue confiar no número para decidir o que entra no Monitor nem para ler o Monitor depois. Incidente PROD 2026-09-13: SOL/USDT 1d «Médias Móveis: Tendência Confirmada» mostra RETURN **+98.591,56%** na grade, «Retorno total» **985,85%** no resumo da análise, e o mesmo número encolhido no cartão «Retorno total» de Ver Trades no Monitor. Canónico já fechado (#193 / #897): o composto **grande**. Decisão de operador em Design (2026-09-14): os três lugares devem ser a mesma informação **e correta**.

## What Changes

- Na mesma linha já preenchida, **três sítios** mostram o **mesmo** percentual composto canónico **e correto** — igualdade no número grande, não no ~100× menor:
  1. coluna RETURN da grade `/favorites`;
  2. «Retorno total» do resumo da análise `/combo/results` (incluindo «Voltar aos favoritos»);
  3. «Retorno total» de **Ver Trades** no Monitor (`/monitor`, ChartModal `viewMode='trades'` → cartão `StrategyTradesTable`).
- Canónico = composto grande já contratado: razão 169,51 / pontos 16951 leem-se **+16.951%** (dezesseis mil), não 169,51%. Neste incidente: **+98.591,56%**, não 985,85%.
- Vale para retorno **já visível**, qualquer origem (combo salvo ou Descoberta). Se o número existe e a unidade quebra, é este card.
- Sharpe, acerto, Max DD e quantidade de negócios do resumo **já batem** com a grade — este card não os altera. No Ver Trades, acerto e n batem com a grade.
- Linhas cujo RETURN já é um composto < 100% (ex. +35%) continuam a bater nos três sítios; não regressam para 0,35% nem para 3.500%.
- Abrir a análise e voltar aos favoritos deixa a grade com o composto grande de antes.
- Monitor entra **só** no Ver Trades / Retorno total da mesma linha; não redesenha Status, Preço, Distância, tags nem Operar.

Fora: ausência de métricas na promoção da Descoberta (#897 OPEN); 32 vs 33 negócios (resumo/grade vs lista do gráfico); holdout / «Treino vs Holdout»; Telegram; Calmar / ranking da Descoberta (#896); redesign do Monitor (Status, Preço, Distância, tags, Operar); redesign da grade, colunas novas, export Excel, copy de milhar vs `toFixed`; mudar qual número é o canónico; recalcular varreduras, universo ou split.

## Capabilities

### New Capabilities

- `favorites-combo-return-parity`: contrato visível de que RETURN da grade `/favorites`, «Retorno total» do resumo em `/combo/results` e «Retorno total» de Ver Trades em `/monitor` da **mesma** linha já preenchida são o mesmo composto canónico grande (incidente SOL +98.591,56%; contrato 169,51 / 16951 → +16.951%); compostos < 100% não regressam nos três sítios; Sharpe/acerto/DD/n intocados.

### Modified Capabilities

- `favorites`: o retorno composto já persistido e mostrado na grade SHALL ser o mesmo percentual canónico no resumo da análise aberta a partir dessa linha; a heurística `|valor| > 1 ⇒ já é %` NÃO pode encolher um composto > 100%.
- `monitor`: Ver Trades da mesma linha já preenchida SHALL mostrar «Retorno total» igual ao composto canónico grande da grade; não redesenha Status, Preço, Distância, tags nem Operar.

## Impact

- Frontend: `/favorites` (grade já mostra o composto grande — não redesenhar); `/combo/results` aberto pelo ícone de gráfico / «Analisar» (formatador do «Retorno total» alinhado ao da grade); `/monitor` botão Ver Trades (ChartModal `viewMode='trades'` → `StrategyTradesTable` deixa de fazer `total_return * 100` cego).
- Sem mudança de API, persistência, varredura, Telegram, Sharpe, acerto, Max DD ou n de negócios do resumo. Sem redesign da tabela de sinais.
- Specs: nova `favorites-combo-return-parity`; delta em `favorites` e `monitor`.
- Protótipo: clone `/favorites` (canónico) + extra `/combo/results` + extra `/monitor` Ver Trades; delta = o mesmo composto grande nas três pontas do incidente.
