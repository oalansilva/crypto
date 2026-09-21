## Context

Card **#994**, Status=Design (Alan devolveu de Aprovação de Design). Captura PROD 2026-09-19: o favorito `Médias Móveis: Tendência em Virada` em BTC/USDT aparece com TF **4h** em `/favorites` e com **1d** ao lado do par em `/monitor`. Filtro só Todos/1d. Abrir gráfico e Ver Trades iniciam em 1d. A ficha já mostra o TF da estratégia e, no mesmo bloco, «Gráfico 1d» e «tf 1d». A coluna 7d desenha em 1d.

**P0 deste rework:** Alan recusou o seletor de timeframe **do gráfico**. O utilizador não deveria selecionar os timeframes do gráfico; o gráfico deveria somente exibir o timeframe da estratégia. Fecha o fork que o issue grelhado deixou em Design («Se, com o gráfico já aberto, o seletor ainda deixar olhar outro TF só para inspecção, isso é Design»).

**Vivo hoje (`MonitorStatusTab.tsx` / `OpportunityCard.tsx` / `ChartModal.tsx`):**
- `resolveChartTimeframe` ignora `opportunity.timeframe` e devolve `'1d'`. Esse valor alimenta `pair-tf`, sparkline e `initialTimeframe` de Abrir gráfico / Ver Trades.
- Filtro `TimeframeFilter = 'all' | '1d'` — opções hardcoded Todos e 1d.
- `OpportunityCard`: `effectiveTimeframe = '1d'`; rótulos «Gráfico {effectiveTimeframe}» e `tf {effectiveTimeframe}`; toggle group só `['1d']`. O TF da estratégia já aparece num `detail-timeframe` à parte.
- `ChartModal` tem toolbar `aria-label="Selecionar timeframe do gráfico"` com `Estratégia (TF)` + 15m/1h/1d e força ação (stock) a 1d. O furo original era o TF **inicial**; este rework **também** tira o seletor quando o gráfico abre a partir do Monitor.
- O sinal, a posição e o stop da lista já são os da estratégia naquele timeframe.

**Impeccable (Operate):** audience = operador que usa Favoritos e Monitor no dia a dia; outcome = ver, filtrar e abrir o gráfico no TF da estratégia (o mesmo da coluna TF dos Favoritos); direction = clone `/monitor` + delta de TF, sem redesign da board; `DESIGN.md` permanece autoridade visual.

Briefing = issue grelhado #994 (Problema, História, Entra, Não entra). Sem reentrevista.

UI impact: affected
live_route: /monitor
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

Regiões clonadas: shell autenticado + workbench `/monitor` (`table.signals`, Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia) no **index.html**. `COPIED:start`/`COPIED:end` nas regiões clonadas. Delta fora desses blocos: TF ao lado do par, filtro da lista com 4h, minigráfico 4h, coluna **Gráfico**, ficha um TF, modal de gráfico aberto em 4h com rótulo só de leitura (sem seletor). Sem extra `/favorites` (copy de Favoritos não muda). Nunca ANTES/DEPOIS como URL canónica.

## Goals / Non-Goals

**Goals:**

- Na lista, o TF ao lado do par é o da estratégia (o mesmo da coluna TF em `/favorites`).
- Ficha (linha e expandida): um só TF, o da estratégia. Sem «Gráfico 1d» nem «tf 1d».
- Filtro de timeframe da **lista** = Todos + os TFs das estratégias crypto visíveis (igual Favoritos). 4h mostra só 4h; 1d mostra só 1d; Todos mostra todas. Este filtro **permanece**; não escolhe o gráfico.
- Minigráfico da lista nas velas do TF da estratégia. Coluna permanece; o rótulo visível passa a **Gráfico**.
- Abrir gráfico e Ver Trades abrem no TF da estratégia e **ficam** nesse TF. O gráfico não oferece seletor: só um rótulo só de leitura do TF da estratégia (chip `4h` ou texto `Estratégia · 4h`). Sem botões 15m / 1h / 1d / «Estratégia (4H)». Sem `role="group"` «Selecionar timeframe do gráfico». Sem JS que troca velas por inspecção.
- Ação (stock) continua só em 1d. Sinal, posição e stop não mudam.

**Non-Goals:**

- Mudar o timeframe gravado no favorito.
- Descoberta, Combo ou backtest.
- Recalcular sinal, stop ou métricas.
- Telegram.
- Gráfico de ação além de 1d.
- Segundo TF de preço na ficha.
- Gravar no Monitor o último TF olhado no gráfico (não há o que olhar noutro TF).
- Seletor de TF no gráfico aberto a partir do Monitor.
- Redesign da board (Status, Preço, Distância, Tags, Operar, Par / Estratégia, KPIs).
- Extra `/favorites` no proto.
- Mudar o default Em portfólio vs Todos.
- Tirar o filtro da lista Todos / 4h / 1d.

## Decisions

1. **TF ao lado do par = `opportunity.timeframe`.**
   O valor visível em `pair-tf` (e no mobile) é o TF da estratégia, o mesmo da coluna TF daquela linha em `/favorites`. Alternativa «manter `resolveChartTimeframe` → 1d» rejeitada: é o incidente. Alternativa «mostrar os dois» rejeitada: Entra pede um só TF.

2. **Filtro da lista = Todos + TFs da lista, como Favoritos.**
   As opções nascem dos timeframes das estratégias crypto visíveis (`uniqueTimeframes` no espírito de `FavoritesDashboard`). Não hardcoded `1d`. Filtrar 4h esconde 1d; filtrar 1d esconde 4h; Todos mostra todas. Default do filtro de lista (Em portfólio) **não** muda. Este controlo **não** escolhe o gráfico: só mostra/esconde linhas pelo TF da estratégia. Alternativa «chips 4h/1d fixos mesmo sem linhas nesses TFs» rejeitada: Favoritos só lista os que existem.

3. **Minigráfico no TF da estratégia; coluna chama-se Gráfico.**
   Sparkline busca velas no TF da linha (4h na linha 4h). O rótulo 7d deixa de aplicar: a janela deixa de ser «7 dias de 1d». Nome visível da coluna = **Gráfico**. A coluna **não** se apaga. Landmark de catálogo `7d` permanece no HTML copiado (comentário COPIED do thead) para o gate HEAD; o th visível é Gráfico. Alternativa «manter 7d no th» rejeitada pelo Entra.

4. **Abrir gráfico / Ver Trades abrem no TF da estratégia e ficam.**
   `initialTimeframe` = TF da estratégia, não 1d fixo. Um BTC 4h abre em velas 4h com rótulo só de leitura `Estratégia · 4h`. A lista continua a mostrar 4h ao lado do par. Não há inspecção noutro TF.

5. **Sem seletor; rótulo só de leitura do TF da estratégia.**
   O gráfico aberto a partir do Monitor (Abrir gráfico / Ver Trades) **não** tem seletor de timeframe. Sem botões 15m / 1h / 1d / «Estratégia (4H)» clicáveis. Sem `role="group"` «Selecionar timeframe do gráfico». Sem JS que troca velas por inspecção. O TF aparece como rótulo só de leitura (chip `4h` ou texto `Estratégia · 4h`). Alternativa «inspecção no seletor não grava» rejeitada por Alan em Aprovação de Design: o utilizador não deveria selecionar os timeframes do gráfico. Alternativa «persistir último TF olhado em `price_timeframe`» rejeitada: Não entra (e não há TF olhado).

6. **Ficha: um só TF.**
   Some o segundo rótulo «Gráfico 1d» / «tf 1d» e o toggle group só-1d. Fica o TF da estratégia (badge `4h` na ficha expandida, `pair-tf` na linha). Alternativa «manter Gráfico 1d como preço de mercado» rejeitada: Não entra.

7. **Ação (stock) só 1d.**
   O vivo já força ação a 1d. Este card não alarga. Crypto 4h não muda o contrato de stock. Ação (stock) continua só 1d, fora desta cena crypto.

8. **Uma URL canónica mostra lista e gráfico.**
   Abrir gráfico é modal da mesma `/monitor`. O `index.html` traz o delta da lista (BTC 4h, filtro da lista com 4h, minigráfico 4h, ficha sem segundo TF) **e** o gráfico aberto em 4h com rótulo só de leitura, abaixo da lista no mesmo URL (para os dois deltas serem visíveis). O Apply mantém o `ChartModal` overlay incumbente e esconde/remove a toolbar de seletor nesse contexto. Sem extra `/favorites`. Sem painel ANTES/DEPOIS.

## Risks / Trade-offs

- [Risco] Apply muda só o filtro e esquece `resolveChartTimeframe` → par continua 1d. Mitigação: tasks 1–4 amarram lista, spark, abrir gráfico e ficha ao mesmo TF.
- [Risco] Apply deixa a toolbar viva `Selecionar timeframe do gráfico` no `ChartModal` aberto do Monitor. Mitigação: decisão 5; task 4.2; proto sem seletor.
- [Risco] Coluna 7d some e o gate HEAD falha. Mitigação: coluna permanece; th visível = Gráfico; texto `7d` no COPIED do thead.
- [Risco] Extra `/favorites` nasce por analogia. Mitigação: proibido; Favoritos não muda.
- [Risco] Spark 4h com o mesmo `SPARKLINE_LIMIT` (14) parece «menos dias». Mitigação: P3 Apply; o contrato visível é velas 4h, não 1d.
- [Risco] Proto dockado vs overlay vivo confunde o crítico. Mitigação: decisão 8; overlay vivo é P3 de Apply.
- [Risco] Apply tira também o filtro da lista ao tirar o seletor do gráfico. Mitigação: são dois controlos distintos; o filtro `#tf-filter` Todos/4h/1d permanece.

## Migration Plan

Sem migração de schema. Rollback = reverter `resolveChartTimeframe`, o filtro hardcoded, os rótulos da ficha e a toolbar do `ChartModal` no contexto Monitor. Favoritos gravados não se apagam. Preferências `price_timeframe=1d` existentes deixam de ter superfície na ficha.

## Apply contract

Apply lê este `design.md` e o HTML em `frontend/public/prototypes/card-994-monitor-multiplos-timeframes/` como spec de layout. Sem HTML neste arquivo. Sem editar produto neste filho de Design.

**Contrato visível (não P3):**

- `/monitor` (`index.html`): BTC/USDT `Médias Móveis: Tendência em Virada` com **4h** ao lado do par; filtro Timeframe da **lista**: Todos + **4h** + 1d; minigráfico da linha 4h em velas 4h; coluna **Gráfico** (não apagada); ficha expandida com um só TF (4h) e **ausente** «Gráfico 1d» / «tf 1d»; gráfico aberto em 4h com rótulo só de leitura (`Estratégia · 4h` / chip `4h`); **ausente** seletor de TF do gráfico (sem botões 15m / 1h / 1d / «Estratégia (4H)»; sem `role="group"` «Selecionar timeframe do gráfico»; sem `data-chart-tf`); landmarks `table.signals` + Status / Preço / Distância / Tags / Operar / Par / Estratégia.
- Testemunha 1d na mesma lista (ETH/USDT) para o filtro 4h vs 1d vs Todos.
- Ação (stock) fora desta cena crypto; contrato = só 1d.
- `/favorites` sem mudança de copy; sem extra no proto.

**Bug vivo (contrato no Design; correção no Apply, não neste filho):**

- `resolveChartTimeframe` devolve `'1d'`.
- Filtro só Todos/1d.
- Sparkline pede 1d.
- `OpportunityCard` pinta «Gráfico 1d» e `tf 1d`.
- `handleOpenChart` abre em 1d.
- `ChartModal` aberto de Abrir gráfico / Ver Trades no Monitor ainda mostra toolbar `aria-label="Selecionar timeframe do gráfico"` com `Estratégia (TF)` + 15m/1h/1d.

**P3 — detalhe de Apply (aceito aqui, não reabrir como P0/P1):**

- `SPARKLINE_LIMIT` 14 vs janela calendário de 4h: velas no TF da estratégia basta.
- Tipo `TimeframeFilter` alargado vs gerar opções da lista.
- Apagar ou ignorar `price_timeframe` persistido: desde que a ficha não mostre segundo TF; não há TF de inspecção para gravar.
- Overlay vivo do `ChartModal` (inset-0) vs proto com o gráfico abaixo da lista no mesmo URL — o vivo permanece overlay.
- Como esconder/remover a toolbar de seletor no `ChartModal` nesse contexto (prop, ramo, CSS) — o contrato visível é ausência do seletor e presença do rótulo.
- Detector `side-tab` nos cards mobile — incumbente do clone.
- Clip Operar/Ver Trades a 1280 — incumbente da board.
- `MonitorDashboardTab` morto: não ressuscitar.

## Prototype

- Canónico: `https://dev.criptofarol.com.br/prototypes/card-994-monitor-multiplos-timeframes/` → `frontend/public/prototypes/card-994-monitor-multiplos-timeframes/index.html`. Clone da página viva `/monitor` + delta do TF da estratégia. Landmarks: `table.signals`, Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia. `COPIED:start`/`COPIED:end` no clone.
- Sem extra `/favorites`. Sem irmão HTML (Abrir gráfico é modal da mesma página).
- `cp`/clone = copied; delta de TF (lista, filtro da lista, spark, ficha, gráfico 4h sem seletor) = generated.
- Sem painel ANTES/DEPOIS como URL canónica.

## Prototype Validation

- **Comando (autor, local):** clone gate estático `design_clone_gate.classify` = PASS; landmarks `/monitor` ok; pares COPIED 9/9.
- **URL canónica:** `frontend/public/prototypes/card-994-monitor-multiplos-timeframes/index.html` (HTTP DEV após o pai publicar: `https://dev.criptofarol.com.br/prototypes/card-994-monitor-multiplos-timeframes/`).
- **Digest (UTF-8 sha256, gate deste autor):**
  - `index.html` `f79ceb83f3d16a0cd03d2facf0937234170206da2996897796050c3f8e18628b` · 39552 B = 21057 copied + 18495 generated. Pares `COPIED:start`/`COPIED:end`: 9/9; soma UTF-8 copiada 21057 (> 0). T5 mede só este index.html.
- **Asserts de contrato no HTML:** BTC/USDT 4h; filtro da lista opções Todos/4h/1d (`#tf-filter`); ausente «Gráfico 1d» e «tf 1d»; ausente `Selecionar timeframe do gráfico`, `data-chart-tf`, botões 15m/1h/1d/«Estratégia (4H)»; presente rótulo só de leitura `Estratégia · 4h`; coluna visível Gráfico; texto landmark `7d` no COPIED do thead.

## Open Questions

Nenhuma. Fronteira veio grelhada do issue #994. Nome da coluna (Gráfico) e **sem seletor no gráfico** (rótulo só de leitura) fecham o fork Design.

## Design Critique

Method: dual-agent (A: `01a0c14c-8f9a-7c70-9efc-63117392c827` · B: `01a0c14c-8f9a-7c70-9efc-632a4844ac19`)

Com-tela. Teto 1+1+1: autor + dupla + **1 rework**. P0 de produto justificado no prompt do rework: Alan recusou o seletor de TF do gráfico em Aprovação de Design. Dupla do rework **PASS**. Sem P0/P1 novos. Sem segundo rework. Pai submete com os P3 aceitos.

- Autor (ronda 1): design-autor 994 isolado; `cursor-grok-4.6-high`. Contrato antigo (inspecção no seletor) — já não vale.
- Assessment A (ronda 1): isolado; `cursor-grok-4.6-high`. PASS no contrato antigo.
- Assessment B (ronda 1): isolado; `cursor-grok-4.6-high`. PASS no contrato antigo.
- Autor (rework 1): `01a0c143-2333-7903-a7f0-989b8959d0cd` isolado. Fecha o fork — gráfico só exibe o TF da estratégia; sem seletor; filtro da lista intacto.
- Assessment A (rework 1): Hegel, isolado. **PASS**. Nielsen 35/40. Seletor ausente. Filtro da lista intacto. sha256 `f79ceb83f3d16a0cd03d2facf0937234170206da2996897796050c3f8e18628b`.
- Assessment B (rework 1): Russell, isolado. **PASS**. Detector CLI 0 findings. Asserts DOM do seletor/filtro/rótulo PASS nos dois viewports. HTTPS == disco.
- Tokens: `UI impact: affected` / `live_route: /monitor` / `surface: existing` — rubrica PASS.
- Snapshot T7: `.impeccable/critique/994-card-994-monitor-multiplos-timeframes-assessment-A.md`
- Proto: https://dev.criptofarol.com.br/prototypes/card-994-monitor-multiplos-timeframes/ · sha256 `f79ceb83f3d16a0cd03d2facf0937234170206da2996897796050c3f8e18628b` · 39552 B = 21057 copied + 18495 generated.

**P0:** nenhum (seletor do gráfico fechado neste rework).  
**P1:** nenhum  
**P2:** nenhum  
**P3 (aceitos, Apply — não reabrir como P0/P1):** overlay vivo `ChartModal` vs gráfico dockado no proto; clip Operar 1280/1440; busca a 390; KPIs do mock não seguem o filtro; gráfico dockado permanece BTC no filtro 1d; fechar 32.8px a 390; `aria-modal` no diálogo dockado; `DELTA:start`=0; cards 390; SPARKLINE_LIMIT; persistência interna de `price_timeframe`; landmark `7d` no COPIED do thead; como esconder/remover a toolbar de seletor no `ChartModal` vivo.

proxy modelo: design-autor → Grok 4.6 (grok-4.6)  
proxy modelo: Assessment A → Grok 4.6 (grok-4.6)  
proxy modelo: Assessment B → Grok 4.6 (grok-4.6)
