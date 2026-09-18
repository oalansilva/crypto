# Assessment A — card 967 · change card-967-discovery-recupera-varredura-ativa

> Avaliador A isolado (produto / UX / a11y / fidelidade do clone). Mesmo modelo do chat (Grok 4.6). Sem transcript do pai. Sem nested-spawn. Sem edição de `design.md`, HTML proto, `backend/`, `frontend/src/` ou OpenSpec. Sem `process_event`. Sem arraste de Status. Única escrita: este arquivo + PNGs `967-A-*` (+ JSON de gate). Sem HTML fonte colado.

`proxy modelo: Assessment A → Grok 4.6 (cursor-grok-4.6-high)`

## Metadata

- card: 967 — "Descoberta: perde a varredura ativa na tela em PROD (logout/login recupera)"
- change: `card-967-discovery-recupera-varredura-ativa`
- cwd: `/srv/apps/dev/criptofarol/crypto-worktrees/card-967-discovery-recupera-varredura-ativa`
- branch: `card-967-discovery-recupera-varredura-ativa`
- tuple: `bound_card=967` · `q_git=card-967-discovery-recupera-varredura-ativa`
- data (UTC): 2026-09-17T12:47Z
- Status observado: Design (GraphQL pontual `repository.issue(number:967).projectItems` → Project 1 `oalansilva`, item `PVTI_lAHOAAHtBM4BV8b2zg7adKU`, Status=`Design`. GraphQL remaining=4709. MUST NOT `gh project item-list`)
- UI impact (rubrica D4): **affected** · `live_route: /combo/discovery` · `surface: existing` — linhas próprias 1–3 de `design.md` (parseáveis)
- Digest proto (autor, verificado nesta sessão): sha256 `9e0447c6f03907bc7c57c5a0045a62ed89f5cb135015c0ff7297dc3ae213e997` · 42186 bytes
- Servido HTTPS == local: IDENTICAL (`sha256` e bytes iguais; HTTP 200)
- Issue: REST `gh api repos/oalansilva/crypto/issues/967` (não `gh issue view`). Grill: fronteira vazia. Q1=A reconstituição **sozinha**; clique só se a automática falhar de novo — fechada no design; **não reaberta**.
- D4: com-tela = autor + dupla + 1 rework. Tokens verificados como item da rubrica — nenhuma rodada extra só para o parser.
- Ignore list: `.impeccable/critique/ignore.md` ausente
- Tooling: Playwright Python + Chromium 1243 (`chrome-linux-arm64`), HTTPS real, viewports 1440×900 e 390×844. 0 console error / 0 pageerror no proto.

## Limitação de sessão (obrigatória)

| URL pedida | URL final | h1 | Landmarks `/combo/discovery` |
|---|---|---|---|
| `https://dev.criptofarol.com.br/combo/discovery` | `https://dev.criptofarol.com.br/login` (HTTP 200 SPA, depois client-nav) | `Bem-vindo de volta` | 0/3 |

**`/login` não é a rota.** Chrome de login **não** é evidência de clone e **não** autoriza PASS de fidelidade. Sem cookie de administrador, a avaliação de clone usa: (1) protótipo canónico HTTPS, (2) fonte viva `frontend/src/pages/DiscoveryPage.tsx` vs catálogo `scripts/process-fsm/route-landmarks.yaml`. Sidebar 224px / tokens `--bg-*` **não** bastam.

HTTP 200 isolado nunca é PASS. Os 200 do proto coincidem com digest e com asserts de landmark/contrato no browser. PNG `967-A-live-combo-discovery.png` (login, descartado).

## Tokens parseáveis (rubrica D4)

`design.md` linhas próprias 1–3:

```
UI impact: affected
live_route: /combo/discovery
surface: existing
```

Justificativa no corpo: clone+delta Operate da rota existente `/combo/discovery`; regiões clonadas marcadas («só estas»: shell AppNav autenticado + heading + 3 modos + Montar (Preflight / Rascunho / heading) + chrome Acompanhar + grelha de parciais + header/grelha Decidir). Delta só no caminho feliz: Acompanhar visível com `#c91f3a07…` e `12 de 24`; banner vermelho ausente; Iniciar outra bloqueado. **PASS** deste item da rubrica. Nenhuma rodada extra nasce só para o parser.

## Digest proto (disco == HTTPS)

| Ponta | sha256 | bytes | HTTP |
|---|---|---|---|
| disco `frontend/public/prototypes/card-967-discovery-recupera-varredura-ativa/index.html` | `9e0447c6f03907bc7c57c5a0045a62ed89f5cb135015c0ff7297dc3ae213e997` | 42186 | — |
| HTTPS `https://dev.criptofarol.com.br/prototypes/card-967-discovery-recupera-varredura-ativa/` | `9e0447c6f03907bc7c57c5a0045a62ed89f5cb135015c0ff7297dc3ae213e997` | 42186 | 200 |
| `design.md` Prototype / prompt do pai | completo igual | 42186 | — |

Disco == HTTPS: IDENTICAL. T5 mede só este `index.html`. `retry.html` é extra URL da mesma rota (residual), não o canónico.

## Fidelidade (clone da página viva)

Catálogo `/combo/discovery` (`scripts/process-fsm/route-landmarks.yaml`): `selectors: []` · texts `Descoberta de estratégias swing`, `Preflight`, `Rascunho de varredura`.

| Landmark | `DiscoveryPage.tsx` (vivo, sem sessão) | Proto + Playwright |
|---|---|---|
| `Descoberta de estratégias swing` | h1 da página | h1 visível no default Acompanhar (desktop e mobile); exact 1 |
| `Preflight` | `aria-label="Preflight da varredura"` + h2 `Preflight` | hidden no default Acompanhar (painel inactivo, igual ao vivo com sweep); **visível após tab Montar** |
| `Rascunho de varredura` | h2 em tabpanel Montar | article `aria-label="Rascunho de varredura"` + h2; **visível após tab Montar** |

Anti-padrões P0:

- URL canónica `…/prototypes/card-967-discovery-recupera-varredura-ativa/` → index é a página (shell + heading + 3 modos + Acompanhar default). **Não** é painel ANTES/DEPOIS. Botões Antes/Depois = 0. Texto visível `ANTES/DEPOIS` = 0 (comentário de fonte «sem painel ANTES/DEPOIS» não conta como galeria).
- Não é grelha de N estados no lugar da listagem. Default = um Acompanhar (progresso + parciais). Decidir = leaderboard de outra run. Montar = rascunho + Preflight. Tabs trocam 1 painel (`aria-selected` + `aria-controls`). `aria-pressed` = null.
- 11 pares `COPIED:start/end` (copied > 0; soma UTF-8 das regiões copiadas > 0). Delta óbvio = Acompanhar reconstituído (id verdadeiro + progresso) + Iniciar bloqueado; banner vermelho ausente no index.

Chrome presente (sidebar 224px desktop, Inter, nav Descoberta activa, `--bg-primary`) = **folha**, não prova. Prova = landmarks 3/3 no proto, alinhados ao TSX.

Tab default = Acompanhar (`#tab-acomp aria-selected=true`; rótulo vivo `Acompanhando #c91f3a07`, não «Acompanhamento», não «#—»).

## Produto (aceite visível — não reabrir Q1)

Delta pedido: sessão autenticada + varredura viva no servidor → Acompanhar reconstitui-se **sozinho** com número verdadeiro e progresso; banner vermelho ausente; sem clique; sem logout. «Tentar novamente» só residual. Iniciar outra bloqueado até ver o Acompanhar. Falha de tela não cancela/duplica a run.

Contrato visível julgado no proto HTTPS (Playwright + pixels), não no HTML fonte. Index = caminho feliz. `retry.html` = residual (irmão, não canónico).

| Aceite visível | Evidência (Playwright + pixels) | Disposition |
|---|---|---|
| Acompanhar default com número verdadeiro (não «#—») | Tab `Acompanhando #c91f3a07`; h2 Sweep ativo `#c91f3a07b6e24d8a9f51c2e8470b3d16`. `Acompanhando #—` visível no index = 0. Desktop e mobile. | OK |
| Progresso visível | `12 de 24`; chip `EM CURSO`; barra `aria-valuenow=12` / `aria-valuemax=24`; «Varredura em execução». | OK |
| Banner vermelho ausente no caminho feliz | «Não foi possível verificar a varredura ativa» visível = 0 no index (desktop/mobile, Acompanhar/Montar/Decidir). | OK |
| Sem clique / sem «Tentar novamente» no index | Botão «Tentar novamente» count = 0 no index. Default já é Acompanhar hidratado. | OK |
| Sem logout como conserto | Proto autenticado (shell Alan Silva / Ambiente DEV). Sem ecrã «Sessão expirada» (visível = 0). | OK |
| Iniciar outra bloqueado até ver o Acompanhar | Após tab Montar: CTA `Iniciar varredura — 24, ~48 min` **disabled**; copy «Há varredura em curso — ver progresso. Iniciar outra continua bloqueado.» Tab Acompanhar continua com id verdadeiro. | OK |
| Residual não é o index | `retry.html`: Montar + banner vermelho + «Tentar novamente» + `Acompanhando #—` disabled + Iniciar `— 0` disabled. URL extra da mesma rota. T5 não mede este ficheiro. | OK |
| Fora do recorte visível | Sem «Sessão expirada». Histórico = outra run concluída (`#cc5e5403…`), Acompanhar = run viva distinta (não #954). Montar congelado (não #952). Sem modos novos. | OK |

Q1=A **não reaberta**. Mecanismo (backoff/teto do retry automático; `hydrateFromSweep` vs GET falhou; testes) = P3 Apply já aceite em `design.md`.

Banner azul «Varredura ativa recuperada do servidor» / «F5 não inicia outra run» = chrome vivo de `reconnected` após restore bem-sucedido (`DiscoveryPage.tsx`), **não** o banner vermelho do contrato. Clone, não delta deste card.

## UX

Hierarquia: h1 → tablist 3 modos → 1 painel. Default Operate = Acompanhar em curso reconstituído. Glance: id verdadeiro no separador + chip EM CURSO + `12 de 24` lêem-se sem traduzir logout. Montar continua a dizer que há run viva e o Iniciar está morto.

Carga: decisão no glance Acompanhar ≤4 (tabs + Pausar / Cancelar / Novo rascunho). Montar = 0 acção de iniciar (disabled) + 1 leitura do bloqueio. Sem terceiro modo inventado.

## Acessibilidade

- `lang=pt-BR`; `:focus-visible`; `prefers-reduced-motion`; alvos de acção `min-height` 44px (tabs 48px, Pausar/Cancelar/Iniciar/Promover).
- Tablist/tab/tabpanel + `aria-selected` (não `aria-pressed`). 1 tabpanel visível de cada vez (`display:none` nos inactivos).
- Progresso: `role=progressbar` com `aria-label` + `aria-valuenow/max`. Chip EM CURSO é texto, não só cor.
- Iniciar disabled (não só paleta). Residual «Tentar novamente» 44px (irmão, não index).
- Contraste: pares Binance (amarelo CTA vs muted Iniciar disabled vs azul info do restore). GO/NO-GO textuais na grelha clone.
- Nav do shell 42px e link inline «novo rascunho» = clone, não delta (P3).

## Responsividade

- Desktop 1440×900: contrato visível (id + progresso + Iniciar bloqueado no Montar). Ação do Decidir clipa «Favo» à direita com sidebar 224px — risco já visto em irmãos; não esconde o delta deste card. PNGs `967-A-desktop-1440x900-{acomp,acomp-return,montar,decidir}.png`.
- Mobile 390×844: sidebar some (`max-width:1023px`); header 72px; tablist 3 colunas; progresso empilha; Iniciar disabled visível no Montar; parciais viram cards `data-label`. PNGs `967-A-mobile-390x844-{acomp,acomp-return,montar,decidir}.png`.
- Sem overflow que esconda id / `12 de 24` / bloqueio de Iniciar. 0 console / 0 pageerror.

## Estados

Mock cobre: Acompanhar reconstituído (caminho feliz); Montar congelado + Iniciar bloqueado; Decidir = Histórico de outra run (sem delta); residual `retry.html` (banner + retry + `#—`). Não mocka: loading «Verificando varredura ativa…» entre tentativas automáticas (MAY no design, P3 Apply); teto esgotado **no mesmo** index (irmão separado, correcto); 401 «Sessão expirada» (fora). Cobertura de mock = P3, não buraco do contrato visível.

## Design specificity

Composição da Descoberta (modos Montar/Acompanhar/Decidir, restore de sweep activo, Preflight, parciais top-5, leaderboard). Não poderia ir a um SaaS genérico inalterado. Modo Impeccable: **Operate** / refinement. Folha Binance; `DESIGN.md` não reescrito.

## Heurísticas Nielsen (0–4, Operate; só neste snapshot)

| # | Heurística | Score | Nota |
|---|---|---|---|
| 1 | Visibility of system status | 4 | Chip EM CURSO + `12 de 24` + tab `#c91f3a07` + restore info |
| 2 | Match between system and real world | 4 | Acompanhar da run viva; não «#—»; logout deixa de ser o conserto |
| 3 | User Control and Freedom | 3 | Tabs + Pausar/Cancelar; auto-retry é o ponto; residual no irmão |
| 4 | Consistency and Standards | 4 | Clone da rota; residual não misturado no index; Decidir = outra run |
| 5 | Error Prevention | 4 | Iniciar disabled; falha de tela não duplica; 401 continua fora |
| 6 | Recognition rather than recall | 4 | Número e progresso no glance; operador não precisa lembrar o truque logout |
| 7 | Flexibility and efficiency | 3 | Teto/backoff do retry automático = Apply; filtros do vivo cosméticos |
| 8 | Aesthetic and Minimalist Design | 3 | Densidade da grelha aceite; Ação aperta no desktop; Montar condensado |
| 9 | Help users recognize/recover errors | 4 | Reconstituição sozinha é a recuperação; vermelho + retry só após teto |
| 10 | Help and Documentation | 3 | Copy do bloqueio + banner de restore; Ajuda fora |
| **Total** | | **35/40** | **Good** |

## Cognitive load

Checklist: 1 h1; 1 modo visível; delta = hidratar o Acompanhar já nomeado (id + progresso), não um ecrã novo. **Pass**. Decisões no glance Acompanhar ≤4.

## Emotional journey

Vale (banner vermelho + `#—` + rascunho 0 + logout como conserto) → pico (Acompanhar `#c91f3a07` + `12 de 24` sozinho, sem clique) → fim (Iniciar continua bloqueado; residual só se a automática esgotar). Reassegurança: a run no servidor não some; Histórico de outra run não mente «em curso».

## Personas (arquivo; não no chat)

1. **Alex (PROD, sessão autenticada, sweep vivo):** abre Descoberta e já vê Acompanhar `#c91f3a07` / `12 de 24`; não clica «Tentar novamente»; não desloga.
2. **Alex (quer iniciar outra cedo):** Montar mostra Iniciar disabled e copy de bloqueio; tab Acompanhar continua com o id verdadeiro.
3. **Sam (teclado / SR):** landmarks 3/3 após Montar; progressbar anunciável; Iniciar disabled anunciável; tabs `aria-selected`.

## Strengths

- Clone estrutural da rota (`/combo/discovery`), não galeria ANTES/DEPOIS.
- Caminho feliz = estado já hidratado; Q1=A visível sem exigir clique.
- Residual isolado em `retry.html` (não contamina o index canónico).
- Iniciar permanece bloqueado com a run viva à vista.
- Non-goals visíveis: outra run no Histórico/Decidir; sem «Sessão expirada»; sem modos novos.

## Playwright (esta sessão)

- Desktop 1440×900 e mobile 390×844: contrato visível PASS. Landmarks Montar visíveis após tab. Voltar a Acompanhar mantém id + progresso. 0 console / 0 pageerror.
- Live `/combo/discovery` → `/login` (descartado). PNG `967-A-live-combo-discovery.png`.
- Residual `retry.html` inspeccionado só para confirmar que **não** é o index. PNG `967-A-desktop-1440x900-retry-residual.png`.
- Detector: não corrido aqui (Assessment A; B é o detector).
- PNGs: `967-A-desktop-1440x900-{acomp,acomp-return,montar,decidir,retry-residual}.png`, `967-A-mobile-390x844-{acomp,acomp-return,montar,decidir}.png`, `967-A-live-combo-discovery.png`. Gate: `967-A-gate.json`.

## Priority issues

Nenhum P0/P1 de produto/escopo/contrato visível.

## P0

_(nenhum)_

## P1

_(nenhum)_

## P2

_(nenhum)_

## P3 — detalhe de Apply / clone de região fora do delta

- **P3-1** Montar condensado vs vivo: landmarks Preflight + Rascunho presentes; workbench/checkboxes/`<details>` do vivo omitidos. Apply lê `DiscoveryPage.tsx` para Montar intacto.
- **P3-2** Parciais copy «top-5» com 1 `<tr>`; Decidir 1 linha vs «Histórico de outra run» completo. Ação clipa «Favo» a 1440×900. Densidade já vista em irmãos; não esconde id / progresso / Iniciar disabled.
- **P3-3** Banner info «Varredura ativa recuperada do servidor» + frase F5 = chrome vivo de `reconnected` (#664 copy). Não é o vermelho do contrato. Não redesenhar neste card.
- **P3-4** Histórico aberto por omissão no proto (testemunha); vivo está atrás do botão. Nav 42px / CSS vars `--accent` vs `--accent-primary` / «novo rascunho» 18px = clone de shell.
- **P3-5** Markup: 11/11 `COPIED`; 2 `DELTA:start` / 1 `DELTA:end`. Teto/backoff, `hydrateFromSweep` vs GET, testes do retry automático e do residual — já no contrato Apply de `design.md`. Sem endpoint novo.

## Disposition

Aceitar P3 no Apply. Não reabrir grelha. Não reabrir Q1. Não exigir segundo rework de Design por estes itens.

## Verdict

**PASS** — zero P0/P1 de produto/escopo/contrato visível. Tokens parseáveis 3/3. Landmarks 3/3 no proto (Montar para Preflight/Rascunho). Disco == HTTPS. Sem galeria/ANTES-DEPOIS como index. copied > 0 (11 pares). Delta = Acompanhar reconstituído sozinho (`#c91f3a07`, `12 de 24`) + banner vermelho ausente + Iniciar bloqueado. `/login` descartado. Clone **não** alegado só por sidebar: prova = landmarks proto × `DiscoveryPage.tsx`. Q1=A visível no index; clique residual só em `retry.html`.

`Design Agent verdict` final da coluna = síntese do pai após A+B. Este filho A não chama `process_event`.

---

```
Assessment A 967
tokens_ok: yes
clone_ok: yes
P0: nenhum
P1: nenhum
P3: Montar condensado; grelha 1 linha + Ação overflow; banner info F5 clone reconnected; histórico aberto; markup DELTA:end; backoff/hydrate Apply
verdict: PASS
```
