# Assessment A — card 969 · change card-969-discovery-selo-go-nogo

> Avaliador A isolado (produto / UX / a11y / fidelidade do clone). Grok 4.6. Sem transcript do pai. Sem nested-spawn. Sem edição de `design.md`, HTML proto, `backend/`, `frontend/src/` ou OpenSpec. Sem `process_event`. Única escrita: este arquivo + PNGs `969-A-*` + `969-A-evidence.json`.

## Metadata

- card: 969 — "Descoberta: selo GO/NO-GO de swing 1d, não o piso Combo de 100 trades"
- change: `card-969-discovery-selo-go-nogo`
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-969-discovery-selo-go-nogo`
- data (UTC): 2026-09-18T13:14Z
- UI impact (rubrica D4): **affected** · `live_route: /combo/discovery` · `surface: existing` — linhas próprias 1–3 de `design.md` (parseáveis)
- Digest proto (pai + esta sessão): sha256 `04967d7546f8d67a1d2e6a8db246faeefb5e1c3ab5283e5d61eb58c8305d47fe` · 50488 bytes
- Servido HTTPS == local: IDENTICAL (`cmp` limpo)
- Issue: REST `gh api repos/oalansilva/crypto/issues/969` (não `gh issue view`). Decisões gravadas não reabertas (treino fraco + holdout positivo = NO-GO com motivo de treino; regra em todas as linhas; Baixa amostra sem GO nem NO-GO).
- D4: com-tela = autor + dupla + 1 rework. Tokens verificados como item da rubrica — nenhuma rodada extra só para o parser. Regiões clonadas marcadas no corpo do `design.md` («só estas») + 10 pares `COPIED:start/end` no proto.

## Limitação de sessão (obrigatória)

Python Playwright 1.62 + Chromium 1243 headed sob `xvfb-run -a` (`executable_path` do cache ms-playwright). Wrapper `playwright-cli-headed` / script Codex `playwright_cli.sh` **não executáveis** nesta sessão. Um ciclo por viewport: `goto` HTTPS + asserts + screenshot na mesma sessão X. Evidência estruturada: `.impeccable/critique/969-A-evidence.json`.

| URL pedida | URL final | h1 | Landmarks `/combo/discovery` |
|---|---|---|---|
| `https://dev.criptofarol.com.br/combo/discovery` | `https://dev.criptofarol.com.br/login` (SPA redireciona) | `Bem-vindo de volta` | 0/3 (`swing=0`, `preflight=0`, `rascunho=0`) |

**`/login` não é a rota.** Chrome de login **não** é evidência de clone e **não** autoriza PASS de fidelidade. HTTP 200 isolado nunca é PASS. Sem cookie de administrador, a avaliação de clone usa: (1) protótipo canónico HTTPS, (2) digest disco == HTTPS, (3) fonte viva `frontend/src/pages/DiscoveryPage.tsx` vs catálogo `scripts/process-fsm/route-landmarks.yaml`. Sidebar 224px / tokens `--bg-*` **não** bastam.

## Tokens parseáveis (rubrica D4)

`design.md` linhas próprias 1–3:

```
UI impact: affected
live_route: /combo/discovery
surface: existing
```

Justificativa no corpo: clone+delta da rota existente; regiões clonadas marcadas («só estas»: shell AppNav autenticado + heading + 3 modos + Montar Preflight/Rascunho/heading + chrome Acompanhar + casca das grelhas; delta só selos + motivos). Estado visível do proto: **Decidir**. **PASS** deste item da rubrica. Gate no autor: tokens parseáveis + regiões clonadas marcadas.

## Digest proto (disco == HTTPS)

| Ponta | sha256 | bytes | HTTP |
|---|---|---|---|
| disco `frontend/public/prototypes/card-969-discovery-selo-go-nogo/index.html` | `04967d7546f8d67a1d2e6a8db246faeefb5e1c3ab5283e5d61eb58c8305d47fe` | 50488 | — |
| HTTPS `https://dev.criptofarol.com.br/prototypes/card-969-discovery-selo-go-nogo/` | `04967d7546f8d67a1d2e6a8db246faeefb5e1c3ab5283e5d61eb58c8305d47fe` | 50488 | 200 |
| `design.md` Prototype / Prototype Validation | mesmo digest | 50488 | — |

`cmp` disco vs `/tmp/969-proto.html`: identical. Confirma disco == HTTPS.

## Fidelidade (clone da página viva)

Catálogo `/combo/discovery` (`scripts/process-fsm/route-landmarks.yaml`): `selectors: []` · texts `Descoberta de estratégias swing`, `Preflight`, `Rascunho de varredura`.

| Landmark | `DiscoveryPage.tsx` (vivo, sem sessão) | Proto HTTPS + Playwright |
|---|---|---|
| `Descoberta de estratégias swing` | h1 ~L1491 + subcopy 4h/1d | h1 visível no default Decidir (desktop e mobile); count 1 |
| `Preflight` | `aria-label="Preflight da varredura"` + h2 `Preflight` ~L2172–2175 | hidden no default Decidir (igual ao vivo fora de Montar); **visível após tab Montar** (`aria-label` + h2). Mobile: abaixo do rascunho (grelha viva também empilha). |
| `Rascunho de varredura` | h2 ~L2015 em tabpanel Montar | article `aria-label="Rascunho de varredura"` + h2; **visível após tab Montar** |

Anti-padrões P0:

- URL canónica `…/prototypes/card-969-discovery-selo-go-nogo/` → página (shell 224px + heading + 3 modos + Montar + Acompanhar + Decidir). **Não** é painel ANTES/DEPOIS. Botões Antes/Depois = 0. `text=ANTES/DEPOIS` visível = 0 (a string só existe num comentário de recorte).
- Não é grelha de N estados no lugar da listagem. Acompanhar = tabela de parciais (5 linhas). Decidir = listagem de candidatos (7 linhas mock + rank `—` amostra).
- Tabs trocam markup (`.modepanel.active` + `aria-selected` + `aria-controls` + roving tabindex). Default proto = Decidir (especificado); vivo sem sweep abre em Montar — **não** é falha de clone; Apply não copia o default do proto à cega.
- 10 pares `COPIED:start/end` (shell, heading, modos, rascunho, preflight, Acompanhar progresso, grelha parciais, header Decidir, grelha Decidir, nota educacional).

Chrome presente (sidebar 224px, Inter, `--bg-primary`, amarelo `#fcd535`, nav Descoberta ativa) = **folha**, não prova. Prova = landmarks 3/3 no proto, alinhados ao TSX.

Vivo: `WalkForwardSeal` pinta só `GO`/`NO-GO` a partir de `oos_verdict.status` (Combo-era); `OosVerdict.reasons` existe no tipo e **não** é renderizado na linha. O proto é o **depois** (perfil Descoberta + motivo treino/holdout visível). Isso é o delta, não falha de clone.

## Produto (aceite visível — não reabrir grelha)

Delta pedido: selo GO/NO-GO da Descoberta deixa o piso Combo 100 / Sharpe 0,8 / 20 holdout; motivos treino vs holdout na linha; Baixa amostra sem chip; mesma regra em 4h/short; Promover no NO-GO elegível permanece.

| Aceite visível | Evidência (Playwright + pixels) | Disposition |
|---|---|---|
| Default Decidir | `aria-selected=true` em `#tab-decidir`; `.modepanel.active` = `panel-decidir`. PNG desktop: tab Decidir amarela. | OK |
| BTC `RS-E0E30719CC` GO (Combo-era seria NO-GO: 43 trades, Sharpe 0,50) | `[data-testid=row-go-btc] data-result=RS-E0E30719CC`; `[data-testid=decidir-seal-go]` exact `GO`. Calmar 10,60; Sharpe 0,50; 43 negócios. Sem NO-GO na linha. | OK |
| NO-GO holdout; motivo aponta Holdout + valor + limiar | `[data-testid=decidir-seal-nogo-holdout]` = `NO-GO`. Motivo visível (não `title`): `Holdout — Sharpe OOS −0,18 ≤ 0 (limiar > 0)`. AGLD elegível (36 trades, Calmar 2,40). | OK |
| NO-GO treino com Sharpe OOS positivo; motivo aponta Treino | DOGE meta `Sharpe OOS 0,22`; selo `NO-GO`; motivo visível `Treino — Calmar 0,42 < 1`. Promover enabled. Decisão gravada **não** reaberta. | OK |
| Baixa amostra: só aviso; sem chip GO/NO-GO (holdout mau) | ADA rank `—`; badge `Baixa amostra`; `.verdict` count = 0; meta `18 trades` + `holdout Sharpe −0,40`; botão disabled «Baixa amostra». | OK |
| Mesma regra 4h e short | SOL/USDT · 4h · Long = `GO`; LINK/USDT · 1d · Short = `GO`. Presente em Decidir e (SOL) nas parciais. | OK |
| Motivos na linha, não tooltip-only | `.seal-reason` innerText não vazio; `title` ausente; visível em Decidir e Acompanhar (desktop e mobile após scroll). Sem exigir «+ detalhes». | OK |
| Promover no NO-GO elegível permanece | `[data-testid=promote-nogo-holdout]` e `promote-nogo-treino` `disabled=false`. Pixels: botão fill amarelo «Promover» (mobile no viewport). Não trava. | OK |
| Ranking Calmar + GO acima de NO-GO intactos (#896 fora) | Decidir `data-verdict` = `GO,GO,GO,GO,NO-GO,NO-GO` depois ADA sem veredito. Acompanhar parciais: 3 GO + 2 NO-GO. | OK |
| Não entra: Combo save-favorite / backfill completed / redesign 3 modos | Sem UI de salvar favorito Combo; mock varredura `#0d7990ca` concluída no Decidir / em curso no Acompanhar (cena, não recálculo); 3 modos intactos. | OK |

## UX

Hierarquia: h1 → tablist 3 modos → 1 painel. Default Operate do proto = Decidir (cena da escolha). Glance: rank 1 = BTC `GO` 10,60 — não um Combo-NO-GO. AGLD/DOGE abaixo com motivo na linha. ADA âmbar distinta.

Carga: 3 modos; selo + motivo co-localizados no candidato. Segmento Treino vs Holdout reduz o risco de ler NO-GO de Calmar como falha de holdout (risco aceite no design). Promover continua no elegível NO-GO.

Prevenção do incidente Combo: (1) 43 trades + Sharpe 0,50 pintam GO; (2) holdout negativo pinta NO-GO Holdout; (3) holdout positivo com Calmar 0,42 pinta NO-GO Treino; (4) 18 trades + holdout −0,40 **não** inventam NO-GO.

Residual visual (não quebra o aceite): texto computado do chip `rgb(112,122,138)` (`--text-muted`) vs par desenhado `#93c5fd` / `#ff8294`; **borda** mantém azul `#3b82f6` / danger `#f6465d`. Desktop chip `inline-flex` compacto (GO 33px / NO-GO 53px). Mobile card layout estica GO/NO-GO a 277px (barra da coluna) — selo textual + motivo continuam legíveis. **Não** reabre como P0/P1.

## Acessibilidade

- `lang=pt-BR`; tablist/tab/tabpanel + `aria-controls` + roving tabindex (Decidir `tabIndex=0`, irmãos `-1`).
- Selo é **texto** `GO`/`NO-GO` (não só cor). Motivo é texto na linha (segmento + valor + limiar).
- Long verde vs GO azul (borda) vs NO-GO danger (borda + copy `#ff8294`) vs âmbar amostra: vocabulário distinto.
- Alvos Promover 44px. Contraste do texto do chip (~muted sobre elevated) fica abaixo do par desenhado — P3 Apply, não falha de significado (a palavra está lá; a borda e o motivo distinguem as classes).
- Motivo holdout/treino `rgb(255,130,148)` sobre o card — copy, não cor-only.

## Responsividade

- Desktop 1440×900: tabela thead + ranks 1–4 no first paint; 5–6 + ADA após scroll. PNG `969-A-desktop-1440x900.png`, `969-A-desktop-1440x900-nogo.png`. Coluna Ação clipada no first paint (há overflow da tabela) — P3.
- Mobile 390×844: tablist 3 colunas; cards `data-label`; NO-GO + motivo + Promover no viewport após `scrollIntoView` (`nogo_in_viewport` PASS, box `{x:49,y:284,w:277,h:26}`). Chip full-width no card = P3.
- Header mobile 72px (folha). Sem overflow bloqueante do aceite. 0 console / 0 pageerror / 0 ≥400 nos dois viewports + live login.

## Estados

Mock cobre: Decidir misto (GO BTC/ETH/SOL 4h/LINK short, NO-GO holdout, NO-GO treino, Baixa amostra); Acompanhar parciais com os mesmos selos + progresso EM CURSO; Montar landmarks. Não mocka: linha `Amostra insuficiente` (só copy «3 amostra insuficiente» no progresso); fail-closed Sharpe OOS ausente/não finito; NO-GO treino por PF ou max DD (DOGE falha Calmar **e** max DD −41%, o motivo cita só Calmar). Cobertura de mock = P3, não buraco do contrato visível — a regra e o padrão de copy estão no `design.md`.

## Design specificity

Composição da Descoberta (modos #852, leaderboard Calmar #896, selo de amostra #876, identidade `RS-*`, Promover). Não poderia ir a um SaaS genérico inalterado. Modo Impeccable: **Operate** / refinement.

## Heurísticas Nielsen (0–4, Operate)

| # | Heurística | Score | Nota |
|---|---|---|---|
| 1 | Visibility of system status | 4 | Chip EM CURSO + selo GO/NO-GO + motivo na linha |
| 2 | Match between system and real world | 4 | Vocabulário Treino/Holdout; limiar visível; BTC testemunho |
| 3 | User control and freedom | 3 | Tabs + Promover no NO-GO permanece; Pausar/Cancelar no Acompanhar |
| 4 | Consistency and standards | 3 | Tokens Binance; GO azul ≠ Long verde; texto do chip muted (P3) |
| 5 | Error prevention | 4 | Baixa amostra não herda NO-GO; fail-closed descrito; treino ≠ holdout |
| 6 | Recognition rather than recall | 4 | Motivo na linha; sem tooltip-only; sem «+ detalhes» obrigatório |
| 7 | Flexibility and efficiency | 3 | Filtros Decidir presentes; Montar condensado |
| 8 | Aesthetic and minimalist design | 3 | Clone Operate; chip mobile full-width (P3) |
| 9 | Help users recognize/recover errors | 3 | Motivo nomeia o segmento que falhou; sem backfill (non-goal) |
| 10 | Help and documentation | 3 | Copy mínima do motivo; Ajuda/landing fora |
| **Total** | | **34/40** | **Good** |

## Cognitive load

Checklist: 1 h1; 1 modo visível; delta localizado na linha. **Pass**. Pontos de decisão no glance Decidir ≤4 (tabs + filtros). Por linha elegível = 2 (Promover/Excluir). **Pass**.

## Personas (arquivo; não ensaio no chat)

1. **Alex (admin Descoberta):** vê BTC `GO` em <5 s; AGLD Holdout e DOGE Treino abaixo; ADA sem chip apesar do holdout mau.
2. **Sam (teclado / SR):** landmarks 3/3 após Montar; chip não é só cor; motivo é texto.
3. **Riley (stress):** 43 trades não reprovam; Sharpe OOS 0,22 não mascara Calmar 0,42; Promover continua no NO-GO.

## Strengths

- Clone estrutural da rota `/combo/discovery`, não galeria ANTES/DEPOIS.
- Decisão gravada visível: treino fraco + holdout positivo = NO-GO **Treino**.
- BTC testemunho GO com números que o Combo reprovaria.
- Non-goals respeitados; Promover não travado; ranking Calmar intacto.

## Playwright (esta sessão)

- Live `/combo/discovery` → `/login`, h1 `Bem-vindo de volta`, landmarks 0/3. PNG `969-A-live-combo-discovery.png`. Descartado como prova de clone.
- Desktop 1440×900: aceite visível 10/10 PASS. 0 console / 0 pageerror / 0 ≥400.
- Mobile 390×844: mesmo aceite; NO-GO no viewport; landmarks Montar PASS. 0 console / 0 pageerror / 0 ≥400.
- PNGs: `969-A-desktop-1440x900.png`, `969-A-desktop-1440x900-nogo.png`, `969-A-desktop-1440x900-montar.png`, `969-A-desktop-1440x900-acomp.png`, `969-A-mobile-390x844.png`, `969-A-mobile-390x844-nogo.png`, `969-A-mobile-390x844-montar.png`, `969-A-mobile-390x844-acomp.png`, `969-A-live-combo-discovery.png`.

## Priority issues

Nenhum P0/P1 de produto/escopo/contrato visível.

## P0

_(nenhum)_

## P1

_(nenhum)_

## P3 — detalhe de Apply / clone de região fora do delta

- **P3-1** Montar condensado vs vivo: sem Iniciar, workbench, checkboxes 4h/1d, período/ranking, impedimentos/`<details>`. Landmarks Preflight + Rascunho presentes. Apply lê `DiscoveryPage.tsx` para Montar intacto.
- **P3-2** Chip GO/NO-GO: texto computado `--text-muted` `rgb(112,122,138)` em vez de `#93c5fd` / `#ff8294`. Bordas azul/danger intactas. Mobile: `display:flex; width:277px` (barra da coluna no card). Desktop já é `inline-flex` compacto. Apply: `.candidate .verdict.verdict-go` / `.verdict-nogo` com cor do par desenhado; no card mobile `width:max-content`.
- **P3-3** Mock não cobre linha `Amostra insuficiente`, fail-closed «Sharpe OOS ausente ou não finito», nem NO-GO treino cujo único falhanço é PF ou max DD. Padrão de copy está no `design.md`. Apply sanitiza `low_sample` / `insufficient_sample` sem chip (já P3 aceite no design).
- **P3-4** Coluna Ação clipada no first paint 1440×900 (Promover cortado); overflow da tabela. Vivo tem a mesma densidade — não bloqueia o aceite (Playwright lê Promover enabled).
- **P3-5** Default proto Decidir vs vivo `useState('montar')` sem sweep. Especificado no design; Apply não promove o default do proto a comportamento vivo.
- **P3-6** `WalkForwardSeal` vivo ignora `oos_verdict.reasons`. Delta = pintar `.seal-reason` na linha (Acompanhar e Decidir) a partir do perfil Discovery. Nome da função / campo persistido = P3 já aceite no `design.md`.

## Disposition

Aceitar P3 no Apply. Não reabrir grelha. Não reabrir decisões gravadas (treino+holdout positivo = NO-GO Treino; regra em todas as linhas; Baixa amostra sem selo). Não exigir segundo rework de Design por estes itens.

## Verdict

**PASS** — zero P0/P1 de produto/escopo/contrato visível. Tokens parseáveis 3/3. Regiões clonadas marcadas. Landmarks 3/3 no proto (Montar para Preflight/Rascunho). Disco == HTTPS. Sem galeria/ANTES-DEPOIS como index. Login descartado. Clone **não** alegado só por sidebar: prova = landmarks proto × `DiscoveryPage.tsx`.

`Design Agent verdict` final da coluna = síntese do pai após A+B. Este filho A não chama `process_event`.

---

```
Assessment A 969
tokens_ok: yes
clone_ok: yes
P0: nenhum
P1: nenhum
P3: Montar condensado; chip texto muted + mobile full-width; mock sem Amostra insuficiente / fail-closed / PF-only; Ação clipada 1440; default proto Decidir ≠ vivo Montar; reasons vivos não pintados (delta)
verdict: PASS
```
