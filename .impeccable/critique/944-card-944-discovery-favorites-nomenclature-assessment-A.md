# Assessment A — card 944 · change card-944-discovery-favorites-nomenclature

> Avaliador A isolado (produto / UX / a11y / fidelidade do clone). Mesmo modelo do chat (Grok 4.6). Sem transcript do pai. Sem nested-spawn. Sem edição de `design.md`, HTML proto, `backend/`, `frontend/src/` ou OpenSpec. Sem `process_event`. Sem arraste de Status. Única escrita: este arquivo + PNGs `944-A-*` (+ JSON de gate).

`proxy modelo: Assessment A → Grok 4.6`

## Metadata

- card: 944 — "dados iguais a favoritos"
- change: `card-944-discovery-favorites-nomenclature`
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-944-discovery-favorites-nomenclature`
- branch: `card-944-discovery-favorites-nomenclature`
- tuple: `bound_card=944` · `q_git=card-944-discovery-favorites-nomenclature` (resolver local; `process-fsm-page.md` ausente)
- data (UTC): 2026-09-14T20:56Z
- Status observado: Design (Project 1 item `PVTI_lAHOAAHtBM4BV8b2zg66i2o`)
- UI impact (rubrica): **affected** · `live_route: /combo/discovery` · `surface: existing` — linhas próprias 1–3 de `design.md` (parseáveis)
- Digest proto (autor, verificado nesta sessão): sha256 `e8e632a2d44c34ac7e93674adad5599f3a2b159ac6a0a57ae6a38640c8f44ed3` · 65246 bytes · prefixo `e8e632a2d44c34ac`
- Servido HTTPS == local: IDENTICAL (`sha256` e bytes iguais; HTTP 200)
- Issue: REST `gh api repos/oalansilva/crypto/issues/944` (não `gh issue view`). Grill: fronteira vazia. Q1 = só nomes e ordem · Q2 = parciais E leaderboard · Q3 = CAGR anualizado no final com nome próprio — fechadas no design; **não reabertas**.
- D4: com-tela = autor + dupla + 1 rework. Tokens verificados como item da rubrica — nenhuma rodada extra só para o parser.
- Ignore list: `.impeccable/critique/ignore.md` ausente
- Tooling: Playwright Python + Chromium 1243 (`executable_path` cache `chrome-linux-arm64`), HTTPS real, viewports 1440×900 e 390×844. 0 console error / 0 pageerror.

## Limitação de sessão (obrigatória)

| URL pedida | URL final | h1 | Landmarks `/combo/discovery` |
|---|---|---|---|
| `https://dev.criptofarol.com.br/combo/discovery` | `https://dev.criptofarol.com.br/login` (HTTP 200) | `Bem-vindo de volta` | 0/3 |

**`/login` não é a rota.** Chrome de login **não** é evidência de clone e **não** autoriza PASS de fidelidade. Sem cookie de administrador, a avaliação de clone usa: (1) protótipo canónico HTTPS, (2) HTML local, (3) fonte viva `frontend/src/pages/DiscoveryPage.tsx` vs catálogo `scripts/process-fsm/route-landmarks.yaml`. Sidebar 224px / tokens `--bg-*` **não** bastam.

HTTP 200 isolado nunca é PASS. Os 200 do proto coincidem com digest e com asserts de landmark/contrato no browser.

## Tokens parseáveis (rubrica D4)

`design.md` linhas próprias 1–3:

```
UI impact: affected
live_route: /combo/discovery
surface: existing
```

Justificativa no corpo: clone+delta Operate da rota existente `/combo/discovery`; regiões clonadas marcadas («só estas»: shell AppNav + heading + 3 modos + grelha Acompanhar (parciais) + grelha Decidir (leaderboard); Montar só landmarks, sem delta de colunas). **PASS** deste item da rubrica. Nenhuma rodada extra nasce só para o parser.

## Digest proto (disco == HTTPS)

| Ponta | sha256 | bytes | HTTP |
|---|---|---|---|
| disco `frontend/public/prototypes/card-944-discovery-favorites-nomenclature/index.html` | `e8e632a2d44c34ac7e93674adad5599f3a2b159ac6a0a57ae6a38640c8f44ed3` | 65246 | — |
| HTTPS `https://dev.criptofarol.com.br/prototypes/card-944-discovery-favorites-nomenclature/` | `e8e632a2d44c34ac7e93674adad5599f3a2b159ac6a0a57ae6a38640c8f44ed3` | 65246 | 200 |
| `design.md` Prototype / prompt do pai | prefixo `e8e632a2d44c34ac` · completo igual | 65246 | — |

Disco == HTTPS: IDENTICAL.

## Fidelidade (clone da página viva)

Catálogo `/combo/discovery` (`scripts/process-fsm/route-landmarks.yaml`): `selectors: []` · texts `Descoberta de estratégias swing`, `Preflight`, `Rascunho de varredura`.

| Landmark | `DiscoveryPage.tsx` (vivo, sem sessão) | Proto + Playwright |
|---|---|---|
| `Descoberta de estratégias swing` | h1 L1471 + subcopy 4h/1d | h1 visível no default Acompanhar (desktop e mobile); exact 1 |
| `Preflight` | `aria-label="Preflight da varredura"` L2137 + h2 `Preflight` L2140 | hidden no default Acompanhar (painel inativo, igual ao vivo com sweep); **visível após tab Montar** |
| `Rascunho de varredura` | h2 L1980 em tabpanel Montar | article `aria-label="Rascunho de varredura"` + h2; **visível após tab Montar** |

Anti-padrões P0:

- URL canónica `…/prototypes/card-944-discovery-favorites-nomenclature/` → index é a página (shell 224px + heading + 3 modos + Acompanhar + Decidir). **Não** é painel ANTES/DEPOIS. Botões Antes/Depois = 0. `getByText('ANTES/DEPOIS')` visível = 0 (o comentário de fonte «Sem painel ANTES/DEPOIS» não conta como galeria).
- Não é grelha de N estados no lugar de lista+detalhe. Acompanhar = tabela de parciais (5 linhas). Decidir = tabela de candidatos (4 linhas mock).
- Tabs trocam markup (`.modepanel.active` + `aria-selected` + `aria-controls`). Não é `aria-pressed` cosmético.
- 11 pares `COPIED:start/end` (copied > 0). Delta óbvio = **ordem e nomes** nas duas grelhas (`DELTA:start` ×5: thead parciais, Ação parciais, thead Decidir, diálogos reutilizados). TSX vivo ainda tem Calmar / Max DD / `Trades/cobertura` / Sharpe / Win% / CAGR no thead (L1875–1894 e L2479–2498); Return **não existe** no vivo. Proto = depois.

Chrome presente (sidebar 224px, Inter, `--bg-primary:#0b0e11`, amarelo `#fcd535`, nav Descoberta ativa) = **folha**, não prova. Prova = landmarks 3/3 no proto, alinhados ao TSX.

Tab default = Acompanhar (`#tab-acomp aria-selected=true`; rótulo vivo `Acompanhando #…` L1519, não «Acompanhamento»).

## Produto (aceite visível — não reabrir Q1 / Q2 / Q3)

Delta pedido: nomes e ordem iguais a Favoritos nas duas grelhas, sem expandir; Return existe e é distinto de CAGR; Trades não se chama Trades/cobertura; extras Calmar (CAGR ÷ Max DD) e CAGR anualizado no final. Fora: números iguais a Favoritos, grade inteira de Favoritos, Favoritos, Montar (grelha), ranking/filtros/ordenar/GO-NO-GO, #897.

Contrato visível: Sharpe → Trades → Win% → Return → Max DD → Calmar (CAGR ÷ Max DD) → CAGR anualizado.

| Aceite visível | Evidência (Playwright + pixels) | Disposition |
|---|---|---|
| Acompanhar top-5: sete métricas na ordem de Favoritos, sem expandir | thead `Sharpe / Trades / Win% / Return / Max DD / Calmar / CAGR anualizado` (hints `cobertura`, `acerto`, `janela`, `CAGR ÷ Max DD`). `expand_in_acomp=0`. Linha ALPHA: Sharpe `0,31` · Trades `30` + `100% velas` · Win% `46,7%` · Return `+12,8%` · Max DD `−16,5%` · Calmar `22,53` · CAGR anualizado `3,7%`. | OK |
| Decidir: mesmo conjunto no mesmo sítio | thead idêntico + Ação. Return `+12,8%` e CAGR `3,7%` visíveis com «+ detalhes» ainda collapsed (`display:none`). | OK |
| Return ≠ CAGR ≠ Return de Favoritos | ALPHA Return `+12,8%` (com `+`) vs CAGR anualizado `3,7%` (sem `+`). `+16.951%` / `+47.916%` count = 0. Hint Return = `janela`. `aria-label` «Return (retorno composto da janela da varredura)» vs «CAGR anualizado da varredura». | OK |
| Trades ≠ Trades/cobertura | `th` exact `Trades/cobertura` = 0 nas duas grelhas. Hint `cobertura`; célula `30` + subtexto `100% velas`. | OK |
| Amostra insuficiente: N/A também em Return e CAGR anualizado | selo exact `Amostra insuficiente`; rank `—`; Sharpe/Trades/Win%/Return/Max DD/Calmar/CAGR anualizado `N/A`; Promover = 0; Excluir = 1. | OK |
| Sort só Calmar e CAGR vs B&H | options exact `Calmar` · `CAGR vs B&H`. Sem Sharpe/Win%/Return/CAGR anualizado como chave. | OK |
| «+ detalhes» guarda extras, não é o único sítio | `none→block`; texto `B&H 8,4% · Δ −4,7 p.p. · PF 1,12 · mercado … janela […]`. Sem Sharpe/Win%/Return/CAGR na expansão. Colunas continuam visíveis. | OK |
| Montar sem grelha de métricas | após tab: Preflight + Rascunho visíveis; `table.lb=0`; `th Sharpe=0`; `th Return=0`. | OK |
| Não entra Favoritos / motor / ordenar Sharpe / #897 | Favoritos só no nav (clone de shell). Selos GO/NO-GO e modal promover são clone, não delta deste card. | OK |

Q1/Q2/Q3 **não reabertas**. Números diferentes de Favoritos **não são falha**.

## UX

Hierarquia: h1 → tablist 3 modos → 1 painel. Default Operate = Acompanhar em curso. Glance: o bloco partilhado começa por Sharpe (como Favoritos), não por Calmar; Return e CAGR anualizado ocupam sítios distintos. Win% `46,7%` não colide com Trades `30` + `100% velas`. Return percent com sinal vs CAGR percent sem sinal vs Calmar razão.

Carga: 7 números é o job (Q1 nomes+ordem; Q2 as duas grelhas). Desktop overflow-x (`min-width:1240px`); Ação da direita pode exigir scroll horizontal a 1440 com sidebar 224px — risco já aceite como P3. Mobile cards em pares com `data-label`. Decidir por linha elegível = 2 (Promover/Excluir); insuficiente = 1 (Excluir). Tablist = 3.

## Acessibilidade

- `lang=pt-BR`; `:focus-visible`; alvos de acção ≥44px (Promover/Excluir/tabs); `prefers-reduced-motion`.
- Tablist/tab/tabpanel + `aria-controls`. Região de tabela `tabindex=0`.
- Headers novos/reordenados com `aria-label` (Sharpe; Trades; Win rate (taxa de acerto); Return (retorno composto da janela da varredura); Maximum Drawdown; Calmar (CAGR anual do calendário ÷ Max DD); CAGR anualizado da varredura) — não só `title`.
- Caption sr-only no Decidir nomeia Return como composto da janela, não CAGR, e Trades como negócios (cobertura = subtexto).
- Selo `Amostra insuficiente` é texto, não só cor. N/A é texto.
- Contraste: pares Binance (`DESIGN.md` não reescrito). Verde/vermelho só em performance (Return/CAGR pos / Max DD neg); ciclo EM CURSO azul/info.
- Nav do shell 42px e link inline «novo rascunho» 18px = clone, não delta (P3).

## Responsividade

- Desktop 1440×900: sete métricas no thead sem cortar candidato; Ação à direita no Decidir (overflow-x, botões podem clipar sem scroll). PNGs `944-A-desktop-1440x900-{acomp,decidir,decidir-detalhes,montar}.png`.
- Mobile 390×844: tablist 3 colunas; tabela → cards `data-label`; as sete métricas permanecem visíveis em pares (Sharpe/Trades, Win rate/Return, Maximum Drawdown/Calmar, CAGR anualizado) mesmo com «+ detalhes» collapsed. Header mobile 72px (folha). PNG `944-A-mobile-390x844-{acomp,decidir,decidir-detalhes,montar}.png`.
- Sem overflow bloqueante do contrato visível. 0 console / 0 pageerror.

## Estados

Mock cobre: Acompanhar em curso com 5 parciais finitas (todas NO-GO, recorte ALPHA); Montar rascunho (landmarks); Decidir misto (3 NO-GO com Promover + amostra insuficiente sem Promover). Não mocka: Calmar N/A com Max DD/Trades finitos, vizinha `Baixa amostra`, loading/erro de leaderboard, vazio, filtros a filtrar de verdade. Cobertura de mock = P3, não buraco do contrato visível.

## Design specificity

Composição da Descoberta (modos #852, parciais top-5, leaderboard Calmar, selo de amostra, métricas fáceis #906). Não poderia ir a um SaaS genérico inalterado. Modo Impeccable: **Operate** / refinement. Folha Binance; `DESIGN.md` não reescrito.

## Heurísticas Nielsen (0–4, Operate; só neste snapshot)

| # | Heurística | Score | Nota |
|---|---|---|---|
| 1 | Visibility of system status | 4 | Chip EM CURSO + 309/697 + tab Acompanhando |
| 2 | Match between system and real world | 4 | Vocabulário de Favoritos; Return ≠ CAGR anualizado; Trades ≠ cobertura |
| 3 | User control and freedom | 3 | Tabs + Pausar/Cancelar/Excluir; filtros/modais do vivo omitidos no Montar |
| 4 | Consistency and standards | 4 | Mesmo conjunto Acompanhar/Decidir; ordem = Favoritos + extras no fim |
| 5 | Error prevention | 4 | Insuficiente sem Promover; N/A nas sete; sort sem Sharpe/Return |
| 6 | Recognition rather than recall | 4 | Sete números em coluna; operador não traduz Calmar-primeiro |
| 7 | Flexibility and efficiency | 3 | Sort real / paginação / atalhos do vivo omitidos no mock |
| 8 | Aesthetic and minimalist design | 3 | Densidade 7 colunas aceite; Ação aperta no desktop; Montar esquelético |
| 9 | Help users recognize/recover errors | 3 | N/A + selo; sem modal Excluir do vivo na cobertura deste juízo |
| 10 | Help and documentation | 3 | Hints no thead + nota educacional; Ajuda fora |
| **Total** | | **35/40** | **Good** |

## Cognitive load

Checklist: 1 h1; 1 modo visível; delta = reordenar/renomear colunas já nomeadas + 1 coluna Return. **Pass** (chunking de 7 números = carga intrínseca do contrato, não ruído). Decisões visíveis no glance Acompanhar ≤4 (tabs + Pausar/Cancelar/Novo rascunho). Decidir elegível = 2 CTAs.

## Emotional journey

Vale (Calmar à esquerda e sem Return → operador acha outra estratégia) → pico (Sharpe primeiro, Return `+12,8%` ao lado de CAGR `3,7%`) → fim (insuficiente continua N/A, sem Promover). Reassegurança: Calmar/Max DD não saem; «+ detalhes» ainda guarda B&H/PF/janela.

## Personas

1. **Alex (operador Acompanhar, veio de Favoritos):** lê Sharpe `0,31` / Trades `30` / Win% `46,7%` / Return `+12,8%` / Max DD `−16,5%` sem traduzir; CAGR anualizado `3,7%` no final, número diferente de propósito.
2. **Alex (Decidir):** escolhe promover com as sete colunas visíveis; sort continua Calmar; insuficiente sem CTA.
3. **Sam (teclado / SR):** landmarks 3/3 após Montar; `aria-label` de Return ≠ CAGR; N/A textual.

## Strengths

- Clone estrutural da rota (`/combo/discovery`), não galeria ANTES/DEPOIS.
- Delta mínimo e óbvio: mesma ordem nas duas grelhas; Return existe; CAGR no final com nome próprio.
- Q1 visível: nomes e ordem, não os números de Favoritos.
- Q2 visível: parciais **e** leaderboard.
- Q3 visível: CAGR anualizado no final, distinto de Return `+12,8%`.
- Non-goals visíveis respeitados (Montar sem grelha; sort intacto; Favoritos só nav).

## Playwright (esta sessão)

- Desktop 1440×900 e mobile 390×844: aceite visível 9/9 PASS. Landmarks Montar visíveis após tab. `+ detalhes` `none→block` sem duplicar Return/CAGR. 0 console / 0 pageerror.
- Live `/combo/discovery` → `/login` (descartado).
- Detector `detect.mjs` no HTML local: `[]`. URL scan Pediu puppeteer (ausente); juízo visual = Playwright, não o detector de URL.
- PNGs: `944-A-desktop-1440x900-{acomp,decidir,decidir-detalhes,montar}.png`, `944-A-mobile-390x844-{acomp,decidir,decidir-detalhes,montar}.png`, `944-A-live-combo-discovery.png`. Gate: `944-A-gate.json`.

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
- **P3-2** `min-width:1240px` da `.discovery-table` / overflow-x desktop — Ação («Promover»/«Excluir») clipa a 1440×900 com sidebar 224px sem scroll horizontal. Já aceite em `design.md` Apply contract.
- **P3-3** Mobile `data-label` das métricas: `Win rate` (EN) e `Maximum Drawdown` vs header `Win%` / `Max DD`. Padrão vivo. Não esconde métrica nem troca Return por CAGR.
- **P3-4** Decidir mock: 4 `<tr>` vs copy «309 de 309 · página 1 de 26»; filtros/paginação cosméticos; sem vizinha `Baixa amostra`; Acompanhar sem linha Calmar N/A; `Excluir` no insuficiente sem `aria-label` com `result_id`.
- **P3-5** CSS vars do proto (`--accent`, `--border`) vs folha (`--accent-primary`, `--border-default`); hex Binance bate. Nav 42px / «novo rascunho» 18px = clone de shell.
- **P3-6** Modal promover ainda etiqueta `Retorno (CAGR)` = `3,7%` (o CAGR, não o Return `+12,8%` da grelha). Clone do vivo L2716 / spec «o mesmo valor rotulado Retorno (CAGR) no diálogo». Fora do contrato das duas grelhas; não reabrir #897.
- **P3-7** Payload `total_return` / `total_return_pct` no top-level; `fmtPct` assinado no Return; testes que ainda afirmam Calmar-primeiro / `Trades/cobertura` — já no contrato Apply.

## Disposition

Aceitar P3 no Apply. Não reabrir grelha. Não reabrir Q1 / Q2 / Q3. Não exigir segundo rework de Design por estes itens.

## Verdict

**PASS** — zero P0/P1 de produto/escopo/contrato visível. Tokens parseáveis 3/3. Landmarks 3/3 no proto (Montar para Preflight/Rascunho). Disco == HTTPS. Sem galeria/ANTES-DEPOIS como index. copied > 0 (11 pares). Delta = ordem/nomes + coluna Return. `/login` descartado. Clone **não** alegado só por sidebar: prova = landmarks proto × `DiscoveryPage.tsx`. Return ALPHA `+12,8%` ≠ CAGR `3,7%` nas duas grelhas sem expandir.

`Design Agent verdict` final da coluna = síntese do pai após A+B. Este filho A não chama `process_event`.

---

```
Assessment A 944
tokens_ok: yes
clone_ok: yes
P0: nenhum
P1: nenhum
P3: Montar condensado; min-width/Ação overflow desktop; data-label EN Win rate / Maximum Drawdown; mock 309/4 linhas + filtros cosméticos + sem Baixa amostra; CSS vars / nav 42px; modal Retorno (CAGR) clone vivo; payload total_return + testes Calmar-primeiro Apply
verdict: PASS
```
