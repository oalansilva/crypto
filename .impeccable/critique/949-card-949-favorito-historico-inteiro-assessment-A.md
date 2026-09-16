# Assessment A — card 949 · change card-949-favorito-historico-inteiro

> Avaliador A isolado (produto / UX / a11y / fidelidade do clone). Crítico independente, onda dupla com-tela. Sem transcript do pai. Sem nested-spawn. Sem edição de `design.md`, HTML proto, `backend/`, `frontend/src/` ou OpenSpec. Sem `process_event`. Sem arraste de Status. Única escrita: este arquivo + PNGs `949-A-*` + `949-A-gate.json`.

`proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)`

## Metadata

- card: 949 — "Ao salvar favorito após 70/30, gravar e mostrar o histórico inteiro"
- change: `card-949-favorito-historico-inteiro`
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-949-favorito-historico-inteiro`
- branch: `card-949-favorito-historico-inteiro`
- tuple: `bound_card=949` · `q_git=card-949-favorito-historico-inteiro` (resolver local; este filho não chama `process_event`)
- data (UTC): 2026-09-16T01:20Z
- Status observado: Design (bind do pai; REST `gh api repos/oalansilva/crypto/issues/949`, não `gh issue view`)
- UI impact (rubrica): **affected** · `live_route: /favorites` · `surface: existing` — linhas próprias 9–11 de `design.md` (parseáveis)
- Digest proto (esta sessão):

| ficheiro | sha256 | bytes |
|---|---|---|
| `index.html` | `0d87ecd5992a5aa343c4d2249209bb8d1d0a3ae4f9f5b487ec925beb369b97e4` | 48155 |
| `descoberta.html` | `03f0980e04646c001bdf25d31bc3408e1e14d39e8604ced05051877f644d08c8` | 67906 |
| `analise.html` | `2bc183850e855a183a166023488483f578a262ef58ec00a3bf335af5572e67ce` | 27023 |
| `combo.html` | `e4f16156b55a4a98083125e6fe718bfc778807bb2211d59d058e4cff5f4fb1ff` | 23263 |

- Servido HTTPS == local: IDENTICAL nos 4 HTML (HTTP 200)
- Issue: REST #949. Fronteira vazia. Q1/Q2/Q3 aceites 2026-09-15 — **não reabertas**.
- D4: com-tela = autor + dupla + 1 rework. Tokens verificados como item da rubrica — nenhuma rodada extra só para o parser.
- Ignore list: `.impeccable/critique/ignore.md` ausente
- Tooling: Playwright Python + Chromium 1148 (`/home/ubuntu/.cache/ms-playwright/chromium-1148/chrome-linux/chrome`), HTTPS real, viewports 1440×900 e 390×844. 0 console error / 0 pageerror.

## Limitação de sessão (obrigatória)

| URL pedida | URL final | h1 | Landmarks |
|---|---|---|---|
| `https://dev.criptofarol.com.br/favorites` | `https://dev.criptofarol.com.br/login` (HTTP 200) | `Bem-vindo de volta` | `table.fav-strategies` = 0 |
| `https://dev.criptofarol.com.br/combo/discovery` | `/login` | `Bem-vindo de volta` | 0 |
| `https://dev.criptofarol.com.br/combo/results` | `/login` | `Bem-vindo de volta` | 0 |
| `https://dev.criptofarol.com.br/combo/select` | `/login` | `Bem-vindo de volta` | `Available Templates` = 0 |

**`/login` não é a rota.** Chrome de login **não** é evidência de clone e **não** autoriza PASS de fidelidade. Sem cookie de administrador, a avaliação de clone usa: (1) protótipo canónico HTTPS, (2) HTML local, (3) fonte viva `FavoritesDashboard.tsx` / `DiscoveryPage` vs catálogo `scripts/process-fsm/route-landmarks.yaml`. Sidebar 224px / tokens `--bg-*` **não** bastam.

HTTP 200 isolado nunca é PASS. Os 200 do proto coincidem com digest e com asserts de landmark/contrato no browser.

## Tokens parseáveis (rubrica D4)

`design.md` linhas próprias 9–11:

```
UI impact: affected
live_route: /favorites
surface: existing
```

Justificativa no corpo: clone+delta Operate da rota existente `/favorites`; regiões clonadas marcadas (shell AppNav + workbench `table.fav-strategies` no index; extras `/combo/discovery` e `/combo/results`). **Não** empresta `/combo/select` nem `/monitor` como `live_route`. **PASS** deste item da rubrica. Nenhuma rodada extra nasce só para o parser.

## Digest proto (disco == HTTPS)

Disco == HTTPS: IDENTICAL nos 4 ficheiros. `design.md` Prototype Validation cita desktop+mobile nas 4 URLs públicas — esta sessão reabriu as mesmas URLs no Playwright e confirma.

## Fidelidade (clone da página viva)

Catálogo `/favorites` (`scripts/process-fsm/route-landmarks.yaml`): `selectors: ["table.fav-strategies"]` · texts `Estratégias favoritas`, `Symbol`, `Estratégia`, `Ações`.

Fonte viva `FavoritesDashboard.tsx` L1257 h1 + L1462 `table.fav-strategies` + thead Symbol / Estratégia / Ações (L1468–1483).

| Landmark | Vivo (`FavoritesDashboard.tsx`) | Proto + Playwright |
|---|---|---|
| `table.fav-strategies` | L1462 | desktop visível count=1; mobile no DOM, cards no lugar (clone do `@media max-width:1023px`) |
| `Estratégias favoritas` | h1 L1257 | h1 visível desktop e mobile |
| `Symbol` | th L1468 | thead desktop; filtro + tile BTC/SOL/ETH no mobile |
| `Estratégia` | th L1469 | thead desktop; nome da estratégia no card mobile |
| `Ações` | th L1483 | thead desktop; Analisar/Revalidar/Delete no card mobile |
| COPIED | — | index 4 pares; descoberta 11; analise 5; combo 5. copied > 0 |

Anti-padrões P0:

- URL canónica `…/prototypes/card-949-favorito-historico-inteiro/` → index **é** a página de Favoritos (shell 224px + workbench + tabela). **Não** é painel ANTES/DEPOIS. Botões Antes/Depois visíveis = 0. Texto visível `ANTES/DEPOIS` = 0.
- Não é grelha de N estados no lugar de lista. Três linhas na tabela viva = o catálogo com o delta (novo «todo», legado Q2, Combo 2 anos). Nunca um painel das N como URL canónica.
- Extras: `descoberta.html` = `/combo/discovery` (default Decidir); `analise.html` e `combo.html` = `/combo/results`. Sem `select.html`. `Available Templates` visível = 0. Sem extra `/monitor` (Monitor só no nav do shell).
- Tabs da Descoberta trocam markup (`aria-selected` + `aria-controls`). Default = Decidir.

Chrome presente (sidebar 224px desktop, Inter/Binance, Favoritos ativo, amarelo `#fcd535`) = **folha**, não prova. Prova = landmarks no proto, alinhados ao TSX.

## Produto (aceite visível — não reabrir Q1 / Q2 / Q3)

Contrato: favorito **novo** Descoberta «todo» = 17/08/2017 → 15/09/2026 (não o treino 17/08/2017 → 24/12/2023). Combo 2 anos + 70/30 = 15/09/2024 → 15/09/2026, **não** todo o histórico. Linha legado 2017→2023 intacta (Q2). Grelha Decidir continua 70/30. Modal promover **sem** preview. Lista/resumo/gráfico/atualização do novo = números do período completo — **não** misturar retrato da grelha com contagem do refresh sob o rótulo 2023-12-24.

Fora: #948, #917, Monitor, ranking 100%, migrar já salvos, preview no modal.

| Aceite visível | Evidência (Playwright 1440×900 e 390×844) | Disposition |
|---|---|---|
| BTC novo «todo» = 17/08/2017 → 15/09/2026 | célula `period-cell-btc-new` + status «atualizado até hoje»; mobile card idêntico. **Não** 24/12/2023 nesta linha. | OK |
| Métricas do novo = período completo, não a grelha | lista: Sharpe `0,38` · Trades `71` · Win% `54,9%` · Return `+210,40%`. Grelha BTC: `0,42` / `48` / `55,0%` / `+120,00%` / Calmar `18,40`. Sem 43 trades / Win 58,14% / 68 sob rótulo 2023. | OK |
| Legado Q2 intacto | SOL `17/08/2017 → 24/12/2023` desktop e mobile; não migrado. | OK |
| Combo 2 anos completo, não «todo» | ETH `15/09/2024 → 15/09/2026`; `+35,00%` / `22`. Sem 17/08/2017 nesta linha. | OK |
| Grelha Decidir 70/30 | default Decidir; retrato «treino 17/08/2017 → 24/12/2023»; GO na linha BTC; Calmar/cobertura da busca. | OK |
| Modal promover sem preview | cobertura `100% · 17/08/2017 → 24/12/2023`; Trades `48`; CAGR `8,1%`. `15/09/2026` ausente do modal. | OK |
| Análise do novo ≠ título de treino | h1 `Resumo · histórico inteiro · 17/08/2017 → 15/09/2026`; métricas `+210,40%` / `54,9%` / `71` / `28,10%`. `janela de treino da Descoberta` = 0. | OK |
| Combo save 2 anos | «Salvar nos Favoritos»; chip `70/30 na busca`; modal «Período a gravar: **15/09/2024 → 15/09/2026** (2 anos completos)». Não amplia a 2017. | OK |
| `/combo/select` sem copy deste card | nenhum `select.html`; `Available Templates` = 0 nos quatro HTML. | OK |
| Monitor / #948 / #917 / ranking 100% fora | 0 cards Monitor; setas #917 não são o delta; grelha continua Calmar/70/30. | OK |

Q1/Q2/Q3 **não reabertas**. O copy «não o treino 17/08/2017 → 24/12/2023» na análise é negação explícita, não misturar retrato com desempenho.

## UX

Hierarquia: AppNav → h1 Estratégias favoritas → tiers → filtros → lista. Job único: ver o período gravado na linha nova vs legado vs Combo 2 anos.

Carga: 3 linhas é o contrato (novo / Q2 / Q3), não um wall of options. Glance: datas na coluna Período (desktop) e no card (mobile). Números do novo (71 / +210,40%) não colidem com os da grelha (48 / +120%).

Delta óbvio sem redesign: a linha BTC deixa de acabar em 24/12/2023; a ETH fica em 2 anos; a SOL legado não se mexe.

## Acessibilidade

- `lang=pt-BR`; `:focus-visible`; `prefers-reduced-motion`.
- Landmarks: `nav` + `main`; tabela `fav-strategies`; extras com `aria-label="Análise da estratégia"` / tablist Descoberta.
- Selo GO/NO-GO e N/A são texto, não só cor.
- Modal promover: `role=dialog` + `aria-modal` + título. Sem preview extra a anunciar.
- Alvos 32px nos ícones da linha e 28px nas estrelas = clone vivo / P3 já no `design.md`. Não esconde o período nem troca 71 por 48.
- Contraste: pares Binance; verde/vermelho só em Return/Max DD.

## Responsividade

- Desktop 1440×900: sidebar 224px; tabela visível; três períodos e três jogos de métricas no thead. Overflow-x index = 0. PNG `949-A-desktop-1440x900-index.png`.
- Mobile 390×844: sidebar 0; header 72px; cards com as mesmas datas/números. Overflow-x = 0. PNG `949-A-mobile-390x844-index.png`.
- Descoberta a 1440: coluna Ação («Promover») clipa à direita com sidebar 224px — incumbente do clone #944, não delta deste card.

## Estados

Mock cobre: lista com novo + legado + Combo 2 anos; Decidir 70/30 + modal sem preview; análise «todo»; Combo 2 anos + save. Não mocka: loading/vazio/erro, 6 meses, Combo sem 70/30 (fora). Cobertura de mock = P3.

## Design specificity

A tela é Favoritos do Cripto Farol depois de 70/30 (período operacional ≠ treino da busca). Não iria a um SaaS genérico inalterado. Modo Impeccable: **Operate** / refinement. Folha Binance; `DESIGN.md` não reescrito.

## Heurísticas Nielsen (0–4, Operate; só neste snapshot)

| # | Heurística | Score | Nota |
|---|---|---|---|
| 1 | Visibility of system status | 4 | «atualizado até hoje» na linha nova; chip 70/30 no Combo; Decidir selecionado |
| 2 | Match between system and real world | 4 | «todo» = primeira vela → agora; 2 anos = 2 anos; treino fica na grelha |
| 3 | User control and freedom | 3 | Voltar / Fechar nos modais; filtros do vivo cosméticos no mock |
| 4 | Consistency and standards | 4 | Lista, resumo e gráfico do novo partilham 71 / +210,40% / 15/09/2026 |
| 5 | Error prevention | 4 | Modal promover sem preview que minta o completo; Combo save nomeia os 2 anos |
| 6 | Recognition rather than recall | 4 | Três linhas na mesma lista; operador não memoriza o treino |
| 7 | Flexibility and efficiency | 3 | Atalhos/paginação do vivo omitidos no mock |
| 8 | Aesthetic and minimalist design | 3 | Clone denso de Favoritos; truncagem da Estratégia (table-layout fixed vivo) |
| 9 | Help users recognize/recover errors | n/a | Sem formulário neste fluxo (modais de confirmação, não input) |
| 10 | Help and documentation | 3 | Nota do retrato 70/30; disclaimer educacional; Ajuda no nav |
| **Total** | | **32/36** | **Good** (heurística 9 n/a) |

## Cognitive load

Checklist: 1 h1; 1 lista; 3 linhas = os 3 casos do contrato. **Pass** (0–1 falhas). Decisão no glance ≤4 (abrir análise da linha nova). Grelha Decidir continua o job de ranking, separado.

## Emotional journey

Vale (favorito «todo» preso em 24/12/2023) → pico (17/08/2017 → 15/09/2026 + 71 negócios) → fim (legado intacto; Combo 2 anos não vira 2017). Reassegurança: modal promover ainda mostra o retrato da busca, não um segundo número a competir.

## Personas

1. **Alex (operador, veio da Descoberta):** promove BTC; na lista lê 17/08/2017 → 15/09/2026 e 71 / +210,40%, não 48 / +120% da grelha.
2. **Riley (stress Q2/Q3):** SOL legado continua 24/12/2023; ETH Combo continua 15/09/2024 → 15/09/2026, sem 2017.
3. **Casey (mobile):** cards 390×844 repetem as três datas e os três jogos de métricas; Analisar na linha nova abre a análise completa.

## Strengths

- Clone estrutural de `/favorites`, não galeria ANTES/DEPOIS.
- Delta mínimo e óbvio: três linhas, três contratos (novo / legado / 2 anos).
- Q1 visível: números do completo na lista **e** no resumo/gráfico.
- Q2 visível: linha já salva não migra.
- Q3 visível: Combo 2 anos não vira histórico inteiro; «Salvar nos Favoritos» nomeia o período.
- Modal promover sem preview (non-goal respeitado).

## Playwright (esta sessão)

- Desktop 1440×900 e mobile 390×844: aceite visível 10/10 PASS. 0 console / 0 pageerror.
- Live `/favorites` `/combo/discovery` `/combo/results` `/combo/select` → `/login` (descartado).
- Detector `detect.mjs`: `side-tab` ×3 em `index.html` L149–151 (cards mobile de tier) — incumbente do clone, P3 já no `design.md`. `descoberta.html` / `analise.html` / `combo.html` = `[]`.
- PNGs: `949-A-desktop-1440x900-{index,descoberta,descoberta-modal,descoberta-montar,analise,combo,combo-modal}.png`, `949-A-mobile-390x844-{index,descoberta,descoberta-modal,descoberta-montar,analise,combo,combo-modal}.png`, `949-A-live-favorites.png`. Gate: `949-A-gate.json`.

## Prototype Validation (rubrica 6)

`design.md` secção Prototype Validation presente: Playwright desktop+mobile, 8/8 PASS declarado pelo autor. Esta sessão **reexecutou** o browser nas 4 URLs públicas e confirma o mesmo aceite visível. Curl 200 não substituiu o Playwright.

## Priority issues

Nenhum P0/P1 de produto/escopo/contrato visível.

## P0

_(nenhum)_

## P1

_(nenhum)_

## P2

_(nenhum)_

## P3 — detalhe de Apply / clone de região fora do delta

- **P3-1** Detector `side-tab` nos cards mobile de tier (`border-left:3px`) — incumbente do clone `/favorites`. Já aceite em `design.md` Apply contract.
- **P3-2** Alvos 32px nos ícones da linha e 28px nas estrelas — clone vivo; já no contrato Apply.
- **P3-3** Análise: label «71 negócios» vs 33 `<tr>` mock (1…33, última = 17/08/2017). Já no Apply «#917 setas; 32 vs 33 negócios». Não mistura 48/55% da grelha com 71 sob rótulo 2023.
- **P3-4** Descoberta a 1440×900: coluna Ação clipa «Promover» com sidebar 224px — clone #944, não delta deste card.
- **P3-5** Truncagem do nome na coluna Estratégia (`table-layout: fixed` vivo). Já no Apply.
- **P3-6** CSS vars do proto (`--accent`) vs folha (`--accent-primary`); hex Binance bate. Nav 42px = clone de shell.
- **P3-7** Gráfico ilustrativo SVG (não `StrategyChartSurface` / setas). #917 fora.
- **P3-8** Mock sem loading/vazio/erro; Combo 6 meses não mockado (contrato 2 anos basta). Mecanismo (segundo backtest vs datas abertas vs `end_date` nulo) = Apply, desde que a tela mostre o completo.
- **P3-9** Extra Descoberta traz DELTA de ordem de colunas #944 (clone do vivo actual). Não é copy de `/combo/select`.

## Disposition

Aceitar P3 no Apply. Não reabrir grelha. Não reabrir Q1 / Q2 / Q3. Não exigir segundo rework de Design por estes itens. Não promover `side-tab` / 32px / 33 vs 71 / clip da Ação a P0/P1.

## Verdict

**PASS** — zero P0/P1 de produto/escopo/contrato visível. Tokens parseáveis 3/3. Landmarks `/favorites` no index. Disco == HTTPS. Sem galeria/ANTES-DEPOIS como index. copied > 0. Delta = período/números do favorito novo + legado intacto + Combo 2 anos. `/login` descartado. Clone **não** alegado só por sidebar: prova = landmarks proto × `FavoritesDashboard.tsx`. BTC novo `17/08/2017 → 15/09/2026` · 71 · +210,40% ≠ grelha 48 · +120% · 24/12/2023. Modal promover sem 15/09/2026. Combo save `15/09/2024 → 15/09/2026`.

`Design Agent verdict` final da coluna = síntese do pai após A+B. Este filho A não chama `process_event`.

---

```
Assessment A 949
tokens_ok: yes
clone_ok: yes
P0: nenhum
P1: nenhum
P3: side-tab cards tier; alvos 32/28px; 33 tr vs 71 negócios; Ação Promover clip 1440; truncagem Estratégia; CSS vars / nav 42px; SVG vs #917; mock sem loading; DELTA colunas #944 no extra Descoberta
verdict: PASS
```
