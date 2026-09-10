# Snapshot — Assessment A · card #718 `card-718-monitor-naming-atalho` · T6

- Card: #718 — Monitor: nomes de estado inconsistentes e atalho Cmd+K que não existe
- Change: `card-718-monitor-naming-atalho`
- Critic: Assessment A (isolado; inherit de modelo; sem transcript do pai; sem partilha com B)
- Modelo: inherit
- UTC: 2026-09-08T21:29:17Z
- Round: T6 (Alan devolveu Design: residual r1 só chrome+⌘K era insuficiente)
- Tuple: worktree `/srv/apps/dev/criptofarol/crypto-worktrees/card-718-monitor-naming-atalho` · branch `card-718-monitor-naming-atalho` · HEAD `7580e7baeb2442b7f83bdd3d121fb5995cf95eec` tracking `origin/develop` · change + proto **untracked**. Esta onda só `.impeccable/critique/**`. Não T5. Não `process_event`. Não commit. Não editar `design.md` / proposal / tasks / specs / produto / HTML.
- Digest `design.md` **medido**: sha256 `8e8cb49077d46ecb58f1f63cbf8710aa963de2e2b516d96a6b5cf55dcf33516f` · **913** palavras (`wc -w`)
- Digest prototype `index.html` **medido**: sha256 `9fb0e14144333144c1b80249099e388579a187de27715eefd457cf612f199660` · **24121** bytes — **bate com o digest do prompt**. HTTPS publicado **404** (esperado até restart).
- Digest extra `ajuda.html` **medido**: sha256 `c42327c826f5d8b68614181a779f6d3745866c6af95f7138cda7ab80af1c5972` · **11167** bytes — **bate com o digest do prompt**. HTTPS publicado **404**.
- Copied vs generated (gate `copied_utf8_sum`): index copied **12533** · generated ≈11588 · pares `COPIED:start/end` **2/2**. Extra ajuda copied **4682** · pares **1/1**. `copied > 0`.
- UI impact: **affected** — board `/monitor` (KPI, h3, Status, pill, busca, ScreenHelpPanel) + parágrafo Monitor em `/help`
- Prototype canónico: `frontend/public/prototypes/card-718-monitor-naming-atalho/index.html`
- Extra (irmão, não substitui o index): `frontend/public/prototypes/card-718-monitor-naming-atalho/ajuda.html`
- `live_route: /monitor` · `surface: existing` · `surface_detail: topbar-search, kpis, filterbar, sections-hold-exit, table-signals-status, mobile-card-status, screen-help-panel` (todos parseáveis em linha própria)
- Catálogo HEAD `/monitor`: selectors `table.signals` · texts Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia
- Incumbente: `MonitorStatusTab.tsx` (`⌘K` :1011; KPI tags Compra/Venda :1062–1076; KPI `Em saída` :1071; badge `Estado {cfg.title}` :1168 com `SectionConfig.title` Compra/Venda; Status :1294 `badgeText`); `signalResolution.ts` (`badgeText` Compra/Venda; `markerLabel` Compra/Venda); `OpportunityCard.tsx` pill :259 + `Sinal · {badgeText}` :312; `HelpPage.tsx:42`; `MonitorPage.tsx:9` ScreenHelpPanel
- Rota viva `https://dev.criptofarol.com.br/monitor`: sem sessão → **`/login`** (200, form, **0** `table.signals`). **Não é evidência de clone.** `/login` não foi tratado como `live_route`.
- Method: issue #718 via REST `gh api repos/oalansilva/crypto/issues/718` (body ainda descreve residual r1 / Ajuda a esperar #788 — contrato T6 está em `design.md` + proposal + spec); Playwright Chromium 152 via `/usr/bin/chromium-browser`, viewports 1280×800 e 390×844, HTTP local `http://127.0.0.1:8765/prototypes/card-718-monitor-naming-atalho/` (HTTPS proto 404). Detector CLI / overlay Impeccable ficam com B.
- ignore.md: ausente.
- Classificação D4: só produto/escopo/contrato visível = P0/P1; detalhe de Apply = P3 aceite.

---

## Brief (só neste snapshot)

Quem vê HOLD no Monitor lê **Compra** na pill, no KPI (tag) e na Ajuda — como se fosse «compre agora». Compra no HOLD é posição já confirmada. O residual r1 (KPI+hint; pill e Ajuda ficam Compra/Venda) não entrega um só vocabulário. T6 alarga o nome canónico às superfícies que já mostram HOLD/EXIT: KPI, h3, coluna Status, pill mobile, ScreenHelpPanel, parágrafo Monitor em `/help`. Q1 = apagar ⌘K sem foco. Q2 = não criar entrada potencial. #788 Cancelado.

Audience: operador do beta no `/monitor` (e Alan em T7). Outcome: um nome por estado, busca sem atalho falso. Direction: **Operate** — Binance dark, clone, delta só naming+hint. Scope: duas seções HOLD/EXIT + extra `/help`.

Mode: **Operate**. Extra ajuda: **Read**.

---

## Browser gate (Assessment A — evidência própria)

HTTPS canónico **404** (index e ajuda). Gate em HTTP local, bytes 24121 / 11167 = disco, sha256 = prompt.

Live `/monitor`: redirect a `/login`. Clone = proto + fonte incumbente + catálogo, não pixel autenticado. Gráfico/Spot não estão no proto Monitor — **não é furo** (D2).

Console proto: 0 erros. Request failed: 0. Meta+K / Ctrl+K **não** focam a busca (activeElement = BODY). Tab: Ajuda → search → Telegram → Tema → Atualizar → filtros.

| Assert | 1280×800 | 390×844 |
| --- | --- | --- |
| (a) `table.signals` ×2 + thead Status · Preço · Distância · 7d · Risco até stop · Tags · Par / Estratégia | PASS (thead CSS uppercase; source = catálogo) | `.table-wrap { display:none }`; `table.signals` permanece `display:table` no nó — **não** é galeria |
| (b) `Operar` visível no DOM | PASS · linhas BTC (Abrir Gráfico / Ver Trades / Operar) + ETH/SOL/DOGE/ADA | tabela hidden; cards stub sem Operar (P3 clone) |
| (c) KPI `Em posição` / `Saída / cobertura` / Total / Em carteira; **0** `.kpis .tag`; **0** `Em saída` | PASS | PASS (grelha 2×2; labels não partem) |
| (d) h3 = mesmos nomes (CSS incumbente `text-transform:uppercase` → `EM POSIÇÃO` / `SAÍDA / COBERTURA`) | PASS | PASS |
| (e) 0 badge `Estado Compra/Venda` / `status-section-label` visível | PASS | PASS |
| (f) busca sem `⌘K` / sem `.search .kbd` visível; placeholder intacto | PASS | PASS |
| (g) Status tabela = `Em posição` (×3 HOLD) / `Saída / cobertura` (×2 EXIT); 0 Compra/Venda visível | PASS · pill 86px / 134px, **0 overflow** | n/a visível (wrap none) |
| (h) pill mobile = mesmos nomes; 0 Compra/Venda | cards `display:none` no desktop (paridade ≤740px) | PASS · 3× EM POSIÇÃO + 2× SAÍDA / COBERTURA; 0 overflow |
| (i) ScreenHelpPanel cita canónicos; não ensina Compra/Venda como estado | PASS | PASS (empilha; link Ajuda) |
| (j) extra `ajuda.html` irmão; parágrafo Monitor com canónicos; Spot `comprar / stop / vender` permanece | click Ajuda → `ajuda.html` (não substitui index) | PASS (artigo Monitor) |
| (k) 0 seção entrada potencial; 0 galeria / ANTES-DEPOIS / state-cards / review-bar | PASS | PASS |
| (l) console | PASS | PASS |

Anti-padrões P0 **ausentes**: 0 grelha de N state-cards; 0 painel 6 ecrãs ANTES/DEPOIS como página; página = lista+detalhe (`Em posição` / `Saída / cobertura`) + KPIs + filterbar + ScreenHelpPanel.

Evidência desta onda (só critique): `A-718-desktop-1280-viewport.png`, `A-718-desktop-1280-kpis.png`, `A-718-desktop-1280-search.png`, `A-718-desktop-1280-help.png`, `A-718-desktop-1280-hold-table.png`, `A-718-desktop-1280-exit-table.png`, `A-718-mobile-390-viewport.png`, `A-718-mobile-390-kpis.png`, `A-718-mobile-390-mobile-cards.png`, `A-718-desktop-ajuda-help-monitor-article.png`, `A-718-mobile-ajuda-viewport.png`, `A-718-browser-gate.json`.

---

## Rubrica (item, não rodada extra)

| Item | Resultado |
| --- | --- |
| `UI impact` parseável em linha própria | PASS · `UI impact: affected` |
| `live_route` parseável em linha própria | PASS · `live_route: /monitor` (nunca `/login`) |
| `surface` parseável em linha própria | PASS · `surface: existing` |
| com-tela marca regiões clonadas (`surface_detail`) | PASS · topbar-search, kpis, filterbar, sections-hold-exit, table-signals-status, mobile-card-status, screen-help-panel |
| Landmarks `/monitor` no index | PASS · `table.signals` ×2; 8 texts do catálogo no thead/ações |
| `COPIED:start/end` copied>0 | PASS · 12533 utf8 no index; 2 pares bem fechados |
| Delta só o card | PASS · naming + hint + copy Ajuda; sem terceiro estado; sem redesenho |
| Extra `ajuda.html` não substitui o canónico | PASS · T5 mede o index; extra é clone `/help` |

---

## Findings

### P0 — bloqueante
- nenhum. Landmarks `/monitor` presentes. Não é galeria. Contrato T6 visível no proto (KPI=h3=Status=pill=Ajuda). Busca sem hint. 0 Compra/Venda-como-estado. 0 entrada potencial.

### P1 — deve corrigir antes de PASS
- nenhum.

### P2 — accepted-residual
- [P2] Clone omite AppNav 224px, `MonitorDisclaimer`, spark 7d, expand/kv do `OpportunityCard`, ações no card mobile. `surface_detail` não pede essas regiões; T6 vive nas que estão. **Disposition: accepted-residual.**
- [P2] Pill EXIT `SAÍDA / COBERTURA` (uppercase incumbente) mede 134px vs 86px de `EM POSIÇÃO`. 0 overflow desktop/mobile. Não compete com Compra/Venda. **Disposition: accepted-residual.**
- [P2] ScreenHelpPanel «Use Em posição, Saída / cobertura, contexto…» é troca estrita D4 (antes «Use Compra, Venda…»). Não reescrever o guia. **Disposition: accepted-residual (contrato).**
- [P2] Filtros/search estáticos; Meta+K não foca (Q1). **Disposition: accepted-residual.**

### P3 — detalhe de Apply / polish (não reabrir como P0/P1)
- [P3] CSS órfão produto `.kbd` / `.kpi-label .tag` — **já aceite em `design.md`**. Proto CSS ainda declara `.status-section-label` sem o usar.
- [P3] Remap board: novo campo vs `badgeText` só na renderização — **já aceite**. Apply MUST cobrir pill **e** `Sinal · {badgeText}` (`OpportunityCard.tsx:312`) se essa linha permanecer visível na board; **não** `markerLabel` / ChartModal / Spot (D2).
- [P3] Sample data (contagens/preços/riscos) — **já aceite**.
- [P3] Filterbar proto sem seg admin `Em portfólio`/`Todos` — **já aceite**.
- [P3] Inter no `font-family` sem `@font-face` / link — fallback sistema.
- [P3] 7d = texto percentual, não spark. Thead existe.
- [P3] `ajuda.html` «Ver guia completo» aponta a si próprio (clone estático).
- [P3] Comment HTML dentro de `.search` menciona `kbd`/⌘K — não visível; innerText sem ⌘K.

---

## 1. Fidelidade (rubrica — bloqueante)

- Topologia = lista+detalhe da vista admin: ScreenHelpPanel → topbar/search → KPIs Em posição / Saída / cobertura / Total / Em carteira → filterbar → seções HOLD+EXIT → `table.signals` ×2 → mobile-cards. Tokens `--bg-*` / `--accent` / `--hold` / `--exit` / Inter / `.monitor-theme`. Sem AppNav (P2).
- Landmarks catálogo **todos** no HTML do index.
- Delta = naming canónico + hint apagado + copy Ajuda. Tabela **não** redesenhada. Sem toggle ANTES/DEPOIS.
- 0 elementos de galeria. `mobile-card` = fallback ≤740px, não grelha de estados.

## 2. Produto

- Quem sofre: operador que traduz Compra↔HOLD e tenta ⌘K no Mac.
- Hipótese T6: um vocabulário nas superfícies que já mostram HOLD/EXIT elimina a mentira; r1 era insuficiente.
- Escopo: board + Ajuda de estado. Non-goals (foco teclado, regra HOLD/EXIT, terceiro estado, markerLabel/Spot, redesign) intactos no proto.
- Contrato T6 no proto:
  1. KPI posição == h3 `Em posição`, sem tag. **PASS**
  2. KPI saída == h3 `Saída / cobertura`, sem tag; não `Em saída`. **PASS**
  3. Busca sem hint; sem foco ⌘K. **PASS**
  4. Status tabela + pill mobile canónicos, não Compra/Venda. **PASS**
  5. Ajuda `/help` + ScreenHelpPanel sem ensinar Compra/Venda como estado; Spot `comprar / vender` no extra. **PASS**
  6. HOLD/EXIT inalterado (2 seções, sem entrada). **PASS**
  7. Gráfico/Spot Compra/Venda fora; proto não mostra gráfico. **não é furo**

Vocabulário Avoid: Compra/Venda-como-estado **ausente** no visível. `entrada potencial` **ausente**.

Issue #718 body (REST) ainda fala residual r1 e Ajuda a esperar #788. Não bloqueia o proto: proposal/design/spec já absorvem T6. Apply segue spec, não o parágrafo stale do issue.

## 3. UX

- Hierarquia Depois: help canónico → busca limpa → KPIs alinhados às seções → pills iguais ao h3. Tirar tag Compra/Venda **reduz** a tradução.
- Carga cognitiva (Operate): Single focus OK · Chunking KPIs 4 = limite · Grouping OK · Hierarchy OK · One thing at a time OK · Minimal choices: filtros mortos não competem com o delta · Working memory: o nome está no sítio (não há ponte KPI→pill) · Progressive disclosure: cards mobile stub. **0–1 falhas = baixa** (densidade = produto vivo).
- Acções: Operar / Abrir Gráfico / Ver Trades no sítio da tabela; Ajuda abre o irmão `/help`.
- Emocional: pico = ler `Em posição` no KPI **e** na pill da mesma linha. Vale = incumbente Compra no HOLD. Fecho EXIT `Saída / cobertura` honesto.

## 4. A11y

- Teclado: search é `<input>` dentro de `<label>`; Tab aterra em Ajuda → busca → chrome. Sem trap. ⌘K não faz nada (Q1). `focus-within` no `.search` (accent-line).
- Nomes: pills têm texto (não só cor hold/exit). Help `aria-label="Como usar o Monitor"`.
- Contraste medido: pill HOLD `#0ecb81` / `#181a20` ≈ **8.18:1** AA; pill EXIT `#f6465d` / `#181a20` ≈ **4.93:1** AA (10.5px bold, incumbente); KPI label `#929aa5` ≈ **6.12:1**; help tertiary ≈ **5.56:1**; accent `#fcd535` ≈ **13.55:1**.
- Significado não só por cor: pip + texto h3 + pill com nome.
- Touch: pills 20px altura — paridade produto (não 44px; P3 herdado, non-goal).
- CSS `text-transform:uppercase` no h3 e na pill = incumbente (`index.css` `.status-row h3` / `.status-pill`). DOM = `Em posição` / `Saída / cobertura`. SR lê o source.

## 5. Responsive

- 1280×800: tabela visível, mobile-cards `display:none`, KPIs 4 col, Operar visível, EXIT `SAÍDA / COBERTURA` cabe na coluna Status.
- 390×844: topbar wrap, search 100%, KPIs 2×2, `.table-wrap` none, 5 `.mobile-card` em grelha 1 col, ScreenHelpPanel coluna, Ajuda no fluxo. Não é galeria 2×2 — é o fallback ≤740px do produto.
- KPI `Saída / cobertura` não parte linha na coluna estreita.

## 6. Estados

| Estado | Superfície | Proto T6 | Incumbente vivo |
| --- | --- | --- | --- |
| HOLD | KPI + h3 + Status + pill | `Em posição` | KPI `Em posição`+tag Compra; h3 `Em posição`; badge `Estado Compra`; pill Compra |
| EXIT | KPI + h3 + Status + pill | `Saída / cobertura` | KPI `Em saída`+tag Venda; h3 `Saída / cobertura`; badge `Estado Venda`; pill Venda |
| Busca | `.search` | sem `.kbd` | `<span className="kbd">⌘K</span>` sem listener |
| Ajuda monitor | ScreenHelpPanel + `/help` | canónicos | Compra, Venda como estados |
| Spot / gráfico | ausente no proto Monitor | fora (D2) | `markerLabel` Compra/Venda |
| Entrada potencial | — | **não criada** | #788 Cancelado |

---

## Heurísticas Nielsen (arquivo; não emitir no chat do pai)

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 4 | KPI = seção = pill; 0 tag divergente |
| 2 | Match System / Real World | 4 | Vocabulário operacional; Compra-como-estado some |
| 3 | User Control and Freedom | 3 | Ajuda navega; filtros estáticos |
| 4 | Consistency and Standards | 3 | Um vocabulário no delta; clone omite AppNav |
| 5 | Error Prevention | 4 | Sem hint falso; sem «compre agora» no HOLD |
| 6 | Recognition Rather Than Recall | 4 | Nome no sítio; sem tradução mental |
| 7 | Flexibility and Efficiency | 2 | Proto estático; Q1 sem atalho (decisão) |
| 8 | Aesthetic and Minimalist Design | 3 | Binance dark; pill EXIT mais larga, cabe |
| 9 | Error Recovery | 2 | Happy path estático; empty/stale não no recorte T6 |
| 10 | Help and Documentation | 4 | Painel + `/help` irmão com a mesma troca |
| **Total** | | **33/40** | **Good** |

Design specificity: **alta** — não serve a outro produto sem o Monitor Cripto Farol (HOLD/EXIT, pares, Operar, tokens Binance).

### Personas
- **Alex (power user Monitor):** ⌘K some — alinhado a Q1; não é P0. Nomes canónicos na coluna Status aceleram o scan. Red flag residual: clone sem atalhos de produto (Tema/Atualizar mortos).
- **Jordan (primeira leitura):** ScreenHelpPanel e `/help` deixam de ensinar Compra/Venda como estado. «Use Em posição…» é D4, não um terceiro tutorial.
- **Casey (mobile 390):** pills legíveis, 0 overflow, KPIs 2×2. Cards stub sem Operar = P3 clone, não furo de naming.
- **Trader beta HOLD:** deixa de ver Compra na pill da posição confirmada.

### Strengths
1. Delta T6 visível no mesmo sítio do incumbente (KPI, h3, Status, pill, help) — não é folha de tokens nem galeria ANTES/DEPOIS.
2. Extra `/help` é clone irmão; Spot `comprar / vender` preservado; index continua canónico.
3. Um vocabulário fecha o furo que o r1 deixava na pill e na Ajuda.

---

## Disposition

- P0/P1: 0 abertos.
- P2/P3: aceitos como residual de clone, troca estrita, ou detalhe de Apply já registado em `design.md`.
- Determinísticos: asserts Playwright que falharam por `text-transform:uppercase` (innerText `EM POSIÇÃO`) são **falsos positivos** — source/DOM = nomes canónicos; paridade CSS vivo. Landmark «missing» no snippet de 800 chars = falso positivo; thead completo no `tableInfo`.
- Detector/overlay: fora desta onda (B).

Não há re-despacho de autor por P0/P1 de produto. Teto com-tela: autor + dupla + 1 rework; sem P0 novo justificado, o pai publica P3 aceitos e submete.

---

## Verdict

**APROVAR-COM-P3** — zero P0/P1, fidelidade lista+detalhe `/monitor`, landmarks presentes, tokens parseáveis, copied>0, delta T6 observável (KPI=h3=Status=pill=Ajuda; busca sem ⌘K; 0 entrada; 0 galeria), extra `ajuda.html` irmão, browser gate próprio em HTTP local (HTTPS 404). P3 = Apply (órfãos CSS, remap `badgeText` incluindo `Sinal ·` na board, sample, filterbar admin) + polish de clone.

---

## Snapshot

`.impeccable/critique/718-card-718-monitor-naming-atalho-T6-A.md`

Prototype local: `http://127.0.0.1:8765/prototypes/card-718-monitor-naming-atalho/` · sha256 `9fb0e14144333144c1b80249099e388579a187de27715eefd457cf612f199660`  
Extra: `…/ajuda.html` · sha256 `c42327c826f5d8b68614181a779f6d3745866c6af95f7138cda7ab80af1c5972`
