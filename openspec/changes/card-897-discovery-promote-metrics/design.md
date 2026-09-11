## Context

Card **#897**, Status=Design (T3 done). Fronteira grelhada no issue; Q1=A e Q2=A aceites (2026-09-11). Sem re-entrevista.

Incidente PROD: operador promoveu `ALPHA/USDT · 1d · Long` (descoberta `RS-B109ED2C80`) a favorito `#193` (tier 3). Na grade `/favorites` as colunas Sharpe, Trades, Win%, Return e Max DD ficaram `-` / 0. Ao abrir o gráfico, o resumo mostrou retorno −13,92%, acerto 33,3%, 12 operações e Max DD «Indisponível» — números de um **terceiro backtest** nas velas atuais, não da linha da Descoberta (Sharpe 0,31, 30 negócios, win 46,7%, retorno +16.951%, Max DD 16,5%, janela 2020-10-10 → 2024-02-01).

Estado atual (worktree `card-897-discovery-promote-metrics`, base develop):

- Promoção grava origem no topo e números em `metrics_snapshot`. A grade lê o topo (`sharpe_ratio`, `win_rate`, `max_drawdown`, `total_return` / `total_return_pct`, `total_trades` ou lista `trades`). Favorito salvo pelo combo já grava essas chaves no topo; o da Descoberta não.
- Abrir a análise sem lista de operações gravada rerroda e **persiste** o resultado por cima das métricas. A tela `/combo/results` deriva retorno/acerto das operações exibidas e só mostra Max DD se a chave existir no objeto — daí «Indisponível».
- Spec `discovery-promotion` já exige guardar o snapshot; o furo é o snapshot não estar no sítio que a grade lê. `#193` está `already_promoted`; promover de novo não regrava.

**Usuário:** administrador que promove um candidato da Descoberta e confere o que acabou de salvar.
**Hipótese:** se a grade e o resumo da análise repetem o snapshot da promoção, o operador não acha que a promoção apagou a estratégia.
**Resultado:** linha preenchida na grade; resumo = snapshot; janela rotulada quando a lista é das velas atuais.

**Impeccable recorte (Operate):** audience = admin na grade de Favoritos e na análise aberta pelo gráfico; outcome = conferir o snapshot sem confundir 12 negócios atuais com 30 da Descoberta; direction = clone da página viva + delta de números e etiquetas, sem redesign; scope = `/favorites` canónico e `/combo/results` extra.

UI impact: affected
live_route: /favorites
surface: existing

> **Design fecha em 1+1+1 (teto):** sem-tela = 1 autor + 1 crítico + 1 rework; com-tela = autor + dupla + 1 rework. Segundo rework só com P0 novo de produto justificado no prompt; fora disso o pai publica a seção de crítica com os P3 aceitos e submete. **Classificação:** só produto/escopo/contrato visível (tela, estados, acessibilidade, escopo furado) gera P0/P1; detalhe de implementação é P3 "detalhe de Apply", aceito em `design.md` e resolvido no Apply — nunca reaberto como P0/P1. **Gate no autor:** o primeiro autor já entrega `UI impact` / `live_route` / `surface` em linha própria parseável; sem-tela declara ausência + justificativa curta (nunca rota de catálogo emprestada); com-tela marca só as regiões clonadas. O crítico/dupla verifica esses tokens como item da rubrica.

Regiões clonadas: shell autenticado + workbench `/favorites` (`table.fav-strategies`, «Estratégias favoritas», «Symbol», «Estratégia», «Ações»). Extra: `/combo/results` em `analise.html` (resumo + lista de operações).

## Goals / Non-Goals

**Goals:**

- Promover a tier 3 deixa na linha de Favoritos, no mesmo sítio que a grade já lê, Sharpe, negócios, win rate, retorno e Max DD (e Profit Factor se o resultado já o tinha) — números do snapshot da promoção.
- Origem (varredura, result id, identity, snapshot completo) continua nos metadados.
- Favoritos já promovidos da Descoberta cujo snapshot já tem os números passam a mostrar esses números (`#193` incluído). Não é preciso promover de novo.
- Abrir o gráfico não apaga da grade os números do snapshot.
- Resumo da análise = snapshot. Max DD não é «Indisponível» se o snapshot tem Max DD.
- Se a lista de operações continuar nas velas atuais, a janela está rotulada e distinta da janela do resumo.

**Non-Goals:**

- Corrigir o Calmar `1e27` nem o ranking das parciais (#896).
- Redesign da grade de Favoritos (colunas novas, mobile, Excel).
- Reconstruir neste card a lista de operações e o gráfico na janela da Descoberta. Velas atuais na lista continuam permitidas se a janela estiver rotulada. Janela recente continua no botão Revalidar.
- Mudar regras de dedup / tier 3 / idempotência da promoção, salvo o necessário para os números aparecerem no contrato da grade.
- Recalcular varreduras antigas, universo de símbolos ou split 70/30.
- Monitor, Telegram.
- Favorito antigo salvo pelo combo: a grade desses continua igual.

## Decisions

1. **Leitura flatten no GET + escrita flatten na promoção.**
   Q2=A exige que `#193` (já `already_promoted`) mostre os números sem promover de novo. A promoção nova também grava no topo, para o persistido coincidir com o GET. Alternativa «só backfill write» rejeitada: promover de novo não regrava o mesmo resultado. Alternativa «a grade passa a ler o envelope aninhado» rejeitada: o contrato visível é o sítio que a grade já lê, sem redesign da tabela.

2. **Persistir o terceiro backtest não substitui as chaves do snapshot.**
   Regenerar nas velas atuais pode gravar a lista de operações e velas para o gráfico. As chaves que a grade e o resumo lêem permanecem as do snapshot. Alternativa «nunca persistir regeneração» rejeitada: combo-saved ainda usa o cache de trades; só o favorito da Descoberta protege o snapshot.

3. **Resumo da análise = snapshot; lista pode ser velas atuais.**
   Q1=A. `/combo/results` deixa de derivar retorno/acerto/negócios/Max DD da lista exibida quando a origem é Descoberta. Max DD vem do snapshot (não «Indisponível»). Alternativa «esconder a lista atual» rejeitada — reconstruir os 30 negócios da Descoberta está fora.

4. **Copy da janela rotulada (visível, não tooltip).**
   Resumo: `Resumo · janela de treino da Descoberta · 10/10/2020 → 01/02/2024`.
   Lista: `Lista de operações · velas atuais · 12 negócios — não é a janela da Descoberta`.
   As duas etiquetas são distintas e visíveis no estado padrão. Datas seguem o período efetivo do snapshot; a contagem da lista é a da lista. Alternativa só `aria-label` rejeitada: o operador precisa ler a diferença.

## Risks / Trade-offs

- [Risco] GET flatten diverge do JSON persistido até o próximo write → Mitigação: promoção nova já grava no topo; GET flatten cobre o estoque (`#193`); testes de GET não exigem PATCH.
- [Risco] Regeneração continua gravando velas/trades e o operador pensa que o gráfico «é a verdade da descoberta» → Mitigação: janela rotulada no resumo e na lista; resumo não usa a lista.
- [Risco] Combo-saved receber o flatten ou a etiqueta → Mitigação: origem Descoberta é o único gatilho; combo-saved fora do contrato deste card.
- [Risco] Max DD do snapshot em escala diferente da UI → Mitigação: reusar o formatador já usado na grade (`formatPct` / `formatMetricPercentage`); P3 de Apply se a escala do JSON exigir normalização.

## Migration Plan

Sem migração de schema. Rollback = reverter o change. `#193` e demais já promovidos passam a aparecer corretos no GET sem job de backfill obrigatório. Persistência flatten na promoção nova é aditiva.

## Apply contract

Apply lê este `design.md` e o HTML em `frontend/public/prototypes/card-897-discovery-promote-metrics/` como spec de layout. Sem HTML neste arquivo.

**Contrato visível (não P3):**

- Grade `/favorites`: linha promovida da Descoberta com Sharpe, Trades, Win%, Return, Max DD preenchidos do snapshot. Exemplo `#193`: Sharpe 0,31 · 30 negócios · win 46,7% · retorno +16.951% · Max DD 16,5%.
- Linha combo-saved inalterada.
- Abrir o gráfico não zera nem troca esses números na grade.
- Resumo `/combo/results` = snapshot; Max DD não «Indisponível» se o snapshot tem Max DD.
- Lista em velas atuais ⇒ etiqueta de janela distinta da do resumo.

**P3 — detalhe de Apply (aceito aqui, não reabrir como P0/P1):**

- Nomes exatos de chaves JSON / ORM (`metrics` topo vs `metrics_snapshot`, `total_return` vs `total_return_pct`, `total_trades` vs lista `trades`).
- Helper de flatten no GET vs cópia na promoção: ambos permitidos desde que o GET de `#193` preencha a grade.
- Onde guardar trades regenerados (mesmo objeto, prefixo `analysis_*`, ou sidecar) desde que as chaves da grade/resumo não sejam sobrescritas.
- `ComboResultsPage`: não usar `derivedMetrics` da lista para o resumo quando a origem é Descoberta; passar o snapshot no `location.state` ou lê-lo do GET.
- Datas da etiqueta: `start_date`/`end_date` do favorito ou do snapshot; formato pt-BR.
- Testids da etiqueta e da linha `#193`.
- Normalização de escala (ratio vs pontos percentuais) reusando os formatadores vivos.

## Prototype

- Canónico: `https://dev.criptofarol.com.br/prototypes/card-897-discovery-promote-metrics/` → `frontend/public/prototypes/card-897-discovery-promote-metrics/index.html`. Clone da página viva `/favorites` + delta deste card (linha Descoberta `#193` preenchida; linha combo-saved igual à de hoje; abrir gráfico não apaga a grade). Landmarks: `table.fav-strategies`, «Estratégias favoritas», «Symbol», «Estratégia», «Ações». `COPIED:start`/`COPIED:end` no clone.
- Extra (copy visível da análise, **não** `index.html`): `https://dev.criptofarol.com.br/prototypes/card-897-discovery-promote-metrics/analise.html` — clone de `/combo/results` com resumo = snapshot e janela rotulada na lista de 12 negócios atuais.
- Digest, desktop/mobile e bytes copied vs generated: ver `## Prototype Validation` após o browser gate.
- Base: live DEV `https://dev.criptofarol.com.br/favorites` e `https://dev.criptofarol.com.br/combo/results`. Folha de tokens = chrome; não substitui o clone. Sem painel ANTES/DEPOIS como URL canónica.

## Prototype Validation

- **URLs:** canónico `https://dev.criptofarol.com.br/prototypes/card-897-discovery-promote-metrics/` (`frontend/public/prototypes/card-897-discovery-promote-metrics/index.html`); extra `https://dev.criptofarol.com.br/prototypes/card-897-discovery-promote-metrics/analise.html`.
- **Viewports:** desktop 1280×800 + mobile 390×844, Chromium headed (`xvfb-run` + `@playwright/cli` `--headed --browser chromium`). Screenshots: `.impeccable/critique/card-897-index-desktop-1280x800.png`, `card-897-index-mobile-390x844.png`, `card-897-analise-desktop-1280x800.png`, `card-897-analise-mobile-390x844.png`.
- **Ações / asserts (index):** landmarks `table.fav-strategies`, «Estratégias favoritas», «Symbol», «Estratégia», «Ações»; linha `#193` Sharpe/Trades/Win%/Return/Max DD ≠ `-` / vazio / 0 (0,31 · 30 · 46,7% · +16.951% · 16,5%); linha combo-saved BTC/USDT preenchida e sem origem Descoberta; ícone de gráfico abre `analise.html` e ao voltar as células de `#193` permanecem iguais.
- **Ações / asserts (analise):** etiquetas visíveis `Resumo · janela de treino da Descoberta · 10/10/2020 → 01/02/2024` e `Lista de operações · velas atuais · 12 negócios — não é a janela da Descoberta`; resumo snapshot +16.951% · 46,7% · 16,5% · 30; Max DD ≠ «Indisponível»; lista com 12 negócios incluindo −13,92%.
- **Resultado:** index PASS 31/31 · analise PASS 12/12 · FAIL 0. Clone gate `classify(/favorites)=PASS`, `copied_utf8_sum(index)=7642`.
- **Digest (UTF-8 sha256, pós-polish = gate):**
  - `index.html` `f35495bc6d0d24b3ae78a258accc17257dd6126b4a4325c01070c11bac8309bc` · 42058 B = 7642 copied (`COPIED` shell+heading+thead+footer) + 34416 generated (delta `#193` / combo-saved / CSS).
  - `analise.html` `5ea6e082ddeae17d8d5c6d6b89deefe78d167a7e62772157f492fd5d93ccb7b7` · 21405 B = 4980 copied + 16425 generated (etiquetas de janela, snapshot, 12 negócios).

## Open Questions

Nenhuma. Fronteira veio grelhada do issue #897 (Q1=A, Q2=A). Copy da etiqueta decidida acima.

## Design Critique

Onda A/B (com-tela) no mesmo turno; zero P0/P1 aberto; sem rework.

- **P0:** nenhum
- **P1:** nenhum
- **P3** aceito (Apply): proto CSS 1400px ≠ vivo 1540/1280 — Win%/Max DD visíveis a 1280; este card não redesenha breakpoints
- **P3** aceito (Apply): chip/meta «Descoberta · RS-… · #193» extra vs apelido vivo — não é coluna nova
- **P3** aceito (Apply): cards mobile acrescentam Win%/Max DD (vivo = TF/Sharpe/Trades/Return)
- **P3** aceito (Apply): `analise.html` omite regras/transparência/candlestick real; h1 = etiqueta de janela
- **P3** aceito (Apply): flatten/chaves JSON/formatadores (`+16.951%` vs `toFixed` vivo) — já no Apply contract
- **P3** aceito (Apply): mock sem loading/vazio/erro; persistência pós-gráfico é HTML estático (tasks 2.1–2.2)
- **P3** aceito (Apply): alvos 28/32px e Delete só `title` = vivo
- **P3** aceito (Apply/detector): `side-tab` ×2 (`border-left` nos cards mobile de tier); truncagem desktop `RS-B109ED2C80 · #193` → `#1…`

Pendências não bloqueantes: live `/favorites` sem sessão cai em `/login` (não é prova de clone). Detector index 2 warning classificados P3; analise 0; nada sem classificação.

Protótipo: `https://dev.criptofarol.com.br/prototypes/card-897-discovery-promote-metrics/` (digest `f35495bc6d0d24b3ae78a258accc17257dd6126b4a4325c01070c11bac8309bc`). Extra: `…/analise.html` (digest `5ea6e082ddeae17d8d5c6d6b89deefe78d167a7e62772157f492fd5d93ccb7b7`).

Snapshot: `.impeccable/critique/897-card-897-discovery-promote-metrics-A-20260911T175925Z.md` · B `.impeccable/critique/897-card-897-discovery-promote-metrics-B-20260911T180043Z.md`

Tokens: `UI impact: affected` · `live_route: /favorites` · `surface: existing`

Design Agent verdict: PASS
