# Assessment A — card 906 · change card-906-discovery-metrics-grid

> Avaliador A isolado (produto / UX / a11y / fidelidade do clone). Mesmo modelo do chat. Sem transcript do pai. Sem nested-spawn. Sem edição de `design.md`, HTML proto, `backend/`, `frontend/src/` ou OpenSpec. Sem `process_event`. Única escrita: este arquivo + PNGs `906-A-*`.

## Metadata

- card: 906 — "detalhamento das metricas na tela de descoberta"
- change: `card-906-discovery-metrics-grid`
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-906-discovery-metrics-grid`
- data (UTC): 2026-09-12T13:30Z
- Status observado: Design
- UI impact (rubrica): **affected** · `live_route: /combo/discovery` · `surface: existing` — linhas próprias 1–3 de `design.md` (parseáveis)
- Digest proto (autor, verificado nesta sessão): sha256 `1e7121225d6cb339e127657c463626dbfed13d751be6bda9d1fcfe84a723c8fc` · 45186 bytes
- Servido HTTPS == local: IDENTICAL (`cmp` limpo; prefixo `1e7121225d6cb339`)
- Issue: REST `gh api repos/oalansilva/crypto/issues/906` (não `gh issue view`). Q1=A · Q2=A travadas; fronteira vazia; não reaberta.
- D4: com-tela = autor + dupla + 1 rework. Tokens verificados como item da rubrica — nenhuma rodada extra só para o parser.
- Snapshot do autor lido: `.impeccable/critique/906-card-906-discovery-metrics-grid.md`
- Ignore list: `.impeccable/critique/ignore.md` ausente.

## Limitação de sessão (obrigatória)

Browser MCP Cursor não manteve tab (`navigate` / `viewId` falharam). Inspeção visual desta sessão = Playwright Chromium 1243 (`executable_path` cache `chrome-linux-arm64`), HTTPS real, viewports 1440×900 e 390×844. 0 console error / 0 pageerror.

| URL pedida | URL final | h1 | Landmarks `/combo/discovery` |
|---|---|---|---|
| `https://dev.criptofarol.com.br/combo/discovery` | `https://dev.criptofarol.com.br/login` (HTTP 200) | `Bem-vindo de volta` | 0/3 |

**`/login` não é a rota.** Chrome de login **não** é evidência de clone e **não** autoriza PASS de fidelidade. Sem cookie de administrador, a avaliação de clone usa: (1) protótipo canónico HTTPS, (2) HTML local, (3) fonte viva `frontend/src/pages/DiscoveryPage.tsx` vs catálogo `scripts/process-fsm/route-landmarks.yaml`. Sidebar 224px / tokens `--bg-*` **não** bastam.

## Tokens parseáveis (rubrica D4)

`design.md` linhas próprias 1–3:

```
UI impact: affected
live_route: /combo/discovery
surface: existing
```

Justificativa no corpo: clone+delta Operate da rota existente; regiões clonadas marcadas («só estas»: shell AppNav + heading + 3 modos + grelha Acompanhar + grelha Decidir; Montar só landmarks, sem delta de colunas). **PASS** deste item da rubrica.

## Digest proto (disco == HTTPS)

| Ponta | sha256 | bytes | HTTP |
|---|---|---|---|
| disco `frontend/public/prototypes/card-906-discovery-metrics-grid/index.html` | `1e7121225d6cb339e127657c463626dbfed13d751be6bda9d1fcfe84a723c8fc` | 45186 | — |
| HTTPS `https://dev.criptofarol.com.br/prototypes/card-906-discovery-metrics-grid/` | `1e7121225d6cb339e127657c463626dbfed13d751be6bda9d1fcfe84a723c8fc` | 45186 | 200 |
| `design.md` Prototype / prompt do pai | prefixo `1e7121225d6cb339` · completo igual | 45186 | — |

`cmp` disco vs `/tmp/card906-proto.html`: identical.

## Fidelidade (clone da página viva)

Catálogo `/combo/discovery` (`scripts/process-fsm/route-landmarks.yaml`): `selectors: []` · texts `Descoberta de estratégias swing`, `Preflight`, `Rascunho de varredura`.

| Landmark | `DiscoveryPage.tsx` (vivo, sem sessão) | Proto + Playwright |
|---|---|---|
| `Descoberta de estratégias swing` | h1 L1357 + subcopy 4h/1d | h1 visível no default Acompanhar (desktop e mobile); exact 1 |
| `Preflight` | `aria-label="Preflight da varredura"` L1980 + h2 `Preflight` L1983 | hidden no default Acompanhar (painel inativo, igual ao vivo com sweep); **visível após tab Montar** |
| `Rascunho de varredura` | h2 L1823 em tabpanel Montar | article `aria-label="Rascunho de varredura"` + h2; **visível após tab Montar** |

Anti-padrões P0:

- URL canónica `…/prototypes/card-906-discovery-metrics-grid/` → index é a página (shell 224px + heading + 3 modos + Acompanhar + Decidir). **Não** é painel ANTES/DEPOIS. Botões Antes/Depois = 0. `getByText('ANTES/DEPOIS')` visível = 0 (o comentário de fonte «Sem painel ANTES/DEPOIS» não conta como galeria).
- Não é grelha de N estados no lugar de lista+detalhe. Acompanhar = tabela de parciais (5 linhas). Decidir = tabela de candidatos (4 linhas mock).
- Tabs trocam markup (`.modepanel.active` + `aria-selected` + `aria-controls`). Não é `aria-pressed` cosmético.
- 10 pares `COPIED:start/end` (copied > 0). Delta óbvio = **3 colunas novas** (Sharpe, Win%, CAGR) depois de Trades/cobertura nas duas grelhas (`DELTA:start` ×2). TSX vivo ainda tem só Calmar / Max DD / Trades no thead (L1759–1769 e L2319–2331); Sharpe/Win/CAGR no vivo ainda moram em «+ detalhes» (L2398–2400). Proto = depois.

Chrome presente (sidebar 224px, Inter, `--bg-primary:#0b0e11`, amarelo `#fcd535`, nav Descoberta ativa) = **folha**, não prova. Prova = landmarks 3/3 no proto, alinhados ao TSX.

Tab default = Acompanhar (`#tab-acomp aria-selected=true`; rótulo vivo `Acompanhando #…` L1405, não «Acompanhamento»).

## Produto (aceite visível — não reabrir grelha / Q1 / Q2)

Delta pedido: seis colunas fáceis no Acompanhar e no Decidir sem expandir; CAGR anualizado da varredura ≠ Return de Favoritos; amostra insuficiente → N/A também em Sharpe / Win% / CAGR. Fora: Favoritos, Montar (grelha), ordenar por Sharpe, motor, GO/NO-GO.

| Aceite visível | Evidência (Playwright + pixels) | Disposition |
|---|---|---|
| Acompanhar top-5: 6 colunas sem expandir | thead `Calmar / Max DD / Trades/cobertura / Sharpe / Win% / CAGR` (hints `CAGR ÷ Max DD`, `negócios · velas`, `acerto`, `anualizado`). `expand_in_acomp=0`. Linha 1: `22,53` · `−16,5%` · `30 · 100%` · Sharpe `0,31` · Win% `46,7%` · CAGR `17,8%`. | OK |
| Decidir: mesmo conjunto no mesmo sítio | thead idêntico + Ação. Sharpe `0,31` e CAGR `17,8%` visíveis com «+ detalhes» ainda collapsed (`display:none`). | OK |
| CAGR ≠ Return Favoritos | célula `17,8%` (sem `+`); `+47.916%` count = 0. Hint `anualizado`. `aria-label` «Retorno (CAGR) anualizado da varredura». | OK |
| Amostra insuficiente: 6× N/A | selo exact `Amostra insuficiente`; rank `—`; Sharpe/Win%/CAGR `N/A`; Promover = 0; Excluir = 1. | OK |
| Sort só Calmar e CAGR vs B&H | options exact `Calmar` · `CAGR vs B&H`. Sem Sharpe/Win%/CAGR como chave. | OK |
| «+ detalhes» guarda extras, não é o único sítio | `none→block`; texto `B&H 8,4% · Δ +9,4 p.p. · PF 1,12 · mercado … janela […]`. Sem Sharpe/Win%/CAGR na expansão. Colunas continuam visíveis. | OK |
| Montar sem grelha de métricas | após tab: Preflight + Rascunho visíveis; `table.lb=0`; `th Sharpe=0`. | OK |
| Não entra Favoritos / motor / ordenar Sharpe | Favoritos só no nav (clone de shell). Selos GO/NO-GO são clone #896, não delta deste card. | OK |

Linha Acompanhar rank 5: Calmar `N/A` com Max DD/Trades finitos e Sharpe/Win%/CAGR `N/A` — contrato de tasks 1.2 (porta do Calmar não-finito), não mistura com amostra insuficiente do Decidir.

## UX

Hierarquia: h1 → tablist 3 modos → 1 painel. Default Operate = Acompanhar em curso. Glance: as três novas alinham-se às três antigas; comparar duas linhas não exige «+ detalhes». Win% `46,7%` não colide com `30 · 100%` (hints `acerto` vs `negócios · velas`). CAGR percent vs Calmar razão.

Carga: 6 números é o job (Q2=A). Desktop overflow-x (`min-width:1080px`); mobile cards em pares com `data-label`. Decidir por linha elegível = 2 (Promover/Excluir); insuficiente = 1 (Excluir). Tablist = 3.

## Acessibilidade

- `lang=pt-BR`; `:focus-visible`; alvos ≥44px; `prefers-reduced-motion`.
- Tablist/tab/tabpanel + `aria-controls`. Região de tabela `tabindex=0`.
- Headers novos com `aria-label` (Sharpe; Win rate (taxa de acerto); Retorno (CAGR) anualizado da varredura) — não só `title`.
- Caption sr-only no Decidir nomeia CAGR anualizado vs acerto vs Calmar.
- Selo `Amostra insuficiente` é texto, não só cor. N/A é texto.
- Contraste: pares Binance (`DESIGN.md` não reescrito). Verde/vermelho só em performance (CAGR pos / Max DD neg); ciclo EM CURSO azul/info.

## Responsividade

- Desktop 1440×900: seis colunas no thead sem cortar candidato; Ação à direita no Decidir. PNGs `906-A-desktop-1440x900-{acomp,decidir,montar}.png`.
- Mobile 390×844: tablist 3 colunas; tabela → cards `data-label`; as seis métricas permanecem visíveis (Calmar/Max DD, Trades/Sharpe, Win rate/Retorno CAGR) mesmo com «− detalhes» aberto. Header mobile 72px (folha). PNG `906-A-mobile-390x844-{acomp,decidir,montar}.png`.
- Sem overflow bloqueante do delta. 0 console / 0 pageerror.

## Estados

Mock cobre: Acompanhar em curso com 5 parciais (4 finitas + 1 Calmar N/A); Montar rascunho (landmarks); Decidir misto (promovido, GO com Promover, amostra insuficiente, NO-GO elegível). Não mocka: Baixa amostra vizinha, loading/erro de leaderboard, vazio, filtros a filtrar de verdade. Cobertura de mock = P3, não buraco do contrato visível.

## Design specificity

Composição da Descoberta (modos #852, parciais top-5, leaderboard Calmar, selo de amostra). Não poderia ir a um SaaS genérico inalterado. Modo Impeccable: **Operate** / refinement. Folha Binance; `DESIGN.md` não reescrito.

## Heurísticas Nielsen (0–4, Operate; só neste snapshot)

| # | Heurística | Score | Nota |
|---|---|---|---|
| 1 | Visibility of system status | 4 | Chip EM CURSO + 248/697 + tab Acompanhando |
| 2 | Match between system and real world | 4 | Vocabulário da grelha; CAGR anualizado ≠ Return; Win% ≠ Trades |
| 3 | User control and freedom | 3 | Tabs + Pausar/Cancelar/Excluir; filtros/modais do vivo omitidos |
| 4 | Consistency and standards | 4 | Mesmo conjunto Acompanhar/Decidir; hints alinhados |
| 5 | Error prevention | 4 | Insuficiente sem Promover; N/A nas seis; sort sem Sharpe |
| 6 | Recognition rather than recall | 4 | Seis números em coluna; «+ detalhes» deixa de ser memória |
| 7 | Flexibility and efficiency | 3 | Sort real / paginação / atalhos do vivo omitidos no mock |
| 8 | Aesthetic and minimalist design | 3 | Densidade 6 colunas aceite; Montar esquelético |
| 9 | Help users recognize/recover errors | 3 | N/A + selo; sem modal Excluir do vivo |
| 10 | Help and documentation | 3 | Hints no thead + nota educacional; Ajuda fora |
| **Total** | | **35/40** | **Good** |

## Cognitive load

Checklist: 1 h1; 1 modo visível; delta nas colunas já nomeadas. **Pass** (chunking de 6 números = carga intrínseca do Q2=A, não ruído). Decisões visíveis no glance Acompanhar ≤4 (tabs + Pausar/Cancelar/Novo rascunho). Decidir elegível = 2 CTAs.

## Emotional journey

Vale (abrir linha a linha no Decidir / cego no Acompanhar) → pico (Sharpe/Win%/CAGR alinhados entre vizinhos) → fim (insuficiente continua N/A, sem Promover). Reassegurança: Calmar/Max DD/Trades não saem; «+ detalhes» ainda guarda B&H/PF/janela.

## Personas

1. **Alex (operador Acompanhar):** lê top-5 Sharpe `0,31` / Win% `46,7%` / CAGR `17,8%` sem expandir; rank 5 N/A nas novas.
2. **Alex (Decidir):** escolhe promover com as seis colunas; sort continua Calmar; insuficiente sem CTA.
3. **Sam (teclado / SR):** landmarks 3/3 após Montar; `aria-label` das colunas novas; N/A textual.

## Strengths

- Clone estrutural da rota (`/combo/discovery`), não galeria ANTES/DEPOIS.
- Delta mínimo e óbvio: exactamente 3 colunas depois de Trades, nos dois modos.
- Q1=A visível: `17,8%` anualizado, não Return `+47.916%`.
- Non-goals visíveis respeitados (Montar sem grelha; sort intacto; Favoritos só nav).

## Playwright (esta sessão)

- Desktop 1440×900 e mobile 390×844: aceite visível 8/8 PASS. Landmarks Montar visíveis após tab. `+ detalhes` `none→block` sem duplicar as três novas. 0 console / 0 pageerror.
- Live `/combo/discovery` → `/login` (descartado).
- PNGs: `906-A-desktop-1440x900-{acomp,decidir,montar}.png`, `906-A-mobile-390x844-{acomp,decidir,montar}.png`, `906-A-live-combo-discovery.png`.

## Priority issues

Nenhum P0/P1 de produto/escopo/contrato visível.

## P0

_(nenhum)_

## P1

_(nenhum)_

## P2

_(nenhum)_

## P3 — detalhe de Apply / clone de região fora do delta

- **P3-1** Montar condensado vs vivo: sem Iniciar, workbench, checkboxes 4h/1d, período/ranking, impedimentos/`<details>`. Landmarks Preflight + Rascunho presentes. Apply lê `DiscoveryPage.tsx` para Montar intacto.
- **P3-2** `min-width` da `.discovery-table` / não herdar `th:last-child` left no Acompanhar (último passa a CAGR) — já aceito em `design.md` Apply contract.
- **P3-3** Mobile `data-label` das novas: `Win rate` (EN) e `Retorno (CAGR)` vs header `Win%` / `CAGR`. `Maximum Drawdown` já era o padrão vivo. Não esconde métrica.
- **P3-4** Decidir mock: 4 `<tr>` vs copy «248 de 248 · página 1 de 21»; filtros/paginação cosméticos; sem vizinha `Baixa amostra`; `Excluir` sem `aria-label` com `result_id`; modais Promover/Excluir omitidos.
- **P3-5** CSS vars do proto (`--accent`, `--border`) vs folha (`--accent-primary`, `--border-default`); hex Binance bate.
- **P3-6** Chip NO-GO residual `display:block` na coluna candidato (especificidade `.candidate span` vs `.verdict`) — clone #896, não delta de colunas.
- **P3-7** `fmtPct` / `fmtNum` nas células novas; não duplicar Sharpe/Win%/CAGR na string de «+ detalhes» — já no contrato Apply.

## Disposition

Aceitar P3 no Apply. Não reabrir grelha. Não reabrir Q1=A / Q2=A. Não exigir segundo rework de Design por estes itens.

## Verdict

**PASS** — zero P0/P1 de produto/escopo/contrato visível. Tokens parseáveis 3/3. Landmarks 3/3 no proto (Montar para Preflight/Rascunho). Disco == HTTPS. Sem galeria/ANTES-DEPOIS como index. copied > 0 (10 pares). Delta = 3 colunas novas. `/login` descartado. Clone **não** alegado só por sidebar: prova = landmarks proto × `DiscoveryPage.tsx`.

`Design Agent verdict` final da coluna = síntese do pai após A+B. Este filho A não chama `process_event`.

---

```
Assessment A 906
tokens_ok: yes
clone_ok: yes
P0: nenhum
P1: nenhum
P3: Montar condensado; min-width/th:last-child; data-label EN Win rate; mock 248/4 linhas + filtros cosméticos + sem Baixa amostra; CSS vars; chip NO-GO block; fmtPct/fmtNum Apply
verdict: PASS
```
