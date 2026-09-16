# Assessment A — card 948 · change card-948-discovery-deleted-favorite

> Avaliador A isolado (produto / UX / a11y / fidelidade do clone). Mesmo modelo do chat (Grok 4.6). Sem transcript do pai. Sem nested-spawn. Sem edição de `design.md`, HTML proto, `backend/`, `frontend/src/` ou OpenSpec. Sem `process_event`. Sem arraste de Status. Única escrita: este arquivo + PNGs `948-A-*` (+ JSON de gate). Sem HTML fonte colado.

`proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)`

## Metadata

- card: 948 — "Descoberta: candidato continua 'Já existe' depois de excluir o favorito"
- change: `card-948-discovery-deleted-favorite`
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-948-discovery-deleted-favorite`
- branch: `card-948-discovery-deleted-favorite`
- tuple: `bound_card=948` · `q_git=card-948-discovery-deleted-favorite`
- data (UTC): 2026-09-16T01:04Z
- Status observado: Design (prompt do pai; MUST NOT `gh project item-list`)
- UI impact (rubrica D4): **affected** · `live_route: /combo/discovery` · `surface: existing` — linhas próprias 1–3 de `design.md` (parseáveis)
- Digest proto (autor, verificado nesta sessão): sha256 `1f8b13c879526506637fe6cce691b87db9d38fd5d4c7047e4be9d839bba13d74` · 69158 bytes
- Servido HTTPS == local: IDENTICAL (`sha256` e bytes iguais; HTTP 200)
- Issue: REST `gh api repos/oalansilva/crypto/issues/948` (não `gh issue view`). Grill: fronteira vazia. Q1 = órfão Já existe → Promover sem nota · Q2 = órfão Favorito tier 3 também entra — fechadas no design; **não reabertas**.
- D4: com-tela = autor + dupla + 1 rework. Tokens verificados como item da rubrica — nenhuma rodada extra só para o parser.
- Ignore list: `.impeccable/critique/ignore.md` ausente
- Tooling: Playwright Python + Chromium 1243 (`chrome-linux-arm64`), HTTPS real, viewports 1440×900 e 390×844. 0 console error / 0 pageerror no proto.

## Limitação de sessão (obrigatória)

| URL pedida | URL final | h1 | Landmarks `/combo/discovery` |
|---|---|---|---|
| `https://dev.criptofarol.com.br/combo/discovery` | `https://dev.criptofarol.com.br/login` (HTTP 200) | `Bem-vindo de volta` | 0/3 |

**`/login` não é a rota.** Chrome de login **não** é evidência de clone e **não** autoriza PASS de fidelidade. Sem cookie de administrador, a avaliação de clone usa: (1) protótipo canónico HTTPS, (2) fonte viva `frontend/src/pages/DiscoveryPage.tsx` vs catálogo `scripts/process-fsm/route-landmarks.yaml`. Sidebar 224px / tokens `--bg-*` **não** bastam.

HTTP 200 isolado nunca é PASS. Os 200 do proto coincidem com digest e com asserts de landmark/contrato no browser.

## Tokens parseáveis (rubrica D4)

`design.md` linhas próprias 1–3:

```
UI impact: affected
live_route: /combo/discovery
surface: existing
```

Justificativa no corpo: clone+delta Operate da rota existente `/combo/discovery`; regiões clonadas marcadas («só estas»: shell AppNav autenticado + heading + 3 modos + Montar landmarks + chrome Acompanhar + grelha de parciais + header/grelha Decidir). Delta só nas células de acção/nota das linhas órfãs vs vivo. **PASS** deste item da rubrica. Nenhuma rodada extra nasce só para o parser.

## Digest proto (disco == HTTPS)

| Ponta | sha256 | bytes | HTTP |
|---|---|---|---|
| disco `frontend/public/prototypes/card-948-discovery-deleted-favorite/index.html` | `1f8b13c879526506637fe6cce691b87db9d38fd5d4c7047e4be9d839bba13d74` | 69158 | — |
| HTTPS `https://dev.criptofarol.com.br/prototypes/card-948-discovery-deleted-favorite/` | `1f8b13c879526506637fe6cce691b87db9d38fd5d4c7047e4be9d839bba13d74` | 69158 | 200 |
| `design.md` Prototype / prompt do pai | prefixo `1f8b13c879526506` · completo igual | 69158 | — |

Disco == HTTPS: IDENTICAL.

## Fidelidade (clone da página viva)

Catálogo `/combo/discovery` (`scripts/process-fsm/route-landmarks.yaml`): `selectors: []` · texts `Descoberta de estratégias swing`, `Preflight`, `Rascunho de varredura`.

| Landmark | `DiscoveryPage.tsx` (vivo, sem sessão) | Proto + Playwright |
|---|---|---|
| `Descoberta de estratégias swing` | h1 da página | h1 visível no default Decidir (desktop e mobile); exact 1 |
| `Preflight` | `aria-label="Preflight da varredura"` + h2 `Preflight` | hidden no default Decidir (painel inactivo, igual ao vivo com sweep); **visível após tab Montar** |
| `Rascunho de varredura` | h2 em tabpanel Montar | h2 visível após tab Montar |

Anti-padrões P0:

- URL canónica `…/prototypes/card-948-discovery-deleted-favorite/` → index é a página (shell 224px + heading + 3 modos + Acompanhar + Decidir). **Não** é painel ANTES/DEPOIS. Botões Antes/Depois = 0. Texto visível `ANTES/DEPOIS` = 0 (o comentário de fonte «sem painel ANTES/DEPOIS» não conta como galeria).
- Não é grelha de N estados no lugar da listagem. Decidir default = tabela de candidatos (5 linhas mock). Acompanhar = tabela de parciais top-5.
- Tabs trocam painel (`aria-selected` + `aria-controls`). Não é `aria-pressed` cosmético. Default = Decidir (`aria-selected=true`) — testemunho do print.
- 11 pares `COPIED:start/end` (copied > 0). Delta óbvio = células de acção/nota das linhas órfãs vs vivo (Q1/Q2) nas duas grelhas.

Chrome presente (sidebar 224px, Inter, nav Descoberta activa) = **folha**, não prova. Prova = landmarks 3/3 no proto, alinhados ao TSX.

Tab Acompanhar = rótulo vivo `Acompanhando #af8fb5de` (prefixo da varredura), não «Acompanhamento».

## Produto (aceite visível — não reabrir Q1 / Q2)

Delta pedido: depois de excluir o favorito, órfão Já existe e órfão Favorito tier 3 voltam a Promover sem nota de favorito; a linha permanece; favorito vivo continua Já existe + Equivale…; Decidir e Acompanhar iguais se a linha visível; Excluir da grelha fora; sem nota histórica; limpeza PROD pontual não é o conserto.

Contrato visível julgado no proto HTTPS (Playwright + pixels), não no HTML fonte.

| Aceite visível | Evidência (Playwright + pixels) | Disposition |
|---|---|---|
| Órfão que era Já existe (`RS-E2FF8F9FEB`, rank 1, BTC/USDT 1d): **Promover**, sem **Já existe**, sem **Equivale ao favorito ativo N**, linha permanece | Decidir desktop/mobile: botão Promover enabled, Excluir visível, 0 Já existe / 0 Equivale / 0 Favorito tier 3 / 0 «já esteve» nessa linha. Identidade `Médias Móveis: Tendência em Virada` + result_id permanecem. | OK |
| Órfão que era Favorito tier 3 (`RS-EA2A508DBD`, rank 2): **Promover**, sem esse rótulo | Decidir: Promover enabled; `Favorito tier 3` visível na página = 0. Linha permanece. | OK |
| Favorito vivo: **Já existe** + **Equivale ao favorito ativo 12** permanecem | Rank 3 `RS-LIVE-DUP`: nota Equivale… visível; botão Já existe **disabled**; Excluir continua. Não é Promover. | OK |
| Decidir e Acompanhar iguais se a linha visível | Acompanhar rank 1 Promover (BTC/USDT, mesmos números do órfão Q1); rank 2 Promover; rank 3 Já existe + Equivale 12 (disabled). 0 Favorito tier 3. | OK |
| Sem nota histórica | `já esteve` visível = 0; `já foi favorito` = 0; `historical_duplicate` = 0. «Histórico de varreduras» = clone do chrome vivo, não nota de órfão. | OK |
| Excluir da grelha fora / linha não some só pela exclusão do favorito | Órfãos 1 e 2 ainda na listagem com Excluir ao lado de Promover. | OK |
| Outros bloqueios reais permanecem | Decidir última linha: selo `Amostra insuficiente`, N/A nas métricas, só Excluir (sem Promover). | OK |
| Tentar promover no órfão não recusa fantasma | Clique Promover em `RS-E2FF8F9FEB` abre diálogo `Promover a favorito tier 3` com CTA enabled `Promover como tier 3`. Sem copy de duplicata do N apagado. Linha por baixo permanece Promover. | OK |
| Montar sem delta de grelha | Após tab: Preflight + Rascunho visíveis; tabelas visíveis = 0. | OK |

Q1/Q2 **não reabertas**. Mecanismo DELETE+relida = P3 Apply já aceite em `design.md`. Limpeza PROD do favorito 9 **não** julgada como conserto.

## UX

Hierarquia: h1 → tablist 3 modos → 1 painel. Default Operate = Decidir (print do testemunho). Glance: órfãos lêem-se como candidatos livres (Promover amarelo); vivo lê-se como bloqueado (Já existe muted + nota Equivale 12). Sem terceiro rótulo inventado.

Carga: decisão por linha órfã = 2 (Promover / Excluir). Vivo = 1 acção real (Excluir) + estado Já existe. Tablist = 3. Desktop overflow-x: Ação clipa à direita a 1440 com sidebar 224px — risco já visto em cards irmãos; não esconde o contrato (Promover vs Já existe distinguem-se pela cor/posição; no mobile os rótulos cabem).

## Acessibilidade

- `lang=pt-BR`; alvos de acção `min-height` 44px (Promover / Já existe / Excluir / tabs / + detalhes).
- Tablist/tab/tabpanel + `aria-selected` (não `aria-pressed`). 1 tabpanel visível de cada vez.
- Selo `Amostra insuficiente` e nota `Equivale ao favorito ativo 12` são texto, não só cor.
- Já existe disabled (não só paleta). Órfão Promover enabled.
- Contraste: pares Binance (amarelo CTA vs muted Já existe vs vermelho Excluir). GO/NO-GO textuais.
- Nav do shell e «novo rascunho» inline = clone, não delta (P3).

## Responsividade

- Desktop 1440×900: contrato visível nas duas grelhas; Ação clipa sem scroll horizontal (`clip` nos botões 156–167px). PNGs `948-A-desktop-1440x900-{decidir,decidir-promover,acompanhar,montar}.png`.
- Mobile 390×844: cards `data-label`; Promover / Já existe / Excluir 44×128 visíveis sem clip. Rank 1–2 Promover; rank 3 Já existe + Equivale 12. PNGs `948-A-mobile-390x844-{decidir,acompanhar,montar}.png`.
- Sem overflow que esconda o contrato. 0 console / 0 pageerror.

## Estados

Mock cobre: Decidir misto (2 órfãos Promover + 1 vivo Já existe + 1 unique extra + 1 amostra insuficiente); Acompanhar top-5 com a mesma verdade nos três primeiros; Montar landmarks; diálogo promover no órfão. Não mocka: Baixa amostra, loading/erro de leaderboard, vazio, POST real de promoção (Apply). Cobertura de mock = P3, não buraco do contrato visível.

## Design specificity

Composição da Descoberta (modos, parciais top-5, leaderboard Calmar, selo de amostra, acções #663/#944). Não poderia ir a um SaaS genérico inalterado. Modo Impeccable: **Operate** / refinement. Folha Binance; `DESIGN.md` não reescrito.

## Heurísticas Nielsen (0–4, Operate; só neste snapshot)

| # | Heurística | Score | Nota |
|---|---|---|---|
| 1 | Visibility of system status | 4 | Chip concluída + run selector + Decidir selected |
| 2 | Match between system and real world | 4 | Órfão = Promover; vivo = Já existe; sem nota fantasma |
| 3 | User Control and Freedom | 3 | Tabs + Excluir + Voltar no modal; undo de favorito é fora desta grelha |
| 4 | Consistency and Standards | 4 | Mesma verdade Decidir/Acompanhar; copy viva sem ramo novo |
| 5 | Error Prevention | 4 | Vivo disabled; insuficiente sem Promover; órfão abre diálogo em vez de recusar N morto |
| 6 | Recognition rather than recall | 4 | Estado na célula; operador não precisa lembrar se o N ainda existe |
| 7 | Flexibility and efficiency | 3 | Sort/filtros/paginação do vivo omitidos no mock |
| 8 | Aesthetic and Minimalist Design | 3 | Densidade da grelha aceite; Ação aperta no desktop |
| 9 | Help users recognize/recover errors | 3 | Modal clona o vivo; proto não simula recusa fantasma (é o ponto) |
| 10 | Help and Documentation | 3 | Nota educacional + hints; Ajuda fora |
| **Total** | | **35/40** | **Good** |

## Cognitive load

Checklist: 1 h1; 1 modo visível; delta = 2 estados de acção já nomeados (Promover vs Já existe). **Pass**. Decisão no glance Decidir órfão ≤4 (Promover/Excluir + tabs). Sem nota histórica extra a traduzir.

## Emotional journey

Vale (Já existe mentiroso para N MISSING → operador preso) → pico (Promover de novo no mesmo sítio, linha não some) → fim (vivo 12 continua bloqueado; insuficiente continua sem Promover). Reassegurança: Excluir da grelha não se mistura com excluir favorito.

## Personas (arquivo; não no chat)

1. **Alex (Decidir, voltou depois de apagar o favorito 9):** rank 1 e 2 mostram Promover; não há Equivale ao 9; confirma no diálogo «Promover como tier 3».
2. **Alex (Acompanhar, mesma varredura):** BTC/ETH Promover; SOL Já existe + Equivale 12.
3. **Sam (teclado / SR):** landmarks 3/3 após Montar; Já existe disabled anunciável; Promover 44px.

## Strengths

- Clone estrutural da rota (`/combo/discovery`), não galeria ANTES/DEPOIS.
- Delta mínimo e óbvio: só as células órfãs vs vivo.
- Q1 e Q2 visíveis no mesmo ecrã, com o vivo a contrastar.
- Non-goals visíveis (Montar sem grelha; Excluir permanece; sem nota histórica; insuficiente intacto).

## Playwright (esta sessão)

- Desktop 1440×900 e mobile 390×844: contrato visível PASS. Landmarks Montar visíveis após tab. Modal promover no órfão sem recusa. 0 console / 0 pageerror.
- Live `/combo/discovery` → `/login` (descartado). PNG `948-A-live-combo-discovery.png`.
- Detector: não corrido aqui (Assessment A; B é o detector).
- PNGs: `948-A-desktop-1440x900-{decidir,decidir-promover,acompanhar,montar}.png`, `948-A-mobile-390x844-{decidir,acompanhar,montar}.png`, `948-A-live-combo-discovery.png`. Gate: `948-A-gate.json`.

## Priority issues

Nenhum P0/P1 de produto/escopo/contrato visível.

## P0

_(nenhum)_

## P1

_(nenhum)_

## P2

_(nenhum)_

## P3 — detalhe de Apply / clone de região fora do delta

- **P3-1** Montar condensado vs vivo: landmarks Preflight + Rascunho presentes; sem CTA Iniciar / workbench completo. Apply lê `DiscoveryPage.tsx` para Montar intacto.
- **P3-2** Overflow-x desktop: Promover / Já existe / Excluir clipam a 1440×900 com sidebar 224px sem scroll. Mobile 390 cabe. Não esconde Promover vs Já existe. Detalhe de densidade já visto em irmãos; Apply.
- **P3-3** Decidir mock: 5 `<tr>` vs copy «680 de 680 · página 1 de 26»; filtros/paginação cosméticos. Acompanhar top-5 usa `símbolo · tf` (clone vivo) em vez do `result_id` do Decidir — mapeamento dos órfãos é por métricas/ordem, não por id visível.
- **P3-4** Diálogo promover clona o vivo (`Retorno (CAGR)`, «o histórico da varredura fica»). Não é nota histórica na grelha (Q1). POST real / favorito número novo = Apply.
- **P3-5** Helper partilhado «favorito ainda existe?», hook no DELETE, append `DiscoveryDedupEvidence`, testes GET/POST N MISSING vs vivo — já no contrato Apply de `design.md`. Frontend só muda se o payload ainda mentir.
- **P3-6** Nav 42px / «novo rascunho» 18px / CSS vars do proto vs folha = clone de shell.

## Disposition

Aceitar P3 no Apply. Não reabrir grelha. Não reabrir Q1 / Q2. Não exigir segundo rework de Design por estes itens.

## Verdict

**PASS** — zero P0/P1 de produto/escopo/contrato visível. Tokens parseáveis 3/3. Landmarks 3/3 no proto (Montar para Preflight/Rascunho). Disco == HTTPS. Sem galeria/ANTES-DEPOIS como index. copied > 0 (11 pares). Delta = órfãos Promover sem nota + vivo Já existe. `/login` descartado. Clone **não** alegado só por sidebar: prova = landmarks proto × `DiscoveryPage.tsx`. Q1 `RS-E2FF8F9FEB` Promover; Q2 `RS-EA2A508DBD` Promover sem Favorito tier 3; vivo Equivale 12 permanece.

`Design Agent verdict` final da coluna = síntese do pai após A+B. Este filho A não chama `process_event`.

---

```
Assessment A 948
tokens_ok: yes
clone_ok: yes
P0: nenhum
P1: nenhum
P3: Montar condensado; Ação overflow desktop; mock 680/5 linhas; modal clone vivo (CAGR / histórico da varredura); DELETE+relida Apply; nav/CSS vars shell
verdict: PASS
```
