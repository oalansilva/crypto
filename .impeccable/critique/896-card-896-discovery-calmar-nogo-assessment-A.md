# Assessment A — card 896 · change card-896-discovery-calmar-nogo

> Avaliador A isolado (produto / UX / a11y / fidelidade do clone). Mesmo modelo do chat. Sem transcript do pai. Sem nested-spawn. Sem edição de `design.md`, HTML proto, `backend/`, `frontend/src/` ou OpenSpec. Sem `process_event`. Única escrita: este arquivo + PNGs `896-A-*`.

## Metadata

- card: 896 — "Descoberta: ranking por Calmar dispara número enorme e esconde NO-GO"
- change: `card-896-discovery-calmar-nogo`
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-896-discovery-calmar-nogo`
- data (UTC): 2026-09-11T17:55Z
- UI impact (rubrica): **affected** · `live_route: /combo/discovery` · `surface: existing` — linhas próprias 1–3 de `design.md` (parseáveis)
- Digest proto (autor, verificado nesta sessão): sha256 `19c07a26d8c479ab5a56482759f58a0683a209f9aeb674cf2ced525b6f3e5a08` · 37328 bytes
- Servido HTTPS == local: IDENTICAL (`cmp` limpo)
- Issue: REST `gh api repos/oalansilva/crypto/issues/896` (não `gh issue view`). Q1 aceite; fronteira vazia; não reaberta.
- D4: com-tela = autor + dupla + 1 rework. Tokens verificados como item da rubrica — nenhuma rodada extra só para o parser.

## Limitação de sessão (obrigatória)

Playwright `@playwright/cli` 0.1.19 headed sob `xvfb-run -a` (`PLAYWRIGHT_MCP_SANDBOX=false`, `PLAYWRIGHT_MCP_BROWSER=chromium`, executable Chromium 1243 arm64). Wrapper `playwright-cli-headed` / `/usr/local/bin/playwright-cli-headed` **ausentes**. Um `run-code` por viewport: `goto` + asserts + `screenshot` na mesma sessão X.

| URL pedida | URL final | h1 | Landmarks `/combo/discovery` |
|---|---|---|---|
| `https://dev.criptofarol.com.br/combo/discovery` | `https://dev.criptofarol.com.br/combo/discovery` (HTTP 200) | `Bem-vindo de volta` | 0/3 (`swing=0`, `preflight=0`, `rascunho=0`) |

**`/login` não é a rota.** Chrome de login **não** é evidência de clone e **não** autoriza PASS de fidelidade. Sem cookie de administrador, a avaliação de clone usa: (1) protótipo canónico HTTP, (2) HTML local, (3) fonte viva `frontend/src/pages/DiscoveryPage.tsx` vs catálogo `scripts/process-fsm/route-landmarks.yaml`. Sidebar 224px / tokens `--bg-*` **não** bastam.

## Tokens parseáveis (rubrica D4)

`design.md` linhas próprias 1–3:

```
UI impact: affected
live_route: /combo/discovery
surface: existing
```

Justificativa no corpo: clone+delta da rota existente; regiões clonadas marcadas («só estas»: shell AppNav + heading + 3 modos + Acompanhar parciais + Decidir linhas; Montar só para landmarks). **PASS** deste item da rubrica.

## Digest proto (disco == HTTPS)

| Ponta | sha256 | bytes | HTTP |
|---|---|---|---|
| disco `frontend/public/prototypes/card-896-discovery-calmar-nogo/index.html` | `19c07a26d8c479ab5a56482759f58a0683a209f9aeb674cf2ced525b6f3e5a08` | 37328 | — |
| HTTPS `https://dev.criptofarol.com.br/prototypes/card-896-discovery-calmar-nogo/` | `19c07a26d8c479ab5a56482759f58a0683a209f9aeb674cf2ced525b6f3e5a08` | 37328 | 200 |
| `design.md` Prototype / Prototype Validation | mesmo digest | 37328 | — |

`cmp` disco vs `/tmp/896-proto.html`: identical. Confirma disco == HTTPS.

## Fidelidade (clone da página viva)

Catálogo `/combo/discovery` (`scripts/process-fsm/route-landmarks.yaml`): `selectors: []` · texts `Descoberta de estratégias swing`, `Preflight`, `Rascunho de varredura`.

| Landmark | `DiscoveryPage.tsx` (vivo, sem sessão) | Proto `index.html` + Playwright |
|---|---|---|
| `Descoberta de estratégias swing` | h1 L1326 + subcopy 4h/1d L1327–1329 | h1 visível no default Acompanhar (desktop e mobile); exact 1 |
| `Preflight` | `aria-label="Preflight da varredura"` L1925 + h2 `Preflight` L1928 | hidden no default Acompanhar (igual ao vivo com sweep); **visível após tab Montar** (`#panel-montar [aria-label="Preflight da varredura"]` + h2) |
| `Rascunho de varredura` | h2 L1768 em tabpanel Montar (`aria-label="Novo rascunho de varredura"` L1764) | article `aria-label="Rascunho de varredura"` + h2; **visível após tab Montar** |

Anti-padrões P0:

- URL canónica `…/prototypes/card-896-discovery-calmar-nogo/` → `index.html` é a página (shell 224px + heading + 3 modos + Acompanhar + Decidir). **Não** é painel ANTES/DEPOIS. Botões Antes/Depois = 0. `text=ANTES/DEPOIS` = 0.
- Não é grelha de N estados no lugar de lista+detalhe. Acompanhar = tabela de parciais (5 linhas). Decidir = tabela de candidatos (5 linhas mock).
- Tabs trocam markup (`.modepanel.active` + `aria-selected` + `aria-controls` + roving tabindex + ArrowLeft/Right). Não é `aria-pressed` cosmético.
- 8 pares `COPIED:start/end` (shell, heading, modos, rascunho, preflight, Acompanhar progresso, leaderboard header, nota rank-stable).

Chrome presente (sidebar 224px, Inter, `--bg-primary:#0b0e11`, amarelo `#fcd535`, nav Descoberta ativa) = **folha**, não prova. Prova = landmarks 3/3 no proto, alinhados ao TSX.

Vivo sem selo GO/NO-GO nas parciais (L1741–1744: só nome + meta) nem no Decidir (L2306–2309: só `Amostra insuficiente` / `Baixa amostra`). `fmtNum` L125–128 formata qualquer finito com 2 casas — causa do `1e27` em 27 dígitos. O proto é o **depois**; o TSX é o **antes**. Isso é o delta, não falha de clone.

## Produto (aceite visível — não reabrir grelha / Q1)

Delta pedido: Calmar honesto com 2 casas; absurdo → `N/A`; selo GO/NO-GO na linha; todo GO acima de todo NO-GO; `30 · 100%` = negócios/cobertura; Promover no NO-GO elegível permanece.

| Aceite visível | Evidência (Playwright + pixels) | Disposition |
|---|---|---|
| Calmar honesto 2 casas (`1,20`) | `[data-testid=cell-calmar-honest]` e `[data-testid=decidir-calmar-honest]` exact `1,20`. PNG desktop ranks 1–3: `1,20` / `0,94` / `0,81`. | OK |
| ALPHA honesto `22,00`, nunca `1e27` / 27 dígitos | `[data-testid=cell-calmar-alpha]` = `22,00`; innerText da linha sem `1e27` e sem `\d{20,}`. Rank 4. Identidade `ALPHA/USDT` + `RS-B109ED2C80`. | OK |
| Absurdo → célula `N/A` | `[data-testid=cell-calmar-na]` e `[data-testid=decidir-calmar-na]` exact `N/A`. Rank 5 parciais / rank 4 Decidir. | OK |
| Selo GO/NO-GO na linha, sem gráfico nem promover | `[data-testid=seal-go]` texto `GO` visível; `[data-testid=seal-nogo]` texto `NO-GO` visível. `canvas`/`[role=dialog]` = 0. Mobile: bounding box do selo no viewport 390×844 após `scrollIntoView` (GO/NO-GO `y≈409`, `height=26`). | OK |
| Todo GO acima de todo NO-GO; NO-GO permanece | Parciais `data-verdict` = `["GO","GO","GO","NO-GO","NO-GO"]`. Decidir linhas com veredito = `["GO","GO","NO-GO","NO-GO"]`. ALPHA permanece rank 4 (parciais) / rank 3 (Decidir). Q1 **não** reaberta. | OK |
| `30 · 100%` = negócios/cobertura, não win rate | `[data-testid=trades-coverage]` e `[data-testid=decidir-trades-coverage]` exact `30 · 100%`. `th[aria-label="negócios / cobertura"]` = 1. Hint `negócios · velas`. Copy `[data-testid=column-copy]`: «não é taxa de acerto». Header win rate = 0. | OK |
| Calmar ≠ retorno | `th[aria-label="Calmar (CAGR anual do calendário ÷ Max DD)"]`; hint visível `CAGR ÷ Max DD`. Nota Decidir: «Calmar não é retorno: é CAGR do calendário…». | OK |
| Promover no NO-GO elegível permanece | `[data-testid=promote-nogo]` `disabled=false` (desktop e mobile). Pixels: botão amarelo «Promover» na linha ALPHA rank 3. | OK |
| `Baixa amostra` ≠ `NO-GO` | Selo amber `Baixa amostra` na linha ADA (rank `—`); botão disabled «Baixa amostra». Linha NO-GO sem `.sample-badge`. Bordas: NO-GO `rgba(246,70,93,.45)` vs amostra `rgba(245,158,11,.35)` vs Long `rgba(14,203,129,.28)` vs GO `rgba(59,130,246,.42)`. | OK |
| Não entra: #876 / #897 / #852 / landing / backfill `#862f31de` | 3 modos intactos; sem galeria; sem landing; mock `#c896nogo` (não recálculo de `#862f31de`); fórmula de progresso já viva com «4 amostra insuficiente» (clone, não delta). | OK |

## UX

Hierarquia: h1 → tablist 3 modos → 1 painel. Default Operate = Acompanhar em curso (cena do incidente). Glance do Acompanhar: rank 1 = GO `1,20` (não ALPHA `1e27`). ALPHA cai para 4.º com selo `NO-GO` + Calmar `22,00` + `30 · 100%`.

Carga: 3 modos; 5 colunas no desktop; selo + Calmar co-localizados na linha. Decidir: Promover continua no NO-GO (Q1); `Baixa amostra` vizinha intacta.

Prevenção do incidente: (1) teto/`N/A` tira o jackpot visual; (2) classe GO-first tira o NO-GO do 1.º mesmo com Calmar `22,00` > `1,20`; (3) selo na linha sem abrir gráfico.

Residual visual (não quebra o aceite): o selo é uma caixa `display:block` de ~452px (desktop) / 277px (mobile) porque `.candidate span` (0,1,1) ganha de `.verdict` / `.verdict-go` / `.verdict-nogo` (0,1,0). Texto computado `rgb(112,122,138)` (`--text-muted`); **borda** mantém azul/danger. `.tag.long` (0,2,0) continua verde. Autor já classificou o wrap mobile como P3; o desktop é a mesma causa. Apply: `.candidate .verdict.verdict-go` / `.verdict.verdict-nogo` com `display:inline-flex; width:max-content`. **Não** reabre como P0/P1 — selo textual visível + bordas distintas + 7 givens verdes.

## Acessibilidade

- `lang=pt-BR`; `:focus-visible`; alvos ≥44px; `prefers-reduced-motion`.
- Tablist/tab/tabpanel + `aria-controls` + roving tabindex + setas.
- `role=progressbar` valuemin/max/now 0/24/18; região de tabela `tabindex=0`.
- Selo é **texto** `GO`/`NO-GO` (não só cor). `aria-label` das colunas Calmar e negócios/cobertura. Caption sr-only no Decidir.
- Contraste do texto do chip (~3,6:1 muted sobre `#1e2329`) fica abaixo do par desenhado (`#93c5fd` / `#ff8294`) por causa da especificidade — P3 Apply, não falha de significado (a palavra está lá; a borda colorida distingue as classes).
- Long verde vs GO azul (borda) vs NO-GO danger (borda) vs âmbar amostra: vocabulário do issue respeitado.

## Responsividade

- Desktop 1440×900: tabela com thead + hints; ranks 1–5 após scroll até `[data-testid=partials-table]`. PNG `896-A-desktop-1440x900.png` (126417 B, IHDR 1440×900).
- Mobile 390×844: tablist 3 colunas; tabela → cards `data-label`; selo no viewport após scroll (`seal_nogo_in_viewport` PASS, box `{x:49,y:408.95,width:277,height:26}`). PNG `896-A-mobile-390x844.png` (50306 B, IHDR 390×844). Chip full-width = P3 já do autor.
- Header mobile 72px (folha). Sem overflow bloqueante. 0 console / 0 pageerror / 0 ≥400 nos dois viewports.

## Estados

Mock cobre: Acompanhar em curso com GO/NO-GO/N/A; Montar rascunho (landmarks); Decidir misto (GO, NO-GO elegível com Promover, N/A, Baixa amostra). Não mocka: veredito ausente (design: sem selo, não compete com GO), loading/erro de leaderboard, sweep concluído. Cobertura de mock = P3, não buraco do contrato visível.

## Design specificity

Composição da Descoberta (modos #852, parciais top-5, leaderboard Calmar, selo de amostra). Não poderia ir a um SaaS genérico inalterado. Modo Impeccable: **Operate** / refinement.

## Heurísticas Nielsen (0–4, Operate)

| # | Heurística | Score | Nota |
|---|---|---|---|
| 1 | Visibility of system status | 4 | Chip EM CURSO + 18/24 + selo GO/NO-GO na linha |
| 2 | Match between system and real world | 4 | Calmar `22,00`; copy negócios/cobertura; vocabulário do issue |
| 3 | User control and freedom | 3 | Tabs + Pausar/Cancelar; Promover no NO-GO permanece (Q1) |
| 4 | Consistency and standards | 3 | Tokens Binance; GO azul ≠ Long verde; NO-GO danger ≠ âmbar; texto do chip muted por CSS (P3) |
| 5 | Error prevention | 4 | GO-first + N/A + selo visível previnem o jackpot `1e27` |
| 6 | Recognition rather than recall | 4 | Veredito na linha; hints no `<th>`; sem tooltip-only |
| 7 | Flexibility and efficiency | 3 | Filtros/paginação/modais do Decidir vivo omitidos |
| 8 | Aesthetic and minimalist design | 3 | Clone Operate; chip full-width (P3) |
| 9 | Help users recognize/recover errors | 3 | N/A sanitiza legado; sem backfill (non-goal) |
| 10 | Help and documentation | 3 | Copy mínima da coluna; Ajuda/landing fora de escopo |
| **Total** | | **34/40** | **Good** |

## Cognitive load

Checklist: 1 h1; 1 modo visível; delta localizado na linha. **Pass**. Pontos de decisão no glance Acompanhar ≤4 (tabs + Pausar/Cancelar/Novo rascunho). Decidir por linha elegível = 2 (Promover/Excluir). **Pass**.

## Personas

1. **Alex (admin Descoberta):** vê GO `1,20` no 1.º em <5 s; ALPHA `22,00` abaixo com `NO-GO`; Promover continua no elegível.
2. **Sam (teclado / SR):** landmarks 3/3 após Montar; `aria-label` Calmar e negócios/cobertura; chip não é só cor (texto GO/NO-GO).
3. **Riley (stress):** `1e27` ausente; `N/A` no 5.º; `Baixa amostra` ADA distinta; Promover disabled só nela.

## Strengths

- Clone estrutural da rota (`/combo/discovery`), não galeria ANTES/DEPOIS.
- Delta mínimo no sítio do incidente (célula + selo + ordem + copy).
- Q1 load-bearing visível: Calmar `22,00` perde o 1.º para GO `1,20`.
- Non-goals respeitados; Promover não travado.

## Playwright (esta sessão)

- Desktop 1440×900: 46/47 harness PASS. Único fail = `nogo_not_baixa_amber` no **texto** computado (`rgb(112,122,138)` nos dois) — bordas distintas (danger vs amber); **não** é falha de produto. Aceite visível 7/7 PASS. 0 console / 0 pageerror / 0 ≥400.
- Mobile 390×844: 24/24 PASS (selo no viewport). 0 console / 0 pageerror / 0 ≥400.
- PNGs: `.impeccable/critique/896-A-desktop-1440x900.png` (tabela parciais 1–5), `896-A-desktop-1440x900-acomp.png` (topo), `896-A-desktop-1440x900-montar.png`, `896-A-desktop-1440x900-decidir.png`, `896-A-desktop-1440x900-decidir-baixa.png`, `896-A-mobile-390x844.png` (ALPHA NO-GO no viewport), `896-A-mobile-390x844-acomp.png`, `896-A-mobile-390x844-montar.png`, `896-A-mobile-390x844-decidir.png`.

## Priority issues

Nenhum P0/P1 de produto/escopo/contrato visível.

## P0

_(nenhum)_

## P1

_(nenhum)_

## P3 — detalhe de Apply / clone de região fora do delta

- **P3-1** Montar condensado vs vivo: sem Iniciar, workbench, checkboxes 4h/1d, período/ranking, impedimentos/`<details>`. Landmarks Preflight + Rascunho presentes. Apply lê `DiscoveryPage.tsx` para Montar intacto.
- **P3-2** Decidir omitiu filtros, paginação, `+ detalhes`, modais Promover/Excluir.
- **P3-3** Promover outline transparente; vivo é fill `--accent-primary` / texto `#181a20`.
- **P3-4** Contagem mock «16 de 16 candidatos» com 5 `<tr>`; `#PF-896-24` no chrome copiado.
- **P3-5** `oos_verdict` top-level vs `metrics.oos_verdict` — contrato de Apply já no `design.md`.
- **P3-6** Chip GO/NO-GO `display:block` largura da coluna (~452px desktop / 277px mobile) e `color: var(--text-muted)` porque `.candidate span` (0,1,1) ganha de `.verdict-go`/`.verdict-nogo` (0,1,0). Bordas continuam azul `#3b82f6` / danger `#f6465d`. Apply: `.candidate .verdict.verdict-go { display:inline-flex; width:max-content; color:#93c5fd }` (e análogo NO-GO). Não reabrir como P0/P1.

## Disposition

Aceitar P3 no Apply. Não reabrir grelha. Não reabrir Q1. Não exigir segundo rework de Design por estes itens.

## Verdict

**PASS** — zero P0/P1 de produto/escopo/contrato visível. Tokens parseáveis 3/3. Landmarks 3/3 no proto (Montar para Preflight/Rascunho). Disco == HTTPS. Sem galeria/ANTES-DEPOIS como index. Login descartado. Clone **não** alegado só por sidebar: prova = landmarks proto × `DiscoveryPage.tsx`.

`Design Agent verdict` final da coluna = síntese do pai após A+B. Este filho A não chama `process_event`.

---

```
Assessment A 896
tokens_ok: yes
clone_ok: yes
P0: nenhum
P1: nenhum
P3: Montar condensado; Decidir sem filtros/modais/+detalhes; Promover outline vs fill; mock 16/16 vs 5 linhas + #PF-896-24; oos_verdict top-level vs nested; chip GO/NO-GO display:block largura da coluna e texto muted (especificidade .candidate span) — bordas azul/danger intactas, Apply encolhe
verdict: PASS
```
