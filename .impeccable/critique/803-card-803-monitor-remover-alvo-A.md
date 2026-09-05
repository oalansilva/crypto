# Snapshot — Assessment A · card #803 `card-803-monitor-remover-alvo`

- Card: #803 — Monitor — remover alvo derivado do card
- Change: `card-803-monitor-remover-alvo`
- Critic: Assessment A (isolado; inherit de modelo; sem transcript do pai; sem partilha com B)
- Modelo: inherit
- UTC: 2026-09-03T23:06:00Z
- Round: 1
- Tuple: worktree `/srv/apps/dev/criptofarol/crypto-worktrees/card-803-monitor-remover-alvo` · branch `card-803-monitor-remover-alvo` · HEAD `0ebf55ea` tracking `origin/develop` · change + proto **untracked**. Esta onda só `.impeccable/critique/**`. Não T5. Não commit. Não editar `design.md` / proposal / tasks / specs / produto / HTML.
- Digest `design.md` **medido**: sha256 `8eac80feef2f0beeaeaa3d0ccee0903884bbad3e53e586312e02ea1ec046fc1d` · **746** palavras (`wc -w`)
- Digest prototype `index.html`: sha256 `24fc626805ebbb3561f4cc3fbf45c0572e00a520b306a24274ce9e49cf2bb92d` · **103142** bytes — **bate com o digest do prompt e com HTTPS publicado**
- Copied vs generated (autor): copied 82027 · generated 21115 (`copied_utf8_sum` > 0)
- UI impact: **affected** — kv HOLD + painel de risco do modal (`OpportunityCard.tsx`, `ChartModal.tsx`); tela já existe: `/monitor`
- Prototype: `frontend/public/prototypes/card-803-monitor-remover-alvo/index.html` → `https://dev.criptofarol.com.br/prototypes/card-803-monitor-remover-alvo/`
- `live_route: /monitor` · `surface: existing`
- Catálogo `/monitor`: selectors `table.signals` · texts Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia
- Incumbente: `MonitorStatusTab.tsx` + `OpportunityCard.tsx` (ainda tem `alvoPrice` / `<dt>alvo`) + `ChartModal.tsx` (`chartAlvoPrice` / row `Alvo` ~L791) + `.monitor-theme`
- Rota viva `https://dev.criptofarol.com.br/monitor`: sem sessão → `/login` (ou SPA no path `/monitor` com form, **0** `table.signals`). **Não é evidência de clone.** `/login` não foi tratado como `/monitor`.
- Method: issue #803 body (DoD + aceite 1–5 + vocabulário); `proposal.md` Why/What; `design.md` D1–D5 + Apply contract; delta `specs/opportunity-monitor/spec.md`; Playwright Chromium 1280×800 e 390×844 na URL publicada; toggle Antes/Depois exercitado; modal SOL/ETH/ADA/LINK; asserts de tabela/kv/copy. Detector CLI e overlay Impeccable ficam com B.
- ignore.md: ausente.

---

## Brief (só neste snapshot)

Quem vê HOLD no Monitor lê **alvo** como preço de operação, mas é `last_price × (1 ± dist/100)` no frontend — não é TP nem ordem. Compete com stop e distâncias. Card #803: tirar rótulo/valor `alvo` no card **e** no modal; ordem `distância até saída` → `distância até stop` → `stop` → `entrada` → `preço atual`; manter `indisponível — dado não confiável`, frase de cenário e EXIT residual; sem linha escondida / tooltip / número equivalente no produto. Proto = clone da página `/monitor` (não galeria, não painel 6 ecrãs ANTES/DEPOIS). Antes = vivo com alvo; Depois = sem alvo. Toggle MUST mudar markup.

Audience: trader do beta no `/monitor` (e Alan em T7). Outcome: olhar HOLD e ver risco real. Direction: Operate — Binance dark, clone, delta só no kv/modal. Scope: 4 linhas (SOL HOLD, ETH stale, ADA EXIT vazio, LINK EXIT residual) + recorte de risco do modal.

Mode: **Operate**.

---

## Browser gate (Assessment A — evidência própria)

URL publicada **200**, bytes 103142, sha256 `24fc6268…`. Console proto: 0 erros. Request failed: 0. HTTPS = disco.

Live `/monitor`: redireciona a `/login` sem sessão (segunda carga); primeira carga SPA pode ficar no path `/monitor` com form e **0** `table.signals`. Clone = proto + fonte incumbente + catálogo, não pixel autenticado.

| Assert | 1280×800 Depois | 390×844 Depois |
| --- | --- | --- |
| (a) `table.signals` ×2 + thead Status · Preço · Distância · 7d · Risco até stop · Tags · Par / Estratégia | PASS | `.table-wrap { display:none }` (CSS vivo ≤740px); `table.signals` permanece `display:table` no nó — **não** é galeria |
| (b) `Operar` visível | PASS · 12 ocorrências no DOM · linha SOL com Abrir Gráfico / Ver Trades / Operar | 4 `.mobile-card` · sidebar `none` |
| (c) linha SOL Compra · `$105.39` · `13.38%` · `35.21%` stop · Médias Móveis · Carteira · ★★★ | PASS (primeiro viewport da tabela) | n/a thead; cards abaixo dos KPIs |
| (d) ETH `indisponível — dado não confiável` ×4 + preço; **sem** dt `alvo`; ADA residual exacta; SOL «cruzar $68.28» | PASS | PASS (mesmos nós) |
| (e) Toggle muda markup: Antes SOL dt inclui `alvo` `$119.48`; Depois ordem 5 dts sem `alvo`; `data-prototype-variant` + `aria-pressed` | PASS (não morto) | PASS |
| (f) Modal SOL Depois: row Alvo não visível; ordem saída → stop% → Stop → Entrada → Preço atual; cenário presente | PASS | modal `width` cabe em 390; recorte igual |
| (g) Modal ETH stale sem Alvo visível; ADA/LINK = preço + Risco residual, hold hidden | PASS | — |
| (h) console | PASS | PASS |

Anti-padrões P0 **ausentes**: 0 grelha de N state-cards; 0 painel 6 ecrãs ANTES/DEPOIS como página; página = lista+detalhe (`Em posição` / `Saída`) + KPIs + filterbar.

Evidência desta onda (só critique): `A-803-desktop-1280-depois.png`, `A-803-desktop-1280-antes.png`, `A-803-table-1280-depois.png`, `A-803-modal-sol-depois.png`, `A-803-mobile-390-depois.png`, `A-803-mobile-390-list.png`, `A-803-browser-gate.json`.

---

## Findings

### P0 — bloqueante
- nenhum. Landmarks `/monitor` presentes. Não é galeria. Toggle altera innerHTML do kv e `hidden` da row do modal.

### P1 — deve corrigir antes de PASS
- nenhum.

### P2 — accepted-residual ou polish recomendado
- [P2] Default: as 4 `head-row` vêm `expanded`. Em 1280×800 o primeiro viewport é review-bar + KPIs + thead + linha SOL; o kv HOLD (prova do delta) exige scroll. Em 390×844 o primeiro viewport é KPIs empilhados (`firstCardY≈1008`). Intencional para T7 ver 4 estados; polish: só SOL expandida no load. **Disposition: accepted-residual.**
- [P2] Modal Depois mantém `<div class="chart-kv-row" data-alvo-row hidden>` com `$119.48` no DOM/JS (`CHART.sol.alvo`, `KV.*.before`). Visual Depois **não** mostra. Contrato D3 do proto (toggle). Aceite 5 / Apply: **apagar** a row em `ChartModal.tsx`, não CSS-hide. **Disposition: accepted-residual (proto); Apply MUST delete.**
- [P2] Overlay do gráfico é recorte (`Painel do gráfico (recorte de risco)`), não clone pixel do `ChartModal` (OHLC/candles). Aceite 2 = bloco de risco igual ao card — coberto. **Disposition: accepted-residual.**
- [P2] `.row-actions { min-width: 0 }` herdado da base #792: ações empilham. Non-goal: não redesenhar tabela. **Disposition: accepted-residual.**
- [P2] Residual LINK («último EXIT em $14.82 · exposição residual 4.10%…») é fixture. Apply usa `signal_history` real. **Disposition: accepted-residual.**

### P3 — melhoria menor
- [P3] Coluna 7d = `-` (sem spark). Thead existe.
- [P3] `data-testid` duplicados (mobile-card + detail-row). QA precisa `.nth` / visible.
- [P3] Modal: sem trap de foco, sem Escape (só Fechar + clique no overlay). `role="dialog"` + `aria-modal` + `aria-labelledby` presentes.
- [P3] `aria-label` do `.row-toggle` fica «Expandir» mesmo aberto.
- [P3] Frase de cenário traz sufixo «segundo a estratégia (stop)» (copy #792). Issue escreve `Se o preço cruzar $X…`. Non-goal mudar copy da frase.
- [P3] Filtros/KPI/search estáticos — esperado em HTML.
- [P3] ETH Antes ainda tem dt `alvo` + literal indisponível (= vivo). Depois remove a linha — correcto.

---

## 1. Fidelidade (rubrica — bloqueante)

- Topologia = lista+detalhe da vista admin: KPIs Em posição/Em saída/Total/Em carteira, filterbar, secções Em posição e Saída, `table.signals` ×2, status-row, mobile-cards, shell AppNav 224px, Monitor `aria-current`, tokens `--bg-*` / `--accent-primary` / `--text-*` / `--border-default`, Inter, `.monitor-theme`.
- Landmarks catálogo **todos** no HTML publicado: `table.signals`; textos Status, Preço, Distância, 7d, Risco até stop, Tags, Operar, Par / Estratégia (contagens Playwright: 2 / 17 / 14 / 2 / 2 / 2 / 12 / 2).
- Delta = kv HOLD sem `alvo` + modal sem Alvo visível + JS Antes/Depois. Tabela **não** redesenhada.
- Antes = clone do kv vivo (`OpportunityCard.tsx` L427–439 ainda tem `alvo` entre stop e entrada). Depois = aceite 1.
- Toggle **não está morto**: `aria-pressed` **e** innerHTML / `data-prototype-variant` / `hidden` na row Alvo.
- 0 elementos de galeria 2×2 / 6 ecrãs. `monitor-card` = OpportunityCard de produto (desktop+mobile), não grelha de estados.

## 2. Produto

- Quem sofre: trader HOLD no Monitor (beta) que calibra risco olhando o card; Alan no T7.
- Hipótese: tirar o derivado que parece TP restaura confiança no stop/distâncias.
- Escopo: card + modal, mesma ordem, sem cálculo `alvoPrice`/`chartAlvoPrice`. Spec MODIFIED para o Apply não reintroduzir. Non-goals (Kelly, Binance stop, Telegram, redesign tabela, terceiro status) intactos.
- Aceite 1–5 no proto Depois:
  1. HOLD SOL: 5 dts na ordem, sem `alvo`. **PASS**
  2. Modal SOL: mesmo recorte visível, sem Alvo. **PASS** (chrome do gráfico = placeholder)
  3. HOLD ETH stale: indisponível nos campos afetados; **sem** linha alvo/«alvo indisponível». **PASS**
  4. EXIT ADA/LINK: `preço atual` + `Risco residual`; sem entrada/stop operáveis; sem `alvo`. **PASS**
  5. Depois visível sem número equivalente; proto guarda string só para Antes/toggle. Apply apaga cálculo. **PASS visual; residual P2 no DOM hidden**

Vocabulário: Distância / Stop / entrada / preço atual / indisponível — dado não confiável / HOLD / EXIT / Risco residual. Avoid TP/preço-alvo não aparece na UI Depois.

## 3. UX

- Hierarquia Depois: badge Compra/Venda → distâncias → stop → entrada → preço → frase cenário (só SOL) → residual só EXIT. Tirar alvo **reduz** uma linha falsa no bloco de risco.
- Carga cognitiva (Operate): Single focus falha (4 expands) · Chunking: kv HOLD 5 linhas (melhor que 6) · Grouping OK · Hierarchy OK · One thing at a time falha · Minimal choices: toggle 2 OK · Working memory: labels no sítio · Progressive disclosure falha no default. **2–3 falhas = moderada** (intencional T7).
- Acções: Operar / Abrir Gráfico / Ver Trades no sítio da tabela; Abrir Gráfico abre o recorte. Filtros mortos não competem com o delta.
- Emocional: pico = caixa «Se o preço cruzar $68.28…» + ausência do `$119.48` que fingia TP. Vale = Antes com alvo. Fecho EXIT honesto.

## 4. A11y

- Teclado: toggle é `<button>` com `aria-pressed` e `role="group"` `aria-label="Variante do protótipo"`; Tab aterra no Depois (`data-variant=after`); `.row-toggle` e Fechar são botões; `focus-visible` 2px `--accent-cyan`.
- Nomes: Operar/Abrir Gráfico com `aria-label` por par; dialog `aria-labelledby="chart-modal-title"`.
- Contraste medido: indisponível `#929aa5` / `#181a20` ≈ **6.12:1** AA; toggle on `#fcd535` / `#0b0e11` ≈ **13.6:1**; texto primário ≈ 16.4:1.
- Significado não só por cor: pill tem texto; indisponível é literal itálico; Alvo some de verdade no Depois (não só cinza).
- Modal: `hidden` na row Alvo tira de AT. Falta trap/Escape = P3, não bloqueia o delta.
- Touch: Operar tabela ~30px — paridade produto.

## 5. Responsive

- 1280×800: sidebar 224px, tabela visível, mobile-cards `display:none`, KPIs 4 col, Operar visível (empilhado — P2 herdado).
- 390×844: sidebar none, `.table-wrap` none, 4 `.mobile-card` em grelha 1 col, kv `word-break`, modal `min(440px, calc(100vw - 24px))` cabe. Não é galeria 2×2 — é o fallback ≤740px do produto.
- Copy longa ETH/LINK parte linha; legível.

## 6. Estados

| Estado | Par | Depois | Antes (vivo com alvo) |
| --- | --- | --- | --- |
| HOLD confiável | SOL | 5 dts sem alvo; cenário `$68.28`; modal igual | 6 dts com `alvo $119.48`; modal Alvo visível |
| HOLD stale | ETH | 4× literal + preço; **sem** linha alvo; sem cenário | 5× literal incluindo dt `alvo` |
| EXIT vazio | ADA | só preço + copy exacta residual | igual (alvo já não existia em EXIT) |
| EXIT residual | LINK | só preço + residual ilustrativo | igual |
| Modal | os 4 | hold vs exit `hidden`; Alvo visível só Antes+HOLD | — |

Stale não inventa «alvo indisponível» no Depois. EXIT não ressuscita Entry/Stop.

---

## Heurísticas Nielsen (arquivo; não emitir no chat do pai)

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 3 | Badge/KPI/toggle claros; filtros estáticos |
| 2 | Match System / Real World | 4 | Vocabulário do issue; alvo some no Depois |
| 3 | User Control and Freedom | 3 | Expand + Antes/Depois + Fechar; filtros mortos |
| 4 | Consistency and Standards | 3 | Clone `/monitor`; ações empilhadas vs vivo |
| 5 | Error Prevention | 4 | Sem TP falso; literal em falta; EXIT limpo |
| 6 | Recognition Rather Than Recall | 4 | Labels no kv; delta = linha que desaparece |
| 7 | Flexibility and Efficiency | 2 | Proto estático |
| 8 | Aesthetic and Minimalist Design | 3 | Binance dark; 4 expands densos |
| 9 | Error Recovery | 3 | Indisponível explica; next step = Abrir Gráfico |
| 10 | Help and Documentation | 2 | Review-bar para Alan |
| **Total** | | **31/40** | **Good** |

Design specificity: **alta** — não serve a outro produto sem o Monitor Cripto Farol.

### Personas
- Trader beta HOLD: deixa de ver `$119.48` como TP; aponta stop `$68.28`. Sem red flag no Depois.
- Alan T7: toggle na mesma tabela prova o corte. Scroll até o kv = atrito P2, não confusão.
- Tester #75 (contexto → risco): card chega; modal confirma o mesmo recorte.

### Strengths
1. Clone da página, não da folha de tokens.
2. Delta óbvio (uma linha some) no mesmo sítio.
3. ETH stale e EXIT não reintroduzem alvo.

---

## Disposition

- P0/P1: 0 abertos.
- P2/P3: aceitos como residual ou polish não bloqueante (scroll 4-expand, hidden row só no proto, recorte de gráfico, ações empilhadas, fixture LINK).
- Determinísticos: nenhum achado sem classificação. O assert Playwright `mobile-table-hidden` falhou porque mediu `table.signals { display:table }` — falso positivo; `.table-wrap` está `none` (paridade CSS vivo L4191–4193).

Não há re-despacho de autor por P0/P1.

---

## Verdict

**PASS** — zero P0/P1, fidelidade lista+detalhe `/monitor`, landmarks presentes, toggle muda markup, delta sem alvo óbvio no Depois (card + modal), 4 estados cobertos, browser gate próprio na URL publicada.

---

## Snapshot

`.impeccable/critique/803-card-803-monitor-remover-alvo-A.md`

Prototype: `https://dev.criptofarol.com.br/prototypes/card-803-monitor-remover-alvo/` · sha256 `24fc626805ebbb3561f4cc3fbf45c0572e00a520b306a24274ce9e49cf2bb92d`
