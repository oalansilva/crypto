## Context

Card **#935**, Status=Design. Rework único do teto com-tela (autor + dupla + 1 rework). Assessment A e Assessment B já PASSARAM no rascunho de duas telas (Favoritos + `/combo/results`): zero P0/P1; proto mostrava +98.591,56% nas duas pontas; +35% não regridia. P3 aceites da dupla (side-tab, truncagem, 32 vs 33, formatador Apply, ETH Analisar inerte no extra). **Este rework não os reabre.**

**P0 novo (Alan, Design, 2026-09-14):** «confira tambem na opção ver trades da tela /monitor» → «a informaçao dos tres lugares deve ser a mesma» → «e correta». Isto fura o «Não entra: Monitor» da grelha original. Escopo de produto: terceira superfície `/monitor` → botão **Ver Trades** (modal ChartModal `viewMode='trades'` → `StrategyTradesTable` cartão «Retorno total»). Os **três** sítios da **mesma** linha já preenchida mostram o **mesmo** percentual composto canónico **e correto** (número grande, não o ~100× menor). Classificação: P0 de produto/escopo/contrato visível (escopo furado + número errado na terceira tela). Não é P3 de Apply. Issue #935 actualizada (Entra inclui Monitor Ver Trades; Não entra: Telegram / Calmar / redesign do Monitor). Sem re-entrevista.

Incidente PROD 2026-09-13: SOL/USDT 1d «Médias Móveis: Tendência Confirmada»: grade RETURN **+98.591,56%** (32 trades, win 68,75%, Max DD 14,15%, Sharpe 0,45); resumo da análise «Retorno total» **985,85%**; Monitor Ver Trades cartão «Retorno total» o mesmo número encolhido (vivo: `StrategyTradesTable` L193 `(displayMetrics.total_return * 100).toFixed(2)%` sobre `GET /favorites/{id}/trades` `payload.metrics`). Sharpe / acerto / drawdown / n do resumo já batem; só o retorno muda ~100×.

Causa visível: o motor grava razão decimal (0,35 = +35%; 985,91 = +98.591%) e pontos percentuais (98591,56). A grade lê os pontos e mostra o composto grande. Combo `formatMetricPercentage` e Monitor `total_return * 100` tratam `|valor| > 1` / razão como se precisassem de outro ×100 — isso acerta acerto/drawdown (ficam < 1 em razão) e **quebra** retorno composto > 100%. 985,85 × 100 = 98.585 vs 98.591,56: residual de arredondamento a 2 casas do número já encolhido, não outra métrica.

Canónico já fechado (#193 / #897): composto **grande**. 169,51 / 16951 → **+16.951%** (dezesseis mil), não 169,51%.

**Usuário:** administrador que compara o catálogo de Favoritos, a análise da mesma linha e o Ver Trades dessa linha no Monitor.
**Hipótese:** se os três sítios repetem o composto grande, o operador não promove, descarta nem lê o Monitor por um número encolhido.
**Resultado:** RETURN da grade, «Retorno total» do resumo e «Retorno total» de Ver Trades são o mesmo composto canónico; compostos < 100% não regressam; Sharpe/acerto/DD/n intocados; tabela de sinais do Monitor não é redesenhada.

**Impeccable recorte (Operate):** audience = admin na grade `/favorites`, na análise aberta pelo gráfico e no modal Ver Trades de `/monitor`; outcome = ler o mesmo composto grande nas três pontas; direction = clone da página viva + delta do número / modal, sem redesign; scope = `/favorites` canónico, `/combo/results` extra, `/monitor` extra (só Ver Trades).

UI impact: affected
live_route: /favorites
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

Regiões clonadas: shell autenticado + workbench `/favorites` (`table.fav-strategies`, «Estratégias favoritas», «Symbol», «Estratégia», «Ações») no **index.html**. Extra 1: `/combo/results` em `analise.html` (`.combo-page`, «Lista de operações», «Análise da estratégia»). Extra 2 (rework): `/monitor` em `monitor.html` (`table.signals`, Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia) + delta Ver Trades / Retorno total. `COPIED:start`/`COPIED:end` nas regiões clonadas. Nunca um painel das N no index. Nunca ANTES/DEPOIS como URL canónica.

## Goals / Non-Goals

**Goals:**

- Na mesma linha já preenchida, RETURN de Favoritos, «Retorno total» do resumo (incluindo «Voltar aos favoritos») e «Retorno total» de Ver Trades no Monitor são o **mesmo** percentual composto canónico — o número grande, não o ~100× menor.
- Incidente SOL: **+98.591,56%** nas três pontas, não 985,85%.
- Contrato #193 / #897: 169,51 / 16951 leem-se **+16.951%** nas três pontas, não 169,51%.
- Vale para retorno já visível, qualquer origem (combo salvo ou Descoberta).
- Compostos < 100% (ex. +35%) continuam a bater nos três sítios; não 0,35% nem 3.500%.
- Sharpe, acerto, Max DD e n do resumo continuam a bater com a grade. No Ver Trades, acerto e n batem com a grade.
- Monitor entra só no Ver Trades / Retorno total; Status, Preço, Distância, tags e Operar ficam como no vivo.

**Non-Goals:**

- Ausência de métricas na promoção da Descoberta (#897 OPEN).
- 32 vs 33 negócios (resumo/grade vs lista do gráfico / velas atuais).
- Holdout / «Treino vs Holdout».
- Telegram, Calmar / ranking da Descoberta (#896).
- Redesign do Monitor (Status, Preço, Distância, tags, Operar).
- Redesign da grade, colunas novas, export Excel, copy de milhar vs `toFixed`.
- Mudar qual número é o canónico (já decidido: composto grande).
- Recalcular varreduras, universo ou split.

## Decisions

1. **Canónico = composto grande, nos três sítios.**
   A grade já está certa neste incidente. O resumo e o Ver Trades alinham-se a ela. Alternativa «o 985,85% é o real» rejeitada: contrato #193 / #897 já fechou +16.951% (dezesseis mil). Alternativa «Monitor pode ficar diferente» rejeitada pelo P0 de Alan (2026-09-14): a informação dos três lugares deve ser a mesma e correta.

2. **A heurística `|valor| > 1 ⇒ já é %` não se aplica ao retorno composto.**
   Continua válida para acerto e drawdown (razões < 1). No retorno, razão 985,91 e pontos 98591,56 são o mesmo composto grande. `StrategyTradesTable` não pode sempre fazer `total_return * 100`. Alternativa «multiplicar sempre ×100» rejeitada: quebraria +35% → 3.500%. Alternativa «nunca ×100» rejeitada: quebraria 0,35 → 0,35% em vez de +35%.

3. **Uma origem, um formatador, três ecrãs.**
   Combo-saved e Descoberta com número já visível entram. Partilhar ou não o helper com combo ainda não salvo / coluna de treino é P3 de Apply, desde que o incidente passe nas três pontas. Alternativa «só Descoberta» rejeitada: o incidente é combo/favorito preenchido. Alternativa «só Favoritos + análise» rejeitada pelo P0 do Monitor.

4. **32 vs 33, holdout e redesign do Monitor ficam fora.**
   O aceite é RETURN da grade vs «Retorno total» do resumo vs «Retorno total» de Ver Trades da **mesma** linha. A lista do gráfico pode continuar com 33 negócios nas velas atuais. A tabela de sinais não muda de colunas.

## Risks / Trade-offs

- [Risco] Corrigir o formatador do resumo ou do Ver Trades reabre acerto/DD → Mitigação: não alterar esses campos; a heurística `|v|>1` permanece só para razões < 1 (win/DD). Teste do incidente: acerto 68,75% e Max DD 14,15% continuam iguais à grade; n=32 no Ver Trades.
- [Risco] Compostos < 100% regressam (0,35% ou 3.500%) → Mitigação: cenário +35% no spec e linha ETH no proto (grade + Ver Trades); Apply não usa um único ramo `abs>1`.
- [Risco] Copy de milhar (`98.591` vs `98591.56` `toFixed`) vira P0 de redesign → Mitigação: fora. Igualdade é o composto grande (ex. contém 98591 ou 98.591), não o glifo do milhar.
- [Risco] #897 OPEN (métrica ausente) funde-se com este card → Mitigação: aceite explícito «não preencher o vazio».
- [Risco] Apply redesenha o Monitor ao tocar em Ver Trades → Mitigação: spec `monitor` limita o delta ao cartão «Retorno total»; Status/Preço/Distância/tags/Operar intocados.

## Migration Plan

Sem migração de schema. Rollback = reverter os formatadores do resumo e do `StrategyTradesTable`. Nenhum backfill: os números já estão persistidos; só a unidade visível do resumo e do Ver Trades muda.

## Apply contract

Apply lê este `design.md` e o HTML em `frontend/public/prototypes/card-935-favorites-combo-return/` como spec de layout. Sem HTML neste arquivo. Sem editar produto neste filho de Design.

**Contrato visível (não P3):**

- Grade `/favorites` incidente: RETURN **+98.591,56%**, Sharpe 0,45, 32 trades, win 68,75%, Max DD 14,15%. Estratégia «Médias Móveis: Tendência Confirmada», SOL/USDT 1d.
- Resumo `/combo/results` da mesma linha: «Retorno total» o mesmo composto (~+98.591%), **não** ~985,85%. Acerto / Max DD / 32 ops iguais à grade.
- Monitor `/monitor` Ver Trades da mesma linha: cartão «Retorno total» o mesmo composto (~+98.591%), **não** ~985,85%. Acerto 68,75% e n=32 iguais à grade.
- Contrato 169,51 / 16951 → +16.951% nas três pontas.
- Linha +35%: resumo e Ver Trades ~+35%.
- «Voltar aos favoritos»: grade segue com o composto grande.

**Bug vivo (contrato no Design; correção no Apply, não neste filho):**

- Favoritos `formatSignedPct(total_return_pct ?? total_return)` — já mostra o grande (certo).
- Combo `formatMetricPercentage` em `total_return` decimal ~985,85 → imprime 985,85% (errado).
- Monitor `StrategyTradesTable` L193: sempre `(displayMetrics.total_return * 100).toFixed(2)%`. `GET /favorites/{id}/trades` passa `payload.metrics`. Apply alinha unidades.

**P3 — detalhe de Apply (aceito aqui, não reabrir como P0/P1):**

- Helper único vs dois/três formatadores (`formatSignedPct` da grade vs `formatMetricPercentage` do resumo vs `total_return * 100` do Ver Trades) desde que o incidente passe nas três pontas.
- Distinguir `total_return` (razão) de `total_return_pct` (pontos) sem mudar nomes de API.
- Combo ainda não salvo / coluna de treino: partilhar o formatador é mecanismo.
- Copy de milhar vs `toFixed` (98.591 vs 98591.56).
- 32 vs 33 na lista do gráfico: não «corrigir».
- Testids da linha SOL, do `data-metric="return"` do resumo e do cartão Ver Trades.
- Detector `side-tab` ×2 (`border-left` 3px nos cards mobile de tier) — incumbente do clone #897 / vivo.
- Truncagem desktop de «Médias Móveis: Tendência Confirmada» na coluna Estratégia (table-layout fixed vivo).
- ETH «Analisar» inerte no extra da análise (P3 da dupla; o +35% está na grade e no Ver Trades ETH).
- Par 169,51 / +16.951% só no spec (o incidente +98.591 demonstra a mesma unidade).
- Mock sem loading/vazio/erro.
- Alvos 32px nos ícones da linha da grade.

## Prototype

- Canónico: `https://dev.criptofarol.com.br/prototypes/card-935-favorites-combo-return/` → `frontend/public/prototypes/card-935-favorites-combo-return/index.html`. Clone da página viva `/favorites` + delta deste card (linha SOL com RETURN canónico grande; linha ETH +35% sem regressão). Landmarks: `table.fav-strategies`, «Estratégias favoritas», «Symbol», «Estratégia», «Ações». `COPIED:start`/`COPIED:end` no clone.
- Extra análise: `https://dev.criptofarol.com.br/prototypes/card-935-favorites-combo-return/analise.html` — clone de `/combo/results` com «Retorno total» = o mesmo composto grande; acerto/DD/32 ops iguais à grade.
- Extra monitor (rework): `https://dev.criptofarol.com.br/prototypes/card-935-favorites-combo-return/monitor.html` — clone de `/monitor` (fonte proto #921, landmarks `table.signals` + Status/Preço/Distância/7d/Risco até stop/Tags/Operar/Par / Estratégia) + delta Ver Trades da linha SOL: cartão «Retorno total» = +98.591,56%; acerto 68,75% e n=32. Linha ETH Ver Trades = +35,00% (sem regressão). Não redesenha a tabela de sinais.
- `cp`/clone = copied; delta do número / modal Ver Trades = generated.
- Sem painel ANTES/DEPOIS como URL canónica.

## Prototype Validation

- **Comando:** `xvfb-run -a python3` + Playwright Chromium headed (`executable_path=/usr/bin/chromium-browser`, `--no-sandbox`). Não `curl` (curl só para digest HTTPS==disco). Evidência: `.impeccable/critique/935-rework-gate.json`.
- **URLs:** canónico `https://dev.criptofarol.com.br/prototypes/card-935-favorites-combo-return/` (`index.html`); extra `…/analise.html`; extra `…/monitor.html`. Disco == HTTPS (sha256 abaixo).
- **Viewports:** desktop 1280×800 + mobile 390×844, `colorScheme: dark`. Screenshots rework: `935-rework-index-desktop-1280x800.png`, `935-rework-index-mobile-390x844.png`, `935-rework-analise-desktop-1280x800.png`, `935-rework-analise-mobile-390x844.png`, `935-rework-monitor-desktop-1280x800.png`, `935-rework-monitor-mobile-390x844.png`, `935-rework-monitor-table-desktop-1280x800.png`, `935-rework-monitor-table-mobile-390x844.png`.
- **Ações / asserts (index):** landmarks `table.fav-strategies`, «Estratégias favoritas», «Symbol», «Estratégia», «Ações»; linha SOL RETURN **+98.591,56%** (não 985,85); Sharpe 0,45 · 32 · 68,75% · Max DD 14,15%; linha ETH **+35,00%** (não 0,35% nem 3.500%).
- **Ações / asserts (analise):** «Retorno total» **+98.591,56%**; acerto 68,75% · Max DD 14,15% · 32 ops; `.combo-page`, «Análise da estratégia», «Lista de operações».
- **Ações / asserts (monitor):** landmarks `/monitor`; clique **Ver Trades** SOL: «Retorno total» **+98.591,56%**; acerto 68,75% · n=32; Ver Trades ETH **+35,00%**; zero `985,85` visível.
- **Console:** 0 errors.
- **Resultado:** **83/83 PASS** · FAIL 0. Clone gate `classify(/favorites)=PASS` no index; `classify(/combo/results)=PASS` em analise; `classify(/monitor)=PASS` em monitor.
- **Digest (UTF-8 sha256, pós-rework = gate):**
  - `index.html` `a9535af5af197d4228a225d1ee1854215953c4cbd5339d4758c48708e314a6ae` · 42109 B = 7681 copied + 34428 generated (nav Monitor → `monitor.html`).
  - `analise.html` `6a56f2dfef63f4809d4afa63c9a0a16b794b7c760cd4a844e6c4616b5e8403fd` · 26823 B = 4992 copied + 21831 generated.
  - `monitor.html` `fe217e1465874d2c3c95e0a66596668abf7203165a6f4ae5b374608f71f9bc9f` · 22816 B = 3369 copied (shell + thead/BTC) + 19447 generated (SOL/ETH Ver Trades + modal).

## Open Questions

Nenhuma. Fronteira veio grelhada do issue #935 e fechada em Design (2026-09-14) com o P0 do Monitor. Canónico e recorte vs #897 / 32 vs 33 / redesign do Monitor já fechados.

## Design Critique

Com-tela. Teto 1+1+1: autor + dupla A/B + 1 rework (P0 novo de produto: Monitor Ver Trades; três sítios = composto canónico correto). Sem segunda dupla. Sem segundo rework.

- Autor: [design-autor 935](317fe663-9f68-4aa7-b340-c8ede13da947) isolado; `model: cursor-grok-4.6-high`.
- Assessment A: [Assessment A 935](18e4a12f-752c-4642-b7f2-481493e82751) isolado; `model: cursor-grok-4.6-high`. **PASS** (duas pontas).
- Assessment B: [Assessment B 935](5b5d789a-c39b-467f-bed2-a35fd27f881a) isolado; `model: cursor-grok-4.6-high`. **PASS** (duas pontas).
- Rework: [design-autor 935](ebee5fab-2c5c-41a7-92eb-924494d72ae3) isolado; `model: cursor-grok-4.6-high`. Terceira ponta `/monitor` Ver Trades. Prototype Validation **83/83 PASS**.
- Verdict: **PASS**. Tokens: `UI impact: affected` / `live_route: /favorites` / `surface: existing`.
- Proto: https://dev.criptofarol.com.br/prototypes/card-935-favorites-combo-return/
- Extra análise: https://dev.criptofarol.com.br/prototypes/card-935-favorites-combo-return/analise.html
- Extra monitor: https://dev.criptofarol.com.br/prototypes/card-935-favorites-combo-return/monitor.html
- Snapshot A: `.impeccable/critique/935-card-935-favorites-combo-return-assessment-A.md`
- Snapshot B: `.impeccable/critique/935-card-935-favorites-combo-return-assessment-B.md`
- Snapshot rework: `.impeccable/critique/935-card-935-favorites-combo-return-rework-2026-09-14.md`

- **P0:** nenhum aberto. O P0 de Alan (terceira superfície) está no proto: Ver Trades = composto grande (+98.591,56%), não 985,85%.
- **P1:** nenhum
- **P3** aceito (Apply, não reabrir): detector `side-tab` ×2 nos cards mobile de tier
- **P3** aceito: truncagem desktop de «Médias Móveis: Tendência Confirmada»
- **P3** aceito: lista 33 negócios vs 32 no resumo/grade — fora (#897)
- **P3** aceito: helper `formatMetricPercentage` vs `formatSignedPct` vs `total_return * 100`; copy de milhar vs `toFixed`
- **P3** aceito: ETH Analisar inerte no extra da análise; +35% visível na grade e no Ver Trades ETH
- **P3** aceito: par 169,51 / +16.951% só no spec
- **P3** aceito: mock sem loading/vazio/erro; alvos 32px ícones da grade
- **Disposition:** P3 aceites no Apply.

### Proxies

- `design.md` words: 2348
- HTML generated vs copied: 75706 vs 16042
- Spawns: 5
- `proxy modelo: grill-card → Grok 4.6 (cursor-grok-4.6-high)`
- `proxy modelo: design-autor → Grok 4.6 (cursor-grok-4.6-high)`
- `proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)`
- `proxy modelo: Assessment B → Grok 4.6 (cursor-grok-4.6-high)`

Design Agent verdict: PASS
