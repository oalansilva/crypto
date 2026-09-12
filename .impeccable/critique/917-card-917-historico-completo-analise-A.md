# Assessment A — card 917 · change card-917-historico-completo-analise

> Avaliador A isolado (produto / UX / a11y / fidelidade do clone). Mesmo modelo do chat. Sem transcript do pai. Sem nested-spawn. Sem edição de `design.md`, HTML proto, `backend/`, `frontend/src/` ou OpenSpec. Sem `process_event`. Única escrita: este arquivo + PNGs `917-A-*`.

## Metadata

- card: 917 — histórico completo na análise (`/combo/results`)
- change: `card-917-historico-completo-analise`
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-917-historico-completo-analise`
- branch: `card-917-historico-completo-analise`
- data (UTC): 2026-09-12T18:35Z
- Status observado: Design
- UI impact (rubrica): **affected** · `live_route: /combo/results` · `surface: existing` — linhas próprias 13–15 de `design.md` (parseáveis; **não** `/favorites` nem `/combo/select`)
- Digest proto (disco, verificado nesta sessão): sha256 `3f4b61913528622ecb87ca57ef6ae1e7cda1a89b835d6f05bc6bdb72b141db38` · 32754 bytes
- Servido HTTPS == local: IDENTICAL (`cmp` limpo)
- Issue: https://github.com/oalansilva/crypto/issues/917
- D4: com-tela = autor + dupla + 1 rework. Tokens verificados como item da rubrica — nenhuma rodada extra só para o parser.
- Snapshot do autor lido: `.impeccable/critique/917-card-917-historico-completo-analise-autor-2026-09-12.md`
- Ignore list: `.impeccable/critique/ignore.md` ausente.
- Catálogo T5 (worktree): `/combo/results` → `selectors: [".combo-page"]`, `texts: ["Lista de operações", "Análise da estratégia"]`

## Limitação de sessão (obrigatória)

Inspeção visual desta sessão = Playwright Chromium 1243 (`executable_path` cache `chrome-linux-arm64`), HTTPS real, viewports 1440×900 e 390×844, `colorScheme: dark`. 0 console error / 0 pageerror.

| URL pedida | URL final | h1 | Landmarks `/combo/results` |
|---|---|---|---|
| `https://dev.criptofarol.com.br/combo/results` | `https://dev.criptofarol.com.br/login` (HTTP 200) | `Bem-vindo de volta` | 0/3 |

**`/login` não é a rota.** Chrome de login **não** é evidência de clone e **não** autoriza PASS de fidelidade. Sem cookie de administrador, a avaliação de clone usa: (1) protótipo canónico HTTPS, (2) HTML local, (3) fonte viva `ComboResultsPage.tsx` / `StrategyChartSurface.tsx` / `StrategyTradesTable.tsx` vs catálogo `scripts/process-fsm/route-landmarks.yaml`. Sidebar 224px / tokens `--bg-*` **não** bastam.

## Tokens parseáveis (rubrica D4)

`design.md` linhas próprias 13–15:

```
UI impact: affected
live_route: /combo/results
surface: existing
```

Regiões clonadas marcadas na linha seguinte: shell AppNav; chrome `/combo/results` (`.combo-page`, «Voltar aos favoritos», `aria-label="Análise da estratégia"`, chips, resumo, regras); chrome do gráfico (Menos / Mais / Resetar, «180 velas»); chrome da «Lista de operações»; disclaimer.

**PASS** deste item: chaves em linha própria; rota do catálogo desta tela; **não** empresta `/favorites` nem `/combo/select` (`.combo-page` no select é coincidência de classe, não `live_route`).

## Digest proto (disco == HTTPS)

| Ponta | sha256 | bytes | HTTP |
|---|---|---|---|
| disco `frontend/public/prototypes/card-917-historico-completo-analise/index.html` | `3f4b61913528622ecb87ca57ef6ae1e7cda1a89b835d6f05bc6bdb72b141db38` | 32754 | — |
| HTTPS `https://dev.criptofarol.com.br/prototypes/card-917-historico-completo-analise/` | `3f4b61913528622ecb87ca57ef6ae1e7cda1a89b835d6f05bc6bdb72b141db38` | 32754 | 200 |

`cmp` disco vs `/tmp/card917-proto.html`: identical. `design.md` Prototype: 6 pares COPIED, 7175 bytes copiados, 25579 gerados, 32754 totais — bate com o disco.

## Fidelidade (clone da página viva)

Catálogo `/combo/results` (`scripts/process-fsm/route-landmarks.yaml` no worktree): `selectors: [".combo-page"]` · texts `Lista de operações`, `Análise da estratégia`.

| Landmark | Vivo (`ComboResultsPage.tsx` / tabela / chart) | Proto + Playwright (desktop e mobile) |
|---|---|---|
| `.combo-page` | `className="app-page combo-page …"` | visível, count=1 |
| `Lista de operações` | `StrategyTradesTable` heading | tab/heading visível; `#trades-window-label` |
| `Análise da estratégia` | `aria-label="Análise da estratégia"` | região visível |
| Chrome extra (não catálogo, clone) | «Voltar aos favoritos»; Menos/Mais/Resetar; «N velas»; `aria-label="Controles de zoom do grafico"` | todos visíveis no default |

Anti-padrões P0:

- URL canónica `…/prototypes/card-917-historico-completo-analise/` → index **é** a página de análise (AppNav + `.combo-page` + resumo + gráfico + lista). **Não** é painel ANTES/DEPOIS. Botões Antes/Depois visíveis = 0. Texto visível `ANTES/DEPOIS` = 0 (único hit é comentário de fonte «NÃO é painel ANTES/DEPOIS» — não conta como galeria).
- Não é grelha de N estados no lugar de lista+detalhe. Uma análise, uma lista, um gráfico.
- 6 pares `COPIED:start/end` (copied > 0). Delta óbvio = setas da lista completa + chip `Lista 73 · Setas 146 (entrada+saída) · 1:1` + zoom que revela 2017. Sem `DELTA:start` no markup (P3 de marcação, não de produto).
- Monitor ao vivo fora: 0 cards de oportunidade; nav Monitor só no shell.

Chrome presente (sidebar 224px desktop, Inter/Binance, Combo ativo, amarelo `#fcd535`) = **folha**, não prova. Prova = landmarks 3/3 no proto, alinhados ao TSX.

## Produto (aceite visível)

Contrato do card: lista completa; gráfico 1:1 com a lista (setas na série inteira); zoom inicial ~180 velas; Menos/arrastar revela setas antigas; Resetar não apaga a série; não forçar todas as velas ao abrir; Monitor ao vivo fora.

| Aceite visível | Evidência (Playwright 1440×900 e 390×844) | Disposition |
|---|---|---|
| Lista completa | 73 operações fechadas; 146 linhas (entrada+saída); cards mobile 73; primeira = #73 Jul 10 2026, última = #1 Oct 5 2017 | OK |
| 1:1 lista↔setas | chip `Lista 73 · Setas 146 (entrada+saída) · 1:1`; `data-list-count=73`; `data-marker-count=146`; após Menos: 73 Compra + 73 Venda no SVG | OK |
| Recorte recente ao abrir | «180 velas»; eixo `2026-01`–`2026-09`; seta `2017-10-05` ausente; seta `2026-07-10` presente; 12 marcadores visíveis (rótulos ligados, n≤260) | OK |
| História antiga na série | 9× Menos → «2367 velas»; eixo `2017-08`–`2026-09`; `data-time=2017-10-05` visível; 146 marcadores; rótulos off (n>260) | OK |
| Resetar não apaga série | «180 velas» de novo; 2017 oculta do viewport; `data-marker-count` continua 146; chip 1:1 intacto | OK |
| Não forçar todas as velas ao abrir | default ≠ 2367; série no subtítulo continua `BTC/USDT • 1d • 2367 velas` | OK |
| Resumo Operações = fechadas | métrica **73** = 73 linhas de operação fechada | OK |
| Monitor ao vivo fora | 0 cards Monitor; sem `signal_history` a encurtar setas no proto | OK |

Origem viva ainda furada (Apply, não o proto): `ComboResultsPage.tsx` ainda prefere `buildSignalHistoryMarkers(signalHistory)` quando o array tem itens — exactamente o delta a implementar. O proto já mostra o depois.

## UX

Hierarquia: AppNav → Voltar → resumo (h1 estratégia + 4 métricas) → Regras → gráfico (toolbar + série) → Lista de operações. Job único: conferir cada entrada/saída no mesmo período das velas.

Carga: chip 1:1 tira a dúvida «o gráfico está quebrado?». Default 180 velas evita milhares de barras ilegíveis. Progressive disclosure: setas antigas só depois de Menos/pan. No zoom afastado os rótulos somem e os triângulos ficam (decisão de densidade do design).

Delta óbvio sem redesign de layout: o chip verde e as setas 2017 após Menos.

## Acessibilidade

- `lang=pt-BR`; `:focus-visible` no CSS; `prefers-reduced-motion`.
- Landmarks: `nav` + `main`; `aria-label="Análise da estratégia"`; zoom `role`/group `Controles de zoom do grafico`; botões com `aria-label` Reduzir/Aumentar/Redefinir.
- Alvos: Menos 94×44, Mais 81×44, Resetar 101×44 (desktop e mobile).
- Compra/Venda não só por cor: triângulo cima/baixo + rótulo no recorte apertado + linhas da lista.
- Tab «Lista de operações» nomeada. Disclaimer educacional presente.
- Teclado: botões reais de zoom; arrastar no stage é extra (wheel/pan) — equivalente Menos/Mais/Resetar existe (não é drag-only).

## Responsividade

- Desktop 1440×900: sidebar 224px; tabela visível (146 linhas); `#trades-mobile` `display:none`. Overflow-x = 0. PNGs `917-A-desktop-{default,menos,resetar,chart-*,lista}.png`.
- Mobile 390×844: sidebar 0; header 72px; cards 73 visíveis; tabela `w/h=0`; zoom 44px; chip 1:1 wrap em 324px. Overflow-x = 0. PNGs `917-A-mobile-*`.
- «Roda do mouse: zoom» no mobile é **clone** de `StrategyChartSurface.tsx` (chrome vivo também mostra). Não é delta deste card.

## Estados

Mock: BTC/USDT 1d, 73 fechadas, 0 abertas, zoom default / out / reset. Não mocka: operação aberta, outro ativo/timeframe, loading/erro da análise, vazio. Cobertura de mock = P3 (o contrato «qualquer ativo» é Apply na mesma tela, não segundo index).

## Design specificity

A tela é a análise do Cripto Farol (Médias Móveis / Favoritos → resultados), não um dashboard genérico de candles. Modo Impeccable: **Operate** / refinement. Folha Binance; `DESIGN.md` não reescrito.

## Heurísticas Nielsen (0–4, Operate; só neste snapshot)

| # | Heurística | Score | Nota |
|---|---|---|---|
| 1 | Visibility of system status | 4 | 180/2367 velas + chip 1:1 + setas visíveis vs série |
| 2 | Match between system and real world | 4 | Compra/Venda, lista, velas, Operações 73 |
| 3 | User control and freedom | 4 | Menos / Mais / Resetar / pan; Resetar não destrói história |
| 4 | Consistency and standards | 4 | Chrome vivo + tokens; «Saida» sem acento = tabela viva |
| 5 | Error prevention | 4 | Não abre em fit-all; não corta série |
| 6 | Recognition rather than recall | 4 | Chip 1:1; lista e gráfico na mesma página |
| 7 | Flexibility and efficiency | 3 | Zoom/pan; proto sem troca de ativo (Apply) |
| 8 | Aesthetic and minimalist design | 3 | Lista longa de propósito; rótulos mobile no default 180 sobrepõem um pouco |
| 9 | Help users recognize/recover errors | n/a | Sem formulário neste fluxo |
| 10 | Help and documentation | 3 | Disclaimer educacional; Ajuda no nav |
| **Total** | | **33/36** | **Good** (heurística 9 n/a) |

## Cognitive load

Checklist: um job; chunking resumo → gráfico → lista; chip reduz memória. **Pass** (0–1 falhas). Decisão no open: nenhuma (default já é o recorte certo). Decisão depois: Menos vs Resetar (≤4).

## Emotional journey

Vale (lista longa, gráfico «só 2026») → pico (Menos revela 2017, chip continua 146) → fim (Resetar volta a ler velas sem perder a história). Reassegurança: Operações 73 não muda.

## Personas

1. **Alex (operador da análise):** confere 73 linhas e vê 146 setas na série; 9 cliques em Menos bastam para 2017-10-05.
2. **Riley (stress do recorte):** Resetar não dropa `data-marker-count`; default não é fit-all.
3. **Casey (mobile):** alvos 44px; cards 73; setas visíveis no zoom out; «Roda do mouse» é chrome herdado.

## Strengths

- Clone estrutural de `/combo/results`, não galeria ANTES/DEPOIS.
- Delta mínimo e óbvio: setas da lista completa + chip 1:1.
- Aceite observável no browser: 180 → 2367 → 180, série 146 estável.
- Non-goals visíveis respeitados (Monitor, Descoberta, Excel extra, fit-all).

## Playwright (esta sessão)

- Desktop 1440×900 e mobile 390×844: estado padrão + 9× Menos até seta `2017-10-05` + Resetar. Landmarks 3/3. 0 console / 0 pageerror.
- Live `/combo/results` → `/login` (descartado).
- PNGs: `917-A-desktop-{default,menos,resetar,chart-default,chart-menos,chart-resetar,lista}.png`, `917-A-mobile-{default,menos,resetar,chart-default,chart-menos,lista}.png`.

## Priority issues

Nenhum P0/P1 de produto/escopo/contrato visível.

## P0

_(nenhum)_

## P1

_(nenhum)_

## P2

_(nenhum)_

## P3 — detalhe de Apply / clone de região fora do delta

- **P3-1** Canvas `lightweight-charts` vs SVG do proto — já aceito em `design.md` Apply contract. Não reabrir.
- **P3-2** MAE/MFE / valor da posição / acumulado como `—` no proto; tabela viva calcula USD/%. Apply lê `StrategyTradesTable.tsx`.
- **P3-3** Nomes internos `buildTradeMarkers` / `signal_history` (origem das setas) — já aceito; TSX vivo ainda tem o furo.
- **P3-4** Cards mobile no DOM desktop (`display:none`) e tabela no DOM mobile (`w/h=0`) — clone de densidade, não contrato.
- **P3-5** Sem marcadores `DELTA:start/end`; 6 COPIED bastam para o clone. Marcação é higiene de proto.
- **P3-6** Rótulos Compra/Venda no default 180 velas sobrepõem um pouco no mobile 356px; triângulos + chip + lista continuam 1:1. Densidade já decidida (rótulo ≤260).
- **P3-7** Mock só BTC/USDT 1d fechadas; «qualquer ativo/timeframe» e operação aberta = Apply na mesma rota, não segundo index.
- **P3-8** «Roda do mouse: zoom» no viewport touch — chrome vivo `StrategyChartSurface`, não delta.

## Disposition

Aceitar P3 no Apply. Não reabrir P3 como P0/P1. Não exigir segundo rework de Design por estes itens. Tokens e clone da rota `/combo/results` estão no sítio.

## Verdict

**PASS** — zero P0/P1 de produto/escopo/contrato visível. Tokens parseáveis 3/3 em `/combo/results` (não emprestados). Landmarks 3/3 no proto. Disco == HTTPS. Sem galeria/ANTES-DEPOIS como index. copied > 0 (6 pares). Delta = setas da lista completa + 1:1 observável. `/login` descartado. Clone **não** alegado só por sidebar: prova = landmarks proto × catálogo `/combo/results` × chrome `ComboResultsPage`.

`Design Agent verdict` final da coluna = síntese do pai após A+B. Este filho A não chama `process_event`.

---

```
Assessment A 917
tokens_ok: yes
live_route: /combo/results
clone_ok: yes
P0: nenhum
P1: nenhum
P2: nenhum
P3: SVG vs lightweight-charts; MAE/MFE —; buildTradeMarkers/signal_history; cards mobile hidden no desktop; sem DELTA:start; rótulos mobile 180 apertados; mock BTC 1d; «Roda do mouse» clone
verdict: PASS
```
