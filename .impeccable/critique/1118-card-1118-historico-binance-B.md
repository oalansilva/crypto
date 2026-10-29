# Assessment B (detector + browser real) — card 1118 · change card-1118-historico-binance

> Assessor B isolado, sem transcript de A nem do pai. Sem nested-spawn. Cliente Claude Code (adapter cooperativo, não oficial; sem modo Auto), superfície claude-desktop.
> Único arquivo escrito por este filho: este snapshot. Screenshots de trabalho em `/tmp/1118-B-shots/` (não versionados).
> Modelo da captura (`cf-assess-b-1118.json`, role `assessment-b`, faixa `juizo`): rótulo **Opus 5.5**, slug **`claude-opus-5-5`**, effort `high`.
> Tokens parseáveis do `design.md` (rubrica D4, sem reabrir o parser): `UI impact: affected` · `live_route: /combo/discovery` · `surface: existing`.

```
Assessment B 1118
model: Opus 5.5 (claude-opus-5-5, effort high)
digest_match: disco == esperado == HTTP local == corpo visto pelo browser, IDENTICAL nos 3 HTML (+ live.css, cobertura.css, cobertura.js == tabela do design.md); HTTPS DEV 404 (não usado como prova)
detector: index exit 2 (2 achados, todos fora do delta: fonte Inter no <head> vivo, 9 travessões em COPIED); combo exit 2 (9, todos COPIED/<head>); optimize exit 2 (6, todos COPIED/<head>); live.css exit 2 (5, CSS vivo); cobertura.css [] exit 0; cobertura.js [] exit 0 → delta limpo
gate: design_token_gap=None · evaluate_clone_gate(HEAD)=True · landmarks_match(/combo/discovery, index)=True · copied_utf8_sum(index)=43646 > 0 · classify=PASS
browser: 278 asserts, 272 PASS, 6 FAIL (o mesmo T6 Esc nas 3 telas × 2 viewports)
P0: nenhum
P1: nenhum
P2: Esc não fecha a tabela de Cobertura (3 telas); resumo "Histórico desde 11 nov. 2014 · 3 timeframes" sobre-declara o intraday de NVDA/SPY (3 telas)
P3: HTTPS DEV 404 até publicar; favicon.ico 404 do http.server; "2 lacunas" do SPY conta a mesma falta no 5m e no 15m; coluna Ação recortada no Decidir 1440 (clone); copy da Demonstração cita "aba Decidir" no combo/optimize; achados do detector no incumbente clonado; sem gatilho visível de "consulta" para sair de "sob demanda" (Open Question do design.md)
verdict: PASS
```

- UTC: 2026-10-22T23:49Z
- Tupla (somente leitura): `bound_card=1118` · `q_git=card-1118-historico-binance` · Status=Design (bind do prompt). Sem `process_event`, sem mexer em Status, sem commit/push/Gist/comentário.
- Fronteira: `gh api repos/oalansilva/crypto/issues/1118 --jq .body` (sem `gh issue view`). Body grelhado com Problema, História, Entra (14 itens), Não entra. Sem reentrevista.
- `design.md` sha256 `5aee2b40701cad7936c362e5a00d4d10247a03e89a746c1b2dfe63a22b0f1fd0` (bate com o prompt).
- Skill do detector: o prompt aponta `.cursor/skills/impeccable/SKILL.md`, que **não existe** nesta árvore; a skill está em `.agents/skills/impeccable/SKILL.md`. Uso tirado de `detect.mjs --help`. Observação de processo, não achado do card.

## 1. Digest servido == local

HTTP local: `python3 -m http.server 18118 --bind 127.0.0.1` com cwd `frontend/public`, em segundo plano, encerrado no fim (porta 18118 livre depois).

| Arquivo | sha256 (disco = esperado = HTTP local = browser) | bytes | HTTP local | HTTPS DEV |
|---|---|---|---|---|
| `index.html` (canônico; `/` serve o mesmo) | `5db21b21c59f4fd41df36c916ed1ba737bd2bfef637834722a03fa7bdeb811ff` | 47342 | 200 | 404 |
| `combo.html` | `c14805cf76af3c46f5f86a86eef361b354b0c30ebfbe8f764d593b739404d804` | 30757 | 200 | 404 |
| `optimize.html` | `a0e8e60daa6cf0981aae433bee66d127dc251ee46ea89a0e8f25c0dc9885e72e` | 25085 | 200 | 404 |
| `live.css` | `03835ef5c21e5a086823248e0656944b120d26c8c44b724cb36dc35df2316674` | 67424 | 200 | — |
| `cobertura.css` | `324ab1db187d4cde5272822c645a6a546b96f455a7b385db4ed3a65bbd74cfc3` | 4721 | 200 | — |
| `cobertura.js` | `55f15658aabf0704f45c484fbb7dab227f0f04cd7769591749e9f94d2237418b` | 19886 | 200 | — |

O hash do corpo da resposta foi recalculado dentro do Playwright (assert L0) nas 6 combinações tela × viewport: **IDENTICAL**. HTTPS DEV `https://dev.criptofarol.com.br/prototypes/card-1118-historico-binance/` devolve 404 (proto ainda não publicado); registrado e não usado como prova.

## 2. Detector Impeccable

CLI: `node .agents/skills/impeccable/scripts/detect.mjs --json <arquivo>` (cwd worktree). Cada achado foi mapeado à região `COPIED`/`DELTA` pela linha.

| Alvo | exit | Achados | Origem |
|---|---|---|---|
| `index.html` | 2 | `overused-font` (Google Fonts Inter, l.8) · `em-dash-overuse` advisory (9 travessões) | l.8 = `<head>` do clone (fonte do vivo). Os 9 travessões estão **todos dentro de COPIED** (texto vivo); 1 fora, num comentário. Nenhum no DELTA. |
| `combo.html` | 2 | `overused-font` l.8 · 4× `gray-on-color` l.24 (zinc sobre `bg-blue-500`) · 3× `ai-color-palette` l.26 (gradiente/heading roxo) · `flat-type-hierarchy` l.18 | `<head>` + COPIED (`/combo/configure` vivo). Nenhum no DELTA. |
| `optimize.html` | 2 | `overused-font` l.8 · 4× `ai-color-palette` l.24/26 · `flat-type-hierarchy` l.18 | `<head>` + COPIED (`/combo/optimize` vivo). Nenhum no DELTA. |
| `live.css` | 2 | `overused-font` l.480 · 4× `ai-color-palette` l.288/289/432/433 | CSS vivo podado (bundle `index-CElzlQFP.css`). |
| `cobertura.css` | 0 | `[]` | DELTA |
| `cobertura.js` | 0 | `[]` | DELTA |

Marcadores: index COPIED 9/9 pares, DELTA 5/5; combo COPIED 4/4, DELTA 2/2; optimize COPIED 4/4, DELTA 2/2 (bate com o `design.md`). Overlay `detect.js` não injetado (CLI + Playwright).

**Classificação:** todos os achados vêm do incumbente clonado (CSS/DOM vivos), o que coincide com a declaração do autor no `design.md`. Delta limpo. Nada a abrir como P0/P1; registro como P3 do incumbente.

## 3. Gate estático (`scripts/process-fsm/design_clone_gate.py`, importado via `python3`)

| Verificação | Resultado |
|---|---|
| `design_token_gap(design.md)` | `None` |
| `parse_ui_impact` / `parse_live_route` / `parse_surface` | `affected` / `/combo/discovery` / `existing` |
| `load_head_catalog(repo)` contém `/combo/discovery` | sim (`texts`: Descoberta de estratégias swing · Preflight · Rascunho de varredura; `kind: authenticated`) |
| `evaluate_clone_gate(design, proto, repo, HEAD)` | **True** (também `True` com o carregamento padrão do HEAD) |
| `canonical_proto_html(proto)` é o `index.html` | sim |
| `landmarks_match(/combo/discovery, index.html)` | **True** |
| `copied_utf8_sum(index.html)` | **43646** (> 0; total 47342) |
| `classify(index.html, /combo/discovery, HEAD)` | **PASS** |
| extras: `copied_utf8_sum` combo / optimize | 28415 / 22739 (bate com o `design.md`); `/combo/configure` e `/combo/optimize` não estão no catálogo, então são extras sem gate próprio, como declarado |

## 4. Browser real

Playwright Python 1.62 + Chromium 1243 (`chrome-linux-arm64`, `--no-sandbox`), headless, `colorScheme: dark`, `locale: pt-BR`. Viewports **1440×900** (desk) e **390×844** (mob). Um contexto novo por tela × viewport. 34 screenshots full-page/viewport em `/tmp/1118-B-shots/` (`<tela>-<vp>-01-load` … `-07-decidir-expired`), todos com conteúdo (64–336 KB).

Console: o único `error` em todas as cargas foi `GET /favicon.ico 404`, pedido automático do Chromium à raiz do `http.server` (o proto não declara favicon e o servidor local não tem um). Separado do assert L1. Fora isso: 0 `console.error`, 0 `pageerror`, 0 resposta ≥400 e 0 `requestfailed` nos recursos do proto.

Sem scroll horizontal: `scrollingElement.scrollWidth == clientWidth` e `body.scrollWidth == innerWidth` em todas as medições (carga, NVDA aberto, QQQ falhou aberto, página 2 com IBIT/WAVES abertos, Decidir e Decidir expirada). Nenhum elemento passou da borda sem estar dentro de um contêiner com overflow próprio. No Decidir, 15 (desk) e 11 (mob) elementos ficam recortados dentro do contêiner da tabela viva: o recorte é do clone, não scroll da página (ver P3-4).

### Ações exercidas (em cada tela × viewport)

1. Carga da URL HTTP local; hash do corpo; console; overflow; screenshot.
2. Leitura das 6 linhas da página 1 (BTC/USDT, ETH/USDT, NVDA, SPY, QQQ, AAPL).
3. Clique em "Cobertura" de NVDA → leitura da tabela → conferência de seleção/contagem e foco → segundo clique fecha.
4. Teclado em SPY: foco no checkbox, `Tab` → botão "Cobertura de SPY"; `Enter` abre; `Escape`; `Space`; `Enter` fecha; `Space` no checkbox seleciona e desmarca.
5. Demonstração QQQ: "Concluída" → "Falhou (limite da Binance)" → abre a Cobertura de QQQ → volta para "Em andamento".
6. "Próxima" → IBIT (abre a Cobertura), SOL/BNB, MSFT/TSLA, WAVES (abre a Cobertura) → "Anterior".
7. Filtro "ETFs" → só SPY/QQQ/IBIT, contagem de selecionados igual → "Todas".
8. Medição do painel Demonstração (posição, topo vs. fim do `#root`, sobreposição).
9. Só no index: aba Decidir → evidência e linhas → "BTC/USDT favoritado" → "Passou de 30 dias" → desfavorita → setas do tablist voltam a Montar.

### Matriz de asserts (278 = 46 × 6 + 9 do Decidir × 2 + K7 × 2)

| # | Assert | index desk | index mob | combo desk | combo mob | optimize desk | optimize mob |
|---|---|---|---|---|---|---|---|
| L0 | digest servido no browser == esperado | PASS | PASS | PASS | PASS | PASS | PASS |
| L1 | carga sem console error / pageerror / ≥400 (favicon.ico do http.server à parte) | PASS | PASS | PASS | PASS | PASS | PASS |
| L2 | sem scroll horizontal (carga) | PASS | PASS | PASS | PASS | PASS | PASS |
| E1 | "Histórico não coletado" ausente | PASS | PASS | PASS | PASS | PASS | PASS |
| E2 | nada de pré/pós-mercado no texto visível | PASS | PASS | PASS | PASS | PASS | PASS |
| E3 | sem gráfico de ação/ETF (0 canvas, sem "gráfico" no seletor) | PASS | PASS | PASS | PASS | PASS | PASS |
| C1 | BTC/USDT coberto: "desde 17 ago. 2017 · 4 timeframes · sem lacunas · atualizado 22 out., 18:00" | PASS | PASS | PASS | PASS | PASS | PASS |
| C2 | NVDA coberto com período, lacunas e atualização | PASS | PASS | PASS | PASS | PASS | PASS |
| C3 | SPY coberto com "2 lacunas" (âmbar) | PASS | PASS | PASS | PASS | PASS | PASS |
| C4 | QQQ coletando (`role=status`, página e hora do pedido) | PASS | PASS | PASS | PASS | PASS | PASS |
| C5 | AAPL "Histórico sob demanda", sem botão Cobertura | PASS | PASS | PASS | PASS | PASS | PASS |
| K0 | alvo "Cobertura" ≥ 24 px (101×32) | PASS | PASS | PASS | PASS | PASS | PASS |
| K1 | `aria-expanded=false` + `aria-controls` antes | PASS | PASS | PASS | PASS | PASS | PASS |
| K2 | clique abre a tabela por timeframe (`aria-expanded=true`, região visível) | PASS | PASS | PASS | PASS | PASS | PASS |
| K3 | NVDA 15m "montado do 5m" + selo "derivado"; 5m nativo; 1d presente | PASS | PASS | PASS | PASS | PASS | PASS |
| K4 | linha "Binance Ações · pregão regular de Nova York · ajustado. Mercado fechado não conta como lacuna." | PASS | PASS | PASS | PASS | PASS | PASS |
| K5 | abrir Cobertura (mouse) não seleciona NVDA nem muda a contagem | PASS | PASS | PASS | PASS | PASS | PASS |
| K6 | foco volta ao botão depois do re-render | PASS | PASS | PASS | PASS | PASS | PASS |
| K7 | coluna estreita: tabela em 2 colunas (painel 320/294 px) | — | — | — | — | PASS | PASS |
| L3 | sem scroll horizontal (NVDA aberto) | PASS | PASS | PASS | PASS | PASS | PASS |
| K8 | segundo clique fecha (região removida) | PASS | PASS | PASS | PASS | PASS | PASS |
| T1 | `Tab` do checkbox SPY chega ao botão "Cobertura de SPY" | PASS | PASS | PASS | PASS | PASS | PASS |
| T2 | foco visível (outline 2px azul) | PASS | PASS | PASS | PASS | PASS | PASS |
| T3 | `Enter` abre a cobertura de SPY e o foco fica no botão | PASS | PASS | PASS | PASS | PASS | PASS |
| T4 | SPY 5m lacuna "14 out. 2026, 10:05–10:40"; 15m bloco 10:00–10:45 "montado do 5m" | PASS | PASS | PASS | PASS | PASS | PASS |
| T5 | `Enter` na Cobertura não seleciona SPY | PASS | PASS | PASS | PASS | PASS | PASS |
| **T6** | **`Escape` fecha a cobertura e devolve o foco** | **FAIL** | **FAIL** | **FAIL** | **FAIL** | **FAIL** | **FAIL** |
| T6b | `Escape` não tira o foco do botão | PASS | PASS | PASS | PASS | PASS | PASS |
| T7 | `Space` alterna a cobertura sem selecionar SPY | PASS | PASS | PASS | PASS | PASS | PASS |
| T8 | `Enter` de novo fecha; foco permanece | PASS | PASS | PASS | PASS | PASS | PASS |
| T9 | `Space` no checkbox SPY seleciona (a linha continua selecionável) | PASS | PASS | PASS | PASS | PASS | PASS |
| S1 | QQQ concluída → coberto com período, lacunas e atualização | PASS | PASS | PASS | PASS | PASS | PASS |
| S2 | QQQ falhou → "Coleta falhou … · limite de requisições da Binance · há 1d desde 05 jan. 2023" (nem vazio nem completo) | PASS | PASS | PASS | PASS | PASS | PASS |
| S3 | Cobertura de QQQ falhou: "incompleto" e "continua do ponto em que parou" | PASS | PASS | PASS | PASS | PASS | PASS |
| L4 | sem scroll horizontal (QQQ falhou aberto) | PASS | PASS | PASS | PASS | PASS | PASS |
| P1 | IBIT "Parcial: pedido desde 22 out. 2021; a Binance tem desde 11 jan. 2024" | PASS | PASS | PASS | PASS | PASS | PASS |
| P2 | Cobertura de IBIT: "insuficiente para o último pedido" | PASS | PASS | PASS | PASS | PASS | PASS |
| P3 | SOL/BNB cobertos; MSFT/TSLA sob demanda | PASS | PASS | PASS | PASS | PASS | PASS |
| P4 | WAVES/USDT congelado, checkbox desabilitado, com motivo | PASS | PASS | PASS | PASS | PASS | PASS |
| P5 | Cobertura de WAVES abre com "Binance Spot · 24/7" | PASS | PASS | PASS | PASS | PASS | PASS |
| L5 | sem scroll horizontal (página 2 com IBIT e WAVES abertos) | PASS | PASS | PASS | PASS | PASS | PASS |
| F1 | filtro ETFs mostra só SPY/QQQ/IBIT, contagem de selecionados igual | PASS | PASS | PASS | PASS | PASS | PASS |
| D0 | Demonstração `position: static`, abaixo do `#root` (+24 px), 0 sobreposição, nada fixo dentro dela | PASS | PASS | PASS | PASS | PASS | PASS |
| R0 | aba Decidir visível, Montar oculto | PASS | PASS | — | — | — | — |
| R1 | evidência "Binance Spot · 1d nativo · v7" + "amostra guardada até 21 nov. 2026; favoritos mantêm a amostra", sem "ccxt" | PASS | PASS | — | — | — | — |
| R2 | cada resultado: "amostra até 21 nov. 2026" | PASS | PASS | — | — | — | — |
| L6 | sem scroll horizontal (Decidir) | PASS | PASS | — | — | — | — |
| R3 | BTC favoritado → "favorito: amostra mantida" | PASS | PASS | — | — | — | — |
| R4 | expirada: ETH "não reproduzível exatamente"; BTC favorito mantém; evidência "amostra expirada em 21 nov. 2026: não reproduzível exatamente" | PASS | PASS | — | — | — | — |
| R5 | expirada sem favorito: BTC também "não reproduzível exatamente" | PASS | PASS | — | — | — | — |
| L7 | sem scroll horizontal (Decidir expirada) | PASS | PASS | — | — | — | — |
| R6 | setas do tablist voltam a Montar | PASS | PASS | — | — | — | — |
| L9 | sem console error / pageerror no fim do fluxo | PASS | PASS | PASS | PASS | PASS | PASS |

**Total: 278 asserts, 272 PASS, 6 FAIL.** Os 6 FAIL são o mesmo T6 (Esc) nas 6 combinações. Estado depois do `Escape`: `aria-expanded=true`, painel presente, foco no botão SPY. `cobertura.js` não tem handler de `Escape`.

Pixels, desk: shell vivo (sidebar 224 px), h1 "Descoberta de estratégias swing", Rascunho e Preflight na primeira dobra. Linhas do seletor com chip de classe, "Negociável", fato de histórico e "Cobertura ▾". A tabela de NVDA abre logo abaixo da linha com a nota de fonte/sessão/ajuste e 1d/5m/15m; o selo azul "derivado" aparece sob 15m. SPY com o fato em âmbar. QQQ com o fato em azul.
Pixels, mob: AppNav móvel, linhas em coluna, a tabela reorganiza em 2 colunas. A Demonstração fica no fim, no fluxo. No Decidir, os cartões mostram "amostra até 21 nov. 2026" sob o candidato.
Pixels, optimize: o seletor estreito (coluna de ~320 px) com a tabela em 2 colunas e foco visível no botão; o painel "Ready to Optimize" vivo ao lado.

## 5. Confronto com o Entra (só o que é visível; backend = Apply)

| Entra | Visto no browser | Disposition |
|---|---|---|
| Cobertura no seletor: ação/ETF deixam de ser "não coletado" e mostram período, lacunas e última atualização | E1, C2, C3, S1 nas 3 telas × 2 viewports | PASS |
| Coleta sob demanda: ativo não pedido continua sem coleta; o pedido coleta só o que falta | AAPL/MSFT/TSLA "sob demanda"; QQQ "Coletando · 1d, página 2"; filtro e paginação não mudam estado nem seleção | PASS (ver P3-7: sem gatilho visível de "consulta") |
| Período honesto: pedido × coberto, lacunas, atualização, insuficiente; falha nunca vira vazio nem completo | IBIT parcial/insuficiente; QQQ falhou com motivo e com o que há; SPY lacunas com data e hora | PASS (ver P2-2: resumo de NVDA/SPY) |
| 15 minutos montado do 5m e marcado como derivado | K3, T4 | PASS |
| Só pregão regular | nota "pregão regular de Nova York"; E2 sem pré/pós | PASS |
| Calendário: mercado fechado não vira lacuna | nota "Mercado fechado não conta como lacuna." | PASS (regra = Apply) |
| Reprodução enquanto favoritado / prazo → "não reproduzível exatamente" | R1–R5 | PASS |
| Amostra estável: o resultado registra fonte e versão | evidência "Binance Spot · 1d nativo · v7" | PASS |
| Não entra: gráfico de ação/ETF, pré/pós-mercado | E2, E3 | PASS |
| Mesma série, sem download repetido, retomada, versão, cache, migração | não são tela | P3 Apply (specs) |
| Demonstração não cobre conteúdo | D0 | PASS |

## 6. Nielsen (observado; sem ensaio de personas)

| # | Heurística | Observado | Sev. |
|---|---|---|---|
| 1 | Visibilidade do estado | Coletando com `role=status`; falha em vermelho com motivo; parcial e lacunas em âmbar com texto | — |
| 2 | Match com o mundo | "pregão regular de Nova York", "montado do 5m", "não reproduzível exatamente" | — |
| 3 | Controle | Cobertura abre e fecha sem marcar o ativo; Esc não fecha | P2 |
| 4 | Consistência | Mesmo delta nas 3 telas; mesma nota de fonte nas 3 classes | — |
| 5 | Prevenção de erro | Abrir a Cobertura não altera a seleção (`preventDefault` dentro do `<label>`) | — |
| 6 | Reconhecimento | Resumo na linha, detalhe sob demanda | — |
| 8 | Estética/densidade | Resumo "desde 2014 · 3 timeframes" mistura janelas diferentes | P2 |
| 9 | Recuperação | Falha diz o que há e que a coleta retoma | — |

## 7. Achados

### P0: nenhum

### P1: nenhum

Nenhum assert ligado a um critério do Entra falhou. O único FAIL (T6 Esc) não está no Entra e não quebra a acessibilidade (ver P2-1).

### P2: não bloqueiam; juízo

- **P2-1 Esc não fecha a tabela de Cobertura** (index, combo, optimize; desk e mob). *Mecânico na detecção, juízo na severidade.* `Escape` com o foco no botão deixa `aria-expanded=true` e o painel aberto. O foco não se perde (T6b PASS), e Tab/Enter/Space funcionam. A tabela é um *disclosure* inline (sem sobreposição e sem prender o foco), e o padrão WAI-ARIA de disclosure só pede Enter/Space. Por isso a acessibilidade não quebra e o achado não vira P1. **Corrigir:** decidir no rework ou no Apply. Opção A: Esc com o foco no botão ou dentro da região fecha e devolve o foco ao botão "Cobertura" (barato e alinhado ao assert pedido). Opção B: registrar no `design.md` que é um disclosure sem Esc.
- **P2-2 O resumo da linha sobre-declara o intraday** (index, combo, optimize; NVDA e SPY). *Juízo.* "Histórico desde 11 nov. 2014 · 3 timeframes · sem lacunas" sugere os 3 timeframes desde 2014, mas o 5m/15m de NVDA cobre de 19 mai. 2026 e o de SPY de 01 jul. 2026. A tabela por timeframe é honesta, mas o resumo é o que o Entra "Período honesto" lê primeiro. **Corrigir:** dizer de qual timeframe é o "desde" (p.ex. "1d desde 11 nov. 2014 · intraday desde 19 mai. 2026 · 3 timeframes …") ou usar o início comum. Copy da decisão 16; ajuste no rework ou registro como P3 aceito.

### P3: aceitos (Apply / clone / ambiente; não reabrir como P0/P1)

- **P3-1 HTTPS DEV 404** até o pai publicar o proto. *Mecânico.* Disco == HTTP local == esperado.
- **P3-2 `favicon.ico` 404** pedido pelo Chromium à raiz do `http.server` local. *Mecânico, ambiente.* Não é do proto.
- **P3-3 "2 lacunas" do SPY** soma a mesma falta de 14 out. no 5m e no bloco 15m que deriva dele. *Juízo.* É coerente com a decisão 9 (bloco incompleto conta como lacuna), mas pode ler como duas faltas distintas. Apply: considerar "1 lacuna (no 5m e no 15m derivado)".
- **P3-4 Coluna Ação recortada no Decidir a 1440** ("Promover"/"Excluir" cortados dentro do contêiner da tabela). *Mecânico.* Vem do clone vivo; o delta da amostra está inteiro e legível.
- **P3-5 Copy da Demonstração no combo/optimize** cita "a aba Decidir mostra a amostra", e essas telas não têm Decidir. *Mecânico.* O texto não vai para o produto.
- **P3-6 Achados do detector no incumbente** (fonte Inter, gradientes roxos e cinza sobre azul do `/combo/configure` e `/combo/optimize`, hierarquia plana, travessões no texto vivo, CSS vivo). *Mecânico.* Nenhum no delta; fora do escopo do card.
- **P3-7 Sem gatilho visível de "consulta"** para ação/ETF saírem de "sob demanda" até o #1119. *Juízo.* Coerente com a Open Question do `design.md` (leitura literal: a coleta vem de `GET /market/history`). Fica para Alan na Aprovação de Design, não para o crítico.
- **P3-8 Números e datas da amostra** (catálogo 8.685, coberturas, "v7", 21 nov. 2026) e formato das datas = `formatDate` vivo. *Mecânico.* Já aceitos no Apply contract.
- **P3-9 Skill do detector apontada em `.cursor/skills/impeccable/`** que não existe; está em `.agents/skills/impeccable/`. *Mecânico, processo.* Não é do card.

Mecânicos (assert/ferramenta): P2-1 (detecção), P3-1, P3-2, P3-4, P3-5, P3-6, P3-8, P3-9. Juízo: P2-1 (severidade), P2-2, P3-3, P3-7.

## 8. Veredito

**PASS.** P0 e P1 zerados. Os digests batem do disco ao browser nos 3 HTML e nos 3 arquivos de apoio. O gate estático passa (`design_token_gap=None`, `evaluate_clone_gate=True` com o catálogo do HEAD, landmarks de `/combo/discovery` no index, `copied_utf8_sum=43646`). O detector só acha o incumbente clonado e o delta sai limpo. No browser, 272/278 asserts passam nas 3 telas × 2 viewports, e todos os critérios visíveis do Entra estão cobertos: sob demanda, coletando, coberto, parcial, falha e congelado; 15m "montado do 5m" com selo "derivado"; Cobertura sem selecionar o ativo e operável por Tab/Enter/Space com o foco preservado; Decidir com amostra guardada, favorito mantido e "não reproduzível exatamente"; sem pré/pós-mercado, sem gráfico de ação/ETF; Demonstração no fluxo. Os 6 FAIL são o Esc (P2-1).

Disposition: sem rework obrigatório. P2-1 e P2-2 ficam para o pai decidir se entram no único rework permitido ou se são registrados como aceitos. P3 aceitos para o Apply.

## 9. Referências

- Disco: `frontend/public/prototypes/card-1118-historico-binance/{index,combo,optimize}.html`, `live.css`, `cobertura.css`, `cobertura.js`
- HTTP local (evidência): `http://127.0.0.1:18118/prototypes/card-1118-historico-binance/` (servidor encerrado)
- HTTPS DEV (404, não é prova): https://dev.criptofarol.com.br/prototypes/card-1118-historico-binance/
- Viewports: 1440×900 · 390×844 · `colorScheme: dark` · `locale: pt-BR`
- Detector: `node .agents/skills/impeccable/scripts/detect.mjs --json`
- Gate: `scripts/process-fsm/design_clone_gate.py` + `scripts/process-fsm/route-landmarks.yaml` (HEAD)
- Shots: `/tmp/1118-B-shots/` (34 PNG, não versionados)

proxy modelo: Assessment B → Opus 5.5 (claude-opus-5-5)
