# Snapshot — Assessment A · card #792 `card-792-monitor-risco-explicito` · r2

- Card: #792 — Card do Monitor: risco explícito (stop, alvo, distância e o que acontece se a leitura falhar)
- Change: `card-792-monitor-risco-explicito`
- Critic: Assessment A (isolado; inherit de modelo; sem transcript do pai; sem partilha com B)
- Modelo: inherit
- UTC: 2026-08-29T20:31:51Z
- Round: 2 (Alan devolveu T7: r1 era galeria 2×2 e PASS indevido)
- Tuple: hook `bound_card=792` `q_git=card-792-monitor-risco-explicito` `q=Aprovação de Design` no pai; esta onda Status=Design, Write só `.impeccable/critique/**`
- Digest `design.md` medido: sha256 `9d916252b2244055999bccbbafaeb4a7d7d3a6425173427fa7ed437b09cfff9d` · 15103 bytes · 1887 palavras
- Digest prototype `index.html`: sha256 `1a1ff265162784ca5708a76de22e6565ae85fb2832b90daec73cc40ac12f90c3` · 95314 bytes — **bate com o digest do prompt e com HTTPS + `http://127.0.0.1`**
- UI impact: **affected** — card + coerência com modal do gráfico (`OpportunityCard.tsx`, `ChartModal.tsx`); tela já existe: `/monitor`
- Prototype: `frontend/public/prototypes/card-792-monitor-risco-explicito/index.html` → `https://dev.criptofarol.com.br/prototypes/card-792-monitor-risco-explicito/`
- Copied vs generated (autor): copied 82460 · generated 12854
- Incumbente: `MonitorStatusTab.tsx` + `OpportunityCard.tsx` + `.monitor-theme` em `frontend/src/index.css`; rota viva `/monitor` redirecciona a `/login` sem sessão (comparação por fonte + linha SOL colada no T7, não por screenshot autenticado)
- Method: issue #792 body (vocabulário Distância/Stop/Alvo/Risco residual/HOLD/EXIT/Indisponível + 6 AC); `design.md` D1–D10 + contrato de clonar a **página** `/monitor` (proibido galeria 2×2); Playwright Chromium 1280×800 e 390×844 na URL publicada; toggle Antes/Depois exercitado; asserts de tabela/kv/copy. Detector CLI e overlay Impeccable ficam com B.

---

## Re-check do r1 (obrigatório neste r2)

O r1 A passou uma galeria de 4 cards 2×2 (digest `068581d6…` · 21275 bytes) tratando shell/tokens como fidelidade. Alan no T7 rejeitou: a rota viva é lista+detalhe. Esse PASS é **inválido**. Achado P0 de topologia **fechado neste HTML**: `table.signals` ×2 (Em posição / Saída), thead com Status · Preço · Distância · 7d · Risco até stop · Tags · ações, linha SOL HOLD visível no primeiro viewport 1280.

---

## Brief (só neste snapshot)

Tester do beta não calibra "quanto pode doer" porque o card mostra Compra/Venda e preço mas omite stop/alvo/distância ou ressuscita Entry/Stop mortos em EXIT. Card #792: hierarquia estado → distância → stop/alvo (ou `indisponível — dado não confiável`); frase "se o preço cruzar X, a leitura deixa de valer" só com dado comprovado; EXIT sem Entry/Stop operáveis e com copy residual vazia exacta. Fonte top-level `opportunity.*`. Protótipo MUST ser clone da página `/monitor` (KPIs, filterbar, `table.signals`, status-row, mobile-cards) com delta só no kv do OpportunityCard. Toggle Antes/Depois é a prova do delta no mesmo sítio.

Audience: investidor do beta (e Alan em T7) que já usa a tabela `/monitor`. Outcome: apontar risco no card expandido sem operador (#75). Direction: clone da página, Binance dark, não galeria. Scope: 4 linhas (SOL HOLD completo, ETH HOLD indisponível, ADA EXIT vazio, LINK EXIT residual).

Mode: **Operate**.

---

## Browser gate (Assessment A — evidência própria)

URL publicada 200, bytes 95314, sha256 `1a1ff265…`. Console: 0 erros. Request failed: 0.

| Assert | 1280×800 Depois | 390×844 Depois |
| --- | --- | --- |
| (a) thead Status, Preço, Distância, 7d, Risco até stop, Tags | PASS (`table.signals` ×2) | tabela `display:none` (igual CSS vivo `@media max-width:740px`) |
| (b) `table.signals` + botão Operar | PASS · 4× Operar visíveis · SOL Operar box x=1163 w=76, não clipado | 4× Operar visíveis nos `.mobile-card` (grid 1 col `362px`) |
| (c) linha SOL Compra · `$105.39` · `13.38%` · `35.21%` stop · Médias Móveis · Carteira · estrelas · Strategy | PASS (primeiro viewport) | n/a (cards, não thead) |
| (d) ETH `indisponível — dado não confiável`; ADA `posição encerrada segundo a estratégia — sem risco residual mapeado`; SOL "cruzar" | PASS | PASS (mesmos nós no DOM móvel) |
| (e) Antes altera kv (`compra`/`distância stop` vs `distância até saída`); `aria-pressed`; residual/cenário hidden no Antes | PASS (não morto) | PASS |
| (f) mobile: `.table-wrap` hidden, `.mobile-cards` grid, delta legível | — | PASS |
| (g) console | PASS | PASS |

Toggle **não está morto**: Depois SOL kv = distância até saída/stop + stop + alvo + entrada + preço; Antes SOL kv = compra + stop + preço atual + distância stop + distância objetivo (paridade com `OpportunityCard.tsx` actual). ETH Antes usa `-`; ETH Depois usa o literal. ADA Antes ainda mostra `distância stop`/`distância objetivo` com `-` (produto actual); Depois só `preço atual` + bloco residual.

Rota viva `https://dev.criptofarol.com.br/monitor` → `/login` (sem sessão). Fidelidade incumbente = fonte + linha T7, não pixel da rota autenticada.

---

## Findings

### P0 — bloqueante
- nenhum. Galeria 2×2 sem tabela **não** está neste digest. Shell/tokens não foram usados como substituto da tabela.

### P1 — deve corrigir antes de PASS
- nenhum.

### P2 — accepted-residual ou polish recomendado
- [P2] Default: as 4 `head-row` vêm `expanded`. O kv/delta fica abaixo da dobra em 1280×800 (tabela começa ~y=568; SOL Operar ~y=708; card SOL só asoma). Toggle funciona, mas a prova do delta exige scroll. Fix de review: só SOL expandida no load, ou `scrollIntoView` do primeiro `[data-risk-kv]`.
- [P2] Ações da linha empilham em coluna ~92–100×110–119px (`min-width: 0` no override gerado). Vivo usa `.row-actions { min-width: 210px }`. Operar continua visível e legendado; o cluster deixa de ser a fila horizontal do produto. Preferir `overflow-x: auto` no wrap **sem** zerar min-width, ou reduzir colunas menos críticas (7d já some &lt;1100px).
- [P2] Kv Depois usa dt `entrada` no HOLD; o produto vivo e o Antes usam `compra` (`entryPriceLabel`). Vocabulário do issue não congela `entrada`. Apply que copiar o HTML introduz sinónimo. Manter `compra`/`venda/short`.
- [P2] Frase de cenário acrescenta sufixo «segundo a estratégia (stop)» à copy do issue/D4 («se o preço cruzar X, a leitura de posição deixa de valer»). Âncora `$68.28` correcta; cortar o sufixo no Apply.
- [P2] `ChartModal` não está no protótipo (contrato Apply §4–5). Aceite se o Apply espelhar a mesma hierarquia/copy; não é prova visual desta onda.
- [P2] Copy de fixture no corpo do card (ETH «estratégia protegida…», LINK «Residual ilustrativo a partir de signal_history») é nota de review, não copy de produto. Não levar para `OpportunityCard.tsx`. Residual LINK («último EXIT em $14.82 · exposição residual 4.10%…») é ilustrativo — Apply usa `signal_history` real.

### P3 — melhoria menor
- [P3] Coluna 7d = `-` (sem spark). Thead existe; spark vivo precisa de série. Aceitável em HTML estático.
- [P3] `th` «ações» vs vivo `actions-cell` vazio. Cosmético.
- [P3] `data-testid` duplicados (mobile-card + detail-row). `querySelectorAll` do toggle cobre os dois; QA Playwright vai precisar de `.nth` / `visible`.
- [P3] 390: primeiro viewport = review-bar + KPIs empilhados 1fr + filterbar; o card SOL exige scroll (igual KPI 1-col do vivo a ≤740px).
- [P3] Só o primeiro `dd` indisponível do ETH no JS Depois leva `title="dado não confiável ≠ erro de rede"` (D10). Replicar nos cinco.
- [P3] Heading HOLD continua «Compra / Stop» com o kv a abrir em distância — D8 pede estender o `dl`, não o título. Aceitável.

---

## Produto

- Problema/user/hipótese/resultado: fiel ao issue (roteiro #75). Vocabulário Distância/Stop/Alvo/Risco residual/HOLD/EXIT/Indisponível presente; avoid gap/delta/spread/N/A. Desvio menor: `entrada` (P2).
- Hierarquia no card Depois: badge Compra/Venda no strip → distância até saída → distância até stop → stop → alvo → (entrada) → preço → frase cenário (só SOL, `aria-live="polite"`) → residual só EXIT.
- HOLD completo (SOL): distância + stop `$68.28` + alvo `$119.48` visíveis sem gráfico; % 2 casas; USD com 2+ casas.
- HOLD indisponível (ETH): cinco campos com literal `indisponível — dado não confiável` itálico; preço actual permanece; sem frase cenário (`hidden`).
- EXIT vazio (ADA): kv só `preço atual`; sem Entry/Stop operáveis; copy exacta `posição encerrada segundo a estratégia — sem risco residual mapeado`.
- EXIT residual (LINK): sem Entry/Stop; bloco Risco residual com exposição ilustrativa «não operável».
- Non-goals: sem Kelly, sem stop na Binance, sem Sharpe/SQN, sem Telegram, sem backfill de outra timeframe.
- Segredo: ETH tag «protegida»; descrição não vaza `parameters`/`indicator_values`.

## UX

- Carga cognitiva (checklist Operate): Single focus falha no review (4 estados abertos de propósito) · Chunking: kv HOLD 6 linhas no limite · Grouping: status-row + tabela + card OK · Hierarchy: badge → distância → stop/alvo OK · One thing at a time: falha com 4 expands · Minimal choices: toggle 2 opções OK · Working memory: labels no sítio OK · Progressive disclosure: falha no default all-expanded. **2–3 falhas = moderada** (intencional para T7 ver os 4 estados; mitigar com só SOL aberta).
- Emocional: o bloco amarelo «Se o preço cruzar $68.28…» é o pico de clareza do HOLD; ETH itálico evita fingir número; ADA residual é o fecho honesto do EXIT. Vale do r1 (galeria) não se repete.
- Filtros/KPI/search são chrome estático — esperado em protótipo; não são a prova do card.

## Fidelidade (rubrica 1 — bloqueante)

- Topologia = lista+detalhe da vista admin (`showTechnicalColumns=true`): KPIs Em posição/Em saída/Total/Em carteira, filterbar Em portfólio/Timeframe/Estrelas/Estratégia, secções `Em posição` e `Saída / cobertura` (copy viva em `MonitorStatusTab.tsx` L1171), `table.signals` com as colunas técnicas, status-row, mobile-cards.
- Linha SOL T7: Compra, $105.39, 13.38%, 35.21% stop, Médias Móveis, Carteira, ★★★, Strategy, Abrir Gráfico / Ver Trades / Operar — **presente no primeiro viewport 1280**.
- Shell: sidebar 224px, Monitor `aria-current`, header workspace, tokens `--bg-*` / `--accent-primary` / `--text-*` / `--border-default` e `--bg-1`/`--t-3` do `monitor-theme`, Inter. `.detail` 3 colunas = CSS vivo L3882–3886. Breakpoint 740px esconde tabela / mostra cards = vivo L4186–4193.
- Delta = kv + cenário + residual + JS Antes/Depois. Sem layout paralelo 2×2.
- Toggle Antes/Depois **vivo** (P0 «morto» não aplica). Prova do clone da **página** é a tabela (visível sem toggle); prova do **delta** é o kv (precisa scroll se as 4 linhas estão abertas).
- 0 elementos `.monitor-card` / galeria. `monitorCardCount=0`.

## Acessibilidade

- Teclado: Tab aterra em Favoritos (nav); botões do toggle e `.row-toggle` são `<button>`. Sem skip-link (paridade com o app).
- Contraste `indisponível` `#929aa5` sobre `#181a20` ≈ 6:1 — AA para texto 13px.
- Semântica: `table`+`th`, `dl.kv` `dt`/`dd`, `aria-pressed` no toggle, `aria-expanded` nas linhas, `aria-live="polite"` no cenário SOL, `hidden` em residual/cenário no Antes.
- Significado não só por cor: pill Compra/Venda tem texto; indisponível é literal, não só itálico.
- Touch: Operar tabela 76×30 (&lt;44) — paridade com `.row-action` vivo `min-height:30`. Mobile foot buttons 4× visíveis.
- Duplicidade de headings/testids mobile+desktop: `display:none` no breakpoint tira da AT.

## Responsividade

- 1280×800: tabela visível, mobile-cards `display:none`, KPIs 4 col, Operar não clipado, sidebar 224px.
- 390×844: sidebar some (≤1024), tabela `none`, 4 `.mobile-card` em 1 coluna, kv com `word-break`, 4 estados no scroll. Não é galeria 2×2 — é o fallback móvel do produto.
- Copy longa do residual ADA/LINK parte linha na 3ª coluna do `.detail`; legível.

## Estados (4)

| Estado | Par | Depois | Antes (clone do kv vivo) |
| --- | --- | --- | --- |
| HOLD completo | SOL | distância 13.38% / 35.21%, stop $68.28, alvo $119.48, cenário cruzar $68.28 | compra $91.40, stop $68.28, distâncias com número |
| HOLD indisponível | ETH | 5× literal; sem cenário | 4× `-` + preço |
| EXIT vazio | ADA | só preço; residual copy exacta; heading Risco residual | preço + distâncias `-`; heading Execução |
| EXIT residual | LINK | só preço; residual ilustrativo não operável | preço + distâncias `-`; heading Execução |

Stale ETH candle `stale` + protegida: bloco inteiro cai em indisponível, preço actual permanece. EXIT não ressuscita Entry/Stop.

---

## Heurísticas Nielsen (arquivo; não emitir no chat do pai)

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 3 | Badge/KPI/toggle claros; filtros estáticos |
| 2 | Match System / Real World | 3 | Vocabulário do issue; dt `entrada` vs `compra` |
| 3 | User Control and Freedom | 3 | Expand/collapse + Antes/Depois; filtros mortos |
| 4 | Consistency and Standards | 3 | Clone `/monitor`; ações empilhadas vs vivo |
| 5 | Error Prevention | 4 | Literal em falta; EXIT sem Entry/Stop mortos |
| 6 | Recognition Rather Than Recall | 3 | Labels no kv; cenário âncora o stop |
| 7 | Flexibility and Efficiency | 2 | Protótipo estático; Tab ok, sem atalhos de produto |
| 8 | Aesthetic and Minimalist Design | 3 | Binance dark; 4 expands densos |
| 9 | Error Recovery | 3 | Indisponível explica; next step = Abrir Gráfico já no footer |
| 10 | Help and Documentation | 2 | Review-bar para Alan; Distância não definida inline para o tester |
| **Total** | | **29/40** | **Good** |

na_heuristics: (nenhuma).

## Design specificity

**LLM:** A composição é do Farol (monitor-theme, pills Compra/Venda, risk-bar, tags Carteira/Strategy, AppNav). Não é dashboard genérico nem a galeria r1. O delta (kv + cenário amarelo + residual tracejado) lê-se como extensão do `dl.kv` existente.

**Deterministic scan:** não corrido nesta onda A (B possui detector). Asserts Playwright acima são evidência visual, não overlay.

**Overlays:** não injectados (A não corre `detect.js`).

## Overall impression

O r2 corrige o P0 de topologia. Alan reconhece `/monitor` no primeiro ecrã 1280. Os 4 estados do card estão no sítio certo com a copy congelada. O que resta é polish de review (default expand, cluster de acções, `entrada` vs `compra`, sufixo da frase).

## What's working

1. Tabela admin + linha SOL T7 no fold — prova de clone, não tokens.
2. Toggle Antes/Depois muta o mesmo `dl` (não uma segunda página).
3. EXIT vazio com a frase exacta do issue; HOLD falho com o literal, não `-`/`N/A`.

## Persona red flags

**Alex (power / dashboard):** filtros mortos e 7d vazio irritam; consegue ler risco no SOL expandido em &lt;60s se souber scrollar. Sem P0.

**Sam (teclado / AT):** `table`+`dl`+`aria-pressed` ok; duplicados de testid; alvo de toque 30px no cluster da linha. Sem bloqueio.

**Riley (stress / estados):** os 4 estados existem e o Antes prova o produto actual (`-` em ETH/ADA). Fixture «ilustrativo» no LINK é o red flag se copiada para produção.

**Investidor beta (contexto PRODUCT.md):** a frase «cruzar $68.28» responde «onde dói»; ETH não finge número. Não parece ordem na corretora (não entra Kelly / stop Binance).

## Minor observations

- `pair-icon` LINK = «LIN» (slice 3 do vivo).
- `canvas-wash` amarelo no protótipo — extra vs página viva; não compete com o delta.
- Heading EXIT Antes = «Execução» = `entryStopHeading` quando `showEntryStopRows` é falso. Fiel.

## Questions to consider (arquivo)

- Default só SOL expandida para o T7 ver tabela **e** kv no mesmo fold?
- Apply copia `compra` do React ou `entrada` do HTML?
- Residual LINK: template fixo ou último `signal_history`?

---

## Disposition

- P0/P1: 0 abertos (P0 de galeria r1 fechado por rewrite).
- P2/P3: residual de polish / Apply; não bloqueiam esta crítica.
- Determinísticos: todos classificados.
- Browser asserts a–g desta onda: verdes na URL do digest `1a1ff265…`.
- Rota `/monitor` autenticada não inspeccionada (login).

## Verdict

**PASS** — zero P0/P1; fidelidade lista+detalhe da `/monitor` (não galeria); toggle Antes/Depois vivo; 4 estados com copy exacta no EXIT vazio e no indisponível.

---

## Handoff (proxies)

- Words `design.md`: 1887
- Bytes prototype: 95314 (copied 82460 / generated 12854 — conta do autor)
- Spawns: esta onda = 1 critic A (r2); B à parte
- Snapshot: `.impeccable/critique/792-card-792-monitor-risco-explicito-r2-A.md`
