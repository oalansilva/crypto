# Assessment A — card 953 · change card-953-grafico-medias-periodo

> Avaliador A isolado (produto / UX / a11y / fidelidade do clone). Crítico independente, onda dupla com-tela. Sem transcript do pai. Sem nested-spawn. Sem edição de `design.md`, HTML proto, `backend/`, `frontend/src/` ou OpenSpec. Sem `process_event`. Sem arraste de Status. Única escrita: este arquivo + PNGs `953-A-*` + `953-A-gate.json`.

`proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)`

## Metadata

- card: 953 — "Gráfico: velas do período inteiro sem médias calculadas"
- change: `card-953-grafico-medias-periodo`
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-953-grafico-medias-periodo`
- branch: `card-953-grafico-medias-periodo`
- tuple: `bound_card=953` · `q_git=card-953-grafico-medias-periodo` (resolver local; este filho não chama `process_event`)
- data (UTC): 2026-09-16T18:34Z
- Status observado: Design (bind do pai; REST `gh api repos/oalansilva/crypto/issues/953`, não `gh issue view`)
- UI impact (rubrica): **affected** · `live_route: /combo/results` · `surface: existing` — linhas próprias 9–11 de `design.md` (parseáveis)
- Digest proto (esta sessão):

| ficheiro | sha256 | bytes |
|---|---|---|
| `index.html` | `7f848b6cd861dff02649aebc04dbc3fb670bc9d3c05dbabfe3c9e9542e16ee4e` | 37236 |
| `monitor.html` | `c59eec83bc3df59c0912f936b5b958eaecb6192eccb46cfcc0629043b242ac01` | 26095 |

- Servido HTTPS == local: IDENTICAL nos 2 HTML (HTTP 200)
- Issue: REST #953. Fronteira vazia. Q2 aceite = B. Aceite 1–10 **não reaberto**.
- D4: com-tela = autor + dupla + 1 rework. Tokens verificados como item da rubrica — nenhuma rodada extra só para o parser.
- Ignore list: `.impeccable/critique/ignore.md` ausente
- Tooling: Playwright Python + Chromium 1148 (`/home/ubuntu/.cache/ms-playwright/chromium-1148/chrome-linux/chrome`), HTTPS real, viewports 1440×900 e 390×844. 0 console error / 0 pageerror.

## Limitação de sessão (obrigatória)

| URL pedida | URL final | h1 | Landmarks |
|---|---|---|---|
| `https://dev.criptofarol.com.br/combo/results` | `https://dev.criptofarol.com.br/login` (HTTP 200) | `Bem-vindo de volta` | `.combo-page` = 0 · «Lista de operações» = 0 · `aria-label="Análise da estratégia"` = 0 |
| `https://dev.criptofarol.com.br/monitor` | `https://dev.criptofarol.com.br/login` (HTTP 200) | `Bem-vindo de volta` | `table.signals` = 0 |

**`/login` não é a rota.** Chrome de login **não** é evidência de clone e **não** autoriza PASS de fidelidade. Sem cookie de administrador, a avaliação de clone usa: (1) protótipo canónico HTTPS, (2) extra `monitor.html` HTTPS, (3) HTML local, (4) fonte viva `ComboResultsPage.tsx` / `StrategyTradesTable.tsx` / `StrategyChartSurface.tsx` / `MonitorStatusTab.tsx` vs catálogo `scripts/process-fsm/route-landmarks.yaml`. Sidebar 224px / tokens `--bg-*` **não** bastam. PNG `953-A-live-results.png` / `953-A-live-monitor.png` = login, descartados.

HTTP 200 isolado nunca é PASS. Os 200 do proto coincidem com digest e com asserts de landmark/contrato no browser.

## Tokens parseáveis (rubrica D4)

`design.md` linhas próprias 9–11:

```
UI impact: affected
live_route: /combo/results
surface: existing
```

Justificativa no corpo: clone+delta Operate da rota existente `/combo/results`; regiões clonadas marcadas (shell AppNav + `.combo-page` + «Lista de operações» + `aria-label="Análise da estratégia"` + chrome Menos/Mais/Resetar «180 velas»). Extra `/monitor` = `monitor.html`, **nunca** `live_route` nem `index.html`. **Não** empresta `/favorites`, `/combo/select` nem `/combo/discovery`. **PASS** deste item da rubrica. Nenhuma rodada extra nasce só para o parser.

Bloco D4 no `design.md` = texto exacto da skill.

## Digest proto (disco == HTTPS)

Disco == HTTPS: IDENTICAL nos 2 ficheiros. `design.md` Prototype Validation cita desktop+mobile nas 2 URLs públicas — esta sessão reabriu as mesmas URLs no Playwright e confirma.

`COPIED:start`/`COPIED:end`: index **6/6** pares · extra **2/2** pares. copied > 0.

## Fidelidade (clone da página viva)

Catálogo `/combo/results` (`scripts/process-fsm/route-landmarks.yaml`): `selectors: [".combo-page"]` · texts `Lista de operações`, `Análise da estratégia`.

Catálogo `/monitor`: `selectors: ["table.signals"]` · texts `Status`, `Preço`, `Distância`, `7d`, `Risco até stop`, `Tags`, `Operar`, `Par / Estratégia`.

Fonte viva: `ComboResultsPage.tsx` L398 `.combo-page` + L425 `aria-label="Análise da estratégia"`; `StrategyTradesTable.tsx` L222 «Lista de operações»; `StrategyChartSurface.tsx` `DEFAULT_VISIBLE_BARS = 180` + Menos/Resetar; `MonitorStatusTab.tsx` L1182 `table.signals` + thead L1186–1193.

| Landmark | Vivo | Proto + Playwright |
|---|---|---|
| `.combo-page` | L398 | index desktop+mobile count=1 |
| `Análise da estratégia` | L425 | `aria-label` count=1, visível |
| `Lista de operações` | L222 | tab `#trades-window-label` visível desktop e mobile |
| `table.signals` | L1182 | extra `monitor.html` count=1, visível |
| Cabeçalhos Monitor | L1186–1193 | thead exacto: Par / Estratégia, Status, Preço, Distância, 7d, Risco até stop, Tags, Operar |
| COPIED | — | index 6 pares; extra 2 pares. copied > 0 |

Anti-padrões P0:

- URL canónica `…/prototypes/card-953-grafico-medias-periodo/` → index **é** a página de análise (shell 224px + `.combo-page` + resumo + regras + gráfico + lista). **Não** é painel ANTES/DEPOIS. Botões Antes/Depois visíveis = 0. Texto visível `ANTES`/`DEPOIS` = 0 (só comentário HTML).
- Não é grelha de N estados no lugar da análise. Chip único de período = favorito **2 anos**. Extra `/monitor` é `monitor.html`, nunca no lugar do index.
- `Available Templates` visível = 0. Sem `select.html`. Combo activo no index; Monitor activo no extra.

Chrome presente (sidebar 224px desktop, Inter/Binance, amarelo `#fcd535`) = **folha**, não prova. Prova = landmarks no proto, alinhados ao TSX.

## Produto (aceite visível — não reabrir Qs)

Contrato: velas **e** linhas da estratégia (médias de preço **e** as outras que o gráfico já desenha, painel de baixo) no mesmo recorte carregado, nas duas telas. Recorte = velas já carregadas. Favorito 6m/2a **não** alarga para todo o mercado. Zoom ~180 permanece; recorte visível ao abrir já tem linha (após warmup); ao afastar/Menos/arrastar, velas antigas também têm linha; Resetar não apaga a série. #917 1:1 intacto; #921 linha **não** à frente da última vela; #949 período do favorito intacto.

P3 de Apply (não reabrir como P0/P1): recompute vs extend, warmup N−1, clip #921, indicadores não-SMA, open sem bloquear, canvas vs SVG.

| Aceite visível | Evidência (Playwright 1440×900 e 390×844 + PNG do chart) | Disposition |
|---|---|---|
| Análise 2 anos: velas 16/09/2024 → 16/09/2026, **não** 17/08/2017 | chip `2 anos · 16/09/2024 → 16/09/2026`; `data-period-start=2024-09-16`; `data-whole-market=0`; body `17/08/2017` = false desktop e mobile | OK |
| Zoom ao abrir ~180 com linha | chip **180 velas**; SMA 9/21 paths `fast_d=2331` / `slow_d=2331`; PNG `953-A-desktop-1440x900-index-chart.png` mostra vermelho+azul no recorte 2026-03 → 2026-09 | OK |
| Menos ×2 → 320; Menos até ao fundo → 731 com linha nas velas antigas | 320 velas / `viewportFrom=2025-11-01`; full `viewportFrom=2024-09-16`, `linesOnOld=1`, `fast_d=9318`; PNG `…-index-chart-full.png` eixo 2024-09 → 2026-09 com SMA contínua | OK |
| Resetar volta a 180 sem apagar a série | reset **180 velas**, paths ainda `2331`, `data-ma-ahead=0` | OK |
| Clip #921 | `data-last-candle=data-last-ma=2026-09-16`; `data-ma-ahead=0`; pontas no extremo direito, não à frente | OK |
| #917 1:1 | chip `Lista 16 · Setas 32`; `data-list-count=16` · `data-marker-count=32`; 32 `<tr>` (16 ops × entrada+saída); mobile 16 cards | OK |
| #949 período intacto | 2 anos, não «todo»; chip «Favorito 2 anos · não todo o mercado»; 731 velas 1d ≈ 2 anos, não 2017 | OK |
| Volume = overlay da Virada, sem inventar RSI/MACD na análise | legend `SMA 9` / `SMA 21` / `Volume (gráfico vivo)`; sem painel MACD no index | OK |
| Monitor: mesmo recorte velas↔linhas | open 180 + SMA; Menos ×2 = 320; full 731 `linesOnOld=1` `loadedCount=731` `wholeMarket=0` | OK |
| Painel de baixo MACD na linha SOL, mesmo recorte | clique SOL: `lower_hidden=false`, título `Painel macd: MACD`, 2 paths, legend EMA 12/26; full 731 ainda 2 paths, eixo 2024-09 → 2026-09. BTC default **sem** MACD (não inventa) | OK |
| Outro intervalo não vira «todo o mercado» | SOL 1h: `loadedCount=240`, `wholeMarket=0`, `maAhead=0`, MACD 2 paths, zoom 180 | OK |
| Linhas não escondidas no Monitor | SMA/EMA visíveis no default BTC e no SOL; lower panel só quando a estratégia o declara | OK |

Qs **não reabertas**. Warmup SMA 21 / EMA 26 nas primeiras velas do full **não** conta como furo (azul arranca depois do extremo esquerdo — aceite do card).

## UX

Hierarquia: AppNav → Voltar aos favoritos → resumo (período 2 anos) → regras → gráfico (180 / Menos / linhas) → lista. Job único: ler preço e indicadores no mesmo recorte.

Carga: um favorito, um gráfico, um extra Monitor. Delta óbvio sem redesign: SMA já no recorte de 180; Menos revela 2024 **com** linha; chip verde nomeia «não todo o mercado».

Monitor: tabela de sinais encima; gráfico abaixo. Trocar BTC→SOL troca legend SMA→EMA e revela o painel MACD — o operador não precisa de adivinhar o valor.

## Acessibilidade

- `lang=pt-BR`; `:focus-visible`; `prefers-reduced-motion`.
- Landmarks: `nav` + `main`; index `aria-label="Análise da estratégia"`; extra `table.signals`; gráfico `role=img` + `aria-label` (clip à última vela nomeado); toolbar `role=group`.
- Timeframe Monitor: `aria-pressed` nos tf-btn.
- Linhas identificadas por texto na legend (SMA 9 / SMA 21 / EMA 12 / EMA 26 / Painel macd), não só cor.
- Alvos 44px nos zoom; nav 42px e Operar 36px = clone vivo / P3 já no `design.md`.
- Contraste: pares Binance; verde/vermelho em velas e Return; SMA vermelho `#f6465d` / azul `#3b82f6` sobre `#0b0e11`.

## Responsividade

- Desktop 1440×900: sidebar 224px; Combo/Monitor activos; overflow-x = 0. PNG de página `953-A-desktop-1440x900-index.png` / `…-monitor.png`. O gráfico da análise fica abaixo das regras no recorte de 900px (clone do empilhamento vivo) — prova do delta = PNG da região `#result-chart`.
- Mobile 390×844: sidebar 0; header 72px; cards da lista (16); overflow-x documento = 0. Tabela Monitor clipa Distância/7d/Operar no thead (tabela larga incumbente) — P3. Gráfico e MACD cabem após scroll.

## Estados

Mock cobre: open 180 com linha; Menos 320/731 com linha nas velas antigas; Resetar 180 com série intacta; clip #921; 2 anos ≠ todo; BTC Virada sem painel inventado; SOL MACD no mesmo recorte; 1h 240 velas. Não mocka: loading/vazio/erro de rede, favorito 6 meses (contrato 2 anos basta). Cobertura de mock = P3.

## Design specificity

A tela é a análise Cripto Farol dum favorito 2 anos + o Monitor de sinais, depois de #917/#921/#949. Não iria a um SaaS genérico inalterado: chips «Favorito 2 anos · não todo o mercado», 1:1 lista↔setas, clip à última vela, painel MACD só na estratégia que o desenha. Modo Impeccable: **Operate** / refinement. Folha Binance; `DESIGN.md` não reescrito.

## Heurísticas Nielsen (0–4, Operate; só neste snapshot)

| # | Heurística | Score | Nota |
|---|---|---|---|
| 1 | Visibility of system status | 4 | «180 velas» / «731 velas»; chips de recorte; `aria-live` no index |
| 2 | Match between system and real world | 4 | 2 anos = 16/09/2024 → 16/09/2026; SMA da Virada; MACD só no SOL |
| 3 | User control and freedom | 4 | Menos / Mais / Resetar / arrastar / roda; Resetar não apaga a série |
| 4 | Consistency and standards | 4 | Mesmo recorte nas duas telas; clip #921; 1:1 #917; #949 intacto |
| 5 | Error prevention | 4 | Não alarga a 2017; não inventa linha; warmup não é furo |
| 6 | Recognition rather than recall | 4 | Legend + chips nomeiam o recorte; linha visível ao abrir |
| 7 | Flexibility and efficiency | 3 | Mock sem atalhos do vivo; tf 15m/1h/4h/1d no extra |
| 8 | Aesthetic and minimalist design | 3 | Clone denso; labels Compra/Venda sobrepostas no recorte 180 |
| 9 | Help users recognize/recover errors | n/a | Sem formulário neste fluxo |
| 10 | Help and documentation | 3 | Chips de guarda; disclaimer educacional no index |
| **Total** | | **33/36** | **Good** (heurística 9 n/a) |

## Cognitive load

Checklist: 1 h1; 1 gráfico; 1 lista; extra 1 tabela + 1 gráfico. **Pass** (0 falhas). Decisão no glance ≤4 (Menos para ver 2024 com linha).

## Emotional journey

Vale (velas no período, médias só no pedaço recente) → pico (180 já com SMA; Menos mostra 2024-09 com linha até 2026-09) → fim (Resetar devolve a leitura recente; 2 anos não vira 2017; SOL revela MACD no mesmo recorte). Reassegurança: pontas da média no último candle, sem buraco à direita.

## Personas

1. **Alex (Favoritos → análise):** abre Virada 2 anos; vê 180 velas **com** SMA 9/21; Menos até 731 ainda com linha; não vê 17/08/2017.
2. **Riley (Monitor):** BTC com SMA; clica SOL e lê EMA 12/26 + painel MACD no mesmo recorte; 1h continua 240 velas, não o mercado inteiro.
3. **Casey (mobile):** 390×844 repete chips 2 anos / 180 velas / 1:1; gráfico com SMA; extra SOL mostra MACD após scroll.

## Strengths

- Clone estrutural de `/combo/results` no index, não galeria ANTES/DEPOIS.
- Delta mínimo e óbvio: linhas no histórico carregado, zoom 180 intacto, 2 anos ≠ todo.
- Extra `/monitor` demonstra o painel de baixo **só** na estratégia que o gráfico já desenha (MACD no SOL), sem inventar na Virada.
- #917 / #921 / #949 visivelmente fechados no mesmo mock.
- Warmup visível e aceite; clip à direita fechado.

## Playwright (esta sessão)

- Desktop 1440×900 e mobile 390×844: aceite visível 12/12 PASS. 0 console / 0 pageerror.
- Live `/combo/results` `/monitor` → `/login` (descartado).
- Detector `detect.mjs`: index `[]`; monitor `flat-type-hierarchy` warning L24 (12/13/20px) — incumbente do clone denso, P3.
- PNGs canónicos: `953-A-desktop-1440x900-{index,monitor}.png`, `953-A-mobile-390x844-{index,monitor}.png`. Extra de contrato: `*-index-chart.png`, `*-index-chart-full.png`, `*-monitor-sol-chart.png`, `*-monitor-sol-chart-full.png`, `*-index-menos.png`, `*-monitor-sol.png`, `953-A-live-{results,monitor}.png`. Gate: `953-A-gate.json`.

## Prototype Validation (rubrica 6)

`design.md` secção Prototype Validation presente: Playwright desktop+mobile, PASS declarado pelo autor. Esta sessão **reexecutou** o browser nas 2 URLs públicas e confirma o mesmo aceite visível (180 / 320 / 731 / Resetar / clip / 2 anos / SOL MACD / 1h). Curl 200 não substituiu o Playwright.

## Priority issues

Nenhum P0/P1 de produto/escopo/contrato visível.

## P0

_(nenhum)_

## P1

_(nenhum)_

## P2

_(nenhum)_

## P3 — detalhe de Apply / clone de região fora do delta

- **P3-1** Detector `flat-type-hierarchy` em `monitor.html` (12/13/20px) — clone denso `/monitor`. Não esconde linhas nem alarga o período.
- **P3-2** Nav 42px / botão Operar 36px — clone vivo; já no contrato Apply (`side-tab` / alvos 32px).
- **P3-3** Canvas lightweight-charts vs SVG do proto; velas sintéticas no Monitor. Já no Apply «canvas vs SVG».
- **P3-4** Labels Compra/Venda sobrepostas no recorte 180 do SVG (#917 mock). 1:1 lista 16 ↔ setas 32 permanece.
- **P3-5** Tabela Monitor a 390×844 clipa Distância/7d/Operar — incumbente da tabela larga, não delta das linhas.
- **P3-6** Mobilebar do extra fica «BTC/USDT 1d» ao seleccionar SOL; o h2 do gráfico actualiza. Chrome mock, não furo de recorte.
- **P3-7** Array `TRADES` no JS ainda tem 2017–2023; a lista visível filtra ≥ 2024-09-16 (16 ops). Higiene do mock.
- **P3-8** Datas da lista em inglês (`Jan`, `Feb`) — clone/i18n do proto #921, não o período do favorito.
- **P3-9** CSS `--accent` vs folha `--accent-primary`; hex Binance bate.
- **P3-10** Mock sem loading/vazio/erro; favorito 6 meses não mockado (2 anos basta). Warmup N−1, recompute vs extend, clip #921, indicadores não-SMA, open sem bloquear = Apply, já aceitos em `design.md`.

## Disposition

Aceitar P3 no Apply. Não reabrir grelha. Não reabrir #917 / #921 / #949. Não exigir segundo rework de Design por estes itens. Não promover `flat-type-hierarchy` / SVG / clip da tabela / mobilebar estático a P0/P1.

## Verdict

**PASS** — zero P0/P1 de produto/escopo/contrato visível. Tokens parseáveis 3/3. Landmarks `/combo/results` no index. Extra `/monitor` em `monitor.html`. Disco == HTTPS. Sem galeria/ANTES-DEPOIS como index. copied > 0. Delta = linhas no recorte das velas carregadas (SMA 9/21 na Virada 2 anos; MACD no SOL), zoom 180, Menos revela 2024 com linha, Resetar conserva a série, clip `data-ma-ahead=0`, 1:1 16/32, período ≠ 2017. `/login` descartado. Clone **não** alegado só por sidebar: prova = landmarks proto × TSX × PNG do gráfico.

`Design Agent verdict` final da coluna = síntese do pai após A+B. Este filho A não chama `process_event`.

---

```
Assessment A 953
tokens_ok: yes
clone_ok: yes
P0: nenhum
P1: nenhum
P3: flat-type-hierarchy monitor; nav 42px / Operar 36px; SVG vs canvas; labels Compra/Venda overlap 180; tabela Monitor clip 390; mobilebar BTC estático no SOL; TRADES 2017 no JS filtrado; datas EN na lista; CSS vars; mock sem loading/6m
verdict: PASS
```
