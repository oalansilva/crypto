# Assessment A — card 1074 · change card-1074-swing-curto-1h-15m

> Avaliador A isolado (produto / UX / acessibilidade / fidelidade do clone). Onda dupla com-tela. Sem transcript do pai. Sem resultados do Assessment B. Sem nested-spawn. Sem `process_event`. Sem arraste de Status. Sem edição de `design.md`, HTML proto, OpenSpec, `backend/` ou `frontend/src/`. Sem `move_agent_to_root`. Única escrita: este arquivo.

`proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)`

## Metadata

- card: 1074 — Swing curto 1h/15m na Descoberta (templates das lacunas + slippage do timeframe)
- change: `card-1074-swing-curto-1h-15m`
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-1074-swing-curto-1h-15m`
- branch / q_git: `card-1074-swing-curto-1h-15m` @ `3a2a3e94`
- tuple: `bound_card=1074` · Status esperado=Design (MUST NOT arrastar)
- data (UTC): 2026-10-02T02:30Z
- modelo desta sessão: **Grok 4.6**, slug **`cursor-grok-4.6-high`**
- UI impact (rubrica D4): **affected** · `live_route: /combo/discovery` · `surface: existing` — linhas próprias parseáveis de `design.md` (L7–L9)
- Issue: REST `gh api repos/oalansilva/crypto/issues/1074` (OPEN; título GitHub ainda cita filtro 1D). Fronteira = body grelhado (Problema / História / Entra / Não entra). Sem reentrevista.
- Digest proto (disco + Vite local 5173/5175; HTTPS público ainda 404):
  - canónico `index.html` sha256 `10523181ee5398e5a67f767b74fe954f7a1f1841e27cd60fb2fe036f6410c1c9` · 53208 B = 26304 copied + 26904 generated
  - `http://127.0.0.1:5173/prototypes/card-1074-swing-curto-1h-15m/` IDENTICAL (HTTP 200, mesmo sha256, mesmos bytes)
  - `http://127.0.0.1:5175/prototypes/card-1074-swing-curto-1h-15m/` IDENTICAL
  - HTTPS `https://dev.criptofarol.com.br/prototypes/card-1074-swing-curto-1h-15m/` → HTTP 404, 608 B, página «Protótipo não encontrado» (pai ainda não publicou; `design.md` §Prototype Validation já diz que a dupla abre a URL pública depois do pai publicar)
- Irmãos HTML: nenhum (`index.html` só). T5 mede só este index.
- Ignore list: `.impeccable/critique/ignore.md` ausente
- D4: com-tela = autor + dupla + 1 rework. Tokens verificados como item da rubrica — nenhuma rodada extra só para o parser.
- Tooling: Playwright Python + Chromium (`executable_path=/usr/bin/chromium-browser`, `--no-sandbox`, headless) contra Vite local IDENTICAL. Viewports 1280×800 e 390×844. Evidência = árvore visível, innerText de landmarks, screenshots em `/tmp/1074-A` (não persistidos: este filho só escreve o snapshot).
- Mode: Impeccable **Operate**. `DESIGN.md` autoridade visual, não sobrescrito. Sem redesign da Descoberta.

## Limitação de sessão (obrigatória)

| URL pedida | URL final / evidência | Landmarks `/combo/discovery` |
|---|---|---|
| `https://dev.criptofarol.com.br/combo/discovery` | SPA autentica; pixels = cartão **Bem-vindo de volta** (login). Playwright `page.url` ficou `/combo/discovery` mas h1 da Descoberta = 0 | 0 |

**`/login` não é a rota.** Chrome de login **não** é evidência de clone e **não** autoriza PASS de fidelidade. Sem cookie de administrador, a avaliação de clone usa: (1) protótipo canónico local com digest == `design.md`, (2) catálogo `scripts/process-fsm/route-landmarks.yaml`, (3) fonte viva `DiscoveryPage.tsx` (só leitura). Sidebar 224px / tokens `--bg-*` **não** bastam.

HTTP 200 isolado nunca é PASS. O 200 do proto local coincide com digest e com asserts de landmark/contrato no browser. HTTPS público 404 não é P0 de produto (publicação do pai).

## Tokens parseáveis (rubrica D4)

`design.md` linhas próprias:

```
UI impact: affected
live_route: /combo/discovery
surface: existing
```

Justificativa no corpo: clone+delta Operate da rota existente `/combo/discovery`; **não** superfície nova; **não** empresta `/combo/select` nem `/favorites`. Regiões clonadas marcadas (`COPIED:start`/`COPIED:end` 14/14): shell autenticado + heading + 3 modos + Rascunho + Preflight + chrome Acompanhar + grelha parciais + header/grelha Decidir + nota rank-stable. Delta fora desses blocos (heading 4h/1h/15m/1d, eixo Timeframes swing 2×2, chips dos 3 templates, rótulo de custo, filtro e linhas 1h/15m no placar). URL canónica **não** é painel ANTES/DEPOIS nem grelha de N estados. **PASS** deste item da rubrica.

## Digest proto (disco == local servido)

| Ponta | sha256 | bytes | HTTP |
|---|---|---|---|
| disco `frontend/public/prototypes/card-1074-swing-curto-1h-15m/index.html` | `10523181ee5398e5a67f767b74fe954f7a1f1841e27cd60fb2fe036f6410c1c9` | 53208 | — |
| Vite `127.0.0.1:5173` / `5175` | idêntico | 53208 | 200 |
| `design.md` §Prototype Validation | idêntico | 53208 | — |
| HTTPS `dev.criptofarol.com.br/prototypes/card-1074-swing-curto-1h-15m/` | 404 «Protótipo não encontrado» | 608 | 404 |

Disco == Vite == prompt: IDENTICAL. HTTPS ainda não publicado.

## Fidelidade (clone da página viva)

Catálogo `/combo/discovery` (`route-landmarks.yaml`): `selectors: []` · texts `Descoberta de estratégias swing`, `Preflight`, `Rascunho de varredura`.

Fonte viva `DiscoveryPage.tsx` (só leitura): h1 L1562; subcopy incumbente «Compare templates em 4h e 1d» L1564 (delta do card troca isto); fieldset «Timeframes swing» L2159–2185 com checkboxes visuais `4 horas` / `1 dia`; aside `aria-label="Preflight da varredura"`; h2 `Rascunho de varredura`; filtro Timeframe só `4h`/`1d` L2547–2549; impedimento vivo `Escolha 1 timeframe (4h ou 1d).` L647.

| Landmark | Catálogo / vivo | Proto 5173 + Playwright (1280 e 390) |
|---|---|---|
| `Descoberta de estratégias swing` | h1 | h1 visível no default Montar; exact 1 |
| `Preflight` | `aria-label="Preflight da varredura"` + h2 `Preflight` | h2 visível no default Montar; aside `aria-label="Preflight da varredura"` |
| `Rascunho de varredura` | h2 em tabpanel Montar | article `aria-label="Rascunho de varredura"` + h2 visível no default Montar |

Anti-padrões P0:

- URL canónica (index) é a Descoberta autenticada (shell 224px + breadcrumb Combo/Varreduras + h1 + 3 modos + Montar + Acompanhar + Decidir). **Não** é painel ANTES/DEPOIS. Botões Antes/Depois visíveis = 0. Texto visível `ANTES`/`DEPOIS` = 0 (único hit está em comentário de fonte).
- **Não** é grelha de N estados no lugar da listagem. Zero HTML irmão. Default canónico = Montar (`data-state="montar"`). Tabs **trocam markup** (`.modepanel.active` único; Acompanhar revela progresso+parciais; Decidir revela `table.lb`).
- Pares `COPIED:start`/`COPIED:end` = 14/14; soma UTF-8 copiada 26304 > 0.
- Chrome (sidebar, amarelo `#fcd535`, nav Descoberta `aria-current=page`) = **folha**, não prova. Prova = landmarks do catálogo no proto canónico + delta só no heading / timeframes / templates / custo.

## Produto (escopo — não reabrir grelha)

Contrato grelhado observado (`data-state` montar no load fresco; Decidir via tab):

| Aceite visível | Evidência (Playwright + pixels) | Disposition |
|---|---|---|
| Descoberta aceita 4h, 1h, 15m e continua 1d | 4 controlos visíveis: «15 minutos», «1 hora», «4 horas», «1 dia»; default só **1 dia** `aria-pressed=true`; 1h/15m disponíveis, não pré-marcados | OK |
| Sem 1m / 5m / 30m na Descoberta | 0 rótulo «1 minuto» / «30 minutos»; filtro Decidir = Todos / 1d / 4h / 1h / 15m | OK |
| Heading não promete filtro 1D | «Compare templates em 4h, 1h, 15m e 1d.»; 0 substring visível «filtro 1D»; 0 controlo de tendência do gráfico diário | OK |
| 3 templates novos visíveis; sem `lab_` | chips Montar: Canal Donchian + volume · Squeeze de Bollinger · Pullback média longa + RSI + ADX + incumbente Médias Móveis: Cruzamento. `lab_` no body visível = 0 | OK |
| Custo só de leitura; taxa 0,075% + slip do TF | nota Preflight `taxa 0,075% · slippage do timeframe (0,02% em 4h e 1d · 0,03% em 1h · 0,05% em 15m) · sem campo para alterar`; `input` count = 0 | OK |
| Linha 1h / 15m no placar | Decidir rank 2 Donchian BTC **1h** `taxa 0,075% · slippage 0,03%`; rank 4 Squeeze BTC **15m** `slippage 0,05%`; Promover à mão | OK |
| Selo e placar da Descoberta; sem promoção automática | GO / NO-GO (Holdout Sharpe OOS; Treino Calmar < 1); Baixa amostra com Promover disabled; 0 copy «promoção automática» | OK |
| Index = clone, não painel de estados | 1 HTML; 3 modos; landmarks 3/3 | OK |

Não-goals respeitados na tela: sem campo de slippage; sem filtro 1D; sem `lab_`; sem tela nova; VWAP fora de `/combo/discovery` (só nos templates, não é UI desta rota); short fora do Montar (só Long).

## UX

Hierarquia desktop: shell autenticado → h1 Descoberta → tablist 3 modos → **Montar** (Rascunho + Preflight). Uma decisão de eixos (templates / símbolos / TFs). Decidir = placar Calmar com Promover por linha.

Carga cognitiva: **média (Operate)**. 4 TFs no fieldset 2×2 (teto de 4). Filtro Decidir ≤4 TFs + Todos. Delta cabe no glance: heading lista os quatro; chips nomeiam as lacunas; nota de custo é leitura.

Prevenção: default não pré-marca 1h/15m; custo sem input. Recuperação: Novo rascunho no Acompanhar volta a Montar; Limpar filtros no Decidir (estático no mock).

Pico: linhas 1h/15m com slip honesto ao lado do selo GO — alinha com o problema grelhado (custo realista).

## Acessibilidade

- `lang="pt-BR"`; `:focus-visible` 2px `#3b82f6`; alvos `.tf-opt` / `.promote` `min-height: 44px`.
- Tabs `role=tablist/tab/tabpanel` + `aria-controls` + setas + roving tabindex; 1 painel `.active`.
- Progressbar ARIA completa (`valuemin/max/now` + label).
- Tabelas em `role=region` `tabindex=0` + caption sr-only de rank estável.
- Timeframes: proto usa `button` + `aria-pressed` + `role=group`; vivo usa `fieldset` + `input type=checkbox` visualmente idêntico. Widget nativo = Apply (P3).
- Impedimento «Escolha 1 timeframe (4h, 1h, 15m ou 1d).» **ausente** no mock (desmarcar todos os TFs → 0 pressed, 0 mensagem). Apply lê `DiscoveryPage.tsx` L647 e alarga a copy (P3).
- Contraste: tokens incumbentes Binance (`--accent #fcd535`, `--success`, `--danger-text`). Sem par novo.

## Responsividade

Desktop 1280: sidebar 224px; heading + 4 TFs 2×2 + Preflight sticky à direita; Decidir com landmarks de custo nas linhas 1h/15m.

Mobile 390: sidebar some; mobilebar; Preflight abaixo da dobra (clone do Montar incumbente, P3); TFs 2×2 intactos; Decidir em cards com Promover visível. Overflow estrutural 0 no Montar.

## Estados

| Estado | Proto | Apply deve… |
|---|---|---|
| Montar default (1d só) | ✓ | preservar default `1d`; acrescentar 15m/1h/4h no mesmo fieldset |
| 0 timeframes | mock permite; sem impedimento | preservar L647, copy alargada |
| Decidir misto 1d/4h/1h/15m | ✓ linhas novas; header cola 0,03% | rótulo **por linha**; header não mentir um único slip |
| GO / NO-GO / Baixa amostra | ✓ selo Descoberta; Promover à mão | preservar #969 |
| loading / erro / 403 / sessão | ausente (mock) | preservar vivo |
| Modal Promover | ausente | preservar vivo |

## Design specificity

A composição é a Descoberta autenticada do Farol (AppNav, 3 modos, Rascunho, Preflight, leaderboard Calmar, selo GO/NO-GO). Não iria a um SaaS genérico inalterado. Modo Impeccable: **Operate**. Delta = copy do heading, quatro TFs, três chips, rótulo taxa+slippage.

## Heurísticas Nielsen (0–4, Operate) — só neste snapshot

| # | Heurística | Score | Nota |
|---|---|---|---|
| 1 | Visibility of system status | 3 | 1 modo + chip RASCUNHO/EM CURSO; header Decidir cola slip único |
| 2 | Match between system and real world | 4 | taxa 0,075% e slip por TF no vocabulário do body |
| 3 | User control and freedom | 3 | tabs + novo rascunho + Promover/Excluir; sem Iniciar no mock |
| 4 | Consistency and standards | 3 | clone do shell/modos; TFs em botão vs checkbox vivo |
| 5 | Error prevention | 3 | sem campo de slip; falta impedimento 0-TF |
| 6 | Recognition rather than recall | 4 | chips nomeados; custo na nota e nas linhas 1h/15m |
| 7 | Flexibility and efficiency | 3 | teclado nas tabs; um caminho Operate |
| 8 | Aesthetic and minimalist design | 3 | condensou Montar (sem workbench/Iniciar) mas o delta cabe |
| 9 | Help users recognize, diagnose, recover | 3 | NO-GO com motivo; Baixa amostra nomeada |
| 10 | Help and documentation | 3 | nota rank-stable; Ajuda fora de escopo |
| **Total** | | **32/40** | Good |

## Cognitive load

Checklist: chunking dos 4 TFs OK; 3 templates novos + 1 incumbente no glance OK. Falha residual: header Decidir + linhas com slips diferentes pede comparação. **Não é P0.**

## Findings

### P0 — bloqueante (produto / escopo / contrato visível)

- nenhum.
  - Landmarks 3/3 no proto (Montar para Preflight/Rascunho).
  - URL canónica = clone Operate `/combo/discovery`, não grelha de N estados nem ANTES/DEPOIS.
  - 4 TFs visíveis; heading sem filtro 1D; 3 templates; custo só leitura.

### P1 — deve corrigir antes de PASS

- nenhum.

### P2 — residual visível, não bloqueia o teto 1+1+1

- **[P2] Cabeçalho do Decidir cola `slippage 0,03%` num sweep misto** enquanto rank 1 é **1d** (contrato 0,02%) e a linha 15m mostra **0,05%**. O vivo hoje deriva evidência da primeira linha elegível; o card pede rótulo **conforme a linha**. **Visível:** meta do leaderboard vs rank 2/4. Disposition: **n/a** (não bloqueia; Apply persiste `fees_slippage` por resultado e não afirma um único slip de sweep quando os TFs diferem).
- **[P2] Linhas 1d e 4h do Decidir omitem `taxa 0,075% · slippage 0,02%`.** O delta 1h/15m está correcto; 1d/4h ficam sem o rótulo novo (o problema original da Descoberta era exactamente o rótulo 0,1%/0,1% nestes TFs). A nota do Montar já lista 0,02%. Disposition: **n/a** (Apply escreve o mesmo rótulo em todas as linhas).

### P3 — detalhe de Apply / incumbente (não reabrir como P0/P1)

- **[P3] Montar condensado vs vivo:** sem CTA `Iniciar varredura — N, ~T`, sem workbench/listas inline, sem impedimento 0-TF, sem `<details>` técnico. Landmarks Preflight + Rascunho presentes. Disposition: **aceito-P3-Apply** — Apply lê `DiscoveryPage.tsx`.
- **[P3] Timeframes em `button`+`aria-pressed` em vez de `fieldset`+checkbox oculto** (visualmente o mesmo chip 44px). Disposition: **aceito-P3-Apply**
- **[P3] Acompanhar «Long + Short» no rascunho congelado** e parciais só 1d/4h. Short já escondido no Montar; 1h/15m estão no placar Decidir. Disposition: **aceito-P3-Apply**
- **[P3] Modal Promover / estados loading-erro-403-sessão ausentes** no mock. Disposition: **aceito-P3-Apply**
- **[P3] HTTPS público 404** — publicação do pai, não furo de produto. Digest local == Vite == `design.md`. Disposition: **aceito-P3-Apply** (pai publica)
- **[P3] Filtro Decidir e combinação do Preflight estáticos** (JS só tabs/TFs/expand). Disposition: **aceito-P3-Apply**
- **[P3] VWAP / helper de slippage / `DISCOVERY_SWING_TIMEFRAMES`** — *como*, não tela. Disposition: **aceito-P3-Apply**
- **[P3] Pullback só como chip no Montar** (não há linha Decidir). Critério de escolha na Descoberta cumprido. Disposition: **aceito-P3-Apply**

## Disposition (resumo)

| Finding | Gravidade | Classe | Bloqueia? | Disposition |
|---|---|---|---|---|
| (nenhum P0/P1) | — | — | não | n/a |
| Header Decidir slip único 0,03% em sweep misto | P2 | produto visível (rótulo) | não | n/a |
| Linhas 1d/4h sem rótulo 0,02% | P2 | produto visível (rótulo) | não | n/a |
| Montar condensado, widget TF, Short no Acompanhar, modal, HTTPS 404, mock estático, *como* VWAP/slip | P3 | detalhe de Apply | não | aceito-P3-Apply |

## Tokens do autor

**ok**

- `UI impact: affected`
- `live_route: /combo/discovery`
- `surface: existing`
- regiões clonadas = shell + heading + 3 modos + Rascunho + Preflight + Acompanhar + Decidir
- URL canónica = clone `/combo/discovery` + delta heading/TFs/templates/custo; **não** painel ANTES/DEPOIS; **não** grelha de N estados

## Verdict

**PASS**

Nenhum P0/P1 de produto/escopo/contrato visível. Teto 1+1+1: este artefacto é o Assessment A; P3 aceitos ficam no Apply; P2 residuais não justificam segundo rework.

Design fecha em 1+1+1: sem `## Design Critique` aqui (o pai publica).

## Artefactos desta sessão

- `.impeccable/critique/1074-card-1074-swing-curto-1h-15m-assessment-A.md` (este arquivo; única escrita)
