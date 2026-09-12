# Assessment A — card 897 · change card-897-discovery-promote-metrics

> Avaliador A isolado (produto / UX / a11y / fidelidade / estados). Mesmo modelo do chat. Sem transcript do pai. Sem nested-spawn. Sem `process_event`. Sem edição de `design.md`, HTML proto, backend, `frontend/src` ou OpenSpec. Única escrita: este arquivo.

## Metadata

- card: 897 — discovery-promoted favorite mostra snapshot nas chaves que a grade já lê
- change: `card-897-discovery-promote-metrics`
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-897-discovery-promote-metrics`
- tuple: `(q=Design, bound_card=897, q_git=card-897-discovery-promote-metrics)` via `scripts/process-fsm` `resolve(..., status='Design')` (Moore page ausente neste worktree)
- data (UTC): 2026-09-11T175925Z
- UI impact (rubrica): **affected** · `live_route: /favorites` · `surface: existing` — linhas próprias 19–21 de `design.md` (parseáveis)
- Issue: Q1=A Q2=A (grelha fechada no `design.md`; não reaberta)
- Digest proto (autor, verificado nesta sessão):
  - canónico `index.html` sha256 `f35495bc6d0d24b3ae78a258accc17257dd6126b4a4325c01070c11bac8309bc` · 42058 B
  - extra `analise.html` sha256 `5ea6e082ddeae17d8d5c6d6b89deefe78d167a7e62772157f492fd5d93ccb7b7` · 21405 B
- Servido HTTPS == local: IDENTICAL (`cmp` limpo nos dois HTML)
- Folha de tokens: path `.agents/skills/impeccable/references/cripto-farol-token-sheet.md` **ausente neste worktree**; chrome lido via `DESIGN.md` (não reescrito) + `frontend/src/index.css`. Folha = chrome; **não** substitui landmarks.
- Tooling: Chromium 1243 headed (`xvfb-run` + Playwright `chromium.launch({headless:false})`, `executable_path` cache ms-playwright arm64). `playwright-cli-headed` wrapper ausente; mesmo binário headed. Sem escrita fora deste snapshot.

## Limitação de sessão (obrigatória)

Playwright Chromium 1243, viewport 1280×800:

| URL pedida | URL final | Landmarks `/favorites` |
|---|---|---|
| `https://dev.criptofarol.com.br/favorites` | `https://dev.criptofarol.com.br/login` (h1 `Bem-vindo de volta`) | 0/4 |
| `https://dev.criptofarol.com.br/combo/results` | `https://dev.criptofarol.com.br/login` (h1 `Bem-vindo de volta`) | n/a (rota extra, sem chave de catálogo) |

**`/login` não é a rota.** Chrome de login **não** é evidência de clone e **não** autoriza PASS de fidelidade. Sem cookie de administrador, a avaliação de clone usa: (1) protótipo canónico HTTP, (2) HTML local, (3) fonte viva `frontend/src/pages/FavoritesDashboard.tsx` + `ComboResultsPage.tsx` vs catálogo `scripts/process-fsm/route-landmarks.yaml`. Sidebar 224px / tokens `--bg-*` **não** bastam.

HTTP 200 isolado nunca é PASS. Os 200 do proto coincidem com digest e com asserts de landmark/contrato no browser.

## Tokens parseáveis (rubrica)

`design.md` linhas próprias 19–21:

```
UI impact: affected
live_route: /favorites
surface: existing
```

Justificativa não vazia no corpo (clone+delta da rota existente `/favorites`; extra `/combo/results` em `analise.html`). **PASS** deste item da rubrica. Nenhuma rodada extra nasce só para o parser.

## Fidelidade (clone da página viva)

Catálogo `/favorites` (`scripts/process-fsm/route-landmarks.yaml`):

| Landmark | Vivo `FavoritesDashboard.tsx` (sem sessão) | Proto `index.html` + Playwright + PNG |
|---|---|---|
| `table.fav-strategies` | L1442 | count=1, `isVisible=true` no desktop 1280; hidden no mobile 390 (cards), igual ao vivo `@media max-width:1023px` |
| `Estratégias favoritas` | h1 L1244 | h1 visível «Estratégias favoritas» (desktop e mobile). `getByText` `.first()` acerta o subtitle escondido do `.mobilebar` (`display:none` no desktop) — falso negativo de locator, não de tela. PNG desktop/mobile mostram o h1. |
| `Symbol` | thead L1448 | visível no thead desktop; filtro «Symbol» também visível |
| `Estratégia` | thead L1449 | visível no thead desktop |
| `Ações` | thead L1463 | visível no thead desktop |

Anti-padrões P0:

- URL canónica `…/prototypes/card-897-discovery-promote-metrics/` → `index.html` é a página de Favoritos (shell + heading + tier cards + filtros + `table.fav-strategies` + 2 linhas). **Não** é painel ANTES/DEPOIS. Botões Antes/Depois = 0. Comentário HTML cita a recusa; markup não a viola.
- Não é grelha de N estados no lugar de lista+detalhe. Default = Operate na listagem.
- Extra `analise.html` **não** é o index; copy visível de `/combo/results` noutro URL, como o skill exige para N superfícies.

Chrome presente (sidebar 224px, Inter/BinanceNova, `--bg-primary:#0b0e11`, amarelo `#fcd535`, nav Favoritos ativa) = **folha**, não prova. Prova = landmarks 4/4 no proto canónico, alinhados ao TSX.

Extra `/combo/results` (não catálogo): clone estrutural visível = `combo-page`, `Voltar aos favoritos`, `aria-label="Análise da estratégia"`, `data-testid="combo-result-summary"`, chips símbolo/TF/direção, `dl` Retorno total / Taxa de acerto / Drawdown máximo / Operações, gráfico, `StrategyTradesTable` chrome (Operação/Tipo/Data/Sinal/Preço/Lucro/Prejuízo), disclaimer educacional. Delta = etiquetas de janela + números do snapshot. Omite painéis vivos não-contrato (regras, transparência, pill «Métricas») — P3, não galeria.

Digest: local == HTTPS 200 == digest do `design.md` / prompt.

PNGs do autor (lidos nesta sessão, pixels):

- `.impeccable/critique/card-897-index-desktop-1280x800.png`
- `.impeccable/critique/card-897-index-mobile-390x844.png`
- `.impeccable/critique/card-897-analise-desktop-1280x800.png`
- `.impeccable/critique/card-897-analise-mobile-390x844.png`

Desktop index: h1 + table + linha ALPHA `#193` com 0,31 / 30 / 46,7% / +16.951% / 16,5% e linha BTC combo sem origem Descoberta. Mobile index: cards, mesmos números. Análise: resumo snapshot e lista de 12 com −13,92%; etiquetas distintas visíveis.

## Produto (escopo — não reabrir grelha)

Delta pedido (issue #897, Q1=A Q2=A): favorito promovido da Descoberta mostra o snapshot nas chaves que a grade já lê; `#193` already-promoted sem promover de novo; resumo da análise = snapshot (Max DD ≠ «Indisponível»); se a lista fica nas velas atuais, etiquetas visíveis distinguem resumo vs lista; combo-saved inalterado; sem Calmar/#896; sem redesign de colunas; sem reconstruir os 30 negócios da Descoberta.

| Aceite visível | Evidência proto (Playwright + pixels + HTML) | Disposition |
|---|---|---|
| Grade `#193`: Sharpe 0,31 · 30 · Win 46,7% · Return +16.951% · Max DD 16,5% ≠ `-` / 0 | desktop `[data-metric]` exact; mobile card contém os cinco | OK |
| Already-promoted: números sem CTA de promover | linha carregada; sem Promover | OK |
| Combo-saved inalterado | BTC/USDT · 0,50 · 72 · 58,3% · +19.927% · 12,2%; texto sem «Descoberta» | OK |
| Abrir gráfico não zera a grade | link `analise.html`; mock estático (números não mudam); script só marca `data-chart-opened` | OK para proto; persistência = Apply |
| Resumo = snapshot; Max DD 16,5% ≠ Indisponível | `combo-result-summary` +16.951% · 46,7% · 16,5% · 30; body sem «Indisponível» | OK |
| Janelas rotuladas, visíveis, não tooltip | h1 `Resumo · janela de treino da Descoberta · 10/10/2020 → 01/02/2024`; h2 `Lista de operações · velas atuais · 12 negócios — não é a janela da Descoberta`; `isVisible=true` desktop e mobile | OK |
| Lista 12 negócios atuais (incl. −13,92%) sem fingir os 30 da Descoberta | 12 `<tr>`; −13,92% visível | OK |
| Fora: Calmar / ranking / colunas novas / Excel / Monitor | sem Calmar; thead igual ao vivo; Exportar já existia | OK |
| Tier 3 da promoção = 1 estrela (Acompanhar) no vivo | `getTierDisplay(3)` → `tier-watch`; proto 1 estrela em `#193` | OK (não é furo) |

Não-goals de motor (flatten JSON, ORM, sidecar de trades regenerados, escala ratio vs %) são contrato de Apply — P3 se citados, nunca P0/P1.

## UX

Hierarquia: shell autenticado → h1 Estratégias favoritas → resumo por estrelas → filtros → tabela (desktop) / cards (mobile). Delta localizado nas células já nomeadas da linha Descoberta. Combo-saved permanece o vizinho de controlo.

Análise: chips de identidade → etiqueta de janela do resumo → 4 métricas do snapshot → gráfico rotulado «velas atuais» → lista com etiqueta distinta. Dois conjuntos de números (30 / +16.951% vs 12 / −13,92%) deixam de competir no mesmo glance sem rótulo.

Carga cognitiva: a grade não adiciona colunas nem um segundo painel. A análise troca o h1 de nome da estratégia pela etiqueta de janela (decisão 4 do `design.md`); identidade continua nos chips + parágrafo. Pontos de decisão visíveis na grade por linha = Analisar / Revalidar / Delete (iguais ao vivo). Etiquetas são leitura, não CTA extra.

Prevenção: o operador não precisa promover de novo para ver `#193`. Recuperação: Voltar aos favoritos devolve à grade (proto estático).

Fricção residual (não bloqueante): «Backtest aguardando atualização» é copy viva de `auto_refresh_status` pending, ao lado de métricas já preenchidas pelo snapshot. Fora do delta; Apply não deve deixar o refresh sobrescrever as chaves (já no contrato).

## Acessibilidade

- `lang=pt-BR`; `:focus-visible`; `prefers-reduced-motion`.
- Etiquetas de janela são **texto visível** em `h1`/`h2` (`data-testid=summary-window-label` / `trades-window-label`), não `title`/`aria-label` só. Contrato a11y do card cumprido.
- Chart da grade: `aria-label="Ver análise completa"` (link). Resumo: `aria-label="Análise da estratégia"` + `dl` «Resumo de desempenho e risco». Gráfico ilustrativo com `role="img"` + `aria-label`.
- Alvos: nav/filtros/mobile CTAs ≥40–44px. Estrelas 28px e ícones de linha 32px = padrão vivo, não deste card.
- Chip «Descoberta» é redundante com a linha de meta visível; não é a única via de nome.
- Contraste: pares Binance do `DESIGN.md` (amarelo `#fcd535` em canvas `#0b0e11`, verde `#0ecb81` / vermelho `#f6465d` para return/DD). Sem par novo inventado.

Gaps vs vivo (P3): `Delete` só `title`; proto não replica `aria-label` composto da célula de estratégia com descrição; h1 da análise deixa de ser `combo-result-title` com o nome da estratégia (o nome vai para o parágrafo).

## Responsividade

Desktop 1280: tabela visível; colunas Symbol / Estratégia / TF / Sharpe / Trades / Win% / Return / Max DD / Ações no PNG. Mobile 390: tabela `display:none`; cards com os cinco números do snapshot; header 72px. Análise mobile: etiquetas wrapam e continuam visíveis; 12 cards de operação; Exportar full-width.

Clone CSS ≠ vivo (P3): proto `@media(max-width:1400px)` esconde select/telegram/period/stop; vivo `@media(max-width:1540px)` esconde telegram/period/**win-col** e `@media(max-width:1280px)` esconde `.risk-col` (Stop **e** Max DD). O proto mantém Win% e Max DD visíveis a 1280 — útil para o contrato, mas é divergência de breakpoint. Apply deve preencher as células do vivo, não inventar um layout novo.

Mobile cards do proto acrescentam Win% e Max DD; o vivo só mostra TF / Sharpe / Trades / Return. Extra de densidade, não coluna nova na tabela.

## Estados

Mock cobre: default Operate da grade com `#193` filled + combo-saved filled; análise com resumo snapshot + lista velas atuais (12). Não mocka: loading, vazio, erro de GET, snapshot ausente, sessão expirada, combo-saved em `/combo/results` (correctamente fora do extra). O aceite visível do card é o estado filled de `#193` e o par de etiquetas — coberto. Restante = P3 de cobertura de mock.

Abrir gráfico → voltar: HTML estático não reescreve células; demonstra o *contrato visível*, não a persistência. Persistência é P3 de Apply (tasks 2.1–2.2).

## Design specificity

A composição é da grade de Favoritos (workbench, estrelas, chaves Sharpe/Trades/Win%/Return/Max DD) e do resumo `/combo/results`. Não poderia ir a um SaaS genérico inalterado. Modo Impeccable: **Operate**.

## Heurísticas Nielsen (0–4, Operate; snapshot only)

| # | Heurística | Score | Nota |
|---|---|---|---|
| 1 | Visibility of system status | 4 | Snapshot filled na linha; janelas nomeadas no resumo e na lista |
| 2 | Match between system and real world | 4 | Vocabulário da grelha (Sharpe, Trades, Win%, Return, Max DD) e «janela de treino da Descoberta» vs «velas atuais» |
| 3 | User control and freedom | 3 | Voltar; Revalidar/Delete do vivo; mock sem confirmação destrutiva |
| 4 | Consistency and standards | 3 | Landmarks da rota; chip/meta de origem e breakpoints 1400 vs vivo 1540/1280 |
| 5 | Error prevention | 4 | Q2=A: `#193` lê o snapshot sem promover de novo; lista não se faz passar pelos 30 |
| 6 | Recognition rather than recall | 4 | Etiquetas visíveis; números nas colunas já nomeadas |
| 7 | Flexibility and efficiency | 3 | Filtros/tier do vivo presentes como chrome; não exercitados |
| 8 | Aesthetic and minimalist design | 3 | Chip Descoberta redundante com a meta; mobile com 6 métricas vs 4 do vivo |
| 9 | Help users recognize/recover errors | 3 | Sem estado erro/vazio; «Indisponível» ausente no caminho feliz |
| 10 | Help and documentation | 3 | Parágrafo do resumo explica snapshot vs terceiro backtest; ScreenHelpPanel do vivo omitido |

## Cognitive load

- Checklist: 1 h1 na grade; delta nas células existentes; 2 etiquetas distintas na análise. **Pass**.
- Pontos de decisão visíveis >4: não no glance da linha (3 ações, iguais ao vivo). Análise = leitura + Exportar. **Pass**.

## Emotional journey

Vale (promoveu e viu `-` / 0; no gráfico outro backtest e Max DD «Indisponível») → pico (linha `#193` com os números da Descoberta; resumo = snapshot) → fim (lista de 12 velas atuais rotulada, sem fingir os 30). Reassegurança: BTC combo-saved continua igual.

## Personas (2–3)

1. **Admin que acabou de promover na Descoberta:** precisa ver na grade o que viu no leaderboard. Células filled na mesma tabela resolvem o glance.
2. **Admin que reabre `#193` already-promoted (Q2=A):** não deve ter de promover de novo. A linha já mostra 0,31 / 30 / 46,7% / +16.951% / 16,5%.
3. **Admin teclado / SR na análise:** precisa distinguir 30 vs 12 sem tooltip. h1/h2 visíveis cobrem; o nome da estratégia deixa o h1 e vai ao parágrafo (P3).

## Strengths

- Clone estrutural da rota canónica (`table.fav-strategies` + 4 texts), não galeria nem ANTES/DEPOIS.
- Delta mínimo e no sítio certo (células já lidas + etiquetas na análise).
- Contrato Q1=A / Q2=A visível no estado padrão, desktop e mobile.
- Combo-saved como vizinho de regressão.
- Extra `analise.html` separado do index.

## Priority issues

Nenhum P0/P1 de produto/escopo/contrato visível.

## P0

(nenhum)

## P1

(nenhum)

## P2

(nenhum — classificação do skill: só P0/P1 de contrato visível vs P3 de Apply)

## P3 — detalhe de Apply (aceito; não reabrir como P0/P1)

- **Breakpoints da tabela:** proto `@media(max-width:1400px)` esconde select/telegram/period/stop; vivo 1540px esconde telegram/period/Win% e 1280px esconde `.risk-col` (Stop e Max DD). Apply preenche as células do vivo; não redesenha a grelha para «mostrar Win%/Max DD a 1280».
- **Chip + meta «Descoberta · RS-B109ED2C80 · #193»:** extra vs `getGridStrategyDetail` vivo (apelido). Não é coluna nova; não é obrigatório no Apply se a identidade já existir noutro sítio. Números nas chaves da grade são o contrato.
- **Mobile cards com Win% e Max DD:** vivo só TF/Sharpe/Trades/Return. Extra de densidade; non-goal «sem redesign mobile». Apply pode ficar nas 4 células vivas desde que a tabela desktop leia o snapshot.
- **`analise.html` omite** `StrategyRuleOverview`, painel de transparência, pill «Métricas», candlestick real; o h1 deixa de ser `combo-result-title` (nome da estratégia) e vira a etiqueta de janela. Apply: página viva + etiquetas visíveis no resumo e na lista; não copiar o SVG ilustrativo.
- **Formatadores / chaves JSON / flatten GET vs write:** já listados no `design.md` § Apply contract (P3). Proto usa `0,31` e `+16.951%` (copy do incidente); vivo `formatNum`/`formatSignedPct`/`formatPct` usam `toFixed` sem milhar. Reusar formatadores vivos.
- **Mock:** sem loading/vazio/erro; persistência pós-gráfico é HTML estático. Tasks 2.1–2.2 no Apply.
- **a11y residual:** alvos 28/32px e `Delete` só `title` = vivo.
- **Copy «Backtest aguardando atualização»:** chrome vivo de refresh pending. Fora deste card; não contradiz o aceite se o refresh não sobrescrever o snapshot.
- **`copied_utf8_sum`:** medição A (inner COPIED) 7438 B vs `design.md` 7642 B. Detalhe T5/contagem, não contrato de tela.
- **PF 1,42 / SQN 0,88** em `.advanced-col` (`display:none`, igual ao vivo). Só renderizar PF se o snapshot o tiver.

## Verdict

**Design Agent verdict: PASS**

Zero P0/P1 abertos. Tokens parseáveis. Clone canónico = `/favorites` + delta, não galeria. Contrato visível coberto no proto servido (digest idêntico) em desktop 1280 e mobile 390.

## Referências

- Proto canónico: https://dev.criptofarol.com.br/prototypes/card-897-discovery-promote-metrics/
- Extra: https://dev.criptofarol.com.br/prototypes/card-897-discovery-promote-metrics/analise.html
- Files: `frontend/public/prototypes/card-897-discovery-promote-metrics/index.html`, `analise.html`
- Design: `openspec/changes/card-897-discovery-promote-metrics/design.md`
- Catálogo: `scripts/process-fsm/route-landmarks.yaml` chave `/favorites`
- Vivo (fonte, sem sessão): `frontend/src/pages/FavoritesDashboard.tsx`, `frontend/src/pages/ComboResultsPage.tsx`, `frontend/src/index.css`
- Screenshots: `.impeccable/critique/card-897-index-desktop-1280x800.png`, `card-897-index-mobile-390x844.png`, `card-897-analise-desktop-1280x800.png`, `card-897-analise-mobile-390x844.png`
