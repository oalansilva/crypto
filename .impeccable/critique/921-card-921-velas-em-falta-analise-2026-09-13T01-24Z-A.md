# Assessment A — card 921 · change card-921-velas-em-falta-analise

> Avaliador A isolado (produto / UX / a11y / heurísticas / fidelidade do clone). Mesmo modelo inherit. Sem transcript do pai. Sem nested-spawn. Sem edição de `design.md`, HTML proto, produto ou OpenSpec specs. Sem `process_event`. Única escrita: `.impeccable/critique/**`. Helper `critique-storage.mjs` não coube no nome pedido (gera `timestamp__slug.md`); ficheiro canónico deste A = este path.

## Metadata

- card: 921 — Velas em falta no gráfico da análise (snapshot + OHLCV parado)
- change: `card-921-velas-em-falta-analise`
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-921-velas-em-falta-analise`
- branch: `card-921-velas-em-falta-analise`
- data (UTC): 2026-09-13T01:24Z
- Status observado: Design (artefatos `openspec/changes/card-921-velas-em-falta-analise/`)
- UI impact (rubrica): **affected** · `live_route: /combo/results` · `surface: existing` — linhas próprias 13–15 de `design.md`
- D4: bloco exacto presente (teto 1+1+1 / classificação P0-P1 vs P3 / gate de tokens). Com-tela = autor + dupla + 1 rework.
- Issue REST: https://github.com/oalansilva/crypto/issues/921 (grelhado; aceite 1–9; decisões Alan gravadas)
- Ignore list: `.impeccable/critique/ignore.md` ausente
- Shape do autor lido: `.impeccable/critique/2026-09-13T01-17-24Z__totypes-card-921-velas-em-falta-analise-index-html.md` (não é este A)
- Catálogo T5 (worktree `scripts/process-fsm/route-landmarks.yaml`):
  - `/combo/results` → `selectors: [".combo-page"]`, `texts: ["Lista de operações", "Análise da estratégia"]`
  - `/monitor` → `selectors: ["table.signals"]`, `texts: ["Status", "Preço", "Distância", "7d", "Risco até stop", "Tags", "Operar", "Par / Estratégia"]`
- `DESIGN.md` lido como autoridade visual; **não reescrito**
- MCP browser desta sessão: tabs instáveis (`No browser tab available`). Equivalente: Playwright Chromium `/usr/bin/chromium-browser`, `colorScheme: dark`, 1440×900 e 390×844, `networkidle`. Evidência JSON: `921-A-evidence.json`

## Limitação de sessão (obrigatória)

| URL pedida | URL final | h1 | Landmarks da rota |
|---|---|---|---|
| `https://dev.criptofarol.com.br/combo/results` | `https://dev.criptofarol.com.br/login` | Bem-vindo de volta | 0/3 (`.combo-page`=0, Lista=0) |
| `https://dev.criptofarol.com.br/monitor` | `https://dev.criptofarol.com.br/login` | Bem-vindo de volta | `table.signals`=0 |

**`/login` não é a rota.** Chrome de login **não** é evidência de clone e **não** autoriza PASS de fidelidade. Sem cookie de administrador, a avaliação de clone usa: (1) protótipo canónico HTTPS, (2) extra `monitor.html` HTTPS, (3) HTML local, (4) fonte viva `ComboResultsPage.tsx` / `StrategyTradesTable.tsx` / `StrategyChartSurface.tsx` / `MonitorStatusTab.tsx` / `ChartModal.tsx` vs catálogo. Sidebar 224px / tokens `--bg-*` **não** bastam.

Proto HTTPS desta sessão **não** é 404 (nota de validação do autor ficou datada): disco == HTTPS.

## Tokens parseáveis (rubrica D4) — item verificado

`design.md` linhas próprias 13–15:

```
UI impact: affected
live_route: /combo/results
surface: existing
```

- `parse_ui_impact` = `affected`
- `parse_live_route` = `/combo/results` (não `/favorites`, não `/combo/select`, não `/monitor`)
- `parse_surface` = `existing`
- Bloco D4 = texto exacto da skill
- Regiões clonadas marcadas: canónico = shell AppNav + `.combo-page` + gráfico chrome (Menos/Mais/Resetar, «180 velas») + «Lista de operações» + disclaimer; extra = AppNav Monitor + `table.signals` + cabeçalhos do catálogo. Extra **nunca** como `index.html`

**PASS deste item.** `live_route` principal = `/combo/results` (rota do catálogo desta tela). Extra `/monitor` é URL irmã. Parser `parse_live_route` devolve a linha seguinte (`surface: existing`) como «justification» vazia-de-mesma-linha — artefacto do helper T5, não empresta rota.

## Digest proto (disco == HTTPS)

| Ponta | sha256 | bytes | HTTP |
|---|---|---|---|
| disco `index.html` | `c48651c3b95ff18d0a4b882e938279815a22dccd046ee6d30b4a08ec98beeac1` | 35170 | — |
| HTTPS `…/prototypes/card-921-velas-em-falta-analise/` | `c48651c3b95ff18d0a4b882e938279815a22dccd046ee6d30b4a08ec98beeac1` | 35170 | 200 |
| disco `monitor.html` | `7ee6c81e1011e10306c0069ba51556b633cdd08ba42e20ca64b1cd07ea4015db` | 19363 | — |
| HTTPS `…/monitor.html` | `7ee6c81e1011e10306c0069ba51556b633cdd08ba42e20ca64b1cd07ea4015db` | 19363 | 200 |

`copied_utf8_sum` oficial (`design_clone_gate.py`): index **7302** (6 pares) · extra **3811** (2 pares). Ambos **> 0**. `classify(index, /combo/results) = PASS`. `landmarks_match` extra `/monitor` = True. Bate com `design.md` Prototype (7302 / 3811).

## Fidelidade (clone da página viva)

### Canónico = index.html = `/combo/results` (não painel ANTES/DEPOIS)

Playwright 1440×900 e 390×844 no HTTPS canónico:

| Landmark catálogo | Vivo (TSX) | Proto |
|---|---|---|
| `.combo-page` | `className="app-page combo-page …"` em `ComboResultsPage.tsx` | visível, count=1 |
| `Lista de operações` | `StrategyTradesTable` | tab `#trades-window-label` visível; 146 linhas (73 ops × entrada+saída) |
| `Análise da estratégia` | `aria-label="Análise da estratégia"` | região visível |

Chrome extra (não catálogo, clone): «Voltar aos favoritos»; chips BTC/USDT · 1D · Long; h1 Médias Móveis; métricas; Regras; Menos/Mais/Resetar; «180 velas»; `aria-label="Controles de zoom do grafico"`; disclaimer educacional. Combo activo na nav.

Anti-padrões P0:

- URL canónica `…/prototypes/card-921-velas-em-falta-analise/` → **é** a página de análise (AppNav + `.combo-page` + resumo + gráfico + lista). **Não** é painel ANTES/DEPOIS. Botões Antes/Depois visíveis = 0. Hits `ANTES`/`DEPOIS` só em comentário HTML («NÃO é painel ANTES/DEPOIS») — não conta como galeria.
- Não é grelha de N estados no lugar de lista+detalhe.
- Extra `/monitor` **não** é o index.
- `copied_utf8_sum` > 0 nas duas superfícies.

Chrome (sidebar 224px, Inter/BinanceNova, amarelo `#fcd535`) = **folha**, não prova. Prova = landmarks 3/3 no index × catálogo `/combo/results` × chrome `ComboResultsPage`.

### Extra = monitor.html = `/monitor` (não index)

| Landmark catálogo | Vivo (`MonitorStatusTab.tsx`) | Proto extra |
|---|---|---|
| `table.signals` | `className="signals"` | presente |
| Status, Preço, Distância, 7d, Risco até stop, Tags, Par / Estratégia | `<th>` da tabela | todos nos `<th>` |
| Operar | botão `Operar` na célula (th de acções vazio no vivo) | `<th>Operar</th>` + botão |

Monitor activo na nav. Copy «Operações ativas e saídas acionáveis. Atualização contínua a cada 30s.» = chrome `MonitorStatusTab`. Duas linhas (BTC + SOL) — não é um furo só de BTC na tabela.

## Delta (contrato visível, sem redesign)

Problema do card: médias até o presente + velas paradas = buraco à direita. Hipótese: mesmo recorte; série de mercado ao abrir quando já está em dia.

Observável no proto (visão + DOM):

- Análise: subtítulo `BTC/USDT • 1d • 3314 velas · série de mercado até 2026-09-12` (3314 = mercado medido no issue, não o snapshot 3286 até 15/08).
- Chip `Velas e médias até 2026-09-12`.
- `data-last-candle = data-last-ma = data-market-last = 2026-09-12`, `data-ma-ahead=0`.
- Extremos SMA no último x do plot (cx 1076 análise / 1080 Monitor) ≈ última vela (rect x 1074/1078). **Sem linha solta à direita.**
- Eixo direito `2026-09` / `2026-09-12`. Screenshot do gráfico: velas e médias terminam juntos; pontos de MA na última barra.
- Monitor: picker 15m / 1h / 4h / 1d; em **todos** `data-ma-ahead=0` e última = 2026-09-12. Zoom inicial continua «180 velas».

Não é redesign de layout da análise: mesma hierarquia AppNav → Voltar → resumo → regras → gráfico → lista. Delta = alinhamento + chip de série, não grelha nova.

## Aceite do Alan (não encolhido)

Decisões gravadas no issue (os três furos; análise **e** Monitor; universo = todos os pares; continuidade; todos os intervalos). `design.md` Goals + Apply contract visível:

| Aceite visível (issue 1–9 / Alan) | Design + proto | Disposition |
|---|---|---|
| 1. Análise: média não à frente da última vela | clip + `data-ma-ahead=0` + screenshot sem buraco | OK |
| 2. Monitor: o mesmo | extra + 4 TFs `ma-ahead=0` | OK |
| 3. Outro activo, não só BTC | tabela Monitor BTC+SOL; mesmo clip; universo no contrato Apply | OK (mock de gráfico = BTC; Apply na mesma rota) |
| 4. Abrir análise com mercado em dia → última vela = mercado (não 15/08) | 3314 velas até 2026-09-12 | OK |
| 5. Par parado (DOGE maio) chega ao presente após enchimento | contrato visível; proto mostra o *depois* (não galeria do parado) | OK como estado resolvido; mock do parado = P3 |
| 6. Pares fora do ecrã também enchem | contrato visível «todos os pares»; «fora do ecrã não é estado de UI» | OK — não encolhido para teto 40 |
| 7. 15m/1h/4h (+ intervalo do favorito) | picker nas quatro; análise 1d do favorito | OK; `ChartTimeframe` só `1d` no TSX vivo = P3 Apply já aceite |
| 8. Continuidade até o presente | contrato visível; incremental no Apply | OK — não dá para teatralizar «semanas depois» no HTML |
| 9. #917 1:1 não reaberto | chip `Lista 73 · Setas 146 · 1:1`; `data-marker-count=146` estável após Menos (240 velas) e Resetar (180); default ≠ fit-all | OK |
| Zoom ~180 | default «180 velas»; Resetar volta a 180; Menos revela mais sem apagar série | OK |

P3 de Apply no `design.md` (writer observador, `MARKET_OHLCV_SYMBOL_LIMIT`/40, `DEFAULT_INGESTION_TIMEFRAMES`, timeout ms, `CURRENT_CHART_CANDLE_LIMIT`, `ChartTimeframe` só 1d, canvas vs SVG, lookback 540) **não** cortam o aceite visível. **Não reabrir como P0/P1.**

## Produto

Usuário = operador que confere o preço até onde a tela afirma estar. Valor = o gráfico deixa de mentir à direita. Fora: redesign; forçar todas as velas no zoom; recálculo de backtest/métricas/promoção; ações/stocks; reabrir 1:1 do #917. Aderência boa.

Decisão 1 (snapshot + actualizar, sem espera bloqueante) não encolhe o critério 4: o proto mostra o estado em que a série viva já chegou. Estado intermédio de timeout não está teatralizado — aceite autoriza pintar snapshot primeiro desde que o critério 4 feche.

## UX

Hierarquia análise: job único (conferir preço + operações no mesmo recorte). Chip verde de alinhamento tira a dúvida «a média foi para o futuro?». Chip 1:1 do #917 permanece — não compete com o delta, complementa.

Monitor: tabela primeiro (landmarks), gráfico do recorte alinhado abaixo. Carga: picker de 4 TFs (já existe no `ChartModal` vivo). Default 180 velas evita milhares de barras.

Progressive disclosure de história: Menos 180→240, Resetar volta; série 3314 e 146 setas intactas.

## Acessibilidade

- `lang=pt-BR`; `:focus-visible`; `prefers-reduced-motion`
- Landmarks `nav` + `main`; `aria-label="Análise da estratégia"`; zoom group nomeado; botões Reduzir/Aumentar/Redefinir
- Alvos desktop zoom: Menos 94×44, Mais 81×44, Resetar 101×44
- Compra/Venda não só por cor (triângulo + rótulo + lista)
- Monitor: `role="group"` Timeframe; `aria-pressed` no TF activo; botão Operar nomeado
- Equivalente a pan: Menos/Mais/Resetar (não é drag-only)
- Disclaimer educacional na análise

## Responsividade

- Desktop 1440×900: sidebar 224px; tabela de operações visível; overflow controlado. PNGs `921-A-proto-index-desktop-*`, `921-A-proto-monitor-desktop-*`
- Mobile 390×844: header 72px; cards de operações no DOM; tabela desk hidden via CSS; picker 15m–1d cabe; tabela Monitor com scroll horizontal (`table-wrap`). PNG `921-A-proto-index-mobile-default.png`, `921-A-proto-monitor-mobile-default.png`
- «Roda do mouse: zoom» no mobile = clone de `StrategyChartSurface.tsx`, não delta deste card

## Estados

Mock análise: BTC/USDT 1d em dia, 73 fechadas, zoom default / out / reset. Mock Monitor: 2 linhas + 4 TFs alinhados. Não mocka: timeout→substituição visível, par ainda parado, vazio, erro de ingestão, permissão. Cobertura de mock = P3 (universo e continuidade são Apply na mesma superfície, não segundo index / não galeria).

## Design specificity

Tela é a análise Cripto Farol (Favoritos → `/combo/results`) e o Monitor de sinais, modo Impeccable **Operate** / refinement. Folha Binance (`#0b0e11`, `#fcd535`, up/down). Não é um dashboard genérico de candles. `DESIGN.md` não reescrito.

## Heurísticas Nielsen (0–4, Operate; só neste snapshot)

| # | Heurística | Score | Nota |
|---|---|---|---|
| 1 | Visibility of system status | 4 | 180/3314 velas; chip «até 2026-09-12»; `data-ma-ahead=0`; 1:1 |
| 2 | Match between system and real world | 3 | Análise interpola trades (parece preço); Monitor usa seno — mock óbvio, contrato de clip intacto |
| 3 | User control and freedom | 4 | Menos/Mais/Resetar; picker TF; Resetar não destroi 1:1 nem série |
| 4 | Consistency and standards | 4 | Chrome vivo + tokens; extra Monitor com cabeçalhos do catálogo |
| 5 | Error prevention | 4 | Clip impede linha solta; default não é fit-all |
| 6 | Recognition rather than recall | 4 | Chip de alinhamento + 1:1 na mesma toolbar |
| 7 | Flexibility and efficiency | 3 | Zoom/pan/TF; proto sem troca de par no gráfico (Apply) |
| 8 | Aesthetic and minimalist design | 4 | Sem galeria; delta mínimo |
| 9 | Help users recognize/recover errors | n/a | Sem formulário neste fluxo |
| 10 | Help and documentation | 3 | Disclaimer análise; extra Monitor sem `ScreenHelpPanel` do vivo |
| **Total** | | **33/36** | **Good** (heurística 9 n/a) |

## Cognitive load

Um job por superfície; chunking resumo → gráfico → lista; chips reduzem memória. **Pass** (0 falhas de checklist). Decisão no open: nenhuma (default já é recorte recente + série em dia). Depois: Menos vs Resetar vs TF (≤4 visíveis no grupo).

## Emotional journey

Vale (buraco à direita no vivo / medo de activo morto) → pico (última vela = 2026-09-12, médias no mesmo x) → fim (Menos revela história #917; Resetar volta a ler). Reassegurança: Operações 73 e chip 1:1 não mudam.

## Personas

1. **Alex (análise Favoritos):** abre BTC 1d e vê 3314 velas até hoje, não 15/08; médias não fogem à direita.
2. **Riley (Monitor):** muda 15m/1h/4h/1d; em todos o chip diz a mesma data e `ma-ahead=0`.
3. **Casey (mobile):** alvos 44px; recorte 180; tabela Monitor scroll; 1:1 e alinhamento ainda visíveis.

## Strengths

- Clone estrutural de `/combo/results` no index; extra `/monitor` com landmarks; zero galeria ANTES/DEPOIS no canónico.
- Delta mínimo e óbvio: série até 2026-09-12 + clip das médias + chip.
- Aceite Alan (três furos, duas telas, universo, continuidade, intervalos) escrito no contrato visível; P3 de writer/teto 40 não o encolhe.
- #917 intacto no mesmo proto (180, 73↔146, Menos/Resetar).

## Playwright (esta sessão)

- Desktop 1440×900 e mobile 390×844. 0 console error / 0 pageerror com impacto.
- Live `/combo/results` e `/monitor` → `/login` (descartado).
- Análise: landmarks 3/3; default 180; Menos 240; Resetar 180; markerCount 146 estável; 3314 velas; ma-ahead 0.
- Monitor: `table.signals` + 8 textos do catálogo; 15m/1h/4h/1d todos alinhados.
- Disco == HTTPS (index e extra).
- PNGs: `921-A-live-*-desktop.png` (login), `921-A-proto-index-desktop-{default,menos,reset,chart-*}.png`, `921-A-proto-index-mobile-*`, `921-A-proto-monitor-desktop-{default,chart-15m,1h,4h,1d}.png`, `921-A-proto-monitor-mobile-default.png`. JSON `921-A-evidence.json`.

## Priority issues

Nenhum P0/P1 de produto/escopo/contrato visível.

## P0

_(nenhum)_

## P1

_(nenhum)_

## P2

_(nenhum)_

## P3 — detalhe de Apply / clone de região fora do delta

- **P3-1** Writer em observador vs oneshot/timer; env `MARKET_OHLCV_SYMBOL_LIMIT` / teto 40; `DEFAULT_INGESTION_TIMEFRAMES` 15m+1d — já aceito em Apply contract. Não reabrir. Não autoriza cortar pares nem 1h/4h.
- **P3-2** `ChartTimeframe` hoje só `1d` em `chartData.ts` vs picker 15m/1h/4h/1d do Monitor / proto — já aceito.
- **P3-3** Canvas `lightweight-charts` vs SVG do proto — já aceito.
- **P3-4** Timeout exacto em ms; `CURRENT_CHART_CANDLE_LIMIT`; lookback 540 barras 1d — já aceito.
- **P3-5** `mergeStrategyTransparencySeries` no vivo ainda mistura overlay até o presente — o furo a cortar no Apply, não no proto.
- **P3-6** Gráfico do extra Monitor está **inline** sob a tabela; o vivo abre `ChartModal`. Landmarks da tabela cumprem o catálogo; simplificação de proto, não segundo index.
- **P3-7** Extra sem `ScreenHelpPanel` / `MonitorDisclaimer`; coluna expander vazia do vivo ausente; th «Operar» no proto vs th vazio + botão no vivo. Clone de região, não landmark em falta (`Operar` existe).
- **P3-8** Série 15m/1h/4h do mock usa passo diário (eixo Mar–Set); seno em vez de OHLC. Contrato de clip (`ma-ahead=0`) observa-se na mesma. Mock.
- **P3-9** Sem estado visível «snapshot a pintar / série viva a substituir»; par parado (DOGE maio) não teatralizado — evitaria galeria de estados no canónico. Apply.
- **P3-10** «Roda do mouse: zoom» no viewport touch — chrome vivo `StrategyChartSurface`.
- **P3-11** Sem marcadores `DELTA:start/end`; 6+2 COPIED bastam. Higiene de proto.
- **P3-12** Nota de validação do autor («HTTPS 404») ficou datada; nesta sessão HTTPS 200 e digest idêntico. Não é contrato visível.

## Disposition

Aceitar P3 no Apply. Não reabrir P3 como P0/P1. Não exigir segundo rework de Design por estes itens. Tokens, clone da rota `/combo/results`, extra `/monitor`, COPIED>0, delta sem buraco à direita, #917 intacto, aceite Alan não encolhido.

## Verdict

**PASS** — zero P0/P1 de produto/escopo/contrato visível. Tokens parseáveis 3/3 em `/combo/results` (não emprestados; extra `/monitor` não é index). Landmarks index 3/3 e extra `table.signals`+cabeçalhos. Disco == HTTPS. Sem galeria/ANTES-DEPOIS como canónico. copied_utf8_sum index 7302 / extra 3811. Delta = velas/médias alinhadas até 2026-09-12. `/login` descartado. Clone **não** alegado só por sidebar.

`Design Agent verdict` final da coluna = síntese do pai após A+B. Este filho A não chama `process_event`.

---

```
Assessment A 921
tokens_ok: yes
live_route: /combo/results
extra: /monitor (not index)
clone_ok: yes
COPIED: 7302 / 3811
P0: nenhum
P1: nenhum
P2: nenhum
P3: writer/teto40/timeframes; ChartTimeframe 1d; SVG vs lightweight-charts; merge ao vivo; chart Monitor inline vs modal; help/disclaimer; mock seno/passo diário; estados snapshot/parado; Roda do mouse; sem DELTA:start
verdict: PASS
```
